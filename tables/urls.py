# categories/urls.py
from django.urls import path
from . import views

app_name = 'table'

urlpatterns = [
    path('admin/available-tables/', views.available_tables, name='available_tables'),
    path('admin/add-table/', views.add_table, name='add_table'),
    path('admin/edit-table/<table_id>/', views.edit_table, name='edit_table'),
    path('admin/delete-table/<table_id>/', views.delete_table, name='delete_table'),

    path('admin/available-rooms', views.available_rooms, name='available_rooms'),
    path('admin/add-room/', views.add_room, name='add_room'),
    path('admin/edit-room/<room_id>/', views.edit_room, name='edit_room'),
    path('admin/delete-room/<room_id>/', views.delete_room, name='delete_room'),  

     path('staff/available-rooms', views.staff_available_rooms, name='staff_available_rooms'),
     path('staff/room/<int:room_id>/tables/', views.tables_by_room, name='tables_by_room'),
     path('staff/table/<int:table_id>/detail/', views.table_detail, name='table_detail'),
     
]

