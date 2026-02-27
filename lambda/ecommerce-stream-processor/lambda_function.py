import json       
import base64      
import boto3       
from datetime import datetime, timezone  
import uuid        

# Using boto3 client
s3 = boto3.client('s3')
BUCKET = 'ecommerce-pipeline-godson'


def lambda_handler(event, context):
    processed_records = []   # Array to hold successfully processed records
    skipped = 0            # counter for errors

    for record in event['Records']:
        try:
            #kineses sends data  as base 64, decode first to get original json file
            raw_data = base64.b64decode(
                record['kinesis']['data']
            ).decode('utf-8')

           # parse json to python dictionary
            payload = json.loads(raw_data)

            
            now = datetime.now(timezone.utc)
            payload['processed_at']  = now.isoformat()      
            payload['processing_id'] = str(uuid.uuid4())     

            #add partition fields for Glue/Athena performance
            
            payload['year']  = str(now.year)
            payload['month'] = str(now.month).zfill(2)   
            payload['day']   = str(now.day).zfill(2)
            payload['hour']  = str(now.hour).zfill(2)

            processed_records.append(payload)

        except Exception as e:
            print(f"Skipping bad record: {e}")
            skipped += 1
            continue


    if processed_records:
        now = datetime.now(timezone.utc)
        # using the s3 folder path as partitioning strategy for better performance in Athena/Glue
        key = (
            f"processed/"
            f"{now.year}/"
            f"{str(now.month).zfill(2)}/"
            f"{str(now.day).zfill(2)}/"
            f"{str(now.hour).zfill(2)}/"
            f"{uuid.uuid4()}.json"
        )

        # join all records into a single line json string
        body = '\n'.join(json.dumps(r) for r in processed_records)

        # Write to S3 — single API call for entire batch
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=body.encode('utf-8'),
            ContentType='application/json'
        )

        # These print statements appear in CloudWatch Logs
        print(f"SUCCESS: {len(processed_records)} records written → s3://{BUCKET}/{key}")
        print(f"Skipped: {skipped} bad records")

    return {
        'statusCode': 200,
        'processed': len(processed_records),
        'skipped': skipped
    }
