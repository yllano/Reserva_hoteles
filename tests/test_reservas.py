import unittest
import sys
import os
import json
from datetime import datetime, date

# Set the environment variable BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Add the microservice directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Reservas_flask')))

from app import app, db, Reservation

class TestReservations(unittest.TestCase):

    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        # Already set via environment variable for initial load, but good to be explicit
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # --- POST /api/reservations ---

    def test_create_reservation_success(self):
        """1. Verify a valid reservation is created (201)"""
        payload = {
            "user_id": 1,
            "hotel_id": "hotel_abc",
            "check_in": "2026-06-01",
            "check_out": "2026-06-05"
        }
        response = self.client.post('/api/reservations', json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['user_id'], 1)
        self.assertEqual(data['hotel_id'], "hotel_abc")
        self.assertEqual(data['status'], 'pending')

    def test_create_reservation_pending_status(self):
        """2. Verify new reservations default to 'pending'"""
        payload = {
            "user_id": 2,
            "hotel_id": "hotel_123",
            "check_in": "2026-07-01",
            "check_out": "2026-07-05"
        }
        self.client.post('/api/reservations', json=payload)
        with app.app_context():
            res = Reservation.query.filter_by(user_id=2).first()
            self.assertEqual(res.status, 'pending')

    def test_create_reservation_overlap_failure(self):
        """3. Verify a reservation fails if there's a confirmed overlap (400)"""
        # Create a confirmed reservation first
        with app.app_context():
            res = Reservation(
                user_id=1, hotel_id="hotel_overlap", 
                check_in=date(2026, 8, 10), check_out=date(2026, 8, 15), 
                status='confirmed'
            )
            db.session.add(res)
            db.session.commit()

        # Try to book overlapping dates
        payload = {
            "user_id": 2,
            "hotel_id": "hotel_overlap",
            "check_in": "2026-08-12",
            "check_out": "2026-08-14"
        }
        response = self.client.post('/api/reservations', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('not available', response.get_json()['error'])

    def test_create_reservation_no_overlap_different_hotel(self):
        """4. Verify overlap check is hotel-specific"""
        with app.app_context():
            res = Reservation(
                user_id=1, hotel_id="hotel_A", 
                check_in=date(2026, 8, 10), check_out=date(2026, 8, 15), 
                status='confirmed'
            )
            db.session.add(res)
            db.session.commit()

        # Same dates, different hotel should succeed
        payload = {
            "user_id": 2,
            "hotel_id": "hotel_B",
            "check_in": "2026-08-10",
            "check_out": "2026-08-15"
        }
        response = self.client.post('/api/reservations', json=payload)
        self.assertEqual(response.status_code, 201)

    def test_create_reservation_no_overlap_different_time(self):
        """5. Verify overlap check respects dates (sequential bookings)"""
        with app.app_context():
            res = Reservation(
                user_id=1, hotel_id="hotel_time", 
                check_in=date(2026, 8, 10), check_out=date(2026, 8, 15), 
                status='confirmed'
            )
            db.session.add(res)
            db.session.commit()

        # Starts exactly when other ends - should succeed (check_in < check_out and check_out > check_in logic)
        payload = {
            "user_id": 2,
            "hotel_id": "hotel_time",
            "check_in": "2026-08-15",
            "check_out": "2026-08-20"
        }
        response = self.client.post('/api/reservations', json=payload)
        self.assertEqual(response.status_code, 201)

    def test_create_reservation_missing_user_id(self):
        """6. Verify error when user_id is missing (400)"""
        payload = {
            "hotel_id": "hotel_fail",
            "check_in": "2026-09-01",
            "check_out": "2026-09-05"
        }
        response = self.client.post('/api/reservations', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields', response.get_json()['error'])

    def test_create_reservation_invalid_date(self):
        """7. Verify error on malformed date string (400)"""
        payload = {
            "user_id": 1,
            "hotel_id": "hotel_date",
            "check_in": "not-a-date",
            "check_out": "2026-10-05"
        }
        response = self.client.post('/api/reservations', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid date format', response.get_json()['error'])

    # --- GET /api/reservations/user/<user_id> ---

    def test_get_user_reservations_empty(self):
        """8. Verify empty list for user with no bookings"""
        response = self.client.get('/api/reservations/user/999')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_user_reservations_populated(self):
        """9. Verify correct list of bookings for a user"""
        with app.app_context():
            db.session.add(Reservation(user_id=5, hotel_id="H1", check_in=date(2026,1,1), check_out=date(2026,1,2)))
            db.session.add(Reservation(user_id=5, hotel_id="H2", check_in=date(2026,2,1), check_out=date(2026,2,2)))
            db.session.commit()

        response = self.client.get('/api/reservations/user/5')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_get_user_reservations_multiple_users(self):
        """10. Verify user isolation (only see own bookings)"""
        with app.app_context():
            db.session.add(Reservation(user_id=10, hotel_id="U10", check_in=date(2026,1,1), check_out=date(2026,1,2)))
            db.session.add(Reservation(user_id=11, hotel_id="U11", check_in=date(2026,1,1), check_out=date(2026,1,2)))
            db.session.commit()

        response = self.client.get('/api/reservations/user/10')
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['hotel_id'], "U10")

    # --- PATCH /api/reservations/<id>/status ---

    def test_update_status_to_confirmed(self):
        """11. Change status from pending to confirmed"""
        with app.app_context():
            res = Reservation(user_id=1, hotel_id="H", check_in=date(2026,1,1), check_out=date(2026,1,2), status='pending')
            db.session.add(res)
            db.session.commit()
            res_id = res.id

        response = self.client.patch(f'/api/reservations/{res_id}/status', json={"status": "confirmed"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'confirmed')

    def test_update_status_to_canceled(self):
        """12. Change status from pending to canceled"""
        with app.app_context():
            res = Reservation(user_id=1, hotel_id="H", check_in=date(2026,1,1), check_out=date(2026,1,2), status='pending')
            db.session.add(res)
            db.session.commit()
            res_id = res.id

        response = self.client.patch(f'/api/reservations/{res_id}/status', json={"status": "canceled"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'canceled')

    def test_update_status_not_found(self):
        """13. Verify 404 for invalid ID"""
        response = self.client.patch('/api/reservations/9999/status', json={"status": "confirmed"})
        self.assertEqual(response.status_code, 404)

    def test_update_status_no_change(self):
        """14. Verify status remains same if no new status provided"""
        with app.app_context():
            res = Reservation(user_id=1, hotel_id="H", check_in=date(2026,1,1), check_out=date(2026,1,2), status='pending')
            db.session.add(res)
            db.session.commit()
            res_id = res.id

        response = self.client.patch(f'/api/reservations/{res_id}/status', json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'pending')

    # --- Model Logic ---

    def test_reservation_timestamp(self):
        """15. Verify created_at is automatically populated"""
        with app.app_context():
            res = Reservation(user_id=1, hotel_id="H", check_in=date(2026,1,1), check_out=date(2026,1,2))
            db.session.add(res)
            db.session.commit()
            self.assertIsNotNone(res.created_at)
            self.assertIsInstance(res.created_at, datetime)

if __name__ == '__main__':
    unittest.main()
