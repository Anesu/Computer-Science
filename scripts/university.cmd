@echo off
rem The University — one-click campus launcher for Open CS Degree 2026.
rem Regenerates the site from the current curriculum/registry data, then
rem starts Blume and opens the browser. Close this window to shut down.
title The University - Open CS Degree 2026
cd /d "%~dp0"

echo.
echo  Preparing the campus...
python build_site_docs.py || (echo  Content build failed.& pause & exit /b 1)

cd /d "%~dp0..\site"
echo  Opening the gates — http://localhost:4321
echo  (Keep this window open while you study; close it to shut down.)
npx blume dev --port 4321 --open
