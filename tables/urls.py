# categories/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('available-tables/', views.available_tables, name='available_tables'),
    path('add-table/', views.add_table, name='add_table'),
    path('edit-table/<table_id>/', views.edit_table, name='edit_table'),
    path('delete-table/<table_id>/', views.delete_table, name='delete_table'),

    path('available-rooms', views.available_rooms, name='available_rooms'),
    path('add-room/', views.add_room, name='add_room'),
    path('edit-room/<room_id>/', views.edit_room, name='edit_room'),
    path('delete-room/<room_id>/', views.delete_room, name='delete_room'),

    
    
]