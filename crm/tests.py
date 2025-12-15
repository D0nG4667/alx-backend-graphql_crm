from django.test import TestCase
from graphene.test import Client
from alx_backend_graphql.schema import schema
from crm.models import Customer, Product, Order
from decimal import Decimal
from django.utils import timezone


class FilterTests(TestCase):
    def setUp(self):
        # Seed test data
        print("Setting up test data...")
        self.customer1 = Customer.objects.create(
            name="Alice", email="alice@example.com", phone="+1234567890"
        )
        self.customer2 = Customer.objects.create(
            name="Bob", email="bob@example.com", phone="123-456-7890"
        )

        self.product1 = Product.objects.create(
            name="Laptop", price=Decimal("999.99"), stock=10
        )
        self.product2 = Product.objects.create(
            name="Phone", price=Decimal("499.99"), stock=5
        )

        # Use timezone-aware datetime for order_date
        self.order1 = Order.objects.create(
            customer=self.customer1,
            total_amount=Decimal("1499.98"),
            order_date=timezone.now(),
        )
        self.order1.products.set([self.product1, self.product2])

        self.client = Client(schema)

    def test_filter_customers_by_name_and_date(self):
        print("Testing customer filtering...")
        query = """
        query {
          allCustomers(filter: { nameIcontains: "Ali", createdAtGte: "2025-01-01" }) {
            edges {
              node {
                id
                name
                email
              }
            }
          }
        }
        """
        executed = self.client.execute(query)
        self.assertNotIn("errors", executed)
        nodes = executed["data"]["allCustomers"]["edges"]
        self.assertTrue(any(node["node"]["name"] == "Alice" for node in nodes))

    def test_filter_products_by_price_and_sort_stock(self):
        print("Testing product filtering...")
        query = """
        query {
          allProducts(filter: { priceGte: 100, priceLte: 1000 }, orderBy: ["-stock"]) {
            edges {
              node {
                name
                price
                stock
              }
            }
          }
        }
        """
        executed = self.client.execute(query)
        self.assertNotIn("errors", executed)
        nodes = executed["data"]["allProducts"]["edges"]
        # Ensure Laptop (stock 10) comes before Phone (stock 5)
        self.assertEqual(nodes[0]["node"]["name"], "Laptop")

    def test_filter_orders_by_customer_and_product(self):
        query = """
        query {
          allOrders(filter: { customerName: "Alice", productName: "Laptop", totalAmountGte: 500 }) {
            edges {
              node {
                id
                customer { name }
                products { name }
                totalAmount
              }
            }
          }
        }
        """
        executed = self.client.execute(query)
        self.assertNotIn("errors", executed)
        nodes = executed["data"]["allOrders"]["edges"]
        self.assertTrue(
            any(node["node"]["customer"]["name"] == "Alice" for node in nodes)
        )
        self.assertTrue(
            any(
                "Laptop" in [p["name"] for p in node["node"]["products"]]
                for node in nodes
            )
        )
