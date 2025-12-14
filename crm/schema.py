import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order


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
    price = graphene.Float(required=True)   # accept raw number
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
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
        if input.phone and not re.match(r"^\+?\d[\d\-]+$", input.phone):
            errors.append("Invalid phone format")

        if errors:
            return CreateCustomer(customer=None, message="Failed to create customer", errors=errors)

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully", errors=[])


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created, errors = [], []
        with transaction.atomic():
            for cust in input:
                try:
                    if Customer.objects.filter(email=cust.email).exists():
                        raise ValidationError("Email already exists")
                    if cust.phone and not re.match(r"^\+?\d[\d\-]+$", cust.phone):
                        raise ValidationError("Invalid phone format")
                    new_customer = Customer(
                        name=cust.name,
                        email=cust.email,
                        phone=cust.phone
                    )
                    new_customer.save()
                    created.append(new_customer)
                except Exception as e:
                    errors.append(f"{cust.email}: {str(e)}")
        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        try:
            price = Decimal(str(input.price))  # convert raw float → Decimal
            if price <= 0:
                errors.append("Price must be positive")
            if input.stock is not None and input.stock < 0:
                errors.append("Stock cannot be negative")

            if errors:
                return CreateProduct(product=None, errors=errors)

            product = Product(
                name=input.name,
                price=price,
                stock=input.stock or 0
            )
            product.save()
            return CreateProduct(product=product, errors=[])
        except Exception as e:
            return CreateProduct(product=None, errors=[str(e)])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        errors = []
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return CreateOrder(order=None, errors=errors)

        products = Product.objects.filter(id__in=input.product_ids)
        if not products.exists():
            errors.append("Invalid product IDs")
            return CreateOrder(order=None, errors=errors)

        total = sum([Decimal(str(p.price)) for p in products])
        order = Order(customer=customer, total_amount=total)
        order.save()
        order.products.set(products)
        return CreateOrder(order=order, errors=[])
        

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
