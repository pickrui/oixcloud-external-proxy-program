class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.60"
  license :cannot_represent

  url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-legacy"
  sha256 "ef2064373ab3013ad63388b299e34dc93c2bcd135acbcfd399170dd3ed26f9b8"

  depends_on macos: :monterey

  on_macos do
    on_sonoma :or_newer do
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-arm64"
        sha256 "0587064cacc6ed8a74568175768093387519a034f4d34a4ce3037b797a68ffa3"

        def install
          bin.install "oixcloud-external-proxy-program-arm64" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-amd64"
        sha256 "fb4e471c91eebf59c63ff2665691a3d50f957b8cbc9f1edb5c33b041f1f8584f"

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
