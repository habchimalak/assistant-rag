def afficher_quiz(quiz_texte):
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
        bonne_lettre = next(
            (l.replace("Reponse:", "").replace("Réponse:", "").strip()
             for l in lignes if l.startswith(("Reponse:", "Réponse:"))),
            "A"
        )
        explication = next(
            (l.replace("Explication:", "").strip()
             for l in lignes if l.startswith("Explication:")),
            ""
        )

        # Trouver le texte complet de la bonne réponse
        # ex: "B) Validation progressive..."
        bonne_rep_complete = next(
            (c for c in choix if c.startswith(bonne_lettre)),
            bonne_lettre
        )

        st.markdown(f"**{question}**")
        rep_user = st.radio(
            f"Question {i+1}",
            choix,
            key=f"q_{i}",
            label_visibility="collapsed"
        )

        if rep_user:
            if rep_user[0] == bonne_lettre:
                st.success(f"✅ Correct ! {explication}")
                score += 1
            else:
                # Affiche la réponse complète + explication
                st.error(
                    f"❌ Incorrect. "
                    f"Bonne réponse : {bonne_rep_complete}. "
                    f"{explication}"
                )
        st.divider()

    if total > 0:
        pct = int((score / total) * 100)
        st.markdown(f"### 🏆 Score : {score}/{total} ({pct}%)")
        if pct >= 80:
            st.balloons()
            st.success("Excellent ! Tu maitrises ce cours !")
        elif pct >= 50:
            st.info("Bien ! Continue a reviser !")
        else:
            st.warning("Courage ! Relis le cours et reessaie !")