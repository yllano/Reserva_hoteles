import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import firestore
from google.oauth2 import service_account

app = Flask(__name__)
CORS(app)

# Firebase configuration
key_path = os.path.join(os.path.dirname(__file__), 'config', 'firebase-key.json')
credentials = service_account.Credentials.from_service_account_file(key_path)
db = firestore.Client(credentials=credentials)
reviews_ref = db.collection('reviews')

@app.route('/api/reviews', methods=['POST'])
def create_review():
    try:
        data = request.json
        # Validate rating 1-5
        rating = int(data.get('rating', 0))
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            
        doc_ref = reviews_ref.add(data)
        return jsonify({'id': doc_ref[1].id, **data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews/hotel/<string:hotel_id>', methods=['GET'])
def get_hotel_reviews(hotel_id):
    try:
        docs = reviews_ref.where('hotel_id', '==', hotel_id).stream()
        reviews = [ {**doc.to_dict(), 'id': doc.id} for doc in docs ]
        return jsonify(reviews)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    try:
        docs = reviews_ref.where('user_id', '==', user_id).stream()
        reviews = [ {**doc.to_dict(), 'id': doc.id} for doc in docs ]
        return jsonify(reviews)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8005, debug=True)
