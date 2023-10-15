'''

'''
import streamlit as st
st.set_page_config(layout="wide")
from streamlit_ace import st_ace
import streamlit_antd_components as sac

import datetime
from utils import get_random_title
from dotenv import load_dotenv
from utils import css
from databases_class import ArchiveNotes, Settings, AIAssistantsDB
from ai_feature import AIAssistant
from calendar_template import OnCalendar


class DuckSoup_st:
    def __init__(self):
        load_dotenv()
        st.write(css, unsafe_allow_html=True)
        self.__initialise_cache()
        self.__initialise_database()
        self.__init_settings()

    def __initialise_database(self):
        '''
        This function initialise the database.
        '''

        self.db = ArchiveNotes
        self.settings_db = Settings
        self.ai_assistants_db = AIAssistantsDB
        self.notes = ArchiveNotes.get_all()

    def __initialise_cache(self):
        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        if "with_assistant_ai" not in st.session_state:
            st.session_state.with_assistant_ai = False
        if "choosen_ai" not in st.session_state:
            st.session_state.choosen_ai = None
        if "open_docs" not in st.session_state:
            st.session_state.open_docs = False

    def __init_css(self):
        css = '''               
            <style>
                .markdown-text-container {
                    color: black;
                    background-color: beige;
                    width: 100%;
                    height: 100%;
                    padding: 10px;
                    border-radius: 10px;
                    border: 1px transparent;
                    overflow-y: scroll;
                }
            </style>'''
        st.write(css, unsafe_allow_html=True)

    def __init_settings(self):
        '''
        Access the database and get the settings from there:
        We then initialise the models with the settings from the database
        '''
        # get the settings from the database
        self.summarizer_model = Settings.get_by_field('summariser')
        self.qa_model = Settings.get_by_field('qa')
        self.text_generation_model = Settings.get_by_field('text_gen')
        self.openai_key = Settings.get_by_field('openai_api_key')
    
    def create_sidebar_menu(self, with_db = True):
        with st.sidebar:
            children = [sac.MenuItem('Upload', icon='upload')] + [sac.MenuItem(f'{n.title}', icon='card-text', tag=f'Tag{n.tags}') for n in self.notes if self.notes != []]
            menu = sac.menu([
                sac.MenuItem('Docs', icon='database', children = children),
                sac.MenuItem('Calendar', icon='calendar'),
                sac.MenuItem('AI Assistant', icon='robot'),
                sac.MenuItem('Settings', icon='gear', children=[
                    sac.MenuItem('AI', icon='robot'),
                    sac.MenuItem('Vault', icon='lock'),
                    sac.MenuItem('Theme', icon='brush'),
                    sac.MenuItem('About', icon='info-circle'),
                ]),
                # add calendar
                    
            ], open_all=False if not st.session_state.open_docs else True)
            return menu

    def get_text(self):
        try:
            return self.text
        except:
            return ''
        
    def TextEditor(self):
        self.__init_css()
        with st.form(key='text_editor'):
            note = ArchiveNotes.get_by_field('title', self.selected_note)

            col = st.columns(10)
            space_new = col[0].empty()
            space_save = col[1].empty()
            space_delete = col[-1].empty()

            c1,c2,c3 = st.columns([1,1,1])
            emoji = c1.text_input('Emoji', value=note.emoji)
            title = c2.text_input('Title', value=note.title)
            date_ = c3.date_input('Date', value=datetime.datetime.strptime(note.date, '%Y-%m-%d'))
            c1,c2 = st.columns([1,1])
            c1.write(datetime.datetime.strptime(note.last_modified, '%Y-%m-%d %H:%M:%S'))
            tags = c2.text_input('Tags', value=note.tags)

            tab1,tab2 = st.tabs([f'Text Editor', f'Markdown Preview'])
            with tab1:
                text = st_ace(placeholder=note.title, value = note.content, height=500, auto_update=True, language='markdown', wrap = True)
            
            with tab2:
                css_for_markdown = '''
                    <div class="markdown-text-container">
                    {{text}}
                '''
                st.markdown(css_for_markdown.replace('{{text}}',text), unsafe_allow_html=True)
                self.text = text

            if space_new.form_submit_button('New', use_container_width=True):
                emoj, titl = get_random_title([n.title for n in self.notes])
                # use the database
                ArchiveNotes.add_element({
                    'emoji': emoj,
                    'title': titl,
                    'content': '',
                    'date': '',
                    'last_modified': '',
                    'tags': ''
                })
                st.rerun()
            elif space_save.form_submit_button('Save',use_container_width=True):
                ArchiveNotes.update_by_field('title', self.selected_note, {'emoji': emoji, 'title': title, 'content': text, 'date': str(date_), 'last_modified': '', 'tags': tags})
                st.rerun()
            elif space_delete.form_submit_button('Delete', use_container_width=True, type='primary'):
                ArchiveNotes.delete_by_field('title', self.selected_note)
                st.rerun()
                st.success('Deleted')

    def OnUpload(self):
        self.__init_css()
        txt = st.sidebar.file_uploader('Upload a file', type=['txt'])
        if txt:
            text = txt.read()
            # transform the text into a list of lines
            text = text.decode('utf-8').split('\n')
            text_joined = '\n'.join(text)

            
            with st.form(key='upload'):
                upload_space_button = st.empty()
                c1,c2,c3,c4 = st.columns([1,1,1,1])
                emoji = c1.text_input('Emoji', value=text[0] if text[0] != '' else '📝')
                title = c2.text_input('Title', value=text[1] if text[1] != '' else 'Title')
                date = c3.date_input('Date', value='today')
                tags = c4.text_input('Tags', value='')
                tab1, tab2 = st.tabs(['Text Editor', 'Markdown Preview'])
                with tab1:
                    content = st_ace(placeholder='New note', value = text_joined, height=500, auto_update=True, language='markdown', wrap = True)
                with tab2:
                    css_for_markdown = '''
                        <div class="markdown-text-container">
                        {{text}}
                    '''
                    st.markdown(css_for_markdown.replace('{{text}}',content), unsafe_allow_html=True)

                upload_button = upload_space_button.form_submit_button('Upload', use_container_width=True)
                if upload_button:
                    ArchiveNotes.add_element(
                        {
                            'emoji': emoji,
                            'title': title,
                            'content': content,
                            'date': date,
                            'last_modified': '',
                            'tags': tags
                        }
                    )
                    st.rerun()
    
    def Onsettings(self):
        options = ['OpenAI', 'BART', 'T5', 'Pegasus']
        if self.selected_command == 'AI':
            with st.form(key='settings'):
                c1,c2 = st.columns([1,1])
                with c1:
                    summarizer_model = st.selectbox('Summarizer', options, index=options.index(Settings.get_by_field('summariser')))
                    qa_model = st.selectbox('QA', options, index=options.index(Settings.get_by_field('qa')))
                    text_generation_model = st.selectbox('Text Generation', options, index=options.index(Settings.get_by_field('text_gen')))
                with c2:
                    self.openai_key = st.text_input('OpenAI Key', value=self.openai_key, type='password')

                save_b = st.form_submit_button('Save', use_container_width=True)
                if save_b and self.with_db:
                    Settings.update_by_field('summariser', summarizer_model)
                    Settings.update_by_field('qa', qa_model)
                    Settings.update_by_field('text_gen', text_generation_model)
                    Settings.update_by_field('openai_api_key', self.openai_key)
                    st.rerun()
        
        elif self.selected_command == 'Vault':
            st.success('No settings for Vault - Currently in DB mode')
        elif self.selected_command == 'Theme':
            color_choose = st.color_picker('Pick A Color', '#00f900')

    def run(self, AI_ASSISTANT = None):
        if AI_ASSISTANT != None:
            self.AI = AI_ASSISTANT

        commands = ['AI', 'Vault', 'Theme', 'About', 'Calendar', 'Upload']
        selected_item_from_menu = self.create_sidebar_menu()
        is_command = selected_item_from_menu in commands
        if selected_item_from_menu == 'Docs' and not st.session_state.open_docs:
            st.session_state.open_docs = True
        
        if is_command and selected_item_from_menu in ['AI', 'Vault', 'Theme', 'About']:
            self.selected_command = selected_item_from_menu
            self.Onsettings()
        elif selected_item_from_menu == 'Calendar':
            OnCalendar()
        elif selected_item_from_menu == 'Upload':
            self.OnUpload()
        elif selected_item_from_menu == 'AI Assistant':
            if AI_ASSISTANT != None:
                self.AI.OnAIAssistant()
            else: 
                st.success('No AI Assistant selected')
        elif selected_item_from_menu in [n.title for n in self.notes]:
            self.selected_note = selected_item_from_menu
            self.TextEditor()
        if AI_ASSISTANT != None:
            self.AI.ChatFeatures()

from ai_feature import AIAssistant

if __name__ == '''__main__''':
    app = DuckSoup_st()
    AI = AIAssistant()
    app.run(AI_ASSISTANT=AI)
