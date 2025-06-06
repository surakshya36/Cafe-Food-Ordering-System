# categories/urls.py
from django.urls import path
from . import views

app_name = 'category'

urlpatterns = [
    path('admin/available-categories/', views.display_categories, name='available_categories'),
    path('admin/delete-all-categories/', views.clear_all_categories, name='clear_all_categories'),
    path('admin/add-category/', views.add_category, name='add_category'),
    path('admin/update-category/<id>/', views.update_category, name='update_category'),
    path('admin/delete-category/<id>/', views.delete_category, name='delete_category'),


    
    
]