#!/usr/bin/env python
"""
Sample Data Generator for Smart Laundry Backend
Run this script to populate the database with test data

Usage: python manage.py shell < create_sample_data.py
Or run: python manage.py runscript create_sample_data (if django-extensions is installed)
"""

import os
import django
import random
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile, DriverProfile
from orders.models import Order, Cloth
from complaints.models import Complaint, Feedback as ComplaintFeedback
from feedback.models import Feedback
from notifications.models import Notification
from ai_predictions.models import AIPrediction
from services.models import ChatbotLog

User = get_user_model()

def create_users():
    """Create sample users"""
    print("📝 Creating users...")
    
    # Create admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@smartlaundry.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            user_type='ADMIN'
        )
        print(f"✅ Created admin user: admin / admin123")
    
    # Create customers
    customers = []
    customer_data = [
        ('testcustomer', 'Test', 'Customer', 'customer@test.com', 'TestPass123!'),
        ('john_doe', 'John', 'Doe', 'john@example.com', 'TestPass123!'),
        ('jane_smith', 'Jane', 'Smith', 'jane@example.com', 'TestPass123!'),
        ('bob_wilson', 'Bob', 'Wilson', 'bob@example.com', 'TestPass123!'),
    ]
    
    for username, first, last, email, password in customer_data:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first,
                last_name=last,
                user_type='CUSTOMER'
            )
            # Create customer profile
            CustomerProfile.objects.create(
                user=user,
                house_no=str(random.randint(1, 999)),
                street_name="Main Street",
                area="Downtown",
                city="New Delhi",
                state="Delhi",
                pincode="110001"
            )
            customers.append(user)
            print(f"✅ Created customer: {username} / {password}")
    
    # Create drivers
    drivers = []
    driver_data = [
        ('testdriver', 'Test', 'Driver', 'driver@test.com', 'TestPass123!'),
        ('mike_driver', 'Mike', 'Johnson', 'mike@example.com', 'TestPass123!'),
        ('sarah_driver', 'Sarah', 'Williams', 'sarah@example.com', 'TestPass123!'),
    ]
    
    for username, first, last, email, password in driver_data:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first,
                last_name=last,
                user_type='DRIVER'
            )
            # Create driver profile
            DriverProfile.objects.create(
                user=user,
                vehicle_no=f"DL{random.randint(10, 99)}-{random.randint(1000, 9999)}",
                availability='AVAILABLE'
            )
            drivers.append(user)
            print(f"✅ Created driver: {username} / {password}")
    
    return customers if customers else list(User.objects.filter(user_type='CUSTOMER')), \
           drivers if drivers else list(User.objects.filter(user_type='DRIVER'))


def create_orders(customers, drivers):
    """Create sample orders"""
    print("\n📦 Creating orders...")
    
    statuses = ['PENDING', 'ASSIGNED', 'PICKED', 'IN_PROCESS', 'DELIVERED', 'CANCELLED']
    orders = []
    
    for i in range(20):
        customer = random.choice(customers)
        driver = random.choice(drivers) if random.random() > 0.3 else None
        status = random.choice(statuses)
        
        order = Order.objects.create(
            customer=customer,
            driver=driver,
            status=status,
            total_amount=round(random.uniform(100, 1000), 2),
            pickup_proof=f"pickup_proof_{i}.jpg" if status != 'PENDING' else None,
            delivery_proof=f"delivery_proof_{i}.jpg" if status == 'DELIVERED' else None
        )
        
        # Backdate some orders
        if random.random() > 0.5:
            days_ago = random.randint(1, 30)
            order.order_date = datetime.now() - timedelta(days=days_ago)
            order.save()
        
        orders.append(order)
        print(f"✅ Created order #{order.id} - Status: {status}")
    
    return orders


def create_clothes(orders):
    """Create sample clothes for orders"""
    print("\n👕 Creating clothes...")
    
    cloth_types = ['Shirt', 'Pants', 'Dress', 'Jacket', 'Sweater', 'Jeans', 'Skirt', 'Blouse']
    colors = ['White', 'Black', 'Blue', 'Red', 'Green', 'Yellow', 'Gray', 'Brown']
    statuses = ['RECEIVED', 'IN_WASH', 'IRONING', 'DELIVERED', 'MISSING']
    
    clothes_created = 0
    for order in orders:
        num_clothes = random.randint(2, 8)
        for i in range(num_clothes):
            cloth = Cloth.objects.create(
                order=order,
                cloth_type=random.choice(cloth_types),
                color=random.choice(colors),
                quantity=random.randint(1, 3),
                qr_code=f"QR{order.id}{i:03d}",
                status=random.choice(statuses),
                special_instruction="Handle with care" if random.random() > 0.7 else ""
            )
            clothes_created += 1
    
    print(f"✅ Created {clothes_created} cloth items")


