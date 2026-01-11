"""
Celery tasks for the CRM application.
"""

import requests
from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report summarizing:
    - Total number of customers
    - Total number of orders
    - Total revenue (sum of order amounts)

    Logs the report to /tmp/crm_report_log.txt
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    try:
        # GraphQL query to fetch report data
        query_string = """
            query {
                allCustomers {
                    edges {
                        node {
                            id
                        }
                    }
                }
                allOrders {
                    edges {
                        node {
                            id
                            totalAmount
                        }
                    }
                }
            }
        """

        # Execute the query
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql(query_string)
        result = client.execute(query)

        # Extract data
        customers = result.get("allCustomers", {}).get("edges", [])
        orders = result.get("allOrders", {}).get("edges", [])

        total_customers = len(customers)
        total_orders = len(orders)

        # Calculate total revenue
        total_revenue = 0.0
        for order_edge in orders:
            order_node = order_edge.get("node", {})
            total_amount = order_node.get("totalAmount", 0)
            if total_amount:
                try:
                    total_revenue += float(total_amount)
                except (ValueError, TypeError):
                    pass

        # Log the report
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        with open(log_file, "a") as f:
            f.write(report_message)

        print(
            f"CRM Report generated: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"
        )
        return {
            "status": "success",
            "customers": total_customers,
            "orders": total_orders,
            "revenue": total_revenue,
        }

    except Exception as e:
        error_message = f"{timestamp} - Error generating report: {str(e)}\n"

        with open(log_file, "a") as f:
            f.write(error_message)

        print(f"Error generating CRM report: {str(e)}")
        return {"status": "error", "error": str(e)}
