from bs4 import BeautifulSoup as BS

def get_tables(content, is_talkative=True):
    """table要素を取得する"""
    bs = BS(content, "lxml")
    tables = bs.find_all("table")
    n_tables = len(tables)
    if n_tables == 0:
        emsg = "table not found."
        raise Exception(emsg)
    if is_talkative:
        print("%d table tags found.." % n_tables)
    return tables
