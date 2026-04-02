const express = require('express');
const cors = require('cors');
const axios = require('axios');
const db = require('./db');

const app = express();
app.use(cors());
app.use(express.json());

const RESERVATION_SERVICE_URL = 'http://localhost:8003/api/reservations';

// Initialize payments table
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
    } catch (err) {
        console.error('Error initializing db:', err);
    }
};
initDb();

app.post('/api/payments/process', async (req, res) => {
    const { reservation_id, amount } = req.body;

    try {
        // 1. Simulate process (90% success rate)
        const isSuccess = Math.random() < 0.95;

        if (!isSuccess) {
            return res.status(400).json({ error: 'Payment failed' });
        }

        // 2. Record transaction if success
        const result = await db.query(
            'INSERT INTO transactions (reservation_id, amount, status) VALUES ($1, $2, $3) RETURNING *',
            [reservation_id, amount, 'success']
        );

        // 3. Notify Reservation MS to confirm reservation
        await axios.patch(`${RESERVATION_SERVICE_URL}/${reservation_id}/status`, {
            status: 'confirmed'
        });

        res.status(201).json({
            message: 'Payment processed and reservation confirmed',
            transaction: result.rows[0]
        });

    } catch (err) {
        res.status(500).json({ error: 'Internal error', message: err.message });
    }
});

const PORT = 8004;
app.listen(PORT, () => {
    console.log(`Payment Microservice running on port ${PORT}`);
});
