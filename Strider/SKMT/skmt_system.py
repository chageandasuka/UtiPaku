import csv
import sys
import requests
import re
import numpy as np
import pandas as pd
import subprocess

# horese_histroy.csvの使用切替
SW_H_HIST = 1

csv_file="meta_list.txt"

df = pd.read_csv(csv_file, encoding="shift_jis", header=None)
print(df.shape)

for r in range(0, len(df)):
    if SW_H_HIST == 1:
        comand = "python skmt_core.py -a lgbm -t race_train.csv -i horse_history.csv -m \"{}\" -r \"{}\"".format(df[0][r], df[1][r])
    elif:
        comand = "python skmt_core.py -a lgbm -t race_train.csv -m \"{}\" -r \"{}\"".format(df[0][r], df[1][r])

    print(comand)
    subprocess.call(comand)
