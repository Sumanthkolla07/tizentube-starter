# Changelog

## v2.1.1-rc.1 — community preview

- Bound the whole launch attempt to 30 seconds, including runtime import, service startup, readiness and app-launch callbacks.
- Restore retry after timeout and ignore late results after timeout, retry or Back.
- Add actionable startup failure messages and regression tests.
- Complete desktop installer/signing guidance and separate ordinary checks from advanced diagnostics.
- Add pinned, read-only Ubuntu/macOS/Windows CI checks and clean-kit rebuild verification.
- Derive package names from the widget version and isolate downloads by release version.

Physical-TV validation remains pending; this release is a preview.

## v2.1.0-rc.1 — community preview

- Rewrite installation, troubleshooting and developer documentation for reuse.
- Add checksum-pinned proxy reconstruction, upstream source snapshots, and repeatable unsigned packaging.
- Disable persistent proxy diagnostics by default and remove HTTP log access entirely.
- Add a separate readiness endpoint, with no log contents, for Starter probes.
- Replace the untraced wordmark asset with an application-name loading screen; retain the attributed Font Awesome icon.
- Add endpoint/privacy checks, contribution guidance and compatibility reporting templates.

Physical-TV validation is pending. The earlier v2.0.11 setup was observed working on QN85C running Tizen 9.0; this preview changes runtime behavior and visuals and does not inherit that validation.
