# categories/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('available-categories/', views.display_categories, name='available_categories'),
    # path('add-category/', views.add_category, name='add_category'),
    # path('update-category/<id>/', views.update_category, name='update_category'),
    # path('delete-category/<id>/', views.delete_category, name='delete_category'),
    path('menu/', views.menu_for_customers, name='customer_menu'),
    path('menu-item/', views.menu_view, name='menu_view'),



    
    
]