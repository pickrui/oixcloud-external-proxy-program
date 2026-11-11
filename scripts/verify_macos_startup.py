from pathlib import Path
import argparse
import hashlib
import json
import os
import plistlib
import signal
import shutil
import socket
import subprocess
import time
import urllib.request


parser = argparse.ArgumentParser(description='Start final signed files through app and command entry points')
parser.add_argument('--app', required=True, type=Path)
parser.add_argument('--raw', required=True, type=Path)
parser.add_argument('--work', required=True, type=Path)
parser.add_argument('--version', required=True)
parser.add_argument('--brew-prefix', type=Path)
parser.add_argument('--sandbox', action='store_true', help='Protect the local developer home; native VM tests run normally')
args = parser.parse_args()
work = args.work.resolve()
work.mkdir(parents=True)
raw = args.raw.resolve()
downloaded_app = args.app.resolve()
assert not any(part in ('.build', 'DerivedData') for part in raw.parts + downloaded_app.parts)
app_name = 'oixCloud Helper.app'
executable = Path('Contents/MacOS/oixcloud-helper')
records = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def app_files(app):
    return {str(p.relative_to(app)): sha(p) for p in app.rglob('*') if p.is_file()}


if args.brew_prefix:
    opt = args.brew_prefix.absolute()
    cellar = opt.resolve()
    assert 'Cellar' in cellar.parts
    app = cellar / app_name
    assert app_files(app) == app_files(downloaded_app), 'Homebrew changed the signed app bytes'
    mode = 'actual Homebrew installation'
else:
    cellar = work / 'prefix/Cellar/oixcloud-external-proxy-program' / (args.version[1:] + '_probe')
    app = cellar / app_name
    shutil.copytree(downloaded_app, app)
    (cellar / 'bin').mkdir()
    for name in ('oixcloud-external-proxy-program', 'oixcloud-helper'):
        (cellar / 'bin' / name).symlink_to(Path('..') / app_name / executable)
    opt = work / 'prefix/opt/oixcloud-external-proxy-program'
    opt.parent.mkdir()
    opt.symlink_to(cellar)
    mode = 'isolated layout of downloaded final app; not a Homebrew installation'

info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
assert info['OIXReleaseTag'] == args.version
assert info['OIXStandaloneSHA256'] == sha(raw)
entries = [app / executable, cellar / 'bin/oixcloud-external-proxy-program',
           opt / 'bin/oixcloud-external-proxy-program', opt / 'bin/oixcloud-helper']
assert all(entry.is_file() for entry in entries)
assert all(entry.resolve() == app / executable for entry in entries)

profile = work / 'startup.sb'
if args.sandbox:
    profile.write_text('(version 1)\n(allow default)\n'
                       '(deny network*)\n'
                       '(allow network-inbound (local ip "localhost:*"))\n'
                       '(allow network-outbound (remote ip "localhost:*"))\n'
                       '(deny file-write*)\n'
                       '(allow file-write* (subpath ' + json.dumps(str(work)) + '))\n'
                       '(deny file-read* (subpath ' + json.dumps(str(Path.home())) + '))\n')


def run(entry, case, reject=False):
    directory = work / ('case-' + str(len(records)))
    directory.mkdir()
    with socket.socket() as reserved:
        reserved.bind(('127.0.0.1', 0))
        port = reserved.getsockname()[1]
    config = directory / 'config.json'
    config.write_text(json.dumps({'listeners': [], 'proxyMode': 'map', 'servePort': port,
                                  'listenAddress': '127.0.0.1', 'accessTokenInKeychain': False}))
    inherited = ('PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL', 'LC_CTYPE',
                 'USER', 'LOGNAME', '__CF_USER_TEXT_ENCODING')
    environment = {name: os.environ[name] for name in inherited if name in os.environ}
    command = [str(entry), '--listen', '127.0.0.1:' + str(port), '--map', '--config', str(config)]
    if args.sandbox:
        command = ['/usr/bin/sandbox-exec', '-f', str(profile), *command]
    log_path = directory / 'startup.log'
    health = None
    status = None
    with log_path.open('w') as log:
        process = subprocess.Popen(command, cwd=directory, env=environment, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            if reject:
                code = process.wait(timeout=15)
                text = log_path.read_text()
                assert code == 1, (case, code, text)
                assert 'integrity check failed: code signature verification failed:' in text, (case, text)
            else:
                deadline = time.monotonic() + 15
                client = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                while time.monotonic() < deadline:
                    assert process.poll() is None, (case, log_path.read_text())
                    try:
                        with client.open('http://127.0.0.1:' + str(port) + '/health', timeout=0.5) as response:
                            health = response.status
                            assert response.read() == b'ok\n'
                        with client.open('http://127.0.0.1:' + str(port) + '/status', timeout=0.5) as response:
                            assert response.status == 200
                            status = json.load(response)
                        break
                    except (OSError, TimeoutError):
                        time.sleep(0.1)
                assert health == 200 and status, (case, log_path.read_text())
                assert status['version'] == args.version and status['mode'] == 'map'
                assert status['nodeCount'] == status['mappingCount'] == 0
                time.sleep(0.3)
                assert process.poll() is None, (case, log_path.read_text())
                text = log_path.read_text()
                assert 'startup: version=' + args.version in text
                assert 'integrity check skipped' not in text and 'integrity check failed' not in text, text
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
    records.append({'entry': str(entry), 'case': case, 'mode': mode,
                    'productionSelfcheck': 'rejected modified resource' if reject else 'passed before HTTP service startup',
                    'healthHTTP': health, 'processAliveAfterHealth': not reject,
                    'accountState': 'no credentials; zero nodes expected', 'sandbox': args.sandbox})
    print(case + ': ' + records[-1]['productionSelfcheck'], flush=True)


if not args.brew_prefix:
    alias = work / 'standalone-alias'
    alias.symlink_to(raw)
    run(raw, 'raw direct')
    run(alias, 'raw alias')
for index, entry in enumerate(entries):
    run(entry, 'app entry ' + str(index))

if not args.brew_prefix:
    for relative in ('Contents/Info.plist', 'Contents/Resources/AppIcon.icns'):
        resource = app / relative
        original = resource.read_bytes()
        try:
            if relative.endswith('.plist'):
                altered = plistlib.loads(original)
                altered['CFBundleDisplayName'] = 'Modified resource'
                resource.write_bytes(plistlib.dumps(altered))
            else:
                resource.write_bytes(b'modified resource')
            for index, entry in enumerate(entries):
                run(entry, relative + ' modified entry ' + str(index), reject=True)
        finally:
            resource.write_bytes(original)

report = {'version': args.version, 'mode': mode, 'records': records,
          'registeredLaunchdService': False, 'realAccountUsed': False,
          'notClaimed': ['user launchd registration', 'physical macOS 12/13 startup']}
(work / 'startup-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print('STARTUP_VERIFICATION ' + json.dumps(report), flush=True)
