#!/usr/bin/env python
"""
Test script to demonstrate the Observer Pattern implementation in the e-commerce backend.

OBSERVER PATTERN DEMONSTRATION:
This script shows how the observer pattern works in the system:
- Order status changes trigger notifications to multiple observers
- Product stock changes trigger notifications to stock observers
- Each observer performs its specific responsibility independently

Usage: python test_observer_pattern.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/ecomprj')
django.setup()

from core.models import Order, Product
from core.patterns import ObserverRegistry, EmailNotificationObserver, InventoryObserver, AnalyticsObserver, ProductStockObserver

def test_order_status_observer():
    """Test order status changes and observer notifications"""
    print("\n=== TESTING ORDER STATUS OBSERVER PATTERN ===")

    # Get or create a test order
    try:
        order = Order.objects.filter(user__username='testvendor').first()
        if not order:
            print("No test order found. Please run create_test_data first.")
            return
    except Exception as e:
        print(f"Error getting test order: {e}")
        return

    print(f"Testing with order: {order.oid} (current status: {order.order_status})")

    # Manually register observers for this test (normally done in apps.py)
    registry = ObserverRegistry()
    registry.register_observer('order_status_changed', EmailNotificationObserver())
    registry.register_observer('order_status_changed', InventoryObserver())
    registry.register_observer('order_status_changed', AnalyticsObserver())

    # Change order status - this will trigger the observer pattern
    print(f"\nChanging order status from '{order.order_status}' to 'processing'...")
    order.order_status = 'processing'
    order.save()  # This triggers the observer notifications

    print(f"\nChanging order status from 'processing' to 'shipped'...")
    order.order_status = 'shipped'
    order.save()  # This triggers the observer notifications

    print(f"\nChanging order status from 'shipped' to 'delivered'...")
    order.order_status = 'delivered'
    order.save()  # This triggers the observer notifications

    print("\n[OK] Order status observer pattern test completed!")


def test_product_stock_observer():
    """Test product stock changes and observer notifications"""
    print("\n=== TESTING PRODUCT STOCK OBSERVER PATTERN ===")

    # Get a test product
    try:
        product = Product.objects.filter(title__icontains='test').first()
        if not product:
            print("No test product found. Please run create_test_data first.")
            return
    except Exception as e:
        print(f"Error getting test product: {e}")
        return

    print(f"Testing with product: {product.title} (current stock: {product.stock_count})")

    # Manually register observers for this test
    registry = ObserverRegistry()
    registry.register_observer('stock_changed', ProductStockObserver())

    # Change product stock - this will trigger the observer pattern
    original_stock = product.stock_count

    print(f"\nReducing stock from {original_stock} to {max(0, original_stock - 5)}...")
    product.stock_count = max(0, original_stock - 5)
    product.save()  # This triggers the observer notifications

    print(f"\nSetting stock to low level (3)...")
    product.stock_count = 3
    product.save()  # This should trigger low stock alert

    print(f"\nSetting stock to zero (out of stock)...")
    product.stock_count = 0
    product.save()  # This should trigger out of stock alert

    print(f"\nRestocking to 10 units...")
    product.stock_count = 10
    product.save()  # This should trigger restock alert

    # Reset stock to original value
    product.stock_count = original_stock
    product.save()

    print("\n[OK] Product stock observer pattern test completed!")


def demonstrate_observer_pattern():
    """Demonstrate the observer pattern concepts"""
    print("=== OBSERVER PATTERN DEMONSTRATION ===")
    print("""
The Observer Pattern allows objects to be notified automatically when another object's state changes.

In this e-commerce system:

1. SUBJECTS (Observable objects):
   - Order model: Notifies when order_status changes
   - Product model: Notifies when stock_count changes

2. OBSERVERS (Objects that react to changes):
   - EmailNotificationObserver: Sends emails when order status changes
   - InventoryObserver: Manages inventory when orders are cancelled/delivered
   - AnalyticsObserver: Tracks metrics when order status changes
   - ProductStockObserver: Monitors stock levels and sends alerts

3. BENEFITS:
   - Loose coupling: Order model doesn't need to know about emails/inventory/analytics
   - Single responsibility: Each observer handles one concern
   - Extensibility: New observers can be added without modifying existing code
   - Testability: Each observer can be tested independently

4. HOW IT WORKS:
   - When order.save() is called and status changed: observers are notified
   - When product.save() is called and stock changed: observers are notified
   - Each observer receives event data and performs its specific action
   - All happens automatically without the calling code needing to know about it
    """)


if __name__ == '__main__':
    print("E-COMMERCE OBSERVER PATTERN TEST")
    print("=" * 50)

    demonstrate_observer_pattern()
    test_order_status_observer()
    test_product_stock_observer()

    print("\n" + "=" * 50)
    print("OBSERVER PATTERN IMPLEMENTATION COMPLETE!")
    print("The observer pattern is now active in your e-commerce system.")