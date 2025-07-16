#!/bin/bash

# 感情日記アプリ デプロイスクリプト
# Usage: ./deploy.sh

set -e  # エラー時に停止

echo "🚀 感情日記アプリのデプロイを開始します..."

# 設定
APP_NAME="emotion_diary"
APP_DIR="/var/www/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="emotion_diary"
NGINX_CONF="/etc/nginx/sites-available/$APP_NAME"
USER="www-data"

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. システム更新とパッケージインストール
log_info "システムパッケージを更新中..."
sudo apt update && sudo apt upgrade -y

log_info "必要なパッケージをインストール中..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git

# 2. アプリケーションディレクトリ作成
log_info "アプリケーションディレクトリを準備中..."
sudo mkdir -p $APP_DIR
sudo mkdir -p /var/log/$APP_NAME
sudo chown -R $USER:$USER $APP_DIR
sudo chown -R $USER:$USER /var/log/$APP_NAME

# 3. Gitからコードを取得（既存の場合は更新）
log_info "アプリケーションコードを取得中..."
if [ -d "$APP_DIR/.git" ]; then
    log_info "既存のリポジトリを更新中..."
    cd $APP_DIR
    sudo -u $USER git pull origin main
else
    log_info "新規リポジトリをクローン中..."
    sudo -u $USER git clone https://github.com/yourusername/emotion_diary.git $APP_DIR
    cd $APP_DIR
fi

# 4. Python仮想環境セットアップ
log_info "Python仮想環境をセットアップ中..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u $USER python3 -m venv $VENV_DIR
fi

sudo -u $USER $VENV_DIR/bin/pip install --upgrade pip
sudo -u $USER $VENV_DIR/bin/pip install -r requirements.txt

# 5. 環境設定ファイル作成
log_info "環境設定ファイルを作成中..."
sudo -u $USER tee $APP_DIR/.env > /dev/null <<EOF
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///instance/emotion_diary.db
EOF

# 6. データベース初期化
log_info "データベースを初期化中..."
cd $APP_DIR
sudo -u $USER mkdir -p instance
sudo -u $USER $VENV_DIR/bin/python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"

# 7. Supervisorサービス設定
log_info "Supervisorサービスを設定中..."
sudo tee /etc/supervisor/conf.d/$SERVICE_NAME.conf > /dev/null <<EOF
[program:$SERVICE_NAME]
command=$VENV_DIR/bin/gunicorn --config gunicorn_config.py run:app
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/$APP_NAME/app.log
environment=PATH="$VENV_DIR/bin"
EOF

# 8. Nginx設定
log_info "Nginx設定を適用中..."
sudo cp nginx.conf $NGINX_CONF
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 9. ファイル権限設定
log_info "ファイル権限を設定中..."
sudo chown -R $USER:$USER $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod 644 $APP_DIR/instance/emotion_diary.db 2>/dev/null || true

# 10. サービス再起動
log_info "サービスを再起動中..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart $SERVICE_NAME

sudo nginx -t && sudo systemctl reload nginx

# 11. ファイアウォール設定
log_info "ファイアウォールを設定中..."
sudo ufw allow 'Nginx Full' 2>/dev/null || true
sudo ufw allow ssh 2>/dev/null || true

# 12. デプロイ完了確認
log_info "デプロイ状況を確認中..."
sleep 3

if sudo supervisorctl status $SERVICE_NAME | grep -q "RUNNING"; then
    log_success "✅ アプリケーションが正常に起動しました！"
else
    log_error "❌ アプリケーションの起動に失敗しました"
    sudo supervisorctl status $SERVICE_NAME
    exit 1
fi

if sudo nginx -t > /dev/null 2>&1; then
    log_success "✅ Nginx設定が正常です！"
else
    log_error "❌ Nginx設定にエラーがあります"
    sudo nginx -t
    exit 1
fi

# 13. 完了メッセージ
log_success "🎉 デプロイが完了しました！"
echo ""
echo "📋 デプロイ情報:"
echo "   アプリケーション: $APP_DIR"
echo "   ログファイル: /var/log/$APP_NAME/"
echo "   Nginx設定: $NGINX_CONF"
echo ""
echo "🔧 管理コマンド:"
echo "   アプリ再起動: sudo supervisorctl restart $SERVICE_NAME"
echo "   ログ確認: sudo tail -f /var/log/$APP_NAME/app.log"
echo "   Nginx再起動: sudo systemctl reload nginx"
echo ""
echo "🌐 アクセス: http://your-server-ip/"
echo ""
log_warning "⚠️  nginx.confのserver_nameを実際のドメインに変更してください"