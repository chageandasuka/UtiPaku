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

# 競馬ラボ用
from u_def import keibaLab_CourseTable as klabtbl
from u_def import UrlRetry as urlget


# HTML データを取得する
inurl = input('データシートURL >> ')
URL_BASE = "https://stride.get-luck.jp/member/"
# 競馬ラボのURL
CNST_LABURL = "https://www.keibalab.jp/db/race/"

################################################################################
def GetSoup(url):
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    content = res.text
    soup = BeautifulSoup(res.content, 'html.parser')

    return soup, content

# 引数( DataFrame, List )
def MoveCol(dmy_df, col_list):
    cols = list(dmy_df.columns.values) # 全列名リスト化
    for col_name in col_list:
        cols.remove(col_name)          # リストから並び替え対象を削除
    cols = col_list + cols             # リストへ並び替え対象を追加
    dmy_df = dmy_df[cols]              # 並び替え実施
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
#csvfile = race_date[0] + '_StridViewer.csv'
csvfile = 'StridViewer.csv'

h_flg = 0 # 最初の書き込みのみヘッダを出すためのフラグ

df_SV = pd.DataFrame()
# 各リンク先データの取得
for member in link_list:
    soup, content = GetSoup(URL_BASE + member)

    race_name = soup.find_all('p', attrs={'class', "race_name"})
    print("  {}".format(race_name[0].text))
    race_detail = soup.find_all('p', attrs={'class', "race_detail"})

    # テキスト取得
    rd_txt = race_detail[0].text

    # コース
    if 0 < len(re.findall('ダート', rd_txt)):
        cource = 'ダート'
    elif 0 < len(re.findall('芝', rd_txt)):
        cource = '芝'
    else:
        cource = '障害'

    if cource != '障害':
        # 会場
        kaijou = race_name[0].text[0:2]

        # 距離
        distance = re.findall('([0-9]{4})m', rd_txt)
        distance = distance[0]

        # クラス
        if ( True == ( '未勝利' in race_name[0].text ) ):
            race_class = '未勝利'
        elif ( True == ( '500万' in race_name[0].text ) ):
            race_class = '500万'
        elif ( True == ( '1000万' in race_name[0].text ) ):
            race_class = '1000万'
        elif ( True == ( '1600万' in race_name[0].text ) ):
            race_class = '1600万'
        else:
            race_class = '特別'

        # print(race_class)

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
                # 展開->外厩->競走馬詳細->調教->直前情報->レース結果 取得
                t_df = pd.DataFrame(rows[1:], columns=rows[0])
                
                # レース結果テーブルには'バイアス'列が2つ存在する為リネーム
                if ( True == ( 'バイアス' in t_df.columns.values ) ):
                    col = t_df.columns.values                                       # 全体の列名を取得
                    col[18] = '直線バイアス'                                        # 一部を加工 ※[18]はマジックNo
                    col[20] = '脚質バイアス'                                        # 一部を加工 ※[20]はマジックNo
                    t_df.columns = col                                              # 加工した列名を戻す
                
                # データ結合
                cols_to_use = t_df.columns.difference(df_race.columns)              # 同名列の衝突回避(df_raceデータを優先する)
                cols_to_use = list( cols_to_use.values )                            # objectタイプ→リスト化
                cols_to_use.insert(0, '馬番' )                                      # 結合用の軸データはリストとして再付与する
                df_race = pd.merge( df_race, t_df[cols_to_use], how='outer', on='馬番' )  # 馬番を軸に結合
            else:
                # 基本 取得
                df_race = pd.DataFrame(rows[1:], columns=rows[0])

        # レース情報の付与
        df_race['日付'] = race_date[0]
        df_race['距離'] = distance
        df_race['コース'] = cource
        df_race['レース'] = race_num
        df_race['会場'] = kaijou
        df_race['クラス'] = race_class
        
        # 引数['C','B','A']はA->B->Cの順に並び変え
        df_race = MoveCol( df_race, ['日付','レース','会場','距離','コース','クラス'] )

        # %表記データを数字に変換する。
        # データなしは0にする。
        df_race['出遅率']             = df_race['出遅率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['厩舎×外厩勝率']     = df_race['厩舎×外厩勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['厩舎×外厩連対率']   = df_race['厩舎×外厩連対率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['厩舎×外厩複勝率']   = df_race['厩舎×外厩複勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['馬×外厩勝率']       = df_race['馬×外厩勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['馬×外厩連対率']     = df_race['馬×外厩連対率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['馬×外厩複勝率']     = df_race['馬×外厩複勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['コース×厩舎勝率']   = df_race['コース×厩舎勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['コース×厩舎連対率'] = df_race['コース×厩舎連対率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['コース×厩舎複勝率'] = df_race['コース×厩舎複勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['調教P×厩舎勝率']    = df_race['調教P×厩舎勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['調教P×厩舎連対率']  = df_race['調教P×厩舎連対率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['調教P×厩舎複勝率']  = df_race['調教P×厩舎複勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['血統×条件勝率']     = df_race['血統×条件勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['血統×条件連対率']   = df_race['血統×条件連対率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['血統×条件複勝率']   = df_race['血統×条件複勝率'].replace('%', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race = df_race.replace('', '0')

        # 馬名の全空白を削除
        df_race['馬名']   = df_race['馬名'].replace('　', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(str)

        # 先行力:47(10)等の順位情報(10)を削除
        df_race['先行力']   = df_race['先行力'].replace('\(.*\)', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['持久力']   = df_race['持久力'].replace('\(.*\)', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['持続力']   = df_race['持続力'].replace('\(.*\)', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['瞬発力']   = df_race['瞬発力'].replace('\(.*\)', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)
        df_race['追走力']   = df_race['追走力'].replace('\(.*\)', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)

        # 順位情報追加
        df_race['先行力順位'] = df_race['先行力'].rank(ascending=False, method='min')
        df_race['追走力順位'] = df_race['追走力'].rank(ascending=False, method='min')
        df_race['持久力順位'] = df_race['持久力'].rank(ascending=False, method='min')
        df_race['持続力順位'] = df_race['持続力'].rank(ascending=False, method='min')
        df_race['瞬発力順位'] = df_race['瞬発力'].rank(ascending=False, method='min')
        df_race['ST指数順位'] = df_race['ST指数'].rank(ascending=False, method='min')
        df_race['仕上指数順位'] = df_race['仕上指数'].rank(ascending=False, method='min')

        # 馬体重の増減情報を削除
        df_race['馬体重']   = df_race['馬体重'].replace('\(.*\)', '', regex=True).replace(' ', '').replace('', '0', regex=True).astype(int)

        if len(df_SV) > 0:
            df_SV = pd.concat([df_SV, df_race])
        else:
            df_SV = df_race

        #print(df.shape)

    else:
        #print('森キュンがんばれ～')
        continue

################################################################################

    #print('****ラボデータ取得開始')
    #####################################
    # 競馬ラボ結果取得
    #####################################
    
    # レースNo.取得
    race_num_str = race_num.replace('R','')

#    if ridx < 9:
#        race_num_str = "0" + str(ridx + 1) #ridx 0~8 = 1~9
#    else:
#        race_num_str = str(ridx + 1) #ridx 9~11 = 10~12

    course = df_race['会場'].loc[0]

    course_no = klabtbl.keibaLab_CourseTables(course)
    # 会場IDを数字で戻すようにしたためここで数字→文字列に変換して2桁表示
    course_no = str(course_no + 1).zfill(2)
    #print("  会場 = {}, 会場ID = {}".format(course, course_no))

    # 競馬ラボURL作成
    url = CNST_LABURL + race_date[0] + course_no + race_num_str + "/"

    content = urlget.UrlRetry(url)

    # table 要素を取得する
    lab_tables = gtbl.get_tables(content)
    # table 要素の先頭が結果
    rows = ptbl.parse_table(lab_tables[0])
    # 列名だけのDataFrameを作成
    tmp = rows[0]
    df = pd.DataFrame(index=[], columns=tmp[0:15])
    # 行追加
    # タイトル行以外のデータをコピー
    rows_new = rows[1:]
    # 添え字初期化
    idx = 0
    for n in rows_new:
        df.loc[idx] = n[0:15]
        idx += 1
    
    # 払い戻し情報取得
    rows2 = ptbl.parse_table(lab_tables[1])
    
    # 複勝払い戻し取得
    idx = 0
    for n in rows2[0]:
        if '複勝' == n:
            # 複勝情報生値
            huku_yen = rows2[0][idx+2].replace(',','')
            huku_yen = re.split('円', huku_yen)
        idx += 1
    
    # 単勝の列データを値で取得
    odds_v = df['単勝'].values
    # データフレームをカンマ区切り変換
    tmp = ",".join(odds_v)
    tmp = tmp.replace('\n','')
    tmp = tmp.replace('\t','')
    # カンマ区切りをデータフレーム用へ変換
    odds_new = tmp.split(",")
    # DataFrameへ書き戻し
    lp = 0
    idx = 0
    for dmy in odds_new:
        # dmy=配列の中身を順に格納
        df.at[lp, '単勝'] = dmy
        
        # 複勝用分岐
        if 0 == lp:    # 1着
            df.at[lp, '複勝'] = float(huku_yen[idx])/100
            idx = lp + 1
        elif  1 == lp: # 2着
            df.at[lp, '複勝'] = float(huku_yen[idx])/100
            idx = lp + 1
        elif  2 <= lp: # 3着以降
            if '' != huku_yen[idx]:
                df.at[lp, '複勝'] = float(huku_yen[idx])/100
                idx = lp + 1
            else:
                df.at[lp, '複勝'] = 0
        else:
            print('想定外エラー(複勝)')
            sys.exit()
        # 次のループへ
        lp += 1
    
    # タイムの列データを変換
    time_v = df['タイム'].values
    # データフレームをカンマ区切り変換
    tmp = ",".join(time_v)
    # 改行の削除
    tmp = tmp.replace('\n','')
    # tabの削除
    tmp = tmp.replace('\t','')
    # カンマ区切りをデータフレーム用へ変換
    time_new = tmp.split(",")
    
    # DataFrameへ書き戻し
    lp = 0
    time_sub = 0
    for dmy in time_new:
        
        # タイムを秒に変換
        if '1:' in dmy:
            dmy = dmy.replace('1:','')
            dmy = float( dmy ) + 60
        elif '2:' in dmy:
            dmy = dmy.replace('2:','')
            dmy = float( dmy ) + 120
        elif '3:' in dmy:
            dmy = dmy.replace('3:','')
            dmy = float( dmy ) + 180
        elif '0:' in dmy:
            dmy = dmy.replace('0:','')
            dmy = float( dmy )
        elif '' == dmy:
            dmy = '中止等'
        else:
            print('想定外エラー(タイム)')
            sys.exit()
        
        # dmy=配列の中身を順に格納
        df.at[lp, 'タイム'] = dmy
        
        if 0 == lp: # 1着時着差(更新しない)
            time_sub = dmy
        elif  1 == lp: # 2着時着差(1着2着を更新)
            df.at[0, '着差'] = time_sub - dmy
            df.at[1, '着差'] = dmy - time_sub
        elif  2 <= lp: # 3着以降時着差(該当着のみ更新)
            if '中止等' != dmy:
                df.at[lp, '着差'] = dmy - time_sub
            else:
                df.at[lp, '着差'] = '中止等'
        else:
            print('想定外エラー(着差)')
            sys.exit()
        
        # 次のループへ
        lp += 1
    
    # 上りの列データを変換(空白はダミー値:999)
    df['上り'] = df['上り'].apply( lambda x: '999' if '' == x else x )
    agari_v = df['上り'].values
    # データフレームをカンマ区切り変換
    tmp = ",".join(agari_v)
    # 改行の削除
    tmp = tmp.replace('\n','')
    # tabの削除
    tmp = tmp.replace('\t','')
    # カンマ区切りをデータフレーム用へ変換
    agari_new = tmp.split(",")
    # 上り最速を取得(浮動小数点化含む)
    agari_min = min( [float(x) for x in agari_new] )
    
    # DataFrameへ書き戻し
    lp = 0
    for dmy in agari_new:
        
        # 上り最速からの差
        df.at[lp, '上り差'] = agari_min - float(dmy)
        # 次のループへ
        lp += 1
        
    
    # 通過順の列データを変換
    tuka_v = df['通過順'].values
    # データフレームをカンマ区切り変換
    tmp = ",".join(tuka_v)
    # 改行の削除
    tmp = tmp.replace('\n','')
    # tabの削除
    tmp = tmp.replace('\t','')
    # カンマ区切りをデータフレーム用へ変換
    tuka_new = tmp.split(",")
    
    # DataFrameへ書き戻し
    lp = 0
    time_sub = 0
    for dmy in tuka_new:
        
        # 〇文字を数字に変換
        if '①' in dmy:
            dmy = dmy.replace('①','1,')
        if '②' in dmy:
            dmy = dmy.replace('②','2,')
        if '③' in dmy:
            dmy = dmy.replace('③','3,')
        if '④' in dmy:
            dmy = dmy.replace('④','4,')
        if '⑤' in dmy:
            dmy = dmy.replace('⑤','5,')
        if '⑥' in dmy:
            dmy = dmy.replace('⑥','6,')
        if '⑦' in dmy:
            dmy = dmy.replace('⑦','7,')
        if '⑧' in dmy:
            dmy = dmy.replace('⑧','8,')
        if '⑨' in dmy:
            dmy = dmy.replace('⑨','9,')
        if '⑩' in dmy:
            dmy = dmy.replace('⑩','10,')
        if '⑪' in dmy:
            dmy = dmy.replace('⑪','11,')
        if '⑫' in dmy:
            dmy = dmy.replace('⑫','12,')
        if '⑬' in dmy:
            dmy = dmy.replace('⑬','13,')
        if '⑭' in dmy:
            dmy = dmy.replace('⑭','14,')
        if '⑮' in dmy:
            dmy = dmy.replace('⑮','15,')
        if '⑯' in dmy:
            dmy = dmy.replace('⑯','16,')
        if '⑰' in dmy:
            dmy = dmy.replace('⑰','17,')
        if '⑱' in dmy:
            dmy = dmy.replace('⑱','18,')
        
        # 脚質判定用の4角位置取得
        kyakusitu_num = dmy[(len(dmy)-3):(len(dmy)-1)]
        kyakusitu_num = kyakusitu_num.replace(',','')
        df.at[lp, '4角順'] = kyakusitu_num
        
        # 脚質判定
        if '' == df.at[lp, '4角順']:
            df.at[lp, '脚質(4角)'] = '判定不可'
        elif 1 >= float( df.at[lp, '4角順'] ):
            df.at[lp, '脚質(4角)'] = '逃げ'
        elif 4 >= float( df.at[lp, '4角順'] ):
            df.at[lp, '脚質(4角)'] = '先行'
        elif 8 >= float( df.at[lp, '4角順'] ):
            df.at[lp, '脚質(4角)'] = '差し'
        else:
            df.at[lp, '脚質(4角)'] = '追込'
        
        # dmy=配列の中身を順に格納
        if '' != dmy:
            df.at[lp, '通過順'] = dmy
        else:
            df.at[lp, '通過順'] = '計測不能'
        
        # 次のループへ
        lp += 1
        
    # 必要そうなデータだけを抽出
    # df = df[['馬','馬名', 'タイム', '通過順', '4角順', '上り', '上り差', '脚質(4角)', '着差', '斤量', '調教師', '着', '人', '単勝', '複勝']]
    df = df[['馬','馬名', 'タイム', '通過順', '4角順', '上り', '上り差', '脚質(4角)', '着差', '斤量', '調教師', '着', '人', '単勝', '複勝']]
    df['馬'] = df['馬'].astype(str).str.zfill(2)
    df = df.rename(columns={'馬': '馬番'})
    df = df.rename(columns={'馬名': '馬名2'})

    # データ結合
    cols_to_use = df.columns.difference(df_race.columns)                 # 同名列の衝突回避(df_raceデータを優先する)
    cols_to_use = list( cols_to_use.values )                             # objectタイプ→リスト化
    cols_to_use.insert(0, '馬番' )                                       # 結合用の軸データはリストとして再付与する

    df_merge = df_race[ df_race['レース'] == race_num ]
    df_merge = df_merge[ df_merge['会場'] == kaijou ]
    df3 = pd.merge( df_merge, df[cols_to_use], how='outer', on='馬番' )  # 馬番を軸に結合
    df3 = df3[ df3['レース'] == race_num ]                               # 取消馬等の差分(ストライド無・競馬ラボ有)を削除
##########################################################################
    if h_flg == 1:
        #print("ヘッダーなし")
        df3.to_csv(csvfile, encoding="shift_jis", header=False, index=False, mode="a")
        # CSV ファイル (employee.csv) として出力（追記モード）
    else:
        #print("ヘッダーあり")
        # hoge == 0の時だけヘッダー出力
        df3.to_csv(csvfile, encoding="shift_jis", index=False, mode="a")
        h_flg = 1

#exit()
#df_SV = df_SV.drop([''], axis=1)
#df_SV.to_csv(csvfile, encoding='shift_jis', index=False, mode='w')
