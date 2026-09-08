#!/bin/zsh

set -u

REPO="pickrui/oixcloud-external-proxy-program"
API_URL="https://api.github.com/repos/${REPO}/releases/latest"
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd -P)"
ARCH="$(uname -m)"

case "$ARCH" in
  arm64) ASSET_ARCH="arm64" ;;
  x86_64|amd64) ASSET_ARCH="amd64" ;;
  *)
    /usr/bin/osascript -e 'display alert "oixCloud" message "不支持当前 Mac 芯片架构" as critical' >/dev/null 2>&1 || true
    echo "不支持当前 Mac 芯片架构：$ARCH"
    exit 1
    ;;
esac

MAJOR="$(/usr/bin/sw_vers -productVersion | /usr/bin/cut -d. -f1)"
if [[ "$MAJOR" -ge 14 ]]; then
  ASSET_NAME="oixcloud-external-proxy-program-${ASSET_ARCH}"
else
  ASSET_NAME="oixcloud-external-proxy-program-legacy"
fi
ASSET_PATH="${SCRIPT_DIR}/${ASSET_NAME}"
PROGRAM_PATH="${SCRIPT_DIR}/oixcloud-external-proxy-program"
INSTALL_PATH="/usr/local/bin/oixcloud-external-proxy-program"
# 发布二进制应由该 Team ID 的 Developer ID 证书签名（发布方固定）
EXPECTED_TEAM_ID="WJHBZFHR7D"
MAX_DOWNLOAD_BYTES=$((64 * 1024 * 1024))
TAG_FILE="${SCRIPT_DIR}/.oixcloud-external-proxy-program.version"
LOG_FILE="${SCRIPT_DIR}/oixcloud-external-proxy-program.log"
TRAY_LOG_DIR="${HOME}/Library/Logs/oixcloud"
TRAY_LOG_FILE="${TRAY_LOG_DIR}/com.oixcloud.external-proxy-program.tray.log"
PLIST_LABEL="com.oixcloud.external-proxy-program.tray"
PLIST_PATH="${HOME}/Library/LaunchAgents/${PLIST_LABEL}.plist"
LAUNCHD_SERVICE="gui/$(id -u)/${PLIST_LABEL}"

notify() {
  /usr/bin/osascript -e "display notification \"$1\" with title \"oixCloud\"" >/dev/null 2>&1 || true
}

alert() {
  /usr/bin/osascript -e "display alert \"oixCloud\" message \"$1\" as critical" >/dev/null 2>&1 || true
}

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE"
}

fetch_latest_release() {
  local release_json="$1"
  /usr/bin/curl --http1.1 -4 -L --fail --silent \
    --retry 3 --connect-timeout 20 \
    --header "Accept: application/vnd.github+json" \
    --output "$release_json" \
    "$API_URL"
}

extract_asset_info() {
  local release_json="$1"
  /usr/bin/osascript -l JavaScript \
    -e 'function run(argv) {' \
    -e '  ObjC.import("Foundation");' \
    -e '  const text = $.NSString.stringWithContentsOfFileEncodingError(argv[0], $.NSUTF8StringEncoding, null);' \
    -e '  if (!text) throw new Error("无法读取发布版本元数据");' \
    -e '  const release = JSON.parse(text.js);' \
    -e '  const assetName = argv[1];' \
    -e '  const asset = (release.assets || []).find(a => a.name === assetName);' \
    -e '  if (!/^v[0-9]+(?:\.[0-9]+){1,2}$/.test(release.tag_name || "")) throw new Error("发布版本号格式无效");' \
    -e '  if (!asset || !asset.browser_download_url) throw new Error("未找到发布文件：" + assetName);' \
    -e '  const prefix = "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/";' \
    -e '  if (!asset.browser_download_url.startsWith(prefix) || /[\r\n]/.test(asset.browser_download_url)) throw new Error("发布文件地址无效");' \
    -e '  if (asset.digest && !/^sha256:[0-9a-f]{64}$/i.test(asset.digest)) throw new Error("发布文件摘要无效");' \
    -e '  return [release.tag_name, asset.browser_download_url, asset.digest || ""].join("\n");' \
    -e '}' \
    "$release_json" "$ASSET_NAME"
}

file_sha256() {
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}

matches_digest() {
  local path="$1"
  local expected_digest="$2"
  [[ -f "$path" && "$expected_digest" == sha256:* ]] || return 1
  [[ "$(file_sha256 "$path")" == "${expected_digest#sha256:}" ]]
}

