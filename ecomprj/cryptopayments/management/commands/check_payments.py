from django.core.management.base import BaseCommand
from cryptopayments.models import PaymentOrder
import random

class Command(BaseCommand):
    help = 'Checks for pending cryptocurrency payments and updates their status.'

    def handle(self, *args, **options):
        pending_orders = PaymentOrder.objects.filter(status__in=['pending', 'partially_paid'])
        self.stdout.write(f'Found {pending_orders.count()} pending orders.')

        for order in pending_orders:
            # Simulate checking a blockchain data source
            # In a real scenario, this would involve API calls to a blockchain explorer
            # or a payment gateway.
            is_paid = random.choice([True, False]) # 50% chance of being paid

            if is_paid:
                order.status = 'paid'
                order.save()
                self.stdout.write(self.style.SUCCESS(f'Payment Order {order.id} for {order.amount} {order.currency} received and marked as paid.'))
            else:
                self.stdout.write(f'Payment Order {order.id} for {order.amount} {order.currency} still pending.')

        self.stdout.write(self.style.SUCCESS('Payment status check complete.'))