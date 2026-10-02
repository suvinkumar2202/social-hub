const express = require('express');
const cors = require('cors');
const session = require('express-session');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({
  secret: 'social-media-secret',
  resave: false,
  saveUninitialized: true,
}));

const db = new sqlite3.Database(path.join(__dirname, 'data.db'), (err) => {
  if (err) {
    console.error('Failed to connect to database:', err.message);
  } else {
    console.log('Connected to SQLite database');
  }
});

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
  db.run(`CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
  )`);
  db.run(`CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(post_id) REFERENCES posts(id)
  )`);
});

const upload = multer({ dest: 'uploads/' });

app.get('/api/status', (req, res) => {
  res.json({ status: 'ok', database: 'sqlite3 connected' });
});

app.post('/api/register', (req, res) => {
  const { username, email, password } = req.body;
  if (!username || !email || !password) {
    return res.status(400).json({ error: 'All fields are required' });
  }
  const stmt = db.prepare('INSERT INTO users (username, email, password) VALUES (?, ?, ?)');
  stmt.run(username, email, password, function(err) {
    if (err) {
      if (err.message.includes('UNIQUE constraint failed')) {
        return res.status(409).json({ error: 'Username or email already exists' });
      }
      return res.status(500).json({ error: err.message });
    }
    res.json({ success: true, user_id: this.lastID });
  });
  stmt.finalize();
});

app.post('/api/posts', (req, res) => {
  const { user_id, content } = req.body;
  if (!user_id || !content) {
    return res.status(400).json({ error: 'user_id and content are required' });
  }
  const stmt = db.prepare('INSERT INTO posts (user_id, content) VALUES (?, ?)');
  stmt.run(user_id, content, function(err) {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ success: true, post_id: this.lastID });
  });
  stmt.finalize();
});

app.get('/api/posts', (req, res) => {
  db.all(`SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.created_at DESC`, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ posts: rows });
  });
});

app.post('/api/posts/:id/like', (req, res) => {
  const { user_id } = req.body;
  const postId = req.params.id;
  if (!user_id) {
    return res.status(400).json({ error: 'user_id is required' });
  }
  db.run('INSERT OR IGNORE INTO likes (user_id, post_id) VALUES (?, ?)', [user_id, postId], function(err) {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ success: true, liked: this.changes > 0 });
  });
});

app.get('/api/posts/:id/likes', (req, res) => {
  const postId = req.params.id;
  db.get('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', [postId], (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ count: row.count });
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
