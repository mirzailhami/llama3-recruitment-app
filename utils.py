# utils.py
import json
import boto3
import logging
import re

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_llama3(prompt):
    try:
        response = bedrock.invoke_model(
            modelId="arn:aws:bedrock:us-east-1:324037276468:inference-profile/us.meta.llama3-3-70b-instruct-v1:0",
            body=json.dumps({
                "prompt": prompt,
                "max_gen_len": 2048,
                "temperature": 0.5,
                "top_p": 0.9
            }),
            contentType="application/json",
            accept="application/json"
        )
        response_body = json.loads(response['body'].read().decode('utf-8'))
        logging.debug(f"Bedrock response: {response_body['generation']}")
        return response_body['generation']
    except Exception as e:
        logging.error(f"Bedrock error: {str(e)}")
        raise ValueError(f"Error calling Bedrock: {str(e)}")

def extract_markdown_block(raw_response):
    try:
        start = raw_response.find('```') + 3
        end = raw_response.find('```', start)
        if start == 2 or end == -1:
            raise ValueError("No valid Markdown block found")
        return raw_response[start:end].strip()
    except Exception as e:
        logging.error(f"Markdown extraction error: {raw_response}")
        raise ValueError(f"Error processing response: {str(e)}")

def extract_json_block(raw_response):
    try:
        # Use regex to find JSON block, optionally labeled with 'json'
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_response, re.DOTALL)
        if not match:
            # If no triple backticks, try parsing the entire response as JSON
            json_str = raw_response.strip()
            return json.loads(json_str)
        
        json_str = match.group(1).strip()
        if not json_str:
            raise ValueError("Empty JSON block found")
        
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logging.error(f"JSON extraction error: {raw_response}")
        raise ValueError(f"Error processing response: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in extract_json_block: {raw_response}")
        raise ValueError(f"Error extracting JSON: {str(e)}")