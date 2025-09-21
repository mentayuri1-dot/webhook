from flask import Flask, request, jsonify, render_template_string
import requests
import logging
import json
from datetime import datetime
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage for requests (in production, use a database)
received_requests = []
response_templates = []

# Configuration
REDIRECT_URL = Config.REDIRECT_URL
LISTEN_PORT = Config.LISTEN_PORT
HOST = Config.HOST

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Webhook Redirector</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .requests { margin-top: 30px; }
        .request { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
        .request-header { background-color: #f9f9f9; padding: 10px; margin: -15px -15px 15px -15px; border-bottom: 1px solid #ddd; }
        .method { font-weight: bold; color: #007acc; }
        .url { color: #666; }
        .timestamp { color: #999; font-size: 0.9em; }
        .data { background-color: #f8f8f8; padding: 10px; margin: 10px 0; border-radius: 3px; }
        .actions { margin-top: 15px; }
        button { background-color: #007acc; color: white; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #005a9e; }
        .response-form { margin-top: 15px; display: none; }
        textarea { width: 100%; height: 100px; }
        .health { background-color: #dff0d8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .error { background-color: #f2dede; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Webhook Redirector</h1>
            <p>Listening on: {{ host }}:{{ port }}</p>
            <p>Redirecting to: {{ redirect_url }}</p>
        </div>
        
        {% if health_status == "healthy" %}
        <div class="health">
            <h3>System Status: Healthy</h3>
            <p>All systems operational</p>
        </div>
        {% else %}
        <div class="error">
            <h3>System Status: Error</h3>
            <p>{{ health_message }}</p>
        </div>
        {% endif %}
        
        <div class="actions">
            <button onclick="refreshRequests()">Refresh Requests</button>
            <button onclick="clearRequests()">Clear All Requests</button>
        </div>
        
        <div class="requests">
            <h2>Received Requests ({{ requests|length }})</h2>
            {% if requests %}
                {% for req in requests|reverse %}
                <div class="request">
                    <div class="request-header">
                        <span class="method">{{ req.method }}</span>
                        <span class="url">{{ req.url }}</span>
                        <span class="timestamp">{{ req.timestamp }}</span>
                    </div>
                    <h4>Headers:</h4>
                    <div class="data">
                        <pre>{{ req.headers|tojson(indent=2) }}</pre>
                    </div>
                    {% if req.data %}
                    <h4>Data:</h4>
                    <div class="data">
                        <pre>{{ req.data|tojson(indent=2) }}</pre>
                    </div>
                    {% endif %}
                    {% if req.query_params %}
                    <h4>Query Parameters:</h4>
                    <div class="data">
                        <pre>{{ req.query_params|tojson(indent=2) }}</pre>
                    </div>
                    {% endif %}
                    <div class="actions">
                        <button onclick="toggleResponseForm('response-form-{{ req.id }}')">Respond to Request</button>
                        <div id="response-form-{{ req.id }}" class="response-form">
                            <h4>Send Response:</h4>
                            <textarea id="response-text-{{ req.id }}" placeholder='{"status": "success", "message": "Response received"}'>{"status": "success"}</textarea>
                            <br><br>
                            <label>Status Code: <input type="number" id="status-code-{{ req.id }}" value="200" min="100" max="599"></label>
                            <br><br>
                            <button onclick="sendResponse('{{ req.id }}')">Send Response</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p>No requests received yet.</p>
            {% endif %}
        </div>
    </div>
    
    <script>
        function refreshRequests() {
            location.reload();
        }
        
        function clearRequests() {
            if (confirm('Are you sure you want to clear all requests?')) {
                fetch('/clear-requests', { method: 'POST' })
                    .then(() => location.reload());
            }
        }
        
        function toggleResponseForm(formId) {
            const form = document.getElementById(formId);
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }
        
        function sendResponse(requestId) {
            const responseText = document.getElementById('response-text-' + requestId).value;
            const statusCode = document.getElementById('status-code-' + requestId).value;
            
            fetch('/respond/' + requestId, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    response: responseText,
                    status_code: parseInt(statusCode)
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            })
            .catch(error => {
                alert('Error sending response: ' + error);
            });
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def webhook_handler():
    """Handle both GET and POST requests and redirect them"""
    # Store request information
    request_info = {
        'id': str(len(received_requests) + 1),
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data': None,
        'query_params': None
    }
    
    try:
        if request.method == 'POST':
            logger.info("Received POST request")
            # Get JSON data if available
            if request.is_json:
                data = request.get_json()
                request_info['data'] = data
            else:
                # Handle form data or raw data
                data = request.get_data(as_text=True)
                if data:
                    try:
                        # Try to parse as JSON
                        request_info['data'] = json.loads(data)
                    except:
                        # If not JSON, store as raw string
                        request_info['data'] = data
            
            # Store request info
            received_requests.append(request_info)
            
            # Forward the request to the redirect URL
            if REDIRECT_URL:
                try:
                    response = requests.post(
                        REDIRECT_URL,
                        json=data if request.is_json else None,
                        data=data if not request.is_json else None,
                        headers=dict(request.headers)
                    )
                    
                    logger.info(f"Forwarded POST request to {REDIRECT_URL}")
                    return jsonify({
                        "status": "success",
                        "message": "POST request forwarded",
                        "redirect_status": response.status_code
                    }), 200
                except Exception as e:
                    logger.error(f"Error forwarding request: {str(e)}")
                    return jsonify({
                        "status": "success",
                        "message": "POST request received",
                        "forward_error": str(e)
                    }), 200
            else:
                # If no redirect URL, just acknowledge receipt
                return jsonify({
                    "status": "success",
                    "message": "POST request received"
                }), 200
                
        elif request.method == 'GET':
            logger.info("Received GET request")
            # Get query parameters
            params = request.args.to_dict()
            request_info['query_params'] = params
            
            # Store request info
            received_requests.append(request_info)
            
            # Forward the request to the redirect URL
            if REDIRECT_URL:
                try:
                    response = requests.get(
                        REDIRECT_URL,
                        params=params,
                        headers=dict(request.headers)
                    )
                    
                    logger.info(f"Forwarded GET request to {REDIRECT_URL}")
                    return jsonify({
                        "status": "success",
                        "message": "GET request forwarded",
                        "redirect_status": response.status_code
                    }), 200
                except Exception as e:
                    logger.error(f"Error forwarding request: {str(e)}")
                    return jsonify({
                        "status": "success",
                        "message": "GET request received",
                        "forward_error": str(e)
                    }), 200
            else:
                # If no redirect URL, just acknowledge receipt
                return jsonify({
                    "status": "success",
                    "message": "GET request received"
                }), 200
                
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/dashboard')
def dashboard():
    """Web interface to view and respond to requests"""
    health_status = "healthy"
    health_message = ""
    
    try:
        # Test if redirect URL is accessible
        if REDIRECT_URL:
            requests.get(REDIRECT_URL, timeout=5)
    except Exception as e:
        health_status = "warning"
        health_message = f"Redirect URL not accessible: {str(e)}"
    
    return render_template_string(
        HTML_TEMPLATE,
        requests=received_requests,
        host=HOST,
        port=LISTEN_PORT,
        redirect_url=REDIRECT_URL,
        health_status=health_status,
        health_message=health_message
    )

@app.route('/respond/<request_id>', methods=['POST'])
def respond_to_request(request_id):
    """Send a custom response to a specific request"""
    try:
        data = request.get_json()
        response_text = data.get('response', '{}')
        status_code = data.get('status_code', 200)
        
        # Parse response text if it's JSON string
        try:
            response_data = json.loads(response_text)
        except:
            response_data = response_text
        
        # Find the request
        request_found = False
        for req in received_requests:
            if req['id'] == request_id:
                request_found = True
                break
        
        if request_found:
            return jsonify(response_data), status_code
        else:
            return jsonify({"status": "error", "message": "Request not found"}), 404
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear-requests', methods=['POST'])
def clear_requests():
    """Clear all stored requests"""
    global received_requests
    received_requests = []
    return jsonify({"status": "success", "message": "All requests cleared"})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "redirect_url": REDIRECT_URL,
        "listen_port": LISTEN_PORT
    }), 200

def main():
    """Main function to run the webhook"""
    logger.info(f"Starting webhook listener on {HOST}:{LISTEN_PORT}")
    logger.info(f"Redirecting requests to {REDIRECT_URL}")
    logger.info(f"Dashboard available at http://{HOST}:{LISTEN_PORT}/dashboard")
    app.run(host=HOST, port=LISTEN_PORT, debug=Config.DEBUG)

if __name__ == '__main__':
    main()