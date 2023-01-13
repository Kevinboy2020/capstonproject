from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MenuItem, Cart, Order, OrderItem
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import MenuItemsSerializers, UserSerializers, CartSerializers, OrderSerializers, OrderItemsSerializers
from .permissions import IsManager
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage
from datetime import date
from rest_framework.throttling import UserRateThrottle
# Create your views here.


@api_view(['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def menu_items(request):
    category_name = request.query_params.get('category')
    to_price = request.query_params.get('to_price')
    search = request.query_params.get('search')
    ordering = request.query_params.get('ordering')
    per_page = request.query_params.get('perpage', default=3)
    page = request.query_params.get('page', default=1)
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        if category_name:
            items = items.filter(category__title=category_name)
            print(category_name)
            print(items)
        if to_price:
            items = items.filter(price__lte=to_price)
            print(items)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page=per_page)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []

        serialized_items = MenuItemsSerializers(items, many=True)
        return Response(serialized_items.data)
    elif request.method == 'POST':
        if not request.user.groups.filter(name='Manager').exists():
            print(request.user)
            return Response({'message': '403 - Unauthorized, Access Denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            serialized_item = MenuItemsSerializers(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'This end point doesn\'t suport PUT,PATCH and DELETE requests'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def single_menu_item(request, pk):
    menuitem = get_object_or_404(MenuItem, id=pk)
    if request.method == 'GET':
        serialized_item = MenuItemsSerializers(menuitem, many=False)
        return Response(serialized_item.data)
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        if not request.user.groups.filter(name='Manager').exists():
            print(request.user)
            return Response({'message': '403 - Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if request.method in ["PUT", "PATCH"]:
                try:
                    if request.data['title']:
                        menuitem.title = request.data['title']
                except:
                    pass
                try:
                    if request.data['price']:
                        menuitem.price = request.data['price']
                except:
                    pass
                try:
                    if request.data['category_id']:
                        menuitem.category = request.data['category_id']
                except:
                    pass
                try:
                    if request.data['featured']:
                        menuitem.featured = request.data['featured']
                except:
                    pass

                menuitem.save()
                serialized = MenuItemsSerializers(menuitem)
                return Response(serialized.data)
            if request.method == 'DELETE':
                menuitem.delete()
                return Response({"message": "Menu Item deleted"}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET', 'POST'])
@permission_classes([IsManager])
@throttle_classes([UserRateThrottle])
def allManagers(request):
    if request.method == "GET":
        group = User.objects.filter(groups__name="Manager").all()
        serialized = UserSerializers(group, many=True)
        return Response(serialized.data)
    if request.method == "POST":
        user = request.data["username"]
        user = get_object_or_404(User, username=user)
        manager = Group.objects.get(name="Manager")
        manager.user_set.add(user)
        return Response({"message": "User {} added to manager Group".format(user)}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsManager])
@throttle_classes([UserRateThrottle])
def delManager(request, pk):
    user = get_object_or_404(User, id=pk)
    manager = Group.objects.get(name="Manager")
    manager.user_set.remove(user)
    return Response({"message": "User {} removed from Manager group".format(user.username)}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsManager])
@throttle_classes([UserRateThrottle])
def allCrew(request):
    if request.method == "GET":
        group = User.objects.filter(groups__name="Delivery Crew").all()
        serialized = UserSerializers(group, many=True)
        return Response(serialized.data)
    if request.method == "POST":
        user = request.data["username"]
        user = get_object_or_404(User, username=user)
        crew = Group.objects.get(name="Delivery Crew")
        crew.user_set.add(user)
        return Response({"message": "User {} added to Delivery Crew".format(user)}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsManager])
@throttle_classes([UserRateThrottle])
def delCrew(request, pk):
    user = get_object_or_404(User, id=pk)
    crew = Group.objects.get(name="Delivery Crew")
    crew.user_set.remove(user)
    return Response({"message": "User {} removed from Delivery Crew".format(user.username)}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def currentCart(request):
    user = request.user
    if request.method == "GET":
        try:
            print(Cart.objects.get(user=request.user))
            cart = Cart.objects.get(user=user)
            print(cart)
            cart = CartSerializers(cart, many=False)
            return Response(cart.data)
        except:
            return Response([])

    if request.method == "POST":
        menuitem = request.data["menuitem"]
        menuitem = get_object_or_404(MenuItem, id=menuitem)
        if len(Cart.objects.filter(user=user)) == 0:
            cart = Cart.objects.create(user=request.user, menuitem_id=menuitem.id,
                                       unit_price=menuitem.price, price=menuitem.price, quantity=1)
            cart.save()
        else:
            cart = Cart.objects.get(user=user)
            cart.menuitem_id = menuitem.id
            cart.unit_price = menuitem.price
            cart.price = menuitem.price
            cart.save()
        cart = CartSerializers(cart)
        return Response(cart.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def allOrders(request):
    if request.method == 'GET':
        per_page = request.query_params.get('perpage', default=3)
        page = request.query_params.get('page', default=1)
        if request.user.groups.filter(name='Delivery Crew').exists():
            orders = Order.objects.filter(delivery_crew=request.user)
            orders = Paginator(orders, per_page=per_page)
            orders = orders.page(number=page)
            orders = OrderSerializers(orders, many=True)
            return Response({'headline': 'Orders assigned to you', 'orders': orders.data})
        if request.user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
            orders = Paginator(orders, per_page=per_page)
            orderitems = OrderItem.objects.all()
            orderitems = Paginator(orderitems, per_page=per_page)
        else:
            orders = Order.objects.filter(user=request.user)
            orders = Paginator(orders, per_page=per_page)
            orderitems = OrderItem.objects.filter(order=request.user)
            orderitems = Paginator(orderitems, per_page=per_page)
        orders = orders.page(number=page)
        orders = OrderSerializers(orders, many=True)

        orderitems = orderitems.page(number=page)
        orderitems = OrderItemsSerializers(orderitems, many=True)
        return Response({"orders": orders.data, "orderitems": orderitems.data})
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
        except:
            return Response({"Message": "No items in the cart"})
        print(cart)

        order = Order.objects.create(
            user=request.user, total=cart.price, date=date.today())
        order.save()
        orderitem = OrderItem.objects.create(
            order=request.user, menuitem_id=cart.menuitem_id, quantity=cart.quantity, price=cart.price, unit_price=cart.unit_price)
        orderitem.save()
        orderitem = OrderItemsSerializers(orderitem)
        cart.delete()
        return Response(orderitem.data)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def singleOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "GET":
        if order.user == request.user or request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery Crew').exists():
            index = Order.objects.all()
            index = list(index)
            index = index.index(order)
            orderItems = OrderItem.objects.all()[index]
            orderItems = OrderItemsSerializers(orderItems)
            order = OrderSerializers(order)
            return Response({"Order": order.data, "Order Items": orderItems.data})
        else:
            return Response({"Message": "Unauthorized"}, status.HTTP_403_FORBIDDEN)

    if request.method in ["PUT", "PATCH"]:
        try:
            deliveryCrew = request.data['delivery_crew_id']
        except:
            deliveryCrew = False
        if deliveryCrew:
            if User.objects.get(id=deliveryCrew).groups.filter(name="Delivery Crew").exists():
                order.delivery_crew_id = deliveryCrew
                order.save()
                return Response({"message": "Order Assigned to the delivery crew member {}".format(User.objects.get(id=deliveryCrew).username)}, status.HTTP_200_OK)
            else:
                return Response({"message": "You can only assign an order to a  delivery Crew member"}, status.HTTP_400_BAD_REQUEST)
        if order.delivery_crew or request.user.groups.filter(name='Delivery Crew').exists():
            try:
                OrderStatus = request.data["status"]
                order.status = OrderStatus
                order.save()
            except:
                return Response({"message": "You haven't provided the new status of order!"}, status.HTTP_200_OK)
            return Response({"message": "Order status Updated"}, status.HTTP_200_OK)
        else:
            return Response({"message": "Order is currently not assigned to a delivery crew member"}, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
            order.delete()
            return Response({"message": "Order Deleted successfully"}, status.HTTP_200_OK)
        else:
            return Response({"message": "Only manager can delete an Order"}, status.HTTP_403_FORBIDDEN)
