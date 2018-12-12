# SKMT system

# 内容物
# skmt_system.py
# skmt_meta_make.py
# skmt_core.py
# race_test.csv, race_train.csv


# 手順
 1. skmt_meta_make.pyを実行してストライドデータシートのURLを入力し、meta_list.txtを生成する。

 2. meta_list.txtが以下の形式で出力されているか確認する。
 　　中山|ダ|晴|1200|20181209,"パルセイティング|石川裕紀,...
 　　※金曜に実行すると天気が取得出来ない可能性が高い。その時は自力で埋めてください。

 3. meta_list.txtが問題なければ、skmt_system.pyを実行する。

 4. SKMTの答えは SKMT_RESULT.txt に出力される。

# その他
 skmt_system.py に定数SW「SW_H_HIST」があります。
 SKMTに馬の過去データを与えるか否かを切り替えるSWです。
 過去データを使うとSKMTの仕事は遅くなりますが、多少品質は向上するかもしれません。

# 参考情報 （2018/12/09 障害除く35レース）
 過去データを与えなかった場合
 SKMT　単回　複回
  1    161%  70%
  2     85%  83%

 過去データを与えた場合
 SKMT　単回　複回
  1     74%  46%
  2    143%  96%
