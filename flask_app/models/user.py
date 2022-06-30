
from unittest import result
from flask import flash
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import event
import re

my_db = 'final_schema'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
LTR_REGEX = re.compile("^[a-zA-Z]+$")

class User:
    def __init__(self, data):
        """
        Mirrors the model for the database
        allows us to create a user that can be mirrored within
        the database
        """
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.birth_date = data['birth_date']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @staticmethod
    def validate_user(data):
        """
        we have to start with the assumption that the data
        is valid because if our conditional evaluates to true
        the is_valid variable will be false
        """
        is_valid = True
        if (len(data['first_name']) <= 2) or not LTR_REGEX.match(data['first_name']):
            flash("First name must only be letters, not #'s and must be at least 2 letters.", 'register')
            is_valid = False
        if (len(data['last_name']) <= 2) or not LTR_REGEX.match(data['last_name']):
            flash("Last name must only be letters, not #'s and must be at least 2 letters.", 'register')
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash('Invalid email address. Please retry.', 'register')
            is_valid = False
        if User.get_user_by_email({'email': data['email']}):
            flash('Email already in use!', 'register')
            is_valid = False
        if len(data['password']) <= 8:
            flash("Password must be greater than 8 characters. Please retry.", 'register')
            is_valid = False
        if data['password'] != data['conf_pw']:
            flash('Password confirmation does not match password. Please retry.', 'register')
            is_valid = False  
        return is_valid

    
    @classmethod
    def add_user(cls, data):
        query = """
            Insert into users (first_name, last_name, email, password, birth_date)
            Values (%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(birth_date)s)
        """

        result = connectToMySQL(my_db).query_db(query, data)
        
        return result

    
    @classmethod
    def get_newest_user(cls):
        query = """
            Select * from users
            Order by id Desc 
            Limit 1;
        """

        result = connectToMySQL(my_db).query_db(query)
        return User(result[0])

    
    @classmethod
    def get_user_by_email(cls, data):
        query = """
            Select * from users
            Where email = %(email)s
                """
        
        result = connectToMySQL(my_db).query_db(query, data)
        
        if result == ():
            return False
        else:
            return cls(result[0])

    
    @classmethod
    def get_creators_of_events(cls, data):
        query = """
                select first_name, last_name from users
                left join sporting_event on users.id = sporting_event.user_id
                where sporting_event.user_id in %(ids)s
                order by sporting_event.id;
                """
        
        result = connectToMySQL(my_db).query_db(query, {'ids': data})
        
        return result

    
    @classmethod
    def get_user_by_id(cls, data):
        query = """
                Select first_name, last_name from users
                where id=%(id)s
                """
        return connectToMySQL(my_db).query_db(query, {'id': data})


    @classmethod
    def get_user_by_first_name(cls, data):
        query = """
                Select * from users
                where first_name like %(first_name)s
                """
        result = connectToMySQL(my_db).query_db(query, {'first_name': data})
        return cls(result[0])        