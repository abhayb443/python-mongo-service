from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'helloworlddb'
COLLECTION_NAME = 'messages'

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Validation functions
def validate_request_data(data):
    """Validate the request JSON data."""
    if not isinstance(data, dict) or 'ip_address' not in data:
        return False
    return True

def validate_headers(headers):
    """Validate required headers."""
    if 'User-Agent' not in headers:
        return False
    return True

@app.route('/api/message', methods=['POST'])
def save_message():
    """Save message data to MongoDB."""
    try:
        # Validate request body
        message_data = request.get_json()
        if not validate_request_data(message_data):
            return jsonify({'error': 'Bad Request. Missing or invalid "ip_address" key.'}), 400
        
        # Validate headers
        headers = request.headers
        if not validate_headers(headers):
            return jsonify({'error': 'Bad Request. Missing "User-Agent" header.'}), 400

        # Add User-Agent to message_data
        user_agent = headers.get('User-Agent')
        message_data['user-agent'] = user_agent

        # Insert data into MongoDB
        result = collection.insert_one({"data": message_data})
        inserted_id = str(result.inserted_id)  # Convert ObjectId to string

        return jsonify({'message': 'Message saved!', 'reference_id': inserted_id}), 200
    
    except Exception as e:
        logger.error(f"Error saving message: {str(e)}")
        return jsonify({'error': 'Internal Server Error.'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
