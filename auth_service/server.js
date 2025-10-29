const express = require('express');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs')
const app = express()
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

const users = [
    {
        id : 1, 
        username : 'duong',
        password : 'password'
    }
]

const authenticate = (req, res) => {
    const {username, password} = req.body

    const user = users.find(user => user.username === username);
    if (!user) { 
        return res.status(401).json({error : 'Invalid username or password'});
    }

    // const valid = bcrypt.compareSync(password, user.password);
    const valid = (password === user.password);
    
    if (!valid) {
        return res.status(401).json({error : 'Invalid username or password'});
    }

    // Header is auto-generated
    // Only define payload
    // Signature is also auto-generated
    // Token type: Bearer
    // https://curity.medium.com/the-different-token-types-and-formats-explained-19dd8b947b2e
    const token = jwt.sign(
        {sub: user.id.toString(), username: user.username}, // Payload
        SECRET, // Signing key
        {expiresIn: '1m'}
    );

    // Access token: The signed JWT token, returned by the server
    // Bearer token: The same token, sent by user
    res.json({access_token: token, token_type: 'Bearer'});
}
app.post('/token', authenticate);

app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    next();
})
PORT = 3000
app.listen(PORT, () => {
    console.log(`Auth server running on http://localhost:${PORT}`)
})