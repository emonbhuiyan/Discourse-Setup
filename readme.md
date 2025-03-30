$ apt install python3.12-venv
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python3 app.py
$ deactivate

cd ~/discourseSetup
gunicorn --bind 127.0.0.1:5000 app:app

nohup gunicorn --bind 0.0.0.0:5000 app:app > nohup.log 2>&1 &