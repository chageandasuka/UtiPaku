import sys
import subprocess
import Yosou_csv_Gen as ycg

# ラッパー関数的な役割
if __name__ == "__main__":
    print("run test_script.py")
    param = sys.argv
    # param[0]:このファイルの名前
    # param[1]:データシートURL
    # param[2]:直展URL
    # param[3]:レース番号
    #print("{}\r{}".format(param[1],param[2]))

    ans = ycg.Yosou_csv_Gen(param[1], param[2], int(param[3]))

    if ans == 1:
        print("*･゜ﾟ･*:.｡..｡.:*･゜乱森ちゃんランド開幕ﾟ･*:.｡. .｡.:*･゜ﾟ･*")
        cmd = 'python MachineLearning_RandomForest.py'
        subprocess.Popen(cmd.split())
    else:
        print("乱森ちゃんランドなんて無かったんや...")
