@echo off
chcp 65001 >nul
cd /d "%~dp0"

python -m nuitka ^
	--msvc=latest ^
	--standalone ^
    --onefile ^
    --assume-yes-for-downloads ^
    --enable-plugin=tk-inter ^
    --include-package=customtkinter ^
    --include-package-data=customtkinter ^
    --include-package=matplotlib.backends.backend_tkagg ^
    --include-package-data=matplotlib ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=calculator.ico ^
    --company-name="ky4ka-boroxla" ^
    --product-name="Windows Style Calculator" ^
    --file-version=0.7.2^
    --product-version=0.7.2 ^
    --file-description="Калькулятор" ^
    --output-filename=Calculator.exe ^
    --output-dir=dist ^
    --remove-output ^
    windows_calculator.py

pause
