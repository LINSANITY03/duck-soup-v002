import streamlit as st
import streamlit_antd_components as sac
from langchain.memory import ConversationBufferMemory
from utils import bot_template_creation
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
import streamlit as st
from langchain.chat_models import ChatOpenAI
from classes.databases_class import Settings, AIAssistantsDB

class AIAssistant:
    def __init__(self):
        self.open_ai_key = Settings.get_by_field('openai_api_key')
        self.ai_assistants_db = AIAssistantsDB.get_all()
        
    def OnAIAssistant(self):
        # need to create a new page when we can set the role of the ai assistant and the parameters of the model
        self.with_ai_assistant = st.toggle('AI Assistant', value=st.session_state.with_assistant_ai)
        if self.open_ai_key == '' or self.open_ai_key == None:
            st.info('Please go in ⚙️ Settings and update your OpenAI API Key')
            st.stop()
        st.session_state.with_assistant_ai = self.with_ai_assistant
        if st.session_state.with_assistant_ai and self.ai_assistants_db == []:
            with st.form(key= 'AI_Assistant'):
                # add parameters for the AI assistant
                save_button = st.form_submit_button('Save Now') 
                name, temperature, role, image = self.CreateAI()
                if save_button:
                    # save the parameters in the database
                    self.ai_assistants_db.insert(name, temperature, role, image)
                    st.experimental_rerun()
        elif st.session_state.with_assistant_ai and self.ai_assistants_db != []:
            self.CreateAI()

    def OnNewAI(self):
        with st.form('AI_Assistant_new'):
            name = st.text_input('Name', value='Elon')
            c1,c2 = st.columns([1,1])
            image = c2.text_input('Image', value = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAoHCBUWFRgVFRUZGBUYGhUSGBIYEhgREhIRGBgZGRgZGBgcIS4lHB4rHxgYJjgmKy8xNTU1GiQ7QDs0Py40NTEBDAwMEA8QHhISHjQkISE0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0MTQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NP/AABEIALcBEwMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAFAQIDBAYABwj/xAA7EAACAQMCBAQEBAUDAwUAAAABAgADBBEhMQUSQVEGImFxE4GRoRQysfAHQlLB0XKC4RUjYiQzkrLx/8QAGQEAAwEBAQAAAAAAAAAAAAAAAQIDAAQF/8QAIREAAgIDAQEBAAMBAAAAAAAAAAECEQMhMRJBUQQTImH/2gAMAwEAAhEDEQA/AMHd3RGxxKqXVZtBkx/DrY1H127TdcP4AoUHEWKopJ2Zaxovu0MoIVurAKNBBgESXTIUCPURsesAS3YjzTVWmwmXsRrNPbMAuToAMk9AIUYtOwAydup6CAOI8cRDhQXJ2Oy++vT1gTjHiTnfkX8gOgxnmxsx1xjrAvEeK5pkArlvL5F5Cw/mxjp0z7/JZQUujRl54S8T8UszlVY8u2F2xBL3LPqWOm2uue4lJlIGchfTr9ekpNXbqeYff5GNGKSpCyk30O2oJOrHTQhjrncYPyhGz4wyFTvy6Z7r2J6f8TL07o7HUH69xLP4rA9fTT694JRvoYya4ekW3iNGUecDvnJx9On71hayv1fI2I3GcjUZBHcGeNm4caj5iaHwtxN2cpzYPK3K3QsMFVPpofrpOTL/AB0laOjHmt0z1JUBnNZKekE8L4l8RFddjuOqsNCD7GGKNyDOJqnR0gu84BTfpg9xoZnb7gdRNUOR22M3rOJRusGGzJswKcSqIcHI94VtPE2NzJOJ2qt0mcuLTB0jaY9G7tfESHcwrQ4ojbMJ5KeZZLS4g69TB4/BXFHrZuQesp3TAiYK24+43MJU+Nlt4ri0FRLN/SEBXFPEK1LrmlKquZilAwiKFlhqUVEhs1Ffknckt/DirSycDc6QWGiqqR3JNba8AATLasftA3ErHkPp+k1gTTBnJOkuROgsYB+F6y516T0G34ivLPJuF1Cg094X/wCqP02nut0eEk2ba/v1IgT4oJmfrcTY7x1tfZMV7Dw0QMlWUKFfMspUijBSxGsv8V4pTp0nVm8xUrygZIJGhbsOsFW9cIrOdlBbfGcdMmYbjN+Xdjr5iSddCT/b/EaKAyN645yToOwwM9NN9ZEKrMc9cYA0AQdPaVtcZJOPfeS21JnYIgOp/ZhYF0sLaFyFQczHtrkzWcJ8DMyg1DjPTO0OeHuCpRQEjzHqRrNPR+0k5t8OlYkumRXwAn9W3rvLlDwLSB1OR9s4mxpLJsCFNmpGOufBtsRgqRvqpwdcf8/Wefcd4JVs3wuWRj5KgGD/AKWHRv1/T2qrTgridklRGRxofTZhsR65i+mnszimtdMl4OJSlyN1PMNebJO+o0EJXVwyHIMylBKlvcFD0PTPKwOxI9obvLkNrOP+RFKXpfS+B2qfwuUvELDRtZZ/6wr9ZlWQk6CbHw34R51FStnB1Cbaesg6LS8x2yhVrBpVehmbe58KUiPLlT3Bmau7JqT8jfI9xFDGcZcM/XtIMuLfE09ZBBF6kKkO0BuSGOHWLMQCDk/QCRWdIZyek03CsZPtGcrFqiI8KwNDKj0iDgzROuIM4kvlB65xEaDFgx0kYWSFoggKCcssWGA65kWI0HByJgG+t6gIgLxNTAQmU7bjHKNc5gvjPEHqkanlHSZE1FpgnnixOSLG0MZi2okAGTgwve2fIsGok9iTPJhEoXJlejUIMIV6cH8muIYvQs47DVrcmFLev6wEilRI/wAfynearFujTcVvAlIDP5mVcd9z/aZO4uFxtk5OuNz8+m8tXd0HQd1OR+hgpzk/2hSozY6gC7jcn31+vSb/AMM2lNMYAZ+rHX6TEWlMjWangNxggDJP72izZTGtm8TPXb9JeoOZTtWyozvL6J9ZBHQ2XaLyfEp0WwdR9pbWt0/f70lExGIwzK1aj/nvLJrgAwdxXi6UkLscn8qKNWZu0zVoKtGU8Y2nKadbGCrhGOMeR9AT7H/7QVTtjzHm6dO8L3tvVqUKju2jqx5N+Qgcyn6riVrxwCoO5UE++BOPPHhfC+ljh9NS6AjQsJ6dRHlGNsTyWnXwQRuNRNnwrxXS5QtRwjdicSHh9Nm3w1YMx/jJwGTvhvppCF54rtkUkOGboqnmJPymHveJPXcu3XQD+legisGCL9WOd4MvJdLSlcxTrK9tUAODsYXtbgqQRAbCS0YwDTVOMrjHLr3G0G3N2znsOgkFNJPyRWzKNEOZIk5lioJhx8YZJIzFMJiROkmkbRjEPw50dOmMCOLXgY6ShRQkZ6QWlVnYZMOoAqz3XCzwoyoo3LACVLZctG31yMkCRW1fBgUaRnK2HKlLyzO3NPDGHFugVg2+TIzCtAZRSriShfMOx2lZ1MPeHeGJXB+JW+GFIVdAedzrg5IwMD7zSaStmjFydIai7Ae/yE3Hhy1RUVwPMdz2mVueHtTznVRordCJpvDFxmng9DISdo6oRqVM0iPiOfjCJ/LzN27mQhSRpvBtai6vzBGd/wCVBjU98nYREylF654xdkcyUmA7BC2n0lVfFtVCFrJyZ7jlYxgtLmsjB6/ISDy00515G/8AI8uT+kjt/BaFPPUZ3AzkbFsnOT1H79JTy6sTSe0aahVL0y46jP2gS3qK7ZKmo4BPKCAtNfc9T+wYa4KeQCkx0A5R6yVrNlZuRVxoNFAOBtnGDMkM+GY4LW+MXYU2RTzLyM5dWxkcwztAF1XLNk7gBfYDSelW9vyAltyegwAOw+pnnXHKfw67qNs849m1/UkfKBxTYrk0gbVvnGkHfGZmyTkx9atkmV0bWPGCSJSm2wvamF7faB7VoVpPpPNz9PRw8LRMq3BjmriVa1aQSLDDJaUrfEEmpOIzQAlSk4lWk8lNSKMPYRqyM1hHK4MxiYyMx2ZBWqYmMPZwJC1UQZc3uOsovxHXeUjjkybyRRoOcToC/wCoesWb+qX4H+yJnrcFWlq5vSFxmSXdIAaQNVfJnu3SPBOZsnMYTOiRQlqyck4htbfIgSwHnmgSr5YGMgRdUMGT8BYCoFb8rEY/1qcr9dR85JUTmld6BXXGu4O2IskmqGjcZKS+Gm4xV5WFNUPKwJGufOddB0Eu+HxyAhhgk/pOsq610R9nXKtplc4116Zlw0xnON8Ejecz1/k7nTakg5ZVwcDOkNKgIBGMzI0SVbTY9IRo3jD99IIyo0o2aJLdCfMqn7/WWKhVFOB01OwAgi1uAesuXL5QrnQjGfQ6SqlZNxAL3GXDDJGek0SV/Kr5xpgjrPPuPXd1T5VSny0xkFmHMCenKwOnvL3BLurV5V2zgnJOnKcnGmsyZRpPRs7l+YZB6TyrxnVP4jAOnIvzPM/+J6W6cuSPyndex9J5z4zt81lbun6O3+YjbTFaVUZao+IynV1kdzkaSp8SdEdo5JupGht7iEqVxpMnSuSDDFtUyJx58P07P42W9BCvcSi916zq50g6pvJ48aZbLJx4EVuJZo14ITMs0mMM4I0JNh6jWnVrnEpU20kdd5zKGy/wm/FS7bVswIglyg5EaUEuBjsOLW0g++uNDIvxOkF3lzmCGNti5JeUUruuScCQfAY6yaimTmEUo6T0U1FUjzmnJ2wHhh1nQhUoamJHtCeWQX10OXA3MFRXYxuZduzmHTomZxgMXuHJuYQJxK3DU3lyokVjRLNnTyNY27oiPs30ktUZk72dXlOJDwS//DuWYZRvK6jcjOhHqJqG4jQdgKbhtOYjZhr1EyT0xnbMWxtilVXU46Eb+U7zOHraBGTjr4bqm2QD1EmK5guhccpwYQo1ges56OhMu2NUBsH6w4zLy5buPlAVJl+cj4vTrMmEYKmcmofMQp7Db6x4isI33EbZB/3GGunwz5mb0x/mU7bilPzPRtqjMdNVZBjHRjoPrM5RptRfmVXdjqamjs3ucaD00EOU/wARVAJcoNDy6En3EommFeUv0np8dy3I9NkJ8uCQ6k/6l0z6TO+Lqf8A3FHZP1YzT0kdMqdc68+NMjpjpM/4iti3LVBzkmk4/odfMPcEH7GLLe/wR1evp5/xVCDBqzR8QoZEDUbU80pCSaObJFqQttRyRDdvRwIy3tsQjTp5OJPJKy2KPl2U7inKVSkRNO1lkSlc2uAZyKflno+FJbAiySm2sjfQxEeWatWQb86CavpK9xVjBUlS5qRIY7YZ5Uo6LdKoJbp1dIEo1pbSvpDPCLjz/pbrVYNcknEmDFzhYX4Zwc7kaymOHknlyetFC3tSBmO+JjSaVuHYXaAr2hymVUG9knKtA5qk6P8AhmdD4E9GfeMxHxcSxzDMTl3j8Rg3mMHeGL5sQt+GzmAuHVfMJqabjESQ0SjStTCNLheV5mJ12A7esiS4XMLWtyrqFyMroR1x0MCVlPTSBlXhnKOYHI213EThNqHrpTOzMAf9O5+wMJ8QuUC8gIycadgO8A2d8Uu7fl1PxUXHoWAP2M6IxS2TlKwgXLDIGCrMhXqGRirD6iPo3E1XGOChmNSngM3mK7K7Yxn0OnzmSv7VkbYq3VCMc3qO85Z42ns6YZLWggFcgFD8s4xCtm7leV2yew1P32mSocTA30O2n+IQt6/Mco49s4P0ieWM5Gqp0VUHr101J+cbRuiRoMDsRiC7apU6n/P1likjA5Y5P0H0lI42D2Xa12QjNgnQkKOumce8orYvV4dWrDmDH/1KDGrCkCW09QzgewlSxqNWvBTBPw6eSxHU9SfuB856RQpLyAFRylSvLjTlOmMdsaS+LGnbfOEc03FV9PBDcBxrv+sg5kU5IM3fivwIlOk1az5yyFnqUSefNMnPkHTkHTqPUa4BKgcQ/wBUY6oi8kpdZeS/TtJ6HE0U6qfrAdRMRmIksUZdQ8cslxm3occtyMElT6rn9JWv7umwPI4P2mSAjw5Eg/4sH+l4/wAzIvwlrUnJOB9xIRTcbgx5eNJlVhilRKWeUnbHipK9Y5ilvt+khd5Px5Y/v1EhJxJEqEnEgcyxw9MuI7WiV7NVwCwyRkTc2dkANoD4BRwBNXTcYxDGNlW6RTurYYxM7dcO11mwdQYOuUEqkkScmzKtwz0iQ6wESTsY8gEUxBFMJITMa04RSJjFiwfziaH8TpMxSbBzCKXEDQUxtS7cNF/HNnWMZMytUGDDVAsK/wDUcDeQ07spUSr1R1qY64DAkfSVre2P52GnQdz39otUZjWwHuNG6BAIIZHCsOzKRkERatNXGMBh/QwB+xmF8FcUL0/w76vTBKdzTznHyJPsMTWU6re/odGHz6/P6y6/0rBdAvi/huk+qryP3Qfqh0PyIgJOAVVPkw47o2GHujYI+WZu0repHo2n/ERrVHYZXU4HMpKnX23iywxfyh1lkjMrSemAH50G2SrLn0BMZxLiQpphdXbyoNySdMz0ROAOAQtxlCCCj0wwI7Ec2CIG4b/D9EuGrVHFRdClPlIWmeuSTqO3b13kXi+Jlo54rqKvg7hvwqeSM1H8zdSAdsnpNhyMVHQYA9Tj+0tUrNFBCAAdQBENRNs/KdUWlFRXw5ZycpWyO2pY1njf8SvCv4aqbiiuKFQliq7Uqh1YDsp3HuR0nsdS5HeDr+1S4Rqb6qwI9j0I9YXFy6KpUfPK3R2Oo+8ctRT/AMwl4j4C9tVZGB5c+VuhHSBwk5mnF0yiplsRqtr6DT5yKnJ6bAdBMYe/f5SPMnZwemJXMxhDv7iVHOJabcSvdL1iyQYuisxl/g488HGEeDfniPg0enpvAxoIbBxAnBDoIYc6R4IeTG3N1yiAK/EstiLxW6xmZ9HJbMSctgS0HfjzoO550X0gHn0dGzpQQbHyMxczGFkiEyIGT0ELEKoyT0mMWEqfWX6FkFHM+rbhOg9/WPt7ZaYydX79F9v8yCvVJjpV0Vs6tUyZA6do4CLN0A+xunpOtRDh0PMD09QfQ7T2fg5S6opWp48w1XIDKw0ZT6g5niNVsTV/w648aFf4TNhKpAGTotbZT/u/L78spjkk6f0L5Z6YbUroyn6aSSwtlWoG5QTg4B1UHvjbMN0a/MP7SG5Kq6HAAJIJxg7S9/GTOq06zHyvyj0XMctKogJeoWxqFwozjXXAll7pEXOczPVaj3TtTLmmg/l3aoPXB+0Xb+aMwobwjB+udBiA7rjSlm5eYDO4wM/WHbbgFNR5sue7eb6A7RtXw9RJzygZ6dIVOCegUwHZPSfJLOSNwxyQPTpDlo6YyoOhwcjYHTIk1LhFNBgDTtsPtLi0F5SuNCCMbTSyJo3kzvizw+tzSIwOcAlT69j6H7GeH8U4Y9BylRSrbgHqJ9I0Tpg7jQ+vrMd4/wDDYr0i6Dzplge/of0PyPSSlvX0eLo8TEkUxr0iCQcgjQjYg9jFVZIcl+JgZG+g7xtUZ1jgk5OxmMVm2+kbWTIj6i4jWaBmKPJLvCtHkVRY+xbDiTY6PTeCNoIWuW0gHgVTQQ3dDIlI8GkZPitTLYi2lvpEv6B58yW1q4GshX+nYST4M6V6lfUxINGPP8xCZIqRGSWskRGdHFYQs+H58z6L0XYt/gQpWYr2dkznTRRux2+XcwzTCUxhRr1Y7n3iPWAGBgAaADQCVWfMZJIV7HO5JjDEZwN5Ga4/YmsJYxGmN+Mp6/XSNqVNNDvNZiGq+TEU/vaNAiiKE9t8Ccf/ABNAcx/79LCVB1cfyv8AMD6gw3cpUdwP5BrnbHsZ4j4U40bW5SrryfkqKP5qTfm06kaMPVcdZ7/RqDAdDlGAYEHIKnUEemJ1Rn6X/USapkSWxbTGncjAjK/D+RMpq4b4gbqWG49saYhdHBEeRM8jsHkbTqBlDdwD7SQmVqS8pKn8pyR89xJKVLlBAJOTnU8x9sybVMdDmjUMc0jUzLgH0RtDnvof7fv1jnQEYM4rkEd4lJ8j12PuN5gHjX8QuAfBq/EQeRzr6P8Av+3eYwLPoXxFwlbmi6MNxoeobof3/aeDXlq1N2puPMh5TpjPY/OZq9jJlYTsRxWIBEGI6q5lepSZcBlKnAOGUqSpGVIz0I1BhfhrIlVHqoHpq6l0OzoD5hpvp064xND/ABWVPxNNkI81FSAoGOTmPIdOhBOPaHzabBezBeklo0sMDGOvWXsgqDOfI3GjoxJSv/hq+BvtNai8yzD8DqbTbWr6CNjkaUSheWY7QFc0SJrrkjEBXFMEwZEBAP4ZnQ1+FE6S8hPN0EVgIwHSKDKElGy3bUFHmYBiNl7epHWPqXBMphzJVlUI0PxGvHRrQhEYZGJXIkymNqr1gZkMURWEUtjQfWMYwBOEWIseBMYRZ69/Cnj/AMSkbVz56Y5qeTq1EnGP9pOPZl7TyLEIcF4i9vWSsn5kYHGcB12ZT6EZHzjRdMWStH0aByn0llGlHh14leklVDlHUOp64PQ+o2PqJZpnpKvYiJKqZGm41HvHI+Rn9g9ROBkRPK3/AIt9m/5g7oYmMiaSGRsJkBiiMBw5HRtf9w3+2PpHCR3O3MN1PN8uv2z9ZkAmnmP8TuC8pFyg/wDF/UHY/wB//lPTgc699ZR4zZLWpOjDIYFdfWZfhrPn1VjgkmuLVqVR6bbqSNd8dP33iYgooNRJU4mzFwWYt5VUZJPKijlVRnYADaEFlLig0U+pH1//ACB8MUYqPpy/ORoY+TnH0hoy8s0PCKnLiaq3vwBvPPKN7yywvFD3nOlJM6fUWqN3Xv8APWQU3zMrQ4gTuZoeHVciM3YjVBGdFxEgAeVUzpFnTpRk+DjvJaRizpRdEY4TmnToRSHrJJ06YYhbTSNC5nTooSQLFxOnQgHERQJ06Yx6d/Cfjhy1o2cHmqUz/SR/7i+x/MPXm7z1HE6dKrgj6OBiVk5l/ek6dN9MR0KhKn+pcj0JG0WlVDjIBGCQQcaEb7RJ0z6ZcH4nNtOnTAILJvKV/pJX/buv2Ilgzp0L6Y8h/iTYfDuUqjZwQfcfvPzmYAnTppdGXDmlK/Hk9iDFnRXwwLEcpnTogxDcL1kdN8Tp0RjImp1zkTZ8EfQTp0nIdGhzOnToox//2Q==')
            temperature = st.slider('Temperature', 0.0, 1.0, 0.5)
            c1.write(bot_template_creation.replace("{{MSG}}", name).replace('{{IMAGE}}', image), unsafe_allow_html=True)
            c1.markdown
            model = ChatOpenAI(openai_api_key=st.session_state.open_ai_key)
            from langchain.schema import (
                AIMessage,
                HumanMessage,
                SystemMessage
            )
            role = st.text_area('Role', value = 'You are a stand-up comedian that always try to make a joke about what the user says.')
            chat_due = st.text_input(label='Chat', key = 'chat_2')
            if chat_due:
                message = role + '\n' + chat_due
                answer = model([HumanMessage(content=message)])
                st.write(answer)

            if st.form_submit_button('Save', use_container_width=True, type='primary'):
                self.ai_assistants_db.insert(name, temperature, role, image)
                st.success('Saved')
                st.experimental_rerun()
            return name, temperature, role, image
        
    def CreateAI(self):
        st.write(st.session_state.choosen_ai if st.session_state.choosen_ai else 'No AI choosen')

        if self.ai_assistants_db == []:
            self.OnNewAI()
            st.stop()
        else:
            buttons =  [sac.ButtonsItem(label='New AI')] + [sac.ButtonsItem(label=f'{ai[1]}') for ai in self.ai_assistants_db]
            choosen = sac.buttons(buttons, format_func='title', align='center', shape='round', index = 1)
            if choosen == 'New AI':
                self.OnNewAI()
            else:
                if choosen != st.session_state.choosen_ai:
                    st.write('Changed')
                    st.session_state.choosen_ai = choosen
                    st.session_state.langchain_messages = []
                    st.experimental_rerun()
                # get ai from name 
                ai = AIAssistantsDB.get_by_field('name', choosen)
                # transform in dict
                ai = dict(zip(['id', 'name', 'temperature', 'role', 'image'], ai))
                st.session_state.choosen_ai = ai['name']
                if ai:
                    with st.form(key = f'{ai["name"]}'):
                        c1,c2 = st.columns([1,1])
                        name = c1.text_input('Name', value=ai['name'])
                        image = c2.text_input('Image', value = ai['image'])
                        st.write(bot_template_creation.replace("{{MSG}}", ai['name']).replace('{{IMAGE}}', ai['image']), 
                                 unsafe_allow_html=True)
                        role = st.text_area('Role', value = ai['role'])
                        temperature = st.slider('Temperature', 0.0, 1.0, ai['temperature'])
                        model = ChatOpenAI(openai_api_key=st.session_state.open_ai_key)
                        from langchain.schema import (
                            AIMessage,
                            HumanMessage,
                            SystemMessage
                        )
                        chat_due = st.text_input(label='Chat', key = 'chat_2', placeholder='Hi, can you help me?')
                        if chat_due:
                            message = role + '\n' + chat_due
                            answer = model([HumanMessage(content=message)])
                            st.write(bot_template_creation.replace("{{MSG}}", answer.content).replace('{{IMAGE}}', image), unsafe_allow_html=True)

                        if st.form_submit_button('Save', use_container_width=True, type='primary'):
                            # get id from name
                            self.ai_assistants_db.update_from_name(name, temperature, role, image)
                            st.success('Saved')
                            st.experimental_rerun()

                        if st.form_submit_button('Delete', use_container_width=True, type='secondary'):
                            self.ai_assistants_db.delete_from_name(name)
                            st.success('Deleted')
                            st.experimental_rerun()

                        return name, temperature, role, image
    
    def ChatAgent(self):
        ai = AIAssistantsDB.get_by_field('name', st.session_state.choosen_ai)
        ai = dict(zip(['id', 'name', 'temperature', 'role', 'image'], ai))

        msgs = StreamlitChatMessageHistory(key="langchain_messages")
        memory = ConversationBufferMemory(chat_memory=msgs)
        if len(msgs.messages) == 0:
            msgs.add_ai_message("How can I help you?")

        view_messages = st.expander("View the message contents in session state")

        # Get an OpenAI API Key before continuing
        if not self.open_ai_key:
            st.info("Enter an OpenAI API Key to continue")
            st.stop()

        # Set up the LLMChain, passing in memory
        # transform in dict
        template = f"""Your role: {ai['role']}"""+""" {history}
        Human: {human_input} """ + f"""
        {ai['name']}""" 
        prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
        llm_chain = LLMChain(llm=OpenAI(openai_api_key=self.open_ai_key), prompt=prompt, memory=memory)

        # Render current messages from StreamlitChatMessageHistory
        def render_messages(image = ai['image'], name = ai['name']):
            with st.expander("Chat History", expanded=True):
                if st.button('Restart Memory', use_container_width=True):
                    st.session_state.langchain_messages = []
                    st.experimental_rerun()

                # for i, msg in enumerate(msgs.messages):
                #     if i % 2 != 0:
                #         st.write(user_template.replace("{{MSG}}", msg.content), unsafe_allow_html=True)
                #     else:
                #         st.write(bot_template_creation.replace("{{MSG}}", msg.content).replace('{{IMAGE}}', image), unsafe_allow_html=True)

                # or use st.chat
                # set user and ai messages icons
                # get image from db

                do_we_have_messages = False if st.session_state.langchain_messages == [] else True
                if do_we_have_messages:
                    for i, msg in enumerate(msgs.messages):
                        if i % 2 == 0:
                            with st.chat_message(avatar= image, name = name):
                                st.write(msg.content)
                        else:
                            with st.chat_message(avatar='user', name='User'):
                                st.write(msg.content)

        # If user inputs a new prompt, generate and draw a new response
        if prompt := st.chat_input():
            response = llm_chain.run(prompt)
    
        render_messages()

    def ChatFeatures(self):
        # get open_ai_key from the config file
        st.session_state.open_ai_key = Settings.get_by_field('openai_api_key')
        try:
            open_ai_key = st.session_state.open_ai_key
        except:
            open_ai_key = st.text_input(
            "Please enter your OpenAI API key", type="password")
            save_button = st.button("Save key")
            if save_button:
                Settings.update_by_field('openai_key', open_ai_key)
                # save as session state
                st.session_state.open_ai_key = open_ai_key

        if st.session_state.with_assistant_ai:
            # get name of selected ai
            self.ChatAgent()

