# Architecture and builds

Starter probes `http://127.0.0.2:8101/__tthealth`, starts its own `wrt:service` proxy if needed, polls readiness, then launches official Cobalt. It carries its own service because cross-package service startup was restricted in the recorded setup.

| Item | Identifier |
| --- | --- |
| Official app | `xvvl3S1TT1.TizenTubeStandalone` |
| Official service | `xvvl3S1TT1.StandaloneService` |
| Starter app/package | `TTStartr01.TizenTubeStarter` / `TTStartr01` |
| Starter service | `TTStartr01.ProxyService` |
| Proxy / ancillary / developer bridge | 8101 / 8100 / 26101 |

Readiness requests abort after 1.5 seconds. A 30-second deadline covers the entire launch attempt: readiness probes, runtime import, service startup, and the Cobalt launch callback. Timeout restores OK retry; Back cancels the attempt. The Samsung service API cannot be forcibly cancelled, so attempt IDs prevent its late results from launching an app or interfering with a retry. Existing-listener readiness does not prove that the modern runtime API ran.

## Pinned inputs

- TizenTube v2.1.1 source commit: `893b663d35efa558d8bdf9f54f0c4f9a31ab6a07` in [reisxd/TizenTube](https://github.com/reisxd/TizenTube/tree/893b663d35efa558d8bdf9f54f0c4f9a31ab6a07).
- Community startup/cache patches: `8294d135566b1074a78249086ac16897d0f7203d` in [cgrkz/tizentube-cobalt-coldstart-fix](https://github.com/cgrkz/tizentube-cobalt-coldstart-fix/tree/8294d135566b1074a78249086ac16897d0f7203d).
- Official binary: [TizenTubeCobalt.wgt v2.1.1](https://github.com/reisxd/TizenTube/releases/download/v2.1.1/TizenTubeCobalt.wgt), SHA-256 `d5ebcf5b61e907912d5200b033f0d366717cb952c9f543a6332d36bef771b3b5`.

`vendor/tizentube/` contains the editable upstream service/mod source snapshots and build configuration; the two original patch scripts live in `scripts/patches/`. The standalone service declared semver dependency ranges and did not provide a lockfile in this tag (other upstream components do include lockfiles). Do not claim that a fresh npm install recreates the release's entire dependency graph. The distributed bundle retains its embedded third-party notices.

The verified packaging path deliberately uses the exact checksum-pinned upstream bundle, then applies the two pinned community patches and `patch_privacy.py`. Before the privacy patch, this reproduced the historical v2.0.11 proxy byte for byte. This keeps the release dependency bytes fixed without resolving new npm versions. The vendor source is for inspection/development; a new full dependency build requires a separately reviewed lockfile and TV validation.

```sh
# Download the official package yourself from the pinned release above, then:
python3 scripts/rebuild_proxy.py /absolute/path/to/TizenTubeCobalt.wgt
python3 tizentube-handoff/build.py
python3 -m unittest discover -s tests -p '*_test.py'
node --test tests/launcher.test.cjs tests/proxy.test.cjs
node --check tizentube-handoff/source/service/dist/index.js
```

Python uses fixed ZIP timestamps, permissions and entry order for repeatable unsigned WGT packaging within the same Python/zlib toolchain. Signing changes the package and is destination-TV-specific. Release tags may have an `-rc` suffix; Tizen widget versions use numeric `2.1.1`.

## Release process

1. Update source, version, compatibility evidence and changelog together. Rebuild the proxy if a patch changes.
2. Run checks. The Node tests execute the generated proxy module with a simulated TV runtime; they verify endpoint/diagnostic behavior and the launcher deadline, stale results, retry and Back handling. They do not validate Samsung API integration, TLS playback or networking.
3. Run `python3 scripts/make_share_kit.py` from a clean checkout, then `python3 scripts/verify_share_kit.py`. Assets are written to `dist/v2.1.1-rc.1/`; this versioned directory keeps older downloads out of a new release. The verifier checks every source-manifest entry, extracts to a temporary directory and rebuilds a byte-identical unsigned WGT. Cobalt is linked upstream rather than redistributed.
4. Upload the WGT, source kit and generated `SHA256SUMS.txt` to a tagged GitHub release. Use a prerelease while device validation is pending.
5. Test on a TV before declaring a stable release. Never include signing identities or actual installation state.

Public build products go in ignored `dist/` and `tizentube-handoff/packages/`; local setup belongs in ignored `local/`. The repository history is a clean community baseline, not the original private backup history.

## Public automated checks

The [Checks workflow](https://github.com/Sumanthkolla07/tizentube-starter/actions/workflows/checks.yml) runs on pushes to main, pull requests and manual dispatch. It runs the Python and Node suites, bundle syntax check, share-kit construction, manifest validation and clean-extraction rebuild on Ubuntu, macOS and Windows using Python 3.11 and Node.js 22. Actions are pinned to full official commit SHAs and have read-only repository permissions. Passing CI does not establish real-TV compatibility.

To compare a source kit manually after rebuilding, compare `packages/TizenTubeStarter-2.1.1.wgt` (the bundled unsigned package) with `tizentube-handoff/packages/TizenTubeStarter-2.1.1.wgt` (your rebuild). On macOS/Linux use `cmp FILE1 FILE2`; no output and exit 0 mean identical. On Windows compare the two `Get-FileHash -Algorithm SHA256` results. Signing changes the bytes; compare before signing. Different Python/zlib versions can change compressed bytes even if package contents agree. CI records its tool versions in the job log.
