# coding: utf-8
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import sys
import datetime
import os

from u_def import get_tables as gtbl
from u_def import parse_table as ptbl

# HTML データを取得する
inurl = input('データシートURL >> ')
URL_BASE = "https://stride.get-luck.jp/member/"

################################################################################
def GetSoup(url):
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    content = res.text
    soup = BeautifulSoup(res.content, 'html.parser')

    return soup, content

def MoveCol(dmy_df, col_list):
    for col_name in col_list:
        cols = list(dmy_df.columns.values)
        cols = [col_name]+ [col for col in dmy_df if col != col_name]
        dmy_df = dmy_df[cols]
    return dmy_df
################################################################################

soup, dmy = GetSoup(inurl)
# 不要なデータはdmyで棄てる
del dmy
# リンクのリスト作成
linka = soup.findAll('a')
link_list = []
for hr in linka:
    link = hr.get('href')
    if link != None:
        if link[0:4] == 'race':
            link_list.append(link)

# URLから日付取得
race_date = re.findall('racedate=([0-9]{8})', inurl)
csvfile = race_date[0] + '_StridViewer.csv'

df = pd.DataFrame()
# 各リンク先データの取得
for member in link_list:
    soup, content = GetSoup(URL_BASE + member)

    race_name = soup.find_all('p', attrs={'class', "race_name"})
    print("  {}".format(race_name[0].text))
    race_detail = soup.find_all('p', attrs={'class', "race_detail"})

    # テキスト取得
    rd_txt = race_detail[0].text

    # 障害判定用文字列
    detail = rd_txt[0:2]

    if detail != '障害':
        # 会場
        kaijou = race_name[0].text[0:2]
        # コース
        cource = re.findall('ダート', rd_txt)
        if len(cource) > 0:
            cource = cource[0]
        else:
            cource = '芝'

        # 距離
        distance = re.findall('([0-9]{4})m', rd_txt)
        distance = distance[0]

        # レース番号はURLから作る
        race_num = re.findall('racekey=[0-9]{6}([0-9][0-9])', member)
        race_num = race_num[0] + 'R'
        #print("{} {} {} {}".format(kaijou, race_num, cource, distance))

        tables = gtbl.get_tables(content)

        # Tab:基本->展開->外厩の順に取得
        df_race = pd.DataFrame()
        for table in tables:
            rows = ptbl.parse_table(table)
            if len(df_race) > 0:
                t_df = pd.DataFrame(rows[1:], columns=rows[0])
                df_race = pd.merge(df_race, t_df)
            else:
                df_race = pd.DataFrame(rows[1:], columns=rows[0])

        # レース情報の付与
        df_race['距離'] = distance
        df_race['コース'] = cource
        df_race['レース'] = race_num
        df_race['会場'] = kaijou

        # 引数['C','B','A']はA->B->Cの順に並び変え
        df_race = MoveCol(df_race, ['距離','コース','レース','会場'])

        # 厩舎×の列データを数字に変換する。
        # データなしは0にする。
        for idx in range(45, 37, -1):
            df_race.iloc[:, idx] = df_race.iloc[:, idx].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        # 出遅率の列データを数字に変換する。
        # データなしは0にする。
        df_race['出遅率'] = df_race['出遅率'].replace('%','', regex=True).replace('', '0', regex=True).astype(int)

        if len(df) > 0:
            df = pd.concat([df, df_race])
        else:
            df = df_race

        #print(df.shape)

    else:
        #print('森キュンがんばれ～')
        pass

#exit()
df = df.drop([''], axis=1)
df.to_csv(csvfile, encoding='shift_jis', index=False, mode='w')
