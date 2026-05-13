import streamlit as st

def generer_quiz(retriever, llm, nb_questions):
    """Génère un quiz QCM depuis les documents"""
    docs = retriever.invoke("concepts importants définitions")
    contexte = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
    Tu es un professeur. Génère exactement {nb_questions} 
    questions QCM basées sur ce contenu.
    Chaque question a 4 choix (A, B, C, D) et UNE seule 
    bonne réponse.
    
    Format OBLIGATOIRE :
    Q1: [question]
    A) [choix]
    B) [choix]
    C) [choix]
    D) [choix]
    Réponse: [lettre]
    Explication: [courte explication]
    ---
    
    Contenu : {contexte}
    Génère les questions en français.
    """
    return llm.invoke(prompt).content

def afficher_quiz(quiz_texte):
    """Affiche le quiz et calcule le score"""
    questions = quiz_texte.split("---")
    score = 0
    total = 0

    for i, bloc in enumerate(questions):
        if not bloc.strip():
            continue
        lignes = [
            l.strip() for l in bloc.strip().split("\n")
            if l.strip()
        ]
        if len(lignes) < 6:
            continue

        total += 1
        question = lignes[0]
        choix = [
            l for l in lignes
            if l.startswith(("A)", "B)", "C)", "D)"))
        ]
        bonne_rep = next(
            (l.replace("Réponse:", "").strip()
             for l in lignes if l.startswith("Réponse:")),
            "A"
        )
        explication = next(
            (l.replace("Explication:", "").strip()
             for l in lignes if l.startswith("Explication:")),
            ""
        )

        st.markdown(f"**{question}**")
        rep_user = st.radio(
            f"Question {i+1}",
            choix,
            key=f"q_{i}",
            label_visibility="collapsed"
        )

        if rep_user:
            if rep_user[0] == bonne_rep:
                st.success(f"✅ Correct ! {explication}")
                score += 1
            else:
                st.error(
                    f"❌ Incorrect. "
                    f"Bonne réponse : {bonne_rep}. "
                    f"{explication}"
                )
        st.divider()

    if total > 0:
        pct = int((score / total) * 100)
        st.markdown(f"### 🏆 Score : {score}/{total} ({pct}%)")
        if pct >= 80:
            st.balloons()
            st.success("Excellent ! Tu maîtrises ce cours !")
        elif pct >= 50:
            st.info("Bien ! Continue à réviser !")
        else:
            st.warning("Courage ! Relis le cours et réessaie !")