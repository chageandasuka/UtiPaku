import requests
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import table2csv as tbl2csv
import pandas as pd
from bs4 import BeautifulSoup



# ◆◆◆◆◆　ストライド競馬のデータと競馬ラボの結果　取得して結合して出力
# HTML データを取得する

repstr = '.html?idpm=ここに・・・'

url = input('ストライド データシートURL >> ')
ftmp = url.replace(repstr, '')
ftmp = ftmp[len(ftmp)-9:]
#csvfile = input('hozon name>> ')
csvfile = ftmp + '_result.csv'


# ステータス順位表示非表示切り替えスイッチ
# 0:非表示　1:表示
sw = 0

#csvfile = 'race_result.csv'

## ストライド新聞のデータ抽出
res = requests.get(url)
res.encoding = res.apparent_encoding
content = res.text

soup = BeautifulSoup(content, "lxml")
# 全ての<div>...</div>を取得
# レース情報の取得
course = soup.find_all("div", attrs={"class", "headding03"})
tl = soup.find_all("title")
print(tl[0].text)

# 競馬ラボのURL
url2 = input('競馬ラボ結果URL >>')
#url2 = "https://www.keibalab.jp/db/race/201811100301/"
url2 = url2[0:len(url2)-3]
# 会場番号
# 01:札幌
# 02:函館
# 03:福島
# 04:新潟
# 05:東京
# 06:中山
# 07:中京
# 08:京都
# 09:阪神
# 10:小倉
#url = input('>> ')
#csvfile = input('hozon name>> ')


# table 要素を取得する
# HTML 中のすべての table 要素が表として使われているとも
# 限らないし、またそれが望んでいるものであるとも限らないので
# このあたりのプロセスは関数としてまとめていない
# ( = テーブルの選択自体はユーザーが行う)
tables = gtbl.get_tables(content)
#### 結果書き出し
hoge = 0
ridx = 0 # 競馬ラボ結果URLレース番号用
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
    #print(df2)
    if sw == 1:
        df2[''] = ''
        df2['先行力順位'] = df2["先行力"].rank(ascending=False, method='min')
        df2['追走力順位'] = df2["追走力"].rank(ascending=False, method='min')
        df2['持久力順位'] = df2["持久力"].rank(ascending=False, method='min')
        df2['持続力順位'] = df2["持続力"].rank(ascending=False, method='min')
        df2['瞬発力順位'] = df2["瞬発力"].rank(ascending=False, method='min')
        df2['ＳＴ指数順位'] = df2["ＳＴ指数"].rank(ascending=False, method='min')
        df2['仕上指数順位'] = df2["仕上指数"].rank(ascending=False, method='min')

    #df2['順位合計'] = df2[['先行力順位','追走力順位','持久力順位','持続力順位','瞬発力順位','ＳＴ指数順位','仕上指数順位']].sum(axis=1)
    #####################################
    # 競馬ラボ結果取得
    #####################################
    if ridx < 9:
        race = "0" + str(ridx + 1) #ridx 0~8 = 1~9
    else:
        race = str(ridx + 1) #ridx 9~11 = 10~12

    url = url2 + race + "/"

    res = requests.get(url)
    # 競馬ラボがたまにレスポンス悪くて取れない時があるのでリトライを入れたいわけで。。。
    res.encoding = res.apparent_encoding
    content = res.text

    # ここから趣味の範囲 #####################################################
    bs = BeautifulSoup(content, "lxml")
    h1t = bs.find_all("h1", attrs={"class", "raceTitle fL"})
    tmp = h1t[0].text
    tmp = tmp.replace('\n','')
    tmp = tmp.replace('\t','')
    print(url, " : ", tmp)
    # ここまで趣味の範囲 #####################################################

    # table 要素を取得する
    lab_tables = gtbl.get_tables(content)
    # table 要素の先頭が結果
    rows = ptbl.parse_table(lab_tables[0])
    # 列名だけのDataFrameを作成
    tmp = rows[0]
    # パースしたtableデータの列タイトルが、オメガ指数（笑）のせいで他の要素よりも長い。
    # データ長を合わせないとエラーになるので、0～15の範囲でデータを作成する。
    df = pd.DataFrame(index=[], columns=tmp[0:15])
    # 行追加
    # タイトル行以外のデータをコピー
    rows_new = rows[1:]
    # 添え字初期化
    idx = 0
    for n in rows_new:
        df.loc[idx] = n[0:15]
        idx += 1

    # 単勝の列データを値で取得
    odds_v = df['単勝'].values
    tmp = ",".join(odds_v)
    # 改行の削除
    tmp = tmp.replace('\n','')
    # tabの削除
    tmp = tmp.replace('\t','')
    # なんでオッズの所に改行コードとか仕込んでるんだろう？
    # 競馬ラボクソだわﾀﾋね！
    odds_new = tmp.split(",")
    # DataFrameへ書き戻し
    lp = 0
    for dmy in odds_new:
        df.at[lp, '単勝'] = dmy
        lp += 1
    # 必要そうなデータだけを抽出
    df = df[['着', '馬', '人', '単勝']]
    # ソートしたいのでstrをint8に変換
    #df['馬'] = df['馬'].astype('int8')
    #print(type(df.loc[0,'馬']))
    #print(df.sort_values(by='馬'))
    #df['馬'] = df['馬'].zfill(2)
    #print(df['馬'].astype(str).str.zfill(2))
    df['馬'] = df['馬'].astype(str).str.zfill(2)
    df = df.rename(columns={'馬': '馬番'})
    #print(df)
    #df3 = pd.concat([ df2, df[['着', '人', '単勝']] ], axis=1)
    df3 = pd.merge(df2, df, how='inner', on='馬番')
    #print(df3)
    if hoge != 0:
        #print("ヘッダーなし")
        #df2.to_csv(csvfile, encoding="shift_jis", header=False, index=False, mode="a")
        df3.to_csv(csvfile, encoding="shift_jis", header=False, index=False, mode="a")
        # CSV ファイル (employee.csv) として出力（追記モード）
    else:
        #print("ヘッダーあり")
        # hoge == 0の時だけヘッダー出力
        #df2.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")
        df3.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")

    hoge += 3
    ridx += 1

print('できた！')
