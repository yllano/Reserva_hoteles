const express = require('express');
const admin = require('firebase-admin');
const cors = require('cors');
const dotenv = require('dotenv');
const serviceAccount = require('./serviceAccountKey.json');

dotenv.config();

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();
const app = express();

app.use(cors());
app.use(express.json());

// ── Validación de Gateway ───────────────────────────────────────────
const GATEWAY_SECRET = process.env.GATEWAY_SECRET || 'gateway-secret-reserva-hoteles-2024';

app.use((req, res, next) => {
  const secret = req.headers['x-gateway-secret'];
  if (secret !== GATEWAY_SECRET) {
    return res.status(401).json({
      error: 'Acceso directo no permitido',
      message: 'Esta petición debe pasar por el API Gateway en http://localhost:8000/api. No accedas directamente al microservicio.',
    });
  }
  next();
});

const hotelRoutes = require('./routes/hotels');
app.use('/api/hotels', hotelRoutes);

const PORT = process.env.PORT || 8002;
app.listen(PORT, () => {
  console.log(`Hotels Microservice running on port ${PORT}`);
});

module.exports = { db };
