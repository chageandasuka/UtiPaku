def parse_table(table):
    """table要素のデータを読み込んで二次元配列を返す"""

    ##### thead 要素をパースする #####

    # thead 要素を取得 (存在する場合)
    thead = table.find("thead")

    # thead が存在する場合
    if thead:
        tr = thead.find("tr")
        ths = tr.find_all("th")
        columns = [th.text for th in ths]    # pandas.DataFrame を意識

    # thead が存在しない場合
    else:
        columns = []

    ##### tbody 要素をパースする #####

    # tbody 要素を取得
    tbody = table.find("tbody")
    
    # tbody が存在する場合
    if tbody:
        # tr 要素を取得
        trs = tbody.find_all("tr")
        
        # 出力したい行データ
        rows = [columns]
        
        # td (th) 要素の値を読み込む
        # tbody -- tr 直下に th が存在するパターンがあるので
        # find_all(["td", "th"]) とするのがコツ
        for tr in trs:
            row = [td.text for td in tr.find_all(["td", "th"])]
            rows.append(row)
            
    # tbody が存在しない場合
    else:
        # 競馬ラボ 払い戻し取得を想定
        rows = []
        row = [td.text for td in table.find_all(["td"])]
        rows.append(row)

    return rows
