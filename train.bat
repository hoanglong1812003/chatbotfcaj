@echo off
echo ========================================
echo   Train Data cho First Cloud Journey
echo ========================================
echo.

echo [1/2] Dang xu ly tai lieu trong thu muc data/...
python process_docs.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [2/2] Hoan thanh! Vectorstore da duoc cap nhat.
    echo.
    echo Ban co the:
    echo - Chay chatbot: streamlit run app.py
    echo - Hoac dung Docker: docker-compose restart
    echo.
) else (
    echo.
    echo [LOI] Khong the xu ly tai lieu!
    echo Kiem tra lai thu muc data/ va cac file PDF/TXT
    echo.
)

pause