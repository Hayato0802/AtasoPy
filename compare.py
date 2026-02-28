import streamlit as st
import os
from datetime import datetime
from compare_core import load_csv, compare_data, convert_df_bom

# 現在の日時を取得してフォーマット
current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

st.set_page_config(
    page_title="AtasoPy",
    layout="wide",
    menu_items={
         'About': """
         ## CSVファイル比較ツール
         ### -AtasoPy-
         あっちにあってこっちにない、を探すツールです。
         """
     })

# カスタムCSSを適用
st.markdown(
    """
    <style>
    .dataframe-container {
        width: 100% !important;
        max-height: 500px !important;
        overflow: auto;
    }
    .dataframe-table th, .dataframe-table td {
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('CSVファイル比較ツール -AtasoPy-')

# Web版（Streamlit Cloud）の場合、機密情報に関する警告を表示
if os.path.exists('/mount/src'):
    st.warning('このページはWeb版です。機密情報は入力しないでください。機密情報を扱う場合はローカル版をご利用ください。')

uploaded_file1 = None
uploaded_file2 = None

# チェックボックスで入力方法を選択
direct_input = st.checkbox('ファイルを使用せず、直接入力する')

if direct_input:
    col1, col2 = st.columns(2)
    with col1:
        paste_data1 = st.text_area('データ1を入力してください')
    with col2:
        paste_data2 = st.text_area('データ2を入力してください')

    # データの読み込み
    if paste_data1:
        df1, err1 = load_csv(paste_data1)
        if err1:
            st.error(f'データ1の読み込みエラー\n\n{err1}')
        else:
            col1.info(f'データ1: {len(df1)}件')
    else:
        df1 = None

    if paste_data2:
        df2, err2 = load_csv(paste_data2)
        if err2:
            st.error(f'データ2の読み込みエラー\n\n{err2}')
        else:
            col2.info(f'データ2: {len(df2)}件')
    else:
        df2 = None

else:
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file1 = st.file_uploader('ファイル1を選択してください', type=['csv', 'txt'])
    with col2:
        uploaded_file2 = st.file_uploader('ファイル2を選択してください', type=['csv', 'txt'])

    # ファイルの読み込み
    if uploaded_file1:
        df1, err1 = load_csv(uploaded_file1)
        if err1:
            st.error(f'ファイル1の読み込みエラー\n\n{err1}')
        else:
            col1.info(f'ファイル1: {len(df1)}件')
    else:
        df1 = None

    if uploaded_file2:
        df2, err2 = load_csv(uploaded_file2)
        if err2:
            st.error(f'ファイル2の読み込みエラー\n\n{err2}')
        else:
            col2.info(f'ファイル2: {len(df2)}件')
    else:
        df2 = None

if df1 is not None and df2 is not None:

    st.divider()

    # プレビュー件数を定義
    MAX_PREVIEW = 20
    preview = st.checkbox('データのプレビュー(最大' + str(MAX_PREVIEW) + '行)')

    # カラム名選択
    columns1 = df1.columns.tolist()
    columns2 = df2.columns.tolist()

    col1, col2 = st.columns(2)
    with col1:
        column1 = st.selectbox('ファイル1：比較のキーとなるカラム名を選択してください', columns1)
    with col2:
        column2 = st.selectbox('ファイル2：比較のキーとなるカラム名を選択してください', columns2)

    if column1 and column2:

        # データ比較
        result = compare_data(df1, df2, column1, column2)
        unique_data1 = result['unique_data1']
        unique_data2 = result['unique_data2']
        merge_data1 = result['merge_data1']
        merge_data2 = result['merge_data2']

        # データフレームをHTMLに変換
        def dataframe_to_html(df):
            # dfは最高20行まで表示
            if len(df) > 20:
                df = df.head(20)
            return df.to_html(classes='dataframe-table', index=False, na_rep='', float_format='{:f}'.format)

        # 横スクロールを可能にするCSSを追加
        scrollable_css = """
        <style>
            .dataframe-container {
                overflow-x: auto;
                white-space: nowrap;
            }
            .dataframe-table {
                margin-right: 10px;
            }
        </style>
        """

        # CSSをStreamlitに追加
        st.markdown(scrollable_css, unsafe_allow_html=True)

        # データのプレビューを横並びで表示
        if preview:
            col1, col2 = st.columns(2)

            with col1:
                st.write('CSVファイル1のデータ')
                st.markdown(f"<div class='dataframe-container'>{dataframe_to_html(df1)}</div>", unsafe_allow_html=True)

            with col2:
                st.write('CSVファイル2のデータ')
                st.markdown(f"<div class='dataframe-container'>{dataframe_to_html(df2)}</div>", unsafe_allow_html=True)



        st.divider()

        # CSVダウンロード
        count_unique_data1 = len(unique_data1)
        count_unique_data2 = len(unique_data2)
        count_merge_data1 = len(merge_data1)
        count_merge_data2 = len(merge_data2)

        csv1 = convert_df_bom(unique_data1)
        csv2 = convert_df_bom(unique_data2)
        mergeCsv1 = convert_df_bom(merge_data1)
        mergeCsv2 = convert_df_bom(merge_data2)

        if uploaded_file1 and uploaded_file1.name:
            file_name1 = f"{os.path.splitext(uploaded_file1.name)[0]}"
        else:
            file_name1 = "file1"

        if uploaded_file2 and uploaded_file2.name:
            file_name2 = f"{os.path.splitext(uploaded_file2.name)[0]}"
        else:
            file_name2 = "file2"

        # ダウンロードボタンを縦に並べる
        st.download_button(
            label=f"CSVファイル1のみに存在するデータをダウンロード({count_unique_data1}件)",
            data=csv1,
            file_name= f"[only_exists]{file_name1}_{current_time}.csv",
            mime='text/csv',
        )

        st.download_button(
            label=f"CSVファイル2のみに存在するデータをダウンロード({count_unique_data2}件)",
            data=csv2,
            file_name=f"[only_exists]{file_name2}_{current_time}.csv",
            mime='text/csv',
        )

        st.download_button(
            label=f"両CSVファイルに含まれるデータをファイル1のフォーマットでダウンロード({count_merge_data1}件)",
            data=mergeCsv1,
            file_name=f"[merge_data]Format={file_name1}_{current_time}.csv",
            mime='text/csv',
        )

        st.download_button(
            label=f"両CSVファイルに含まれるデータをファイル2のフォーマットでダウンロード({count_merge_data2}件)",
            data=mergeCsv2,
            file_name=f"[merge_data]Format={file_name2}_{current_time}.csv",
            mime='text/csv',
        )
