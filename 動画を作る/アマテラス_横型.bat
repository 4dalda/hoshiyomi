@echo off
cd /d "%~dp0.."
echo アマテラスシリーズの1時間動画を作成します...
python make_video.py --series アマテラス --format long
pause
