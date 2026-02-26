#!/bin/bash
set -e

# =============================================================================
# docker-entrypoint-custom.sh
# 役割: 起動時に WordPress ファイルを共有ボリューム（/var/www/html）にコピーする
#       nginx コンテナが /var/www/html を read-only でマウントしてファイルを配信する
# =============================================================================

TARGET_DIR="/var/www/html"
SOURCE_DIR="/usr/src/wordpress"

echo "=== WordPress ファイルコピー開始 ==="

# 共有ボリュームが空の場合のみコピー（2回目以降の起動では index.php が存在する）
if [ ! -f "${TARGET_DIR}/index.php" ]; then
    echo "WordPress ファイルをコピー中: ${SOURCE_DIR} → ${TARGET_DIR}"
    cp -r ${SOURCE_DIR}/. ${TARGET_DIR}/
    echo "コピー完了"
else
    echo "WordPress ファイルは既に存在します。スキップ。"
fi

echo "=== WordPress ファイルコピー完了 ==="

# 元の WordPress エントリーポイントに処理を引き渡す
exec docker-entrypoint.sh "$@"
