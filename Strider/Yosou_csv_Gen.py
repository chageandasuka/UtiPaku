import requests
import pandas as pd
import re
import sys
from bs4 import BeautifulSoup

# user define functions
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import get_tyokuten as getyoku

def Yosou_csv_Gen(url1, url2, race_id):
    csv_name = '00_test01.csv' # MachineLearning_RandomForest.pyの指定する文字列

    # 直展取得
    res2 = requests.get(url2)
    htstcd = res2.status_code
    # HTTPステータスコード 404
    if  htstcd == 404:
        print("Yosou_csv_Gen >> まだ直前展開がありません...")
        return -1
    else:
        pass

    res2.encoding = res2.apparent_encoding
    content2 = res2.text

    # データシート取得
    res = requests.get(url1)
    # HTTPステータスコード 404
    if  htstcd == 404:
        print("Yosou_csv_Gen >>障害レースかもね...")
        return -1
    else:
        pass

    tmpdate = re.findall('\/[0-9]{8}\/', url1)
    race_date = tmpdate[0].replace('/', '')

    res.encoding = res.apparent_encoding
    content = res.text

    tables = gtbl.get_tables(content)
    tcount = 0
    for dmy in tables:
        rows = ptbl.parse_table(dmy)
        if not rows[0]: # パラメータの無いテーブルは先頭からっぽ
            continue
        else:
            tcount += 1
            pass
        #print("{}:{}".format(tcount, race_id))
        if tcount == race_id:
            print("race_id : {}R".format(race_id))

            # データフレームにパラメータテーブルの情報を格納
            df2 = pd.DataFrame(rows[1:], columns=rows[0])

            ## レース情報
            soup = BeautifulSoup(content, "lxml")
            race_str = soup.find_all("div", attrs={"class", "headding03"})
            race_tmp = re.split('　', race_str[((race_id - 1) * 3)].text)
            tmpstr = race_tmp[0] #
            kaijou = tmpstr[:2]
            race_num = tmpstr[2:]

            tmpstr = race_tmp[2]
            course = tmpstr[:1]
            distance = tmpstr[1:-1]

            df2['日付'] = race_date
            df2['会場'] = kaijou
            df2['レース'] = race_num
            df2['コース'] = course
            df2['距離'] = distance
            cols = list(df2.columns.values)
            cols = ['距離']+ [col for col in df2 if col != '距離']
            df2 = df2[cols]
            cols = list(df2.columns.values)
            cols = ['コース']+ [col for col in df2 if col != 'コース']
            df2 = df2[cols]
            cols = list(df2.columns.values)
            cols = ['レース']+ [col for col in df2 if col != 'レース']
            df2 = df2[cols]
            cols = list(df2.columns.values)
            cols = ['会場']+ [col for col in df2 if col != '会場']
            df2 = df2[cols]
            cols = list(df2.columns.values)
            cols = ['日付']+ [col for col in df2 if col != '日付']
            df2 = df2[cols]

            df2['先行力順位'] = df2["先行力"].rank(ascending=False, method='min')
            df2['追走力順位'] = df2["追走力"].rank(ascending=False, method='min')
            df2['持久力順位'] = df2["持久力"].rank(ascending=False, method='min')
            df2['持続力順位'] = df2["持続力"].rank(ascending=False, method='min')
            df2['瞬発力順位'] = df2["瞬発力"].rank(ascending=False, method='min')
            df2['ＳＴ指数順位'] = df2["ＳＴ指数"].rank(ascending=False, method='min')
            df2['仕上指数順位'] = df2["仕上指数"].rank(ascending=False, method='min')

            # 直前ファクター取得
            t_df = getyoku.get_tyokuten(url2)

            # データシートと重複する列を除外する
            t_df = t_df.drop(["馬番", "馬名", "騎手名", "ST指数", "仕上指数"], axis=1)
            # データシートのDFと直前展開のDFを結合
            df2 = pd.merge(df2, t_df, right_index=True, left_index=True)

            df2.to_csv(csv_name, encoding="shift_jis", index=False, mode="w")
            print("Success!! : {}".format(csv_name))

        else:
            # 目的のレースではない
            pass

    return 1
