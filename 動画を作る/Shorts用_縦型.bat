@echo off
cd /d "%~dp0.."
echo シリーズ名を入力してください:
echo   月 / 星 / 祭 / アマテラス / ツクヨミ / スサノオ / 叢雲の導き
set /p SERIES="シリーズ名: "
echo %SERIES% のShorts用縦型動画を作成します...
python make_video.py --series %SERIES% --format shorts
pause
