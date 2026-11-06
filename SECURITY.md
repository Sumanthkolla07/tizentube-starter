# Privacy and security

This preview is intended for trusted home networks. It is not a hardened multi-user proxy service.

- Detailed persistent proxy diagnostics are **off by default** in community v2.1.0. The log function returns before collecting or writing messages. The health endpoint `/__tthealth` contains no viewing data.
- `/__ttlog` always returns 404, even to loopback clients when diagnostics are enabled. Restricting it only by peer IP would be bypassable through the forward proxy. A developer may opt in to **file-only** logging with service environment variable `TIZENTUBE_DIAGNOSTICS=1` in a controlled test environment, then inspect the files through their developer tooling. There is no supported consumer remote-toggle or installer switch for this option.
- Existing diagnostic files from an older package are not automatically deleted. An old running proxy can continue to expose its old endpoint until stopped; a warm upgrade does not change another process. Restart and verify the new behavior.
- Upstream error paths can still write errors to the TV system console. Disabled persistent diagnostics does not mean every dependency is silent. Review/redact any system output before sharing it.
- The inherited proxy still listens on `0.0.0.0:8101`, so LAN devices can use it. Loopback-only binding is deferred until TV testing establishes it preserves Cobalt connectivity. Never port-forward this or the developer bridge. Port 8100 is an inherited loopback listener.
- The service generates TLS interception keys and certificates on the TV. Keep them, cached certificate JSON, Samsung signing material, DUIDs, serial numbers, accounts, and raw logs private. Never include them in issues, releases or commits.
- The inherited service fetches its userscript from jsDelivr at runtime. Playback behavior can change independently of the WGT. The release is not fully offline or fully reproducible end to end.
- The health endpoint is a readiness signal, not an authenticated service identity. A different process listening on that port may satisfy an opaque startup probe.

Keep personal setup in the ignored `local/` directory. The default share-kit script uses an explicit Git-tracked allowlist and never includes that directory. `.gitignore` helps prevent accidental staging; it is not a security boundary.

## Reporting a vulnerability

Do not post secrets or raw logs in a public issue. Use GitHub private vulnerability reporting if the repository exposes that option. Otherwise open an issue containing only a general description and ask for a private reporting route before supplying sensitive details. No response-time guarantee or formal security audit is claimed.
