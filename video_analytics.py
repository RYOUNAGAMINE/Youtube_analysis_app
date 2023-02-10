import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import re
import app as ap
import my_function as mf

def ids_titles_function(youtube_analytics,start_date,youtube,max_results=50):
    video_analysis = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=datetime.date(2020,4,26),
        endDate=datetime.date.today(),
        metrics='estimatedMinutesWatched,views,likes,subscribersGained',
        dimensions='video',
        sort='-estimatedMinutesWatched',
        maxResults=max_results
    )
    rows = video_analysis['rows']

    video_ids = []
    for row in rows:
        video_id = row[0]
        video_ids.append(video_id)

    response = youtube.videos().list(
    part="snippet",
    id =video_ids
    ).execute()
    video_titles=[]
    upload_dates = []
    response = response['items']
    for item in response:
        video_title=item['snippet']['title']
        upload_date = item['snippet']['publishedAt'][:10]
        video_titles.append(video_title)
        upload_dates.append(upload_date)

    ids_titles = {}
    ids_upload_dates = {}
    for i in range(len(video_titles)):
        ids_titles[f'{video_ids[i]}'] = video_titles[i]
        ids_upload_dates[f'{video_ids[i]}'] = upload_dates[i]

    return ids_titles,video_titles,ids_upload_dates


def channel_basis_reports(youtube_analytics,start_date,end_date,video_id):
    channel_analytics = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched,likes,dislikes,comments,shares,subscribersGained',
        dimensions='video',
        filters=f'video=={video_id}'
    )
    video_basis_data = channel_analytics['rows'][0]
    video_basis_data.pop(0)

    return video_basis_data


def video_graph_function(youtube_analytics,start_date,end_date,video_id):
    video_report_graph = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='day',
        metrics='views,estimatedMinutesWatched,subscribersGained',
        filters=f'video=={video_id}'
    )
    video_report_graph = video_report_graph['rows']

    Video_report = {}
    day = []
    view = []
    watch_hour = []
    subscriber = []
    total_day = 0

    for i in range(len(video_report_graph)):
        hour = video_report_graph[i][2] / 60
        total_day += 1
        day.append(video_report_graph[i][0])
        view.append(video_report_graph[i][1])
        watch_hour.append(hour)
        subscriber.append(video_report_graph[i][3])

    Video_report['day'] = day
    Video_report['view'] = view
    Video_report['watch_hour'] = watch_hour
    Video_report['subscriber'] = subscriber

    total_microsecond = 1000*60*60*24*total_day
    interval_day = total_microsecond / 5

    fig_view = px.line(Video_report, x = 'day',y='view')
    fig_watch_hour = px.line(Video_report, x = 'day',y='watch_hour')
    fig_subscriber = px.line(Video_report, x = 'day',y='subscriber')

    fig_view.update_layout(title='視聴回数',
        width=1000,
        height=500)
    fig_view.update_xaxes(tickformat='%Y/%m/%d',dtick=interval_day)

    fig_watch_hour.update_layout(title='視聴時間(時間)',
        width=1000,
        height=500)
    fig_watch_hour.update_xaxes(tickformat='%Y/%m/%d',dtick=interval_day)

    fig_subscriber.update_layout(title='チャンネル登録者数',
        width=1000,
        height=500)
    fig_subscriber.update_xaxes(tickformat='%Y/%m/%d',dtick=interval_day)

    return fig_view,fig_watch_hour,fig_subscriber


def time_minute(youtube,video_id):
    video_data = youtube.videos().list(
    part="contentDetails",
    id =f'{video_id}'
    ).execute()
    video_time=video_data['items'][0]['contentDetails']['duration']

    m = r'PT(.*)M'
    s = r'M(.*)S'

    minute = re.findall(m, video_time)
    second = re.findall(s, video_time)

    if not second:
        second.append(0)
    if not minute:
        minute.append(0)

    minute = int(minute[0])
    second = int(second[0])

    minute_second = minute * 60
    fulltime_second = minute_second + second

    return fulltime_second


