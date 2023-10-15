from database import DatabaseManager 
from datetime import datetime

NOTES_SCHEMA = {
    'notes': {
        'id': 'INTEGER PRIMARY KEY',
        'emoji': 'TEXT',
        'title': 'TEXT',
        'content': 'TEXT',
        'date': 'TEXT',
        'last_modified': 'TEXT',
        'tags': 'TEXT'
    }
}
SETTINGS_SCHEMA = {
    'settings': {
        'summariser': 'TEXT',
        'qa': 'TEXT',
        'text_gen': 'TEXT',
        'openai_api_key': 'TEXT'

    }
}
AI_ASSISTANTS_SCHEMA = {
    'ai_assistants': {
        'id': 'INTEGER PRIMARY KEY',
        'name': 'TEXT',
        'temperature': 'REAL',
        'role': 'TEXT',
        'image_path': 'TEXT'
    }
}

from note_class import Note

class NotesDB(DatabaseManager):
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
        super().update_by_id(id, fields)

    def update_by_field(self, field, value, fields : dict, multiple = False):
        # as d/m/y hh:mm:ss
        fields['last_modified'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        super().update_by_field(field, value, fields, multiple)

    def get_by_field(self, field, value, multiple=False):
        n = super().get_by_field(field, value, multiple)
        if multiple:
            n = [Note(note) for note in n]
        else:
            n = Note(n)
        return n
    
    def get_all(self):
        all = super().get_all()
        all = [Note(note) for note in all]
        return all
    
class SettingsDB(DatabaseManager):
    def __init__(self, schema):
        super().__init__(schema)
        if not self.cursor.execute('''SELECT * FROM {}'''.format(self.db_name)).fetchone():
            self.set_default()
    # rewrite the get by field function to return the value in that field (assuming there is only one value)
    def set_default(self):
        self.cursor.execute('''INSERT INTO {} VALUES (?, ?, ?, ?)'''.format(self.db_name), ('OpenAI', 'OpenAI', 'OpenAI', ''))
        self.conn.commit()

    def get_by_field(self, field):
        try:
            return self.cursor.execute('''SELECT {} FROM {}'''.format(field, self.db_name)).fetchone()[0]
        except:
            return None
    
    def update_by_field(self, field, new_value):
        self.cursor.execute('''UPDATE {} SET {} = ?'''.format(self.db_name, field), (new_value,))
        self.conn.commit()
        
ArchiveNotes = NotesDB(NOTES_SCHEMA)
Settings = SettingsDB(SETTINGS_SCHEMA)
AIAssistantsDB = DatabaseManager(AI_ASSISTANTS_SCHEMA)
