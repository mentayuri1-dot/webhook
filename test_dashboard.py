#!/usr/bin/env python3
"""
Test script to demonstrate the webhook dashboard functionality
"""

import requests
import time
import threading

def send_test_requests():
    """Send test requests to the webhook"""
    # Send a POST request
    post_data = {
        "event": "user_signup",
        "user_id": 12345,
        "email": "test@example.com",
        "timestamp": "2023-01-01T12:00:00Z"
    }
    
    print("Sending POST request...")
    response = requests.post(
        "http://localhost:5000/",
        json=post_data,
        headers={"User-Agent": "Test-Client/1.0", "X-Test-Header": "test-value"}
    )
    print(f"POST Response: {response.status_code} - {response.json()}")
    
    # Send a GET request
    print("\nSending GET request...")
    response = requests.get(
        "http://localhost:5000/",
        params={"event": "user_login", "user_id": 67890},
        headers={"User-Agent": "Test-Client/1.0"}
    )
    print(f"GET Response: {response.status_code} - {response.json()}")

def check_dashboard():
    """Check the dashboard endpoint"""
    print("\nChecking dashboard...")
    try:
        response = requests.get("http://localhost:5000/dashboard")
        print(f"Dashboard Response: {response.status_code}")
        if response.status_code == 200:
            print("Dashboard is accessible!")
        else:
            print("Dashboard returned an error")
    except Exception as e:
        print(f"Could not access dashboard: {e}")

if __name__ == "__main__":
    print("Webhook Dashboard Test")
    print("=" * 30)
    
    # Send test requests
    send_test_requests()
    
    # Wait a moment for requests to be processed
    time.sleep(2)
    
    # Check dashboard
    check_dashboard()
    
    print("\nTo view the requests:")
    print("1. Make sure the webhook is running")
    print("2. Open your browser and go to: http://localhost:5000/dashboard")
    print("3. You should see the requests you just sent")