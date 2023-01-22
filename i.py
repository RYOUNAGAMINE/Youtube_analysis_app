import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import asyncio
import streamlit as st
import os

SCOPES_ANALYTICS = ['https://www.googleapis.com/auth/yt-analytics.readonly']
API_SERVICE_NAME_ANALYTICS = 'youtubeAnalytics'
API_VERSION_ANALYTICS = 'v2'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES_YOUTUBE= ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME_YOUYUBE = 'youtube'
API_VERSION_YOUYUBE = 'v3'

CLIENT_SECRETS_FILE = 'YOUR_CLIENT_SECRET_FILE.json'

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES_ANALYTICS)
flow.redirect_uri = 'http://localhost:8501'
authorization_url, state = flow.authorization_url(
  access_type='offline',
  # state=sample_passthrough_value,
  login_hint='ryou110216@yahoo.co.jp',
  include_granted_scopes='true')

def get_login_str():

  return f'''
  <a target="_self"
  href="{authorization_url}">Google login</a>'''

st.write(get_login_str(),unsafe_allow_html=True)
# authorization_state = st.experimental_get_query_params()['state']
# state = authorization_state[0]
# authorization_code = st.experimental_get_query_params()['code']
# code = authorization_code[0]
# authorization_scope = st.experimental_get_query_params()['scope']
# scope = authorization_code[0]
# authorization_response = "localhost:8501/?state="+state+"&code="+code+"&scope="+scope
if 'code' in st.experimental_get_query_params():
  authorization_response = st.experimental_get_query_params()['code']
  authorization_response=authorization_response[0]


  flow.fetch_token(code=authorization_response)
  credentials = flow.credentials

  youtube = build(API_SERVICE_NAME_ANALYTICS, API_VERSION_ANALYTICS, credentials = credentials,cache_discovery=False)



  # state = flask.session['state']



  # credentials = flow.credentials
  # flask.session['credentials'] = {
  #     'token': credentials.token,
  #     'refresh_token': credentials.refresh_token,
  #     'token_uri': credentials.token_uri,
  #     'client_id': credentials.client_id,
  #     'client_secret': credentials.client_secret,
  #     'scopes': credentials.scopes}

  def execute_api_request(client_library_function, **kwargs):
    response = client_library_function(
      **kwargs
    ).execute()

    return response

  channel_analytics = execute_api_request(
        youtube.reports().query,
        ids='channel==MINE',
        startDate='2020-01-26',
        endDate='2022-07-31',
        metrics='views,estimatedMinutesWatched,likes,dislikes,comments,shares,subscribersGained',
        dimensions='channel',
    )
  penny = channel_analytics['rows'][0]
  st.write(penny)