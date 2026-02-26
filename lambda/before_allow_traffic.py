"""
BeforeAllowTraffic Lambda
役割: :443 → Green への切り替え前に Test リスナー (:8080) 経由で動作確認を行う
      Succeeded → デプロイ続行  /  Failed → 自動ロールバック

Lambda 環境変数（コンソールで設定すること）:
  ALB_DNS_NAME : ashimizu-wordpress-alb の DNS 名
  TEST_PORT    : 8080（デフォルト）
"""

import boto3
import urllib.request
import urllib.error
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

codedeploy = boto3.client('codedeploy', region_name='ap-northeast-3')


def check_health(alb_dns: str, port: int) -> tuple[bool, str]:
    url = f"http://{alb_dns}:{port}/nginx-health"
    logger.info(f"ヘルスチェック: {url}")
    try:
        req = urllib.request.urlopen(url, timeout=10)
        code = req.getcode()
        body = req.read().decode('utf-8').strip()
        logger.info(f"レスポンス: status={code}, body={body}")
        if code == 200:
            return True, f"OK: {url} → {code}"
        return False, f"NG: 期待値=200, 実際={code}"
    except urllib.error.HTTPError as e:
        return False, f"HTTPError: {e.code} {e.reason}"
    except urllib.error.URLError as e:
        return False, f"URLError: {e.reason}"
    except Exception as e:
        return False, f"エラー: {str(e)}"


def check_wordpress(alb_dns: str, port: int) -> tuple[bool, str]:
    url = f"http://{alb_dns}:{port}/wp-login.php"
    logger.info(f"WordPress 疎通確認: {url}")
    try:
        req = urllib.request.urlopen(url, timeout=15)
        code = req.getcode()
        body = req.read().decode('utf-8')
        logger.info(f"レスポンス: status={code}, body_length={len(body)}")
        if code == 200 and "WordPress" in body:
            return True, "OK: WordPress ログインページを確認"
        elif code == 200:
            return False, "NG: ステータス200だが WordPress のコンテンツが見つからない"
        return False, f"NG: 期待値=200, 実際={code}"
    except urllib.error.HTTPError as e:
        return False, f"HTTPError: {e.code} {e.reason}"
    except urllib.error.URLError as e:
        return False, f"URLError: {e.reason}"
    except Exception as e:
        return False, f"エラー: {str(e)}"


def report(deployment_id: str, hook_id: str, status: str):
    # CodeDeploy に結果を報告しないとタイムアウトまで待ち続けるため必須
    logger.info(f"CodeDeploy 報告: {status}")
    codedeploy.put_lifecycle_event_hook_execution_status(
        deploymentId=deployment_id,
        lifecycleEventHookExecutionId=hook_id,
        status=status
    )


def handler(event, context):
    logger.info(f"イベント: {event}")

    deployment_id = event['DeploymentId']
    hook_id = event['LifecycleEventHookExecutionId']
    alb_dns = os.environ.get('ALB_DNS_NAME', '')
    test_port = int(os.environ.get('TEST_PORT', '8080'))

    if not alb_dns:
        logger.error("ALB_DNS_NAME が未設定")
        report(deployment_id, hook_id, 'Failed')
        return

    # チェック1: nginx ヘルスチェック
    ok, msg = check_health(alb_dns, test_port)
    logger.info(f"ヘルスチェック: {msg}")
    if not ok:
        logger.error(f"失敗 → ロールバック: {msg}")
        report(deployment_id, hook_id, 'Failed')
        return

    # チェック2: WordPress 疎通確認
    ok, msg = check_wordpress(alb_dns, test_port)
    logger.info(f"WordPress 確認: {msg}")
    if not ok:
        logger.error(f"失敗 → ロールバック: {msg}")
        report(deployment_id, hook_id, 'Failed')
        return

    logger.info("全チェック通過 → デプロイ続行")
    report(deployment_id, hook_id, 'Succeeded')
