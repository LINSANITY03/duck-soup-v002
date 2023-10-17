#https://firebase.google.com/docs/firestore/manage-data/add-data
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st

class FirestoreManager:
    def __init__(self, schema):
        # Use the application default credentials.
        cred = credentials.Certificate(dict(st.secrets['firebase']))
        self.schema = schema
        try:
            firebase_admin.initialize_app(cred)
        except:
            pass
        self.db = firestore.client()
        self.collection_name = list(self.schema.keys())[0]

    def add_element(self, fields : dict):
        name = fields['id'] if 'id' in fields  else list(fields.values())[0]
        doc_ref = self.db.collection(self.collection_name).document(name)
        doc_ref.set(fields)
        print('Added element: {}'.format(fields))

    def update_by_id(self, id, fields : dict):
        doc_ref = self.db.collection(self.collection_name).document(id)
        doc_ref.update(fields)
        print('Updated element: {}'.format(fields))

    def update_by_field(self, field, value, fields : dict, multiple = False):
        notes_ref = self.db.collection(self.collection_name)
        query = notes_ref.where(field, '==', value)
        results = query.get()
        for result in results:
            result.reference.update(fields)
        print('Updated element: {}'.format(fields))

    def update_single_field(self, field, new_value):
        # use the field as a column and the new_value as the value
        #example field = 'title', new_value = 'new title'
        notes_ref = self.db.collection(self.collection_name)
        # i dont need to use where because i want to update all the elements
        query = notes_ref
        results = query.get()
        for result in results:
            result.reference.update({field: new_value})
        print('Updated element: {}'.format(new_value))

    def delete_by_field(self, field, value, multiple = False):
        notes_ref = self.db.collection(self.collection_name)
        query = notes_ref.where(field, '==', value)
        results = query.get()
        for result in results:
            result.reference.delete()
        print('Deleted element: {}'.format(value))

    def get_all(self):
        notes_ref = self.db.collection(self.collection_name)
        all_notes = notes_ref.stream()
        all_notes = [note.to_dict() for note in all_notes]
        return all_notes

    def get_by_field(self, field, value, multiple = False):
        notes_ref = self.db.collection(self.collection_name)
        query = notes_ref.where(field, '==', value)
        results = query.get()
        res = [result.to_dict() for result in results] 
        return res if multiple else res[0] if res else None
    
    def get_by_value_at_field(self, field):
        notes_ref = self.db.collection(self.collection_name)
        query = notes_ref.order_by(field)
        results = query.get()
        res = [result.to_dict() for result in results] 
        return res
    
    def get_schema(self):
        return self.schema[self.collection_name]

    def delete_all(self):
        notes_ref = self.db.collection(self.collection_name)
        query = notes_ref.get()
        for result in query:
            result.reference.delete()
        print('Deleted all elements')
        
if __name__ == '''__main__''':
    SHEMA = {
        'notes': {
            'id': 'INTEGER PRIMARY KEY',
            'emoji': 'TEXT',
            'title': 'TEXT',
            'content': 'TEXT',
            'date': 'TEXT',
            'last_updated': 'TEXT',
            'tags': 'TEXT'
        }
    }
    f = FirestoreManager(SHEMA)

    new_note = {
        'id': '10',
        'emoji': '📝',
        'title': 'test',
        'content': 'test',
        'date': '',
        'last_updated': '',
        'tags': ''
    }
    #f.add_element(new_note)
    #print(f.get_all())

        
'''
st.success('Connected to Firestore')

radio = st.radio('Select', ['add notes', 'update notes'])


def get_note_by_index(index):
    notes_ref = db.collection('notes')
    query = notes_ref.where('id', '==', str(index))
    results = query.get()
    res = [result.to_dict() for result in results] 
    return res[0] if res else None

if radio == 'add notes':
    with st.form('add notes'):
        notes = {
            'id' : st.text_input('id', value='1'),
            'emoji' : st.text_input('emoji', value='👋'),
            'title': st.text_input('title', value='This is a title'),
            'content': st.text_area('content', value='This is some content'),
            'date': str(datetime.datetime.now().date()),
            'last_updated': str(datetime.datetime.now().date()),
            'tags': 'tag1, tag2, tag3'
        }
        if st.form_submit_button('Add'):
            doc_ref = db.collection('notes').document(notes['id'])
            doc_ref.set(notes)
            st.success('Added notes: {}'.format(notes))

elif radio == 'update notes':
    index = st.number_input('index', value=0)
    notes = get_note_by_index(index)
    st.write(notes if notes else 'No notes found')

    with st.form('update notes'):
        note = {
            'id' : st.text_input('id', value=notes['id']),
            'emoji' : st.text_input('emoji', value=notes['emoji']),
            'title': st.text_input('title', value=notes['title']),
            'content': st.text_area('content', value=notes['content']),
            'date': str(datetime.datetime.now().date()),
            'last_updated': str(datetime.datetime.now().date()),
            'tags': notes['tags']
        }
        if st.form_submit_button('Update'):
            doc_ref = db.collection('notes').document(note['id'])
            doc_ref.set(note)
            st.success('Updated notes: {}'.format(note))
    
with st.expander('all notes'):
    notes_ref = db.collection('notes')
    all_notes = notes_ref.stream()
    all_notes = [note.to_dict() for note in all_notes]
    for n in all_notes:
        st.write(n)'''