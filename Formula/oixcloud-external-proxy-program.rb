class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.66"
  revision 2
  license :cannot_represent

  url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-legacy.zip"
  sha256 "684bf882dc155685070fbb2716c4bde9c530eb416efc523b28c4c665fd49c878"

  depends_on macos: :monterey

  on_macos do
    on_sonoma :or_newer do
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-arm64.zip"
        sha256 "8f0bbc7664073babd53ab67633eb2bcd2a88b0152dee7210907df6d87d893d72"

        def install
          (prefix/"oixCloud Helper.app").install "Contents"
          bin.install_symlink prefix/"oixCloud Helper.app/Contents/MacOS/oixcloud-helper" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-amd64.zip"
        sha256 "fadccd33af3eefb4b07397a800c01bba88d635ab8da4af8d397869a1d2d21a78"

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
