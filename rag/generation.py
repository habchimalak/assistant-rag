from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


def get_llm(api_key, temperature=0):
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=api_key
    )


def repondre(question, retriever, llm, historique):
    prompt_ref = ChatPromptTemplate.from_messages([
        ("system", """Reformule la question en une question
        autonome et complete. Retourne UNIQUEMENT la question."""),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ])
    chaine_ref = prompt_ref | llm | StrOutputParser()
    question_ref = chaine_ref.invoke({
        "chat_history": historique.messages,
        "question": question
    })

    docs = retriever.invoke(question_ref)
    contexte = "\n\n".join(d.page_content for d in docs)

    prompt_rep = ChatPromptTemplate.from_messages([
        ("system", """Tu es un assistant expert. Reponds
        UNIQUEMENT en utilisant le contexte fourni.
        Si tu ne trouves pas, dis-le clairement.

        Contexte : {contexte}"""),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ])
    chaine_rep = prompt_rep | llm | StrOutputParser()
    reponse = chaine_rep.invoke({
        "chat_history": historique.messages,
        "question": question,
        "contexte": contexte
    })

    historique.add_user_message(question)
    historique.add_ai_message(reponse)

    return reponse, docs
