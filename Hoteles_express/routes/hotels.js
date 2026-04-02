const express = require('express');
const router = express.Router();
const hotelsController = require('../controllers/hotelsController');

router.post('/', hotelsController.createHotel);
router.get('/', hotelsController.getHotels);
router.get('/:id', hotelsController.getHotelById);
router.put('/:id', hotelsController.updateHotel);
router.delete('/:id', hotelsController.deleteHotel);

module.exports = router;
