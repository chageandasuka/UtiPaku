import numpy as np
import pandas as pd 
from sklearn.datasets import load_boston
from sklearn.ensemble import RandomForestRegressor
from matplotlib import pyplot as plt

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

# ユーザー関数
from u_def import JockeyTable as jtbl   # 騎手名→勝率変換用関数


# 学習&教師用ファクターリスト
factor_list01 = [
                  "合計値順位",   #グループ1
                 
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

# 教師データ取得
data_y = learn_DataFrame[ "着" ]


# 森の深さ設定
depth_set = 15
# 森の数設定
n_estimators_set = 100

# ランダムフォレスト準備
rf1 = RandomForestRegressor( n_estimators = n_estimators_set, max_depth = depth_set )

print(data_x.head())
print(data_y.head())

# ランダムフォレスト学習
rf1.fit( data_x, data_y )

# ランダムフォレスト予想
test_X = test_DataFrame[ factor_list01 ]
test_X = jtbl.JockeyTable(test_X)            # 騎手名 → 勝率変換
result1 = rf1.predict( test_X )

print('check:',result1)

# CSVファイルへ結果出力
test_DataFrame['R予想'] = result1
test_DataFrame.to_csv("01_rslt_rnd.csv", encoding="shift_jis", index=False, mode="a")


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
