@echo off
cd /d "%~dp0.."
echo 叢雲の画像を5枚自動生成します（DALL-E 3使用）
echo.
echo 【注意】OPENAI_API_KEYが必要です
echo 設定されていない場合は手動でチャッピーにプロンプトを貼り付けてください
echo.
set /p APIKEY="OpenAI APIキーを入力（Enterでスキップ）: "
if not "%APIKEY%"=="" set OPENAI_API_KEY=%APIKEY%
python 動画を作る/画像自動生成.py --character 叢雲 --count 5
pause
