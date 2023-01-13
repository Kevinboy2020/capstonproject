from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemsSerializers(serializers.ModelSerializer):
    category = CategorySerializers(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", 'title', 'price',
                  'featured', 'category', 'category_id']


class UserSerializers(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField(method_name="group_name")

    class Meta:
        model = User
        fields = ["id", 'username', 'email', 'groups']

    def group_name(self, person: User):
        return [x.name for x in person.groups.all()]


class CartSerializers(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name="totalprice")
    menuitem = MenuItemsSerializers(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "menuitem", "menuitem_id",
                  "quantity", "unit_price", "price"]

    def totalprice(self, model: Cart):
        return model.price * model.quantity


class OrderSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name="username")
    delivery_crew = UserSerializers(read_only=True)
    delivery_crew_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew',
                  'status', 'total', 'date', 'delivery_crew_id']

    def username(self, model: User):
        return model.user.username


class OrderItemsSerializers(serializers.ModelSerializer):
    order = serializers.SerializerMethodField(method_name="username")
    menuitem = MenuItemsSerializers(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity',
                  'unit_price', 'price', 'menuitem_id']

    def username(self, model: User):
        return model.order.username
