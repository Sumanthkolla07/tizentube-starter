#!/usr/bin/env python3
"""Fix TizenTube Cobalt's "Network error occurred" pop-up on cold start.

Cause (from the diagnostic log): the proxy generated two RSA-2048 certificates
(~1-2 s each on the TV) *before* it started listening on port 8101. When the app and
the proxy service start together, the app's first connection arrives during that
window, finds nothing listening and fails.

Fix:
  1. Start listening on 8101 immediately, before any certificate work.
  2. Create each YouTube certificate only when first needed, and save it to
     /home/owner/share so later starts reuse it instead of generating a new key.

Apply after patch_diag.py (it relies on the ttlog() helper that patch adds).
usage: patch_fix.py <extracted wgt dir>
"""
import sys
import pathlib

root = pathlib.Path(sys.argv[1])
js_path = root / "service" / "dist" / "index.js"
js = js_path.read_text(encoding="utf-8")

if "function ttlog(" not in js:
    sys.exit("apply patch_diag.py first")


def replace_once(old, new):
    global js
    count = js.count(old)
    if count != 1:
        sys.exit(f"expected exactly 1 match, found {count}: {old[:90]!r}")
    js = js.replace(old, new)


# 1. Load the CA lazily instead of at the top of startServer().
replace_once(
    "  var caCertificate = forge.pki.certificateFromPem(fs.readFileSync('/home/owner/share/tizentube-ca.crt', 'utf8'));\n"
    "  var caPrivateKey = forge.pki.privateKeyFromPem(fs.readFileSync('/home/owner/share/tizentube-ca.key', 'utf8'));\n",
    "  var caCertificate = null;\n"
    "  var caPrivateKey = null;\n"
    "  function loadCa() {\n"
    "    if (caCertificate) return;\n"
    "    caCertificate = forge.pki.certificateFromPem(fs.readFileSync('/home/owner/share/tizentube-ca.crt', 'utf8'));\n"
    "    caPrivateKey = forge.pki.privateKeyFromPem(fs.readFileSync('/home/owner/share/tizentube-ca.key', 'utf8'));\n"
    "  }\n",
)
replace_once(
    "  function createHostCertificate(hostname) {\n    var __kg = Date.now();\n",
    "  function createHostCertificate(hostname) {\n    loadCa();\n    var __kg = Date.now();\n",
)

# 2. Replace the eager certificate generation with cached, on-demand loading.
replace_once(
    "  var ytCertWWW = createHostCertificate('www.youtube.com');\n"
    "  var ytCert = createHostCertificate('youtube.com');\n",
    "  var __certCache = {};\n"
    "  function hostCert(hostname) {\n"
    "    if (__certCache[hostname]) return __certCache[hostname];\n"
    "    var file = '/home/owner/share/tizentube-cert-' + hostname + '.json';\n"
    "    var caFile = '/home/owner/share/tizentube-ca.crt';\n"
    "    try {\n"
    "      var st = fs.statSync(file);\n"
    "      var fresh = Date.now() - st.mtimeMs < 300 * 24 * 60 * 60 * 1000;\n"
    "      var newerThanCa = !fs.existsSync(caFile) || st.mtimeMs >= fs.statSync(caFile).mtimeMs;\n"
    "      if (fresh && newerThanCa) {\n"
    "        var saved = JSON.parse(fs.readFileSync(file, 'utf8'));\n"
    "        if (saved.key && saved.cert) {\n"
    "          ttlog('cert ' + hostname + ' loaded from cache');\n"
    "          return __certCache[hostname] = saved;\n"
    "        }\n"
    "      }\n"
    "    } catch (e) {}\n"
    "    var made = createHostCertificate(hostname);\n"
    "    try { fs.writeFileSync(file, JSON.stringify(made)); } catch (e) { ttlog('cert cache write failed: ' + (e && e.message)); }\n"
    "    return __certCache[hostname] = made;\n"
    "  }\n",
)
replace_once(
    "    var tlsServer = new tls.Server(hostname === 'www.youtube.com' ? ytCertWWW : ytCert);\n",
    "    var tlsServer = new tls.Server(hostCert(hostname === 'www.youtube.com' ? 'www.youtube.com' : 'youtube.com'));\n",
)

# 3. After listening, warm up both certificates in the background (from cache: instant).
replace_once(
    "  proxyServer.listen(proxyPort, '0.0.0.0', function () { ttlog('LISTENING on 0.0.0.0:' + proxyPort); });\n",
    "  proxyServer.listen(proxyPort, '0.0.0.0', function () {\n"
    "    ttlog('LISTENING on 0.0.0.0:' + proxyPort);\n"
    "    setTimeout(function () {\n"
    "      try { hostCert('www.youtube.com'); hostCert('youtube.com'); ttlog('certificates ready'); }\n"
    "      catch (e) { ttlog('certificate warm-up failed: ' + (e && e.stack || e)); }\n"
    "    }, 0);\n"
    "  });\n",
)

js_path.write_text(js, encoding="utf-8")
print("patched", js_path)
