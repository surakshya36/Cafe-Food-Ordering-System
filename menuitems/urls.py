from django.urls import path
from . import views

app_name = 'menuitem'

urlpatterns = [
    path('staff/available_items/', views.available_items, name='staff_available_items'),
    path('admin/available_items/', views.available_items, name='admin_available_items'),
    path('admin/delete-all-items/', views.clear_all_items, name='clear_all_items'),
    path('staff/view-menu-item/<id>/', views.view_item, name='staff_view_item'),
    path('admin/view-menu-item/<id>/', views.view_item, name='admin_view_item'),
    path('staff/update-menu-item/<item_id>/', views.update_item, name='staff_update_item'),
    path('admin/update-menu-item/<item_id>/', views.update_item, name='admin_update_item'),


    # path('available-menu-items/', views.available_items, name='available_items'),
    path('staff/add-menu-item/', views.add_item, name='staff_add_item'),
    path('admin/add-menu-item/', views.add_item, name='admin_add_item'),

    path('staff/delete-menu-item/<id>/', views.delete_item, name='staff_delete_item'),
    path('admin/delete-menu-item/<id>/', views.delete_item, name='admin_delete_item'),

]
