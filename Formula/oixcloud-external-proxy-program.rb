class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.45"
  license :cannot_represent

  url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-legacy"
  sha256 "018cf64090fdabc9307294a5e681b4a790f57d4e548e610f136c948c7a72f7c0"

  depends_on macos: :monterey

  on_macos do
    on_sonoma :or_newer do
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-arm64"
        sha256 "26b2efaf7cae8ef8cbac9405d7426c3d2073bb2468fbfe9c4e8253367b803430"

        def install
          bin.install "oixcloud-external-proxy-program-arm64" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-amd64"
        sha256 "e8dffe2369f17ccef18da09cc6a3e1470c983adf2bb2ee7999f75263772e0ce0"

        def install
          bin.install "oixcloud-external-proxy-program-amd64" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end
    end

    on_ventura :or_older do
      def install
        bin.install "oixcloud-external-proxy-program-legacy" => "oixcloud-external-proxy-program"
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
