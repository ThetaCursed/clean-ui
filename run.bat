@echo off
call .\venv-ui\Scripts\activate  :: Activates the virtual environment
python clean-ui.py  :: Runs the Python script
pause  :: Keeps the window open after execution
