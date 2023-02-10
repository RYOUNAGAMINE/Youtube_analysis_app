import streamlit as st
import json
import os
import traceback

import channel_analytics as ca
import video_analytics as va
import search_analysis as sa
import my_function as mf

import oauthlib
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import googleapiclient


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES_ANALYTICS = ['https://www.googleapis.com/auth/yt-analytics.readonly']
API_SERVICE_NAME_ANALYTICS = 'youtubeAnalytics'
API_VERSION_ANALYTICS = 'v2'

SCOPES_YOUTUBE= ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME_YOUYUBE = 'youtube'
API_VERSION_YOUYUBE = 'v3'

with open('secret.json') as f:
    secret = json.load(f)
DEVELOPER_KEY = secret['KEY']
CLIENT_SECRETS_FILE = 'YOUR_CLIENT_SECRET_FILEwebapp.json'

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES_ANALYTICS)
flow.redirect_uri = 'http://localhost:8501'

authorization_url, state = flow.authorization_url(
    access_type='offline',
    login_hint='ryou110216@yahoo.co.jp',
    include_granted_scopes='true'
)

st.set_page_config(
    layout="wide"
)

st.title("Youtube分析ダッシュボード")

pages = [
    "チャンネルのアナリティクス",
    "動画のアナリティクス",
    "競合動画のリサーチ"
]
st.sidebar.title('メニュー')
selection_analytics = st.sidebar.radio("選択してください。", pages)
st.sidebar.button("リロード")


if 'code' in st.experimental_get_query_params() or  'credentials' in st.session_state:
    try:
        if  'credentials' in st.session_state:
            credentials = google.oauth2.credentials.Credentials(
        **st.session_state['credentials'])
            st.session_state['credentials']=mf.credentials_to_dict(credentials)

        else:
            authorization_response = st.experimental_get_query_params()['code']
            authorization_response=authorization_response[0]
            flow.fetch_token(code=authorization_response)
            credentials = flow.credentials
            st.session_state['credentials']=mf.credentials_to_dict(credentials)
            st.balloons()

        youtube_analytics = build(API_SERVICE_NAME_ANALYTICS, API_VERSION_ANALYTICS, credentials = credentials,cache_discovery=False)
        youtube = build(API_SERVICE_NAME_YOUYUBE, API_VERSION_YOUYUBE,  developerKey=DEVELOPER_KEY)

        if selection_analytics =="チャンネルのアナリティクス" or selection_analytics =="動画のアナリティクス":
            period = st.selectbox('期間を指定してください。',('過去7日間','過去30日間','過去180日間','過去360日間','全期間','カスタム'))
            periods = mf.time_select(period)
            start_date = periods[0]
            end_date = periods[1]

        if selection_analytics == "チャンネルのアナリティクス":
            ca.app_channel(youtube_analytics,start_date,end_date,period)
        elif selection_analytics == "動画のアナリティクス":
            va.app_video(youtube_analytics,youtube,start_date,end_date,period)
        elif selection_analytics == "競合動画のリサーチ":
            sa.app_search(youtube)

    except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:#リロードによる認証の無効に対するエラー処理
        st.write(mf.get_login_str(authorization_url),unsafe_allow_html=True)
        st.write("リンクから認証を行ってください。")
        print("リンクから認証を行ってください。1")
        traceback.print_exc()

    except google.auth.exceptions.RefreshError:#アクセストークンの有効期限が切れたときのエラー処理
        st.write(mf.get_login_str(authorization_url),unsafe_allow_html=True)
        st.write("リンクから認証を行ってください。")
        traceback.print_exc()
        print("リンクから認証を行ってください。2")

    except googleapiclient.errors.HttpError:
        traceback.print_exc()
        st.write("APIクォータの消費量が最大値を超えたか、APIのリクエストに問題が発生しました。")

    except Exception as e:
        traceback.print_exc()
        st.write("エラーが発生しました。")
        st.write(e)
        pass

    else:
        print ('正常に処理が完了しました')

else:
    st.write(mf.get_login_str(authorization_url),unsafe_allow_html=True)
    st.write("リンクから認証を行ってください。")