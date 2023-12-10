import logging
import sqlite3
import pandas as pd
import re
from  flask import Flask, render_template, request, flash, url_for, redirect
from waitress import serve


class Tasks:
    def __init__(self, logger, conn):
        self._logger = logger
        self._conn = conn

        self._get_task_info_from_db()

    def _get_task_info_from_db(self):
        self._logger.info('Getting all tasks from database')
        query = '''
            select
                tasks.task_id
                , tasks.created_at
                , tasks.updated_at
                , tasks.user_id
                , tasks.title as task_title
                , tasks.notes as task_description
                , tasks.trigger_date
                , tasks.status
                , users.user_name
            from tasks
            join users
                on tasks.user_id = users.user_id
            '''
        self.task_info = pd.read_sql(query, self._conn, index_col='task_id')

    def add_task(self, user_id, task_title, task_description, trigger_date):
        if trigger_date == '':
            status = 'open'
            trigger_date = 'null'
        else:
            status = 'scheduled'

        self._logger.info(f'Adding task, {task_title}, from user ID, {user_id}, to database')

        query = f'''
            insert into tasks (
                user_id 
                , title 
                , notes
                , trigger_date 
                , status
                ) values 
                (?, ?, ?, ?, ?)
                ;
        '''
        cur = self._conn.cursor()
        cur.execute(query, (str(user_id), task_title, task_description, trigger_date, status))
        self._conn.commit()

        self._get_task_info_from_db()

    def get_task_info(self, task_id):
        return self.task_info.loc[int(task_id)]
    
    def get_tasks_for_user(self, user_name, status=None):
        if status is None:
            return self.task_info.loc[self.task_info['user_name'] == user_name]
        else:
            return self.task_info.loc[(self.task_info['user_name'] == user_name) & (self.task_info['status'] == status)]
        
    def get_task_table_for_user_and_status(self, user_name, status):
        tasks_df = self.get_tasks_for_user(user_name, status)
        if len(tasks_df) == 0:
            task_html = 'None'
        else:
            tasks_df = tasks_df.reset_index()
            tasks_df['task_description'] = tasks_df.apply(lambda r_: r_['task_description'].replace('\r\n', '<br>'), axis=1)
            tasks_df['task_link'] = tasks_df.apply(lambda r_: f'''<a href="{url_for('/task/<task_id>', task_id=r_['task_id'])}">link</a>''', axis=1)
            task_html = tasks_df \
                .loc[:, ['task_id', 'task_title', 'task_description', 'task_link']] \
                .rename(columns={'task_id': 'Task ID', 'task_title': 'Title', 'task_description': 'Description', 'task_link': 'Link'}) \
                .to_html(index=False, render_links=True, escape=False)
        return task_html



class Users:
    def __init__(self, logger, conn):
        self._logger = logger
        self._conn = conn

        self._get_user_info_from_db()

    def _get_user_info_from_db(self):
        self._logger.info('Getting all users from database')
        query = '''
            select
                user_id
                , created_at
                , updated_at
                , user_name
                , email_address
            from users
            '''
        self.user_info = pd.read_sql(query, self._conn)
        self.user_names = self.user_info['user_name'].unique()

    def add_user(self, user_name, email_address):
        self._logger.info(f'Adding user, {user_name}, to database')
        sql = f'''
            insert into users (
                user_name
                , email_address
                ) values 
                (?, ?)
                ;
        '''
        cur = self._conn.cursor()
        cur.execute(sql, (user_name, email_address))
        self._conn.commit()
        
        self._get_user_info_from_db()

    def get_user_id(self, user_name):
        return self.user_info.loc[self.user_info['user_name'] == user_name, 'user_id'].values[0]
     


