from classes.sqlite3_manager import SQLite3Manager
from classes.firestore_connection import FirestoreManager
from datetime import datetime

NOTES_SCHEMA = {
    'notes': {
        'id': 'INTEGER PRIMARY KEY',
        'emoji': 'TEXT',
        'title': 'TEXT',
        'content': 'TEXT',
        'date': 'TEXT',
        'last_modified': 'TEXT',
        'tags': 'TEXT',
        'user_id': 'TEXT'
    }
}
SETTINGS_SCHEMA = {
    'settings': {
        'summariser': 'TEXT',
        'qa': 'TEXT',
        'text_gen': 'TEXT',
        'openai_api_key': 'TEXT',
        'user_id': 'TEXT'

    }
}
AI_ASSISTANTS_SCHEMA = {
    'ai_assistants': {
        'id': 'INTEGER PRIMARY KEY',
        'name': 'TEXT',
        'temperature': 'REAL',
        'role': 'TEXT',
        'image_path': 'TEXT',
        'user_id': 'TEXT'
    }
}

from classes.note_class import Note

class NotesDB(FirestoreManager):
    def __init__(self, schema, user_id):
        super().__init__(schema)
        self.user_id = user_id
        self.set_default()
    
    def add_element(self, fields : dict):
        fields['date'] = str(datetime.now().strftime(
            '%Y-%m-%d'
        )) if fields['date'] == '' else fields['date']

        fields['last_modified'] = str(datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        ))
        super().add_element(fields)

    def update_by_id(self, id, fields : dict):
        fields['last_modified'] = str(datetime.now())
        # check the user id
        if self.get_by_field('id', id).user_id == self.user_id:
            super().update_by_id(id, fields)

    def update_by_field(self, field, value, fields : dict, multiple = False):
        # as d/m/y hh:mm:ss
        fields['last_modified'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # user id check
        if multiple:
            for note in self.get_by_field(field, value, multiple=True):
                if note.user_id == self.user_id:
                    super().update_by_field(field, value, fields, multiple)
        else:
            if self.get_by_field(field, value).user_id == self.user_id:

                super().update_by_field(field, value, fields, multiple)

    def get_by_field(self, field, value, multiple=False):
        n = super().get_by_field(field, value, multiple)
        if multiple:
            n = [Note(note) for note in n]
        else:
            n = Note(n)
        return n
    
    def get_all_for_the_user(self):
        # take the ones that match the user id filtering the user_id
        all = self.db.collection(self.collection_name).get()
        all = [a.to_dict() for a in all if a.to_dict()['user_id'] == self.user_id]
        all = [Note(a) for a in all]
        return all
    
    def set_default(self):
        if not self.get_all():
            self.add_element({
                'id': '0',
                'emoji': '📝',
                'title': 'Welcome to Duck Soup!',
                'content': 'To get started, click on the "New Note" button on the nav bar.',
                'date': '',
                'last_modified': '',
                'tags': '',
                'user_id': self.user_id

            })
class SettingsDB(FirestoreManager):
    def __init__(self, schema, user_id):
        self.user_id = user_id
        super().__init__(schema)
        self.set_default()

    def get_all(self):
        # take the ones that match the user id
        settings = super().get_all()
        settings = [s for s in settings if s['user_id'] == self.user_id]
        return settings

    # rewrite the get by field function to return the value in that field (assuming there is only one value)
    def set_default(self):
        if not self.get_all():
            self.add_element({
                'summariser': 'OpenAI',
                'qa': 'OpenAI',
                'text_gen': 'OpenAI',
                'openai_api_key': '',
                'user_id': self.user_id
            })

    def get_by_value_at_field(self, field):
        # take the ones that match the user id
        ai = super().get_by_value_at_field(field)
        ai = [a[field] for a in ai if a['user_id'] == self.user_id]
        return ai[0]
    
    def update_by_field(self, field, new_value):
        # take the ones that match the user id
        setting = super().get_by_field('user_id', self.user_id)
        setting[field] = new_value
        super().update_by_field('user_id', self.user_id, setting)
class AIAssistantDB_(FirestoreManager):
    # assign the default values to the AI assistants database
    def __init__(self, schema, user_id):
        self.user_id = user_id
        super().__init__(schema)
        self.set_default()
    def get_all(self):
        # take the ones that match the user id
        ai = super().get_all()
        ai = [a for a in ai if a['user_id'] == self.user_id]
        return ai

    def set_default(self):
        if not self.get_all():
            self.add_element({
                'name': 'Elon Musk',
                'temperature': 0.7,
                'role': 'Your friendly neighbourhood billionaire',
                'image_path': 'data:image/jpeg;base64,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',
                'user_id': self.user_id
            })
            self.add_element({
                'name': 'Albert Einstein',
                'temperature': 0.7,
                'role': 'Your friendly neighbourhood physicist',
                'image_path': 'https://media-cldnry.s-nbcnews.com/image/upload/t_fit-1500w,f_auto,q_auto:best/msnbc/Components/Photos/z_Projects_in_progress/050418_Einstein/050405_einstein_tongue.jpg',
                'user_id': self.user_id
            })
