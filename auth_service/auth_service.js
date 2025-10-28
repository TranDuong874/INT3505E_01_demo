import express from 'express'
import bodyParser from 'body-parser'
import jwt from 'jsonwebtoken'
import fetch from 'node-fetch'

const app = express();
app.use(bodyParser.json());

// Basic in-memory client registry (for demo)
const clients = new Map([
  [
    'demo-client',
    {
      client_id: 'demo-client',
      client_secret: 'demo-secret',
      scope: 'borrows:read borrows:write',
    },
  ],
]);

const ISSUER = process.env.ISSUER || 'http://localhost:8080';
const SHARED_SECRET = process.env.SHARED_SECRET || 'super-secret-dev-key';

// OAuth 2.0 Token endpoint (client_credentials)
app.post('/oauth/token', async (req, res) => {
  try {
    const { grant_type, client_id, client_secret, scope, audience } = req.body || {};

    if (grant_type !== 'client_credentials') {
      return res.status(400).json({ error: 'unsupported_grant_type' });
    }
    const client = clients.get(client_id);
    if (!client || client.client_secret !== client_secret) {
      return res.status(401).json({ error: 'invalid_client' });
    }
    const requestedScope = scope || client.scope;
    const now = Math.floor(Date.now() / 1000);
    const exp = now + 60 * 60; // 1 hour

    const token = jwt.sign(
      {
        scope: requestedScope,
        aud: audience || 'flask-api',
        iss: ISSUER,
        sub: client_id,
        iat: now,
        exp,
      },
      SHARED_SECRET,
      { algorithm: 'HS256' }
    );

    return res.json({
      access_token: token,
      token_type: 'Bearer',
      expires_in: exp - now,
      scope: requestedScope,
    });
  } catch (e) {
    return res.status(500).json({ error: 'server_error', details: String(e) });
  }
});

// Simple metadata
app.get('/.well-known/openid-configuration', (req, res) => {
  const base = ISSUER;
  res.json({ issuer: base, token_endpoint: `${base}/oauth/token` });
});

app.use('/api', async (req, res) => {
  try {
    const targetUrl = `http://localhost:5000${req.url.replace(/^\/api/, '')}`;
    const headers = { 'Content-Type': 'application/json' };
    const authHeader = req.headers['authorization'];
    if (authHeader) headers['Authorization'] = authHeader;
    const method = req.method.toUpperCase();
    const body = ['GET', 'HEAD'].includes(method) ? undefined : JSON.stringify(req.body || {});

    const resp = await fetch(targetUrl, { method, headers, body });
    const text = await resp.text();
    res.status(resp.status);
    const ct = resp.headers.get('content-type') || 'application/json';
    res.set('Content-Type', ct);
    res.send(text);
  } catch (e) {
    res.status(500).json({ error: 'proxy_error', details: String(e) });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`Auth service listening on http://0.0.0.0:${port}`);
});