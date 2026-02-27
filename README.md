A fully serverless, event-driven ETL pipeline that ingests real-time e-commerce streaming data, processes and enriches it using AWS Lambda, stores it in a partitioned S3 data lake, and enables business analytics through Amazon Athena — all monitored via a live CloudWatch dashboard.
This project was built console-first for deep architectural understanding, demonstrating real-world Solutions Architect decision-making around service selection, IAM least-privilege design, cost optimisation, and data lake architecture.


<b>Sample Analytics Queries</b><br><br>
Revenue by Category
sqlSELECT
    category,
    COUNT(*) as total_orders,
    ROUND(SUM(revenue), 2) as total_revenue,
    ROUND(AVG(price), 2) as avg_price
FROM "ecommerce_analytics"."ecommerce_processed"
WHERE event_type = 'order_placed'
GROUP BY category
ORDER BY total_revenue DESC;


Cart Abandonment Rate
sqlSELECT
    ROUND(cart_abandons * 100.0 / cart_adds, 1) as abandonment_rate_pct,
    ROUND(orders_placed * 100.0 / cart_adds, 1) as conversion_rate_pct
FROM (
    SELECT
        COUNT(CASE WHEN event_type = 'cart_add' THEN 1 END) as cart_adds,
        COUNT(CASE WHEN event_type = 'cart_abandon' THEN 1 END) as cart_abandons,
        COUNT(CASE WHEN event_type = 'order_placed' THEN 1 END) as orders_placed
    FROM "ecommerce_analytics"."ecommerce_processed"
);


This project implements production-grade IAM policies — scoped to specific resources, not broad managed policies.
Lambda Kinesis Policy — reads from one specific stream only:
json{
  "Effect": "Allow",
  "Action": ["kinesis:GetRecords", "kinesis:GetShardIterator",
             "kinesis:DescribeStream", "kinesis:ListShards"],
  "Resource": "arn:aws:kinesis:eu-west-1:ACCOUNT_ID:stream/ecommerce-events-stream"
}
Lambda S3 Policy — writes to /processed/ folder only:
json{
  "Effect": "Allow",
  "Action": ["s3:PutObject"],
  "Resource": "arn:aws:s3:::ecommerce-pipeline-godson/processed/*"
}


https://github.com/user-attachments/assets/a3e97c71-5a55-4b40-9adc-6bb642ca12d8


Author<br>
Godson — <i>AWS Certified Developer & Solutions Architect</i>
