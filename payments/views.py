from .decorators import admin_required, staff_required,login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment
from django.contrib import messages


# Create your views here.
def admin_all_payments(request):
    payments = Payment.objects.select_related('order', 'order__table').order_by('-created_at')

    payment_data = [
        {
            'payment_id': payment.id,
            'transaction_id': payment.transaction_id,
            'status': payment.get_status_display(),
            'method': payment.get_method_display(),
            'amount': payment.amount,
            'order_id': payment.order.id,
            'customer_name': payment.order.customer_name,
            'order_type': payment.order.get_order_type_display(),
            'table_number': payment.order.table.table_number if payment.order.table else 'N/A',
            'created_at': payment.created_at,
        }
        for payment in payments
    ]

    return render(request, 'payments/admin/all_payments.html', {'payments': payment_data, 'page': 'All Payments'})


from django.shortcuts import render, get_object_or_404
from .models import Payment

@admin_required
def admin_view_payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payments/admin/view_payment_detail.html', {'payment': payment, 'page':'Payment Details'})
def admin_delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, "Payment record deleted successfully.")
        return redirect('admin_all_payments')

    return render(request, 'payments/admin/confirm_delete.html', {'payment': payment, 'page':'Delete Payment Record'})

@admin_required
def clear_all_payments(request):
    if request.method == "POST":
        Payment.objects.all().delete()
        messages.success(request, "All payments have been successfully cleared.")
        return redirect('admin_all_payments')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('admin_all_payments')