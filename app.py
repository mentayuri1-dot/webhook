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

# Enhanced HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Webhook Monitor - Simple UI</title>
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --success: #4cc9f0;
            --danger: #f72585;
            --warning: #f8961e;
            --info: #4895ef;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f5f7fb;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        h1 {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .config-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .config-card {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        button:hover {
            background-color: var(--secondary);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .btn-success {
            background-color: #28a745;
        }
        
        .btn-danger {
            background-color: #dc3545;
        }
        
        .btn-warning {
            background-color: #ffc107;
            color: #212529;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
        }
        
        .stat-label {
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        .requests-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
        }
        
        .requests-header {
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .request-list {
            max-height: 600px;
            overflow-y: auto;
        }
        
        .request-item {
            padding: 20px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.2s;
        }
        
        .request-item:hover {
            background-color: #f8f9fa;
        }
        
        .request-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .method-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .method-post {
            background-color: #d1ecf1;
            color: #0c5460;
        }
        
        .method-get {
            background-color: #d4edda;
            color: #155724;
        }
        
        .timestamp {
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        .request-details {
            margin: 15px 0;
        }
        
        .detail-section {
            margin-bottom: 15px;
        }
        
        .detail-title {
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--dark);
        }
        
        .detail-content {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            max-height: 200px;
            overflow: auto;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .response-form {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            display: none;
        }
        
        textarea, input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            margin: 5px 0;
            font-family: 'Courier New', monospace;
        }
        
        .empty-state {
            text-align: center;
            padding: 50px 20px;
            color: var(--gray);
        }
        
        .empty-state i {
            font-size: 3rem;
            margin-bottom: 15px;
            display: block;
        }
        
        @media (max-width: 768px) {
            .config-info {
                grid-template-columns: 1fr;
            }
            
            .stats {
                grid-template-columns: 1fr 1fr;
            }
            
            .controls {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📬 Webhook Monitor</h1>
            <p>Monitor and respond to incoming webhook requests</p>
            
            <div class="config-info">
                <div class="config-card">
                    <h3>📍 Listening Address</h3>
                    <p>{{ host }}:{{ port }}</p>
                </div>
                <div class="config-card">
                    <h3>🔄 Redirect URL</h3>
                    <p>{{ redirect_url or 'Not set (requests stored locally)' }}</p>
                </div>
                <div class="config-card">
                    <h3>📊 Status</h3>
                    <p style="color: #4cc9f0;">🟢 Running</p>
                </div>
            </div>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ requests|length }}</div>
                <div class="stat-label">Total Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ post_count }}</div>
                <div class="stat-label">POST Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ get_count }}</div>
                <div class="stat-label">GET Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ recent_count }}</div>
                <div class="stat-label">Last Hour</div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="refreshRequests()">🔄 Refresh</button>
            <button class="btn-danger" onclick="clearRequests()">🗑️ Clear All Requests</button>
            <button class="btn-success" onclick="sendTestRequest()">🧪 Send Test Request</button>
        </div>
        
        <div class="requests-container">
            <div class="requests-header">
                <h2>📥 Received Requests</h2>
                <span>{{ requests|length }} requests</span>
            </div>
            
            <div class="request-list">
                {% if requests %}
                    {% for req in requests|reverse %}
                    <div class="request-item" id="request-{{ req.id }}">
                        <div class="request-header">
                            <span class="method-badge method-{{ req.method|lower }}">{{ req.method }}</span>
                            <span class="timestamp">{{ req.timestamp }}</span>
                        </div>
                        <div class="request-url">
                            <strong>{{ req.url }}</strong>
                        </div>
                        
                        <div class="request-details">
                            {% if req.headers %}
                            <div class="detail-section">
                                <div class="detail-title">📋 Headers</div>
                                <div class="detail-content">
                                    <pre>{{ req.headers|tojson(indent=2) }}</pre>
                                </div>
                            </div>
                            {% endif %}
                            
                            {% if req.data %}
                            <div class="detail-section">
                                <div class="detail-title">📄 Data</div>
                                <div class="detail-content">
                                    <pre>{{ req.data|tojson(indent=2) }}</pre>
                                </div>
                            </div>
                            {% endif %}
                            
                            {% if req.query_params %}
                            <div class="detail-section">
                                <div class="detail-title">🔍 Query Parameters</div>
                                <div class="detail-content">
                                    <pre>{{ req.query_params|tojson(indent=2) }}</pre>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                        
                        <div class="actions">
                            <button onclick="toggleResponseForm('response-form-{{ req.id }}')">💬 Respond</button>
                        </div>
                        
                        <div id="response-form-{{ req.id }}" class="response-form">
                            <h4>Send Custom Response</h4>
                            <textarea id="response-text-{{ req.id }}" placeholder='{"status": "success", "message": "Response received"}'>{"status": "success", "message": "Request processed successfully"}</textarea>
                            <label>Status Code: 
                                <input type="number" id="status-code-{{ req.id }}" value="200" min="100" max="599">
                            </label>
                            <button class="btn-success" onclick="sendResponse('{{ req.id }}')">Send Response</button>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <div>📭</div>
                        <h3>No Requests Yet</h3>
                        <p>Send a request to http://{{ host }}:{{ port }}/ to see it here</p>
                        <button class="btn-success" onclick="sendTestRequest()" style="margin-top: 15px;">Send Test Request</button>
                    </div>
                {% endif %}
            </div>
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
                alert('Response sent successfully!');
                // Hide the response form after sending
                document.getElementById('response-form-' + requestId).style.display = 'none';
            })
            .catch(error => {
                alert('Error sending response: ' + error);
            });
        }
        
        function sendTestRequest() {
            fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Webhook Monitor UI',
                    'X-Test-Request': 'true'
                },
                body: JSON.stringify({
                    message: 'This is a test request from the Webhook Monitor UI',
                    timestamp: new Date().toISOString(),
                    test: true
                })
            })
            .then(() => {
                alert('Test request sent! Refresh to see it.');
                setTimeout(() => location.reload(), 1000);
            })
            .catch(error => {
                alert('Error sending test request: ' + error);
            });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            // Only refresh if we're not in the middle of filling out a form
            if (!document.querySelector('.response-form[style*="block"]')) {
                location.reload();
            }
        }, 30000);
    </script>
