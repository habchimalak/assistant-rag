import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Charger la clé API
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# ÉTAPE 1 — Charger les PDFs
def charger_documents():
    print("📄 Chargement des documents...")
    loader = DirectoryLoader(
        "documents/",
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    print(f"✅ {len(documents)} pages chargées")
    return documents

# ÉTAPE 2 — Découper en chunks
def decouper_en_chunks(documents):
    print("✂️ Découpage en chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ {len(chunks)} chunks créés")
    return chunks

# ÉTAPE 3 — Créer la base vectorielle
def creer_base_vectorielle(chunks):
    print("🔢 Création des embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    base = FAISS.from_documents(chunks, embeddings)
    base.save_local("faiss_index")
    print("✅ Base vectorielle sauvegardée !")
    return base

# ÉTAPE 4 — Charger la base existante
def charger_base():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    base = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    return base

# ÉTAPE 5 — Créer la chaîne RAG
def creer_chaine(base):
    print("🤖 Connexion au LLM Groq...")
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=groq_api_key
    )

    retriever = base.as_retriever(search_kwargs={"k": 3})

    prompt = PromptTemplate.from_template("""
    Tu es un assistant expert. Réponds à la question en utilisant
    UNIQUEMENT le contexte fourni. Si tu ne trouves pas la réponse,
    dis "Je ne trouve pas cette information dans les documents."

    Contexte : {context}
    Question : {question}
    Réponse :
    """)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chaine = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chaine, retriever

# PROGRAMME PRINCIPAL
if __name__ == "__main__":
    if os.path.exists("faiss_index"):
        print("📂 Base existante trouvée, chargement...")
        base = charger_base()
    else:
        docs = charger_documents()
        chunks = decouper_en_chunks(docs)
        base = creer_base_vectorielle(chunks)

    chaine, retriever = creer_chaine(base)

    print("\n🎉 RAG prêt ! Pose tes questions (tape 'quit' pour quitter)\n")

    while True:
        question = input("❓ Ta question : ")
        if question.lower() == "quit":
            break

        # Obtenir la réponse
        reponse = chaine.invoke(question)
        print(f"\n💡 Réponse : {reponse}")

        # Afficher les sources
        docs_sources = retriever.invoke(question)
        print(f"\n📚 Sources :")
        for doc in docs_sources:
            print(f"   → {doc.page_content[:100]}...")
        print("\n" + "="*60 + "\n")