'''
This file contains the class for the note object.
'''
import streamlit as st
class Note:
    ''' the note takes a list of values from the database and converts it into a note object'''
    def __init__(self, note : dict, db_name = 'databases/notes.db'):
        # from dict to list if needed
        self.id = note['id']
        self.emoji = note['emoji'] 
        self.title = note['title']
        self.content = note['content']
        self.date = note['date']
        self.last_modified = note['last_modified']
        self.tags = note['tags']
        self.user_id = note['user_id']
        self.fields = ['emoji', 'title', 'content', 'date', 'last_modified', 'tags', 'id']

    def update(self, field = None, value = None, save = True, fields : dict = None):
        if field and value is None and fields is None:
            raise Exception("Value not found")
        if value and field is None and fields is None:
            raise Exception("Field not found")
        if field not in self.fields and fields is None:
            raise Exception("Field not found")
        if field and value and fields is None:
            self.__dict__[field] = value
            if save:
                self.db_manager.update(
                    self.id,
                    self.emoji,
                    self.title,
                    self.content,
                    self.date,
                    self.last_modified,
                    self.tags
                )
        if not field and not value and fields:
            for field, value in fields.items():
                self.__dict__[field] = value
            self.db_manager.update(
                *fields
            )
            print('updated')
        return self.__dict__
    
    def __str__(self) -> str:
        # if content is too long, only show the first 100 characters
        #print(self.__dict__)
        return '\n'.join([f'{key}: {value if key != "content" else value[:100] if len(value) >100 else value}' for key, value in self.__dict__.items()])
    
    def is_on_db(self):
        # return true if all the fields are the same
        query = self.db_manager.cursor.execute('''SELECT * FROM notes WHERE id = ? and emoji = ? and title = ? and content = ? and date = ? and last_modified = ? and tags = ?''', (self.id, self.emoji, self.title, self.content, self.date, self.last_modified, self.tags)).fetchone()
        return True if query else False

class Archive:
    def __init__(self, notes):
        self.notes = [Note(note)for note in notes]

    def __getitem__(self, index):
        return self.notes[index]
    
    def __len__(self):
        return len(self.notes)
    