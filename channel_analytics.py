import app as ap
import pandas as pd
import plotly.express as px
import streamlit as st
import datetime
import my_function as mf

def channel_basis_reports(youtube_analytics,start_date,end_date):
    channel_analytics = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched,likes,dislikes,comments,shares,subscribersGained',
        dimensions='channel',
    )
    channel_basis_data = channel_analytics['rows'][0]


    channel_basis_data.pop(0)
    channel_basis_data = pd.Series(channel_basis_data, index=['視聴回数','視聴時間(時間)','高評価','低評価','コメント','シェア','チャンネル登録回数'])
    return channel_basis_data

def age_gender_graph(youtube_analytics,start_date,end_date):
    age_gender = mf.execute_api_request(
    youtube_analytics.reports().query,
    ids='channel==MINE',
    startDate=start_date,
    endDate=end_date,
    dimensions='ageGroup,gender',
    metrics='viewerPercentage',
    sort='gender,ageGroup'
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

def channel_basis_graph(youtube_analytics,start_date,end_date):
    Channel_report_response = mf.execute_api_request(
    youtube_analytics.reports().query,
    ids='channel==MINE',
    startDate=start_date,
    endDate=end_date,
    dimensions='day',
    metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained' ,#視聴回数,視聴分数,平均視聴時間(秒),動画の平均維持率,チャンネル登録数
    sort='day'
    )
    Channel_report_response = Channel_report_response['rows']
    Channel_report = {}
    day = []
    view = []
    watch_hour = []
    subscriber = []
    total_day = 0
    for i in range(len(Channel_report_response)):
        hour = Channel_report_response[i][2] / 60
        total_day += 1
        day.append(Channel_report_response[i][0])
        view.append(Channel_report_response[i][1])
        watch_hour.append(hour)
        subscriber.append(Channel_report_response[i][5])

    Channel_report['day'] = day
    Channel_report['view'] = view
    Channel_report['watch_hour'] = watch_hour
    Channel_report['subscriber'] = subscriber

    total_microsecond = 1000*60*60*24*total_day
    interval_day = total_microsecond / 5

    fig_view = px.line(Channel_report, x = 'day',y='view')
    fig_watch_hour = px.line(Channel_report, x = 'day',y='watch_hour')
    fig_subscriber = px.line(Channel_report, x = 'day',y='subscriber')

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

def country_analysis(youtube_analytics,start_date,end_date):
    result = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='country',
        metrics='views,estimatedMinutesWatched,averageViewDuration',
        sort='-estimatedMinutesWatched'
    )

    result = result['rows']
    country_list = []
    view_list = []
    watch_minute_list = []
    average_watch_time_list = []


    for i in range(len(result)):
        country_list.append(mf.country_name(result[i][0]))
        view_list.append(result[i][1])
        watch_minute_list.append(round(result[i][2] / 60,1))
        average_time = str(datetime.timedelta(seconds=result[i][3]))
        average_watch_time_list.append(average_time)



    df_country = pd.DataFrame(
        data = {'国名' : country_list,
            '視聴回数' : view_list,
            '視聴時間(時間)' : watch_minute_list,
            '平均視聴時間': average_watch_time_list
        }
    )
    df_country = df_country.style.format(formatter={('視聴時間(時間)'): "{:.1f}"})
    return df_country

def device_analysis(youtube_analytics,start_date,end_date):
    device_type_response = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='deviceType',
        metrics='views',
        # sort='-shares'
    )
    device_type_response = device_type_response['rows']
    device_name = []
    device_views = []
    for i in range(len(device_type_response)):
        device_name.append(mf.device_name(device_type_response[i][0]))
        device_views.append(device_type_response[i][1])
    df_device_type = pd.DataFrame(
        data = {'デバイス名' : device_name,
            '視聴回数' : device_views
        }
    )
    return df_device_type

def traffic_source_analysis(youtube_analytics,start_date,end_date):
    traffic_source_type_response = mf.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='insightTrafficSourceType',
        metrics='views',
        sort='-views'
    )
    traffic_source_type_response = traffic_source_type_response['rows']
    traffic_source_name = []
    traffic_source_views = []
    for i in range(len(traffic_source_type_response)):
        traffic_source_name.append(mf.traffic_name(traffic_source_type_response[i][0]))
        traffic_source_views.append(traffic_source_type_response[i][1])   

    df_traffic_source_type = pd.DataFrame(
    data = {'トラフィックソース名' : traffic_source_name,
            '視聴回数' : traffic_source_views
    })
    return df_traffic_source_type

def app_channel(youtube_analytics,start_date,end_date,period):

    channel_basis_data = channel_basis_reports(youtube_analytics,start_date,end_date)

    if period == 'カスタム':
        st.markdown('## 選択した期間中')
    else:
        st.markdown(f'## {period}の期間中')

    video_views = channel_basis_data[0]
    video_hourWatched = round(channel_basis_data[1] / 60,1)
    video_likes = channel_basis_data[2]
    video_dislikes = channel_basis_data[3]
    video_comments = channel_basis_data[4]
    video_shares = channel_basis_data[5]
    video_subscriber = channel_basis_data[6]

    st.markdown(f'###### 視聴回数  :  {video_views}回')
    st.markdown(f'###### 視聴時間  :  {video_hourWatched}時間')
    st.markdown(f'###### 高評価    : {video_likes}個')
    st.markdown(f'###### 低評価    : {video_dislikes}個')
    st.markdown(f'###### コメント  : {video_comments}個')
    st.markdown(f'###### 共有      : {video_shares}回')
    st.markdown(f'###### 登録者数  : {video_subscriber}人')


    channel_basis_graphs=channel_basis_graph(youtube_analytics,start_date,end_date)

    channel_view = channel_basis_graphs[0]
    channel_watch_hour = channel_basis_graphs[1]

    col1, col2= st.columns(2)
    with col1:
        st.plotly_chart(channel_view, use_container_width=True)
    with col2:
        st.plotly_chart(channel_watch_hour, use_container_width=True)


    channel_subscriber = channel_basis_graphs[2]
    channel_age_gender_graph = age_gender_graph(youtube_analytics,start_date,end_date)

    col1, col2= st.columns(2)
    with col1:
        st.plotly_chart(channel_subscriber, use_container_width=True)
    with col2:
        st.plotly_chart(channel_age_gender_graph, use_container_width=True)


    df_country = country_analysis(youtube_analytics,start_date,end_date)
    df_device = device_analysis(youtube_analytics,start_date,end_date)
    df_traffic_source = traffic_source_analysis(youtube_analytics,start_date,end_date)
    
    col1, col2,col3= st.columns(3)
    with col1:
        st.dataframe(df_country)
    with col2:
        st.dataframe(df_device)
    with col3:
        st.dataframe(df_traffic_source)
