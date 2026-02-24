"""AtasoPy コアロジックのユニットテスト"""
import pytest
import pandas as pd
from compare_core import load_csv, compare_data, convert_df_bom, parse_csv_error_detail


# ============================================================
# A. 正常系 - 基本機能
# ============================================================

class TestA1_BasicComparison:
    """A-1: 基本的な比較（部分一致）"""

    def setup_method(self):
        self.csv1 = "宛名番号,名前,住所\n1,山田太郎,東京都\n2,鈴木花子,神奈川県\n3,田中一郎,大阪府\n4,佐藤二郎,愛知県\n5,伊藤三郎,福岡県\n6,高橋四郎,北海道\n7,渡辺五郎,埼玉県"
        self.csv2 = "口座番号,宛名番号,名前\nA001,1,山田太郎\nA002,3,田中一郎\nA003,5,伊藤三郎\nA004,7,渡辺五郎\nA005,8,木村六郎\nA006,9,小林七郎"
        df1, _ = load_csv(self.csv1)
        df2, _ = load_csv(self.csv2)
        self.result = compare_data(df1, df2, '宛名番号', '宛名番号')

    def test_unique_data1_count(self):
        assert len(self.result['unique_data1']) == 3

    def test_unique_data1_content(self):
        keys = self.result['unique_data1']['宛名番号'].tolist()
        assert sorted(keys) == ['2', '4', '6']

    def test_unique_data2_count(self):
        assert len(self.result['unique_data2']) == 2

    def test_unique_data2_content(self):
        keys = self.result['unique_data2']['宛名番号'].tolist()
        assert sorted(keys) == ['8', '9']

    def test_merge_data1_count(self):
        assert len(self.result['merge_data1']) == 4

    def test_merge_data2_count(self):
        assert len(self.result['merge_data2']) == 4

    def test_merge_data1_columns(self):
        assert self.result['merge_data1'].columns.tolist() == ['宛名番号', '名前', '住所']

    def test_merge_data2_columns(self):
        assert self.result['merge_data2'].columns.tolist() == ['口座番号', '宛名番号', '名前']


class TestA2_FullMatch:
    """A-2: 完全一致（全データ共通）"""

    def setup_method(self):
        csv1 = "ID,名前,部署\n101,田中太郎,営業部\n102,鈴木花子,開発部\n103,佐藤一郎,総務部\n104,高橋二郎,人事部\n105,伊藤三郎,経理部"
        csv2 = "社員ID,氏名,メール\n101,田中太郎,tanaka@example.com\n102,鈴木花子,suzuki@example.com\n103,佐藤一郎,sato@example.com\n104,高橋二郎,takahashi@example.com\n105,伊藤三郎,ito@example.com"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        self.result = compare_data(df1, df2, 'ID', '社員ID')

    def test_unique_data1_empty(self):
        assert len(self.result['unique_data1']) == 0

    def test_unique_data2_empty(self):
        assert len(self.result['unique_data2']) == 0

    def test_merge_count(self):
        assert len(self.result['merge_data1']) == 5
        assert len(self.result['merge_data2']) == 5


class TestA3_NoMatch:
    """A-3: 完全不一致（共通データなし）"""

    def setup_method(self):
        csv1 = "コード,商品名,価格\nP001,りんご,100\nP002,みかん,80\nP003,バナナ,120"
        csv2 = "コード,商品名,価格\nP004,ぶどう,300\nP005,いちご,250\nP006,メロン,500"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        self.result = compare_data(df1, df2, 'コード', 'コード')

    def test_unique_data1_count(self):
        assert len(self.result['unique_data1']) == 3

    def test_unique_data2_count(self):
        assert len(self.result['unique_data2']) == 3

    def test_merge_empty(self):
        assert len(self.result['merge_data1']) == 0
        assert len(self.result['merge_data2']) == 0


