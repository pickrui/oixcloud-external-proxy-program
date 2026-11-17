class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.73"
  license :cannot_represent

  url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-legacy.zip"
  sha256 "3445a677bf6390c43bd427ce69e68abd1ba0e646bbda98dda23d5ee60141cbde"

  depends_on macos: :monterey

  on_macos do
    on_sonoma :or_newer do
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-arm64.zip"
        sha256 "916ef0c92cd33d98d64bf5488d704e13095c5216e5095150fb8893df83eb1558"

        def install
          (prefix/"oixCloud Helper.app").install "Contents"
          bin.install_symlink prefix/"oixCloud Helper.app/Contents/MacOS/oixcloud-helper" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-helper-amd64.zip"
        sha256 "fb14885cf2a9a77dc0a284af7f295b9f3a7b1b4005dcffe32c106055df2dfa80"

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
