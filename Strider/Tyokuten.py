
import requests
import sys
import re

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import keibaLab_CourseTable as klabtbl
from u_def import UrlRetry as urlget



collist = [
        "直前印",
        "前日印",
        "指数印",
        "ST指数",
        "仕上指数",
        "馬番",
        "馬名",
        "激走馬",
        "脚質(前走)",
        "騎手名",
        "パドック",
        "オッズ",
        "馬体",
        "気配",
        "状態",
        "脚元",
        "馬具",
        "馬場",
        "脚質",
        "合算値",
        "ゴール前着差",
        "上昇馬"
]

print("ヘッダの数={}".format(len(collist)))

# HTML データを取得する
url = input("直展URL >> ")

res = requests.get(url)
res.encoding = res.apparent_encoding
content = res.text

htstcd = res.status_code
# HTTPステータスコード 404
if  htstcd == 404:
    print("{} 無いです".format(url))
    sys.exit()

# 列のみのデータフレーム作成
df = pd.DataFrame(index=[], columns=collist)
#print(df.head())

soup = BeautifulSoup(content, "lxml")
tables = soup.find_all("table")

print("table num:{}".format(len(tables)))
for table in tables:
    tmp = table.find_all('tr')
    print("trの数={}".format(len(tmp)))

# 直前総合のテーブルを直接指定
# 0: 前日総合, 1: 直前総合, 2: 前半３F順, 3: 勝負所順, 4: ゴール前順
trs = tables[1].find_all('tr', attrs={"class", "result"})
print("tr class=resultの数={}".format(len(trs)))
for tr in trs:
    #print(tr)
    columns = []
    i = 0
    for me in tr:
        if type(me) is Tag:
            #print(i)
            #print(me)
            # imgタグを取得
            imgtag = me.find_all('img')
            # Noneで初期化
            srcstr = None

            # imgタグがあればsrcの文字列を取得する
            for e in imgtag:
                srcstr = e['src']

            # 非該当馬のために初期化
            gekihorse = 0
            uphorse = 0
            ashi = 0 # 新馬だけ？
            if srcstr != None:

                if "gekihorse" in srcstr:
                    #激走馬
                    #print("激走馬")
                    gekihorse = 1
                else:

                    if "k1.png" in srcstr:
                        #脚質：逃げ
                        #print("脚質は 逃げ だよ！")
                        ashi = 1
                    elif "k2.png" in srcstr:
                        #脚質：先行
                        #print("脚質は 先行 だよ！")
                        ashi = 2
                    elif "k3.png" in srcstr:
                        #脚質：差し
                        #print("脚質は 差し だよ！")
                        ashi = 3
                    elif "k4.png" in srcstr:
                        #脚質：追込
                        #print("脚質は ポツン だよ！")
                        ashi = 4
                    else:

                        if "uphorse.png" in srcstr:
                            #上昇馬
                            #print("上昇！")
                            uphorse = 1

            tmpstr = me.text
            tmpstr = tmpstr.replace('\n', '')
            tmpstr = tmpstr.replace(' ',  '')
            tmpstr = tmpstr.replace('p',  '')

            # このifはtrタグと列名が対応できる
            if i == 7:
                # 脚質
                columns.append(ashi)
            elif i == 20:
                # 上昇馬
                columns.append(uphorse)
            else:
                columns.append(tmpstr)

            # 激走馬は馬名の後ろにimgタグでくっついているだけなので↑のifとは分ける
            if i == 6:
                columns.append(gekihorse)

            i += 1
        elif type(me) is NavigableString:
            continue

#    print("詳細データ={}:{}".format(len(columns), columns))
    se = pd.Series(columns, index=collist)

    # 記号を置換する。とりあえず良い印を高い数字に。
    se = se.replace({'－': 0, '注': 1, '△': 2, '▲': 3, '○': 4, '◎': 5})
    #print(se)
    df = df.append(se, ignore_index=True)
    #print(df.shape)


print(df.head())
df.to_csv('tyokuten.csv', encoding="shift_jis", index=False, mode="a")
