@echo off
set cur_time=%time::=-%
set cur_time=%cur_time: =0%
set cur_date=%date:/=-%
set filename=log_%cur_date:~4%_%cur_time:~0,-3%.txt
echo saving output to logs\%filename%
python3 -u check_repos.py > logs\%filename% 2>&1