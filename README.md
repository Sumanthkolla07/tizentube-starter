# TizenTube Starter

An unofficial TV-only launcher for **TizenTube Cobalt**. It starts a bundled proxy service before opening TizenTube, for setups where launching Cobalt directly produces a network error because its service has not started. After installation, select the Starter tile with the TV remote; a computer is not needed for daily launches.

**Status: community preview, v2.1.0-rc.1.** The previous v2.0.11 launcher was observed working on Samsung QN85C with Tizen 9.0. This revision adds privacy defaults and replaces artwork; it has automated checks but **has not been tested on a physical TV**. Other models/platforms are unverified. This is launch-on-selection, not a guarantee of launch at TV power-on.

## Install

1. Read the [installation guide](docs/INSTALL.md), including Developer Mode and destination-TV signing.
2. Get official **TizenTube Cobalt v2.1.1** from its [upstream release](https://github.com/reisxd/TizenTube/releases/tag/v2.1.1).
3. Get the unsigned Starter and optional source/reinstall kit from [Releases](https://github.com/Sumanthkolla07/tizentube-starter/releases). Sign/install both for your TV, Cobalt first.
4. Open **TizenTube Starter** and complete the [restart/playback checks](docs/COMPATIBILITY.md).

Each TV needs appropriate signing coverage. An unsigned WGT is not a one-click universal installer. Do not share private certificates or account credentials with friends.

## Documentation

- [Installation and removal](docs/INSTALL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Compatibility and experiment evidence](docs/COMPATIBILITY.md)
- [Architecture, source provenance, and reproducible builds](docs/DEVELOPMENT.md)
- [Privacy and security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Source and artwork attribution](ATTRIBUTION.md)

## Build and check

Python 3 builds the included source without npm dependencies. Node.js 18+ runs the behavioral checks.

```sh
python3 tizentube-handoff/build.py
python3 -m unittest discover -s tests -p '*_test.py'
node --test tests/proxy.test.cjs
```

The unsigned output is `tizentube-handoff/packages/TizenTubeStarter-2.1.0.wgt`. To reproduce the bundled proxy from the checksum-pinned official package, follow [DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Privacy and scope

Persistent proxy diagnostics are disabled by default; startup uses a separate health endpoint. The proxy still listens on the LAN for compatibility. Use only on a trusted home network and never port-forward it. Read [SECURITY.md](SECURITY.md) before installing.

This project is independent of Samsung, Google/YouTube, TizenTube, and Apps2Samsung. It retains upstream code and notices under [GPL-3.0](LICENSE); artwork and third-party dependencies have their own notices. It neither supplies accounts nor changes subscription entitlements.
