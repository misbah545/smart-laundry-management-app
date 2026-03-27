#!/usr/bin/env python
"""
Comprehensive API Testing Script for Smart Laundry Backend
Run this script to test all API endpoints
"""

import requests
import json
from pprint import pprint

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

# Test credentials (you'll need to create these users first)
TEST_CUSTOMER = {
    "username": "testcustomer",
    "password": "TestPass123!"
}

TEST_DRIVER = {
    "username": "testdriver",
    "password": "TestPass123!"
}

# Store tokens
tokens = {}


class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.customer_token = None
        self.driver_token = None
        
    def print_response(self, response, title="Response"):
        """Pretty print API response"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print(f"Response Data:")
            pprint(data)
        except:
            print(f"Response Text: {response.text[:500]}")
        print(f"{'='*60}\n")
        
    def test_user_registration(self):
        """Test user registration"""
        print("\n🔹 Testing User Registration...")
        
        customer_data = {
            "username": "newcustomer",
            "email": "customer@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
            "role": "CUSTOMER"
        }
        
        response = self.session.post(f"{API_BASE}/accounts/api/users/register/", json=customer_data)
        self.print_response(response, "User Registration")
        
    def test_login(self):
        """Test JWT authentication"""
        print("\n🔹 Testing Login (JWT Authentication)...")
        
        # Login as customer
        response = self.session.post(f"{API_BASE}/login/", json=TEST_CUSTOMER)
        self.print_response(response, "Customer Login")
        
        if response.status_code == 200:
            data = response.json()
            self.customer_token = data.get('access')
            tokens['customer'] = self.customer_token
            print(f"✅ Customer token obtained: {self.customer_token[:50]}...")
        
        # Login as driver
        response = self.session.post(f"{API_BASE}/login/", json=TEST_DRIVER)
        if response.status_code == 200:
            data = response.json()
            self.driver_token = data.get('access')
            tokens['driver'] = self.driver_token
            print(f"✅ Driver token obtained: {self.driver_token[:50]}...")
    
    def get_headers(self, token_type='customer'):
        """Get authorization headers"""
        token = tokens.get(token_type)
        if token:
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        return {'Content-Type': 'application/json'}
    
    def test_orders(self):
        """Test order endpoints"""
        print("\n🔹 Testing Order Endpoints...")
        
        headers = self.get_headers('customer')
        
        # Get all orders
        response = self.session.get(f"{API_BASE}/orders/api/orders/", headers=headers)
        self.print_response(response, "GET All Orders")
        
        # Get order statistics
        response = self.session.get(f"{API_BASE}/orders/api/orders/statistics/", headers=headers)
        self.print_response(response, "GET Order Statistics")
        
        # Create new order (you'll need valid customer and driver IDs)
        # new_order = {
        #     "customer": 1,
        #     "driver": 2,
        #     "status": "PENDING",
        #     "total_amount": "150.00"
        # }
        # response = self.session.post(f"{API_BASE}/orders/api/orders/", json=new_order, headers=headers)
        # self.print_response(response, "POST Create Order")
        
    def test_clothes(self):
        """Test cloth endpoints"""
        print("\n🔹 Testing Cloth Endpoints...")
        
        headers = self.get_headers('customer')
        
        # Get all clothes
        response = self.session.get(f"{API_BASE}/orders/api/clothes/", headers=headers)
        self.print_response(response, "GET All Clothes")
        
    def test_complaints(self):
        """Test complaint endpoints"""
        print("\n🔹 Testing Complaint Endpoints...")
        
        headers = self.get_headers('customer')
        
        # Get all complaints
        response = self.session.get(f"{API_BASE}/orders/api/complaints/complaints/", headers=headers)
        self.print_response(response, "GET All Complaints")
        
        # Get complaint statistics
        response = self.session.get(f"{API_BASE}/orders/api/complaints/complaints/statistics/", headers=headers)
        self.print_response(response, "GET Complaint Statistics")
        
    def test_notifications(self):
        """Test notification endpoints"""
        print("\n🔹 Testing Notification Endpoints...")
        
        headers = self.get_headers('customer')
        
        # Get all notifications
        response = self.session.get(f"{API_BASE}/notifications/api/notifications/", headers=headers)
        self.print_response(response, "GET All Notifications")
        
        # Get unread notifications
        response = self.session.get(f"{API_BASE}/notifications/api/notifications/?is_read=false", headers=headers)
        self.print_response(response, "GET Unread Notifications")
        
    def test_feedback(self):
        """Test feedback endpoints"""
        print("\n🔹 Testing Feedback Endpoints...")
        
        headers = self.get_headers('customer')
        
        # Get all feedbacks
        response = self.session.get(f"{API_BASE}/feedbacks/api/feedbacks/", headers=headers)
        self.print_response(response, "GET All Feedbacks")
        
    def test_ai_predictions(self):
        """Test AI prediction endpoints"""
        print("\n🔹 Testing AI Prediction Endpoints...")
        
        headers = self.get_headers('customer')
        
        # Get all AI predictions
        response = self.session.get(f"{API_BASE}/ai/api/ai-predictions/", headers=headers)
        self.print_response(response, "GET All AI Predictions")
        
    def test_chatbot(self):
        """Test chatbot endpoints"""
        print("\n🔹 Testing Chatbot Endpoints...")
        
        headers = self.get_headers('customer')
        
        # Get chatbot logs
        response = self.session.get(f"{API_BASE}/chatbot/api/chatbot-logs/", headers=headers)
        self.print_response(response, "GET Chatbot Logs")
        
    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*60)
        print("🚀 STARTING SMART LAUNDRY API TESTS")
        print("="*60)
        
        # self.test_user_registration()  # Uncomment to test registration
        self.test_login()
        
        if self.customer_token:
            self.test_orders()
            self.test_clothes()
            self.test_complaints()
            self.test_notifications()
            self.test_feedback()
            self.test_ai_predictions()
            self.test_chatbot()
        else:
            print("\n❌ Login failed. Please ensure test users exist.")
            print(f"Create users with credentials:")
            print(f"  Customer: {TEST_CUSTOMER}")
            print(f"  Driver: {TEST_DRIVER}")
        
        print("\n" + "="*60)
        print("✅ API TESTS COMPLETED")
        print("="*60)


def main():
    """Main test runner"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   Smart Laundry API Test Suite              ║
    ╚═══════════════════════════════════════════════╝
    
    Prerequisites:
    1. Django server must be running on http://127.0.0.1:8000
    2. Test users must exist (or uncomment registration test)
    
    Starting tests...
    """)
    
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
