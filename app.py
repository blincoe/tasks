import logging
import sqlite3
import pandas as pd
import re
from  flask import Flask, render_template, request, flash, url_for, redirect
from waitress import serve


class Task:
    def __init__(self):
        pass

class Users:
    def __init__(self, logger, conn):
        self._conn = conn
        self._logger = logger
        self._get_user_info_from_db()

    def _get_user_info_from_db(self):
        self.user_info = pd.read_sql('select * from users', self._conn)
        self.user_names = self.user_info['user_name'].unique()

    def add_user(self, user_name, email_address):
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


class App:
    def __init__(self, app_name, logger):
        self.app = Flask(app_name)
        self.app.secret_key = 'jfjfjhfdjkfd'

        self._logger = logger

        self._conn = sqlite3.connect('app.db', check_same_thread=False)

        self._add_endpoints()
        self._users = Users(logger, self._conn)
    
    def _add_endpoints(self):
        self.app.add_url_rule(rule='/', view_func=self._index)
        self.app.add_url_rule(rule='/login', view_func=self._login_home)
        self.app.add_url_rule(rule='/user-login', view_func=self._user_login, methods=['POST'])
        self.app.add_url_rule(rule='/create-user', endpoint='create-user', view_func=self._create_user, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/create-user-home', endpoint='create-user-home', view_func=self._create_user_home, methods=['POST', 'GET'])
        self.app.add_url_rule(rule='/user/<user_name>', endpoint='/user/<user_name>', view_func=self._user_login_home, methods=['POST', 'GET'])

    def _index(self):
        return redirect('/login')
    
    def _login_home(self):
        return render_template('login.html')
    
    def _create_user_home(self):
        return render_template('create_user.html')
    
    def _user_login(self):
        user_name = request.form['user-name']
        if user_name not in self._users.user_names:
            flash(f'User ID, {user_name}, does not exists. Enter another ID or create a new one.')
            return render_template('login.html')
        else:
            return redirect(f'/user/{user_name}')
    
    def _user_login_home(self, user_name):
            return render_template('user_home.html', user_name=user_name)
    
    def _create_user(self):
        user_name = request.form['user-name']
        email_address = request.form['email-address']
        valid_new_user_info, message = self._validate_new_user_info(user_name, email_address)
        if valid_new_user_info:
            self._users.add_user(user_name, email_address)
            return render_template('user_home.html')
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
