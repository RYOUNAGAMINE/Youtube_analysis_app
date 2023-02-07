import app as ap
import plotly.express as px
import re
import datetime
import streamlit as st
import my_function as mf

def ids_titles_function(youtube_analytics,start_date,youtube,max_results=50):
    video_analysis = ap.execute_api_request(
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
    response = response['items']
    for item in response:
        video_title=item['snippet']['title']
        video_titles.append(video_title)



    ids_titles = {}
    for i in range(len(video_titles)):
        ids_titles[f'{video_ids[i]}'] = video_titles[i]

    return ids_titles,video_titles


def channel_basis_reports(youtube_analytics,start_date,end_date,video_id):
    channel_analytics = ap.execute_api_request(
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
    video_report_graph = ap.execute_api_request(
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
    result = ap.execute_api_request(
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
    age_gender = ap.execute_api_request(
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

# def title_session():


def app_video(youtube_analytics,youtube,start_date,end_date,period):
    ids_titles_list = ids_titles_function(youtube_analytics,start_date,youtube)
    video_ids_titles = ids_titles_list[0]
    video_titles = ids_titles_list[1]

    video_select_title = st.selectbox(label="動画を選択してください。",
        options=video_titles)


    video_id = mf.get_key(video_select_title,video_ids_titles)
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
    col1, col2, col3= st.columns(3)
    with col1:
        st.plotly_chart(video_view, use_container_width=True)
    with col2:
        st.plotly_chart(video_watch_hour, use_container_width=True)
    with col3:
        st.plotly_chart(video_subscriber, use_container_width=True)





    fulltime_second = time_minute(youtube,video_id)
    viewing_data = viewing_function(youtube_analytics,start_date,end_date,video_id,fulltime_second)

    viewing_graph = viewing_data[0]
    st.write("平均視聴率 : " + str(viewing_data[1]) +"%")
    st.write("平均視聴時間 : " + str(viewing_data[2]))
    st.plotly_chart(viewing_graph, use_container_width=True)

    video_age_gender_graph= age_gender_graph_video(youtube_analytics,start_date,end_date,video_id)
    st.write(video_age_gender_graph)
