import logging
from mysql.connector import connect
import pandas as pd
import re
from  flask import Flask, render_template, request, flash, url_for, redirect, make_response
import datetime
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib


def send_mail(
        distribution_list, 
        email_subject, 
        sender_address, 
        smtp_server, 
        body, 
        sender_password=None,
        file_buffer=None, 
        output_file_name=None
        ):
    msg = MIMEMultipart()
    msg['From'] = sender_address
    msg['To'] = ';'.join(distribution_list)
    msg['Subject'] = email_subject
    msg.attach(MIMEText(body, "html"))

    if file_buffer is not None:
        part = MIMEApplication(file_buffer.getvalue(), Name=output_file_name)
        part['Content-Disposition'] = f'attachment; filename="{output_file_name}"' 
        msg.attach(part)

    with smtplib.SMTP(smtp_server) as smtp:
        if sender_password is not None:
            smtp.login(sender_address, sender_password)
        smtp.sendmail(sender_address, distribution_list, msg.as_string())


def tomorrow():
    return (datetime.datetime.now() + datetime.timedelta(1)).strftime('%Y-%m-%d')


class Tasks:
    def __init__(self, logger, conn):
        self._logger = logger
        self._conn = conn

        self._get_task_info_from_db()

    def _get_task_info_from_db(self):
        self._logger.info('Getting all tasks from database')
        proc = 'get_task_info'
        
        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc)
        proc_result = next(cursor.stored_results())
        table_rows = proc_result.fetchall()

        self.task_info = pd.DataFrame(table_rows, columns=proc_result.column_names).set_index('task_id')
        self._conn.close()

    def add_task(self, user_name, **kwargs):
        task_title = kwargs['task_title']
        task_description = kwargs['task_description']
        trigger_date = kwargs['trigger_date']
        if trigger_date == '':
            status = 'open'
            trigger_date = None
        else:
            status = 'scheduled'
            trigger_date = datetime.datetime.strptime(trigger_date, '%Y-%m-%d').date()

        self._logger.info(f'Adding task, {task_title}, from user, {user_name}, to database')

        proc = 'add_task'
            
        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc, [user_name, task_title, task_description, trigger_date, status])
        proc_result = next(cursor.stored_results())
        task_id, created_at, updated_at = proc_result.fetchone()
        self._conn.close()

        self.task_info = pd.concat([
            self.task_info,
            pd.DataFrame([[
                created_at, 
                updated_at, 
                user_name, 
                task_title, 
                task_description, 
                trigger_date, 
                status
                ]], columns=self.task_info.columns, index=[task_id]).astype(self.task_info.dtypes)
        ])
        

    def get_task_info(self, task_id):
        return self.task_info.loc[int(task_id)].to_dict()
    
    def get_tasks_for_user(self, user_name, status=None):
        if status is None:
            return self.task_info.loc[self.task_info['user_name'] == user_name]
        else:
            return self.task_info.loc[(self.task_info['user_name'] == user_name) & (self.task_info['status'] == status)]
        
    def get_task_table_for_user_and_status(self, user_name, closed_task_display_count_preference, status):
        tasks_df = self.get_tasks_for_user(user_name, status)
        if len(tasks_df) == 0:
            task_html = 'None'
        else:
            tasks_df.loc[:, 'task_description'] = tasks_df.apply(lambda r_: r_['task_description'].replace('\r\n', '<br>'), axis=1)
            date_header = {'open': 'Created Date', 'scheduled': 'Trigger Date', 'closed': 'Close Date'}[status]
            date_column = {'open': 'created_at', 'scheduled': 'trigger_date', 'closed': 'updated_at'}[status]
            task_html = f'''
                <table cellpadding=1 cellspacing=0>
                    <col width="100">
                    <col width="190">
                    <col width="90">
                    <tr bgcolor="#002060", style="color:white;" align="center">
                        <th>Title</th>
                        <th>Description</th>
                        <th>{date_header}</th>
                    </tr>
                '''
            if status == 'closed':
                df = tasks_df.sort_values(date_column, ascending=False).head(int(closed_task_display_count_preference))
            else:
                df = tasks_df.sort_values(date_column, ascending=True)
            for task_id, r_ in df.iterrows():
                if isinstance(r_[date_column], str):
                    date_col_val = r_[date_column]
                else:
                    date_col_val = r_[date_column].strftime('%Y-%m-%d')
                task_html += f'''
                    <tr>
                        <td><a href="{url_for('/task/<task_id>', task_id=task_id, _external=True)}">{r_['task_title']}</a></td>
                        <td>{r_['task_description']}</td>
                        <td align="center">{date_col_val}</td>
                    </tr>
                    '''
            task_html += '</table>'
        return task_html
    
    def close_task(self, task_id):

        self._logger.info(f'Closing task, {task_id}')

        status, updated_at = 'closed', datetime.datetime.now()

        proc = 'close_task'

        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc, [status, updated_at, task_id])
        proc_result = next(cursor.stored_results())
        created_at, user_name, task_title, task_description, trigger_date = proc_result.fetchone()
        self._conn.close()

        self.task_info.loc[int(task_id), ['created_at', 'updated_at', 'user_name', 'task_title', 'task_description', 'trigger_date', 'status']] = [
            created_at, 
            str(updated_at), 
            user_name, 
            task_title, 
            task_description, 
            trigger_date, 
            status
            ]
    
    def delete_task(self, task_id):

        self._logger.info(f'deleting task, {task_id}')

        proc = 'delete_task'

        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc, [task_id])
        self._conn.close()

        self.task_info.drop(int(task_id), inplace=True)
    
    def update_task(self, task_id, **kwargs):
        task_title = kwargs['task_title']
        task_description = kwargs['task_description']
        trigger_date = kwargs['trigger_date']
        self._logger.info(f'Updating task, {task_id}')
        if trigger_date == '':
            status = 'open'
            trigger_date = None
        else:
            status = 'scheduled'

        updated_at = datetime.datetime.now()

        proc = 'update_task'

        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc, [task_title, task_description, trigger_date, status, updated_at, task_id])
        proc_result = next(cursor.stored_results())
        created_at, user_name  = proc_result.fetchone()
        self._conn.close()

        self.task_info.loc[int(task_id), ['created_at', 'updated_at', 'user_name', 'task_title', 'task_description', 'trigger_date', 'status']] = [
            created_at, 
            updated_at, 
            user_name, 
            task_title, 
            task_description, 
            trigger_date, 
            status
            ]


