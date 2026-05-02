def generer_resume(chunks, llm):
    extrait = "\n\n".join(c.page_content for c in chunks[:5])

    prompt = f"""
    Voici un extrait d'un document.
    Fais un resume clair en 5 points maximum.
    Reponds en francais.

    Document : {extrait}

    Resume :
    """
    return llm.invoke(prompt).content
