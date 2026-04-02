from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:0806@localhost/reserva_hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    hotel_id = db.Column(db.String(50), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, confirmed, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Ensure database exists and tables are created
with app.app_context():
    db.create_all()

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.json
    user_id = data.get('user_id')
    hotel_id = data.get('hotel_id')
    check_in = datetime.strptime(data.get('check_in'), '%Y-%m-%d').date()
    check_out = datetime.strptime(data.get('check_out'), '%Y-%m-%d').date()

    # Availability Logic (Simplistic: no existing confirmed overlap)
    overlap = Reservation.query.filter(
        Reservation.hotel_id == hotel_id,
        Reservation.status == 'confirmed',
        Reservation.check_in < check_out,
        Reservation.check_out > check_in
    ).first()

    if overlap:
        return jsonify({'error': 'Hotel not available for these dates'}), 400

    new_reservation = Reservation(
        user_id=user_id,
        hotel_id=hotel_id,
        check_in=check_in,
        check_out=check_out,
        status='pending'
    )
    
    db.session.add(new_reservation)
    db.session.commit()

    return jsonify({
        'id': new_reservation.id,
        'user_id': new_reservation.user_id,
        'hotel_id': new_reservation.hotel_id,
        'status': new_reservation.status
    }), 201

@app.route('/api/reservations/user/<int:user_id>', methods=['GET'])
def get_user_reservations(user_id):
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': r.id,
        'hotel_id': r.hotel_id,
        'check_in': r.check_in.isoformat(),
        'check_out': r.check_out.isoformat(),
        'status': r.status
    } for r in reservations])

@app.route('/api/reservations/<int:id>/status', methods=['PATCH'])
def update_status(id):
    data = request.json
    res = Reservation.query.get(id)
    if not res:
        return jsonify({'message': 'Not found'}), 404
    
    res.status = data.get('status', res.status)
    db.session.commit()
    return jsonify({'id': res.id, 'status': res.status})

if __name__ == '__main__':
    app.run(port=8003, debug=True)
