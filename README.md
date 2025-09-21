# Webhook Redirector

A simple Python Flask application that listens for incoming GET and POST requests and redirects them to a specified URL (your laptop or VPS). Now includes a web dashboard to view and respond to requests directly.

## Features

- Handles both GET and POST requests
- Preserves headers and data from the original request
- Configurable redirect URL via environment variables
- Configurable listening port
- Health check endpoint
- Detailed logging
- **Web dashboard to view and respond to requests** (`/dashboard`)
- In-memory storage of received requests

## Setup

### Option 1: Manual Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the application by copying the example environment file:
   ```bash
   # On Linux/Mac:
   cp .env.example .env
   
   # On Windows:
   copy .env.example .env
   ```
   
   Then edit the `.env` file to set your configuration.

3. Run the application:
   ```bash
   python app.py
   ```

### Option 2: Using Docker

1. Build and run with Docker:
   ```bash
   docker build -t webhook-redirector .
   docker run -p 5000:5000 -e REDIRECT_URL="http://your-vps-or-laptop-url:port/path" webhook-redirector
   ```

2. Or use docker-compose:
   ```bash
   docker-compose up
   ```

## Usage

Once running, the webhook will listen on the specified port (default 5000) and redirect all requests to your configured URL.

### Endpoints

- `/` - Main webhook endpoint (handles both GET and POST)
- `/dashboard` - Web interface to view and respond to requests
- `/health` - Health check endpoint

### Web Dashboard

Access the web dashboard at `http://localhost:5000/dashboard` to:
- View all received requests with their details
- See headers, data, and query parameters
- Send custom responses to requests
- Clear request history

### Examples

```bash
# Send a test POST request
curl -X POST http://localhost:5000/ -H "Content-Type: application/json" -d '{"message": "Hello World"}'

# Send a test GET request
curl -X GET "http://localhost:5000/?param1=value1&param2=value2"
```

## Testing with Example Receiver

For testing purposes, you can use the included example receiver:

1. In one terminal, start the receiver:
   ```bash
   python example_receiver.py
   ```
   
2. In another terminal, start the webhook redirector:
   ```bash
   # Set redirect URL to point to the receiver
   export REDIRECT_URL="http://localhost:8080/webhook"
   python app.py
   ```

3. Access the dashboard at `http://localhost:5000/dashboard` to view and respond to requests

## Testing the Webhook

You can test the webhook functionality using the provided test script:

```bash
python test_webhook.py
```

Or manually with curl:

```bash
# Send a test POST request
curl -X POST http://localhost:5000/ -H "Content-Type: application/json" -d '{"message": "Hello World"}'

# Send a test GET request
curl -X GET "http://localhost:5000/?param1=value1&param2=value2"
```

### Testing the Dashboard

You can also test the dashboard functionality:

```bash
python test_dashboard.py
```

Then open your browser and go to `http://localhost:5000/dashboard` to see the received requests.

## Configuration

The application can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIRECT_URL` | URL to redirect incoming requests to | http://localhost:8080/webhook |
| `LISTEN_PORT` | Port for the webhook to listen on | 5000 |
| `HOST` | Host to bind to | 0.0.0.0 |
| `DEBUG` | Enable debug mode | False |

## Deployment

### Running on a Server

To run this webhook on a server to receive external requests:

1. Set the `REDIRECT_URL` to your laptop or VPS address
2. Ensure the `LISTEN_PORT` is accessible (configure firewall if needed)
3. Run the application

### Using with Ngrok (for local testing)

If you want to test with a local machine:

1. Install ngrok: https://ngrok.com/
2. Run the webhook application locally
3. Expose it with ngrok: `ngrok http 5000`
4. Use the ngrok URL as your webhook endpoint

## Logging

The application logs all requests and forwarding actions. Check the console output for detailed information.