class Users:
    def __init__(self, logger, conn):
        self._logger = logger
        self._conn = conn

        self._get_user_info_from_db()

    def _get_user_info_from_db(self):
        self._logger.info('Getting all users from database')
        proc = 'get_user_info'

        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc)
        proc_result = next(cursor.stored_results())
        table_rows = proc_result.fetchall()

        self.user_info = pd.DataFrame(table_rows, columns=proc_result.column_names).set_index('user_name')
        self._conn.close()

    def add_user(self, **kwargs):
        user_name = kwargs['user_name']
        email_address = kwargs['email_address']
        summary_notification_preference = kwargs['summary_notification_preference']
        trigger_notification_preference = kwargs['trigger_notification_preference']
        closed_task_display_count_preference = kwargs['closed_task_display_count_preference']
        self._logger.info(f'Adding user, {user_name}, to database')
        proc = 'add_user'

        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc, [user_name, email_address, summary_notification_preference, trigger_notification_preference, closed_task_display_count_preference])
        proc_result = next(cursor.stored_results())
        created_at, updated_at = proc_result.fetchone()
        self._conn.close()
        
        self.user_info.loc[user_name] = [created_at, updated_at, email_address, summary_notification_preference, trigger_notification_preference, closed_task_display_count_preference]

    def get_user_info(self, user_name):
        return self.user_info.loc[user_name].to_dict()
    
    def delete_user(self, user_name):

        self._logger.info(f'deleting user, {user_name}')

        proc = 'delete_user'
        
        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc, [user_name])
        self._conn.close()

        self.user_info.drop(user_name, inplace=True)
    
    def update_user(self, user_name, **kwargs):
        email_address = kwargs['email_address']
        summary_notification_preference = kwargs['summary_notification_preference']
        trigger_notification_preference = kwargs['trigger_notification_preference']
        closed_task_display_count_preference = kwargs['closed_task_display_count_preference']
        self._logger.info(f'updating user, {user_name}')

        updated_at = datetime.datetime.now()

        proc = 'update_user'
        
        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc, [updated_at, email_address, summary_notification_preference, trigger_notification_preference, closed_task_display_count_preference, user_name])
        proc_result = next(cursor.stored_results())
        created_at = proc_result.fetchone()
        self._conn.close()


        self.user_info.loc[user_name, ['created_at', 'updated_at', 'email_address', 'summary_notification_preference', 'trigger_notification_preference', 'closed_task_display_count_preference']] = [
            created_at[0], 
            updated_at, 
            email_address, 
            summary_notification_preference, 
            trigger_notification_preference,
            closed_task_display_count_preference
            ]
    
    def _purge_inactive_users(self):
        self._logger.info(f'purging inactive users')

        proc = 'purge_inactive_users'
        
        self._conn.reconnect()
        cursor = self._conn.cursor()
        cursor.callproc(proc)
        self._conn.close()

        self._get_user_info_from_db()
     


