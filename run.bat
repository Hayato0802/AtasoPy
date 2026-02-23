@echo off
python -m streamlit run compare.py
if %errorlevel% neq 0 (
    echo.
    echo Error occurred (exit code: %errorlevel%)
    pause
)