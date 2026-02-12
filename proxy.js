// Simple reverse proxy: /api/* → FastAPI (8100), everything else → Flutter web (8101)
const http = require('http');

const FLUTTER_PORT = 8101;
const API_PORT = 8100;
const LISTEN_PORT = 8102;

const server = http.createServer((req, res) => {
  const isApi = req.url.startsWith('/api');
  const targetPort = isApi ? API_PORT : FLUTTER_PORT;

  const options = {
    hostname: '127.0.0.1',
    port: targetPort,
    path: req.url,
    method: req.method,
    headers: req.headers,
  };

  const proxy = http.request(options, (proxyRes) => {
    // Add CORS headers for API
    if (isApi) {
      proxyRes.headers['access-control-allow-origin'] = '*';
      proxyRes.headers['access-control-allow-methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
      proxyRes.headers['access-control-allow-headers'] = 'Content-Type, Authorization';
    }
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxy.on('error', (err) => {
    res.writeHead(502);
    res.end(`Proxy error: ${err.message}`);
  });

  req.pipe(proxy);
});

server.listen(LISTEN_PORT, '0.0.0.0', () => {
  console.log(`TaxLens proxy listening on :${LISTEN_PORT}`);
  console.log(`  /api/* → :${API_PORT} (FastAPI)`);
  console.log(`  /*     → :${FLUTTER_PORT} (Flutter web)`);
});
