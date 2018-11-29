import numpy as np
import pandas as pd 
from sklearn.datasets import load_boston
from sklearn.ensemble import RandomForestRegressor
from matplotlib import pyplot as plt

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

# ユーザー関数
from u_def import JockeyTable as jtbl   # 騎手名→勝率変換用関数


# 事前/直前ファクター切替 (0：事前, 1：直前)
sw_Tyokuten = 1

if sw_Tyokuten == 0:

    # 学習&教師用ファクターリスト
    factor_list01 = [
    #                 "合計値順位",   #グループ1    # 該当ファクターは影響力強すぎの為、コメントアウト
                     
                      "仕上指数順位", #グループ2
                      "ＳＴ指数順位", #グループ2
                     
                      "合計値",       #グループ3
                      "展開順位",     #グループ3
                    
                      "展開ゴール差", #グループ4
                      "瞬発力順位",   #グループ4
                      "ＳＴ指数",     #グループ4
                      "仕上指数",     #グループ4
                      
                      "持続力順位",   #グループ5
                      "瞬発力",       #グループ5
                      "騎手名",       #グループ5
                      "先行力順位",   #グループ5
                      "持久力",       #グループ5
                      "先行力",       #グループ5
                      "追走力",       #グループ5
                      "持続力",       #グループ5
                      "持久力順位",   #グループ5
                      "追走力順位"    #グループ5
                    ]