def create_complaints(customers, orders):
    """Create sample complaints"""
    print("\n⚠️ Creating complaints...")
    
    issue_types = ['Damaged Item', 'Missing Item', 'Late Delivery', 'Poor Service', 'Incorrect Billing']
    
    for i in range(10):
        customer = random.choice(customers)
        order = random.choice(orders)
        
        Complaint.objects.create(
            order=order,
            customer=customer,
            issue_type=random.choice(issue_types),
            description=f"Sample complaint description for issue {i+1}",
            status=random.choice(['OPEN', 'RESOLVED'])
        )
    
    print(f"✅ Created 10 complaints")


def create_feedbacks(customers, orders, drivers):
    """Create sample feedbacks"""
    print("\n⭐ Creating feedbacks...")
    
    # Create complaint feedbacks
    for i in range(15):
        customer = random.choice(customers)
        order = random.choice(orders)
        
        ComplaintFeedback.objects.create(
            customer=customer,
            order=order,
            rating=random.randint(1, 5),
            comments=f"Sample feedback comment {i+1}"
        )
    
    # Create regular feedbacks
    feedback_types = ['SERVICE', 'DRIVER', 'APP']
    for i in range(15):
        customer = random.choice(customers)
        order = random.choice(orders)
        driver = random.choice(drivers)
        
        Feedback.objects.create(
            customer=customer,
            order=order,
            driver=driver,
            rating=random.randint(1, 5),
            comments=f"Sample regular feedback {i+1}",
            feedback_type=random.choice(feedback_types)
        )
    
    print(f"✅ Created 30 feedbacks")


def create_notifications(customers, drivers):
    """Create sample notifications"""
    print("\n🔔 Creating notifications...")
    
    messages = [
        "Your order has been placed successfully",
        "Driver is on the way to pick up your order",
        "Your order has been picked up",
        "Your clothes are being washed",
        "Your order is ready for delivery",
        "Your order has been delivered",
        "New order assigned to you",
        "Payment received successfully"
    ]
    
    all_users = customers + drivers
    for i in range(30):
        user = random.choice(all_users)
        
        Notification.objects.create(
            user=user,
            message=random.choice(messages),
            is_read=random.choice([True, False])
        )
    
    print(f"✅ Created 30 notifications")


def create_ai_predictions(orders):
    """Create sample AI predictions"""
    print("\n🤖 Creating AI predictions...")
    
    prediction_types = ['Delivery Time', 'Load Optimization', 'Pricing Suggestion', 'Demand Forecast']
    
    for i in range(15):
        order = random.choice(orders)
        
        AIPrediction.objects.create(
            order=order,
            prediction_type=random.choice(prediction_types),
            predicted_value=f"{random.randint(20, 120)} minutes" if 'Time' in random.choice(prediction_types) else f"${random.randint(50, 200)}"
        )
    
    print(f"✅ Created 15 AI predictions")


def create_chatbot_logs(customers):
    """Create sample chatbot logs"""
    print("\n💬 Creating chatbot logs...")
    
    queries = [
        "What is the status of my order?",
        "How much does dry cleaning cost?",
        "When will my order be delivered?",
        "Can I track my driver?",
        "Do you offer same-day service?"
    ]
    
    responses = [
        "Your order is currently being processed.",
        "Dry cleaning starts at $15 per item.",
        "Your order will be delivered within 24 hours.",
        "Yes, you can track your driver in real-time through our app.",
        "Yes, we offer same-day service for orders placed before 10 AM."
    ]
    
    for i in range(25):
        customer = random.choice(customers)
        
        ChatbotLog.objects.create(
            customer=customer,
            query=random.choice(queries),
            response=random.choice(responses)
        )
    
    print(f"✅ Created 25 chatbot logs")


def main():
    """Main function to create all sample data"""
    print("\n" + "="*60)
    print("🚀 SMART LAUNDRY - SAMPLE DATA GENERATOR")
    print("="*60 + "\n")
    
    try:
        customers, drivers = create_users()
        orders = create_orders(customers, drivers)
        create_clothes(orders)
        create_complaints(customers, orders)
        create_feedbacks(customers, orders, drivers)
        create_notifications(customers, drivers)
        create_ai_predictions(orders)
        create_chatbot_logs(customers)
        
        print("\n" + "="*60)
        print("✅ SAMPLE DATA GENERATION COMPLETED!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   Users: {User.objects.count()}")
        print(f"   Orders: {Order.objects.count()}")
        print(f"   Clothes: {Cloth.objects.count()}")
        print(f"   Complaints: {Complaint.objects.count()}")
        print(f"   Feedbacks: {ComplaintFeedback.objects.count() + Feedback.objects.count()}")
        print(f"   Notifications: {Notification.objects.count()}")
        print(f"   AI Predictions: {AIPrediction.objects.count()}")
        print(f"   Chatbot Logs: {ChatbotLog.objects.count()}")
        print("\n🔑 Test Login Credentials:")
        print("   Admin: admin / admin123")
        print("   Customer: testcustomer / TestPass123!")
        print("   Driver: testdriver / TestPass123!")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
