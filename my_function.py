import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta


def get_login_str(authorization_url):
    return f'<a target="_self" href="{authorization_url}">Google login</a>'


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


def time_select(period):
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


def get_key(val,id_title):
    for key, value in id_title.items():
        if val == value:
            return key


def country_name(code):
    country_code_dictionary = {
        'JP' : '日本',
        'TW' : '台湾',
        'HK' : '香港',
        'US' : 'アメリカ',
        'TH' : 'タイ',
        'MX' : 'メキシコ',
        'ID' : 'インドネシア'
    }

    for key, value in country_code_dictionary.items():
        if code == key:
            return value
    return('不明な国')


def device_name(device_code):
    device_code_dictionary = {
        'DESKTOP' : 'パソコン',
        'GAME_CONSOLE' : 'ゲームコンソール',
        'MOBILE' : '携帯',
        'TABLET' : 'タブレット',
        'TV' : 'テレビ',
        'UNKNOWN_PLATFORM' : '不明なデバイス'
    }

    for key, value in device_code_dictionary.items():
        if device_code == key:
            return value


def traffic_name(traffic_source_code):
    traffic_source_code_dictionary = {
        'NO_LINK_OTHER' : '	直接or不明',
        'SUBSCRIBER' : 'ブラウジング機能',
        'YT_CHANNEL' : 'チャンネルページ',
        'YT_SEARCH' : '	YouTube内検索',
        'RELATED_VIDEO' : '	関連動画',
        'YT_OTHER_PAGE' : 'その他のYouTube',
        'EXT_URL' : '外部サイト',
        'ANNOTATION' : 'アノテーション',
        'PLAYLIST' : '再生リスト',
        'NOTIFICATION' : 'Youtube通知',
        'YT_PLAYLIST_PAGE' : '再生リストページ',
        'END_SCREEN' : '別動画の終了画面',
        'HASHTAGS' : 'ハッシュタグ',
    }

    for key, value in traffic_source_code_dictionary.items():
        if traffic_source_code == key:
            return value
    return 'その他'



