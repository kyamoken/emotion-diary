# 感情日記 (Emotion Diary)

AI搭載の感情分析付き日記アプリケーション

## 🌟 特徴

- **AI感情分析**: BERT多言語モデルによる自動感情分析（ポジティブ/ネガティブ/ニュートラル）
- **自動タグ付け**: KeyBERTによる内容に基づく自動タグ生成
- **完全プライベート**: ユーザー毎に完全に分離された日記データ
- **レスポンシブデザイン**: スマホ・タブレット・PC対応
- **PWA対応**: オフライン機能とホーム画面追加可能
- **美しいUI**: モダンなグラデーションデザイン

## 🚀 技術スタック

- **バックエンド**: Flask, SQLAlchemy, Flask-Login
- **AI**: Transformers (BERT), TextBlob, KeyBERT, scikit-learn
- **フロントエンド**: Bootstrap 5, Jinja2
- **データベース**: SQLite
- **PWA**: Service Worker対応

## 📦 インストール

```bash
# リポジトリをクローン
git clone https://github.com/kyamoken/emotion-diary.git
cd emotion-diary

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
python run.py
```

## 🌐 デプロイ

### Nginx + Gunicorn での本番環境デプロイ

```bash
# Gunicornでアプリケーションを起動
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📱 使い方

1. **新規登録**: ユーザー名、メール、パスワードで登録
2. **ログイン**: 登録した情報でログイン
3. **日記作成**: 日付と内容を入力して保存
4. **AI分析**: 自動で感情分析とタグ付けが実行
5. **検索**: 感情やタグで過去の日記を検索

## 🔒 プライバシー

- 各ユーザーの日記は完全に分離されています
- 他のユーザーがあなたの日記を見ることは技術的に不可能です
- データは全てローカルまたは指定されたサーバーに安全に保存されます

## 📄 ライセンス

MIT License# emotion-diary
