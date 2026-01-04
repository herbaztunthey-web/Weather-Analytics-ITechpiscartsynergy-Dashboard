const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const port = process.env.PORT || 3000;

const db = new sqlite3.Database('./final_weather.db');

// This URL (localhost:3000/api/weather) will show your data
// Add this below your other app.get route
app.get('/api/history', (req, res) => {
    const sql = "SELECT city, temperature, search_time FROM weather ORDER BY id DESC LIMIT 5";
    db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});
app.listen(port, () => {
    console.log(`🚀 Weather Server running at http://localhost:${port}/api/weather`);
});