class App:
    def __init__(self, app_name, logger, wd=''):
        self.app = Flask(app_name, template_folder=f'{wd}templates')
        self.app.secret_key = 'jfjfjhfdjkfd'

        self._logger = logger

        db_args = {
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASS'),
            'host': os.getenv('MYSQL_HOST'),
            'database': os.getenv('MYSQL_TASKS_DB'),
            'autocommit': True
        }

        self._conn = connect(**db_args)

        self._add_endpoints()
        self._users = Users(logger, self._conn)
        self._tasks = Tasks(logger, self._conn)

        self._sender_address = os.getenv('TASKCUR_NOTIFICATIONS_ADDRESS')
        self._smtp_server = os.getenv('TASKCUR_NOTIFICATIONS_SERVER')

    
    def _add_endpoints(self):
        self.app.add_url_rule(rule='/', view_func=self._index)
        self.app.add_url_rule(rule='/login', view_func=self._login_home)
        self.app.add_url_rule(rule='/user-login', view_func=self._user_login, methods=['POST'])
        self.app.add_url_rule(rule='/create-user', endpoint='create-user', view_func=self._create_user, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/create-user-home', endpoint='create-user-home', view_func=self._create_user_home, methods=['POST', 'GET'])

        self.app.add_url_rule(rule='/user/<user_name>', endpoint='/user/<user_name>', view_func=self._user_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>/create-task-home', endpoint='/user/<user_name>/create-task-home', view_func=self._create_task_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>/create-task', endpoint='/user/<user_name>/create-task', view_func=self._create_task, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>/delete', endpoint='/user/<user_name>/delete', view_func=self._delete_user, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>/update-home', endpoint='/user/<user_name>/update-home', view_func=self._update_user_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>/update', endpoint='/user/<user_name>/update', view_func=self._update_user, methods=['POST', 'GET'])


        self.app.add_url_rule(rule='/task/<task_id>', endpoint='/task/<task_id>', view_func=self._task_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/close', endpoint='/task/<task_id>/close', view_func=self._close_task, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/close-home', endpoint='/task/<task_id>/close-home', view_func=self._close_task_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/delete', endpoint='/task/<task_id>/delete', view_func=self._delete_task, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/modify-task-options', endpoint='/task/<task_id>/modify-task-options', view_func=self._modify_task_options, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/close-task-options', endpoint='/task/<task_id>/close-task-options', view_func=self._close_task_options, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/update', endpoint='/task/<task_id>/update', view_func=self._update_task, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/update-home', endpoint='/task/<task_id>/update-home', view_func=self._update_task_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/task/<task_id>/close-and-recreate', endpoint='/task/<task_id>/close-and-recreate', view_func=self._close_task_and_recreate, methods=['POST', 'GET'])

        self.app.add_url_rule(rule='/weekly-summary', endpoint='/weekly-summary', view_func=self._weekly_summary, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/daily-task-trigger', endpoint='/daily-task-trigger', view_func=self._daily_task_trigger, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/purge-inactive-users', endpoint='/purge-inactive-users', view_func=self._purge_inactive_users, methods=['POST', 'GET'])

        self.app.after_request(self._add_response_headers)

    def _index(self):
        return redirect('/login')
    
    def _login_home(self):
        return render_template('login.html')
    
    def _create_user_home(self):
        return render_template('create_user.html')
    
    def _update_user_home(self, user_name):
        user_info = self._users.get_user_info(user_name)
        return render_template(
            'update_user.html',
            user_name=user_name,
            **user_info
            )
    
    def _update_user(self, user_name):
        self._users.update_user(user_name, **request.form)
        user_info = self._users.get_user_info(user_name)
        flash(f'User Updated')
        return render_template(
            'update_user.html',
            user_name=user_name,
            **user_info
            )

    def _update_task_home(self, task_id):
        task_info = self._tasks.get_task_info(task_id)
        if task_info['status'] == 'scheduled':
            task_status = f"Scheduled - {task_info['trigger_date']}"
        else:
            task_status = task_info['status']
        return render_template(
            'update_task.html',
            task_id=task_id,
            task_status=task_status,
            min_date=tomorrow(),
            **task_info
            )
    
    def _update_task(self, task_id):
        self._tasks.update_task(task_id, **request.form)
        task_info = self._tasks.get_task_info(task_id)
        if task_info['status'] == 'scheduled':
            task_status = f"Scheduled - {task_info['trigger_date']}"
        else:
            task_status = task_info['status']
        flash(f'Task Updated')
        return render_template(
            'update_task.html',
            task_id=task_id,
            task_status=task_status,
            min_date=tomorrow(),
            **task_info
            )
    
    def _close_task(self, task_id):
        task_info = self._tasks.get_task_info(task_id)
        self._tasks.close_task(task_id)
        user_name = task_info['user_name']
        return redirect(f'/user/{user_name}')

    def _close_task_and_recreate(self, task_id):
        task_info = self._tasks.get_task_info(task_id)
        self._tasks.close_task(task_id)
        return render_template(
            'recreate_task.html',
            min_date=tomorrow(),
            **task_info
            )
    
    def _close_task_home(self, task_id):
        task_info = self._tasks.get_task_info(task_id)
        task_info['task_description'] = task_info['task_description'].replace('\r\n', '<br>')
        if task_info['status'] == 'scheduled':
            task_status = f"Scheduled - {task_info['trigger_date']}"
        else:
            task_status = task_info['status']
        return render_template(
            'close_task_home.html',
            task_id=task_id,
            task_status=task_status,
            **task_info
            )
    
    def _task_home(self, task_id):
        task_info = self._tasks.get_task_info(task_id)
        task_info['task_description'] = task_info['task_description'].replace('\r\n', '<br>')
        if task_info['status'] == 'scheduled':
            task_status = f"Scheduled - {task_info['trigger_date']}"
        else:
            task_status = task_info['status']
        return render_template(
            'task_home.html',
            task_id=task_id,
            task_status=task_status,
            **task_info
            )
    
    def _create_task_home(self, user_name):
        return render_template('create_task.html', user_name=user_name, min_date=tomorrow())
    
    def _create_task(self, user_name):
        self._tasks.add_task(user_name, **request.form)
        flash(f'Task Created')
        return render_template('create_task.html', user_name=user_name, min_date=tomorrow())
    
    def _user_login(self):
        user_name = request.form['user_name']
        if user_name not in self._users.user_info.index:
            flash(f'User ID, {user_name}, does not exists. Enter another ID or create a new one.')
            return render_template('login.html')
        else:
            return redirect(f'/user/{user_name}')
    
    def _user_home(self, user_name):
        user_info = self._users.get_user_info(user_name)
        closed_task_display_count_preference = user_info['closed_task_display_count_preference']
        open_task_html = self._tasks.get_task_table_for_user_and_status(user_name, closed_task_display_count_preference, 'open')
        scheduled_task_html = self._tasks.get_task_table_for_user_and_status(user_name, closed_task_display_count_preference, 'scheduled')
        closed_task_html = self._tasks.get_task_table_for_user_and_status(user_name, closed_task_display_count_preference, 'closed')
        return render_template(
            'user_home.html', 
            user_name=user_name,
            open_tasks=open_task_html,
            scheduled_tasks=scheduled_task_html,
            closed_tasks=closed_task_html,
            )
    
    def _add_response_headers(self, response):
        response.headers['Cache-Control'] = 'no-cache, no-store'
        response.headers['Pragma'] = 'no-cache'
        return response
    
    def _create_user(self):
        form = request.form.to_dict()
        form['user_name'] = form['user_name'].strip()
        form['email_address'] = form['email_address'].replace(' ', '')
        valid_new_user_info, message = self._validate_new_user_info(**form)
        if valid_new_user_info:
            self._users.add_user(**form)
            user_name = form['user_name']
            return redirect(f'/user/{user_name}')
        else:
            flash(message)
            return render_template('create_user.html')

    def _validate_new_user_info(self, **kwargs):
        valid_new_user_info = False
        user_name = kwargs.get('user_name')
        email_address = kwargs.get('email_address')
        if user_name in self._users.user_info.index:
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
        return all([bool(re.fullmatch(regex, x_)) for x_ in email_address.split(',')])
    
    def _modify_task_options(self, task_id):
        if request.form['action'] == 'Update Task':
            return redirect(f'/task/{task_id}/update-home')
        elif request.form['action'] == 'Close Task':
            return redirect(f'/task/{task_id}/close-home')
        else:
            raise ValueError(f"unknown  value: {request.form['action']}")
    
    def _close_task_options(self, task_id):
        if request.form['action'] == 'Close Task':
            return redirect(f'/task/{task_id}/close')
        elif request.form['action'] == 'Close Task and Re-Create':
            return redirect(f'/task/{task_id}/close-and-recreate')
        else:
            raise ValueError(f"unknown  value: {request.form['action']}")
    
    def _delete_task(self, task_id):
        task_info = self._tasks.get_task_info(task_id)
        self._tasks.delete_task(task_id)
        user_name = task_info['user_name']
        return redirect(f'/user/{user_name}')
    
    def _delete_user(self, user_name):
        self._users.delete_user(user_name)
        return redirect('/login')

    def _weekly_summary_for_user(self, user_name):
        user_info = self._users.get_user_info(user_name)
        closed_task_display_count_preference = user_info['closed_task_display_count_preference']
        email_address = user_info['email_address'].split(',')
        open_task_html = self._tasks.get_task_table_for_user_and_status(user_name, closed_task_display_count_preference, 'open')
        scheduled_task_html = self._tasks.get_task_table_for_user_and_status(user_name, closed_task_display_count_preference, 'scheduled')
        closed_task_html = self._tasks.get_task_table_for_user_and_status(user_name, closed_task_display_count_preference, 'closed')
        summary_html = render_template(
            'user_summary.html', 
            user_name=user_name,
            open_tasks=open_task_html,
            scheduled_tasks=scheduled_task_html,
            closed_tasks=closed_task_html,
            )
        open_task_count = len(self._tasks.get_tasks_for_user(user_name, 'open'))
        scheduled_task_count = len(self._tasks.get_tasks_for_user(user_name, 'scheduled'))
        if open_task_count + scheduled_task_count > 0:
            send_mail(
                distribution_list=email_address, 
                email_subject=f'TaskCur Summary for {user_name}',
                sender_address=self._sender_address,
                smtp_server=self._smtp_server,
                body=summary_html,
                sender_password=os.getenv('TASKCUR_NOTIFICATIONS_PW'),
                )

    def _weekly_summary(self):
        for user_name, user_info in self._users.user_info.iterrows():
            if user_info['summary_notification_preference'] == 'weekly:friday':
                self._weekly_summary_for_user(user_name)
        return ('', 204)

    def _daily_task_trigger(self):
        today = datetime.date.today()
        triggered_tasks = self._tasks.task_info.loc[self._tasks.task_info['trigger_date'] <= today, ]
        for task_id, triggered_task_info in triggered_tasks.iterrows():
            self._tasks.update_task(
                task_id=task_id, 
                task_title=triggered_task_info['task_title'], 
                task_description=triggered_task_info['task_description'], 
                trigger_date=''
                )
            user_name = triggered_task_info['user_name']
            user_info = self._users.get_user_info(user_name)
            if user_info['trigger_notification_preference'] == 'email':
                self._send_task_trigger_email(task_id, triggered_task_info)
        return ('', 204)

    def _send_task_trigger_email(self, task_id, triggered_task_info):
        user_name = triggered_task_info['user_name']
        email_address = self._users.get_user_info(user_name)['email_address'].split(',')
        trigger_html = render_template(
            'task_trigger.html', 
            task_id=task_id,
            user_name=user_name,
            task_title=triggered_task_info['task_title'],
            task_description=triggered_task_info['task_description'],
            )
        send_mail(
            distribution_list=email_address, 
            email_subject=f"Task Triggered: {triggered_task_info['task_title']}",
            sender_address=self._sender_address,
            smtp_server=self._smtp_server,
            body=trigger_html,
            sender_password=os.getenv('TASKCUR_NOTIFICATIONS_PW'),
            )
    
    def _purge_inactive_users(self):
        self._users._purge_inactive_users()
        return ('', 204)

    def serve(self):
        from waitress import serve
        serve(self.app, host='0.0.0.0', port=8080, threads=1)

    def run(self, debug=False):
        self.app.run(debug=debug)

    


if __name__ == '__main__':
    logger = logging.getLogger('Tasks')
    app = App('Tasks', logger)
    app.serve()
