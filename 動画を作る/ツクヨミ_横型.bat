@echo off
cd /d "%~dp0.."
echo ツクヨミシリーズの1時間動画を作成します...
python make_video.py --series ツクヨミ --format long
pause
