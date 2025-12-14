import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from decimal import Decimal

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        
        
# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    
# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        name = input.name
        email = input.email
        phone = input.phone
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        if phone and not re.match(r"^\+?\d[\d\-]+$", phone):
            raise ValidationError("Invalid phone format")
        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for cust_input in input:
                try:
                    if Customer.objects.filter(email=cust_input.email).exists():
                        raise ValidationError("Email already exists")
                    cust = Customer.objects.create(
                        name=cust_input.name,
                        email=cust_input.email,
                        phone=cust_input.phone
                    )
                    created.append(cust)
                except Exception as e:
                    errors.append(str(e))
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        price = Decimal(str(input.price))  # convert float → Decimal safely
        if price <= 0:
            raise ValidationError("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name,
            price=price,
            stock=input.stock or 0
        )
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        products = Product.objects.filter(id__in=input.product_ids)
        if not products.exists():
            raise ValidationError("Invalid product IDs")

        total = sum([p.price for p in products])
        order = Order.objects.create(customer=customer, total_amount=total)
        order.products.set(products)
        return CreateOrder(order=order)

# Root Mutation
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Root Query
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()
