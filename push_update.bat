@echo off
set /p msg="Scrie mesajul commitului: "
git add .
git commit -m "%msg%"
git push
pause
