import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    # Case-insensitive partial matches
    nameIcontains = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )
    emailIcontains = django_filters.CharFilter(
        field_name="email", lookup_expr="icontains"
    )

    # Date range filters
    createdAtGte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    createdAtLte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    # Custom phone pattern filter
    phonePattern = django_filters.CharFilter(method="filter_phone_pattern")

    class Meta:
        model = Customer
        fields = ["name", "email", "created_at", "phone"]

    def filter_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):
    # Case-insensitive partial match
    nameIcontains = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )

    # Price range filters
    priceGte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    priceLte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Stock filters
    stockGte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stockLte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")

    # Ordering support
    orderBy = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("price", "price"),
            ("stock", "stock"),
        )
    )

    class Meta:
        model = Product
        fields = ["name", "price", "stock"]


class OrderFilter(django_filters.FilterSet):
    # Total amount range
    totalAmountGte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    totalAmountLte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte"
    )

    # Order date range
    orderDateGte = django_filters.DateTimeFilter(field_name="order_date", lookup_expr="gte")
    orderDateLte = django_filters.DateTimeFilter(field_name="order_date", lookup_expr="lte")

    # Related field lookups
    customerName = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    productName = django_filters.CharFilter(
        field_name="products__name", lookup_expr="icontains"
    )

    # Filter orders by product ID
    productId = django_filters.NumberFilter(field_name="products__id")

    class Meta:
        model = Order
        fields = ["total_amount", "order_date", "customer", "products"]