def viewing_function(youtube_analytics,start_date,end_date,video_id,fulltime):
    result = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='elapsedVideoTimeRatio',
        metrics='audienceWatchRatio,relativeRetentionPerformance',
        filters=f'video=={video_id};audienceType==ORGANIC'
    )

    timeRatio = {}
    time = []
    persentage = []
    average_persentage = 0

    for i in range(len(result['rows'])):
        videotime_second = result['rows'][i][0] * fulltime
        videotime_now = str(datetime.timedelta(seconds=int(videotime_second)))

        if videotime_now[:2] == '0:':
            videotime_now = videotime_now[2:]
        time.append(videotime_now)
        persentage.append(result['rows'][i][1]*100)
        average_persentage += result['rows'][i][1]

    average_persentage = int((average_persentage / len(persentage))*100)

    average_fullsecond =  int((average_persentage / 100) * fulltime)
    average_time= str(datetime.timedelta(seconds=average_fullsecond))

    if average_time[:2] == '0:':
        average_time = average_time[2:]

    timeRatio['time'] = time
    timeRatio['persentage'] = persentage

    fig = px.line(timeRatio, x = 'time',y='persentage')
    fig.update_layout(title='視聴者維持率',
                    width=1000,
                    height=500)

    interval_time = fulltime //100
    fig.update_xaxes(dtick=interval_time)#dtickは1ミリ秒単位で間隔を設定するがplotlyがTimeRatio['time']に入っている時間(間隔を設定する時間)を1秒当たり0.1ミリ秒と認識するため10等分に等しい100で割った値を間隔に設定する

    return fig,average_persentage,average_time


def age_gender_graph_video(youtube_analytics,start_date,end_date,video_id):
    age_gender = mf.execute_api_request(
    youtube_analytics.reports().query,
    ids='channel==MINE',
    startDate=start_date,
    endDate=end_date,
    dimensions='ageGroup,gender',
    metrics='viewerPercentage',
    sort='gender,ageGroup',
    filters=f'video=={video_id}'
    )
    age_gender = age_gender['rows']

    Character = ["男性","女性"]
    Parent = ["",""]
    Value = [0,0]

    for i in range(len(age_gender)):
        age_gender[i][0] = age_gender[i][0].replace('age', '')
        age_gender[i][0] += '歳'
        Character.append(age_gender[i][0])
        if age_gender[i][1] == 'female':
            age_gender[i][1] = '女性'
        elif age_gender[i][1] == 'male':
            age_gender[i][1] = '男性'
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

    return fig


def traffic_source_analysis(youtube_analytics,start_date,end_date,video_id):
    traffic_source_type_response = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='insightTrafficSourceType',
        metrics='views',
        sort='-views',
        filters=f'video=={video_id}'
    )
    traffic_source_type_response = traffic_source_type_response['rows']

    traffic_source_name = []
    traffic_source_views = []
    traffic_source_persenstages = []
    traffic_source_sum = 0
    for i in range(len(traffic_source_type_response)):
        traffic_source_sum += traffic_source_type_response[i][1]
    for i in range(len(traffic_source_type_response)):
        traffic_source_name.append(mf.traffic_name(traffic_source_type_response[i][0]))
        traffic_source_views.append(traffic_source_type_response[i][1])
        traffic_source_persenstage = round((int(traffic_source_type_response[i][1]) / traffic_source_sum)*100,1)
        traffic_source_persenstages.append(f'{traffic_source_persenstage}' + '%')

    df_traffic_source_type = pd.DataFrame(
    data = {'トラフィックソース名' : traffic_source_name,
        '視聴回数' : traffic_source_views,
        '' : traffic_source_persenstages
    })

    return df_traffic_source_type


