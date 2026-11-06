#!/usr/bin/env python3
"""Add diagnostic logging to TizenTube Cobalt's proxy (service/dist/index.js).

Behaviour is unchanged; the patch only records events. Every event is appended to
/home/owner/share/tizentube-diag.log on the TV. When that file passes 2 MB it is
renamed to tizentube-diag.log.1 (replacing the older one), so at most ~4 MB is kept.

The log survives restarts and is served as plain text at http://<TV IP>:8101/__ttlog:
  /__ttlog          last 500 lines across both files (spans restarts)
  /__ttlog?all=1    both files in full
  /__ttlog?clear=1  delete both files and start over

usage: patch_diag.py <extracted wgt dir> [label]
  label (optional) is added to the start-up line, e.g. "Starter copy", to tell copies apart.
"""
import sys
import pathlib

root = pathlib.Path(sys.argv[1])
label = sys.argv[2] if len(sys.argv) > 2 else ""
tag = " [" + label + "]" if label else ""
js_path = root / "service" / "dist" / "index.js"
js = js_path.read_text(encoding="utf-8")

LOGGER = r"""function startServer() {
  var __ttT0 = Date.now();
  var __ttLog = [];
  var __ttFile = '/home/owner/share/tizentube-diag.log';
  var __ttOld = __ttFile + '.1';
  function ttlog(msg) {
    var line = new Date().toISOString() + ' +' + (Date.now() - __ttT0) + 'ms ' + msg;
    __ttLog.push(line);
    if (__ttLog.length > 500) __ttLog.shift();
    try {
      if (fs.existsSync(__ttFile) && fs.statSync(__ttFile).size > 2000000) fs.renameSync(__ttFile, __ttOld);
      fs.appendFileSync(__ttFile, line + '\n');
    } catch (e) {}
  }
  function ttread(all) {
    var text = '';
    try {
      if (fs.existsSync(__ttOld)) text += fs.readFileSync(__ttOld, 'utf8');
      if (fs.existsSync(__ttFile)) text += fs.readFileSync(__ttFile, 'utf8');
    } catch (e) {
      return __ttLog.join('\n') + '\n(log file unreadable: ' + (e && e.message) + '; showing this session only)\n';
    }
    if (!text) return __ttLog.join('\n') + '\n';
    if (all) return text;
    var lines = text.split('\n');
    return lines.slice(Math.max(0, lines.length - 501)).join('\n');
  }
  try { process.on('uncaughtException', function (e) { ttlog('UNCAUGHT ' + (e && e.stack || e)); }); } catch (e) {}
  try { process.on('unhandledRejection', function (e) { ttlog('UNHANDLED REJECTION ' + (e && e.stack || e)); }); } catch (e) {}
  // Only SIGTERM is observed, and its default outcome (the process ends) is kept.
  // Other signals are left alone: the TV may use them for normal service housekeeping.
  try {
    process.once('SIGTERM', function () {
      ttlog('SIGNAL SIGTERM received - the TV is shutting the service down');
      process.exit(143);
    });
  } catch (e) {}
  try { process.on('exit', function (code) { ttlog('EXIT code ' + code); }); } catch (e) {}
  var __ttOs = null;
  try { __ttOs = require('os'); } catch (e) {}
  var __ttConns = 0;
  // Diagnostics must never break the proxy: every probe is guarded, because the TV's
  // sandbox may block some of them (e.g. reading the process's own memory figures).
  function mb(n) { return Math.round(n / 1048576) + 'MB'; }
  function ttstats() {
    var parts = [];
    try { var m = process.memoryUsage(); parts.push('rss ' + mb(m.rss) + ' heap ' + mb(m.heapUsed) + '/' + mb(m.heapTotal)); }
    catch (e) { parts.push('mem n/a (' + (e && (e.code || e.message)) + ')'); }
    try { parts.push('TV free ' + mb(__ttOs.freemem()) + '/' + mb(__ttOs.totalmem())); } catch (e) { parts.push('TV mem n/a'); }
    parts.push('conns ' + __ttConns);
    return parts.join(' | ');
  }
  var __ttLastStats = '';
  try {
    var __ttTimer = setInterval(function () {
      try {
        var s = ttstats();
        if (s !== __ttLastStats) { ttlog('STATS ' + s); __ttLastStats = s; }
      } catch (e) {}
    }, 5000);
    if (__ttTimer && __ttTimer.unref) __ttTimer.unref();
  } catch (e) {}
  var __ttStart = '';
  try { __ttStart = ttstats(); } catch (e) { __ttStart = 'stats failed'; }
  ttlog('=== proxy service start@@TAG@@, node ' + process.version + ' pid ' + process.pid + ' | ' + __ttStart);
"""

def replace_once(old, new):
    global js
    count = js.count(old)
    if count != 1:
        sys.exit(f"expected exactly 1 match, found {count}: {old[:80]!r}")
    js = js.replace(old, new)

# 1. logger at the top of startServer()
replace_once("function startServer() {\n", LOGGER.replace("@@TAG@@", tag))

# 2. time each certificate key generation
replace_once(
    "  function createHostCertificate(hostname) {\n    var keys = forge.pki.rsa.generateKeyPair(2048);\n",
    "  function createHostCertificate(hostname) {\n    var __kg = Date.now();\n    var keys = forge.pki.rsa.generateKeyPair(2048);\n"
    "    ttlog('keygen ' + hostname + ' took ' + (Date.now() - __kg) + 'ms');\n",
)

