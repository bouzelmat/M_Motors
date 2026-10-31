resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts-${terraform.workspace}"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count     = var.monitoring_alert_email == null ? 0 : 1
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.monitoring_alert_email
}

resource "aws_cloudwatch_log_metric_filter" "backend_errors" {
  name           = "${local.common_name}-backend-errors"
  log_group_name = aws_cloudwatch_log_group.backend.name
  pattern        = "\"ERROR\""

  metric_transformation {
    name      = "ApplicationErrorCount"
    namespace = "M-Motors/Backend"
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "backend_errors" {
  alarm_name          = "${local.common_name}-backend-errors"
  alarm_description   = "Au moins 5 événements de journalisation ERROR du backend en 5 minutes."
  namespace           = "M-Motors/Backend"
  metric_name         = "ApplicationErrorCount"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  threshold           = 5
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alerts.arn]

  depends_on = [aws_cloudwatch_log_metric_filter.backend_errors]
}
