"""
AfterAllowTraffic Lambda
役割: :443 → Green への切り替え後にスモークテストと Slack 通知を行う
      Succeeded → Blue タスク削除待機へ  /  Failed → ロールバック

Lambda 環境変数（コンソールで設定すること）:
  ALB_DNS_NAME  : ashimizu-wordpress-alb の DNS 名
  PROD_PORT     : 80（デフォルト。HTTPS は ALB が処理するため HTTP で確認）
  SLACK_WEBHOOK : Slack Webhook URL（省略可）
"""

import boto3
import urllib.request
import urllib.error
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

codedeploy = boto3.client('codedeploy', region_name='ap-northeast-3')


def check_production(alb_dns: str, port: int) -> tuple[bool, str]:
    url = f"http://{alb_dns}:{port}/nginx-health"
    logger.info(f"本番確認: {url}")
    try:
        req = urllib.request.urlopen(url, timeout=15)
        code = req.getcode()
        logger.info(f"レスポンス: {code}")
        return code == 200, f"status={code}"
    except Exception as e:
        return False, str(e)


def notify_slack(webhook_url: str, message: str, success: bool):
    color = "#36a64f" if success else "#ff0000"
    icon = "✅" if success else "❌"
    payload = {
        "attachments": [{
            "color": color,
            "title": f"{icon} WordPress Blue/Green デプロイ通知",
            "text": message,
            "footer": "CodeDeploy AfterAllowTraffic"
        }]
    }
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=10)
        logger.info("Slack 通知完了")
    except Exception as e:
        # Slack 通知失敗はデプロイ結果に影響させない
        logger.warning(f"Slack 通知失敗（デプロイには影響なし）: {e}")


def get_deploy_info(deployment_id: str) -> dict:
    try:
        res = codedeploy.get_deployment(deploymentId=deployment_id)
        info = res.get('deploymentInfo', {})
        return {
            'application': info.get('applicationName', 'N/A'),
            'group': info.get('deploymentGroupName', 'N/A'),
        }
    except Exception as e:
        logger.warning(f"デプロイ情報取得失敗: {e}")
        return {}


def report(deployment_id: str, hook_id: str, status: str):
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
    prod_port = int(os.environ.get('PROD_PORT', '80'))
    slack_webhook = os.environ.get('SLACK_WEBHOOK', '')

    if not alb_dns:
        logger.error("ALB_DNS_NAME が未設定")
        report(deployment_id, hook_id, 'Failed')
        return

    deploy_info = get_deploy_info(deployment_id)
    ok, msg = check_production(alb_dns, prod_port)
    logger.info(f"本番確認: ok={ok}, {msg}")

    if ok:
        notify_msg = (
            f"*デプロイ成功*\n"
            f"Application: {deploy_info.get('application')}\n"
            f"DeploymentGroup: {deploy_info.get('group')}\n"
            f"DeploymentId: {deployment_id}\n"
            f":443 への切り替えが完了しました。"
        )
        if slack_webhook:
            notify_slack(slack_webhook, notify_msg, success=True)
        report(deployment_id, hook_id, 'Succeeded')
    else:
        notify_msg = (
            f"*デプロイ後確認失敗 → ロールバック*\n"
            f"Application: {deploy_info.get('application')}\n"
            f"DeploymentGroup: {deploy_info.get('group')}\n"
            f"DeploymentId: {deployment_id}\n"
            f"エラー: {msg}"
        )
        if slack_webhook:
            notify_slack(slack_webhook, notify_msg, success=False)
        logger.error(f"失敗 → ロールバック: {msg}")
        report(deployment_id, hook_id, 'Failed')
