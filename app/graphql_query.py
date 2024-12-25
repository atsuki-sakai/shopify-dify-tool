q_get_products = """
query GetProducts($first: Int!) {
    products(first: $first) {
        edges {
            node {
                id
                title
                description
                handle
                createdAt
                updatedAt
                variants(first: 1) {
                    edges {
                        node {
                            id
                            price
                            compareAtPrice
                        }
                    }
                }
                images(first: 1) {
                    edges {
                        node {
                                url
                        }
                    }
                }
            }
        }
    }
}
"""

q_get_product = """
    query GetProduct($id: ID!) {
        product(id: $id) {
            id
            title
            description
            handle
            createdAt
            updatedAt
            variants(first: 1) {
                edges {
                    node {
                        id
                        price
                        compareAtPrice
                    }
                }
            }
            images(first: 1) {
                edges {
                    node {
                        url
                    }
                }
            }
        }
    }
"""

q_get_orders = """
query GetOrders($first: Int!) {
    orders(first: $first) {
        edges {
            node {
                id
                totalPriceSet {
                  shopMoney {
                    amount
                  }
                }
                createdAt
                lineItems(first: 10) {
                  edges {
                    node {
                      product {
                        id
                      }
                      variant {
                        id
                      }
                      title
                      quantity
                      originalUnitPrice
                    }
                  }
                }
              }
            }
          }
        }
        """

q_get_customer_orders = """
query GetCustomerOrders($customerId: ID!, $first: Int!) {
  customer(id: $customerId) {
    createdAt
    displayName
    email
    phone
    tags
    productSubscriberStatus
    lastOrder {
      lineItems(first: 10) {
        edges {
          node {
            product {
              id
            }
            variant {
              id
            }
            title
            quantity
            originalUnitPrice
          }
        }
      }
    }
    defaultAddress {
      address1
      address2
      city
      country
      province
      zip
    }
    orders(first: $first) {
      edges {
        node {
          id
          createdAt
          totalPriceSet {
            shopMoney {
              amount
            }
          }
          lineItems(first: 10) {
            edges {
              node {
                product {
                  id
                }
                variant {
                  id
                }
                title
                quantity
                originalUnitPrice
              }
            }
          }
        }
      }
    }
  }
}
"""