import requests
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import keibaLab_CourseTable as klabtbl
from u_def import UrlRetry as urlget

import pandas as pd
from bs4 import BeautifulSoup
import re


# ◆◆◆◆◆　ストライド競馬のデータと競馬ラボの結果　取得して結合して出力
# HTML データを取得する
inurl = input('データシートURL >> ')

# 後々replaceで使ったりする。
idpm = re.findall('\.html.+', inurl)

u_tmp = inurl.replace(idpm[0], '')
ftmp = u_tmp[len(u_tmp)-9:len(u_tmp)-1]

csvfile = ftmp + 'EWL_data.csv'
print(csvfile)

# 東西＋ローカル
tablst = ['E', 'W', 'L']
#print(tablst)
for kaijou in tablst:
    url = u_tmp[0:len(u_tmp)-1] + kaijou + idpm[0]
    print(url)

    #csvfile = '00_test.csv'
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    content = res.text

    htstcd = res.status_code
    # HTTPステータスコード 404
    if  htstcd == 404:
        print(str(htstcd) + ':' + kaijou)
        continue

    soup = BeautifulSoup(content, "lxml")
    # 全ての<div>...</div>を取得
    race_str = soup.find_all("div", attrs={"class", "headding03"})

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
    ridx = 0 # 競馬ラボのレースindex
    for dmy in tables:
        rows = ptbl.parse_table(dmy)
        if not rows[0]:
            continue
        df2 = pd.DataFrame(rows[1:], columns=rows[0])
        ##ここから　コース情報分割処理
        # レース情報に含まれる全角スペースを基準にして分割する
        #   0              1                  2            3
        #['中山1R', '３歳未勝利３歳(馬齢)', 'ダ1200ｍ', '10:10発走']
        # ひとまず右記の形式で出力する。　例：中山, 1R, ダ, 1200
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
        ##########################################
        # レース情報をDataFrameに追加
        #df2['レース情報'] = race_str[hoge].text
        # DataFrame末尾に追加したレース情報を先頭に移動する
        #cols = list(df2.columns.values)
        #cols = ['レース情報']  + [col for col in df2 if col != 'レース情報']
        #df2 = df2[cols]
        df2['日付'] = ftmp

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
        ##ここまで　コース情報分割処理

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

        # 競馬ラボから結果取得
        sw_KeibaLab = 1     # 競馬ラボ情報取得切り替えSW (1：有効 0：無効)
        if sw_KeibaLab == 1:

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
            url2 = "https://www.keibalab.jp/db/race/" + ftmp + course_no + "01/"
            url2 = url2[0:len(url2)-3]

            #####################################
            # 競馬ラボ結果取得
            #####################################
            if ridx < 9:
                race = "0" + str(ridx + 1) #ridx 0~8 = 1~9
            else:
                race = str(ridx + 1) #ridx 9~11 = 10~12

            url = url2 + race + "/"

            #res = requests.get(url)

            content = urlget.UrlRetry(url)
            # 競馬ラボがたまにレスポンス悪くて取れない時があるのでリトライを入れたいわけで。。。
            #res.encoding = res.apparent_encoding
            #content = res.text

            # ここから趣味の範囲 #####################################################
            #bs = BeautifulSoup(content, "lxml")
            #h1t = bs.find_all("h1", attrs={"class", "raceTitle fL"})
            #tmp = h1t[0].text
            #tmp = tmp.replace('\n','')
            #tmp = tmp.replace('\t','')
            #print(url, " : ", tmp)
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

            ridx += 1

            #CSV出力処理(競馬ラボ使用時)
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
        else:
            #CSV出力処理(競馬ラボ未使用時)
            if hoge != 0:
                #print("ヘッダーなし")
                #df2.to_csv(csvfile, encoding="shift_jis", header=False, index=False, mode="a")
                df2.to_csv(csvfile, encoding="shift_jis", header=False, index=False, mode="a")
                # CSV ファイル (employee.csv) として出力（追記モード）
            else:
                #print("ヘッダーあり")
                # hoge == 0の時だけヘッダー出力
                #df2.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")
                df2.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")

        hoge += 3

print('できた！')
