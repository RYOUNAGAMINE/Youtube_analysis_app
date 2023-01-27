import streamlit as st
import plotly.express as px
import datetime
import asyncio
import os
import json
from dateutil.relativedelta import relativedelta
# from dotenv import load_dotenv
import pandas as pd
import traceback

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

    age_gender = execute_api_request(
      youtube_analytics.reports().query,
      ids='channel==MINE',
      startDate=start_date,
      endDate=end_date,
      dimensions='ageGroup,gender',
      metrics='viewerPercentage',
      sort='gender,ageGroup'
      )

    age_gender = age_gender['rows']

    for i in range(len(age_gender)):
      if age_gender[i][1] == 'female':
        age_gender[i][1] = '女性'
      elif age_gender[i][1] == 'male':
        age_gender[i][1] = '男性'

    Character = ["男性","女性"]
    Parent = ["",""]
    Value = [0,0]
    for i in range(len(age_gender)):
      Character.append(age_gender[i][0])
      Parent.append(age_gender[i][1])
      Value.append(age_gender[i][2])

    data = dict(
    character=Character,
    parent=Parent,
    value=Value)

    fig = px.sunburst(
        data,
        names='character',
        parents='parent',
        values='value',
    )
    st.write(fig)

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
    response = youtube.videos().list(

    part="snippet",
    id =video_ids
    ).execute()

    video_titles=[]
    response = response['items']
    # st.write(response)
    for item in response:
      video_title=item['snippet']['title']
      video_titles.append(video_title)

    # st.write(video_titles)
    video_select = st.selectbox(label="動画を選択してください。",
    options=video_titles)
    st.button("アクション")
    video_data = {}
    for i in range(len(video_titles)):
      video_data[f'{video_ids[i]}'] = video_titles[i]

    st.write(video_data)

    def get_key(val):
        for key, value in video_data.items():
            if val == value:
                return key

    VIDEO_ID = get_key(video_select)
    st.write(VIDEO_ID)
    result = execute_api_request(
    youtube_analytics.reports().query,
    ids='channel==MINE',
    # ids='contentOwner==OWNER_NAME,',
    startDate=start_date,
    endDate=end_date,
    dimensions='elapsedVideoTimeRatio',
    metrics='audienceWatchRatio,relativeRetentionPerformance',
    filters=f'video=={VIDEO_ID};audienceType==ORGANIC'
    )

    # st.columns(2)
  except Exception as e:
    # print("エラーが発生しました")
    # print(e)
    traceback.print_exc()
    pass


