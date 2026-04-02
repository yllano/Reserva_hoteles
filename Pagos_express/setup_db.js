const db = require('./db');

const initDb = async () => {
    try {
        await db.query(`
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                reservation_id INTEGER NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(20) DEFAULT 'success',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);
        console.log('Transactions table checked/created');
        process.exit(0);
    } catch (err) {
        console.error('Error initializing db:', err);
        process.exit(1);
    }
};

initDb();
