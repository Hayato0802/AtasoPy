# AtasoPy プロジェクトルール

## コミット前のテスト実行（必須）

コミットを作成する前に、必ず全テストを実行して全件パスすることを確認すること。

```bash
python -m pytest test_compare_core.py test_compare_app.py -v
```

テストが失敗した場合はコミットせず、修正を優先すること。
