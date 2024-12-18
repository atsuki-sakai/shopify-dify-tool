# Firestore API GCP デプロイガイド

このREADMEは、FirestoreとShopify Admin APIと連携するFastAPIアプリケーションをGoogle Cloud Platform (GCP)にデプロイするまでの手順を詳しく説明します。また、よくあるエラーやその解決方法についても記載しています。

用途:
- Difyのカスタムツールの作成
- firestoreをDBとしたバックエンドサーバー

---

## **プロジェクト概要**
このFastAPIアプリケーションは、Firestoreに対するCRUD操作とShopify Admin APIを利用した製品管理機能を提供します。主な機能は以下の通りです：
- **Firestore統合**: Firestoreへのデータ保存と取得。
- **Shopify Admin API統合**: Shopifyへの製品の作成、取得、更新、削除。
- **Google Cloud Run**: スケーラブルなプラットフォームでAPIをホスト。
- **Google Cloud Build**: 自動デプロイのためのCI/CDパイプライン。
- **Artifact Registry**: Dockerイメージの保存。
- **Firestore Security Rules**: Firestoreアクセスのセキュリティ確保。
- **OpenAPI (Swagger)**: APIスキーマのドキュメント化。

---

## **前提条件**

### **1. GCPのセットアップ**
- 課金が有効なGCPプロジェクト。
- Firestoreモードを「ネイティブモード」に設定。
- 必要なAPIを有効化：
  - Firestore API
  - Shopify Admin API（外部APIとして設定）
  - Cloud Run API
  - Cloud Build API
  - Artifact Registry API

### **2. 必要なツールとライブラリ**
- Python 3.10以上
- Pythonパッケージ管理ツール `pip`
- GCP CLIツール `gcloud`（インストールおよび認証済み）
- ローカルにインストールされた `Docker` と `docker-compose`
- Firebase CLI（`npm install -g firebase-tools`でインストール）

### **3. 権限**
サービスアカウントには以下のロールが必要です：
- **Artifact Registry 管理者**
- **Cloud Build サービス アカウント**
- **Cloud Datastore ユーザー**
- **Cloud Run 管理者**
- **Firebase 管理者**
- **Firestore サービス エージェント**

### **4. Shopify APIの設定**
Shopify APIの認証情報を設定します。以下を追加：
- Shopify Admin APIの認証情報（APIキー、パスワード、ストア名）

---

## **ローカル開発**

### **1. リポジトリをクローン**
リポジトリをクローンし、プロジェクトフォルダに移動します：
```bash
git clone <repository-url>
cd <project-folder>
```

### **2. 依存関係をインストール**
必要なPythonパッケージをインストールします：
```bash
pip install -r requirements.txt
```

### **3. 環境変数を設定**
サービスアカウントJSONキーのパスとShopify APIの認証情報を環境変数として `.env` に設定します：
```env
GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
ENVIRONMENT=development
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_PASSWORD=your_shopify_password
SHOPIFY_STORE_NAME=your_store_name
```

### **4. アプリケーションを実行**
FastAPIアプリケーションをローカルで起動します：
```bash
uvicorn app.main:app --reload
```
ブラウザまたはPostmanで `http://127.0.0.1:8000` にアクセスしてエンドポイントをテストします。

### **5. OpenAPI (Swagger) ドキュメントの確認**
FastAPIでは、Swagger UIを自動生成します。以下のURLにアクセスしてAPIドキュメントを確認してください：
```plaintext
http://127.0.0.1:8000/docs
```
または、OpenAPIスキーマのJSONファイルを直接確認するには：
```plaintext
http://127.0.0.1:8000/openapi.json
```
Difyでこのスキーマを使用する場合は以下を追加して下さい。
```
"openapi": "3.1.0",
  "info": {
  "title": "Firestore and Shopify CRUD API",
  "version": "1.0.0"
},
"servers": [
  {
    "url": "<APIのエンドポイントのURL>"
  }
],
"paths": {}
```

### **6. OpenAPIスキーマのダウンロード**
OpenAPIスキーマをローカルに保存するには以下のコマンドを実行します：
```bash
curl -o openapi.json http://127.0.0.1:8000/openapi.json
```
これにより、現在のAPIスキーマが `openapi.json` として保存されます。

---

## **テスト**

### **1. Pytest用のテストコード**
以下のテストコードを `tests/test_main.py` に記述します：

```python
import pytest
from httpx import AsyncClient
from app.main import create_app

app = create_app()

@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/items", json={"name": "Test Item", "description": "A test description"})
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_item_not_found():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/nonexistent_id")
        assert response.status_code == 404
```

### **2. RedisのDockerコンテナの起動**
テスト用にRedisをDockerコンテナとして起動します：

```bash
docker run -d --name redis-test -p 6379:6379 redis
```

### **3. テストの実行方法**
以下のコマンドでpytestを実行します：

