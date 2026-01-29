from django.core.management.base import BaseCommand
from cryptopayments.models import PaymentOrder

class Command(BaseCommand):
    help = 'Simulates a successful payment for a given PaymentOrder ID.'

    def add_arguments(self, parser):
        parser.add_argument('order_id', type=int, help='The ID of the PaymentOrder to mark as paid.')

    def handle(self, *args, **options):
        order_id = options['order_id']
        try:
            payment_order = PaymentOrder.objects.get(pk=order_id)
            payment_order.status = 'paid'
            payment_order.save()
            self.stdout.write(self.style.SUCCESS(f'Payment Order {order_id} marked as paid.'))
        except PaymentOrder.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Payment Order with ID {order_id} does not exist.'))