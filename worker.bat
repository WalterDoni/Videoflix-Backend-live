@echo off
cd videoflix_backend
python manage.py rqworker --worker-class rq_win.WindowsWorker default
