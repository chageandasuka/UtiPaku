import requests
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import JockeyTable as jtbl
import pandas as pd
from bs4 import BeautifulSoup

from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn import linear_model
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler



##学習用データの読み込み
fname = "00_LearnData.csv"
df = pd.read_csv(fname, encoding="shift_jis")
#print(df.head())

print(df.info())
df = df[[
            #"騎手名",
            "展開順位",
            "展開ゴール差",
            "瞬発力",
            "瞬発力順位",
            "仕上指数",
            "ＳＴ指数順位",
            "仕上指数順位",
            "着",
            "人",
            "単勝"
       ]]
#print(df.head())

# 値の無い行、中止の行を削除
df = df.dropna()
df = df[df["着"] != "中止"]
df = df[df["着"] != "除外"]
#print(df["着"])
#print(df.info())
#print("********************")

####df["基準オッズ"] = df["基準オッズ"] * 10
####df["単勝"] = df["単勝"].astype("float64") * 10
#print(df["単勝"])
####df = df.astype('int16')

#標準化テスト
sc = StandardScaler()
#data_std = sc.fit_transform(df)
#print('*************************************')
#print(pd.DataFrame(data_std))
#print('*************************************')
#print(df.info())
cols = df.columns.tolist()
#print(cols)

# 不要列削除
x_dat = df.drop(columns=["着", "人", "単勝"])

# 騎手名 → 数値変換
x_dat = jtbl.JockeyTable(x_dat)
print(x_dat.head())

# float64へキャスト
x_dat = x_dat.astype('float64')

x_dat = pd.DataFrame(sc.fit_transform(x_dat))
y_dat = df["着"]

print(x_dat.head())
print(y_dat.head())

###############################################################################
# テストデータ入力
#df = pd.read_csv("00_test01.csv", encoding="shift_jis")

for lp in range(1, 13):
    df = pd.read_csv("00_test" + str(lp).zfill(2) + ".csv", encoding="shift_jis")
    print(lp)
    print(df.head())
    # テストデータには結果列無いよ
    df_t = df[[
                #"騎手名",
                "展開順位",
                "展開ゴール差",
                "瞬発力",
                "瞬発力順位",
                "仕上指数",
                "ＳＴ指数順位",
                "仕上指数順位"
             ]]

    # 騎手名 → 数値変換
    test_X = jtbl.JockeyTable(df_t)

    #####df["基準オッズ"] = df["基準オッズ"] * 10
    test_X = test_X.astype('float64')
    test_X = pd.DataFrame(sc.fit_transform(test_X))
    print(test_X.head())

    ###### ここから機械学習
    clf = SVC(C=1.0)
    clf.fit(x_dat, y_dat)

    pred_y = clf.predict(test_X)
    print("予測結果",pred_y)
    df['予想'] = pred_y
    print(df.head())
    df.to_csv("01_rslt.csv", encoding="shift_jis", index=False, mode="a")
#print(accuracy_score(y_dat,pred_y))

#cat_var = rdat.dtypes.loc[rdat.dtypes=='object'].index
#print(cat_var)
