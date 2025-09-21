import requests
import json

def test_post_request():
    """Test sending a POST request to the webhook"""
    url = "http://localhost:5000/"
    
    # Sample data
    data = {
        "event": "test_event",
        "payload": {
            "id": 123,
            "name": "Test Item",
            "timestamp": "2023-01-01T00:00:00Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Test-Client/1.0"
    }
    
    print("Sending POST request to webhook...")
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_get_request():
    """Test sending a GET request to the webhook"""
    url = "http://localhost:5000/"
    params = {
        "event": "test_event",
        "id": "123"
    }
    
    headers = {
        "User-Agent": "Test-Client/1.0"
    }
    
    print("Sending GET request to webhook...")
    response = requests.get(url, params=params, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("Testing Webhook Redirector")
    print("=" * 30)
    
    print("\n1. Testing POST Request:")
    test_post_request()
    
    print("\n2. Testing GET Request:")
    test_get_request()