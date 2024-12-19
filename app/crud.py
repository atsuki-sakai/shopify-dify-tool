from fastapi import FastAPI, HTTPException, Query
from app.models import Item, ItemCreate, Product, ShopifyCredentials, Order, OrderStatus
from app.database import get_firestore_client
from typing import List, Optional
from datetime import datetime, timezone
import json
import logging
from app.shopify import ShopifyClient

# FirestoreとRedisの初期化
db = get_firestore_client()
collection_name = "shopify-dify-tool"

app_name = "Shopify Dify Tool API"
version = "1.0.0"

def create_app() -> FastAPI:
    app = FastAPI(title=app_name, version=version)

    logging.basicConfig(level=logging.INFO)

    @app.post("/items", response_model=Item)
    def create_item(item: ItemCreate):
        try:
            # Firestoreにデータを保存
            doc_ref = db.collection(collection_name).document()
            data = item.dict()
            created_at = datetime.now(timezone.utc)
            data["created_at"] = created_at.isoformat() 
            doc_ref.set(data)

            return {"id": doc_ref.id, **data}
        except Exception as e:
            logging.error(f"Error creating item: {e}")
            raise HTTPException(status_code=500, detail="Failed to create item.")

    @app.get("/items/{item_id}", response_model=Item)
    def get_item(item_id: str):
        try:
            # Firestoreからデー���を取得
            doc = db.collection(collection_name).document(item_id).get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Item not found")

            data = doc.to_dict()
            return {"id": doc.id, **data}
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error retrieving item {item_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve item.")

    @app.get("/items", response_model=List[Item])
    def list_items():
        try:
            # Firestoreからデータを取得
            docs = db.collection(collection_name).stream()
            items = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            return items
        except Exception as e:
            logging.error(f"Error listing items: {e}")
            raise HTTPException(status_code=500, detail="Failed to list items.")

    @app.put("/items/{item_id}", response_model=Item)
    def update_item(item_id: str, item: ItemCreate):
        try:
            # Firestoreのドキュメントを更新
            doc_ref = db.collection(collection_name).document(item_id)
            if not doc_ref.get().exists:
                raise HTTPException(status_code=404, detail="Item not found")
    
            data = item.dict()
            updated_at = datetime.now(timezone.utc)
            data["updated_at"] = updated_at.isoformat() 
            doc_ref.update(data)
            # 更新前のcreated_atを取得
            doc = doc_ref.get()
            created_at = doc.to_dict().get("created_at")
            return {"id": item_id, "created_at": created_at, **data}
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error updating item {item_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update item.")

    @app.delete("/items/{item_id}")
    def delete_item(item_id: str):
        try:
            # Firestoreのドキュメントを削除
            doc_ref = db.collection(collection_name).document(item_id)
            if not doc_ref.get().exists:
                raise HTTPException(status_code=404, detail="Item not found")
            doc_ref.delete()

            return {"message": "Item deleted successfully"}
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error deleting item {item_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete item.")

    @app.post("/shopify/products", response_model=List[Product])
    def list_shopify_products(credentials: ShopifyCredentials):
        try:
            shopify_client = ShopifyClient(
                api_key=credentials.api_key,
                access_token=credentials.access_token,
                store_url=credentials.store_url
            )
            products = shopify_client.get_products()
            return [{"id": p.id, "name": p.title, "description": p.body_html} for p in products]
        except Exception as e:
            logging.error(f"Error listing Shopify products: {e}")
            raise HTTPException(status_code=500, detail="Failed to list products.")

    @app.post("/shopify/products/{product_id}", response_model=Product)
    def get_shopify_product(product_id: int, credentials: ShopifyCredentials):
        try:
            shopify_client = ShopifyClient(
                api_key=credentials.api_key,
                access_token=credentials.access_token,
                store_url=credentials.store_url
            )
            product = shopify_client.get_product(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return {"id": product.id, "name": product.title, "description": product.body_html}
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error retrieving Shopify product {product_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve product.")

    @app.post("/shopify/orders", response_model=List[Order])
    async def list_shopify_orders(
        credentials: ShopifyCredentials,
        limit: Optional[int] = Query(default=100),
    ):
        try:
            logging.info(f"Fetching orders from store: {credentials.store_url}")
            
            shopify_client = ShopifyClient(
                api_key=credentials.api_key,
                access_token=credentials.access_token,
                store_url=credentials.store_url
            )
            
            orders = shopify_client.get_orders(limit=limit)
            
            return [{
                "id": int(order.id),
                "order_number": str(order.order_number),
                "total_price": float(order.total_price),
                "created_at": order.created_at,
                "financial_status": order.financial_status,
                "fulfillment_status": order.fulfillment_status or None,
                "customer_email": order.email or None,
                "items": [{
                    "product_id": int(item.product_id) if item.product_id else 0,
                    "variant_id": int(item.variant_id) if item.variant_id else None,
                    "title": str(item.title),
                    "quantity": int(item.quantity),
                    "price": float(item.price)
                } for item in order.line_items]
            } for order in orders]
        except Exception as e:
            logging.error(f"Error listing Shopify orders: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list orders: {str(e)}"
            )

    return app
