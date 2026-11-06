# Installation

This guide uses the Apps2Samsung **desktop app**. You do not need to build source or use a terminal for the normal installation.

## 1. Gather the downloads

You need a Samsung TV with Developer Mode, a computer on the same home network, and a Samsung account for signing. Record the TV's model family and actual Tizen version from its settings/device information. QN85C running Tizen 9.0 is the only recorded hardware baseline; this new preview still needs physical-TV testing. Read [compatibility](COMPATIBILITY.md) before experimenting on another model.

| Download | Choose this file |
| --- | --- |
| [Apps2Samsung desktop v3.1.0](https://github.com/Apps2Samsung/Apps2Samsung/releases/tag/v3.1.0) | macOS Apple silicon: `Apps2Samsung-v3.1.0-macos-arm64.dmg`; Intel Mac: `...-macos-x64.dmg`. Windows x64: `...-win-x64.msi` or the portable `...-win-x64.zip`. Linux: the `.deb`, `.rpm` or AppImage matching your architecture. |
| [Official TizenTube Cobalt v2.1.1](https://github.com/reisxd/TizenTube/releases/tag/v2.1.1) | Expand **Assets** and download `TizenTubeCobalt.wgt`. Do not choose GitHub's automatic source ZIP for installation. |
| [Starter preview v2.1.1-rc.1](https://github.com/Sumanthkolla07/tizentube-starter/releases/tag/v2.1.1-rc.1) | Download `TizenTubeStarter-2.1.1.wgt` and `SHA256SUMS.txt`. The community source kit is optional. |

Install/open the Apps2Samsung desktop app using your operating system's usual installer flow. Extract the Windows portable ZIP before running its app. On macOS, check **About This Mac** if you are unsure which processor you have. For newer installer versions or OS-specific launch problems, follow [Apps2Samsung's own instructions](https://github.com/Apps2Samsung/Apps2Samsung#readme); this walkthrough's control names are checked against v3.1.0.

Optional download verification: compute the WGT's SHA-256 and compare it with the matching line in `SHA256SUMS.txt`:

- macOS: `shasum -a 256 TizenTubeStarter-2.1.1.wgt`
- Linux: `sha256sum TizenTubeStarter-2.1.1.wgt`
- Windows PowerShell: `Get-FileHash .\TizenTubeStarter-2.1.1.wgt -Algorithm SHA256`

The official Cobalt v2.1.1 WGT used for development has SHA-256 `d5ebcf5b61e907912d5200b033f0d366717cb952c9f543a6332d36bef771b3b5`. Hashes apply to the original downloads; signing changes the files.

## 2. Enable Developer Mode on the TV

1. Find the TV's current LAN IP in its network settings. Find the computer's current IP on the same network. Use those current values, not addresses copied from a guide.
2. On the TV open **Apps → App Settings**, then enter **12345** on the remote number keypad. Entering it on the general Apps browsing page may do nothing on newer interfaces.
3. Turn Developer Mode on and set **Host PC IP** to the installation computer's actual LAN IP.
4. Hold Power until the Samsung logo appears for a full restart; a short press is standby.
5. Open Apps2Samsung and select this TV. If discovery does not find it, use the installer's manual-address option. Check the displayed model/address and follow its readiness messages if Developer Mode, host address or restart status is wrong. Do not proceed against a different TV.

Developer Mode UI/API status can briefly disagree after restart. A fresh successful installer connection to the intended TV matters more than an old saved device-information response.

## 3. Prepare destination-TV signing

In Apps2Samsung v3.1.0, open **Settings → Installing → Signing**, and set **Certificate → Partner**. Select the intended TV before preparing or using its certificate. Keep **Always create a new certificate** off for normal use; it forces another sign-in rather than enabling Partner signing.

On the first install, or when preparing the certificate in Settings, a certificate window offers **Sign in with Samsung**. Complete the sign-in yourself in the browser, then return to Apps2Samsung and let certificate creation finish. If the installer shows a certificate-validity countdown, let it finish. Do not send your password, signing files or account session to this project or a friend.

Apps2Samsung creates/reuses signing material on this computer and binds the distributor certificate to the target TV's DUID. You do not need to edit a certificate manually. Keep the app's certificate store and any exported certificate backup private. A different TV needs signing coverage for that TV; a signed WGT from another household is not a portable installer.

## 4. Install both packages, in order

1. Use **Install a file** / the custom WGT file picker and select `TizenTubeCobalt.wgt`.
2. Confirm the intended TV and Partner signing setting, then start installation. Wait for the installer's completion result. An automatic direct launch of Cobalt may show the network error this workaround addresses; that is different from an installation failure.
3. Select **Install a file** again and choose `TizenTubeStarter-2.1.1.wgt`. Install it to the same TV with Partner signing and wait for completion.
4. Confirm **TizenTube** and **TizenTube Starter** both appear in the TV's Apps list or the installer's installed-app list. Installation completion alone does not prove playback works.
5. Add **TizenTube Starter** to the Home row. Keep both packages installed and open Starter with the remote for daily use. Regular Samsung YouTube can stay installed.

If an install fails, record the exact error and use [troubleshooting](TROUBLESHOOTING.md). Do not enable automatic removal or change package IDs to get past an unexplained failure. Both IDs are part of how Starter finds Cobalt.

Complete the [ordinary device checks](COMPATIBILITY.md#ordinary-device-checks) next. No computer is needed for normal daily launches after setup. Keep Host PC IP as the installation computer's LAN IP; this two-app setup is not the separate TV-Store arming workflow.

## Optional CLI installation

The recorded setup used Apple silicon CLI v3.1.0. If you prefer a terminal, download the matching `Apps2Samsung-cli-...` archive from that release, extract it, and make `apps2samsung-cli` available on PATH. Consult `--help` and `install --help` for your version. Replace every placeholder:

```sh
TV_IP='CURRENT_TV_IP'
INSTALLER_IP='CURRENT_COMPUTER_IP'
SIGNING_DIR='/absolute/private/path/to/certificate-store'
COBALT_WGT='/absolute/path/to/TizenTubeCobalt.wgt'
STARTER_WGT='/absolute/path/to/TizenTubeStarter-2.1.1.wgt'

apps2samsung-cli tv "$TV_IP" --local-ip "$INSTALLER_IP" --data-dir "$SIGNING_DIR"
apps2samsung-cli install "$COBALT_WGT" --partner --tv "$TV_IP" --local-ip "$INSTALLER_IP" --data-dir "$SIGNING_DIR"
apps2samsung-cli install "$STARTER_WGT" --partner --tv "$TV_IP" --local-ip "$INSTALLER_IP" --data-dir "$SIGNING_DIR"
```

These examples use POSIX shell syntax. For PowerShell, use `$TV_IP = '...'` assignments and corresponding PowerShell variable names. The widget version is `2.1.1`; the release tag is `v2.1.1-rc.1` because TV validation is pending.

## Updating, rollback and removal

Reuse your saved signing identity when updating Starter, keep Cobalt v2.1.1 installed, then fully restart and repeat the ordinary device checks. A running older proxy is not replaced merely by installing a new package.

An author-certificate mismatch (such as 118/-11) requires the original author certificate or a deliberate removal/reinstall. Removing an app erases its saved state; do not do it automatically. If only one package is missing, reinstall that package. Keep a privately stored known-working version for rollback and follow the same destination-TV signing rules when reinstalling it. A first-time community user has no previously validated Starter version; all public previews are explicitly unverified on a physical TV.

To remove this workaround, uninstall `TTStartr01.TizenTubeStarter`. Cobalt may stay installed, though its direct-start symptom may return. Removing regular YouTube is unnecessary.
