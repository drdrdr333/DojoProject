from unittest import result
from flask_bcrypt import Bcrypt
from flask_app.models import user
from flask_app.config.mysqlconnection import connectToMySQL

my_db = 'final_schema'

class Event:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.location = data['location']
        self.members = data['members']
        self.date = data['date']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']



    @classmethod
    def get_user_events(cls, data):
        query = """
            select * from sporting_event
            join user_and_event on user_and_event.sporting_event_id = sporting_event.id
            join users on users.id = user_and_event.user_id
            where users.id = %(id)s;
        """

        result = connectToMySQL(my_db).query_db(query, {'id': data})
        
        return result


    @classmethod
    def get_members_joined(cls, data):
        query = """
                select count(user_and_event.user_id) as ActiveMembers from user_and_event
                left join sporting_event on sporting_event.id = user_and_event.sporting_event_id
                where sporting_event.id = %(id)s;
        """
        result = connectToMySQL(my_db).query_db(query, {'id': data})
        
        return result[0]

    
    @classmethod
    def get_all_events(cls):
        query = """
                Select * from sporting_event;
        """

        result = []
        results = connectToMySQL(my_db).query_db(query)

        for row in results:
            result.append(cls(row))
        return result

    
    @classmethod
    def get_searched_event(cls, data):
        query = """
                select * from sporting_event
                where id = %(id)s;
                """
        return connectToMySQL(my_db).query_db(query, data)


    @classmethod
    def add_event(cls, data):
        query = """
                Insert into sporting_event (name, location, members, date, user_id)
                Values (%(name)s, %(location)s, %(members)s, %(date)s, %(user_id)s)
                """
        
        return connectToMySQL(my_db).query_db(query, data)


    @classmethod
    def get_all_users_in_events(cls):
        query = """
                Select * from user_and_event
                """
        
        result = connectToMySQL(my_db).query_db(query)
        
        return result


    @classmethod
    def add_member_to_event(cls, data):
        query = """
                Insert into user_and_event (sporting_event_id, user_id)
                Values (%(sporting_event_id)s, %(user_id)s)
                """
        return connectToMySQL(my_db).query_db(query, data)

    
    @classmethod
    def select_event_messages(cls, data):
        query = """
                Select * from messages
                where sporting_event_id = %(id)s
                """
        return connectToMySQL(my_db).query_db(query, data)

    
    @classmethod
    def add_new_message(cls, data):
        query = """
                Insert into messages (text, user_id, sporting_event_id)
                Values (%(text)s, %(user_id)s, %(sporting_event_id)s)
                """
        return connectToMySQL(my_db).query_db(query, data)