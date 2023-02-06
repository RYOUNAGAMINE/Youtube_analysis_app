import streamlit as st
import pandas as pd
import app as ap
def video_search(youtube, q = "沖縄 フカセ釣り", max_results=50):
    response = youtube.search().list(
    q=q,
    part="snippet",
    order='viewCount',
    type='video',
    maxResults=max_results,
    ).execute()

    items_id = []
    items = response['items']
    for item in items:
        item_id = {}
        item_id['video_id'] = item['id']['videoId']
        item_id['channel_id'] = item['snippet']['channelId']
        items_id.append(item_id)
    df_video = pd.DataFrame(items_id)

    return df_video

def get_results(df_video,youtube,limiter):

    # channel_ids = df_video['channel_id'].unique().tolist()
    channel_ids = df_video['channel_id'].tolist()


    subscriber_list = youtube.channels().list(
    id=','.join(channel_ids),
    part='snippet,statistics',
    fields = 'items(id,statistics(subscriberCount),snippet(title))'
    ).execute()

    subscribers = []
    for item in subscriber_list['items']:
        subscriber = {}
        subscriber['channel_id'] = item['id']
        subscriber['チャンネル名'] = item['snippet']['title']
        if len(item['statistics']) > 0:#登録者数が隠されている時の処理
            subscriber['チャンネル登録数'] = int(item['statistics']['subscriberCount'])
        else:
            subscriber['チャンネル登録数'] = ""
        subscribers.append(subscriber)

    df_subscribers = pd.DataFrame(subscribers)

    df = pd.merge(left=df_video, right=df_subscribers, on='channel_id')
    df_extracted = df[df['チャンネル登録数'] < limiter]

    video_ids = df_extracted['video_id'].tolist()
    #video_idsが全体のid
    videos_list = youtube.videos().list(
    part='snippet,statistics',
    id=','.join(video_ids),
    fields='items(id,snippet(title),statistics(viewCount,likeCount,commentCount))'
    ).execute()

    videos_info = []

    items = videos_list['items']
    for item in items:
        video_info = {}
        video_info['video_id'] = item['id']
        video_info['動画のタイトル'] = item['snippet']['title']
        video_info['視聴回数'] = item['statistics']['viewCount']
        if 'likeCount' in item['statistics'].keys():#高評価が隠されていた時の処理
            video_info['高評価'] = item['statistics']['likeCount']
        else:
            video_info['高評価'] =""
        if 'commentCount' in item['statistics'].keys():#コメントが隠されていた時の処理
            video_info['コメント数'] = item['statistics']['commentCount']
        else:
            video_info['コメント数'] = ""
        videos_info.append(video_info)
    
    df_videos_info = pd.DataFrame(videos_info)
    if len(videos_info) > 0:
        serch_video_ids = df_videos_info['video_id'].tolist()
        serch_video_titles = df_videos_info['動画のタイトル'].tolist()
        serch_ids_titles = {}
        for i in range(len(serch_video_titles)):
            serch_ids_titles[f'{serch_video_ids[i]}'] = serch_video_titles[i]

        results = pd.merge(left=df_extracted, right=df_videos_info, on='video_id')
        results = results.drop(['video_id', 'channel_id'], axis=1)
        #     カラム並び替え
        results = results.loc[:, ['動画のタイトル', '視聴回数', '高評価','コメント数','チャンネル名','チャンネル登録数']]
    elif len(videos_info) == 0:
        results = ""
        serch_video_titles = ""
        serch_ids_titles = ""

    return results, serch_video_titles,serch_ids_titles

def get_key(val,id_title):
    for key, value in id_title.items():
        if val == value:
            return key






def app_search(youtube):
    st.sidebar.write("""## 検索ワードと登録者数上限の設定""")
    st.sidebar.write("""### 検索ワードの入力""")
    query = st.sidebar.text_input('検索ワードを入力してください。', '沖縄 フカセ釣り')

    st.sidebar.write("""### 登録者数上限の設定""")
    limiter = st.sidebar.slider("登録者数の閾値", 100, 1000000, 1000)

    st.markdown('### 選択中のパラメータ')
    st.markdown(f"""
    - 検索ワード: {query}
    - 登録者数の閾値: {limiter}
    """)

    df_video = video_search(youtube, q=query, max_results=50)
    results = get_results(df_video,youtube, limiter=limiter)[0]
    serch_video_titles = get_results(df_video,youtube, limiter=limiter)[1]
    serch_ids_titles = get_results(df_video,youtube, limiter=limiter)[2]
    st.write("### 分析結果")
    st.write("### 動画再生")
    if len(serch_video_titles) > 0:
        st.dataframe(results)
        selectbox_video_titles = []
        for i in range(len(serch_video_titles)):
            selectbox_video_title = f'{i}:{serch_video_titles[i]}' 
            selectbox_video_titles.append(selectbox_video_title)

        select_video_title = st.selectbox(label="動画を選択してください。",
        options=selectbox_video_titles)
        
        target = ':'
        idx = select_video_title.find(target)
        video_select_title = select_video_title[idx+1:]
        
        video_id = get_key(video_select_title,serch_ids_titles)
        video_field = st.empty()
        url = f'https://youtu.be/{video_id}'
        video_field.video(url)

        video_field.write('こちらに動画が表示されます')

        if st.button('ビデオ表示'):
            try:
                video_field.video(url)
            except:
                st.write("エラーが発生しました。")
    elif results == "":
        st.write("登録者数上限以下の動画が見つかりませんでした。登録者数の上限を変更してください。")

