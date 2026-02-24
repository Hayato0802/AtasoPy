"""AtasoPy コアロジック - Streamlit非依存の比較処理"""
import re
import pandas as pd
from io import StringIO


def parse_csv_error_detail(e):
    """ParserErrorのメッセージから原因を日本語で説明する"""
    msg = str(e)
    match = re.search(r'Expected (\d+) fields in line (\d+), saw (\d+)', msg)
    if match:
        expected, line, saw = match.group(1), match.group(2), match.group(3)
        return (
            f"**{line}行目**でカラム数が一致しません（ヘッダー: {expected}列、{line}行目: {saw}列）\n\n"
            f"**考えられる原因:**\n"
            f"- データ内にカンマが含まれている（例: 住所や説明文にカンマがある）\n"
            f"- ダブルクォートで囲まれていないフィールドがある\n"
            f"- CSVの区切り文字がカンマではない（タブ区切りなど）\n\n"
            f"**対処法:**\n"
            f"- 該当行（{line}行目付近）のデータを確認してください\n"
            f"- カンマを含むフィールドをダブルクォートで囲んでください"
        )
    return f"CSV読み込みエラー: {msg}"


def load_csv(source, dtype=str):
    """CSVを読み込む。文字列ならStringIOで、それ以外はそのまま渡す。

    Returns:
        (DataFrame, None) on success
        (None, error_message) on failure
    """
    try:
        if isinstance(source, str):
            df = pd.read_csv(StringIO(source), dtype=dtype)
        else:
            df = pd.read_csv(source, dtype=dtype)
        return df, None
    except pd.errors.ParserError as e:
        return None, parse_csv_error_detail(e)


def compare_data(df1, df2, column1, column2):
    """2つのDataFrameをキーカラムで比較する。

    Returns:
        dict with keys:
            unique_data1: df1にのみ存在するデータ
            unique_data2: df2にのみ存在するデータ
            merge_data1: 両方に存在するデータ（df1のフォーマット）
            merge_data2: 両方に存在するデータ（df2のフォーマット）
    """
    unique_data1 = df1[~df1[column1].isin(df2[column2])]
    unique_data2 = df2[~df2[column2].isin(df1[column1])]
    merge_data1 = df1[df1[column1].isin(df2[column2])]
    merge_data2 = df2[df2[column2].isin(df1[column1])]

    # NaN値を空文字列に置き換える
    unique_data1 = unique_data1.fillna('')
    unique_data2 = unique_data2.fillna('')
    merge_data1 = merge_data1.fillna('')
    merge_data2 = merge_data2.fillna('')

    return {
        'unique_data1': unique_data1,
        'unique_data2': unique_data2,
        'merge_data1': merge_data1,
        'merge_data2': merge_data2,
    }


def convert_df_bom(df):
    """DataFrameをBOM付きUTF-8のCSVバイト列に変換する"""
    return '\ufeff'.encode('utf-8') + df.to_csv(index=False).encode('utf-8')