class TestA4_DifferentColumns:
    """A-4: 異なるカラム構成での比較"""

    def setup_method(self):
        csv1 = "宛名番号,氏名,生年月日,住所,電話番号\n1001,山田太郎,1990-01-15,東京都新宿区,03-1234-5678\n1002,鈴木花子,1985-06-20,神奈川県横浜市,045-123-4567\n1003,田中一郎,1992-11-03,大阪府大阪市,06-1234-5678\n1004,佐藤二郎,1988-03-25,愛知県名古屋市,052-123-4567"
        csv2 = "口座ID,支店,宛名番号,口座種別\nACC001,新宿支店,1001,普通\nACC002,横浜支店,1002,普通\nACC003,梅田支店,1005,当座"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        self.result = compare_data(df1, df2, '宛名番号', '宛名番号')

    def test_unique_data1_count(self):
        assert len(self.result['unique_data1']) == 2

    def test_unique_data2_count(self):
        assert len(self.result['unique_data2']) == 1

    def test_merge_count(self):
        assert len(self.result['merge_data1']) == 2

    def test_merge_data1_has_5_columns(self):
        assert len(self.result['merge_data1'].columns) == 5

    def test_merge_data2_has_4_columns(self):
        assert len(self.result['merge_data2'].columns) == 4


# ============================================================
# B. 境界値・エッジケース
# ============================================================

class TestB1_SingleRow:
    """B-1: 1行のみ（ヘッダー+1行）"""

    def test_single_row_match(self):
        csv1 = "ID,名前\n1,山田太郎"
        csv2 = "ID,名前\n1,山田太郎"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        assert len(result['merge_data1']) == 1
        assert len(result['unique_data1']) == 0


class TestB2_HeaderOnly:
    """B-2: ヘッダーのみ（データ行なし）"""

    def test_header_only(self):
        csv1 = "ID,名前,部署"
        csv2 = "ID,名前,メール"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        assert len(result['unique_data1']) == 0
        assert len(result['unique_data2']) == 0
        assert len(result['merge_data1']) == 0
        assert len(result['merge_data2']) == 0


class TestB3_LargeVsSmall:
    """B-3: 大量データ（1000行 vs 3行）"""

    def setup_method(self):
        rows1 = "ID,名前\n" + "\n".join(f"{i},社員{i:04d}" for i in range(1, 1001))
        rows2 = "ID,名前\n500,社員0500\n999,社員0999\n1500,存在しない社員"
        df1, _ = load_csv(rows1)
        df2, _ = load_csv(rows2)
        self.result = compare_data(df1, df2, 'ID', 'ID')

    def test_unique_data1_count(self):
        assert len(self.result['unique_data1']) == 998

    def test_unique_data2_count(self):
        assert len(self.result['unique_data2']) == 1

    def test_unique_data2_content(self):
        assert self.result['unique_data2']['ID'].tolist() == ['1500']

    def test_merge_count(self):
        assert len(self.result['merge_data1']) == 2


# ============================================================
# C. データ品質テスト
# ============================================================

class TestC1_EmptyCells:
    """C-1: 空白セルを含むデータ"""

    def test_empty_cells(self):
        csv1 = "ID,名前,備考\n1,山田太郎,正常データ\n2,鈴木花子,\n3,,備考のみ\n4,佐藤二郎,正常データ"
        csv2 = "ID,名前\n1,山田太郎\n3,田中一郎\n5,伊藤三郎"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        assert len(result['merge_data1']) == 2  # ID=1, 3
        assert len(result['unique_data1']) == 2  # ID=2, 4
        assert len(result['unique_data2']) == 1  # ID=5

    def test_nan_replaced_with_empty_string(self):
        csv1 = "ID,名前,備考\n1,山田太郎,\n2,,備考のみ"
        csv2 = "ID,名前\n1,山田太郎"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        # merge_data1のID=1の備考はNaN→空文字列
        row = result['merge_data1'][result['merge_data1']['ID'] == '1']
        assert row['備考'].values[0] == ''


