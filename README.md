# GraphQL CRM Project

This project implements a simple CRM (Customer Relationship Management) system using **Django**, **Graphene‑Django**, and **django‑filter**. It exposes a GraphQL API with support for queries, mutations, and advanced filtering.

---

## 🚀 Installation & Usage (with uv)

### 1. Clone the Repository

```bash
git clone https://github.com/D0nG4667/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
```

---

### 2. Create Virtual Environment

```bash
uv venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows PowerShell
```

---

### 3. Install Dependencies

The project contains `pyproject.toml` and `uv.lock`, just run:

```bash
uv sync
```

This will:

- Read the `pyproject.toml` for declared dependencies.
- Use `uv.lock` to install the exact versions pinned for reproducibility.

---

### 4. Apply Migrations

```bash
python manage.py migrate
```

---

### 5. Run Development Server

```bash
python manage.py runserver
```

Server will start at:

```url
http://127.0.0.1:8000/
```

---

### 6. Access GraphQL Playground

Navigate to:

```url
http://127.0.0.1:8000/graphql
```

Here you can run queries like:

```graphql
query {
  allCustomers(filter: { nameIcontains: "Ali", createdAtGte: "2025-01-01T00:00:00Z" }) {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

---

### 7. Run Tests

```bash
python manage.py test crm.tests
```

---

## 📌 Tasks Overview

### **Task 0 – Project Setup**

- Initialized Django project `alx_backend_graphql_crm`.
- Created `crm` app for managing customers, products, and orders.
- Installed dependencies:
  - `django`
  - `graphene-django`
  - `django-filter`
- Configured `settings.py` with:
  - `INSTALLED_APPS = ['graphene_django', 'django_filters', 'crm']`
  - `GRAPHENE = { 'SCHEMA': 'alx_backend_graphql.schema.schema' }`

---

### **Task 1 – Models**

Defined core models in `crm/models.py`:

- **Customer**
  - `name`, `email`, `phone`
  - `created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True)`

- **Product**
  - `name`, `price`, `stock`

- **Order**
  - `customer` (FK → Customer)
  - `products` (M2M → Product)
  - `total_amount`, `order_date`

---

### **Task 2 – Filters**

Implemented custom filter classes in `crm/filters.py` using `django-filter`:

- **CustomerFilter**
  - `nameIcontains`, `emailIcontains`
  - `createdAtGte`, `createdAtLte`
  - `phonePattern` (custom method: startswith)

- **ProductFilter**
  - `nameIcontains`
  - `priceGte`, `priceLte`
  - `stockGte`, `stockLte`
  - `orderBy` (supports sorting by name, price, stock)

- **OrderFilter**
  - `totalAmountGte`, `totalAmountLte`
  - `orderDateGte`, `orderDateLte`
  - `customerName`, `productName`
  - `productId`

---

### **Task 3 – Schema Integration**

Defined GraphQL schema in `crm/schema.py`:

- **Nodes**: `CustomerNode`, `ProductNode`, `OrderNode` (Relay‑compatible, with filters).
- **Types**: `CustomerType`, `ProductType`, `OrderType`.
- **Mutations**:
  - `CreateCustomer`, `BulkCreateCustomers`
  - `CreateProduct`
  - `CreateOrder`
- **Queries**:
  - `allCustomers(filter: {...}, orderBy: [...])`
  - `allProducts(filter: {...}, orderBy: [...])`
  - `allOrders(filter: {...}, orderBy: [...])`

Integrated into root schema in `graphql_crm/schema.py`.

---

### **Task 4 – Testing**

Created unit tests in `crm/tests/test_filters.py`:

- **Customer filter test**: query by `nameIcontains` and `createdAtGte`.
- **Product filter test**: query by `priceGte`, `priceLte`, and sort by `stock`.
- **Order filter test**: query by `customerName`, `productName`, and `totalAmountGte`.

✅ All tests passed successfully.  
⚠️ RuntimeWarning about naive datetime was resolved by using `timezone.make_aware` for seeded datetimes.

---

## 🚀 Example Queries

### Filter Customers

```graphql
query {
  allCustomers(filter: { nameIcontains: "Ali", createdAtGte: "2025-01-01T00:00:00Z" }) {
    edges {
      node { id name email createdAt }
    }
  }
}
```

### Filter Products

```graphql
query {
  allProducts(filter: { priceGte: 100, priceLte: 1000 }, orderBy: ["-stock"]) {
    edges {
      node { id name price stock }
    }
  }
}
```

### Filter Orders

```graphql
query {
  allOrders(filter: { customerName: "Alice", productName: "Laptop", totalAmountGte: 500 }) {
    edges {
      node {
        id
        customer { name }
        products { name }
        totalAmount
        orderDate
      }
    }
  }
}
```

---

## ✅ Next Steps

- Extend filters to support **nested relationships** (e.g., filter orders by customer email).
- Add **mutation tests** for creating customers, products, and orders.
- Improve documentation with API usage examples.
