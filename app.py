import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory

from rag.indexation import charger_base
from rag.generation import get_llm
from rag.quiz import generer_quiz, afficher_quiz
from ui.sidebar import afficher_sidebar
from ui.chat import afficher_chat

load_dotenv()
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Assistant RAG", page_icon="📚", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "historique" not in st.session_state:
    st.session_state.historique = ChatMessageHistory()

afficher_sidebar(groq_api_key)

st.title("Assistant RAG avec Memoire")
st.markdown("*Pose des questions sur tes documents PDF*")
st.divider()

if not os.path.exists("faiss_index"):
    st.info("Commence par uploader des PDFs a gauche !")
else:
    @st.cache_resource
    def charger_rag():
        base = charger_base()
        if base is None:
            return None, None
        llm = get_llm(groq_api_key)
        retriever = base.as_retriever(search_kwargs={"k": 3})
        return retriever, llm

    retriever, llm = charger_rag()

    if retriever is None:
        st.error("Erreur de chargement. Reindexe tes documents.")
    else:
        st.success("Systeme pret avec memoire conversationnelle !")
        mode = st.radio("Mode :", ["Chat", "Quiz"], horizontal=True)
        st.divider()

        if mode == "Quiz":
            st.markdown("### Mode Quiz")
            nb_questions = st.slider("Nombre de questions", 3, 10, 5)
            if st.button("Generer le quiz", type="primary"):
                with st.spinner("Generation des questions..."):
                    llm_quiz = get_llm(groq_api_key, temperature=0.7)
                    st.session_state.quiz = generer_quiz(retriever, llm_quiz, nb_questions)
            if st.session_state.get("quiz"):
                afficher_quiz(st.session_state.quiz)

        elif mode == "Chat":
            afficher_chat(retriever, llm)