else:
    factor_list01 = [
                      "直前印",
                      "前日印",
                      "指数印",
                      "激走馬",
                      "脚質(前走)",
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


print("データ準備中...")
# 学習用CSV名設定
l_DataName = "00_LearnData.csv"
# 予想用CSV名設定
t_DataName = "00_test01.csv"

# 学習用データフレーム(ベース)
learn_DataFrame = pd.read_csv(l_DataName, encoding="shift_jis")
# 予想結果CSV出力用データ読込み(ベース)
test_DataFrame = pd.read_csv(t_DataName, encoding="shift_jis")

# 不要行を削除
learn_DataFrame = learn_DataFrame[ learn_DataFrame["着"] != "中止" ]                             # 中止行削除
learn_DataFrame = learn_DataFrame[ learn_DataFrame["着"] != "除外" ]                             # 除外行削除
learn_DataFrame = learn_DataFrame[ learn_DataFrame["着"] != "取消" ]                             # 取消行削除


# 学習データ取得
data_x = learn_DataFrame[ factor_list01 ]
data_x = jtbl.JockeyTable(data_x)            # 騎手名 → 勝率変換
data_x = data_x.astype('float64')            # データフレーム全体を浮動小数点型でキャスト

# 教師データ取得
data_y = learn_DataFrame[ "着" ]
data_y = data_y.astype('float64')            # データフレーム全体を浮動小数点型でキャスト


# 森の深さ設定 (設定なしの場合最大深度まで実施)
depth_set = 15

# 森の数設定
n_estimators_set = 100

# ランダムフォレスト準備
rf1 = RandomForestRegressor( n_estimators = n_estimators_set, max_depth = depth_set )

print("学習1回目")
########################################################################################
# 学習1回目
########################################################################################
# ランダムフォレスト学習
rf1.fit( data_x, data_y )

# ランダムフォレスト予想
test_X = test_DataFrame[ factor_list01 ]
test_X = jtbl.JockeyTable(test_X)            # 騎手名 → 勝率変換
result1 = rf1.predict( test_X )
# CSVファイルへ結果出力
test_DataFrame['R予想1'] = result1


print("学習2回目")
########################################################################################
# 学習2回目
########################################################################################
# ランダムフォレスト学習
rf1.fit( data_x, data_y )

# ランダムフォレスト予想
test_X = test_DataFrame[ factor_list01 ]
test_X = jtbl.JockeyTable(test_X)            # 騎手名 → 勝率変換
result1 = rf1.predict( test_X )
# CSVファイルへ結果出力
test_DataFrame['R予想2'] = result1


print("学習3回目")
########################################################################################
# 学習3回目
########################################################################################
# ランダムフォレスト学習
rf1.fit( data_x, data_y )

# ランダムフォレスト予想
test_X = test_DataFrame[ factor_list01 ]
test_X = jtbl.JockeyTable(test_X)            # 騎手名 → 勝率変換
result1 = rf1.predict( test_X )

# CSVファイルへ結果出力
test_DataFrame['R予想3'] = result1


print("学習4回目")
########################################################################################
# 学習4回目
########################################################################################
# ランダムフォレスト学習
rf1.fit( data_x, data_y )

# ランダムフォレスト予想
test_X = test_DataFrame[ factor_list01 ]
test_X = jtbl.JockeyTable(test_X)            # 騎手名 → 勝率変換
result1 = rf1.predict( test_X )

# CSVファイルへ結果出力
test_DataFrame['R予想4'] = result1


print("学習5回目")
########################################################################################
# 学習5回目
########################################################################################
# ランダムフォレスト学習
rf1.fit( data_x, data_y )

# ランダムフォレスト予想
test_X = test_DataFrame[ factor_list01 ]
test_X = jtbl.JockeyTable(test_X)            # 騎手名 → 勝率変換
result1 = rf1.predict( test_X )

# CSVファイルへ結果出力
test_DataFrame['R予想5'] = result1



# 評価補助用マスク処理
# ◎は1に、〇は2に、△は3に、それ以下は4に置換
# test_DataFrame['単勝(Mask)']   = test_DataFrame.apply( lambda x: 2 if float( x['単勝'] ) < 2
#                                                             else 1 if float( x['単勝'] ) <= 5
#                                                             else 3 if float( x['単勝'] ) <= 10
#                                                             else 4, axis=1 )
test_DataFrame['R予想1(Mask)'] = test_DataFrame.apply( lambda x: 1 if float( x['R予想1'] ) < 3
                                                            else 2 if float( x['R予想1'] ) < 4
                                                            else 3 if float( x['R予想1'] ) < 5
                                                            else 4, axis=1 )
test_DataFrame['R予想2(Mask)'] = test_DataFrame.apply( lambda x: 1 if float( x['R予想2'] ) < 3
                                                            else 2 if float( x['R予想2'] ) < 4
                                                            else 3 if float( x['R予想2'] ) < 5
                                                            else 4, axis=1 )
test_DataFrame['R予想3(Mask)'] = test_DataFrame.apply( lambda x: 1 if float( x['R予想3'] ) < 3
                                                            else 2 if float( x['R予想3'] ) < 4
                                                            else 3 if float( x['R予想3'] ) < 5
                                                            else 4, axis=1 )
test_DataFrame['R予想4(Mask)'] = test_DataFrame.apply( lambda x: 1 if float( x['R予想4'] ) < 3
                                                            else 2 if float( x['R予想4'] ) < 4
                                                            else 3 if float( x['R予想4'] ) < 5
                                                            else 4, axis=1 )
test_DataFrame['R予想5(Mask)'] = test_DataFrame.apply( lambda x: 1 if float( x['R予想5'] ) < 3
                                                            else 2 if float( x['R予想5'] ) < 4
                                                            else 3 if float( x['R予想5'] ) < 5
                                                            else 4, axis=1 )


print("CSV出力")
print("*****************************************************************************")
########################################################################################
# CSV出力
########################################################################################
if sw_Tyokuten == 0:
    test_DataFrame.to_csv("01_rslt_rnd_Pre.csv", encoding="shift_jis", index=False, mode="a")
else:
    test_DataFrame.to_csv("01_rslt_rnd_Now.csv", encoding="shift_jis", index=False, mode="a")


# print('check:',result1)


########################################
######  ここから特徴量重要度出力  ######
########################################

#特徴量の重要度を上から順に取得する
feature = rf1.feature_importances_
f = pd.DataFrame({'number': range(0, len(feature)),'feature': feature[:]})
f2 = f.sort_values('feature',ascending=False)
f3 = f2.loc[:, 'number']

#特徴量の名前取得
label = data_x.columns[0:]

#特徴量の重要度順ターミナル出力(降順)
indices = np.argsort(feature)[::-1]

for i in range(len(feature)):
    print (str(i + 1) + "   " + str(label[indices[i]]) + "   " + str(feature[indices[i]]))

#特徴量の重要度順プロット出力(日本語は文字化け)
plt.title('Feature Importance')
plt.bar(range(len(feature)),feature[indices], color='lightblue', align='center')
plt.xticks(range(len(feature)), label[indices], rotation=90)
plt.xlim([-1, len(feature)])
plt.tight_layout()
plt.show()
