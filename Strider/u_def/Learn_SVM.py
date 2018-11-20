import requests
import pandas as pd
from bs4 import BeautifulSoup

# scikit-learn(機械学習用インポート)
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn import linear_model
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

# ユーザー関数
from u_def import JockeyTable as jtbl   # 騎手名→勝率変換用関数


################################################################
# 機械学習(SVM)実施関数                                        #
################################################################
def svm_func(l_DataName,test_DataFrame,factor_list):

    #####################################
    # 学習用データ準備                  #
    #####################################
    
    # 学習用データ読込み
    df = pd.read_csv(l_DataName, encoding="shift_jis")
    
    # 学習用データ選定
    df = df[ factor_list ]
    
    print("*****************************************************************************")
    print("学習用データ")
    print(df.head())  # 確認用出力
    print("*****************************************************************************")
    
    # 値の無い行、中止の行を削除
    df = df.dropna()
    df = df[df["着"] != "中止"]
    df = df[df["着"] != "除外"]
    
    # 標準化準備処理
    sc = StandardScaler()
    
    # 不要列削除
    x_dat = df.drop(columns=["着"])
    
    # 騎手名 → 勝率変換
    x_dat = jtbl.JockeyTable(x_dat)
    
    # データフレーム全体を浮動小数点型でキャスト
    x_dat = x_dat.astype('float64')
    
    # 標準化実施
    x_dat = pd.DataFrame(sc.fit_transform(x_dat))
    
    # 標準化後のサンプル表示
    print("学習用データ標準化")
    print(x_dat.head())
    print("*****************************************************************************")
    
    
    #####################################
    # 教師用データ準備                  #
    #####################################
    
    # 教師データ設定
    y_dat = df["着"]
    
    
    #####################################
    # 予想用データ準備                  #
    #####################################
    
    # 予想対象データ読込み
    df = test_DataFrame
    
    # 予想用データフレーム作成
    df_t = df[ factor_list ]
    df_t = df_t.drop(columns=["着"])   # 不要列削除
    
    # 騎手名 → 勝率変換
    test_X = jtbl.JockeyTable(df_t)
    
    # データフレーム全体を浮動小数点型でキャスト
    test_X = test_X.astype('float64')
    
    # 標準化実施
    test_X = pd.DataFrame(sc.fit_transform(test_X))
    
    # 標準化後のサンプル表示
    print("予想用データ標準化")
    print(test_X.head())
    print("*****************************************************************************")
    
    # 予想結果表示
    print("機械ちゃん 予想計算中...")
    print("*****************************************************************************")
    
    #####################################
    ######  ここから機械学習(SVM)  ######
    #####################################
    clf = SVC(C=1.0)
    clf.fit(x_dat, y_dat)
    pred_y = clf.predict(test_X)
    #####################################
    ######  ここまで機械学習(SVM)  ######
    #####################################
    
    # 予想結果をリターン
    return pred_y
