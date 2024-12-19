import shopify
import os
from dotenv import load_dotenv

# .env ファイルをロード
load_dotenv()

class ShopifyClient:
    def __init__(self, api_key: str, password: str, store_url: str):
        shop_url = f"https://{api_key}:{password}@{store_url}/admin/api/2023-10"
        shopify.ShopifyResource.set_site(shop_url)

    def get_products(self):
        return shopify.Product.find()

    def get_product(self, product_id: int):
        return shopify.Product.find(product_id)