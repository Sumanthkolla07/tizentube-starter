# Compatibility and evidence

| Device/platform | Version | Evidence |
| --- | --- | --- |
| Samsung QN85C (2023), actual Tizen 9.0 | Starter v2.0.11 + Cobalt v2.1.1 | Owner reported successful remote launch; modern service API revision opened in roughly 10 seconds after restart. Timing was observational, not a controlled benchmark. |
| Same hardware | Community v2.1.0 / release v2.1.0-rc.1 | Automated packaging and privacy/readiness checks pass locally; physical-TV validation pending. |
| Other Samsung TVs or Tizen releases | Any | Unverified; reports welcome. |

The config's inherited `required_version="3.0"` is not evidence of Tizen 3–8 support. The launcher uses modern `wrt:service`, `fetch`, AbortController and dynamic import. Model year alone does not establish the installed OS.

## Device checklist

1. Full restart; do not start the proxy manually from a computer.
2. Establish whether 8101 was closed before launching, so an already-running service does not mask startup behavior.
3. Select Starter with the remote and record startup time and any error.
4. Verify the native interface, actual video playback, and a TizenTube feature/settings screen. One ad-free video is not proof of ad blocking.
5. Repeat after another full restart and after standby/resume.
6. Check external tile, loading screen, OK retry and Back exit.
7. For community v2.1.0, verify `/__tthealth` responds, `/__ttlog` returns 404 from another LAN device, and normal use creates no new persistent diagnostic entries. Existing old logs need not be erased automatically.

Report the model family, actual Tizen version, both package versions, installer version, and each observed result. Omit device identifiers and network details. No exhaustive restart, long playback, or cross-model evaluation has been established.

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
