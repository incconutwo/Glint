@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building Glint executable...
pyinstaller --noconsole --onefile --clean --name="Glint" --collect-all customtkinter Glint.pyw

echo.
echo Build complete! Your executable is in the 'dist' folder.
pause
