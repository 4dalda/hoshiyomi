@echo off
cd /d "%~dp0.."
echo スサノオシリーズの1時間動画を作成します...
python make_video.py --series スサノオ --format long
pause