def search_word_analysis(youtube_analytics,start_date,end_date,video_id):
    search_word_response = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='insightTrafficSourceDetail',
        metrics='views',
        filters=f'video=={video_id};insightTrafficSourceType==YT_SEARCH',
        # filters='insightTrafficSourceType==YT_SEARCH',
        maxResults=25,
        sort='-views'
    )
    search_word_response = search_word_response['rows']

    search_word_name = []
    search_word_views = []
    search_word_persenstages = []
    search_word_sum = 0
    for i in range(len(search_word_response)):
        search_word_sum += search_word_response[i][1]
    for i in range(len(search_word_response)):
        search_word_name.append(search_word_response[i][0])
        search_word_views.append(search_word_response[i][1])

        search_word_persenstage = round((int(search_word_response[i][1]) / search_word_sum)*100,1)
        search_word_persenstages.append(f'{search_word_persenstage}' + '%')

    df_search_word_response = pd.DataFrame(
    data = {'検索ワード' : search_word_name,
            '視聴回数' : search_word_views,
            '' : search_word_persenstages
        })

    return df_search_word_response


def app_video(youtube_analytics,youtube,start_date,end_date,period):

    ids_titles_list = ids_titles_function(youtube_analytics,start_date,youtube)
    video_ids_titles = ids_titles_list[0]
    video_titles = ids_titles_list[1]
    video_ids_uploaded_date = ids_titles_list[2]

    video_select_title = st.selectbox(label="動画を選択してください。",
        options=video_titles)

    video_id = mf.get_key(video_select_title,video_ids_titles)
    select_upload_date = video_ids_uploaded_date[video_id]

    video_field = st.empty()
    url = f'https://youtu.be/{video_id}'
    if st.button('ビデオを表示する'):
        video_field.video(url)

    video_basis_data = channel_basis_reports(youtube_analytics,start_date,end_date,video_id)
    video_views = video_basis_data[0]
    video_hourWatched = round(video_basis_data[1] / 60,1)
    video_likes = video_basis_data[2]
    video_dislikes = video_basis_data[3]
    video_comments = video_basis_data[4]
    video_shares = video_basis_data[5]
    video_subscriber = video_basis_data[6]

    if period == 'カスタム':
        st.markdown('## 選択した期間中')
    else:
        st.markdown(f'## {period}の期間中')

    st.markdown(f'##### アップロード日  :  {select_upload_date}')
    st.markdown(f'###### 視聴回数  :  {video_views}回')
    st.markdown(f'###### 視聴時間  :  {video_hourWatched}時間')
    st.markdown(f'###### 高評価    : {video_likes}個')
    st.markdown(f'###### 低評価    : {video_dislikes}個')
    st.markdown(f'###### コメント  : {video_comments}個')
    st.markdown(f'###### 共有      : {video_shares}回')
    st.markdown(f'###### 登録者数  : {video_subscriber}人')

    video_graphs  = video_graph_function(youtube_analytics,start_date,end_date,video_id)
    video_view = video_graphs[0]
    video_watch_hour = video_graphs[1]
    video_subscriber = video_graphs[2]

    graphs = [
    "視聴回数",
    "視聴時間",
    "登録者数"
    ]
    selection_graph = st.radio("表示したいグラフを選択してください。", graphs)

    if selection_graph == "視聴回数":
        st.plotly_chart(video_view, use_container_width=True)
    elif selection_graph == "視聴時間":
        st.plotly_chart(video_watch_hour, use_container_width=True)
    elif selection_graph == "登録者数":
        st.plotly_chart(video_subscriber, use_container_width=True)

    fulltime_second = time_minute(youtube,video_id)

    viewing_data = viewing_function(youtube_analytics,start_date,end_date,video_id,fulltime_second)
    st.write("平均視聴率 : " + str(viewing_data[1]) +"%")
    st.write("平均視聴時間 : " + str(viewing_data[2]))

    viewing_graph = viewing_data[0]
    st.plotly_chart(viewing_graph, use_container_width=True)

    video_age_gender_graph= age_gender_graph_video(youtube_analytics,start_date,end_date,video_id)
    st.write(video_age_gender_graph)

    df_video_traffic_source= traffic_source_analysis(youtube_analytics,start_date,end_date,video_id)
    st.dataframe(df_video_traffic_source)

    df_video_search_word  = search_word_analysis(youtube_analytics,start_date,end_date,video_id)
    st.dataframe(df_video_search_word)