# 校验 Developer ID 代码签名，并确认 Team ID 与发布方一致
verify_signature() {
  local path="$1"
  /usr/bin/codesign --verify --strict "$path" >/dev/null 2>&1 || return 1
  local team
  team="$(/usr/bin/codesign -dv "$path" 2>&1 | /usr/bin/awk -F= '/^TeamIdentifier=/{print $2}')"
  [[ -n "$team" && "$team" == "$EXPECTED_TEAM_ID" ]]
}

is_valid_release_tag() {
  [[ "$1" != *$'\n'* && "$1" != *$'\r'* ]] || return 1
  printf '%s\n' "$1" | /usr/bin/grep -Eq '^v[0-9]+(\.[0-9]+){1,2}$'
}

is_trusted_download_url() {
  [[ "$1" == https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/* \
      && "$1" != *$'\n'* && "$1" != *$'\r'* ]]
}

verify_release_binary() {
  local path="$1"
  local expected_digest="$2"
  local expected_tag="$3"
  [[ -x "$path" ]] || return 1
  is_valid_release_tag "$expected_tag" || return 1
  if [[ "$expected_digest" == sha256:* ]]; then
    matches_digest "$path" "$expected_digest" || return 1
  fi
  verify_signature "$path" || return 1
  [[ "$("$path" --version 2>/dev/null)" == "oixcloud-external-proxy-program ${expected_tag}" ]]
}

replace_local_binary() {
  setopt localtraps
  local source_path="$1"
  local target_path="$2"
  local expected_digest="$3"
  local latest_tag="$4"
  local install_tmp="${target_path}.new.$$.${RANDOM}"
  local install_backup="${target_path}.backup.$$.${RANDOM}"
  local target_replaced=0

  /bin/cp "$source_path" "$install_tmp" || return 1
  /bin/chmod 755 "$install_tmp" || return 1
  verify_release_binary "$install_tmp" "$expected_digest" "$latest_tag" || {
    /bin/rm -f "$install_tmp"
    return 1
  }
  trap 'trap - HUP INT TERM; rollback_local_binary; exit 130' HUP INT TERM
  if [[ -e "$target_path" ]]; then
    if ! /bin/cp -p "$target_path" "$install_backup"; then
      trap - HUP INT TERM
      /bin/rm -f "$install_tmp"
      return 1
    fi
  fi
  if /bin/mv -f "$install_tmp" "$target_path"; then
    target_replaced=1
  fi
  if [[ "$target_replaced" -eq 1 ]] \
      && verify_release_binary "$target_path" "$expected_digest" "$latest_tag"; then
    trap - HUP INT TERM
    /bin/rm -f "$install_backup"
    return 0
  fi
  trap - HUP INT TERM
  rollback_local_binary
  return 1
}

rollback_local_binary() {
  /bin/rm -f "$install_tmp"
  if [[ "$target_replaced" -eq 1 && -e "$install_backup" ]]; then
    /bin/mv -f "$install_backup" "$target_path" || true
  elif [[ "$target_replaced" -eq 1 ]]; then
    /bin/rm -f "$target_path"
  else
    /bin/rm -f "$install_backup"
  fi
}

download_and_install() {
  local download_url="$1"
  local expected_digest="$2"
  local latest_tag="$3"
  local temp_bin
  temp_bin="$(/usr/bin/mktemp "${TMPDIR:-/tmp}/oixcloud.XXXXXX")" || return 1

  log "正在下载 ${ASSET_NAME} ${latest_tag}..."
  if ! /usr/bin/curl --http1.1 -4 -L --fail --silent \
      --retry 3 --connect-timeout 20 --max-time 300 \
      --max-filesize "$MAX_DOWNLOAD_BYTES" \
      --output "$temp_bin" \
      "$download_url"; then
    log "下载 ${ASSET_NAME} ${latest_tag} 失败"
    rm -f "$temp_bin"
    return 1
  fi

  /bin/chmod 755 "$temp_bin"
  /usr/bin/xattr -dr com.apple.quarantine "$temp_bin" >/dev/null 2>&1 || true
  if ! verify_release_binary "$temp_bin" "$expected_digest" "$latest_tag"; then
    log "下载文件校验失败，已终止安装"
    rm -f "$temp_bin"
    return 1
  fi

  if ! replace_local_binary "$temp_bin" "$PROGRAM_PATH" "$expected_digest" "$latest_tag" \
      || ! replace_local_binary "$temp_bin" "$ASSET_PATH" "$expected_digest" "$latest_tag"; then
    log "无法安全替换本地发布文件"
    rm -f "$temp_bin"
    return 1
  fi
  rm -f "$temp_bin"
  printf '%s\n' "$latest_tag" > "$TAG_FILE"
  log "已更新本地文件 ${ASSET_NAME} ${latest_tag}"
  return 0
}

install_command_atomically() {
  setopt localtraps
  local source_path="$1"
  local expected_digest="$2"
  local latest_tag="$3"
  local install_tmp="${INSTALL_PATH}.new.$$.${RANDOM}"
  local install_backup="${INSTALL_PATH}.backup.$$.${RANDOM}"
  local target_replaced=0

  /usr/bin/sudo -p "请输入管理员密码：" /bin/cp "$source_path" "$install_tmp" || return 1
  /usr/bin/sudo -p "请输入管理员密码：" /bin/chmod 755 "$install_tmp" || return 1
  /usr/bin/sudo -p "请输入管理员密码：" /usr/bin/xattr -dr com.apple.quarantine "$install_tmp" >/dev/null 2>&1 || true
  if ! verify_release_binary "$install_tmp" "$expected_digest" "$latest_tag"; then
    /usr/bin/sudo -p "请输入管理员密码：" /bin/rm -f "$install_tmp" >/dev/null 2>&1 || true
    return 1
  fi
  trap 'trap - HUP INT TERM; rollback_installed_command; exit 130' HUP INT TERM
  if [[ -e "$INSTALL_PATH" ]]; then
    if ! /usr/bin/sudo -p "请输入管理员密码：" /bin/cp -p "$INSTALL_PATH" "$install_backup"; then
      trap - HUP INT TERM
      /usr/bin/sudo -p "请输入管理员密码：" /bin/rm -f "$install_tmp" >/dev/null 2>&1 || true
      return 1
    fi
  fi
  if /usr/bin/sudo -p "请输入管理员密码：" /bin/mv -f "$install_tmp" "$INSTALL_PATH"; then
    target_replaced=1
  fi
  if [[ "$target_replaced" -eq 1 ]] \
      && verify_release_binary "$INSTALL_PATH" "$expected_digest" "$latest_tag"; then
    trap - HUP INT TERM
    /usr/bin/sudo -p "请输入管理员密码：" /bin/rm -f "$install_backup" >/dev/null 2>&1 || true
    return 0
  fi
  trap - HUP INT TERM
  rollback_installed_command
  return 1
}

rollback_installed_command() {
  /usr/bin/sudo -p "请输入管理员密码：" /bin/rm -f "$install_tmp" >/dev/null 2>&1 || true
  if [[ "$target_replaced" -eq 1 ]] \
      && /usr/bin/sudo -p "请输入管理员密码：" /usr/bin/test -e "$install_backup"; then
    /usr/bin/sudo -p "请输入管理员密码：" /bin/mv -f "$install_backup" "$INSTALL_PATH" || true
  elif [[ "$target_replaced" -eq 1 ]]; then
    /usr/bin/sudo -p "请输入管理员密码：" /bin/rm -f "$INSTALL_PATH" >/dev/null 2>&1 || true
  else
    /usr/bin/sudo -p "请输入管理员密码：" /bin/rm -f "$install_backup" >/dev/null 2>&1 || true
  fi
}

ensure_installed_command() {
  local expected_digest="$1"
  local latest_tag="$2"

  if ! verify_release_binary "$PROGRAM_PATH" "$expected_digest" "$latest_tag"; then
    if verify_release_binary "$ASSET_PATH" "$expected_digest" "$latest_tag"; then
      replace_local_binary "$ASSET_PATH" "$PROGRAM_PATH" "$expected_digest" "$latest_tag" || return 1
    else
      log "没有找到匹配 ${latest_tag} 的本地程序，无法安装命令"
      return 1
    fi
  fi

  /bin/chmod 755 "$PROGRAM_PATH"
  /usr/bin/xattr -dr com.apple.quarantine "$PROGRAM_PATH" >/dev/null 2>&1 || true

  if verify_release_binary "$INSTALL_PATH" "$expected_digest" "$latest_tag"; then
    log "已安装命令是最新版本：${INSTALL_PATH}"
    return 0
  fi

  if ! verify_release_binary "$PROGRAM_PATH" "$expected_digest" "$latest_tag"; then
    log "本地程序校验失败，已终止安装"
    return 1
  fi

  log "正在安装命令到 ${INSTALL_PATH}..."
  log "复制到 /usr/local/bin 需要管理员权限"
  if ! /usr/bin/sudo -p "请输入管理员密码：" -v; then
    log "管理员密码验证失败，无法安装 ${INSTALL_PATH}"
    return 1
  fi

  /usr/bin/sudo -p "请输入管理员密码：" /bin/mkdir -p /usr/local/bin || return 1
  if ! install_command_atomically "$PROGRAM_PATH" "$expected_digest" "$latest_tag"; then
    log "安装后校验失败，旧版本已恢复"
    return 1
  fi
  log "已安装 ${INSTALL_PATH} ${latest_tag}"
}

ensure_cached_command() {
  local cached_tag cached_digest candidate

  if [[ -x "$PROGRAM_PATH" ]] && verify_signature "$PROGRAM_PATH"; then
    candidate="$PROGRAM_PATH"
  elif [[ -x "$ASSET_PATH" ]] && verify_signature "$ASSET_PATH"; then
    candidate="$ASSET_PATH"
  else
    log "没有可用的本地缓存程序"
    return 1
  fi

  cached_tag="$("$candidate" --version 2>/dev/null | /usr/bin/awk '{print $NF}')"
  is_valid_release_tag "$cached_tag" || return 1
  cached_digest="sha256:$(file_sha256 "$candidate")"
  if [[ "$candidate" != "$PROGRAM_PATH" ]]; then
    replace_local_binary "$candidate" "$PROGRAM_PATH" "$cached_digest" "$cached_tag" || return 1
  fi
  log "正在使用 ${cached_tag} 的本地缓存程序"
  ensure_installed_command "$cached_digest" "$cached_tag"
}

update_if_needed() {
  local release_json asset_info latest_tag download_url expected_digest local_tag local_sha expected_sha
  release_json="$(/usr/bin/mktemp "${TMPDIR:-/tmp}/oixcloud-release.XXXXXX")" || return 2

  log "正在检查最新发布版本..."
  if ! fetch_latest_release "$release_json"; then
    log "无法获取最新发布版本元数据"
    rm -f "$release_json"
    return 2
  fi
  if ! asset_info="$(extract_asset_info "$release_json")"; then
    log "无法解析最新发布版本元数据"
    rm -f "$release_json"
    return 2
  fi
  rm -f "$release_json"

  latest_tag="$(printf '%s\n' "$asset_info" | sed -n '1p')"
  download_url="$(printf '%s\n' "$asset_info" | sed -n '2p')"
  expected_digest="$(printf '%s\n' "$asset_info" | sed -n '3p')"
  if ! is_valid_release_tag "$latest_tag" || ! is_trusted_download_url "$download_url"; then
    log "发布元数据格式无效"
    return 2
  fi

  local_tag=""
  [[ -f "$TAG_FILE" ]] && local_tag="$(cat "$TAG_FILE" 2>/dev/null || true)"

  if [[ -x "$PROGRAM_PATH" && "$expected_digest" == sha256:* ]]; then
    local_sha="$(file_sha256 "$PROGRAM_PATH")"
    expected_sha="${expected_digest#sha256:}"
    if [[ "$local_sha" == "$expected_sha" ]]; then
      [[ "$local_tag" != "$latest_tag" ]] && printf '%s\n' "$latest_tag" > "$TAG_FILE"
      log "本地发布程序已是最新版本：${latest_tag}"
      ensure_installed_command "$expected_digest" "$latest_tag"
      return $?
    fi
  elif [[ -x "$PROGRAM_PATH" && "$local_tag" == "$latest_tag" ]]; then
    log "本地发布程序已是最新版本：${latest_tag}"
    ensure_installed_command "$expected_digest" "$latest_tag"
    return $?
  fi

  download_and_install "$download_url" "$expected_digest" "$latest_tag" || return 1
  ensure_installed_command "$expected_digest" "$latest_tag"
}

escape_plist_text() {
  local value="$1"
  value="${value//&/&amp;}"
  value="${value//</&lt;}"
  value="${value//>/&gt;}"
  printf '%s' "$value"
}

write_launch_agent() {
  local plist_dir="${PLIST_PATH:h}" plist_tmp
  /bin/mkdir -p "$plist_dir" "$TRAY_LOG_DIR" || return 1
  if [[ -L "$PLIST_PATH" || -d "$PLIST_PATH" ]]; then
    log "自动启动配置路径不是普通文件：${PLIST_PATH}"
    return 1
  fi
  plist_tmp="$(/usr/bin/mktemp "${plist_dir}/.${PLIST_LABEL}.XXXXXX")" || return 1
  {
  /bin/cat > "$plist_tmp" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>$(escape_plist_text "$PLIST_LABEL")</string>
<key>ProgramArguments</key><array>
<string>$(escape_plist_text "$INSTALL_PATH")</string><string>--tray</string></array>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
<key>StandardOutPath</key><string>$(escape_plist_text "$TRAY_LOG_FILE")</string>
<key>StandardErrorPath</key><string>$(escape_plist_text "$TRAY_LOG_FILE")</string>
</dict></plist>
EOF
  [[ $? -eq 0 ]] || return 1
  /usr/bin/plutil -lint "$plist_tmp" >/dev/null || return 1
  /bin/chmod 644 "$plist_tmp" || return 1
  # Rename uses directory permissions, so a read-only/root-owned old plist
  # can be replaced without opening it or changing unrelated startup items.
  /bin/mv -f -- "$plist_tmp" "$PLIST_PATH"
  } always {
    /bin/rm -f -- "$plist_tmp"
  }
}

choose_launch_mode() {
  local selected key rest
  selected=0

  case "${OIX_LAUNCH_MODE:-}" in
    launchagent|agent|persistent)
      printf '%s\n' "launchagent"
      return 0
      ;;
    temporary|temp|foreground)
      printf '%s\n' "temporary"
      return 0
      ;;
    uninstall|remove|disable|disable-autostart)
      printf '%s\n' "uninstall"
      return 0
      ;;
  esac

  if [[ ! -t 0 ]]; then
    printf '%s\n' "launchagent"
    return 0
  fi

  while true; do
    {
      printf '\033[2J\033[H'
      printf '请选择 oixCloud 启动方式\n\n'
      if [[ "$selected" -eq 0 ]]; then
        printf '> 1. 临时启动（关闭这个终端窗口后程序会退出）\n'
      else
        printf '  1. 临时启动（关闭这个终端窗口后程序会退出）\n'
      fi
      if [[ "$selected" -eq 1 ]]; then
        printf '> 2. 常驻启动（系统自动启动项，推荐；关闭终端后仍会运行，并开机自启）\n'
      else
        printf '  2. 常驻启动（系统自动启动项，推荐；关闭终端后仍会运行，并开机自启）\n'
      fi
      if [[ "$selected" -eq 2 ]]; then
        printf '> 3. 卸载自动启动（停止并删除系统自动启动项）\n'
      else
        printf '  3. 卸载自动启动（停止并删除系统自动启动项）\n'
      fi
      printf '\n使用上下方向键选择，然后按回车确认；也可以直接按 1、2 或 3\n'
    } > /dev/tty

    IFS= read -r -s -k 1 key < /dev/tty || {
      printf '%s\n' "launchagent"
      return 0
    }

    case "$key" in
      $'\e')
        IFS= read -r -s -k 2 rest < /dev/tty || rest=""
        case "$rest" in
          "[A") selected=$(( (selected + 2) % 3 )) ;;
          "[B") selected=$(( (selected + 1) % 3 )) ;;
        esac
        ;;
      $'\n'|$'\r')
        break
        ;;
      1)
        selected=0
        break
        ;;
      2)
        selected=1
        break
        ;;
      3)
        selected=2
        break
        ;;
    esac
  done

  printf '\n' > /dev/tty
  if [[ "$selected" -eq 0 ]]; then
    printf '%s\n' "temporary"
  elif [[ "$selected" -eq 1 ]]; then
    printf '%s\n' "launchagent"
  else
    printf '%s\n' "uninstall"
  fi
}

uninstall_launch_agent() {
  log "正在卸载自动启动..."
  if [[ -f "$PLIST_PATH" ]]; then
    /bin/launchctl unload -w "$PLIST_PATH" >/dev/null 2>&1 || true
    /bin/rm -f "$PLIST_PATH"
    log "已停止并删除自动启动配置：${PLIST_PATH}"
    notify "已卸载 oixCloud 自动启动"
  else
    /bin/launchctl bootout "gui/$(id -u)" "$PLIST_PATH" >/dev/null 2>&1 || true
    log "未找到自动启动配置，无需卸载：${PLIST_PATH}"
    notify "未找到 oixCloud 自动启动配置"
  fi
}

start_with_launch_agent() {
  if ! write_launch_agent; then
    log "无法写入自动启动配置：${PLIST_PATH}，请检查 LaunchAgents 目录所有者和写权限"
    alert "无法写入自动启动配置，请检查 LaunchAgents 目录权限后重试"
    return 1
  fi

  log "正在通过系统自动启动项启动 oixCloud 菜单栏程序..."
  /bin/launchctl bootout "gui/$(id -u)" "$PLIST_PATH" >/dev/null 2>&1 || \
    /bin/launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true

  if ! /bin/launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" >> "$LOG_FILE" 2>&1; then
    if ! /bin/launchctl load -w "$PLIST_PATH" >> "$LOG_FILE" 2>&1; then
      alert "无法启动 oixCloud 自动启动项，请查看 ${LOG_FILE}"
      log "无法启动 oixCloud 自动启动项"
      exit 1
    fi
  fi

  /bin/launchctl enable "$LAUNCHD_SERVICE" >/dev/null 2>&1 || true
  /bin/launchctl kickstart -k "$LAUNCHD_SERVICE" >/dev/null 2>&1 || true

  sleep 2
  if /bin/launchctl print "$LAUNCHD_SERVICE" >/dev/null 2>&1; then
    log "oixCloud 自动启动项已加载：${PLIST_LABEL}"
    notify "oixCloud 已启动"
  else
    alert "oixCloud 自动启动项未能加载，请查看 ${LOG_FILE}"
    log "oixCloud 自动启动项未能加载"
    exit 1
  fi
}

start_temporarily() {
  log "正在临时启动 oixCloud 菜单栏程序，关闭此终端窗口后程序会退出"
  notify "oixCloud 正在临时启动"
  /bin/launchctl bootout "gui/$(id -u)" "$PLIST_PATH" >/dev/null 2>&1 || \
    /bin/launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
  exec "$INSTALL_PATH" --tray
}

launch_program() {
  local launch_mode="$1"
  local launch_mode_label

  if [[ ! -x "$INSTALL_PATH" ]]; then
    alert "程序不存在或不可执行：${INSTALL_PATH}"
    log "程序不存在或不可执行：${INSTALL_PATH}"
    exit 1
  fi

  /usr/bin/xattr -dr com.apple.quarantine "$INSTALL_PATH" >/dev/null 2>&1 || true

  if [[ "${OIX_NO_LAUNCH:-0}" == "1" ]]; then
    log "已设置 OIX_NO_LAUNCH=1，跳过启动"
    return 0
  fi

  case "$launch_mode" in
    temporary) launch_mode_label="临时启动" ;;
    *) launch_mode_label="常驻启动" ;;
  esac

  log "已选择启动方式：${launch_mode_label}"
  if [[ "$launch_mode" == "temporary" ]]; then
    start_temporarily
  else
    start_with_launch_agent
  fi
}

main() {
  local update_status launch_mode
  update_status=0

  launch_mode="launchagent"
  if [[ "${OIX_NO_LAUNCH:-0}" != "1" ]]; then
    launch_mode="$(choose_launch_mode)"
    if [[ "$launch_mode" == "uninstall" ]]; then
      uninstall_launch_agent
      exit 0
    fi
  fi

  update_if_needed || update_status=$?

  if [[ "$update_status" -ne 0 ]]; then
    if [[ "$update_status" -eq 2 && ( -x "$PROGRAM_PATH" || -x "$ASSET_PATH" ) ]]; then
      log "更新检查失败，正在尝试使用本地缓存程序"
      if ! ensure_cached_command; then
        alert "无法更新或安装本地缓存的 oixCloud，请查看 ${LOG_FILE}"
        exit 1
      fi
      notify "更新检查失败，将启动本地缓存的 oixCloud"
    elif [[ "$update_status" -eq 2 && -x "$INSTALL_PATH" ]]; then
      log "更新检查失败，将启动现有已安装命令"
      notify "更新检查失败，将启动现有 oixCloud"
    else
      alert "无法更新并安装 oixCloud，请查看 ${LOG_FILE}"
      exit 1
    fi
  fi

  launch_program "$launch_mode"
}

if [[ "${OIX_LAUNCHER_SOURCE_ONLY:-0}" != "1" ]]; then
  main "$@"
fi
