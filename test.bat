@echo off

:: Activate the virtual environment

call %VIRTUAL_ENV%\Scripts\activate.bat

:: Run flake8

flake8 %VIRTUAL_ENV%\..\

:: Run python tests

python -m unittest discover -s %VIRTUAL_ENV%\..\tests -p "test_*.py"


