import streamlit as st
import requests

from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

st.set_page_config(page_title="Multi AI Agent" , layout="centered")
st.title("ABHI`S Multi AI Agent")

system_prompt = st.text_area("Define your AI Agent: " , height=70)
selected_model = st.selectbox("Select your AI model: ", settings.ALLOWED_MODEL_NAMES)

allow_web_search = st.checkbox("Allow web search")

user_query = st.text_area("Enter your query : " , height=150)

API_URL = "http://127.0.0.1:9999/chat"

if st.button("Ask Agent") and user_query.strip():

    backend_data = {
    "model_name": selected_model,
    "system_prompt": system_prompt,
    "message": user_query,          
    "allow_search": allow_web_search
}


    try:
        logger.info("Sending request to backend")

        response = requests.post(API_URL , json=backend_data)

        if response.status_code==200:
            agent_response = response.json().get("response","")
            logger.info("Sucesfully recived response from backend")

            st.subheader("I Think...this will help you:")
            st.markdown(agent_response.replace("\n","<br>"), unsafe_allow_html=True)

        else:
            logger.error("Backend error")
            st.error("Error with backend")
    
    except Exception as e:
        logger.error("Error occured while sending request to backend")
        st.error(str(CustomException("Failed to communicate to backend")))

        

