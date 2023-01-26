import streamlit as st
import datetime
import asyncio
import os
from dateutil.relativedelta import relativedelta
# from dotenv import load_dotenv
import pandas as pd

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

DEVELOPER_KEY = "secret.json"
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
  period = st.selectbox(label="期間を指定してください。",
    options=["過去7日間","過去30日間","過去180日間","過去360日間","全期間","カスタム"])

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
      credentials = flow.credentials
      st.session_state['credentials']=credentials_to_dict(credentials)



    youtube_analytics = build(API_SERVICE_NAME_ANALYTICS, API_VERSION_ANALYTICS, credentials = credentials,cache_discovery=False)


    period = time_select()
    start_date = period[0]
    end_date = period[1]

    channel_analytics = execute_api_request(
          youtube_analytics.reports().query,
          ids='channel==MINE',
          startDate=start_date,
          endDate=end_date,
          metrics='views,estimatedMinutesWatched,likes,dislikes,comments,shares,subscribersGained',
          dimensions='channel',
      )
    penny = channel_analytics['rows'][0]

    print(penny)
    penny = penny.pop(1)
    penny = pd.Series(penny, index=['視聴回数','視聴時間(分)','いいね','バッド','コメント','シェア','チャンネル登録回数'])
    st.write(penny)

    video_analysis = execute_api_request(
      youtube_analytics.reports().query,
      ids='channel==MINE',
      # ids='contentOwner==OWNER_NAME,',
      startDate='2020-01-26',
      endDate='2022-07-31',
      metrics='estimatedMinutesWatched,views,likes,subscribersGained',
      dimensions='video',
      sort='-estimatedMinutesWatched',
      maxResults=10

    )
    rows = video_analysis['rows']
    video_ids = []
    for row in rows:
      video_id = row[0]
      video_ids.append(video_id)
    
    youtube = build(API_SERVICE_NAME_YOUYUBE, API_VERSION_YOUYUBE,  developerKey=DEVELOPER_KEY)
    search_response = youtube.videos().list(
    
    part="id",
    id =video_ids[0]
    ).execute()

    print(search_response)
    st.button("アクション")
    # st.columns(2)
  except Exception as e:
    print("エラーが発生しました")
    print(e)
    pass


