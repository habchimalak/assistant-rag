import os
import shutil
import stat
import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory
from rag.indexation import indexer_fichiers
from rag.resume import generer_resume
from rag.generation import get_llm


def afficher_sidebar(groq_api_key):
    with st.sidebar:
        st.title("Mes documents")
        st.markdown("Uploade tes PDFs ici !")

        fichiers = st.file_uploader(
            "Choisir des fichiers PDF",
            type="pdf",
            accept_multiple_files=True
        )

        if fichiers:
            st.success(f"{len(fichiers)} fichier(s) pret(s)")
            for f in fichiers:
                st.markdown(f"- {f.name}")

            if st.button("Indexer ces documents", type="primary"):
                with st.spinner("Indexation en cours..."):
                    chunks = indexer_fichiers(fichiers)
                    st.session_state.messages = []
                    st.session_state.historique = ChatMessageHistory()
                    st.session_state.quiz = None
                    st.cache_resource.clear()

                with st.spinner("Resume en cours..."):
                    llm = get_llm(groq_api_key)
                    st.session_state.resume = generer_resume(
                        chunks, llm
                    )

                st.success(f"{len(chunks)} chunks indexes !")
                st.rerun()

        st.divider()
        st.markdown("### Base actuelle")
        if os.path.exists("faiss_index"):
            st.markdown("Base vectorielle active")
        else:
            st.markdown("Aucune base — uploade des PDFs")

        st.divider()
        st.markdown("### Resume")
        if st.session_state.get("resume"):
            st.markdown(st.session_state.resume)
        else:
            st.caption("Indexe un document pour voir le resume !")

        st.divider()
        st.markdown("### Exporter")
        if st.session_state.get("messages"):
            texte = "=== HISTORIQUE DU CHAT RAG ===\n\n"
            for msg in st.session_state.messages:
                role = "MOI" if msg["role"] == "user" else "ASSISTANT"
                texte += f"[{role}]\n{msg['content']}\n\n"
                texte += "-" * 40 + "\n\n"
            st.download_button(
                label="Telecharger la conversation",
                data=texte,
                file_name="historique_rag.txt",
                mime="text/plain"
            )
        else:
            st.caption("Pose une question d'abord !")

        st.divider()
        if st.button("Tout reinitialiser"):
            st.session_state.messages = []
            st.session_state.historique = ChatMessageHistory()
            st.session_state.resume = None
            st.session_state.quiz = None
            st.cache_resource.clear()
            if os.path.exists("faiss_index"):
                def forcer(action, chemin, exc):
                    os.chmod(chemin, stat.S_IWRITE)
                    action(chemin)
                shutil.rmtree("faiss_index", onexc=forcer)
            st.rerun()
