import requests
from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import table2csv as tbl2csv
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn import linear_model
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler


aaa = 0


##学習用データの読み込み
fname = "00_LearnData.csv"
df = pd.read_csv(fname, encoding="shift_jis")
#print(df.head())

print(df.info())
df = df[["基準オッズ", "基準人気順位", "展開順位", "先行力", "追走力", "持久力", "持続力",
 "瞬発力", "ＳＴ指数", "仕上指数", "着", "人", "単勝"]]
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
df = df.astype('float64')

#標準化テスト
sc = StandardScaler()
#data_std = sc.fit_transform(df)
#print('*************************************')
#print(pd.DataFrame(data_std))
#print('*************************************')
#print(df.info())
cols = df.columns.tolist()
#print(cols)
x_dat = df.drop(columns=["着", "人", "単勝"])
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
    df_t = df[["基準オッズ", "基準人気順位", "展開順位", "先行力", "追走力", "持久力", "持続力",
     "瞬発力", "ＳＴ指数", "仕上指数"]]

    #####df["基準オッズ"] = df["基準オッズ"] * 10
    #test_X = df.astype('int16')
    test_X = df_t.astype('float64')
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


if aaa == 1:
    # HTML データを取得する
    url = "https://stride.get-luck.jp/member/lap_character/2018/20181103/20181103E.html?idpm=72076a00a8f68388b3c0fcd3f2057c84"
    #url = input('>> ')
    #csvfile = input('hozon name>> ')
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    content = res.text
    tables = get_tables(content)

    for dmy in tables:
        rows = parse_table(dmy)
        if not rows[0]:
            continue
        df2 = pd.DataFrame(rows[1:], columns=rows[0])

        data = df2
        print(len(data))
        X = data.drop(['ラップ適性', 'ラップキャラ', '合計値', '合計値順位'], axis=1)
        print(X)
        #X = X.iloc[:,3:15]
        X = X.iloc[:,[8,11]]
        print(X)
        #Y = data['合計値順位']

        model1 = KMeans(n_clusters=len(data), random_state=1)
        #model = DecisionTreeClassifier(max_depth=3, random_state=0)
        #model.fit(X, Y)
        model1.fit(X)
        Y1 = model1.labels_
        #tmp = model.predict(X)
        print(Y1)
        X['何か'] = Y1
        print(X)
        X.to_csv("hoge.csv", encoding="shift_jis", index=False, mode="a")
