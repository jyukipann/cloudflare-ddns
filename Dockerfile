FROM python:3.10-slim

# 作業ディレクトリ
WORKDIR /app

# ファイルをコピー
COPY cronjob /etc/cron.d/ddns-cron

RUN pip install requests

# cronをインストールし、設定を反映
RUN apt-get update && apt-get install -y cron
RUN chmod 0644 /etc/cron.d/ddns-cron && \
    crontab /etc/cron.d/ddns-cron

# cronサービスとログ出力を実行
CMD cron && tail -f /var/log/cron.log