import app as ap

def channel_basis_reports():
    channel_analytics = ap.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched,likes,dislikes,comments,shares,subscribersGained',
        dimensions='video',
        filters=f'video=={VIDEO_ID}'
    )
    video_basis_data = channel_analytics['rows'][0]
    video_basis_data.pop(0)
    return video_basis_data

def video_graph_function():
    video_report_graph = ap.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='day',
        metrics='views,estimatedMinutesWatched,subscribersGained',
        filters=f'video=={VIDEO_ID}'
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

def time_minute():
    video_data = youtube.videos().list(
    part="contentDetails",
    id =f'{VIDEO_ID}'
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



def viewing_function(fulltime):
    result = ap.execute_api_request(
        youtube_analytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        dimensions='elapsedVideoTimeRatio',
        metrics='audienceWatchRatio,relativeRetentionPerformance',
        filters=f'video=={VIDEO_ID};audienceType==ORGANIC'
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