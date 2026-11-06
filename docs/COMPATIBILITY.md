# Compatibility and evidence

| Device/platform | Version | Evidence |
| --- | --- | --- |
| Samsung QN85C (2023), actual Tizen 9.0 | Starter v2.0.11 + Cobalt v2.1.1 | Owner reported successful remote launch; modern service API revision opened in roughly 10 seconds after restart. Timing was observational, not a controlled benchmark. |
| Same hardware | Community v2.1.0 and v2.1.1 previews | Automated checks only; physical-TV validation pending for both. |
| Other Samsung TVs or Tizen releases | Any | Unverified; reports welcome. |

The config's inherited `required_version="3.0"` is not evidence of Tizen 3–8 support. The launcher uses modern `wrt:service`, `fetch`, AbortController and dynamic import. Model year alone does not establish the installed OS.

## Device checklist

### Ordinary device checks

These checks need only your remote and TV. Advanced networking/file inspection is optional.

1. Fully restart the TV. Do not manually start a service from a computer.
2. Select **TizenTube Starter** with the remote. Record the time until Cobalt opens and any visible error.
3. Confirm the native interface appears, play a video, and check a TizenTube settings/feature screen. One video without ads does not establish ad blocking.
4. Repeat after another full restart, then after normal standby/resume.
5. Check the Home tile, loading screen and Back-to-exit behavior. If a startup fails, check that the error appears within about 30 seconds and OK retries. Successful starts need not display an error.
6. Report the model family, actual Tizen version, Starter/Cobalt/installer versions, and which checks you observed. Omit serials, DUIDs, account data and household network details.

A warm launch alone does not establish cold-start recovery. Without the optional port check below, report whether the proxy was initially stopped as **not checked**, rather than inferring it from a restart. No exhaustive restart, long-playback or cross-model evaluation has been established.

### Optional advanced network checks

These are for contributors diagnosing startup/privacy behavior. Confirm the TV is reachable first. A port timeout can indicate network filtering and does not by itself prove a stopped service.

Before selecting Starter, test 8101 from the installation computer:

```sh
# macOS terminal; replace the placeholder with this TV's current address.
TV_IP='CURRENT_TV_IP'
nc -z -v -G 3 "$TV_IP" 8101
# Linux netcat equivalent:
nc -z -v -w 3 "$TV_IP" 8101
```

PowerShell alternative: `$TV_IP = 'CURRENT_TV_IP'`, then `Test-NetConnection -ComputerName $TV_IP -Port 8101 -InformationLevel Quiet`. False means the connection was not established, not a diagnosis of why.

After opening Starter, check health and HTTP log rejection:

```sh
# macOS/Linux; keep TV_IP set to this TV's actual address.
curl --noproxy '*' --connect-timeout 3 --max-time 5 -i "http://$TV_IP:8101/__tthealth"
curl --noproxy '*' --connect-timeout 3 --max-time 5 -s -o /dev/null -w 'HTTP %{http_code}\n' "http://$TV_IP:8101/__ttlog"
```

Expect health **HTTP 200** with body `ok`, and logs **HTTP 404**. On PowerShell, use `curl.exe`, `$TV_IP = '...'`, and replace `/dev/null` with `NUL`. The log-check command discards the body so an old service's viewing logs are not printed. A 200 on the log route may mean a legacy service is still running; fully restart and investigate. Health alone is not proof of playback or an authenticated service identity.

### Optional developer-only persistent-log check

This requires an authorized **service debugger with Node.js filesystem access**. The installer GUI and ordinary network checks do not provide this access; if unavailable, record **not checked**. Never enable diagnostics just to test the default behavior.

In that service debugger, take this metadata-only snapshot before and after ordinary playback:

```js
(function () {
  var fs = require('fs');
  return ['/home/owner/share/tizentube-diag.log', '/home/owner/share/tizentube-diag.log.1'].map(function (file) {
    if (!fs.existsSync(file)) return {file: file, exists: false};
    var stat = fs.statSync(file);
    return {file: file, exists: true, size: stat.size, modified: String(stat.mtime)};
  });
}())
```

With default diagnostics disabled, no new diagnostic file or changed metadata is expected from this service. Old files are not automatically erased, and another running legacy service can still write them. Do not collect or post their contents. This check is separate from HTTP log rejection.

## Prior experiments

| Experiment | Recorded result |
| --- | --- |
| Official v2.1.1 installed with Apps2Samsung and Partner signing | Installed; proxy absent after restart, network error. |
| Official installer instead of Apps2Samsung | Same startup symptom. |
| Manual official service start with SDB | Proxy became reachable; diagnostic YouTube request returned HTTP 200. |
| Replace loopback with current TV LAN IP | Proxy still stopped after restart. An initial run was confounded by an address change. |
| Add `type="ui"` to official service metadata | Did not restore startup; reverted. |
| Official v2.0.1 | Owner reported working, with slower loading and softer thumbnails. |
| Initial community Starter/cache patches | Worked; owner reported roughly 30 seconds loading. |
| Modern service API launcher | Owner reported roughly 10 seconds and successful opening; later visual changes were approved. |

These observations apply to one setup. They do not establish a universal Tizen defect or prove that signing, LAN addressing, or other installers never matter. The repeated blocker measured here was a stopped service.
