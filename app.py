import streamlit as st
import plotly.express as px
import datetime
import asyncio
import os
import re
import json
from dateutil.relativedelta import relativedelta

import pandas as pd
import traceback
import datetime
import channel_analytics as ca
import video_analytics as va

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build


SCOPES_ANALYTICS = ['https://www.googleapis.com/auth/yt-analytics.readonly']
API_SERVICE_NAME_ANALYTICS = 'youtubeAnalytics'
API_VERSION_ANALYTICS = 'v2'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES_YOUTUBE= ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME_YOUYUBE = 'youtube'
API_VERSION_YOUYUBE = 'v3'

with open('secret.json') as f:
  secret = json.load(f)
DEVELOPER_KEY = secret['KEY']
CLIENT_SECRETS_FILE = 'YOUR_CLIENT_SECRET_FILEwebapp.json'

def get_login_str():

  return f'''
  <a target="_self"
  href="{authorization_url}">Google login</a>'''

def execute_api_request(client_library_function, **kwargs):
  response = client_library_function(
    **kwargs
  ).execute()
  return response


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def time_select():

  if period == "過去7日間":
    start_date = datetime.date.today() - datetime.timedelta(days=6)
    end_date = datetime.date.today()
  elif period == "過去30日間":
    start_date =  datetime.date.today() - datetime.timedelta(days=29)
    end_date = datetime.date.today()
  elif period == "過去180日間":
    start_date = datetime.date.today() - datetime.timedelta(days=179)
    end_date = datetime.date.today()
  elif period == "過去360日間":
    start_date = datetime.date.today() - datetime.timedelta(days=359)
    end_date = datetime.date.today()
  elif period == "全期間":
    start_date = datetime.date(2020,4,26)
    end_date = datetime.date.today()
  elif period == "カスタム":
    start_date = st.date_input(
      '開始日',
      datetime.date.today() - relativedelta(months=1),
      datetime.date(2020,4,26),
      datetime.date.today() - datetime.timedelta(days=1)
    )
    end_date = st.date_input(
      '終了日',
      datetime.date.today(),
      start_date + datetime.timedelta(days=1),
      datetime.date.today()
    )
  return start_date, end_date





flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES_ANALYTICS)
flow.redirect_uri = 'http://localhost:8501'

authorization_url, state = flow.authorization_url(
  access_type='offline',
  login_hint='ryou110216@yahoo.co.jp',
  include_granted_scopes='true')






st.title("Youtube分析ダッシュボード")

st.write(get_login_str(),unsafe_allow_html=True)
period = st.selectbox(label="期間を指定してください。",
  options=["過去7日間","過去30日間","過去180日間","過去360日間","全期間","カスタム"])

PAGES = {
    "チャンネルのアナリティクス": ca,
    "動画のアナリティクス": va
}
st.sidebar.title('メニュー')
selection_analytics = st.sidebar.radio("選択してください。", list(PAGES.keys()))
page = PAGES[selection_analytics]
# page.app()
st.sidebar.button("リロード")

if 'code' in st.experimental_get_query_params() or  'credentials' in st.session_state:
  try:
    if  'credentials' in st.session_state:
      credentials = google.oauth2.credentials.Credentials(
      **st.session_state['credentials'])
      st.session_state['credentials']=credentials_to_dict(credentials)
    else:
      authorization_response = st.experimental_get_query_params()['code']
      authorization_response=authorization_response[0]
      try:
        flow.fetch_token(code=authorization_response)
      except:
        st.write("リンクから認証を行ってください。")
        print("リンクから認証を行ってください。1")
      credentials = flow.credentials
      st.session_state['credentials']=credentials_to_dict(credentials)



    youtube_analytics = build(API_SERVICE_NAME_ANALYTICS, API_VERSION_ANALYTICS, credentials = credentials,cache_discovery=False)
    youtube = build(API_SERVICE_NAME_YOUYUBE, API_VERSION_YOUYUBE,  developerKey=DEVELOPER_KEY)

    periods = time_select()
    start_date = periods[0]
    end_date = periods[1]

    if page == ca:
      page.app_channel(youtube_analytics,start_date,end_date)

    if page == va:
      page.app_video(youtube_analytics,youtube,start_date,end_date,period)

  except google.auth.exceptions.RefreshError:
    st.write("リンクから認証を行ってください。")
    traceback.print_exc()
    print("リンクから認証を行ってください。2")

  except Exception as e:
    traceback.print_exc()
    st.write("エラーが発生しました。")
    pass

  else:
    print ('正常に処理が完了しました')

