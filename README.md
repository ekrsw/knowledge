# FastAPI ナレッジ投稿システム

FastAPIとSQLAlchemyを使用したナレッジ投稿システムです。

## 機能

- ユーザー登録・認証（JWT認証）
- 管理者権限管理
- ナレッジの作成・読取・更新・削除（CRUD）
- ステータス管理（下書き→提出→承認→反映）
- ユーザーごとのナレッジ管理
- ナレッジ一覧表示（新しい順）
- ステータス別ナレッジ一覧

## データベース構造

### Userテーブル
- id: 主キー
- username: ユーザー名（ユニーク）
- hashed_password: ハッシュ化されたパスワード
- full_name: フルネーム
- is_admin: 管理者フラグ

### Knowledgeテーブル
- id: 主キー
- title: タイトル
- info_category: 情報カテゴリ
- keywords: キーワード
- importance: 重要度（Boolean）
- target: 対象者
- open_publish_start: 公開開始日
- open_publish_end: 公開終了日
- question: 質問
- answer: 回答
- add_comments: 追加コメント
- remarks: 備考
- status: ステータス（draft, submitted, approved, published）
- created_by: 作成者ID（Userテーブルの外部キー）
- submitted_at: 提出日時
- created_at: 作成日時
- updated_at: 更新日時

## ステータス管理

### ステータス種類
- **draft**: 下書き
- **submitted**: 提出
- **approved**: 承認
- **published**: 反映

### ステータス遷移ルール
- **作成者**: draft ⇔ submitted のみ可能
- **管理者**: 全てのステータス変更が可能

## セットアップ

1. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

2. アプリケーションを起動：
```bash
python main.py
```

または

```bash
uvicorn main:app --reload
```

3. ブラウザで http://localhost:8000/docs にアクセスしてSwagger UIを確認

## API エンドポイント

### ユーザー関連
- `POST /users/` - 新しいユーザーを作成
- `POST /token` - ログインしてアクセストークンを取得
- `GET /users/` - ユーザー一覧を取得
- `GET /users/{user_id}` - 特定のユーザーとナレッジを取得
- `GET /users/me/` - 現在のユーザー情報を取得
- `GET /users/{user_id}/knowledge/` - 特定ユーザーのナレッジ一覧を取得

### ナレッジ関連
- `POST /knowledge/` - 新しいナレッジを作成（認証必要）
- `GET /knowledge/` - ナレッジ一覧を取得
- `GET /knowledge/status/{status}` - ステータス別ナレッジ一覧を取得
- `GET /knowledge/{knowledge_id}` - 特定のナレッジを取得
- `PUT /knowledge/{knowledge_id}` - ナレッジを更新（認証必要・作成者のみ）
- `PUT /knowledge/{knowledge_id}/status` - ナレッジのステータスを更新（権限チェック付き）
- `DELETE /knowledge/{knowledge_id}` - ナレッジを削除（認証必要・作成者のみ）

## 使用例

### 1. 一般ユーザー登録
```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "user1",
       "password": "password123",
       "full_name": "一般ユーザー",
       "is_admin": false
     }'
```

### 2. 管理者ユーザー登録
```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "admin123",
       "full_name": "管理者",
       "is_admin": true
     }'
```

### 3. ログイン
```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user1&password=password123"
```

### 4. ナレッジ作成（認証トークンが必要）
```bash
curl -X POST "http://localhost:8000/knowledge/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{
       "title": "FastAPI入門",
       "info_category": "技術",
       "keywords": "FastAPI, Python, API",
       "importance": true,
       "target": "開発者",
       "question": "FastAPIとは何ですか？",
       "answer": "FastAPIは高性能なPython Webフレームワークです。",
       "add_comments": "初心者向けの内容です",
       "remarks": "定期的に更新予定"
     }'
```

### 5. ステータス変更（提出）
```bash
curl -X PUT "http://localhost:8000/knowledge/1/status" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{
       "status": "submitted"
     }'
```

### 6. ステータス別一覧取得
```bash
curl -X GET "http://localhost:8000/knowledge/status/submitted"
```

## 権限管理

### 一般ユーザー
- 自分のナレッジの作成・更新・削除
- draft → submitted、submitted → draft のステータス変更

### 管理者
- 全てのナレッジの閲覧
- 全てのステータス変更（submitted → approved → published）
- ナレッジの差し戻し（approved → submitted）

## 注意事項

- 本システムはSQLiteデータベースを使用しています（knowledge.db）
- 本番環境では、SECRET_KEYを環境変数から取得するように変更してください
- 本番環境では、PostgreSQLやMySQLなどのより堅牢なデータベースの使用を推奨します

## ファイル構成

- `main.py` - FastAPIアプリケーションのメインファイル
- `models.py` - SQLAlchemyモデル定義
- `schemas.py` - Pydanticスキーマ定義
- `database.py` - データベース設定
- `crud.py` - データベース操作関数
- `auth.py` - 認証関連のユーティリティ
- `requirements.txt` - 依存関係
