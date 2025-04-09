@echo off

:: Di chuyển vào thư mục chart
cd chart

:: Gọi build.sh bằng Git Bash
"E:\Github\bin\bash.exe" build.sh

:: Quay lại thư mục gốc
cd ..

:: Chạy Python
python main.py

pause
