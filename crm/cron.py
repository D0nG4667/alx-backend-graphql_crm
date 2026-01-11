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
