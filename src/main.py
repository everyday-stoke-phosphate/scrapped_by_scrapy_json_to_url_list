#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd

"""
    プログラム全体の説明
    実行方法とか必要なライブラリとか
    動作確認しているPythonのバージョンとか
"""


def main():
    """ エントリポイント

    """
    out = pd.DataFrame()
    out_tmp = pd.DataFrame()
    out_path = "../data/out"
    df = pd.DataFrame()
    path = "../data/all_article"
    key_list = ["新型肝炎", "新型コロナ", "プリンセス号", "ウェルステルダム",
                "新型ウイルス", "感染", "休校", "マスク", "武漢",
                "ウイルス性肺炎", "コロナウイルス", "陰性", "陽性", "ウイルス検査", "肺ペスト"]
    diff_check_columns = ["url", "title"]
    search_target_colums = ["title","subtitle","description"]
    # 読み込み
    df = data_import(df, path)

    # 検索
    for key in key_list:
        tmp = df[df['title'].str.contains(key)]
        tmp = pd.concat([tmp, df[df['subtitle'].str.contains(key)]], ignore_index=True)
        tmp = pd.concat([tmp, df[df['description'].str.contains(key)]], ignore_index=True)
        out_tmp = pd.concat([out_tmp, tmp.drop_duplicates()], ignore_index=True)
    out = pd.concat([out, out_tmp.drop_duplicates()])
    out = out.drop_duplicates()
    # 含まれていない部分を抽出
    not_inclued_out = pd.DataFrame()
    not_inclued_out = check_new_entry(df, out, diff_check_columns)
    not_inclued_out = not_inclued_out.drop("比較用の列", axis=1)
    print("hi")

    # 保存
    out.to_json("{o}-include.json".format(o=out_path), orient='records', force_ascii=False)
    not_inclued_out.to_json("{o}-not-include.json".format(o=out_path), orient='records', force_ascii=False)
    not_inclued_out.to_csv("{o}-not-include.csv".format(o=out_path), columns=['url'], header=False, index=False)
    print("end")


def data_import(df, path: str):
    for i in range(10):
        tmp = pd.read_json("{path}{i}.json".format(path=path, i=i), orient='records')
        df = pd.concat([df, tmp], ignore_index=True)
    return df.drop_duplicates()


def search_data(data, key_list: list, target_columns_list):
    tmp = pd.DataFrame()
    out_tmp = pd.DataFrame()
    out_data = pd.DataFrame()
    for key in key_list:
        for clumn_name in target_columns_list:
            tmp = pd.concat([tmp, df[df[clumn_name].str.contains(key)]], ignore_index=True)
        out_tmp = pd.concat([out_tmp, tmp.drop_duplicates()], ignore_index=True)
    out_data = pd.concat([out_data, out_tmp.drop_duplicates()])
    out_data = out_data.drop_duplicates()
    return out_data


def check_new_entry(new_data, old_data, columns_list: list):
    """
    newdataとold_dataの差集合 (new_data - old_data もしくはnew_data ∖ old_data)をpandsのDataFrame形式で返す
    :param new_data: 比較元
    :param old_data: 減算元
    :param columns_list:辞書のキー
    :return:
    """
    # new_dataにold_dataと一致する行が存在するか調べる
    if new_data.empty is False:
        new_data["比較用の列"] = new_data[columns_list].apply(lambda x: "{}_{}".format(x[0], x[1]), axis=1)
    else:
        new_data = {}
    if old_data.empty is False:
        old_data["比較用の列"] = old_data[columns_list].apply(lambda x: "{}_{}".format(x[0], x[1]), axis=1)
        # new_dataにのみ存在する行を表示
        df_diff = new_data[~new_data['比較用の列'].isin(old_data['比較用の列'])]
    else:
        df_diff = pd.DataFrame()
        print("hi")
    if df_diff.empty:
        print("新着のニュースはありません")
    else:
        print("差分表示")
        print(df_diff)
    return df_diff


if __name__ == "__main__":
    main()
