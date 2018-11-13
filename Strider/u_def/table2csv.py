import os, csv


def table2csv(path, rows, lineterminator="\n",
    is_talkative=True):
    """二次元データをCSVファイルに書き込む"""

    # 安全な方に転ばせておく
    if os.path.exists(path):
        emsg = "%s already exists." % path
        raise ValueError(emsg)

    # データを書き込む
    with open(path, "w") as f:
        writer = csv.writer(f, lineterminator=lineterminator)
        writer.writerows(rows)
        if is_talkative:
            print("%s successfully saved." % path)
