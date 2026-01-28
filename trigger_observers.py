#!/usr/bin/env python
"""
Script to manually trigger observer pattern notifications to show where they appear.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/ecomprj')
django.setup()

from core.models import Order, Product
from django.contrib.auth import get_user_model

User = get_user_model()

def trigger_order_notifications():
    """Trigger order status change notifications"""
    print("=== TRIGGERING ORDER STATUS CHANGE NOTIFICATIONS ===")

    # Get the first order
    try:
        order = Order.objects.first()
        if not order:
            print("No orders found. Run the API tests first to create an order.")
            return

        print(f"Found order: {order.oid} (current status: {order.order_status})")

        # Change status to trigger observers
        print(f"\nChanging order status to 'processing'...")
        order.order_status = 'processing'
        order.save()

        print(f"\nChanging order status to 'shipped'...")
        order.order_status = 'shipped'
        order.save()

        print(f"\nChanging order status to 'delivered'...")
        order.order_status = 'delivered'
        order.save()

    except Exception as e:
        print(f"Error: {e}")


def trigger_product_notifications():
    """Trigger product stock change notifications"""
    print("\n=== TRIGGERING PRODUCT STOCK CHANGE NOTIFICATIONS ===")

    try:
        product = Product.objects.filter(title__icontains='test').first()
        if not product:
            print("No test products found.")
            return

        print(f"Found product: {product.title} (current stock: {product.stock_count})")

        # Change stock to trigger observers
        original_stock = product.stock_count

        print(f"\nSetting stock to low level (2)...")
        product.stock_count = 2
        product.save()

        print(f"\nSetting stock to zero (out of stock)...")
        product.stock_count = 0
        product.save()

        print(f"\nRestocking to 15 units...")
        product.stock_count = 15
        product.save()

        # Reset stock
        product.stock_count = original_stock
        product.save()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    print("OBSERVER PATTERN NOTIFICATION DEMO")
    print("=" * 50)
    print("Watch the terminal output below for observer notifications:")
    print("=" * 50)

    trigger_order_notifications()
    trigger_product_notifications()

    print("\n" + "=" * 50)
    print("Check the terminal output above for observer notifications!")
    print("Notifications appear as log messages in the console.")