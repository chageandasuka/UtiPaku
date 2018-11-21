import requests
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import keibaLab_CourseTable as klabtbl
from u_def import UrlRetry as urlget

import pandas as pd
from bs4 import BeautifulSoup
import re

# データシートのあるアドレスの固定文字列
CNST_URL = "https://stride.get-luck.jp/member/lap_character"
# 競馬ラボのURL
CNST_LABURL = "https://www.keibalab.jp/db/race/"

csvfile = "00_LearnData.csv"

# 構文解析したいマン
inurl = input('データシートURL(いつのURLでもOK!) >> ')

# ストライドURLの.html~を抽出。
# 後々replaceで使ったりする。
idpm = re.findall('\.html.+', inurl)

ydir = re.findall('\/[0-9]{4}\/', inurl)
# 正規表現で抽出した結果はlist objectで格納される。
# 今回抽出するのは /数字4桁/ 、つまりURL内の西暦なので1か所しかHitしない前提。
yyyy = ydir[0].replace('/', '')
#print(yyyy)

import datetime
from datetime import timedelta
# 任意の日付データをyyyymmdd形式にする
# 追走力形式は20180310から導入されたみたい。
datestr = datetime.date(int(yyyy), 3, 9)
yyyymmdd = datestr.strftime('%Y%m%d')

dt_now = datetime.date.today()

td = dt_now - datestr
print(td.days)

# 東西ローカル記号リスト
wel = ['E', 'W', 'L']

# 最初の書き込みのみヘッダを出すためのフラグ
h_flg = 0
# 順次アクセスするためのfor
for d in range(1, td.days):
    # 日のインクリメント
    datestr = datestr + timedelta(days=1)
    # yyyymmdd形式へ変換
    yyyymmdd = datestr.strftime('%Y%m%d')
    # 東西ローカル記号リストのfor
    for s in wel:
        # URL文字列作成
        # http://~~~ + /2018/ + yyyymmdd + / + yyyymmdd + {'W','E','L'} + .html?idpm=0000
        url = CNST_URL + ydir[0] + yyyymmdd + '/' + yyyymmdd + s + idpm[0]
        #print(url)

        ##### URLへリクエスト #####
        res = requests.get(url)

        # HTTPステータスコード = 404 を判定する。
        # 競馬開催日でなければ西のURLが存在しない = 404なのでbreakしてその日は終了。
        # 過剰アクセス抑制になるかな？
        htstcd = res.status_code
        # HTTPステータスコード 404
        if  htstcd == 404:
            print(str(htstcd) + ':' + yyyymmdd + s)
            break

        print(yyyymmdd + s + " データシート取得")
        res.encoding = res.apparent_encoding
        content = res.text
        soup = BeautifulSoup(content, "lxml")
        tables = gtbl.get_tables(content)
        # 全ての<div>...</div>を取得
        race_str = soup.find_all("div", attrs={"class", "headding03"})

        ridx = 0 # 競馬ラボ結果URLレース番号用
        hoge = 0
        for dmy in tables:
            rows = ptbl.parse_table(dmy)
            if not rows[0]:
                continue
            df2 = pd.DataFrame(rows[1:], columns=rows[0])
            #print(course[hoge].text)
            # レース情報をDataFrameに追加
            #df2['レース情報'] = course[hoge].text
            #print(head3[hoge].text)
            # レース情報に含まれる全角スペースを基準にして分割する
            #   0              1                  2            3
            #['中山1R', '３歳未勝利３歳(馬齢)', 'ダ1200ｍ', '10:10発走']
            # 1と3は不要
            # 0は会場名とレース番号を分ける
            # 2はコースと距離を分ける
            race_tmp = re.split('　', race_str[hoge].text)
            print(race_tmp)

            # 東京と1R分割
            tmpstr = race_tmp[0]
            kaijou = tmpstr[:2]
            race_num = tmpstr[2:]

            tmpstr = race_tmp[2]
            course = tmpstr[:1]
            distance = tmpstr[1:-1]

            df2['日付'] = yyyymmdd

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

            df2[''] = ''
            df2['先行力順位'] = df2["先行力"].rank(ascending=False, method='min')
            df2['追走力順位'] = df2["追走力"].rank(ascending=False, method='min')
            df2['持久力順位'] = df2["持久力"].rank(ascending=False, method='min')
            df2['持続力順位'] = df2["持続力"].rank(ascending=False, method='min')
            df2['瞬発力順位'] = df2["瞬発力"].rank(ascending=False, method='min')
            df2['ＳＴ指数順位'] = df2["ＳＴ指数"].rank(ascending=False, method='min')
            df2['仕上指数順位'] = df2["仕上指数"].rank(ascending=False, method='min')

            #print('****ラボデータ取得開始')
            #####################################
            # 競馬ラボ結果取得
            #####################################
            if ridx < 9:
                race_num_str = "0" + str(ridx + 1) #ridx 0~8 = 1~9
            else:
                race_num_str = str(ridx + 1) #ridx 9~11 = 10~12

            # 競馬場名抽出 → 競馬ラボ会場Noへ変換
            #course = df2['レース情報'].loc[0]     # 競馬場名抽出 (先頭データより判定)
            #print(df2['レース情報'].loc[0])
            #course = course[0:2]                    # ↑(左から2文字抽出)
            course = df2['会場'].loc[0]

            course_no = klabtbl.keibaLab_CourseTables(course)
            # 会場IDを数字で戻すようにしたためここで数字→文字列に変換して2桁表示
            course_no = str(course_no + 1).zfill(2)
            print("  会場 = {}, 会場ID = {}".format(course, course_no))

            # 競馬ラボURL作成
            url = CNST_LABURL + yyyymmdd + course_no + race_num_str + "/"

            content = urlget.UrlRetry(url)

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


            if h_flg == 1:
                #print("ヘッダーなし")
                #df2.to_csv(csvfile, encoding="shift_jis", header=False, index=False, mode="a")
                df3.to_csv(csvfile, encoding="shift_jis", header=False, index=False, mode="a")
                # CSV ファイル (employee.csv) として出力（追記モード）
            else:
                #print("ヘッダーあり")
                # hoge == 0の時だけヘッダー出力
                #df2.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")
                df3.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")
                h_flg = 1

            hoge += 3
            ridx += 1


input("Enterで終了")
