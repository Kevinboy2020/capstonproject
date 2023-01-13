from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.single_menu_item),
    path('groups/manager/users/<int:pk>', views.delManager),
    path('groups/manager/users', views.allManagers),
    path('groups/delivery-crew/users/<int:pk>', views.delCrew),
    path('groups/delivery-crew/users', views.allCrew),
    path('cart/menu-items', views.currentCart),
    path('orders', views.allOrders),
    path('orders/<int:pk>', views.singleOrder)
]