</body>
</html>
'''

def count_requests_by_method(method):
    """Count requests by HTTP method"""
    return len([req for req in received_requests if req['method'] == method])

def count_recent_requests(hours=1):
    """Count requests from the last hour"""
    now = datetime.now()
    count = 0
    for req in received_requests:
        try:
            req_time = datetime.strptime(req['timestamp'], '%Y-%m-%d %H:%M:%S')
            if (now - req_time).total_seconds() < hours * 3600:
                count += 1
        except:
            pass
    return count

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
    return render_template_string(
        HTML_TEMPLATE,
        requests=received_requests,
        host=HOST,
        port=LISTEN_PORT,
        redirect_url=REDIRECT_URL,
        post_count=count_requests_by_method('POST'),
        get_count=count_requests_by_method('GET'),
        recent_count=count_recent_requests()
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
        "listen_port": LISTEN_PORT,
        "total_requests": len(received_requests)
    }), 200

def main():
    """Main function to run the webhook"""
    logger.info(f"Starting webhook listener on {HOST}:{LISTEN_PORT}")
    logger.info(f"Redirecting requests to {REDIRECT_URL}")
    logger.info(f"Dashboard available at http://{HOST}:{LISTEN_PORT}/dashboard")
    
    # For Dokploy, we need to ensure we bind to all interfaces
    app.run(host='0.0.0.0', port=LISTEN_PORT, debug=Config.DEBUG)

if __name__ == '__main__':
    main()