from django.urls import path
from . import views

urlpatterns = [
    # path('available-menu-items/', views.available_items, name='available_items'),
    # path('add-menu-item/', views.add_item, name='add_item'),
    # path('view-menu-item/<id>/', views.view_item, name='view_item'),
    # path('update-menu-item/<item_id>/', views.update_item, name='update_item'),
    # path('delete-menu-item/<id>/', views.delete_item, name='delete_item'),

    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/notifications/', views.get_staff_notifications, name='get_staff_notifications'),   
    path('staff/notifications/mark-read/', views.mark_staff_notifications_read, name='mark_staff_notifications_read'),
    path('staff/notifications/clear-all/', views.soft_clear_all_staff_notifications, name='clear_all_notifications'),



]
