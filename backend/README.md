# FastAPI ナレッジ修正・削除案投稿システム

FastAPIとSQLAlchemyを使用したナレッジ修正・削除案投稿システムです。既存のナレッジに対する修正案や削除案を提出し、承認プロセスを経て反映するシステムです。

## 機能

- ユーザー登録・認証（JWT認証）
- 管理者権限管理
- 既存記事の管理（CSVインポート機能）
- 記事番号による検索・バリデーション
- ナレッジ修正・削除案の作成・管理
- ステータス管理（下書き→提出→承認→反映）
- 権限ベースのステータス変更
- 外部システムURL生成

## データベース構造

### Userテーブル
- id: 主キー
- username: ユーザー名（ユニーク）
- hashed_password: ハッシュ化されたパスワード
- full_name: フルネーム
- is_admin: 管理者フラグ

### Articleテーブル（既存ナレッジ管理）
- article_uuid: 主キー（UUID）
- article_number: 記事番号（KBA-01234-AB567形式）
- title: 記事タイトル
- content: 記事内容
- is_active: 有効フラグ
- created_at: 作成日時
- updated_at: 更新日時

### Knowledgeテーブル（修正・削除案）
- id: 主キー
- article_number: 対象記事番号（Articleテーブルと関連付け）
- change_type: 変更種別（modify: 修正案, delete: 削除案）
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

### 記事管理関連
- `POST /articles/import` - CSVファイルから記事を一括インポート（管理者のみ）
- `GET /articles/` - 記事一覧を取得
- `GET /articles/search?q={query}` - 記事番号またはタイトルで記事を検索
- `GET /articles/{article_number}` - 記事番号で特定の記事を取得
- `GET /articles/uuid/{article_uuid}` - UUIDで特定の記事を取得
- `GET /articles/uuid/{article_uuid}/url` - 記事の外部システムURLを生成
- `GET /articles/{article_number}/proposals` - 特定記事に対する修正・削除案一覧を取得

### ナレッジ（修正・削除案）関連
- `POST /knowledge/` - 新しいナレッジ（修正・削除案）を作成（認証必要・記事番号バリデーション付き）
- `GET /knowledge/` - ナレッジ一覧を取得
- `GET /knowledge/status/{status}` - ステータス別ナレッジ一覧を取得
- `GET /knowledge/{knowledge_id}` - 特定のナレッジを取得
- `PUT /knowledge/{knowledge_id}` - ナレッジを更新（認証必要・作成者のみ）
- `PUT /knowledge/{knowledge_id}/status` - ナレッジのステータスを更新（権限チェック付き）
- `DELETE /knowledge/{knowledge_id}` - ナレッジを削除（認証必要・作成者のみ）

## 使用例

### 1. 管理者ユーザー登録
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

### 2. 一般ユーザー登録
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

### 3. ログイン
```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user1&password=password123"
```

### 4. CSVファイルから記事をインポート（管理者のみ）
CSVファイル形式：
```csv
article_uuid,article_number,title,content
550e8400-e29b-41d4-a716-446655440001,KBA-00001-AB123,FastAPI基礎知識,FastAPIの基本的な使い方について説明します
```

```bash
curl -X POST "http://localhost:8000/articles/import" \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
     -F "file=@articles.csv"
```

### 5. 記事検索
```bash
curl -X GET "http://localhost:8000/articles/search?q=KBA-00001"
```

### 6. ナレッジ（修正案）作成（認証トークンが必要）
```bash
curl -X POST "http://localhost:8000/knowledge/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{
       "article_number": "KBA-00001-AB123",
       "change_type": "modify",
       "title": "FastAPI基礎知識の修正案",
       "info_category": "技術",
       "keywords": "FastAPI, Python, 修正",
       "importance": true,
       "target": "開発者",
       "question": "FastAPIの基本的な使い方は？",
       "answer": "FastAPIは高性能なPython Webフレームワークで、自動的なAPIドキュメント生成機能があります。",
       "add_comments": "より詳細な説明を追加しました",
       "remarks": "初心者向けに内容を充実させました"
     }'
```

### 7. 削除案作成
```bash
curl -X POST "http://localhost:8000/knowledge/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{
       "article_number": "KBA-00002-CD456",
       "change_type": "delete",
       "title": "SQLAlchemy入門記事の削除案",
       "remarks": "内容が古くなったため削除を提案します"
     }'
```

### 8. ステータス変更（提出）
```bash
curl -X PUT "http://localhost:8000/knowledge/1/status" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{
       "status": "submitted"
     }'
```

### 9. 外部システムURL取得
```bash
curl -X GET "http://localhost:8000/articles/uuid/550e8400-e29b-41d4-a716-446655440001/url"
```

### 10. 特定記事に対する提案一覧
```bash
curl -X GET "http://localhost:8000/articles/KBA-00001-AB123/proposals"
```

## 外部システム連携

記事のUUIDを使用して、以下の形式で外部システムのURLが生成されます：

```
http://sv-vw-ejap:5555/SupportCenter/main.aspx?etc=127&extraqs=%3fetc%3d127%26id%3d%257b{article_uuid}%257d&newWindow=true&pagetype=entityrecord
```

## 権限管理

### 一般ユーザー
- 自分のナレッジの作成・更新・削除
- draft → submitted、submitted → draft のステータス変更
- 記事検索・閲覧

### 管理者
- 全てのナレッジの閲覧
- 全てのステータス変更（submitted → approved → published）
- ナレッジの差し戻し（approved → submitted）
- CSVファイルからの記事インポート

## 記事番号バリデーション

ナレッジ作成時に、指定された記事番号が既存のArticleテーブルに存在するかチェックします。存在しない記事番号が指定された場合は、エラーメッセージが返されます。

## 注意事項

- 本システムはSQLiteデータベースを使用しています（knowledge.db）
- 本番環境では、SECRET_KEYを環境変数から取得するように変更してください
- 本番環境では、PostgreSQLやMySQLなどのより堅牢なデータベースの使用を推奨します
- CSVインポート機能は管理者のみ利用可能です

## ファイル構成

- `main.py` - FastAPIアプリケーションのメインファイル
- `models.py` - SQLAlchemyモデル定義
- `schemas.py` - Pydanticスキーマ定義
- `database.py` - データベース設定
- `crud.py` - データベース操作関数
- `auth.py` - 認証関連のユーティリティ
- `requirements.txt` - 依存関係
- `test_articles.csv` - テスト用記事データ
