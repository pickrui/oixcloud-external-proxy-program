class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.84"
  license :cannot_represent

  url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-legacy.zip"
  sha256 "f12d7efd029512eeeee4a00c4cc51e6b6ad44c3a2596785b43a781ff70f9cf6d"

  depends_on macos: :monterey

  on_macos do
    on_sonoma :or_newer do
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-arm64.zip"
        sha256 "a8c2b1e267fb2e357d26024a05e95a578f2b5dce786e9441e35a45fda4d2fcad"

        def install
          (prefix/"oixCloud Helper.app").install "Contents"
          bin.install_symlink prefix/"oixCloud Helper.app/Contents/MacOS/oixcloud-helper" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-amd64.zip"
        sha256 "19c2cd7b16560f2e9da20e4edca081151366433db0b6dec5fa4bf5e0d98d6ef7"

        def install
          (prefix/"oixCloud Helper.app").install "Contents"
          bin.install_symlink prefix/"oixCloud Helper.app/Contents/MacOS/oixcloud-helper" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end
    end

    on_ventura :or_older do
      def install
        (prefix/"oixCloud Helper.app").install "Contents"
        bin.install_symlink prefix/"oixCloud Helper.app/Contents/MacOS/oixcloud-helper" => "oixcloud-external-proxy-program"
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
