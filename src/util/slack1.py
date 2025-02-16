import json
import sys
import requests
import dotenv
import os
from dotenv import load_dotenv

# 현재 실행 중인 폴더의 .env 파일 자동 로드
load_dotenv()

def send_msg(msg):
    
    url = os.getenv("slack_key_url")
    message = ("Crawling 알림\n" + msg) 
    title = (f"New Incoming Message :zap:") # 타이틀 입력
    slack_data = {
        "username": "NotificationBot", # 보내는 사람 이름
        "icon_emoji": ":satellite:",
        #"channel" : "#somerandomcahnnel",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
