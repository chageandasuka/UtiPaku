import requests
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import table2csv as tbl2csv
import pandas as pd
from bs4 import BeautifulSoup

# 機械学習予測用データ作成コード
#
#
#
#

# HTML データを取得する
url = input('抽出するデータのURL >> ')
#csvfile = input('hozon name>> ')


csvfile = '00_test'
res = requests.get(url)
res.encoding = res.apparent_encoding
content = res.text

soup = BeautifulSoup(content, "lxml")
# 全ての<div>...</div>を取得
course = soup.find_all("div", attrs={"class", "headding03"})
tl = soup.find_all("title")
print(tl[0].text)

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
fcnt = 1
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
    #df2[''] = ''
    #df2['先行力順位'] = df2["先行力"].rank(ascending=False, method='min')
    #df2['追走力順位'] = df2["追走力"].rank(ascending=False, method='min')
    #df2['持久力順位'] = df2["持久力"].rank(ascending=False, method='min')
    #df2['持続力順位'] = df2["持続力"].rank(ascending=False, method='min')
    #df2['瞬発力順位'] = df2["瞬発力"].rank(ascending=False, method='min')
    #df2['ＳＴ指数順位'] = df2["ＳＴ指数"].rank(ascending=False, method='min')
    #df2['仕上指数順位'] = df2["仕上指数"].rank(ascending=False, method='min')

    # レース情報のインデックスは0,3,6...なので
    hoge += 3
    # CSV ファイル (employee.csv) として出力（追記モード）
    race_num = str(fcnt)
    race_num = race_num.zfill(2)
    df2.to_csv(csvfile + race_num + '.csv', encoding="shift_jis", index=False, mode="a")
    #break
    fcnt += 1
