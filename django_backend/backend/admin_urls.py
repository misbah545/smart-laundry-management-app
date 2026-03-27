"""
Admin Panel URL Configuration
"""
from django.urls import path
from .admin_views import (
    admin_dashboard_overview,
    admin_orders_list,
    verify_order_qr,
    update_order_status,
    inventory_management,
    restock_inventory,
    complaints_management,
    resolve_complaint,
    analytics_reports,
    customer_loyalty_tracking,
    assign_driver_to_order,
    workload_prediction,
    apply_discount_or_refund,
    all_customers_list,
    all_drivers_list
)

urlpatterns = [
    # Dashboard
    path('dashboard/', admin_dashboard_overview, name='admin_dashboard'),
    path('orders/', admin_orders_list, name='admin_orders_list'),
    
    # QR Code Operations
    path('verify-qr/', verify_order_qr, name='verify_qr'),
    
    # Order Management
    path('orders/<int:order_id>/status/', update_order_status, name='update_order_status'),
    path('orders/assign-driver/', assign_driver_to_order, name='assign_driver'),
    
    # Inventory Management
    path('inventory/', inventory_management, name='inventory_management'),
    path('inventory/restock/', restock_inventory, name='restock_inventory'),
    
    # Complaints Management
    path('complaints/', complaints_management, name='complaints_management'),
    path('complaints/<int:complaint_id>/resolve/', resolve_complaint, name='resolve_complaint'),
    
    # Analytics & Reports
    path('analytics/', analytics_reports, name='analytics_reports'),
    path('workload-prediction/', workload_prediction, name='workload_prediction'),
    
    # Customer & Loyalty
    path('customers/', all_customers_list, name='all_customers'),
    path('loyalty-tracking/', customer_loyalty_tracking, name='loyalty_tracking'),
    
    # Drivers
    path('drivers/', all_drivers_list, name='all_drivers'),
    
    # Discount & Refund
    path('apply-discount-refund/', apply_discount_or_refund, name='apply_discount_refund'),
]
