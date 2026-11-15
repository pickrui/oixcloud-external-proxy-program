class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.70"
  license :cannot_represent

  url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-legacy.zip"
  sha256 "07211fb4454f946de82fddebb2520277df9da3b4a1e06208c23b6c1e42129184"

  depends_on macos: :monterey

  on_macos do
    on_sonoma :or_newer do
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-arm64.zip"
        sha256 "7e1e8a930591b691385952dc18f9734a00685ccdfaf628eda9072fba42f6c997"

        def install
          (prefix/"oixCloud Helper.app").install "Contents"
          bin.install_symlink prefix/"oixCloud Helper.app/Contents/MacOS/oixcloud-helper" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-amd64.zip"
        sha256 "43da8f57cd56819188961287aaa5ba00f9c1b587701aee71f994b3b799e2e665"

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
