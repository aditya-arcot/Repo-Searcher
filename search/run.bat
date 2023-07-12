@echo off
set /p mode="enter mode - include (I) / exclude (anything else): "
set cur_time=%time::=-%
set cur_time=%cur_time: =0%
set cur_date=%date:/=-%
set filename=log_%cur_date:~4%_%cur_time:~0,-3%.txt
echo saving output to logs\%filename%
if "%mode%"=="I" (
    echo using include mode
    python3 -u check_repos.py include > logs\%filename% 2>&1
) else (
    echo using exclude mode
    python3 -u check_repos.py exclude > logs\%filename% 2>&1
)
echo done