class App:
    def __init__(self, app_name, logger):
        self.app = Flask(app_name)
        self.app.secret_key = 'jfjfjhfdjkfd'

        self._logger = logger

        self._conn = sqlite3.connect('app.db', check_same_thread=False)

        self._add_endpoints()
        self._users = Users(logger, self._conn)
        self._tasks = Tasks(logger, self._conn)
    
    def _add_endpoints(self):
        self.app.add_url_rule(rule='/', view_func=self._index)
        self.app.add_url_rule(rule='/login', view_func=self._login_home)
        self.app.add_url_rule(rule='/user-login', view_func=self._user_login, methods=['POST'])
        self.app.add_url_rule(rule='/create-user', endpoint='create-user', view_func=self._create_user, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/create-user-home', endpoint='create-user-home', view_func=self._create_user_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>', endpoint='/user/<user_name>', view_func=self._user_home, methods=['POST', 'GET'])

        self.app.add_url_rule(rule='/user/<user_name>/create-task-home', endpoint='/user/<user_name>/create-task-home', view_func=self._create_task_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>/create-task', endpoint='/user/<user_name>/create-task', view_func=self._create_task, methods=['POST', 'GET'])


        self.app.add_url_rule(rule='/task/<task_id>', endpoint='/task/<task_id>', view_func=self._task_home, methods=['POST', 'GET'])
        #self.app.add_url_rule(rule='/user/<user_name>/close-task', endpoint='/user/<user_name>/close-task', view_func=self._create_task, methods=['POST', 'GET'])
        #self.app.add_url_rule(rule='/user/<user_name>/modify-task', endpoint='/user/<user_name>/create-task', view_func=self._create_task, methods=['POST', 'GET'])
        #self.app.add_url_rule(rule='/user/<user_name>/delete-task', endpoint='/user/<user_name>/create-task', view_func=self._create_task, methods=['POST', 'GET'])

        #self.app.add_url_rule(rule='/modify-user', endpoint='modify-user', view_func=self._modify_user, methods=['POST', 'GET'])
        #self.app.add_url_rule(rule='/delete-user', endpoint='delete-user', view_func=self._delete_user, methods=['POST', 'GET'])

    def _index(self):
        return redirect('/login')
    
    def _login_home(self):
        return render_template('login.html')
    
    def _create_user_home(self):
        return render_template('create_user.html')
    
    def _task_home(self, task_id):
        task_info = self._tasks.get_task_info(task_id)
        
        user_name = task_info['user_name']
        task_title = task_info['task_title']
        task_description = task_info['task_description'].replace('\r\n', '<br>')
        if task_info['status'] == 'scheduled':
            task_status = f"Scheduled - {task_info['trigger_date']}"
        else:
            task_status = task_info['status']
        return render_template(
            'task_home.html',
            task_id=task_id,
            user_name=user_name,
            task_title=task_title,
            task_description=task_description,
            task_status=task_status,
            )
    
    def _create_task_home(self, user_name):
        return render_template('create_task.html', user_name=user_name)
    
    def _create_task(self, user_name):
        task_title = request.form['task-title']
        task_description = request.form['task-description']
        trigger_date = request.form['trigger-date']
        user_id = self._users.get_user_id(user_name)
        self._tasks.add_task(user_id, task_title, task_description, trigger_date)
        flash(f'Task Created')
        return render_template('create_task.html', user_name=user_name)
    
    def _user_login(self):
        user_name = request.form['user-name']
        if user_name not in self._users.user_names:
            flash(f'User ID, {user_name}, does not exists. Enter another ID or create a new one.')
            return render_template('login.html')
        else:
            return redirect(f'/user/{user_name}')
    
    def _user_home(self, user_name):
            open_task_html = self._tasks.get_task_table_for_user_and_status(user_name, 'open')
            scheduled_task_html = self._tasks.get_task_table_for_user_and_status(user_name, 'scheduled')
            closed_task_html = self._tasks.get_task_table_for_user_and_status(user_name, 'closed')
            return render_template(
                'user_home.html', 
                user_name=user_name,
                open_tasks=open_task_html,
                scheduled_tasks=scheduled_task_html,
                closed_tasks=closed_task_html,
                )
    
    def _create_user(self):
        user_name = request.form['user-name']
        email_address = request.form['email-address']
        valid_new_user_info, message = self._validate_new_user_info(user_name, email_address)
        if valid_new_user_info:
            self._users.add_user(user_name, email_address)
            return redirect(f'/user/{user_name}')
        else:
            flash(message)
            return render_template('create_user.html')

    def _validate_new_user_info(self, user_name, email_address):
        valid_new_user_info = False
        if user_name in self._users.user_names:
            message = f'User ID, {user_name}, already exists. Enter another ID.'
        elif not self._validate_user_name(user_name):
            message = f'Invalid User Name: {user_name}'
        elif not self._validate_email_address(email_address):
            message = f'Invalid Email Address: {email_address}'
        else:
            valid_new_user_info = True
            message = ''
        return valid_new_user_info, message
    
    def _validate_user_name(self, user_name):
        regex = r'^[a-zA-Z0-9_.-]+$'
        return re.fullmatch(regex, user_name)
    
    def _validate_email_address(self, email_address):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return re.fullmatch(regex, email_address)

    def serve(self):
        serve(self.app, host='0.0.0.0', port=8080, threads=1)

    


if __name__ == '__main__':
    logger = logging.getLogger('Tasks')
    app = App('Tasks', logger)
    app.serve()
