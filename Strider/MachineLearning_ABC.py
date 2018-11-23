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

# 学習用データフレーム(ベース)
learn_DataFrame = pd.read_csv(l_DataName, encoding="shift_jis")
# 予想結果CSV出力用データ読込み(ベース)
test_DataFrame = pd.read_csv(t_DataName, encoding="shift_jis")
## ダミー用に列を追加。この列は後で消す
test_DataFrame["着"] = 0

# 不要行を削除
# if learn_DataFrame["着"].str.endswith("中止").sum() > 0:                           # 中止文字有無判定
learn_DataFrame = learn_DataFrame[ learn_DataFrame["着"] != "中止" ]                             # 中止行削除
# if learn_DataFrame["着"].str.endswith("除外").sum() > 0:                           # 除外文字有無判定
learn_DataFrame = learn_DataFrame[ learn_DataFrame["着"] != "除" ]                             # 除外行削除
# if learn_DataFrame["着"].str.endswith("取消").sum() > 0:                           # 取消文字有無判定
learn_DataFrame = learn_DataFrame[ learn_DataFrame["着"] != "取消" ]                             # 取消行削除


sw_Kikaichang_Nomal = 1     # 機械ちゃんの通常処理 有効無効切り替えSW (1：有効 0：無効)
if sw_Kikaichang_Nomal == 1:

    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_list01 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['予想1'] = l_result

    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_list02 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['予想2'] = l_result

    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_list03 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['予想3'] = l_result

    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_list04 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['予想4'] = l_result

#######################################
######   ここから機械ちゃんの穴   ######
#######################################
sw_Kikaichang_ANAL = 0     # 機械ちゃんの穴処理 有効無効切り替えSW (1：有効 0：無効)
if sw_Kikaichang_ANAL == 1:

    factor_ANA_list01 = [
                          "瞬発力",
                          "瞬発力順位",
                          "仕上指数",
                          "ＳＴ指数順位",
                          "仕上指数順位",
                          #"単勝",
                          "着"
                        ]

    factor_ANA_list02 = [
                          "先行力",
                          "追走力",
                          "持久力",
                          "持続力",
                          "先行力順位",
                          "追走力順位",
                          "持久力順位",
                          "持続力順位",
                          #"単勝",
                          "着"
                        ]

    factor_ANA_list03 = [
                          "展開順位",
                          "展開ゴール差",
                          "合計値",
                          "合計値順位",
                          #"単勝",
                          "着"
                        ]

    factor_ANA_list04 = [
                          "騎手名",
                          "ＳＴ指数",
                          "ＳＴ指数順位",
                          "仕上指数",
                          "仕上指数順位",
                          #"単勝",
                          "着"
                        ]

# この処理はコメントアウトしたほうが成績が良くなる
#    # 不要行を削除
#    learn_DataFrame = learn_DataFrame[ learn_DataFrame.apply(lambda x:
#                                                             float( x["単勝"] ), axis=1) >= 10  ]   # 単勝10倍以下行削除
#    learn_DataFrame = learn_DataFrame[ learn_DataFrame.apply(lambda x:
#                                                             float( x["単勝"] ), axis=1) <= 100 ]   # 単勝100倍以上行削除

    # 1-3着は1に、4-6着は2に、7-9着は3に、それ以下は4に置換
    learn_DataFrame["着(複)"] = learn_DataFrame.apply( lambda x: 1 if float( x["着"] ) <= 3
                                                       else 2 if float( x["着"] ) <= 6
                                                       else 3 if float( x["着"] ) <= 9
                                                       else 4, axis=1 )
    learn_DataFrame["着"] = learn_DataFrame["着(複)"]

    print(learn_DataFrame.head())

    # 不要リスト削除
    #factor_ANA_list01.remove("単勝")   # 単勝ヘッダ削除

    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_ANA_list01 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['穴予想1'] = l_result


    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_ANA_list02 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['穴予想2'] = l_result


    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_ANA_list03 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['穴予想3'] = l_result


    # 機械学習実施(SVM)  (引数：学習用データフレーム, 予想用データフレーム, 学習&教師用ファクターリスト)
    l_result = lrn_svm.svm_func( learn_DataFrame, test_DataFrame, factor_ANA_list04 )
    # 予想欄としてデータフレームに追加(右端)
    test_DataFrame['穴予想4'] = l_result

    # ダミー列の削除
    test_DataFrame = test_DataFrame.drop(columns="着")

# CSVファイルへ結果出力
test_DataFrame.to_csv("01_rslt.csv", encoding="shift_jis", index=False, mode="a")

print( "できた！！" )
