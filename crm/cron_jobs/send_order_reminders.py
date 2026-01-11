#!/usr/bin/env python
"""
Order Reminders Script
Queries the GraphQL endpoint for orders within the last 7 days
and logs reminders with timestamps.
"""

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Calculate the date 7 days ago
today = datetime.now()
seven_days_ago = today - timedelta(days=7)
seven_days_ago_str = seven_days_ago.isoformat()

# GraphQL query to fetch orders from the last 7 days
query_string = (
    """
    query {
        allOrders(filter: {orderDateGte: "%s"}) {
            edges {
                node {
                    id
                    orderDate
                    customer {
                        id
                        email
                        name
                    }
                }
            }
        }
    }
"""
    % seven_days_ago_str
)

try:
    # Set up the GraphQL client
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Execute the query
    query = gql(query_string)
    result = client.execute(query)

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Process orders and log reminders
    orders = result.get("allOrders", {}).get("edges", [])
    log_file = "/tmp/order_reminders_log.txt"

    with open(log_file, "a") as f:
        for order_edge in orders:
            order_node = order_edge.get("node", {})
            order_id = order_node.get("id", "N/A")
            customer_email = order_node.get("customer", {}).get("email", "N/A")
            customer_name = order_node.get("customer", {}).get("name", "N/A")

            log_entry = f"[{timestamp}] Order ID: {order_id}, Customer: {customer_name} ({customer_email})\n"
            f.write(log_entry)

    print("Order reminders processed!")

except Exception as e:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/order_reminders_log.txt"

    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] Error: {str(e)}\n")

    print(f"Error: {str(e)}", file=sys.stderr)
    sys.exit(1)