class TestC2_WhitespaceKeys:
    """C-2: 前後スペースのあるキー（仕様確認）"""

    def test_leading_space_treated_as_different(self):
        csv1 = "ID,名前\n 001,田中一郎"  # 先頭スペース
        csv2 = "ID,名前\n001,田中一郎"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        # " 001" != "001" なので共通0件
        assert len(result['merge_data1']) == 0

    def test_trailing_space_treated_as_different(self):
        csv1 = "ID,名前\n001 ,佐藤二郎"  # 末尾スペース
        csv2 = "ID,名前\n001,佐藤二郎"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        assert len(result['merge_data1']) == 0


class TestC3_DuplicateKeys:
    """C-3: 重複キーを含むデータ"""

    def test_duplicate_keys_all_included(self):
        csv1 = "宛名番号,名前,住所\n1,山田太郎,東京都\n1,山田太郎,神奈川県\n2,鈴木花子,大阪府\n3,田中一郎,愛知県\n3,田中一郎,福岡県\n3,田中一郎,北海道"
        csv2 = "宛名番号,口座番号\n1,ACC001\n2,ACC002\n2,ACC003\n4,ACC004"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, '宛名番号', '宛名番号')
        # ファイル1: 宛名番号1(2行)+2(1行)+3(3行) → 1,2は共通、3はファイル1のみ
        assert len(result['merge_data1']) == 3   # 宛名番号1×2行 + 宛名番号2×1行
        assert len(result['unique_data1']) == 3   # 宛名番号3×3行
        # ファイル2: 宛名番号1,2は共通、4はファイル2のみ
        assert len(result['merge_data2']) == 3   # 宛名番号1×1行 + 宛名番号2×2行
        assert len(result['unique_data2']) == 1   # 宛名番号4×1行


class TestC4_ZeroPadding:
    """C-4: ゼロパディング（dtype=strの仕様確認）"""

    def test_zero_padded_not_equal_to_unpadded(self):
        csv1 = "コード,名前\n001,山田太郎\n002,鈴木花子\n010,田中一郎\n100,佐藤二郎"
        csv2 = "コード,名前\n1,山田太郎\n2,鈴木花子\n10,田中一郎\n100,佐藤二郎"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'コード', 'コード')
        # "100" == "100" のみ一致
        assert len(result['merge_data1']) == 1
        assert len(result['unique_data1']) == 3
        assert len(result['unique_data2']) == 3


class TestC5_JapaneseKeys:
    """C-5: 日本語キーでの比較"""

    def test_japanese_key_comparison(self):
        csv1 = "都道府県,人口,地方\n東京都,14000000,関東\n大阪府,8800000,近畿\n愛知県,7500000,中部\n北海道,5200000,北海道\n福岡県,5100000,九州"
        csv2 = "都道府県,県庁所在地\n東京都,新宿区\n神奈川県,横浜市\n大阪府,大阪市\n京都府,京都市\n北海道,札幌市"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, '都道府県', '都道府県')
        assert len(result['merge_data1']) == 3   # 東京都, 大阪府, 北海道
        assert len(result['unique_data1']) == 2   # 愛知県, 福岡県
        assert len(result['unique_data2']) == 2   # 神奈川県, 京都府


class TestC6_QuotedComma:
    """C-6: カンマを含むフィールド（クォート付き）"""

    def test_quoted_comma_parsed_correctly(self):
        csv1 = 'ID,名前,住所\n1,山田太郎,"東京都新宿区西新宿2-8-1, 都庁ビル"\n2,鈴木花子,神奈川県横浜市中区日本大通1\n3,"田中,一郎",大阪府大阪市北区中之島1-3-20'
        csv2 = "ID,名前\n1,山田太郎\n2,鈴木花子\n4,佐藤二郎"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        assert len(result['merge_data1']) == 2   # ID=1, 2
        assert len(result['unique_data1']) == 1   # ID=3
        assert len(result['unique_data2']) == 1   # ID=4

    def test_comma_in_name_preserved(self):
        csv1 = 'ID,名前\n1,"田中,一郎"'
        csv2 = "ID,名前\n2,鈴木花子"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        assert df1['名前'].values[0] == '田中,一郎'


