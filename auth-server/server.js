const express = require('express');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Secret key (in production, use environment variable)
const JWT_SECRET = 'your-secret-key-change-in-production';
const TOKEN_EXPIRY = '1h';

// Simple in-memory users (for demo)
const users = [
  { id: 1, username: 'admin', password: 'admin123', role: 'admin' },
  { id: 2, username: 'user', password: 'user123', role: 'user' },
  { id: 3, username: 'guest', password: 'guest123', role: 'guest' }
];

// Role permissions
const permissions = {
  admin: ['read', 'create', 'update', 'delete'],
  user: ['read', 'create', 'update'],
  guest: ['read']
};

// POST /auth/login - Get JWT token
app.post('/auth/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password required' });
  }

  const user = users.find(u => u.username === username && u.password === password);

  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Create JWT token
  const token = jwt.sign(
    {
      userId: user.id,
      username: user.username,
      role: user.role,
      permissions: permissions[user.role]
    },
    JWT_SECRET,
    { expiresIn: TOKEN_EXPIRY }
  );

  console.log(`[AUTH] User '${username}' logged in with role '${user.role}'`);

  res.json({
    message: 'Login successful',
    token,
    user: {
      id: user.id,
      username: user.username,
      role: user.role,
      permissions: permissions[user.role]
    }
  });
});

// POST /auth/verify - Verify JWT token
app.post('/auth/verify', (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    console.log(`[AUTH] Token verified for user '${decoded.username}'`);
    res.json({ valid: true, user: decoded });
  } catch (err) {
    console.log(`[AUTH] Token verification failed: ${err.message}`);
    res.status(401).json({ valid: false, error: 'Invalid or expired token' });
  }
});

// POST /auth/check-permission - Check if user has permission
app.post('/auth/check-permission', (req, res) => {
  const authHeader = req.headers.authorization;
  const { permission } = req.body;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  if (!permission) {
    return res.status(400).json({ error: 'Permission required' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const hasPermission = decoded.permissions.includes(permission);

    console.log(`[AUTH] Permission check: user '${decoded.username}' ${hasPermission ? 'has' : 'lacks'} '${permission}' permission`);

    res.json({
      allowed: hasPermission,
      user: decoded.username,
      role: decoded.role,
      requestedPermission: permission
    });
  } catch (err) {
    res.status(401).json({ allowed: false, error: 'Invalid or expired token' });
  }
});

// GET /auth/users - List users (admin only demo endpoint)
app.get('/auth/users', (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET);

    if (decoded.role !== 'admin') {
      console.log(`[AUTH] Access denied: user '${decoded.username}' tried to access admin endpoint`);
      return res.status(403).json({ error: 'Admin access required' });
    }

    console.log(`[AUTH] Admin '${decoded.username}' accessed user list`);
    res.json(users.map(u => ({ id: u.id, username: u.username, role: u.role })));
  } catch (err) {
    res.status(401).json({ error: 'Invalid or expired token' });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`[AUTH] Authorization server running on http://localhost:${PORT}`);
  console.log(`[AUTH] Available users: admin/admin123, user/user123, guest/guest123`);
});
