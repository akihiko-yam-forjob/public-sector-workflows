import os
import datetime
from urllib.parse import urljoin
import requests
import bs4
import pandas as pd
from google.cloud import storage

# 環境変数の読み込み
BUCKET1 = os.environ.get('BUCKET1')
FILEPATH = os.environ.get('FILEPATH_soumu1')
LINE_TOKEN = os.environ.get('LINE_TOKEN')

# Google Cloud Functionsのエントリーポイント
# 定期実行トリガーによってこのmain関数が呼び出されます
def main(event, context):
    # 1. スクレイピングを実行し、現在のWebサイトの状態を <df_current> として作成
    df_current = scrape_website()

    # 2. Google Cloud Storage (GCS) から前回実行時のデータを <df_previous> として取得
    df_previous = download_csv_from_google_storage(BUCKET1, FILEPATH)
    
    # 3. 新旧データを比較し、今回新たに追加された要素のみを抽出
    new_elements = extract_new_elements(df_previous, df_current)
    
    # 4. 通知用のメッセージ文を作成し、LINEに送信
    message = create_message(new_elements)
    send_line_notification(message)
    
    # 5. 次回比較用に、現在の状態 <df_current> をGCSに上書き保存
    upload_csv_from_google_storage(BUCKET1, FILEPATH, df_current)

# WebサイトをスクレイピングしてDataFrameを作成する関数
def scrape_website():
    url = "https://www.soumu.go.jp/menu_news/s-news/index.html"
    html = requests.get(url)
    soup = bs4.BeautifulSoup(html.content, "html.parser")

    # 日付の取得と整形
    raw_dates = soup.find_all(class_='nw')
    str_dates = [x.text for x in raw_dates]
    # "YYYY年mm月dd日" 形式を変換
    d1 = [datetime.datetime.strptime(x, '%Y年%m月%d日') for x in str_dates]
    d2 = [x.strftime('%Y%m%d') for x in d1]
    dates = list(reversed(d2))  # 時系列を合わせるためリストを反転

    # タイトルの取得
    raw_titles = soup.select('td a')
    t1 = [x.text for x in raw_titles]
    titles = list(reversed(t1))

    # URLの取得（相対パスを絶対パスに変換）
    base_url = "https://www.soumu.go.jp/"
    raw_urls = [urljoin(base_url, x.get("href")) for x in raw_titles]
    urls = list(reversed(raw_urls))

    # まとめてDataFrame化
    zips = zip(dates, titles, urls)
    df_current = pd.DataFrame(list(zips), columns=['date', 'title', 'url'])
    
    return df_current

# Google Cloud Storage上のCSVファイルを読み込む関数
def download_csv_from_google_storage(bucket_name, blob_name):
    storage_client = storage.Client()
    
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # GCS上のファイルをCloud Functionsの一時ディレクトリ(/tmp)にダウンロード
    temp_path = '/tmp/previous_data.csv'
    blob.download_to_filename(temp_path)
    
    df_previous = pd.read_csv(temp_path, encoding="UTF-8") 

    return df_previous

# 新旧のDataFrameを比較し、新しいお知らせを抽出する関数
def extract_new_elements(df_previous, df_current):
    # タイトルをキーにして結合 (outer join)
    check = pd.merge(df_current, df_previous, on='title', how='outer')
    
    # 前回データ(date_y)が存在しない＝今回新しく出た記事、として抽出
    new_elements = check[check['date_y'].isnull()] 
    return new_elements

# 通知用メッセージを作成する関数
def create_message(new_elements):
    # 各要素をリスト化
    d = new_elements['date_x'].to_list()
    t = new_elements['title'].to_list()
    u = new_elements['url_x'].to_list()
    n = len(t) # 新着件数

    str1 = f"総務省が新たに{n}件の報道発表をしました。\n"
    # map関数で各件のメッセージを生成
    str2 = list(map(lambda x: f"件名：{t[x]}\n発表日：{d[x]}\nURL：{u[x]}\n", range(len(t))))
    
    # 新着が1件以上ある場合のみメッセージを結合、なければ 0 を返す
    if n >= 1:
        message = str1 + "\n" + "\n".join(str2)
    else:
        message = 0
        
    return message

# LINE Notify APIへ通知を送る関数
def send_line_notification(message):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {LINE_TOKEN}'}
    data = {'message': f'{message}'}
    
    # メッセージがある場合(0でない場合)のみ送信実行
    if message == 0:
        pass
    else:
        requests.post(line_notify_api, headers=headers, data=data)

# 最新のDataFrameをGoogle Cloud Storageへ保存する関数
def upload_csv_from_google_storage(bucket_name, blob_name, df_current):
    storage_client = storage.Client()
    
    # 一時ディレクトリにCSVとして書き出し
    temp_path = '/tmp/current_data.csv'
    df_current.to_csv(temp_path, index=False)
    
    # GCSへアップロード
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(temp_path)
    
    # 一時ファイルの削除 (メモリ節約のため)
    if os.path.exists(temp_path):
        os.remove(temp_path)