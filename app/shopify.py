import requests
import logging
from typing import List, Optional, Dict, Any
from app.graphql_query import q_get_products, q_get_orders, q_get_product, q_get_customer_orders

SHOPIFY_GRAPHQL_API_VERSION = "2024-10"

class ShopifyClient:

    def __init__(self, access_token: str, store_url: str):
        self.store_url = f"https://{store_url}/admin/api/{SHOPIFY_GRAPHQL_API_VERSION}/graphql.json"
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }

    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            response = requests.post(
                self.store_url,
                headers=self.headers,
                json={'query': query, 'variables': variables or {}}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"GraphQL query execution failed: {e}")
            raise

    def get_products(self, first: int = 10) -> List[Dict[str, Any]]:
       
        variables = {"first": first}
        result = self.execute_query(q_get_products, variables)
        
        if 'data' in result and 'products' in result['data']:
            return [
                {
                    "id": int(node['id'].split('/')[-1]),
                    "name": node['title'],
                    "description": node['description'],
                    "handle": node['handle'],
                    "created_at": node['createdAt'],
                    "updated_at": node['updatedAt'],
                    "price": node['variants']['edges'][0]['node']['price'] if node['variants']['edges'] else None,
                    "image_url": node['images']['edges'][0]['node']['url'] if node['images']['edges'] else None
                }
                for node in [edge['node'] for edge in result['data']['products']['edges']]
            ]
        return []

    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
       
        variables = {"id": f"gid://shopify/Product/{product_id}"}
        result = self.execute_query(q_get_product, variables)
        
        if 'data' in result and 'product' in result['data'] and result['data']['product']:
            product = result['data']['product']
            return {
                "id": int(product['id'].split('/')[-1]),
                "name": product['title'],
                "description": product['description'],
                "handle": product['handle'],
                "created_at": product['createdAt'],
                "updated_at": product['updatedAt'],
                "price": product['variants']['edges'][0]['node']['price'] if product['variants']['edges'] else None,
                "image_url": product['images']['edges'][0]['node']['url'] if product['images']['edges'] else None
            }
        return None

    def get_orders(self, first: int = 10) -> List[Dict[str, Any]]:
       
        variables = {"first": first}
        result = self.execute_query(q_get_orders, variables)
        
        if 'data' in result and 'orders' in result['data']:
            return [
                {
                    "id": int(node['id'].split('/')[-1]),
                    "order_number": node['name'],
                    "total_price": float(node['totalPriceSet']['shopMoney']['amount']),
                    "created_at": node['createdAt'],
                    "customer_email": node['email'],
                    "items": [
                        {
                            "product_id": int(item['node']['product']['id'].split('/')[-1]) if item['node']['product'] else None,
                            "variant_id": int(item['node']['variant']['id'].split('/')[-1]) if item['node']['variant'] else None,
                            "title": item['node']['title'],
                            "quantity": item['node']['quantity'],
                            "price": float(item['node']['originalUnitPrice'])
                        }
                        for item in node['lineItems']['edges']
                    ]
                }
                for node in [edge['node'] for edge in result['data']['orders']['edges']]
            ]
        return []

    def get_customer_orders(self, customer_id: str, first: int = 10) -> List[Dict[str, Any]]:
        variables = {
            "customerId": f"gid://shopify/Customer/{customer_id}",
            "first": first
        }
        result = self.execute_query(q_get_customer_orders, variables)
        
        if ('data' in result and 'customer' in result['data'] and 
            result['data']['customer']):
            customer = result['data']['customer']
            return {
                "created_at": customer['createdAt'],
                "display_name": customer['displayName'],
                "email": customer['email'],
                "phone": customer['phone'],
                "tags": customer['tags'],
                "product_subscriber_status": customer['productSubscriberStatus'],
                "last_order": {
                    "items": [
                        {
                            "product_id": int(item['node']['product']['id'].split('/')[-1]) if item['node']['product'] else None,
                            "variant_id": int(item['node']['variant']['id'].split('/')[-1]) if item['node']['variant'] else None,
                            "title": item['node']['title'],
                            "quantity": item['node']['quantity'],
                            "price": float(item['node']['originalUnitPrice'])
                        }
                        for item in customer['lastOrder']['lineItems']['edges']
                    ]
                } if customer.get('lastOrder') else None,
                "default_address": {
                    "address1": customer['defaultAddress']['address1'],
                    "address2": customer['defaultAddress']['address2'],
                    "city": customer['defaultAddress']['city'],
                    "country": customer['defaultAddress']['country'],
                    "province": customer['defaultAddress']['province'],
                    "zip": customer['defaultAddress']['zip']
                } if customer.get('defaultAddress') else None,
                "orders": [
                    {
                        "id": int(node['id'].split('/')[-1]),
                        "order_number": node['name'],
                        "total_price": float(node['totalPriceSet']['shopMoney']['amount']),
                        "created_at": node['createdAt'],
                        "customer_email": node['email'],
                        "items": [
                            {
                                "product_id": int(item['node']['product']['id'].split('/')[-1]) if item['node']['product'] else None,
                                "variant_id": int(item['node']['variant']['id'].split('/')[-1]) if item['node']['variant'] else None,
                                "title": item['node']['title'],
                                "quantity": item['node']['quantity'],
                                "price": float(item['node']['originalUnitPrice'])
                            }
                            for item in node['lineItems']['edges']
                        ]
                    }
                    for node in [edge['node'] for edge in customer['orders']['edges']]
                ]
            }
        return None