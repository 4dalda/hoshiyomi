@echo off
cd /d "%~dp0.."
echo 叢雲の導きシリーズの動画を作成します...
python make_video.py --series 叢雲の導き --format long
pause
