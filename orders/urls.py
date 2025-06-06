from django.urls import path
from . import views


urlpatterns = [
    path('admin/orders/<int:order_id>/view-order-detail', views.adnin_order_detail_view, name='admin_order_detail_view'),
    path('admin/orders/<int:order_id>/edit-order-status', views.adnin_edit_order_status, name='admin_edit_order_status'),
    path('admin/orders/', views.admin_all_orders_view, name='admin_all_orders_view'),
    path('admin/orders/ajax/all/', views.admin_all_orders_ajax, name='admin_all_orders_ajax'),
    path('admin/orders/vip/', views.adnin_vip_orders_view, name='admin_vip_orders_view'),
    path('admin/orders/rush/', views.adnin_rush_orders_view, name='admin_rush_orders_view'),
    path('admin/orders/normal/', views.adnin_normal_orders_view, name='admin_normal_orders_view'),
    path('admin/orders/<int:order_id>/delete/', views.admin_order_delete, name='admin_order_delete'),
    path('admin/orders/clear_all/', views.clear_all_orders, name='clear_all_orders'),

  
    path('staff/orders/<int:order_id>/view-order-detail', views.staff_order_detail_view, name='staff_order_detail_view'),
    path('staff/orders/<int:order_id>/edit-order-status', views.staff_edit_order_status, name='staff_edit_order_status'),
    path('staff/orders/', views.staff_all_orders_view, name='staff_all_orders_view'),
    path('staff/orders/ajax/all/', views.staff_all_orders_ajax, name='staff_all_orders_ajax'),
    path('staff/orders/vip/', views.staff_vip_orders_view, name='staff_vip_orders_view'),
    path('staff/orders/rush/', views.staff_rush_orders_view, name='staff_rush_orders_view'),
    path('staff/orders/normal/', views.staff_normal_orders_view, name='staff_normal_orders_view'),


]
