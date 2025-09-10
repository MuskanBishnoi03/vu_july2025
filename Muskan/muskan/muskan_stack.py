# from aws_cdk import (
#     # Duration,
#      Stack,
#     aws_lambda as lambda_
#      # aws_sqs as sqs,
# )


# from constructs import Construct

# class MuskanStack(Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # Grant permissions to use the imported profile
#         lambda_function = lambda_.Function(self, "hellolambda",
#             runtime=lambda_.Runtime.PYTHON_3_12,
#             handler="hellolambda.lambda_handler",
#             code=lambda_.Code.from_asset("muskan/modules")
#         )

'''

from aws_cdk import (
    Stack, Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

class MuskanStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Lambda canary ---
        canary = _lambda.Function(
            self, "WebCanary",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="canary.handler",
            code=_lambda.Code.from_asset("./modules"),  # relative path to your canary.py
            timeout=Duration.seconds(30),
            environment={
                "TARGET_URL": "https://medilinks.com.au/",
                "NAMESPACE": "Canary",
                "SITE_NAME": "Medilinks",
            },
        )

        # Allow Lambda to publish metrics
        canary.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"],
        ))

        # Schedule: run every 5 minutes
        rule = events.Rule(
            self, "CanarySchedule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
        )
        rule.add_target(targets.LambdaFunction(canary))

        # Metrics
        availability_metric = cloudwatch.Metric(
            namespace="Canary", metric_name="Availability",
            period=Duration.minutes(5), statistic="Average",
        )
        latency_metric = cloudwatch.Metric(
            namespace="Canary", metric_name="LatencyMs",
            period=Duration.minutes(5), statistic="Average",
        )

        # Alarms
        cloudwatch.Alarm(
            self, "AvailabilityAlarm",
            metric=availability_metric,
            threshold=0.5,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            evaluation_periods=1, datapoints_to_alarm=1,
        )
        cloudwatch.Alarm(
            self, "LatencyAlarm",
            metric=latency_metric,
            threshold=2000,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            evaluation_periods=1, datapoints_to_alarm=1,
        )

        CfnOutput(self, "FunctionName", value=canary.function_name)
        CfnOutput(self, "Schedule", value=rule.rule_name)
'''
'''

from aws_cdk import (
    Stack, Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct
import json
from pathlib import Path

class MuskanStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Load sites from config ---
        sites = json.loads(
            Path(__file__).resolve().parent.parent.joinpath("modules", "websites.json").read_text()
        )

        # --- Canary Lambda ---
        canary = _lambda.Function(
            self, "WebCanary",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="canary.handler",
            code=_lambda.Code.from_asset("./modules"),
            timeout=Duration.seconds(30),
        )

        # Allow Lambda to put metrics
        canary.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"],
        ))

        # Schedule every 5 minutes
        rule = events.Rule(
            self, "CanarySchedule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
        )
        rule.add_target(targets.LambdaFunction(canary))

        # Create metrics and alarms for each site
        for site in sites:
            site_name = site["SITE_NAME"]

            availability_metric = cloudwatch.Metric(
                namespace="Canary",
                metric_name="Availability",
                dimensions_map={"SiteName": site_name},
                period=Duration.minutes(5),
                statistic="Average",
            )

            latency_metric = cloudwatch.Metric(
                namespace="Canary",
                metric_name="LatencyMs",
                dimensions_map={"SiteName": site_name},
                period=Duration.minutes(5),
                statistic="Average",
            )

            cloudwatch.Alarm(
                self, f"{site_name}AvailabilityAlarm",
                metric=availability_metric,
                threshold=0.5,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
            )

            cloudwatch.Alarm(
                self, f"{site_name}LatencyAlarm",
                metric=latency_metric,
                threshold=2000,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
            )

        CfnOutput(self, "FunctionName", value=canary.function_name)
        CfnOutput(self, "Schedule", value=rule.rule_name)
'''


from aws_cdk import (
    Stack, Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_dynamodb as dynamodb,
    CfnOutput,
)
from constructs import Construct
import json
from pathlib import Path

ALERT_EMAIL = "s8155246@live.vu.edu.au"   # put your email address here

class MuskanStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Load sites from modules/websites.json (path relative to this file) ---
        sites = json.loads(
            Path(__file__).resolve().parent.parent.joinpath("modules", "websites.json").read_text()
        )

        # --- Canary Lambda (reads websites.json and publishes metrics) ---
        canary = _lambda.Function(
            self, "WebCanary",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="canary.handler",
            code=_lambda.Code.from_asset("./modules"),   # path is relative to project root (where cdk.json lives)
            timeout=Duration.seconds(30),
        )
        canary.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:PutMetricData"],
            resources=["*"],
        ))

        # --- SNS Topic (email + lambda subscriber) ---
        topic = sns.Topic(self, "CanaryAlarmTopic", display_name="Website Canary Alarms")
        topic.add_subscription(subs.EmailSubscription(ALERT_EMAIL))

        # --- DynamoDB table for logging alarm state changes ---
        table = dynamodb.Table(
            self, "CanaryAlarmEvents",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        # --- Alarm logger Lambda: subscribed to SNS, writes to DynamoDB ---
        alarm = _lambda.Function(
            self, "Alarm",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="alarm.handler",
            code=_lambda.Code.from_asset("./modules"),
            timeout=Duration.seconds(30),
            environment={"TABLE_NAME": table.table_name},
        )
        table.grant_write_data(alarm)
        topic.add_subscription(subs.LambdaSubscription(alarm))

        # --- Schedule the canary every 5 minutes ---
        rule = events.Rule(
            self, "CanarySchedule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
        )
        rule.add_target(targets.LambdaFunction(canary))

        # --- Per-site metrics & alarms (keys match your JSON: SITE_NAME) ---
        for site in sites:
            site_name = site["SITE_NAME"]

            availability_metric = cloudwatch.Metric(
                namespace="Canary",
                metric_name="Availability",
                dimensions_map={"SiteName": site_name},   # must match canary dimension
                period=Duration.minutes(5),
                statistic="Average",
            )
            latency_metric = cloudwatch.Metric(
                namespace="Canary",
                metric_name="LatencyMs",
                dimensions_map={"SiteName": site_name},
                period=Duration.minutes(5),
                statistic="Average",
            )

            avail_alarm = cloudwatch.Alarm(
                self, f"{site_name}AvailabilityAlarm",
                metric=availability_metric,
                threshold=0.5,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                alarm_description=f"Availability below 0.5 for {site_name}",
            )
            latency_alarm = cloudwatch.Alarm(
                self, f"{site_name}LatencyAlarm",   
                metric=latency_metric,
                threshold=2000,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                alarm_description=f"Latency > 2000ms for {site_name}",
            )

            action = cw_actions.SnsAction(topic)
            avail_alarm.add_alarm_action(action)
            avail_alarm.add_ok_action(action)
            avail_alarm.add_insufficient_data_action(action)

            latency_alarm.add_alarm_action(action)
            latency_alarm.add_ok_action(action)
            latency_alarm.add_insufficient_data_action(action)

        # --- Outputs ---
        CfnOutput(self, "CanaryFunctionName", value=canary.function_name)
        CfnOutput(self, "ScheduleRule", value=rule.rule_name)
        CfnOutput(self, "SnsTopicArn", value=topic.topic_arn)
        CfnOutput(self, "AlarmTableName", value=table.table_name)
