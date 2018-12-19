import csv
import sys
import requests
import re
import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from time import sleep

## ストライドからメタリストを作る

# 今のところ競馬ラボのアクセス時にエラー（タイムアウト？）している僕のための処置。
# ひょっとすると、おま環である可能性が高い。
def UrlRetry(url):

    # Webアクセスのリトライ回数を指定する
    retry_max_count = 5
    retry_count = 0
    sleep_time = 2.5

    #print("url={}".format(url))
    try:
        for i in range(0, retry_max_count):
            retry_count += 1
            try:
                # タイムアウト設定してみる
                res = requests.get(url, timeout=10)
                return res
            except requests.exceptions.RequestException as err:
                #print("{}:{}".format(type(err), retry_count))
                sys.stdout.write("retry_count:{}\r".format(retry_count))
                sys.stdout.flush()
            # sleep_time[sec]何もしない
            sleep(sleep_time)
        # リトライ回数の上限を超えた場合はエラーにする
        if retry_count > retry_max_count:
            raise Exception("リトライ回数の上限を超えました")
    except Exception as e:
        raise e
    return

def JK_Daisuki(jk):

    if jk == "中谷雄":
        jk = "中谷雄太"
    elif jk == "津村明":
        jk = "津村明秀"
    elif jk == "丸田恭":
        jk = "丸田恭介"
    elif jk == "菱田裕":
        jk == "菱田裕二"
    elif jk == "木幡巧":
        jk = "木幡巧也"
    elif jk == "丹内祐":
        jk = "丹内祐次"
    elif jk == "北村友":
        jk = "北村友一"
    elif jk == "柴山雄":
        jk = "柴山雄一"
    elif jk == "中井裕":
        jk = "中井裕二"
    elif jk == "五十嵐":
        jk = "五十嵐"
    elif jk == "田辺裕":
        jk = "田辺裕信"
    elif jk == "野中悠":
        jk = "野中悠太"
    elif jk == "石川裕":
        jk = "石川裕紀"
    elif jk == "内田博":
        jk = "内田博幸"
    elif jk == "戸崎圭":
        jk = "戸崎圭太"
    elif jk == "横山典":
        jk = "横山典弘"
    elif jk == "長岡禎":
        jk = "長岡禎仁"
    elif jk == "松岡正":
        jk = "松岡正海"
    elif jk == "蛯名正":
        jk = "蛯名正義"
    elif jk == "柴田善":
        jk = "柴田善臣"
    elif jk == "勝浦正":
        jk = "勝浦正樹"
    elif jk == "西田雄":
        jk = "西田雄一"
    elif jk == "鮫島克":
        jk = "鮫島克駿"
    elif jk == "松若風":
        jk = "松若風馬"
    elif jk == "松田大":
        jk = "松田大作"
    elif jk == "岩崎翼":
        jk = "岩崎翼"
    elif jk == "川須栄":
        jk = "川須栄彦"
    elif jk == "坂井瑠":
        jk = "坂井瑠星"
    elif jk == "伴啓太":
        jk = "伴啓太"
    elif jk == "丸山元":
        jk = "丸山元気"
    elif jk == "杉原誠":
        jk = "杉原誠人"
    elif jk == "黛弘人":
        jk = "黛弘人"
    elif jk == "武　豊":
        jk ="武豊"
    elif jk == "川島信":
        jk ="川島信二"
    elif jk == "福永祐":
        jk ="福永祐一"
    elif jk == "幸英明":
        jk ="幸英明"
    elif jk == "松山弘":
        jk ="松山弘平"
    elif jk == "森裕太":
        jk ="森裕太朗"
    elif jk == "秋山真":
        jk ="秋山真一"
    elif jk == "武士沢":
        jk ="武士沢友"
    elif jk == "太宰啓":
        jk ="太宰啓介"
    elif jk == "加藤祥":
        jk ="加藤祥太"
    elif jk == "国分優":
        jk ="国分優作"
    elif jk == "川又賢":
        jk ="川又賢治"
    elif jk == "荻野極":
        jk ="荻野極"
    elif jk == "酒井学":
        jk = "酒井学"
    elif jk == "高倉稜":
        jk ="高倉稜"
    elif jk == "和田竜":
        jk ="和田竜二"
    elif jk == "横山和":
        jk ="横山和生"
    elif jk == "原田和":
        jk ="原田和真"
    elif jk == "石橋脩":
        jk ="石橋脩"
    elif jk == "浜中俊":
        jk ="浜中俊"
    elif jk == "鮫島良":
        jk ="鮫島良太"
    elif jk == "岡田祥":
        jk ="岡田祥嗣"
    elif jk == "水口優":
        jk ="水口優也"
    elif jk == "富田暁":
        jk ="富田暁"
    elif jk == "Ｍデム":
        jk ="Ｍ．デム"
    elif jk == "服部寿":
        jk ="服部寿希"
    elif jk == "アヴド":
        jk ="アヴドゥ"
    elif jk == "西村淳":
        jk ="西村淳也"
    elif jk == "ルメー":
        jk ="ルメール"
    elif jk == "川田将":
        jk ="川田将雅"
    elif jk == "池添謙":
        jk ="池添謙一"
    elif jk == "四位洋":
        jk ="四位洋文"
    elif jk == "藤岡佑":
        jk ="藤岡佑介"
    elif jk == "藤岡康":
        jk ="藤岡康太"
    elif jk == "岩田康":
        jk ="岩田康誠"
    elif jk == "小崎綾":
        jk ="小崎綾也"
    elif jk == "難波剛":
        jk ="難波剛健"
    elif jk == "藤懸貴":
        jk ="藤懸貴志"
    elif jk == "三津谷":
        jk ="三津谷隼"
    elif jk == "三浦皇":
        jk ="三浦皇成"
    elif jk == "柴田大":
        jk ="柴田大知"
    elif jk == "吉村智":
        jk ="吉村智洋"
    elif jk == "田中健":
        jk ="田中健"
    elif jk == "義英真":
        jk ="義英真"
    elif jk == "熊沢重":
        jk ="熊沢重文"
    elif jk == "吉田隼":
        jk ="吉田隼人"
    elif jk == "大野拓":
        jk ="大野拓弥"
    elif jk == "岩部純":
        jk ="岩部純二"
    elif jk == "嶋田純":
        jk ="嶋田純次"
    elif jk == "菊沢一":
        jk ="菊沢一樹"
    elif jk == "横山武":
        jk ="横山武史"
    elif jk == "木幡初":
        jk ="木幡初也"
    elif jk == "小牧太":
        jk ="小牧太"
    elif jk == "国分恭":
        jk ="国分恭介"
    elif jk == "柴田未":
        jk ="柴田未崎"
    elif jk == "城戸義":
        jk ="城戸義政"
    elif jk == "宮崎北":
        jk ="宮崎北斗"
    elif jk == "田中勝":
        jk ="田中勝春"
    elif jk == "村田一":
        jk ="村田一誠"
    elif jk == "木幡育":
        jk ="木幡育也"
    elif jk == "菅原隆":
        jk ="菅原隆一"
    elif jk == "北村宏":
        jk ="北村宏司"
    elif jk == "江田照":
        jk ="江田照男"
    elif jk == "藤田菜":
        jk ="藤田菜七"
    elif jk == "黒岩悠":
        jk ="黒岩悠"
    elif jk == "古川吉":
        jk ="古川吉洋"
    elif jk == "荻野琢":
        jk ="荻野琢真"
    elif jk == "伊藤工":
        jk ="伊藤工真"
    elif jk == "山口勲":
        jk ="山口勲"
    elif jk == "西村太":
        jk ="西村太一"
    elif jk == "嘉藤貴":
        jk ="嘉藤貴行"
    elif jk == "小林徹":
        jk ="小林徹弥"
    elif jk == "武藤雅":
        jk ="武藤雅"
    elif jk == "白浜雄":
        jk = "白浜雄造"
    elif jk == "高田潤":
        jk = "高田潤"
    elif jk == "森一馬":
        jk = "森一馬"
    elif jk == "植野貴":
        jk = "植野貴也"
    elif jk == "石神深":
        jk ="石神深一"
    elif jk == "平沢健":
        jk ="平沢健治"
    elif jk == "中村将":
        jk ="中村将之"
    elif jk == "上野翔":
        jk ="上野翔"
    elif jk == "佐久間寛":
        jk = "佐久間"
    elif jk == "井上敏":
        jk ="井上敏樹"
    elif jk == "佐藤友":
        jk ="佐藤友則"
    elif jk == "竹之下":
        jk ="竹之下智"
    elif jk == "オドノヒ":
        jk ="オドノヒ"
    elif jk == "モレイ":
        jk ="モレイラ"
    elif jk == "的場勇":
        jk ="的場勇人"
    elif jk == "吉原寛":
        jk ="吉原寛人"
    elif jk == "山田敬":
        jk ="山田敬士"
    elif jk == "小島太":
        jk ="小島太一"
    elif jk == "ムーア":
        jk ="ムーア"
    elif jk == "中野省":
        jk ="中野省吾"
    elif jk == "高野和":
        jk ="高野和馬"
    elif jk == "ボウマ":
        jk ="ボウマン"
    elif jk == "小坂忠":
        jk ="小坂忠士"
    elif jk == "浜野谷":
        jk ="浜野谷憲"
    elif jk == "今野忠成":
        jk ="今野忠成"
    elif jk == "森泰斗":
        jk ="森泰斗"
    elif jk == "石川倭":
        jk ="石川倭"
    elif jk == "Ｃデム":
        jk ="Ｃ．デム"
    elif jk == "ビュイ":
        jk ="ビュイッ"
    elif jk == "鮫島駿":
        jk ="鮫島克駿"
    else:
        print("{}->その他".format(jk))
        jk ="その他"
    return jk

