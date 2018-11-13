import requests
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import table2csv as tbl2csv

import pandas as pd
from bs4 import BeautifulSoup


repstr = '.html?idpm=ここに数字の列をいれとく'


# HTML データを取得する
url = input('>> ')
u_tmp = url.replace(repstr, '')
ftmp = u_tmp[len(u_tmp)-9:len(u_tmp)-1]

csvfile = ftmp + 'EWL_data.csv'
print(csvfile)

# 東西＋ローカル
# 2会場の時はどうしよう？また今度考える
tablst = ['E', 'W', 'L']

for kaijou in tablst:
    url = u_tmp[0:len(u_tmp)-1] + kaijou + repstr
    print(url)

    #csvfile = '00_test.csv'
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    content = res.text

    soup = BeautifulSoup(content, "lxml")
    # 全ての<div>...</div>を取得
    course = soup.find_all("div", attrs={"class", "headding03"})

    # table 要素を取得する
    # HTML 中のすべての table 要素が表として使われているとも
    # 限らないし、またそれが望んでいるものであるとも限らないので
    # このあたりのプロセスは関数としてまとめていない
    # ( = テーブルの選択自体はユーザーが行う)
    tables = gtbl.get_tables(content)
    #table = tables[8]
    #print(table)
    #for num in tables:
    #    print(num)
    hoge = 0
    for dmy in tables:
        rows = ptbl.parse_table(dmy)
        if not rows[0]:
            continue
        df2 = pd.DataFrame(rows[1:], columns=rows[0])
        #print(course[hoge].text)
        # レース情報をDataFrameに追加
        df2['レース情報'] = course[hoge].text

        # DataFrame末尾に追加したレース情報を先頭に移動する
        cols = list(df2.columns.values)
        cols = ['レース情報']  + [col for col in df2 if col != 'レース情報']
        df2 = df2[cols]

        # for Debug
        # print(df2)
        df2[''] = ''
        df2['先行力順位'] = df2["先行力"].rank(ascending=False, method='min')
        df2['追走力順位'] = df2["追走力"].rank(ascending=False, method='min')
        df2['持久力順位'] = df2["持久力"].rank(ascending=False, method='min')
        df2['持続力順位'] = df2["持続力"].rank(ascending=False, method='min')
        df2['瞬発力順位'] = df2["瞬発力"].rank(ascending=False, method='min')
        df2['ＳＴ指数順位'] = df2["ＳＴ指数"].rank(ascending=False, method='min')
        df2['仕上指数順位'] = df2["仕上指数"].rank(ascending=False, method='min')

        # レース情報のインデックスは0,3,6...なので
        hoge += 3
        # CSV ファイル (employee.csv) として出力（追記モード）
        df2.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")
