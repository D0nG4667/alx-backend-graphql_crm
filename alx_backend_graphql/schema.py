import graphene

class Query(graphene.ObjectType):
    # Declare the field
    hello = graphene.String(default_value="Hello, GraphQL!")
