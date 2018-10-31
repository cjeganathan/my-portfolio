import json
import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    
    topic = sns.Topic('arn:aws:sns:us-east-1:516774481232:deployPortfolioTopic')

    try:
        portfolio_bucket = s3.Bucket('bytetechinc.com')
        build_bucket = s3.Bucket('portfolio.bytetechinc.com')
        
        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        
        topic.publish(Subject="Portfolio Deployed", Message="Charly Portfolio Deployed Successfully")
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="The Portfolio was not Deployed Successfully")
        raise
    return 'Hello from Lambda'
