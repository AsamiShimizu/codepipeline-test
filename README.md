# WordPress ECS Blue/Green デプロイ

## ディレクトリ構成

```
.
├── buildspec.yml                       # CodeBuild ビルド定義
├── ecs/
│   ├── appspec.yml                     # CodeDeploy デプロイ定義
│   ├── ecs-task-definition.json        # ECS タスク定義テンプレート
│   ├── nginx/
│   │   ├── Dockerfile
│   │   └── default.conf               # 127.0.0.1:9000 で php-fpm に接続
│   ├── php-fpm/
│   │   ├── Dockerfile
│   │   └── docker-entrypoint-custom.sh
│   └── mysql/
│       └── Dockerfile
├── lambda/
│   ├── before_allow_traffic.py         # BeforeAllowTraffic フック
│   └── after_allow_traffic.py          # AfterAllowTraffic フック
├── iam/
│   ├── codebuild-policy.json
│   ├── codepipeline-policy.json
│   ├── codedeploy-trust-policy.json
│   └── lambda-policy.json
└── pipeline/
    └── pipeline-definition.json        # CodePipeline 定義
```

## 環境情報

| 項目 | 値 |
|------|-----|
| アカウント ID | 533876055951 |
| リージョン | ap-northeast-3 |
| クラスター | ashimizu-testwp-cluster |
| ALB | ashimizu-wordpress-alb |
| Blue TG | ashimizu-wordpress-tg-blue |
| Green TG | ashimizu-wordpress-tg-green |

## appspec.yml の修正が必要な箇所

GitHub に push する前に以下を実際の値に変更すること。

```yaml
Subnets:
  - subnet-xxxxxxxx   # ← 実際のサブネット ID
SecurityGroups:
  - sg-xxxxxxxx       # ← 実際のセキュリティグループ ID
```
