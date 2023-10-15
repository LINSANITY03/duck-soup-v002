'''
author: @robsca (github)
date  : 2023-10-15

Rewriting the database module to using a more dynamic approach
'''
import sqlite3

class DatabaseManager:
    '''
    ```python
    SCHEMA_EXAMPLE = {
    'testing': {
        'id': 'INTEGER PRIMARY KEY',
        'title': 'TEXT',
        'content': 'TEXT',
        }

    }

    db = DatabaseManager(SCHEMA_EXAMPLE)
    db.add_element({
        'title': 'test',
        'content': 'test'
    })
    db.update_by_id(1, {
        'title': 'test2',
        'content': 'test2'
    })
    db.update_by_field('title', 'test2', {
        'title': 'test3',
        'content': 'test3'
    })
    db.delete_by_field('title', 'test3')
    db.delete_by_field('title', 'test3', multiple = True)
    db.get_all()
    db.get_by_field('title', 'test3')
    db.get_by_field('title', 'test3', multiple = True)
    db.get_schema()
    ```
    '''
    def __init__(self, SCHEMA: dict):
        self.SCHEMA = SCHEMA
        self.db_name =  str(list(self.SCHEMA.keys())[0])
        self.conn = sqlite3.connect('databases/' + self.db_name + '.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        '''
        Creates a table in the database if it doesn't exist already - it uses the schema to create the table
        '''
        ''''''
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.db_name} ({', '.join([f'{key} {value}' for key, value in self.SCHEMA[self.db_name].items()]) }
        )''')
        self.conn.commit()
    
    def add_element(self, fields : dict):
        '''
        parameters:
        fields: a dictionary with the keys being the column names and the values being the values to insert
        '''
        self.cursor.execute('''INSERT INTO {} VALUES (NULL, {})'''.format(self.db_name, ', '.join(['?' for _ in fields.keys()])), (*fields.values(),))
        self.conn.commit()
    
    def update_by_id(self, id, fields : dict):
        '''
        parameters:
        id: the id of the record to update
        fields: a dictionary with the keys being the column names and the values being the values to update
        '''
        self.cursor.execute('''UPDATE {} SET {} WHERE id = ?'''.format(self.db_name, ', '.join([f'{key} = ?' for key in fields.keys()])), (*fields.values(), id))
        self.conn.commit()

    def update_by_field(self, field, value, fields : dict, multiple = False):
        '''
        parameters:
        field: the field to search by
        value: the value to search by
        fields: a dictionary with the keys being the column names and the values being the values to update
        multiple: whether to update multiple records or not

        Example:
        ```python
        # I want to update the record with the title 'test' to have the title 'test2' and the content 'test2'

        new_values = {
            'title': 'test2',
            'content': 'test2'
        }
        db.update_by_field('title', 'test', new_values)

        '''
        if multiple:
            self.cursor.execute('''UPDATE {} SET {} WHERE {} = ?'''.format(self.db_name, ', '.join([f'{key} = ?' for key in fields.keys()]), field), (*fields.values(), value))
        else:
            # need to check if more than one record is returned
            how_many = self.cursor.execute('''SELECT * FROM {} WHERE {} = ?'''.format(self.db_name, field), (value,)).fetchall()
            if len(how_many) > 1:
                raise Exception("More than one record returned")
            else:
                self.cursor.execute('''UPDATE {} SET {} WHERE {} = ?'''.format(self.db_name, ', '.join([f'{key} = ?' for key in fields.keys()]), field), (*fields.values(), value))
        self.conn.commit()

    def delete_by_field(self, field, value, multiple = False):
        if multiple:
            self.cursor.execute('''DELETE FROM {} WHERE {} = ?'''.format(self.db_name, field), (value,))
        else:
            how_many = self.cursor.execute('''SELECT * FROM {} WHERE {} = ?'''.format(self.db_name, field), (value,)).fetchall()
            if len(how_many) > 1:
                raise Exception("More than one record returned")
            else:
                self.cursor.execute('''DELETE FROM {} WHERE {} = ?'''.format(self.db_name, field), (value,))
        self.conn.commit()

    def get_all(self):
        self.cursor.execute('''SELECT * FROM {}'''.format(self.db_name))
        return self.cursor.fetchall()
    
    def get_by_field(self, field, value, multiple = False):
        self.cursor.execute('''SELECT * FROM {} WHERE {} = ?'''.format(self.db_name, field), (value,)) 
        return self.cursor.fetchall() if multiple else self.cursor.fetchone() 
    
    def get_schema(self):
        return self.SCHEMA[self.db_name]

if __name__ == "__main__":

    NOTES_SCHEMA = {
        'test': {
            'id': 'INTEGER PRIMARY KEY',
            'emoji': 'TEXT',
            'title': 'TEXT',
            'content': 'TEXT',
            'date': 'TEXT',
            'last_modified': 'TEXT',
            'tags': 'TEXT'
        }
    }

    NotesDB = DatabaseManager(NOTES_SCHEMA)
    # add a note
    print(NotesDB.get_all())
    print(len(NotesDB.get_all()))
    
    NotesDB.add_element({
        'emoji': '📝',
        'title': 'test',
        'content': 'test',
        'date': '',
        'last_modified': '',
        'tags': ''
    })

    print(NotesDB.get_all())
    print(len(NotesDB.get_all()))


    # update a note
    NotesDB.update_by_field('title', 'test', {
        'emoji': '📝',
        'title': 'test',
        'content': 'test',
        'date': '',
        'last_modified': '',
        'tags': ''
    })
