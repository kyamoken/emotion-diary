# Gunicorn設定ファイル
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = None
group = None
tmp_upload_dir = None
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"