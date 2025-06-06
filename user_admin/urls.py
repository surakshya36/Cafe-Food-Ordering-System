from django.urls import path
from . import views
urlpatterns = [
    # path('available-menu-items/', views.available_items, name='available_items'),
    # path('add-menu-item/', views.add_item, name='add_item'),
    # path('view-menu-item/<id>/', views.view_item, name='view_item'),
    # path('update-menu-item/<item_id>/', views.update_item, name='update_item'),
    # path('delete-menu-item/<id>/', views.delete_item, name='delete_item'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('user-admin/admin-notifications/', views.get_admin_notifications, name='get_admin_notifications'),
    # path('user-admin/notifications/mark-read/', views.mark_admin_notifications_read, name='mark_admin_notifications_read'),

]
