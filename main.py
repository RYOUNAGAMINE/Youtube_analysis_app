# import pandas as pd
# import os
# import streamlit as st
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
import streamlit as st
import os
import json
import httplib2#
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.tools import run_flow#
from oauth2client.client import flow_from_clientsecrets#
from oauth2client.file import Storage#

SCOPES_ANALYTICS = ['https://www.googleapis.com/auth/yt-analytics.readonly']
API_SERVICE_NAME_ANALYTICS = 'youtubeAnalytics'
API_VERSION_ANALYTICS = 'v2'


SCOPES_YOUTUBE= ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME_YOUYUBE = 'youtube'
API_VERSION_YOUYUBE = 'v3'

CLIENT_SECRETS_FILE = 'YOUR_CLIENT_SECRET_FILE.json'




def get_service(scopes,api_service_name, api_version):
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes)
  credentials = flow.run_console()
  return build(api_service_name, api_version, credentials = credentials,cache_discovery=False)#file_cache is only supported with oauth2client<4.0.0が出るためcache_discovery=Falseを追加

def execute_api_request(client_library_function, **kwargs):
  response = client_library_function(
    **kwargs
  ).execute()

  return response

if __name__ == '__main__':

  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  youtubeAnalytics = get_service(SCOPES_ANALYTICS,API_SERVICE_NAME_ANALYTICS,API_VERSION_ANALYTICS)
  youtube = get_service(SCOPES_YOUTUBE,API_SERVICE_NAME_YOUYUBE,API_VERSION_YOUYUBE)

st.title('My YouTube アナリティクスダッシュボード')

