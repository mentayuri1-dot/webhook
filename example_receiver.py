from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook_receiver():
    """Example receiver endpoint for webhook requests"""
    if request.method == 'POST':
        logger.info("Received POST webhook")
        
        # Get JSON data if available
        if request.is_json:
            data = request.get_json()
            logger.info(f"JSON data received: {data}")
        else:
            # Handle form data or raw data
            data = request.get_data(as_text=True)
            logger.info(f"Raw data received: {data}")
        
        # Get headers
        headers = dict(request.headers)
        logger.info(f"Headers received: {headers}")
        
        return jsonify({
            "status": "received",
            "message": "POST webhook received successfully",
            "data": data if request.is_json else None
        }), 200
        
    elif request.method == 'GET':
        logger.info("Received GET webhook")
        
        # Get query parameters
        params = request.args.to_dict()
        logger.info(f"Query parameters received: {params}")
        
        # Get headers
        headers = dict(request.headers)
        logger.info(f"Headers received: {headers}")
        
        return jsonify({
            "status": "received",
            "message": "GET webhook received successfully",
            "params": params
        }), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Webhook receiver is running",
        "endpoints": {
            "webhook": "/webhook (GET and POST)",
            "dashboard": "Webhook redirector dashboard at /dashboard"
        }
    }), 200

@app.route('/test-response', methods=['GET', 'POST'])
def test_response():
    """Test endpoint that returns different responses"""
    return jsonify({
        "message": "This is a test response from the receiver",
        "timestamp": "2023-01-01T12:00:00Z",
        "test_data": {
            "id": 123,
            "name": "Test Item"
        }
    }), 200

if __name__ == '__main__':
    logger.info("Starting webhook receiver on http://localhost:8080")
    app.run(host='localhost', port=8080, debug=True)