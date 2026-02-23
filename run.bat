@echo off
python -m streamlit run compare.py
if %errorlevel% neq 0 (
    echo.
    echo エラーが発生しました（エラーコード: %errorlevel%）
    pause
)