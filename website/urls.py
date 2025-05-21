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


    
    
]