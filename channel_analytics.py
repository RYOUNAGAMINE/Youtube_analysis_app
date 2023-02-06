import app as ap
import pandas as pd
import plotly.express as px
import streamlit as st

def channel_basis_reports(youtube_analytics,start_date,end_date):
    channel_analytics = ap.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched,likes,dislikes,comments,shares,subscribersGained',
        dimensions='channel',
    )
    channel_basis_data = channel_analytics['rows'][0]


    channel_basis_data.pop(0)
    channel_basis_data = pd.Series(channel_basis_data, index=['視聴回数','視聴時間(分)','いいね','バッド','コメント','シェア','チャンネル登録回数'])
    return channel_basis_data

def age_gender_graph(youtube_analytics,start_date,end_date):
    age_gender = ap.execute_api_request(
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
    Channel_report_response = ap.execute_api_request(
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

def app_channel(youtube_analytics,start_date,end_date):

    channel_basis_data = channel_basis_reports(youtube_analytics,start_date,end_date)
    st.dataframe(channel_basis_data)

    channel_basis_graphs=channel_basis_graph(youtube_analytics,start_date,end_date)
    channel_view = channel_basis_graphs[0]
    channel_watch_hour = channel_basis_graphs[1]
    channel_subscriber = channel_basis_graphs[2]

    col1, col2, col3= st.columns(3)
    with col1:
        st.plotly_chart(channel_view, use_container_width=True)
    with col2:
        st.plotly_chart(channel_watch_hour, use_container_width=True)
    with col3:
        st.plotly_chart(channel_subscriber, use_container_width=True)

    channel_age_gender_graph = age_gender_graph(youtube_analytics,start_date,end_date)
    st.plotly_chart(channel_age_gender_graph, use_container_width=True)