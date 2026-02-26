# =============================================================================
# Stage 1: 設定ファイルのバリデーション
# =============================================================================
FROM alpine:3.19 AS config-validator

RUN apk add --no-cache mariadb mariadb-client

RUN mkdir -p /etc/mysql/conf.d

RUN { \
        echo '[mysqld]'; \
        echo 'character-set-server=utf8mb4'; \
        echo 'collation-server=utf8mb4_unicode_ci'; \
        echo ''; \
        echo 'innodb_buffer_pool_size=128M'; \
        echo 'innodb_log_file_size=64M'; \
        echo 'innodb_flush_log_at_trx_commit=2'; \
        echo 'innodb_flush_method=O_DIRECT'; \
        echo ''; \
        echo 'query_cache_type=1'; \
        echo 'query_cache_size=32M'; \
        echo 'query_cache_limit=2M'; \
        echo ''; \
        echo 'max_connections=100'; \
        echo 'wait_timeout=28800'; \
        echo 'interactive_timeout=28800'; \
        echo ''; \
        echo 'tmp_table_size=64M'; \
        echo 'max_heap_table_size=64M'; \
        echo 'table_open_cache=400'; \
        echo ''; \
        echo 'slow_query_log=0'; \
        echo 'general_log=0'; \
        echo ''; \
        echo '[client]'; \
        echo 'default-character-set=utf8mb4'; \
        echo ''; \
        echo '[mysql]'; \
        echo 'default-character-set=utf8mb4'; \
    } > /etc/mysql/conf.d/wordpress.cnf

# =============================================================================
# Stage 2: 本番イメージ
# =============================================================================
FROM mariadb:11.2-jammy

LABEL maintainer="WordPress Docker Environment"
LABEL description="Minimal MariaDB for WordPress"

COPY --from=config-validator /etc/mysql/conf.d/wordpress.cnf /etc/mysql/conf.d/wordpress.cnf

RUN rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/* \
    && rm -rf /usr/share/doc/* \
    && rm -rf /usr/share/man/*

EXPOSE 3306

CMD ["mariadbd"]