```bash
pytest
```

## **GCPへのデプロイ**

### **1. DockerイメージをビルドしてArtifact Registryにプッシュ**
```bash
gcloud artifacts repositories create my-repo --repository-format=docker --location=asia-northeast1

docker buildx build --platform=linux/amd64 -t asia-northeast1-docker.pkg.dev/$PROJECT_ID/my-repo/shopify-dify-tool .
docker buildx build --platform=linux/amd64 -t asia-northeast1-docker.pkg.dev/$PROJECT_ID/my-repo/shopify-api .
docker push asia-northeast1-docker.pkg.dev/$PROJECT_ID/my-repo/shopify-dify-tool
docker push asia-northeast1-docker.pkg.dev/$PROJECT_ID/my-repo/shopify-api
```

### **2. Cloud Runにデプロイ**
```bash
gcloud run deploy shopify-dify-tool \
    --image=asia-northeast1-docker.pkg.dev/$PROJECT_ID/my-repo/shopify-dify-tool \
    --region=asia-northeast1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

gcloud run deploy shopify-api \
    --image=asia-northeast1-docker.pkg.dev/$PROJECT_ID/my-repo/shopify-api \
    --region=asia-northeast1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars SHOPIFY_API_KEY=your_shopify_api_key,SHOPIFY_PASSWORD=your_shopify_password,SHOPIFY_STORE_NAME=your_store_name
```

### **3. デプロイの確認**
Cloud Runによって提供されたURLにアクセスし、FirestoreおよびShopifyのエンドポイントが動作していることを確認します。

---

## **Firestoreセキュリティルールの管理**

### **1. Firestoreルールをローカルで編集**
Firebase CLIを使用してFirestoreルールを初期化し、ルールファイルを作成します：
```bash
firebase init firestore
```
ルールファイル `firestore.rules` を編集します：
```plaintext
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

### **2. Firestoreルールをデプロイ**
Firebase CLIを使用してルールをデプロイします：
```bash
firebase deploy --only firestore:rules
```

### **注意**:
`gcloud firestore security-rules` コマンドを使用してルールをデプロイすることもできますが、Firebase CLIを使用する方が簡単です。

---

## **よくあるエラーとその解決方法**

### **1. 権限が不足しているエラー**
- **エラー**: `google.api_core.exceptions.PermissionDenied: 403 Missing or insufficient permissions.`
- **解決方法**: サービスアカウントに必要なロール（`roles/datastore.user`, `roles/datastore.admin`）が付与されていることを確認します。

### **2. サービスアカウントJSONが見つからない**
- **エラー**: `FileNotFoundError: Service account key file not found.`
- **解決方法**: 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` が有効なJSONキーを指していることを確認します。

### **3. Firestore APIが有効になっていない**
- **エラー**: `google.api_core.exceptions.NotFound: 404 The project does not have Firestore enabled.`
- **解決方法**: GCPコンソールでFirestore APIを有効化します。

### **4. Mac (M1/M2)でのデプロイが失敗**
- **エラー**: `Cloud Run does not support the selected platform.`
- **解決方法**: Dockerイメージビルド時に `--platform=linux/amd64` を使用します。

---

## **開発用ブランチを切って継続的に機能を追加する方法**

### **1. Gitリポジトリの準備**
プロジェクトディレクトリに移動し、リモートリポジトリを確認します：
```bash
git remote -v
```

### **2. 開発用ブランチの作成**
新しいブランチを作成してチェックアウトします。ブランチ名には機能や目的を明示する名前を付けます：
```bash
git checkout -b feature/add-new-endpoint
```

### **3. 作業内容の実装**
コードの変更や新機能の実装を行います。

### **4. 変更のステージングとコミット**
変更を確認し、ステージングしてコミットします
```bash
git status
git add .
git commit -m "Add a new endpoint for item details"
```

### **5. リモートリポジトリへのプッシュ**
新しいブランチをリモートリポジトリにプッシュします：
```bash
git push origin feature/add-new-endpoint
```

### **6. プルリクエストの作成**
GitHubやGitLabなどでプルリクエスト（Pull Request）を作成し、他のメンバーにレビューを依頼します。

### **7. レビューと修正**
レビューコメントを反映し、必要ならブランチに再度コミットします：
```bash
git commit -m "Fix review comments"
git push origin feature/add-new-endpoint
```

### **8. ブランチのマージ**
レビューが完了したら、開発ブランチをメインブランチ（例：main または develop）にマージします：
```bash
git checkout main
git pull origin main
git merge feature/add-new-endpoint
```

### **9. 古いブランチの削除**
マージが完了したら、不要になった開発ブランチを削除します：
```bash
git branch -d feature/add-new-endpoint
git push origin --delete feature/add-new-endpoint
```

### **10. CI/CD パイプラインの確認**
新しいコードがCI/CDパイプラインで正しくデプロイされることを確認します。

