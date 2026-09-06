class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.29"
  license :cannot_represent

  on_macos do
    on_arm do
      url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-arm64"
      sha256 "7bacde236d551a38ec6596b74fc77ea824e7e488fb8e5a3b1f03247c4b1581ff"

      def install
        bin.install "oixcloud-external-proxy-program-arm64" => "oixcloud-external-proxy-program"
        bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
      end
    end

    on_intel do
      url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-amd64"
      sha256 "7022b1f7d90b8c09c440ddf515547fa17f77f83164c4ef70ae824c18f5a0a3bf"

      def install
        bin.install "oixcloud-external-proxy-program-amd64" => "oixcloud-external-proxy-program"
        bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
      end
    end
  end

  service do
    run [opt_bin/"oixcloud-external-proxy-program", "--tray"]
    keep_alive true
    log_path var/"log/oixcloud-external-proxy-program.log"
    error_log_path var/"log/oixcloud-external-proxy-program.log"
  end

  test do
    assert_match "oixcloud-external-proxy-program v#{version}", shell_output("#{bin}/oixcloud-external-proxy-program --version")
    assert_match "oixcloud-external-proxy-program v#{version}", shell_output("#{bin}/oixcloud-helper --version")
  end
end
