from google.cloud import firestore
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import shopify

# .env ファイルをロード
load_dotenv()

def get_firestore_client():
    # 環境変数から環境を取得（デフォルトは "development"）
    environment = os.getenv("ENVIRONMENT", "development")
    
    # 開発環境の場合、サービスアカウントJSONのパスを環境変数から取得
    if environment == "development":
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path or not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Service account key file not found. Check your GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}"
            )
        # サービスアカウント資格情報をロード
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        return firestore.Client(credentials=credentials)
    
    # 本番環境（Cloud Run）ではデフォルト認証を使用
    return firestore.Client()

def init_shopify():
    SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
    SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
    SHOPIFY_STORE_NAME = os.getenv("SHOPIFY_STORE_NAME")

    shopify.ShopifyResource.set_site(f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10")

