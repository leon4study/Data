
import json
import sys
import requests

def send_msg(msg):
    #https://12teamtoday.tistory.com/145
    #위 링크 참고해서 url 수정해주세요
    url = "your_slack_address"
    
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
