#!/usr/bin/env python3
"""Apply community privacy changes after the pinned upstream patches."""
from pathlib import Path
import sys

def patch(js):
    replacements = [
        ("  var __ttT0 = Date.now();", "  var __ttDiagnostics = process.env.TIZENTUBE_DIAGNOSTICS === '1';\n  var __ttT0 = Date.now();"),
        ("  function ttlog(msg) {", "  function ttlog(msg) {\n    if (!__ttDiagnostics) return;"),
    ]
    for old, new in replacements:
        if js.count(old) != 1:
            raise ValueError('Expected one patch anchor: ' + old)
        js = js.replace(old, new, 1)
    start = js.index("    if (request.url.indexOf('/__ttlog') === 0) {")
    end = js.index('    var targetUrl = url.parse(request.url);', start)
    js = js[:start] + """    if (request.url.split('?')[0] === '/__tthealth') {
      response.writeHead(200, { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' });
      return response.end('ok\\n');
    }
    // Never serve logs over HTTP: proxy relaying can make LAN clients appear local.
    if (request.url.indexOf('/__ttlog') === 0) {
      response.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
      return response.end('Not found\\n');
    }
""" + js[end:]
    return js

if __name__ == '__main__':
    target = Path(sys.argv[1]) / 'service/dist/index.js'
    target.write_text(patch(target.read_text()))
