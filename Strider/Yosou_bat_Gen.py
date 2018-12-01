import numpy as np
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import sys
import codecs

from u_def import get_tables as gtbl
from u_def import parse_table as ptbl
from u_def import keibaLab_CourseTable as klabtbl
from u_def import UrlRetry as urlget
from u_def import get_tyokuten as getyoku

class DataGenerator:
    def __init__ (self):
        self.CNST_URL = 'https://stride.get-luck.jp/member/' # データシートのあるアドレスの固定文字列
        self.myurl = '' # 自分のストライドデータシートURL
        if not self.myurl:
            print("作成したいURLを設定してから使ってね！")
            sys.exit()
        self.myurl_year = re.findall('\/[0-9]{4}\/', self.myurl) # yyyy
        self.myurl_year = re.findall('[0-9]{4}', self.myurl_year[0]) # yyyy
        self.myurl_race_day = re.findall('\/[0-9]{8}\/', self.myurl) # yyyymmdd
        self.myurl_race_day = re.findall('[0-9]{8}', self.myurl_race_day[0]) # yyyymmdd
        self.myurl_idpm = re.findall('\.html.+', self.myurl) # idp=***

        self.wel = ['E', 'W', 'L']
        self.kaijou = []
        self.chara_url = []
        self.tyokuten_url = []

        self.file_name = '' # 出力ファイル名

    def read(self):
        # 3会場分のループ
        for s in self.wel:

            # 会場データシートURL生成
            #tmp_char_url = self.CNST_URL + 'lap_character/' + self.myurl_year[0] + '/' + self.myurl_race_day[0] + '/' + self.myurl_race_day[0] + s + self.myurl_idpm[0]
            tmp_char_url = "{}lap_character/{}/{}/{}{}{}".format( self.CNST_URL, self.myurl_year[0], self.myurl_race_day[0], self.myurl_race_day[0], s, self.myurl_idpm[0] )
            # データシートページ取得
            res = requests.get(tmp_char_url)
            htstcd = res.status_code
            # HTTPステータスコード 404
            if  htstcd == 404:
                print("{} : Not Found @ {}{}".format(str(htstcd), self.myurl_race_day[0], s))
                continue
            else:
                self.chara_url = np.append(self.chara_url, tmp_char_url)


            res.encoding = res.apparent_encoding
            content = res.text
            soup = BeautifulSoup(content, 'lxml')

            race_str = soup.find_all("div", attrs={"class", "headding04"})
            race_str_text = race_str[0].text
            self.kaijou.append(race_str_text[2:4])

            tmp_tyokuten_url = []
            # データシートページのリンクを取得
            elems = soup.select('a')
            for elem in elems:
                if elem.getText() == "直前":
                    tmp = elem.get('href')
                    tmp = tmp.replace('../', '')
                    tmp_tyokuten_url = np.append(tmp_tyokuten_url, self.CNST_URL + tmp) # 縦方向で結合

            self.tyokuten_url.append(tmp_tyokuten_url) # 横方向で結合[0,1,2]

        pass


def main():
    loader = DataGenerator()
    loader.read()

    # 作成
    for i, chara_url in enumerate(loader.chara_url):
        for j, tyokuten_url in enumerate(loader.tyokuten_url[i]):
            print("会場{}-{}R\rデータシート：{}\r展開予想(直前)：{}".format(loader.wel[i], j+1, chara_url, tyokuten_url))

            # バッチファイル名生成（例：20181201E_01R.bat
            bat_fname = "{}{}_{}R.bat".format(loader.myurl_race_day[0], loader.kaijou[i], str(j+1).zfill(2))

            with codecs.open(bat_fname, 'w', 'shift_jis') as f:
                batheader = "cd /d %~dp0\n"
                batstr = "@python test_script.py " + chara_url + " " + tyokuten_url + " " + str(j+1) + "\n"
                batfutter = "pause\n"

                f.write(batheader)
                f.write(batstr)
                f.write(batfutter)
                f.close()

                print("Gen {}".format(bat_fname))



if __name__ == '__main__':
    main()
