# ETF Crash Alert

This serverless application monitors ETFs for potential market crashes using Bollinger Bands analysis.

## Architecture

```mermaid
architecture-beta
    group monitoring(fa:fa-cloud)[ETF Monitoring Stack]
        service scheduler(fa:fa-clock)[EventBridge Scheduler] in monitoring
        service analyzer(fa:fa-function)[Lambda Analyzer] in monitoring
        service logs(fa:fa-chart-line)[CloudWatch Logs] in monitoring
        service deployment(fa:fa-database)[S3 Deployment] in monitoring
        service security(fa:fa-key)[IAM Permissions] in monitoring
        service yahoo(fa:fa-chart-bar)[Yahoo Finance] in monitoring
        service telegram(fa:fa-bell)[Telegram Alerts] in monitoring

        scheduler:R --> L:analyzer
        analyzer:R --> L:logs
        deployment:T -- B:analyzer
        security:T -- B:analyzer
        analyzer:T --> B:yahoo
        analyzer:B --> T:telegram
```

## Components

- **EventBridge Rule**: Triggers the Lambda function every weekday at 11:00 AM (cron: 0 11 ? * MON-FRI *)
- **Lambda Function**: Executes the Bollinger Bands analysis on ETF data and sends alerts when price drops below threshold
- **CloudWatch Logs**: Stores execution logs from the Lambda function
- **IAM Role**: Provides necessary permissions for Lambda execution
- **S3 Bucket**: Stores the Lambda deployment package
- **Yahoo Finance**: Data source for ETF prices (SWDA.MI)
- **Telegram Bot**: Sends notifications when price drops below the lower Bollinger Band margin

[CloudFormation Stack](https://eu-south-1.console.aws.amazon.com/cloudformation/home?region=eu-south-1#/stacks/resources?filteringText=&filteringStatus=active&viewNested=true&stackId=arn%3Aaws%3Acloudformation%3Aeu-south-1%3A778425763547%3Astack%2Fswda-etf-crash-alert-prod%2Feb1703e0-a9ba-11ef-bfde-0e287014c749)
