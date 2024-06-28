import streamlit as st
import pandas as pd
from io import StringIO

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

st.title('CSVファイル比較ツール')

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
        df1 = pd.read_csv(StringIO(paste_data1))
    else:
        df1 = None

    if paste_data2:
        df2 = pd.read_csv(StringIO(paste_data2))
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
        df1 = pd.read_csv(uploaded_file1)
    else:
        df1 = None

    if uploaded_file2:
        df2 = pd.read_csv(uploaded_file2)
    else:
        df2 = None

if df1 is not None and df2 is not None:
    # カラム名選択
    columns1 = df1.columns.tolist()
    columns2 = df2.columns.tolist()

    column1 = st.selectbox('ファイル1の比較に使用するカラム名を選択してください', columns1)
    column2 = st.selectbox('ファイル2の比較に使用するカラム名を選択してください', columns2)

    if column1 and column2:
        preview = st.checkbox('データのプレビュー')

        # データ比較
        unique_data1 = df1[~df1[column1].isin(df2[column2])]
        unique_data2 = df2[~df2[column2].isin(df1[column1])]
        merge_data1 = df1[df1[column1].isin(df2[column2])]
        merge_data2 = df2[df2[column2].isin(df1[column1])]

        # NaN値を空文字列に置き換える
        unique_data1 = unique_data1.fillna('')
        unique_data2 = unique_data2.fillna('')
        merge_data1 = merge_data1.fillna('')
        merge_data2 = merge_data2.fillna('')

        # データフレームをHTMLに変換
        def dataframe_to_html(df):
            #dfは最高20行まで表示
            if len(df) > 20:
                df = df.head(20)
            return df.to_html(classes='dataframe-table', index=False, na_rep='', float_format='{:f}'.format)

        # データのプレビュー
        if preview:
            st.write('CSVファイル1のユニークなデータ')
            st.markdown(f"<div class='dataframe-container'>{dataframe_to_html(unique_data1)}</div>", unsafe_allow_html=True)
            st.write('CSVファイル2のユニークなデータ')
            st.markdown(f"<div class='dataframe-container'>{dataframe_to_html(unique_data2)}</div>", unsafe_allow_html=True)


        # CSVダウンロード
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv1 = convert_df(unique_data1)
        csv2 = convert_df(unique_data2)
        mergeCsv1 = convert_df(merge_data1)
        mergeCsv2 = convert_df(merge_data2)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.download_button(
                label='CSVファイル1のみに存在するデータをダウンロード',
                data=csv1,
                file_name='unique_data1.csv',
                mime='text/csv',
            )

        with col2:
            st.download_button(
                label='CSVファイル2のみに存在するデータをダウンロード',
                data=csv2,
                file_name='unique_data2.csv',
                mime='text/csv',
            )

        with col3:
            st.download_button(
                label='両CSVファイルに含まれるデータをファイル1のフォーマットでダウンロード',
                data=mergeCsv1,
                file_name='merge_data1.csv',
                mime='text/csv',
            )
        with col4: 
            st.download_button(
                label='両CSVファイルに含まれるデータをファイル2のフォーマットでダウンロード',
                data=mergeCsv2,
                file_name='merge_data2.csv',
                mime='text/csv',
            )
else:
    st.write('CSVファイルをアップロードするか、データをコピペしてください。')
