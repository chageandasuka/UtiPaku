# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import argparse
import chainer
from chainer import cuda, Function, gradient_check, Variable, optimizers, serializers, utils
from chainer import Link, Chain, ChainList#, FunctionSet
from chainer import training
from chainer.datasets import tuple_dataset
from chainer.training import extensions
import chainer.functions as F
import chainer.links as L
import pickle as P
from chainer.functions.loss.sigmoid_cross_entropy import sigmoid_cross_entropy
import pandas as pd

# Network definition
class MLP(chainer.Chain):

    def __init__(self, n_units, n_out):
        print(self, n_units, n_out)
        super(MLP, self).__init__(
            # the size of the inputs to each layer will be inferred
            l1=L.Linear(None, n_units),  # n_in -> n_units\
            l2=L.Linear(None, n_units),  # n_units -> n_units
            l3=L.Linear(None, n_units),  # n_units -> n_units
            l4=L.Linear(None, n_units),  # n_units -> n_units
            l5=L.Linear(None, n_out),  # n_units -> n_out
        )

    def __call__(self, x):
        h1 = F.relu(self.l1(x))
        h2 = F.relu(self.l2(h1))
        h3 = F.relu(self.l3(h2))
        h4 = F.relu(self.l4(h3))
        return self.l5(h4)


def main():
    parser = argparse.ArgumentParser(description='Chainer example: MNIST')
    parser.add_argument('--batchsize', '-b', type=int, default=100, help='Number of images in each mini-batch')
    parser.add_argument('--epoch', '-e', type=int, default=40, help='Number of sweeps over the dataset to train')
    parser.add_argument('--gpu', '-g', type=int, default=-1, help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--out', '-o', default='result', help='Directory to output the result')
    parser.add_argument('--resume', '-r', default='', help='Resume the training from snapshot')
    parser.add_argument('--unit', '-u', type=int, default=600, help='Number of units')
    args = parser.parse_args()

    print('GPU: {}'.format(args.gpu))
    print('# unit: {}'.format(args.unit))
    print('# Minibatch-size: {}'.format(args.batchsize))
    print('# epoch: {}'.format(args.epoch))
    print('')
    # まず同じネットワークのオブジェクトを作る
    model = L.Classifier(MLP(args.unit, 18))

    # そのオブジェクトに保存済みパラメータをロードする
    serializers.load_npz("my_mnist.npz", model) # "mymodel.npz"の情報をmodelに読み込む

    # 学習用に数値に変換する
    # とりあえずオリジナルのナンバーでやるけど。。。そのうち修正したい。
    dataMap = {
      1 : { "札幌": 0, "函館": 1, "福島": 2, "東京": 3, "中山": 4, "京都": 5, "新潟": 6, "阪神": 7, "中京": 8, "小倉": 9 },
      3 : { "芝" : 0, "ダ" : 1 , "障" : 2, "直" : 3},
    }
    ##学習用データの読み込み
    #そのうちリスト化してループする
    #fname = "00_test01.csv"
    fname_list = ["00_test01.csv", "00_test02.csv", "00_test03.csv", "00_test04.csv", "00_test05.csv", "00_test06.csv", "00_test07.csv", "00_test08.csv", "00_test09.csv", "00_test10.csv", "00_test11.csv", "00_test12.csv"]
    #fname_list = ["00_test11.csv"]
    for fname in fname_list:
        df = pd.read_csv(fname, encoding="shift_jis")
        # DateFlameの行列取得
        row, col = df.shape
        print("row = {}, col = {}".format(row, col))
        print(df.head())
        hedder_data = df.iloc[0,[1,3]]
        #print(hedder_data[0],hedder_data[1])
        for course_idx, course in enumerate(dataMap[1]):
            if course == hedder_data[0]:
                break
        #print(course_idx)
        for track_idx, track in enumerate(dataMap[3]):
            if track == hedder_data[1]:
                break
        #print(track_idx)

        #出力用にコピー
        dfcpy = df

        # 行数18未満ならゼロ埋め
        idx = 0
        for idx in range(row, 18):
            df.loc[idx] = -1
        # End of for

        diff = 18 - row
        print(diff)

        yyyymmdd = df.iloc[0,0]
        tmp = df["馬番"]
        #df = df[["馬番", "先行力", "追走力", "持久力", "持続力", "瞬発力", "ＳＴ指数", "仕上指数", "合計値", "合計値順位", "基準人気順位", "基準オッズ"]]
        df = df[["馬番", "展開順位", "展開ゴール差", "先行力", "追走力", "持久力", "持続力", "瞬発力", "ＳＴ指数", "仕上指数", "合計値", "合計値順位", "基準人気順位"]]
        #入力データをnumpy配列に変更
        data = np.array([course_idx, track_idx], dtype=np.float32)
        #data = float32(data)
        dfary = np.array(df.iloc[:,:]).astype(np.float32)
        #print(dfary)
        data = np.append(data, dfary)
        print("data length={}".format(len(data)))
        #print(data)
        data = data.reshape(1,len(data))
        #print(data)
        #ここです！
        #予測後の出力ノードの配列を作成
        outputArray = model.predictor(data).data
        #print(outputArray)
        outputArray = outputArray.reshape(18,1)
        #出力ノードの値のデータフレーム版を作成

        outputDF = pd.DataFrame(outputArray[0:18-diff],columns=["機械"])
        #outputDF = outputDF[0:18-diff]
        #outputDF = pd.DataFrame(outputArray,columns=["機械"])
        #print(outputDF)
        outputDF["予想着順"] = outputDF["機械"].rank(ascending=False, method='min')
        outputDF["馬番"] = tmp


        cols = list(outputDF.columns.values)
        cols = ['馬番']+ [col for col in outputDF if col != '馬番']
        outputDF = outputDF[cols]

        dfcpy["予想着順"] = outputDF["予想着順"]
        #print(str(yyyymmdd))
        dfcpy.to_csv(str(yyyymmdd) + "_DL.csv", encoding="shift_jis", index=False, mode="a")

if __name__ == '__main__':
    main()
