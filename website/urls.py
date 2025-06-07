# categories/urls.py
from django.urls import path
from . import views
from .views import (
    menu_for_customers, 
    item_detail, 
    handle_search,
    cart,
    add_to_cart,
    increase_quantity,
    decrease_quantity,
    remove_item)

urlpatterns = [
    # path('available-categories/', views.display_categories, name='available_categories'),
    # path('add-category/', views.add_category, name='add_category'),
    # path('update-category/<id>/', views.update_category, name='update_category'),
    # path('delete-category/<id>/', views.delete_category, name='delete_category'),
    path('menu/', views.menu_for_customers, name='customer_menu'),
    path('', views.menu_for_customers, name='home'),
    path('item_detail/<int:item_id>', views.item_detail, name='item_detail'),
    path('search/', views.handle_search, name='handle_search'),
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    # These are the critical URLs for cart operations
    path('cart/items/increase_quantity/<int:item_id>/', increase_quantity, name='increase_quantity'),
    path('cart/items/decrease_quantity/<int:item_id>/', decrease_quantity, name='decrease_quantity'),
    path('cart/items/remove_item/<int:item_id>/', remove_item, name='remove_item'),
    path('empty/', views.empty_cart, name='empty_cart'),
    path('confirm-order/', views.show_confirm_order, name='show_confirm_order'),
    path('process-order/', views.process_order, name='process_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('my-order/', views.view_my_order, name='view_my_order'),
    path('order-status/<int:order_id>/', views.get_order_status, name='order_status'),
    path('my-orders/', views.my_orders, name='my_orders'),
   path('order-notifications/', views.order_status_notifications_view, name='order_status_notifications_view'),
    path('api/notifications/unread/', views.fetch_unread_notifications, name='fetch_unread_notifications'),



    path('vip-menu/', views.menu_for_vipcustomers, name='menu_for_vipcustomers'),
    path('vip-search/', views.vip_handle_search, name='vip_handle_search'),
    path('vip-item_detail/<int:item_id>', views.vip_item_detail, name='vip_item_detail'),
    path("vip-cart/", views.vip_cart, name="vip_cart"),
    path('vip-add-to-cart/', views.vip_add_to_cart, name='vip_add_to_cart'),
    path('vip-cart/items/vip_increase_quantity/<int:item_id>/', views.vip_increase_quantity, name='vip_increase_quantity'),
    path('vip-cart/items/vip_decrease_quantity/<int:item_id>/', views.vip_decrease_quantity, name='vip_decrease_quantity'),
    path('vip-cart/items/vip_remove_item/<int:item_id>/', views.vip_remove_item, name='vip_remove_item'),
    path('vip-empty-cart/', views.vip_empty_cart, name='vip_empty_cart'),
    path('vip-confirm-order/', views.vip_show_confirm_order, name='vip_show_confirm_order'),
    path('vip-process-order/', views.vip_process_order, name='vip_process_order'),
    path('vip-order/<int:order_id>/', views.vip_order_detail, name='vip_order_detail'),
    path('vip-my-order/', views.view_my_order, name='vip_view_my_order'),
    path('vip-order-status/<int:order_id>/', views.vip_get_order_status, name='vip_order_status'),
     path('vip-my-orders/', views.vip_my_orders, name='vip_my_orders'),
   path('vip-order-notifications/', views.vip_order_status_notifications_view, name='vip_order_status_notifications_view'),
    path('vip-api/notifications/unread/', views.vip_fetch_unread_notifications, name='vip_fetch_unread_notifications'),


    # path('khalti-request/<int:order_id>/', views.khalti_payment_request, name='khalti_payment_request'),
    # path('payment/khalti/verify/', views.khalti_payment_verify, name='khalti_payment_verify'),
    # path('payment/vip/khalti/verify/', views.khalti_payment_verify_vip, name='khalti_payment_verify_vip'),

    path('payment/esewa/success/normal/', views.esewa_normal_payment_success, name='esewa_normal_payment_success'),
    path('payment/esewa/failure/normal/', views.esewa_normal_payment_failure, name='esewa_normal_payment_failure'),
    path('payment/esewa/request/normal/<int:order_id>/', views.esewa_payment_request_normal, name='esewa_payment_request_normal'),






 
]