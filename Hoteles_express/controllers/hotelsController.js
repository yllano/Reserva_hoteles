const admin = require('firebase-admin');

const db = admin.firestore();
const collection = db.collection('hotels');

exports.createHotel = async (req, res) => {
  try {
    const data = req.body;
    const docRef = await collection.add(data);
    res.status(201).json({ id: docRef.id, ...data });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getHotels = async (req, res) => {
  try {
    const city = req.query.city;
    let query = collection;
    if (city) {
      query = query.where('city', '==', city);
    }
    const snapshot = await query.get();
    const hotels = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    res.json(hotels);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getHotelById = async (req, res) => {
  try {
    const doc = await collection.doc(req.params.id).get();
    if (!doc.exists) return res.status(404).json({ message: 'Hotel not found' });
    res.json({ id: doc.id, ...doc.data() });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.updateHotel = async (req, res) => {
  try {
    const data = req.body;
    await collection.doc(req.params.id).update(data);
    res.json({ id: req.params.id, ...data });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.deleteHotel = async (req, res) => {
  try {
    await collection.doc(req.params.id).delete();
    res.json({ message: 'Hotel deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
