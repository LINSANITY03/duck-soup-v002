from classes.firestore_connection import FirestoreManager
import streamlit as st

SHEMA = {
    'users': {
        'id': 'INTEGER PRIMARY KEY',
        'username': 'TEXT',
        'password': 'TEXT',
        'email': 'TEXT',
    }
}
f = FirestoreManager(SHEMA)

class UsersManager(FirestoreManager):
    # rewrite add element
    def add_element(self, element):
        # dont' allow same username or email
        if self.get_by_username(element['username']):
            st.error('Username already exists')
        if self.get_by_email(element['email']):
            st.error('Email already exists')
        element['id'] = self.get_next_id()
        super().add_element(element)

    def get_next_id(self):
        all_users = self.get_all()
        if not all_users:
            return str(1)
        return str(max([int(user['id']) for user in all_users]) + 1)
    
    def get_by_username(self, username):
        return self.get_by_field('username', username)
    
    def get_by_email(self, email):
        return self.get_by_field('email', email)
    
    def get_by_username_and_password(self, username, password):
        return self.get_by_field('username', username)['password'] == password
    
    def get_by_email_and_password(self, email, password):
        return self.get_by_field('email', email)['password'] == password
    
users_manager = UsersManager(SHEMA)

def login_form():
    with st.form('login'):
        username = st.text_input('username')
        password = st.text_input('password', type='password')
        submit = st.form_submit_button('Login', type='primary', use_container_width=True)
    return username, password, submit

def register_form():
    with st.form('register'):
        username = st.text_input('username')
        password = st.text_input('password', type='password')
        email = st.text_input('email')
        submit = st.form_submit_button('submit')
        if submit:
            users_manager.add_element({
                'username': username,
                'password': password,
                'email': email
            })
            st.success('User created')
            st.rerun()
    return username, password, email, submit

def login():
    username, password, submit = login_form()
    if submit:
        try:
            if users_manager.get_by_username_and_password(username, password):
                # redirect to home page
                st.success('logged in')
                # get id
                id = users_manager.get_by_username(username)['id']
                return id
            
            else:
                st.error('Wrong username or password')
        except:
            register_form()
    return None

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['id'] = None
    st.rerun()

def auth():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['id'] = None

    if st.session_state.logged_in:
        if st.sidebar.button(f'Logout **{st.session_state.username}**', type = 'primary', use_container_width=True):
            logout()
            return False
        return True
    else:
        radio = st.sidebar.radio('Login or register', ['Login', 'Register'])
        if radio == 'Login':
            id = login()
            if id:
                st.session_state['id'] = id
                st.session_state['username'] = users_manager.get_by_field('id', id)['username']
                st.session_state['logged_in'] = True
                st.rerun()
                return True
        else:
            register_form() 

