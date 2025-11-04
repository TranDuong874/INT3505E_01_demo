import express from 'express';
import jwt from 'jsonwebtoken';
import bodyParser from 'body-parser';
import bcrypt from 'bcryptjs';
import crypto from 'crypto';

const app = express();
app.use(bodyParser.json());

// CORS: reflect origin and requested headers; handle preflight
app.use((req, res, next) => {
    const origin = req.headers.origin || '*';
    const reqHeaders = req.headers['access-control-request-headers'];
    res.header('Access-Control-Allow-Origin', origin);
    res.header('Vary', 'Origin');
    res.header('Access-Control-Allow-Methods', 'GET,POST,PATCH,PUT,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', reqHeaders || 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
    if (req.method === 'OPTIONS') {
        return res.status(204).end();
    }
    next();
});

const SECRET = 'demo-secret-key';
const REFRESH_SECRET = 'demo-refresh-secret-key';
const ISSUER = 'http://localhost:3000';
const AUDIENCE = 'flask-api';

// In-memory store for refresh tokens (use Redis or DB in production)
const refreshTokenStore = new Map();

const users = [
    {
        id: 1,
        username: 'duong',
        password: 'password',
        roles: ['admin'],
        scopes: [
            'books:read',
            'books:write',
            'borrows:read',
            'borrows:write',
            'users:read',
            'users:write',
            'posts:read',
            'posts:write'
        ]
    },
    {
        id: 2,
        username: 'user1',
        password: 'password',
        roles: ['user'],
        scopes: [
            'books:read',
            'borrows:read',
            'posts:read',
            'posts:write'
        ]
    }
];

const generateAccessToken = (user) => {
    return jwt.sign(
        {
            sub: user.id.toString(),
            username: user.username,
            roles: user.roles,
            scope: user.scopes.join(' ')  // Space-separated scopes
        },
        SECRET,
        {
            expiresIn: '15m',  // Short-lived access token
            issuer: ISSUER,
            audience: AUDIENCE
        }
    );
};

const generateRefreshToken = (user) => {
    const tokenId = crypto.randomBytes(32).toString('hex');
    const refreshToken = jwt.sign(
        {
            sub: user.id.toString(),
            tokenId: tokenId,
            type: 'refresh'
        },
        REFRESH_SECRET,
        {
            expiresIn: '7d',  // Long-lived refresh token
            issuer: ISSUER,
            audience: AUDIENCE
        }
    );
    
    // Store refresh token with user info
    refreshTokenStore.set(tokenId, {
        userId: user.id,
        username: user.username,
        createdAt: Date.now()
    });
    
    return refreshToken;
};

const authenticate = (req, res) => {
    const { username, password } = req.body;

    const user = users.find(u => u.username === username);
    if (!user) {
        return res.status(401).json({ error: 'Invalid username or password' });
    }

    // const valid = bcrypt.compareSync(password, user.password);
    const valid = (password === user.password);
    
    if (!valid) {
        return res.status(401).json({ error: 'Invalid username or password' });
    }

    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);

    res.json({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'Bearer',
        expires_in: 900,  // 15 minutes in seconds
        scope: user.scopes.join(' ')
    });
};

const refresh = (req, res) => {
    const { refresh_token } = req.body;

    if (!refresh_token) {
        return res.status(400).json({ error: 'refresh_token is required' });
    }

    try {
        // Verify refresh token
        const decoded = jwt.verify(refresh_token, REFRESH_SECRET, {
            issuer: ISSUER,
            audience: AUDIENCE
        });

        // Check if it's a refresh token
        if (decoded.type !== 'refresh') {
            return res.status(401).json({ error: 'Invalid token type' });
        }

        // Check if token exists in store
        const storedToken = refreshTokenStore.get(decoded.tokenId);
        if (!storedToken || storedToken.userId !== parseInt(decoded.sub)) {
            return res.status(401).json({ error: 'Invalid refresh token' });
        }

        // Find user
        const user = users.find(u => u.id === storedToken.userId);
        if (!user) {
            return res.status(401).json({ error: 'User not found' });
        }

        // Generate new access token (and optionally new refresh token)
        const accessToken = generateAccessToken(user);
        
        res.json({
            access_token: accessToken,
            token_type: 'Bearer',
            expires_in: 900
        });

    } catch (err) {
        return res.status(401).json({ error: 'Invalid or expired refresh token', details: err.message });
    }
};

const revoke = (req, res) => {
    const { refresh_token } = req.body;

    if (!refresh_token) {
        return res.status(400).json({ error: 'refresh_token is required' });
    }

    try {
        const decoded = jwt.verify(refresh_token, REFRESH_SECRET);
        
        // Remove from store
        refreshTokenStore.delete(decoded.tokenId);
        
        res.json({ message: 'Token revoked successfully' });
    } catch (err) {
        return res.status(400).json({ error: 'Invalid token' });
    }
};

app.post('/token', authenticate);
app.post('/token/refresh', refresh);
app.post('/token/revoke', revoke);

app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    next();
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Auth server running on http://localhost:${PORT}`);
});