import socket
import requests

from bs4 import BeautifulSoup
from time import sleep

# 今のところ競馬ラボのアクセス時にエラー（タイムアウト？）している僕のための処置。
# ひょっとすると、おま環である可能性が高い。
def UrlRetry(url):

    # Webアクセスのリトライ回数を指定する
    retry_max_count = 5
    retry_count = 0
    sleep_time = 1

    #print("url={}".format(url))
    try:
        for i in range(0, retry_max_count):
            retry_count += 1
            try:
                # タイムアウト設定してみる
                res = requests.get(url, timeout=10)
                res.encoding = res.apparent_encoding
                #res.raise_for_status()
                content = res.text
                bs = BeautifulSoup(content, "lxml")
                h1t = bs.find_all("h1", attrs={"class", "raceTitle fL"})
                # イケてないけど・・・
                # 何らかの理由によりrequestsに失敗した場合ここでエラーにする。
                # その際はIndexErrorとなるのでtyr~exceptはIndexErrorを採用する。
                tmp = h1t[0].text
                tmp = tmp.replace('\n','')
                tmp = tmp.replace('\t','')
                print("  競馬ラボ:{}".format(tmp))
                # HTMLパーサーでパースする
                return content
            except IndexError:
                print("retry_count:{}".format(retry_count))

            # sleep_time[sec]何もしない
            sleep(sleep_time)
        # リトライ回数の上限を超えた場合はエラーにする
        if retry_count > retry_max_count:
            raise Exception("リトライ回数の上限を超えました")
            input("Enterで終了")
    except Exception as e:
        raise e
    return
