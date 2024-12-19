import shopify
import os

class ShopifyClient:
    def __init__(self, api_key: str, access_token: str, store_url: str):
        shop_url = f"https://{store_url}/admin/api/2024-01"
        shopify.ShopifyResource.set_site(shop_url)
        shopify.ShopifyResource.set_headers({'X-Shopify-Access-Token': access_token})

    def get_products(self):
        return shopify.Product.find()

    def get_product(self, product_id: int):
        return shopify.Product.find(product_id)