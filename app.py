# -*- coding: utf8 -*-
from flask import Flask, request, abort, render_template
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests,os,urllib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


# import gspread,json,io
# from google.oauth2.service_account import Credentials
# from google.colab import userdata,files
# sheetUrl = 'https://docs.google.com/spreadsheets/d/1eTaynVYAtOs6qtEhIDWfV5Ch80juRYZ23Bbe03_M7Pk/edit#gid=0'
# scopes = ["https://www.googleapis.com/auth/spreadsheets"]
# CredjsonFile = '/etc/secrets/credentials.json'
# creds = Credentials.from_service_account_file(CredjsonFile,scopes=scopes)
# client = gspread.authorize(creds)




#tokens
LineNotifyToken = os.environ.get('LineNotifyToken')
ChannelAccessToken = os.environ.get('ChannelAccessToken')
ChannelSecret = os.environ.get('ChannelSecret')

kw = os.environ.get('KeyWord')
kw = kw.split(',')

def lineNotify(msg):
    token = LineNotifyToken
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + token
    }   
    payload = {'message': msg}
    # files = {'imageFile': open(picURI, 'rb')}
    r = requests.post(url, headers = headers, params = payload)
    return r.status_code
# def getKeyWord():
#     with open('kw.txt','r',encoding='utf8')as f:
#         kw= f.read().split(',')
#     return kw
def containKeyWord(stringText,keyword):
    return stringText.find(keyword) != -1


app = Flask(__name__)

# Channel access token:(選取自己的機器人→Messaging API→Channel access token)
line_bot_api = LineBotApi(ChannelAccessToken)
# Channel secret:(選取自己的機器人→Basic settings→Channel secret)
handler = WebhookHandler(ChannelSecret)

@ app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@ handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    Tags =[]
    for k in kw:
        if containKeyWord(event.message.text,k):
            Tags.append(f'#{k}')
    if len(Tags)>0:
        Tags = ' '.join(Tags)
        now = datetime.now() + timedelta(hours=8)
        msg= f'''{now.strftime('%m%d %H%M')}  {Tags}
{event.message.text}
'''
        if len(msg)>=950:
            msg= f'''[擷取]{now.strftime('%m%d %H%M')}   {Tags}
{event.message.text[:890]}...'''
        lineNotify(msg)
    # if event.message.text =='a':
        # msg = (TextSendMessage(text='這是測試'))
        # line_bot_api.reply_message(event.reply_token, msg)

if __name__ == "__main__":
    port = int(os.environ.get('PORT',5050))
    app.run(host='0.0.0.0', port=port)
