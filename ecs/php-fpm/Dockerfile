FROM wordpress:php8.1-fpm

# php-fpm-healthcheck インストール（HealthCheck コマンドで使用）
RUN curl -o /usr/local/bin/php-fpm-healthcheck \
    https://raw.githubusercontent.com/renatomefi/php-fpm-healthcheck/master/php-fpm-healthcheck \
    && chmod +x /usr/local/bin/php-fpm-healthcheck

# php-fpm の ping 設定を有効化（healthcheck が使用）
RUN echo "pm.status_path = /status" >> /usr/local/etc/php-fpm.d/zz-docker.conf \
    && echo "ping.path = /ping" >> /usr/local/etc/php-fpm.d/zz-docker.conf

# WordPress ファイルを共有ボリューム用ディレクトリにコピーするスクリプト
COPY docker-entrypoint-custom.sh /usr/local/bin/docker-entrypoint-custom.sh
RUN chmod +x /usr/local/bin/docker-entrypoint-custom.sh

ENTRYPOINT ["docker-entrypoint-custom.sh"]
CMD ["php-fpm"]
