from django.shortcuts import render, redirect
from .models import PaymentOrder
import uuid

def start_payment(request):
    # Simulate creating a payment order (Mock/Test Mode)
    payment_order = PaymentOrder.objects.create(
        payment_address=str(uuid.uuid4()),  # Dummy address
        amount=10.00,
        currency='BTC',
        status='pending',
        qr_code='dummy_qr_code_url' # Dummy QR code
    )
    return redirect('payment_detail', pk=payment_order.pk)

def payment_detail(request, pk):
    payment_order = PaymentOrder.objects.get(pk=pk)
    context = {
        'payment_order': payment_order
    }
    return render(request, 'cryptopayments/payment_detail.html', context)