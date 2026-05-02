import streamlit as st
from rag.generation import repondre


def afficher_chat(retriever, llm):
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Pose ta question ici...")

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("assistant"):
            with st.spinner("Recherche dans tes documents..."):
                rep, sources = repondre(
                    question, retriever, llm,
                    st.session_state.historique
                )
                st.markdown(rep)

                if sources:
                    with st.expander("Sources utilisees"):
                        for i, doc in enumerate(sources):
                            st.markdown(
                                f"**Source {i+1}**"
                                f" — Page {doc.metadata.get('page','?')}"
                            )
                            st.markdown(
                                f"> {doc.page_content[:200]}..."
                            )
                            st.divider()

        st.session_state.messages.append({
            "role": "assistant",
            "content": rep
        })
