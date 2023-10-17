from classes.firestore_connection import FirestoreManager
import streamlit as st

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

    # f.add_element({
    #     'id': '10',
    #     'emoji': '📝',
    #     'title': 'test',
    #     'content': 'test',
    #     'date': '',
    #     'last_updated': '',
    #     'tags': ''
    # })

    f.delete_all()
    #st.write(f.get_all())