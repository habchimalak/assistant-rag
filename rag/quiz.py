import streamlit as st


def generer_quiz(retriever, llm, nb_questions):
    docs = retriever.invoke("concepts importants definitions")
    contexte = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
    Tu es un professeur. Genere exactement {nb_questions}
    questions QCM basees sur ce contenu.
    Chaque question a 4 choix (A, B, C, D) et UNE seule
    bonne reponse.

    Format OBLIGATOIRE :
    Q1: [question]
    A) [choix]
    B) [choix]
    C) [choix]
    D) [choix]
    Reponse: [lettre]
    Explication: [courte explication]
    ---

    Contenu : {contexte}
    Genere les questions en francais.
    """
    return llm.invoke(prompt).content


def afficher_quiz(quiz_texte):
    questions = [q for q in quiz_texte.split("---") if q.strip()]

    # Initialiser les réponses et validations
    if "reponses_user" not in st.session_state:
        st.session_state.reponses_user = {}
    if "validees" not in st.session_state:
        st.session_state.validees = {}

    score = 0
    total = 0

    for i, bloc in enumerate(questions):
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
            (l.replace("Reponse:", "").strip()
             for l in lignes if l.startswith("Reponse:")),
            "A"
        )
        explication = next(
            (l.replace("Explication:", "").strip()
             for l in lignes if l.startswith("Explication:")),
            ""
        )

        # Afficher la question
        st.markdown(f"**{question}**")

        # Si pas encore validée — afficher les choix
        if not st.session_state.validees.get(i):
            rep = st.radio(
                f"Choix {i+1}",
                choix,
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            st.session_state.reponses_user[i] = rep

            # Bouton valider
            if st.button("Valider", key=f"btn_{i}"):
                st.session_state.validees[i] = True
                st.rerun()

        # Si validée — afficher le résultat
        else:
            rep_choisie = st.session_state.reponses_user.get(i, "")

            # Afficher les choix en lecture seule
            for c in choix:
                lettre = c[0]
                if lettre == bonne_rep and lettre == (rep_choisie[0] if rep_choisie else ""):
                    st.markdown(f"✅ **{c}** ← Ta réponse — Correct !")
                elif lettre == bonne_rep:
                    st.markdown(f"✅ **{c}** ← Bonne réponse")
                elif rep_choisie and lettre == rep_choisie[0]:
                    st.markdown(f"❌ {c} ← Ta réponse")
                else:
                    st.markdown(f"○ {c}")

            # Explication
            if rep_choisie and rep_choisie[0] == bonne_rep:
                st.success(f"Correct ! {explication}")
                score += 1
            else:
                st.error(f"Incorrect. {explication}")

        st.divider()

    # Score final — seulement si tout est validé
    if total > 0 and len(st.session_state.validees) == total:
        pct = int((score / total) * 100)
        st.markdown(f"### Score final : {score}/{total} ({pct}%)")
        if pct >= 80:
            st.balloons()
            st.success("Excellent ! Tu maitrises ce cours !")
        elif pct >= 50:
            st.info("Bien ! Continue a reviser !")
        else:
            st.warning("Courage ! Relis le cours et reessaie !")

        if st.button("Recommencer le quiz"):
            st.session_state.quiz = None
            st.session_state.reponses_user = {}
            st.session_state.validees = {}
            st.rerun()
