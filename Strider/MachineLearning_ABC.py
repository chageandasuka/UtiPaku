import requests
import pandas as pd
from bs4 import BeautifulSoup

# ユーザー関数
from u_def import Learn_SVM as lrn_svm   # 機械学習関数(SVM)

#####################################
# 複数予想出力処理                  #
#####################################

# 学習&教師用ファクターリスト
factor_list01 = [
                  "瞬発力",
                  "瞬発力順位",
                  "仕上指数",
                  "ＳＴ指数順位",
                  "仕上指数順位",
                  "着"
                ]

factor_list02 = [
                  "先行力",
                  "追走力",
                  "持久力",
                  "持続力",
                  "先行力順位",
                  "追走力順位",
                  "持久力順位",
                  "持続力順位",
                  "着"
                ]

factor_list03 = [
                  "展開順位",
                  "展開ゴール差",
                  "合計値",
                  "合計値順位",
                  "着"
                ]

factor_list04 = [
                  "騎手名",
                  "ＳＴ指数",
                  "ＳＴ指数順位",
                  "仕上指数",
                  "仕上指数順位",
                  "着"
                ]

# 学習用CSV名設定
l_DataName = "00_LearnData.csv"
# 予想用CSV名設定
t_DataName = "00_test01.csv"

# 予想結果CSV出力用データ読込み(ベース)
test_DataFrame = pd.read_csv(t_DataName, encoding="shift_jis")

# 機械学習実施(SVM)  (引数：学習用データ, 予想用データフレーム, 学習&教師用ファクターリスト)
l_result = lrn_svm.svm_func( l_DataName, test_DataFrame, factor_list01 )
# 予想欄としてデータフレームに追加(右端)
test_DataFrame['予想1'] = l_result

# 機械学習実施(SVM)  (引数：学習用データ, 予想用データフレーム, 学習&教師用ファクターリスト)
l_result = lrn_svm.svm_func( l_DataName, test_DataFrame, factor_list02 )
# 予想欄としてデータフレームに追加(右端)
test_DataFrame['予想2'] = l_result

# 機械学習実施(SVM)  (引数：学習用データ, 予想用データフレーム, 学習&教師用ファクターリスト)
l_result = lrn_svm.svm_func( l_DataName, test_DataFrame, factor_list03 )
# 予想欄としてデータフレームに追加(右端)
test_DataFrame['予想3'] = l_result

# 機械学習実施(SVM)  (引数：学習用データ, 予想用データフレーム, 学習&教師用ファクターリスト)
l_result = lrn_svm.svm_func( l_DataName, test_DataFrame, factor_list04 )
# 予想欄としてデータフレームに追加(右端)
test_DataFrame['予想4'] = l_result


# CSVファイルへ結果出力
test_DataFrame.to_csv("01_rslt.csv", encoding="shift_jis", index=False, mode="a")

print( "できた！！" )