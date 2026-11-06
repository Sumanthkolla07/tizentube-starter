# Installation

## Before starting

You need a Samsung TV with Developer Mode, its current LAN address, a computer on the same network, and a Samsung account for signing. QN85C running Tizen 9.0 is the only recorded hardware baseline; see [compatibility](COMPATIBILITY.md). The new community package still needs physical-TV testing.

Download official TizenTube Cobalt v2.1.1 from [upstream](https://github.com/reisxd/TizenTube/releases/tag/v2.1.1) and Starter from this project's [Releases](https://github.com/Sumanthkolla07/tizentube-starter/releases). Verify the Starter asset against its release `SHA256SUMS.txt` using `shasum -a 256 FILE` (macOS) or `sha256sum FILE` (Linux). The official v2.1.1 WGT used for development has SHA-256 `d5ebcf5b61e907912d5200b033f0d366717cb952c9f543a6332d36bef771b3b5`.

## Enable Developer Mode

1. Find the TV's current IP and the installation computer's current IP. Do not copy another household's addresses.
2. On the TV, open **Apps → App Settings**, then enter **12345** on the remote number keypad. Entering it on the general Apps browsing page may do nothing on newer interfaces.
3. Turn Developer Mode on and enter the actual computer's LAN IP as Host PC IP.
4. Hold Power until the Samsung logo appears to perform a full restart; a short press is standby.
5. Verify the current device identity and bridge connection. Developer Mode UI/API status can briefly disagree; inspect fresh results.

## Sign and install

Use [Apps2Samsung](https://github.com/Apps2Samsung/Apps2Samsung). The recorded setup used Apple silicon CLI v3.1.0; consult your installed version's help rather than assuming newer CLI options are identical.

Install **official Cobalt first**, then **Starter**, using a Samsung **Partner** certificate covering the destination TV's DUID. Complete Samsung sign-in yourself. Keep the certificate store private and persistent. For another TV, obtain signing coverage for that TV; do not pass around your private identity.

The desktop route is Custom WGT → Force Samsung Certificate → Partner signing. Example CLI, with placeholders you must replace:

```sh
TV_IP='CURRENT_TV_IP'
INSTALLER_IP='CURRENT_COMPUTER_IP'
SIGNING_DIR='/absolute/private/path/to/certificate-store'
COBALT_WGT='/absolute/path/to/TizenTubeCobalt.wgt'
STARTER_WGT='/absolute/path/to/TizenTubeStarter-2.1.0.wgt'

apps2samsung-cli tv "$TV_IP" --local-ip "$INSTALLER_IP" --data-dir "$SIGNING_DIR"
apps2samsung-cli install "$COBALT_WGT" --partner --tv "$TV_IP" --local-ip "$INSTALLER_IP" --data-dir "$SIGNING_DIR"
apps2samsung-cli install "$STARTER_WGT" --partner --tv "$TV_IP" --local-ip "$INSTALLER_IP" --data-dir "$SIGNING_DIR"
```

The widget version is `2.1.0`; the community release tag is `v2.1.0-rc.1` because TV validation is pending.

Put Starter on the Home row, keep both apps installed, and use Starter daily. Regular Samsung YouTube may remain installed. Do not replace Host PC IP with loopback just because an older guide says so.

## Verify, update, and remove

Complete [the device checklist](COMPATIBILITY.md#device-checklist) after installation and after updates. Warm-launch success alone does not establish cold-start recovery.

An author-certificate mismatch (such as 118/-11) requires the original author certificate or a deliberate removal/reinstall. Removing an app erases its saved state; do not do it automatically. If only one package is missing, reinstall that package.

To remove this workaround, uninstall `TTStartr01.TizenTubeStarter`. Cobalt can stay installed, though its direct-start symptom may return. Uninstalling regular YouTube is unnecessary. Keep a privately stored known-working version for rollback, and follow the same signing rules when reinstalling it.