# 3. tunnelled (non-YouTube) connections: start, connected, errors, close
replace_once(
    "  function tunnel(hostname, port, clientSocket, initialData) {\n    var targetSocket = net.connect(port, hostname, function () {\n",
    "  function tunnel(hostname, port, clientSocket, initialData) {\n    var __t = Date.now();\n    ttlog('TUNNEL start ' + hostname + ':' + port);\n"
    "    var targetSocket = net.connect(port, hostname, function () {\n"
    "      ttlog('TUNNEL connected ' + hostname + ':' + port + ' in ' + (Date.now() - __t) + 'ms via ' + targetSocket.remoteAddress);\n",
)
replace_once(
    "    targetSocket.on('error', function () {\n      return clientSocket.destroy();\n    });\n    clientSocket.on('error', function () {\n      return targetSocket.destroy();\n    });\n  }\n",
    "    targetSocket.on('error', function (e) {\n      ttlog('TUNNEL upstream ERROR ' + hostname + ':' + port + ' after ' + (Date.now() - __t) + 'ms: ' + (e && e.code) + ' ' + (e && e.message));\n      return clientSocket.destroy();\n    });\n"
    "    clientSocket.on('error', function (e) {\n      ttlog('TUNNEL client ERROR ' + hostname + ': ' + (e && e.code));\n      return targetSocket.destroy();\n    });\n  }\n",
)

# 4. intercepted YouTube requests: each request, its status and time, and errors
replace_once(
    "        var isTvPath = request.url === '/tv' || request.url.startsWith('/tv?');\n",
    "        var __r = Date.now();\n        __req = true;\n        ttlog('MITM ' + request.method + ' ' + hostname + request.url.slice(0, 120));\n"
    "        var isTvPath = request.url === '/tv' || request.url.startsWith('/tv?');\n",
)
replace_once(
    "        }, function (targetResponse) {\n          var headers = Object.assign({}, targetResponse.headers);\n",
    "        }, function (targetResponse) {\n          ttlog('MITM ' + targetResponse.statusCode + ' ' + hostname + request.url.slice(0, 80) + ' first byte ' + (Date.now() - __r) + 'ms');\n"
    "          targetResponse.on('end', function () { ttlog('MITM done ' + hostname + request.url.slice(0, 80) + ' ' + (Date.now() - __r) + 'ms'); });\n"
    "          var headers = Object.assign({}, targetResponse.headers);\n",
)
replace_once(
    "        targetRequest.on('error', function (error) {\n          response.destroy();\n        });\n",
    "        targetRequest.on('error', function (error) {\n          ttlog('MITM upstream ERROR ' + hostname + request.url.slice(0, 80) + ' after ' + (Date.now() - __r) + 'ms: ' + (error && error.code) + ' ' + (error && error.message));\n          response.destroy();\n        });\n",
)
replace_once(
    "    tlsServer.on('secureConnection', function (clientTlsSocket) {\n",
    "    var __secured = false;\n"
    "    clientSocket.on('close', function () {\n"
    "      if (!__secured) ttlog('MITM app closed ' + hostname + ' before TLS finished (it likely rejected the proxy certificate)');\n"
    "    });\n"
    "    tlsServer.on('secureConnection', function (clientTlsSocket) {\n      __secured = true;\n"
    "      var __req = false;\n"
    "      clientTlsSocket.on('close', function () {\n"
    "        if (!__req) ttlog('MITM app closed ' + hostname + ' without sending a request (it likely rejected the proxy certificate for this name)');\n"
    "      });\n",
)
replace_once(
    "    tlsServer.on('tlsClientError', function () {\n      clientSocket.destroy();\n    });\n",
    "    tlsServer.on('tlsClientError', function (e) {\n      ttlog('MITM TLS handshake with app FAILED for ' + hostname + ': ' + (e && e.code) + ' ' + (e && e.message));\n      clientSocket.destroy();\n    });\n",
)

# 5. plain-HTTP handler: serve the log at /__ttlog
replace_once(
    "  var proxyServer = http.createServer(function (request, response) {\n    var targetUrl = url.parse(request.url);\n",
    "  var proxyServer = http.createServer(function (request, response) {\n"
    "    if (request.url.indexOf('/__ttlog') === 0) {\n"
    "      if (request.url.indexOf('clear=1') !== -1) {\n"
    "        __ttLog = [];\n"
    "        try { fs.unlinkSync(__ttOld); } catch (e) {}\n"
    "        try { fs.unlinkSync(__ttFile); } catch (e) {}\n"
    "        ttlog('log cleared');\n"
    "      }\n"
    "      response.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });\n"
    "      return response.end(ttread(request.url.indexOf('all=1') !== -1));\n"
    "    }\n"
    "    var targetUrl = url.parse(request.url);\n",
)

# 6. every CONNECT from the app, and when the proxy starts listening
replace_once(
    "  proxyServer.on('connect', function (request, clientSocket, initialData) {\n    var reqUrl = request.url.split(':');\n",
    "  proxyServer.on('connect', function (request, clientSocket, initialData) {\n    ttlog('CONNECT ' + request.url + ' from ' + clientSocket.remoteAddress);\n"
    "    __ttConns++;\n    clientSocket.once('close', function () { __ttConns--; });\n"
    "    var reqUrl = request.url.split(':');\n",
)
replace_once(
    "  proxyServer.listen(proxyPort, '0.0.0.0');\n}\nmodule.exports = startServer;",
    "  proxyServer.on('error', function (e) { ttlog('PROXY SERVER ERROR ' + (e && e.code) + ' ' + (e && e.message)); });\n"
    "  proxyServer.listen(proxyPort, '0.0.0.0', function () { ttlog('LISTENING on 0.0.0.0:' + proxyPort); });\n}\nmodule.exports = startServer;",
)

js_path.write_text(js, encoding="utf-8")
print("patched", js_path)