# ============================================================
# D. 異常系 - エラーハンドリング
# ============================================================

class TestD1_BrokenCSV:
    """D-1: カラム数不一致の壊れたCSV"""

    def test_broken_csv_returns_error(self):
        csv = "ID,名前,住所\n1,山田太郎,東京都\n2,鈴木花子,神奈川県\n3,田中一郎,大阪府,中央区,追加データ1,追加データ2\n4,佐藤二郎,愛知県"
        df, err = load_csv(csv)
        assert df is None
        assert err is not None

    def test_error_contains_line_number(self):
        csv = "ID,名前,住所\n1,山田太郎,東京都\n2,鈴木花子,神奈川県\n3,田中一郎,大阪府,中央区,追加データ1,追加データ2\n4,佐藤二郎,愛知県"
        _, err = load_csv(csv)
        assert '4行目' in err

    def test_error_contains_column_counts(self):
        csv = "ID,名前,住所\n1,山田太郎,東京都\n2,鈴木花子,神奈川県\n3,田中一郎,大阪府,中央区,追加データ1,追加データ2\n4,佐藤二郎,愛知県"
        _, err = load_csv(csv)
        assert '3列' in err
        assert '6列' in err


class TestD2_UnquotedComma:
    """D-2: クォートなしカンマ入りデータ"""

    def test_unquoted_comma_returns_error(self):
        csv = "ID,名前,住所\n1,山田太郎,東京都新宿区\n2,鈴木花子,神奈川県横浜市中区日本大通1, 2F\n3,田中一郎,大阪府"
        df, err = load_csv(csv)
        assert df is None
        assert err is not None


# ============================================================
# E. 出力検証
# ============================================================

class TestE1_BOMOutput:
    """E-1: BOM付きUTF-8出力"""

    def test_bom_present(self):
        csv1 = "ID,名前\n1,山田太郎"
        df, _ = load_csv(csv1)
        output = convert_df_bom(df)
        assert output[:3] == b'\xef\xbb\xbf'

    def test_content_after_bom_is_valid_csv(self):
        csv1 = "ID,名前\n1,山田太郎"
        df, _ = load_csv(csv1)
        output = convert_df_bom(df)
        content = output[3:].decode('utf-8')
        assert 'ID' in content
        assert '山田太郎' in content


class TestE2_OutputCounts:
    """E-2: 件数の一致"""

    def test_sum_equals_total(self):
        """ファイル1のみ + 共通 = ファイル1の全行数"""
        csv1 = "ID,名前\n1,A\n2,B\n3,C\n4,D\n5,E"
        csv2 = "ID,名前\n1,A\n3,C\n5,E\n7,G"
        df1, _ = load_csv(csv1)
        df2, _ = load_csv(csv2)
        result = compare_data(df1, df2, 'ID', 'ID')
        assert len(result['unique_data1']) + len(result['merge_data1']) == len(df1)
        assert len(result['unique_data2']) + len(result['merge_data2']) == len(df2)


class TestParseErrorDetail:
    """parse_csv_error_detail関数のテスト"""

    def test_known_format(self):
        try:
            pd.read_csv(pd.io.common.StringIO("a,b\n1,2,3"))
        except pd.errors.ParserError as e:
            detail = parse_csv_error_detail(e)
            assert '行目' in detail
            assert '考えられる原因' in detail

    def test_unknown_format(self):
        detail = parse_csv_error_detail(Exception("unknown error"))
        assert 'CSV読み込みエラー' in detail
