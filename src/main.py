#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import yaml

"""
データ内に指定のキーワードを含むレコードと含まないレコードに分割

dataディレクトリにある指定しconfig.ymlによって指定したjsonのデータを読み込み、
設定で指定されたキーワードのリストのファイルに含まれるものがないか検索、
分割して保存
"""


def main():
    """ エントリポイント

    """

    # 設定の読み込み
    config = import_config()
    out_name = config["out_name"]
    import_directory = config["import_directory"]
    import_file_name = config["import_file_name"]
    last_number = config["last_number"]
    key_list = list(pd.read_csv(config["key_list_path"], header=None, squeeze=True))
    diff_check_columns = config["diff_check_columns"]
    search_target_columns = config["search_target_columns"]

    # 読み込み
    df = json_data_import(import_directory, import_file_name, last_number)

    # 検索
    out = search_data(df, key_list, search_target_columns)

    # 含まれていない部分を抽出
    not_include_out = check_new_entry(df, out, diff_check_columns)

    # 保存
    out.to_json(
        "{directory}{name}-include.json".format(directory=import_directory, name=out_name),
        orient='records', force_ascii=False)
    not_include_out.to_json(
        "{directory}{name}-not-include.json".format(directory=import_directory, name=out_name),
        orient='records', force_ascii=False)
    # urlのみのリストを作成
    not_include_out.to_csv(
        "{directory}{name}{-not-include.txt".format(directory=import_directory, name=out_name),
        columns=['url'], header=False, index=False)
    print("end")


def import_config(config_path: str = "../config.yml") -> dict:
    with open(config_path, encoding='utf-8') as f:
        config = yaml.safe_load(f.read())
    return config


def json_data_import(directory: str, file_name: str, last_number: int):
    """
    連番になっているjsonのデータを読み込んで1まとまりのデータにする
    data0.json, data1.json … data100.jsonが./data/にあったとき
    path ="./data/" file_name=data, last_number=100を代入すると全てのデータが1つにまとまってDataFrame形式で帰ってくる
    このとき各データの重複は削除される
    :param file_name:読み込ませたいファイルの名前
    :param directory:読み込みたいディレクトリ
    :param last_number:
    :return: 読み込んだデータ(pands)
    """
    df = pd.DataFrame()
    for i in range(last_number):
        tmp = pd.read_json(
            "{path}{file_name}{i}.json".format(path=directory, file_name=file_name, i=i),
            orient='records')
        df = pd.concat([df, tmp], ignore_index=True)
    return df.drop_duplicates()


def search_data(data, key_list: list, target_columns_list):
    """
    pandsのデータからリストにあるのキーワードを含んでいるデータを抽出し、返す
    :param data: pandsの検索をかけたいデータ
    :param key_list: 検索したキーワードリスト
    :param target_columns_list: 検索したいカラム名のリスト
    :return: 検索結果(pandas)
    """
    # 該当するカラム
    tmp = pd.DataFrame()
    out_tmp = pd.DataFrame()
    out_data = pd.DataFrame()
    for key in key_list:
        for column_name in target_columns_list:
            tmp = pd.concat([tmp, data[data[column_name].str.contains(key)]], ignore_index=True)
        out_tmp = pd.concat([out_tmp, tmp.drop_duplicates()], ignore_index=True)
    out_data = pd.concat([out_data, out_tmp.drop_duplicates()])
    out_data = out_data.drop_duplicates()
    return out_data


def check_new_entry(new_data, old_data, columns_list: list):
    """
    # パクリ元
    - https://quzee.hatenablog.com/entry/2017/08/13/172151
    - https://qiita.com/karashi39/items/e1b8939044f25dbc419f
    new_dataとold_dataの差集合 (new_data - old_data もしくはnew_data ∖ old_data)をpandasのDataFrame形式で返す

    SQLで書くとこう
    SELECT * FROM df1
    WHER new_data.columns_list NOT IN (SELECT columns_list FROM old_data)

    :param new_data: 比較元
    :param old_data: 減算元
    :param columns_list:辞書のキー これを1つにしたものを主キーにする
    :return:pandasの差分のデータ
    """
    # new_dataにold_dataと一致するレコードが存在するか調べる
    if new_data.empty is False:
        new_data["比較用の列"] = new_data[columns_list].apply(lambda x: "{}_{}".format(x[0], x[1]), axis=1)
    else:
        new_data = {}
    if old_data.empty is False:
        old_data["比較用の列"] = old_data[columns_list].apply(lambda x: "{}_{}".format(x[0], x[1]), axis=1)
        # new_dataにのみ存在するレコードを作成
        df_diff = new_data[~new_data['比較用の列'].isin(old_data['比較用の列'])]
        df_diff = df_diff.drop("比較用の列", axis=1)
    else:
        df_diff = pd.DataFrame()
    return df_diff


if __name__ == "__main__":
    main()
