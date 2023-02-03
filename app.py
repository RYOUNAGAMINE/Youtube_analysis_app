import streamlit as st
import plotly.express as px
import datetime
import asyncio
import os
import re
import json
from dateutil.relativedelta import relativedelta
# from dotenv import load_dotenv
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
  return start_date, end_date,period

def ids_titles_function():
  video_analysis = execute_api_request(
    youtube_analytics.reports().query,
    ids='channel==MINE',
    startDate=start_date,
    endDate=datetime.date.today(),
    metrics='estimatedMinutesWatched,views,likes,subscribersGained',
    dimensions='video',
    sort='-estimatedMinutesWatched',
    maxResults=50
  )

  rows = video_analysis['rows']
  video_ids = []
  for row in rows:
    video_id = row[0]
    video_ids.append(video_id)

  youtube = build(API_SERVICE_NAME_YOUYUBE, API_VERSION_YOUYUBE,  developerKey=DEVELOPER_KEY)
  response = youtube.videos().list(

  part="snippet",
  id =video_ids
  ).execute()

  video_titles=[]
  response = response['items']
  for item in response:
    video_title=item['snippet']['title']
    video_titles.append(video_title)



  ids_titles = {}
  for i in range(len(video_titles)):
    ids_titles[f'{video_ids[i]}'] = video_titles[i]

  return ids_titles

def get_key(val,id_title):
    for key, value in id_title.items():
        if val == value:
            return key

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
        print("リンクから認証を行ってください。1")
      credentials = flow.credentials
      st.session_state['credentials']=credentials_to_dict(credentials)



    youtube_analytics = build(API_SERVICE_NAME_ANALYTICS, API_VERSION_ANALYTICS, credentials = credentials,cache_discovery=False)


    periods = time_select()
    start_date = periods[0]
    end_date = periods[1]
    period = periods[2]
    

    channel_basis_data = ca.channel_basis_reports()
    st.write(channel_basis_data)


    channel_age_gender_graph = ca.age_gender_graph()
    st.write(channel_age_gender_graph)


    channel_basis_graph=ca.channel_basis_graph()
    channel_view = channel_basis_graph[0]
    channel_watch_hour = channel_basis_graph[1]
    channel_subscriber = channel_basis_graph[2]

    st.write(channel_view)
    st.write(channel_watch_hour)
    st.write(channel_subscriber)




    ids_titles = ids_titles_function()
    video_select = st.selectbox(label="動画を選択してください。",
    options=video_titles)
    st.button("リロード")
    


    VIDEO_ID = get_key(video_select,ids_titles)
    video_field = st.empty()
    url = f'https://youtu.be/{VIDEO_ID}'
    video_field.video(url)



    video_basis_data = va.channel_basis_reports()
    
    video_views = video_basis_data[0]
    video_hourWatched = int(video_basis_data[1] / 60)
    video_likes = video_basis_data[2]
    video_dislikes = video_basis_data[3]
    video_comments = video_basis_data[4]
    video_shares = video_basis_data[5]
    video_subscriber = video_basis_data[6]
      
    if period == 'カスタム':
      st.markdown('## 選択した期間中')
    else:
      st.markdown(f'## {period}の期間中')

    st.markdown(f'### 視聴回数  :  {video_views}回')
    st.markdown(f'### 視聴時間  :  {video_hourWatched}時間')
    st.markdown(f'### 高評価    : {video_likes}個')
    st.markdown(f'### 低評価    : {video_dislikes}個')
    st.markdown(f'### コメント  : {video_comments}個')
    st.markdown(f'### 共有      : {video_shares}回')
    st.markdown(f'### 登録者数  : {video_subscriber}人')
    
    video_graphs  = va.video_graph_function()
    video_view = video_graphs[0]
    video_watch_hour = video_graphs()[1]
    video_subscriber = video_graphs()[2]

    st.plotly_chart(video_view, use_container_width=True)
    st.plotly_chart(video_watch_hour, use_container_width=True)
    st.plotly_chart(video_subscriber, use_container_width=True)




    fulltime_second = va.time_minute()
    viewing_data = va.viewing_function(fulltime_second)

    viewing_graph = viewing_data[0]
    st.write("平均視聴率 : " + str(viewing_data[1]) +"%")
    st.write("平均視聴時間 : " + str(viewing_data[2]))
    st.plotly_chart(viewing_graph, use_container_width=True)

  except google.auth.exceptions.RefreshError:
    st.write("リンクから認証を行ってください。")
    print("リンクから認証を行ってください。2")
    traceback.print_exc()
    
  except Exception as e:
    traceback.print_exc()
    st.write("エラーが発生しました。")
    pass

  else:
    print ('正常に処理が完了しました')

