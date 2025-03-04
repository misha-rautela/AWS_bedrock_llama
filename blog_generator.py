#File has mainly three functions 
#1.blog_generate_using_bedrock() : It has LLM model details and it invokes the model and response is captured.
#2.lambda_handler() : to call the aws lambda function, it calls the blog_generate_using_bedrock once the blog is generated it calls save_blog_details_s3 to save the details in S3 bucket.
#3.save_blog_details_s3(): it saves the blog in the S3 bucket in the form of text file.

import boto3
import botocore.config
import json
import response
import datetime

def blog_generate_using_bedrock(blogtopic:str)-> str:
    prompt=f"""<s>[INST]Human: Write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]
    """
    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }

    try:
        bedrock=boto3.client("bedrock-runtime",rregion_name="us-east-1",
                            config=botocore.config.Config(read_timeout=300,retries={'max_attempts'=3}))
        response=bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-8b-instruct-v1:0")
        response_content=response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        #gereration is the key variable where data is saved
        blog_details=response_data['generation']
        return blog_details
    except Exception as ex:
        print(f"Error generating the blog:{ex}")
        return ""
        
def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    blogtopic=event['blog_topic']

    generate_blog=blog_generate_using_bedrock(blogtopic=blogtopic)

    if generate_blog:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key=f"blog-output/{current_time}.txt"
        s3_bucket='mishabedrockbucket1'
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)
    else:
        print("No blog was generated")

    return{
        'statusCode':200,
        'body': json.dumps('Hello from Lambda!')
    }
def save_blog_details_s3(s3_key,s3_bucket,generate_blog):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body =generate_blog )
        print("Code saved to s3 bucket")

    except Exception as ex:
        print("Error when saving the code to s3 bucket")
