![](https://img.shields.io/github/repo-size/RYOUNAGAMINE/Youtube_analysis_app)
[![](https://img.shields.io/badge/YouTube-DataAPI-red)](https://developers.google.com/youtube/v3)
[![](https://img.shields.io/badge/YouTube-AnalyticsAPI-red)](https://developers.google.com/youtube/analytics)
![](https://img.shields.io/github/languages/top/RYOUNAGAMINE/Youtube_analysis_app)
![](https://img.shields.io/github/languages/count/RYOUNAGAMINE/Youtube_analysis_app)
![](https://img.shields.io/github/stars/RYOUNAGAMINE/Youtube_analysis_app?style=social)
# Youtube_analysis_app
自身のYoutubeチャンネルや動画を分析する

## 目次
- [Youtube\_analysis\_app](#youtube_analysis_app)
  - [目次](#目次)
  - [デモ](#デモ)
  - [機能](#機能)
  - [使い方](#使い方)
  - [環境](#環境)
  - [文責](#文責)
  - [ライセンス](#ライセンス)
  - [参考文献](#参考文献)

## デモ
![demo](https://user-images.githubusercontent.com/103870534/220037587-5e03ae9a-5da3-4e12-85c0-bda259783ea1.gif)

## 機能
- *自身のユーチューブチャンネルアナリティクス分析*
    - 分析する期間の指定機能
    - 分析できるアナリティクス
        <details>
        <summary>表示</summary>

        - 基本的なアナリティクス
            - 視聴回数
            - 視聴回数
            - 視聴時間
            - 高評価
            - 低評価
            - コメント
            - 共有回数
            - 登録回数
        - 日ごとの時系列アナリティクス(折れ線グラフ)
            - 視聴回数
            - 視聴時間
            - 登録者数
        - 性別年齢別のアナリティクス(円グラフ)
        - 再生場所の詳細アナリティクス
        - 国別のアナリティクス
        - 再生デバイスごとのアナリティクス
        - 検索ワード別の再生回数
        </details>
- *自身のアップロードした動画のアナリティクス分析*
    - 分析する期間の指定機能
    - 分析する動画の選択機能
    - 選択したビデオ再生機能
    - 分析できるアナリティクス
        <details>
        <summary>表示</summary>

        - 基本的なアナリティクス
            - 視聴回数
            - 視聴回数
            - 視聴時間
            - 高評価
            - 低評価
            - コメント
            - 共有回数
            - 登録回数
        - 日ごとの時系列アナリティクス(折れ線グラフ)
            - 視聴回数
            - 視聴時間
            - 登録者数
        - 視聴維持率(折れ線グラフ)
        - 性別年齢別のアナリティクス(円グラフ)
        - 再生場所の詳細アナリティクス
        - 検索ワード別の再生回数
        </details>
- *競合動画の分析*
    - 検索ワード指定による動画検索機能
    - 検索する動画のチャンネル登録者数の閾値設定機能
    - 動画を選択して再生する機能
    - 分析できるアナリティクス
        <details>
        <summary>表示</summary>

        - アップロード日
        - 視聴回数
        - 高評価
        - コメント数
        - チャンネル名
        - チャンネル登録者数
        </details>

## 使い方
最初にリポジトリをクローンしてください。
```bash
git clone https://github.com/RYOUNAGAMINE/Youtube_analysis_app.git
```

クローンしたリポジトリに移動してください。
```bash
cd Youtube_analysis_app
```


以下のコードを実行し、必要なパッケージをインストールします。
```bash
pip install -r requirements.txt
```



GoogleCloudPlatformのコンソール画面にて、YouTube Data API v3を有効化しAPIキーを取得します。
詳細についてはこちら[「YouTubeDataAPIの有効化とAPIキーを取得する。」](https://qiita.com/ryou110216/items/181296d7eaf83d405754)を参照してください。
取得したAPIキーはクローンしたリポジトリに"secret.json"として保存します。
```json:secret.json
{
    "KEY": "取得したAPIキーを入力"
}
```
GoogleCloudPlatformのコンソール画面にて、YouTube Analytics API を有効化しOAuthクライアントを作成します。
詳細についてはこちら[「YouTubeAnalyticsAPIの有効化とOAuthクライアントを作成する。」](https://qiita.com/ryou110216/items/73df6f8e6764549edf0b)を参照してください。
ダウンロードしたOAuthクライアントの認証情報を、クローンしたリポジトリに"YOUR_CLIENT_SECRET_FILEwebapp.json"として保存する。



ターミナルで以下のコマンドを実行するとローカルで、アプリを起動できます。
```bash
streamlit run app.py
```
## 環境
- Windows
- Python 3.10.7


## 文責
- 作成者:長嶺亮
- Email:ryou110216@yahoo.co.jp

## ライセンス
[![](https://img.shields.io/github/license/RYOUNAGAMINE/Youtube_analysis_app)](LICENSE)

## 参考文献
以下の情報を参考にしました。
- [YouTube Data API 公式ドキュメント](https://developers.google.com/youtube/v3)
- [YouTube Analytics and Reporting APIs 公式ドキュメント](https://developers.google.com/youtube/analytics)
