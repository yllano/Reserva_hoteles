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

const hotelRoutes = require('./routes/hotels');
app.use('/api/hotels', hotelRoutes);

const PORT = process.env.PORT || 8002;
app.listen(PORT, () => {
  console.log(`Hotels Microservice running on port ${PORT}`);
});

module.exports = { db };
