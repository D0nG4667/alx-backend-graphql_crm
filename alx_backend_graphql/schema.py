import graphene
from crm.schema import Query as CRMQuery

class Query(CRMQuery, graphene.ObjectType):
    # Declare the field
    hello = graphene.String(default_value="Hello, GraphQL!")

# Instantiate the schema
schema = graphene.Schema(query=Query)