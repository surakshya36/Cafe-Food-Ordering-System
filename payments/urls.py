from django.urls import path
from . import views

urlpatterns = [
    path('all-payments/', views.admin_all_payments, name='admin_all_payments'),
    path('view/<int:payment_id>/', views.admin_view_payment_detail, name='admin_view_payment_detail'),
    path('delete/<int:payment_id>/', views.admin_delete_payment, name='admin_delete_payment'),
    path('clear-all-payments/', views.clear_all_payments, name='clear_all_payments'),
]