# データシートのあるアドレスの固定文字列
CNST_URL = "https://stride.get-luck.jp/member/"
wel = ['E', 'W', 'L']

if __name__ == "__main__":
    url = input('>>' )

    y = re.findall('\/[0-9]{4}\/', url)

    yyyymmdd = re.findall('\/[0-9]{8}\/', url)
    yyyymmdd = re.findall('[0-9]{8}', yyyymmdd[0])
    # ストライドURLの.html~を抽出。
    idpm = re.findall('\.html.+', url)

    tmp_tenkai_url = []
    for s in wel:
        url = CNST_URL + 'lap_character' + y[0] + yyyymmdd[0] + '/' + yyyymmdd[0] + s + idpm[0]
        #print(url)
        # ここからリンク作成
        tenkai_url = []
        with UrlRetry(url) as response:
            response.encoding = response.apparent_encoding
            html = response.text

            soup = BeautifulSoup(html, 'lxml')
            # データシートページのリンクを取得
            elems = soup.select('a')
            for elem in elems:
                if elem.getText() == "前日":
                    tmp = elem.get('href')
                    tmp = tmp.replace('../', '')
                    tmp_tenkai_url = np.append(tmp_tenkai_url, CNST_URL + tmp) # 縦方向で結合

        tenkai_url.append(tmp_tenkai_url) # 横方向で結合[0,1,2]

    # ここから作成したURLでスクレイピング
    for tenkai in tenkai_url:
        for url in tenkai:
            #print("url:{}".format(url))
            with UrlRetry(url) as response:
                if response.status_code == 404:
                    continue

                #response.encoding = response.apparent_encoding
                #html = response.text
                #soup = BeautifulSoup(html, 'lxml')
                soup = BeautifulSoup(response.content, 'html.parser')

                racenumber = soup.find_all("div", id="racenumber")
                racenumber = racenumber[0].text

                racejoken = soup.find_all("div", id="racejoken")

                kyori = soup.find_all("span", id="kyori")
                kyori = kyori[0].text
                kyori_met = re.findall('[0-9]{4}', kyori)
                tenki = soup.find_all("span", id="tenki")
                tenki = tenki[0].text
                baba = soup.find_all("span", id="baba")
                baba = baba[0].text

                #header ="{}|{}|{}|{}|{}|{}".format(racenumber[:2],kyori[:1],kyori[1:-1],tenki,baba,yyyymmdd[0])
                #print("{}|{}|{}|{}|{}|{}".format(racenumber[:2],kyori[:1],kyori[1:-1],tenki,baba,yyyymmdd[0]))
                header = []
                tmp = (racenumber[:2], kyori[:1], tenki, kyori_met[0], yyyymmdd[0])

                header.append('|'.join(tmp))
                print(header)

                tables = soup.find_all("table")
                #print("table num:{}".format(len(tables)))
                # 直前総合のテーブルを直接指定
                # 0: 前日総合, 1: 前半３F順, 2: 勝負所順, 3: ゴール前順
                trs = tables[0].find_all('tr', attrs={"class", "result"})
                horses_name = tables[0].find_all('span', attrs={"class", "stbamei"})
                jks_name = tables[0].find_all('span', attrs={"class", "stkisyuname"})

                #print(horses_name)
                #print(jks_name)

            with open('meta_list.txt', 'w', newline='') as wf:
                csvwriter = csv.writer(wf, quoting=csv.QUOTE_MINIMAL)
                hrjk = []
                for i, horse in enumerate(horses_name):
                    tmp = (horse.text, JK_Daisuki(jks_name[i].text))
                    hrjk.append('|'.join(tmp))

                header.append(','.join(hrjk)) #なんか知らんがこれでうまく結合できる
                csvwriter.writerow(header)


            #sys.exit()
