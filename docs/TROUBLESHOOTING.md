# Troubleshooting

First check TV power, current address, and network reachability. Do not diagnose the app from an old saved device-information response.

| Symptom | Next check |
| --- | --- |
| Direct Cobalt launch shows a network error | Open Starter; on the recorded TV Cobalt's service was absent after restart. |
| TV API and developer bridge unreachable | Check current IP, power, network, Developer Mode and installer host address. |
| Port 8101 refuses connections | Proxy is not listening. Changing DNS cannot start a stopped service. |
| Port 8101 answers but hostname requests hang | Investigate upstream DNS/network independently of service startup. |
| Startup timed out | The whole launch attempt exceeded 30 seconds. Press OK to retry; if repeated, fully restart the TV and confirm both packages remain installed. The prior API operation may still finish, but its late result is ignored by Starter. |
| Couldn’t open TizenTube | Confirm official Cobalt is installed under its original app ID; press OK after correcting the install. |
| Service API unavailable / couldn’t start background service | Check the actual Tizen version against compatibility limits; use Back to exit or restart before another attempt. |
| Another proxy already owns 8101 | Restart and identify the listener; official and Starter services can race. |
| Author certificate mismatch | Reuse the signing identity, or deliberately reinstall after considering saved-data loss. |
| Modern service API unavailable | Report the actual Tizen version. There is no verified legacy fallback. |

See [ordinary and advanced verification](COMPATIBILITY.md#device-checklist) for optional port, endpoint and metadata-only file checks.

Starter stores its last startup status and elapsed time in its local storage as `lastStartup`. Its method label does not prove which runtime branch executed, especially if a proxy was already running.

The community service exposes `http://TV_IP:8101/__tthealth` with only `ok`. This checks a listener, not video playback or TizenTube feature activation. Startup polls this endpoint on `127.0.0.2`; a no-CORS response is opaque, so readiness is not identity authentication.

For macOS diagnostics with your actual TV address:

```sh
nc -z -v -G 3 "$TV_IP" 8101
curl --connect-timeout 3 --max-time 5 "http://$TV_IP:8101/__tthealth"
```

`nc -G` is macOS-specific. Logs from old v2.0.11 packages may still exist and remain LAN-readable while that old service is running. Upgrading Starter does not rewrite a separately running legacy service. See [SECURITY.md](../SECURITY.md).

For a one-time investigation, Samsung SDB can start the official service:

```sh
sdb connect "$TV_IP"
sdb -s "$TV_IP:26101" shell 0 execute xvvl3S1TT1.StandaloneService
```

This restored connectivity in the recorded investigation; it is not the daily solution or proof of boot recovery. Apps2Samsung CLI `launch` used a different verb and did not reproduce this service command. Do not substitute Android ADB blindly.

Do not post raw viewing logs, TV DUIDs, serial numbers, signing material, account data, or full network-information dumps in issues.
