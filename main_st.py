# to run: streamlit run main_st.py

from duck_soup_v002 import DuckSoup_st
from classes.ai_template import AIAssistant
import streamlit as st
from classes.users import auth

if __name__ == '''__main__''':
    if auth():
        app = DuckSoup_st(user_id=st.session_state['id'])
        ai_assistant = AIAssistant(app.settings_db, app.ai_assistants_db)
        app.run(AI_ASSISTANT = ai_assistant)
