import streamlit as st
import pandas as pd
import my_function as mf

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
        if len(items_id) <= 49:#video_searchでmax_resultsを50にしても51個のデータを取ってくることがあるため
            items_id.append(item_id)
    df_video_channel_ids = pd.DataFrame(items_id)

    return df_video_channel_ids

def get_results(df_video,youtube,limiter):
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
    fields='items(id,snippet(title,publishedAt),statistics(viewCount,likeCount,commentCount))'
    ).execute()

    videos_info = []

    items = videos_list['items']
    for item in items:
        video_info = {}
        video_info['video_id'] = item['id']
        video_info['動画のタイトル'] = item['snippet']['title']
        video_info['アップロード日'] = item['snippet']['publishedAt'][:10]
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
        search_video_ids = df_videos_info['video_id'].tolist()
        search_video_titles = df_videos_info['動画のタイトル'].tolist()
        search_ids_titles = {}
        for i in range(len(search_video_titles)):
            search_ids_titles[f'{search_video_ids[i]}'] = search_video_titles[i]

        results = pd.merge(left=df_extracted, right=df_videos_info, on='video_id')
        results = results.drop(['video_id', 'channel_id'], axis=1)
        #     カラム並び替え
        results = results.loc[:, ['動画のタイトル', 'アップロード日','視聴回数', '高評価','コメント数','チャンネル名','チャンネル登録数']]
    elif len(videos_info) == 0:
        results = ""
        search_video_titles = ""
        search_ids_titles = ""

    return results, search_video_titles,search_ids_titles

def app_search(youtube):
    st.sidebar.write("""## 検索ワードと登録者数上限の設定""")
    st.sidebar.write("""### 検索ワードの入力""")
    query = st.sidebar.text_input('検索ワードを入力してください。', '沖縄 フカセ釣り')
    if 'query'  not in st.session_state:
        st.session_state['query'] = query

    st.sidebar.write("""### 登録者数上限の設定""")
    limiter = st.sidebar.slider("登録者数の閾値", 100, 1300000, 1000)
    if 'limiter'  not in st.session_state:
        st.session_state['limiter'] = limiter


    st.markdown('### 選択中のパラメータ')
    st.markdown(f"""
    - 検索ワード: {query}
    - 登録者数の閾値: {limiter}
    """)

    if 'results'  not in st.session_state or st.session_state['query'] != query or st.session_state['limiter'] != limiter:
        df_search_video_channel_ids = video_search(youtube, q=query, max_results=50)
        results = get_results(df_search_video_channel_ids,youtube, limiter=limiter)
        df_search_analysis = results[0]
        search_video_titles = results[1]
        search_ids_titles = results[2]
        st.session_state['results'] = results
    else:
        selectbox_video_titles = st.session_state['video_titles']
        df_search_analysis = st.session_state['results'][0]
        search_video_titles = st.session_state['results'][1]
        search_ids_titles = st.session_state['results'][2]

    st.write("### 検索結果")
    if len(st.session_state['results'][1]) > 0:
        selectbox_video_titles = []

        if 'video_titles'  not in st.session_state or st.session_state['query'] != query or st.session_state['limiter'] != limiter:
            for i in range(len(search_video_titles)):
                selectbox_video_title = f'{i}:{search_video_titles[i]}'
                selectbox_video_titles.append(selectbox_video_title)
            st.session_state['limiter'] = limiter
            st.session_state['query'] = query
            st.session_state['video_titles'] = selectbox_video_titles
        else:
            selectbox_video_titles = st.session_state['video_titles']

        st.dataframe(df_search_analysis)
        select_video_title = st.selectbox(label="動画を選択してください。",
        options=selectbox_video_titles)

        target = ':'
        idx = select_video_title.find(target)
        video_select_title = select_video_title[idx+1:]
        video_id = mf.get_key(video_select_title,search_ids_titles)

        video_field = st.empty()
        url = f'https://youtu.be/{video_id}'
        video_field.video(url)

        video_field.write('こちらに動画が表示されます')

        if st.button('ビデオを表示する'):
                video_field.video(url)

    else:
        st.write("登録者数上限以下の動画が見つかりませんでした。登録者数の上限を変更してください。")

