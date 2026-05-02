import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def indexer_fichiers(fichiers):
    dossier_temp = tempfile.mkdtemp()
    tous_les_docs = []

    for fichier in fichiers:
        chemin = os.path.join(dossier_temp, fichier.name)
        with open(chemin, "wb") as f:
            f.write(fichier.read())
        loader = PyPDFLoader(chemin)
        tous_les_docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(tous_les_docs)

    base = FAISS.from_documents(chunks, get_embeddings())
    base.save_local("faiss_index")

    return chunks


def charger_base():
    if not os.path.exists("faiss_index"):
        return None

    base = FAISS.load_local(
        "faiss_index",
        get_embeddings(),
        allow_dangerous_deserialization=True
    )
    return base
