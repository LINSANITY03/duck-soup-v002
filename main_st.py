# to run: streamlit run main_st.py

from duck_soup_v002 import DuckSoup_st
from ai_feature import AIAssistant

if __name__ == '''__main__''':
    app = DuckSoup_st()
    AI = AIAssistant()
    app.run(AI_ASSISTANT=AI)

