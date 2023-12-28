# To-do:

- Implement outside actions: weekly email, daily recurring task creation, schedule with cron

- User Home Task List:
    - Show trigger date for pending tasks
    - Show task updated date for open tasks
    - Show updated date for closed tasks and order by these dates
    - Make tables prettier (not pandas)

# Installation / Deployment

Clone this repo: `git clone https://$GITHUB_TOKEN@github.com/blincoe/tasks.git`

Create virtual python environment:
```sh
pip3 install virtualenv 
virtualenv tasks_env -p /usr/bin/python3
source tasks_env/bin/activate
pip install Flask
pip install pandas
```

Create `passenger_wsgi.py` file inside of host directory:
```sh
vi host_name.com/passenger_wsgi.py
```
```python
import sys
import os
import logging

INTERP = os.path.expanduser("/home/ssh_user/tasks_env/bin/python3") ### In terminal, with the environment `venv` activated, type "which python3". The result would be used here.
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

wd = '/home/ssh_user/host_name.com/tasks/'
sys.path.append(wd) # This is the address of your `app` folder, as shown below.

from tasks.app import App
logger = logging.getLogger('Tasks')
app = App('Tasks', logger, wd=wd)
application = app.app

if __name__ == '__main__':
    app.run()

```

And then make executable:
```sh
chmod +x host_name.com/passenger_wsgi.py
```

Add restart file:
```sh
mkdir host_name.com/tmp
touch host_name.com/tmp/restart.txt 
```

Initialize database:
```sh
sh tasks/setup.sh 
```