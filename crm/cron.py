"""
Cron jobs for the CRM application.
"""

from datetime import datetime


def log_crm_heartbeat():
    """
    Log a heartbeat message to confirm the CRM application is alive.
    This function is called every 5 minutes by django-crontab.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    log_file = "/tmp/crm_heartbeat_log.txt"

    try:
        with open(log_file, "a") as f:
            f.write(message)

        # Optionally query the GraphQL endpoint to verify it's responsive
        try:
            from gql import gql, Client
            from gql.transport.requests import RequestsHTTPTransport

            query_string = """
                query {
                    __schema {
                        queryType {
                            name
                        }
                    }
                }
            """

            transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
            client = Client(transport=transport, fetch_schema_from_transport=False)
            query = gql(query_string)
            result = client.execute(query)

            if result:
                print(
                    f"[{timestamp}] Heartbeat logged - GraphQL endpoint is responsive"
                )
        except Exception as e:
            print(
                f"[{timestamp}] Heartbeat logged - GraphQL endpoint check failed: {str(e)}"
            )

    except Exception as e:
        print(f"Error logging heartbeat: {str(e)}")


def update_low_stock():
    """
    Execute the UpdateLowStockProducts GraphQL mutation to restock low-stock products.
    This function is called every 12 hours by django-crontab.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"

    try:
        from gql import gql, Client
        from gql.transport.requests import RequestsHTTPTransport

        # GraphQL mutation to update low-stock products
        mutation_string = """
            mutation {
                updateLowStockProducts {
                    updatedProducts {
                        id
                        name
                        stock
                    }
                    message
                    errors
                }
            }
        """

        # Execute the mutation
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=False)
        mutation = gql(mutation_string)
        result = client.execute(mutation)

        # Log the results
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Low Stock Update Started\n")

            update_result = result.get("updateLowStockProducts", {})
            updated_products = update_result.get("updatedProducts", [])
            message = update_result.get("message", "")
            errors = update_result.get("errors", [])

            if errors:
                f.write(f"[{timestamp}] Errors: {', '.join(errors)}\n")
            else:
                f.write(f"[{timestamp}] {message}\n")
                for product in updated_products:
                    product_name = product.get("name", "N/A")
                    new_stock = product.get("stock", "N/A")
                    f.write(
                        f"[{timestamp}] Updated: {product_name} - New Stock: {new_stock}\n"
                    )

        print(f"[{timestamp}] Low stock products updated successfully")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Error: {str(e)}\n")
        print(f"Error updating low stock products: {str(e)}")
