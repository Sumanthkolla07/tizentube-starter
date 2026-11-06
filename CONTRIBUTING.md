# Contributing

Small reproducible fixes and compatibility reports are welcome. This is an unofficial launcher workaround, not the upstream TizenTube project.

1. Read [DEVELOPMENT.md](docs/DEVELOPMENT.md), [SECURITY.md](SECURITY.md), and the compatibility limits.
2. Keep IDs stable unless proposing an explicit migration. Avoid silently changing the playback proxy, signing workflow, or remote userscript source.
3. For proxy changes, update the editable patch scripts and regenerate the bundle from the checksum-pinned WGT. Do not edit only the 4 MB generated file.
4. Run the documented Python/Node checks and include a clear behavior change and verification evidence in your pull request.
5. Separate automated evidence from real-TV observations. Report cold start, standby/resume and playback individually. Keep untested builds labeled as previews.
6. Retain upstream copyright and dependency notices. Original project contributions use the repository's GPL-3.0 terms; separately licensed assets keep their terms.

Public reports must exclude DUIDs, serials, certificates, private keys, account information, raw viewing logs, and household IP addresses. Use placeholders for network addresses.
