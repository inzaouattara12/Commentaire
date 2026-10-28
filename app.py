
import streamlit as st
from supabase import create_client

# Configuration de la page
st.set_page_config(
    page_title="Mon chatbot de service client",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Mon chatbot de service client")
st.write(
    "Saisis une ou plusieurs phrases séparées par des points-virgules."
)

# Connexion à Supabase
@st.cache_resource
def connecter_supabase():
    url = st.secrets["SUPABASE_URL"]
    cle = st.secrets["SUPABASE_KEY"]
    return create_client(url, cle)

# Normalisation du texte
def normaliser(texte):
    return " ".join(texte.strip().lower().split())

# Recherche d'une réponse dans Supabase
def rechercher_reponse(question):
    question = normaliser(question)

    resultat = (
        supabase.table("phrases")
        .select("reponse")
        .eq("question", question)
        .limit(1)
        .execute()
    )

    if resultat.data:
        return resultat.data[0]["reponse"]

    return None

# Traitement de plusieurs phrases
def chatbot(texte):
    questions = [
        normaliser(q)
        for q in texte.split(";")
        if q.strip()
    ]

    resultats = []

    for question in questions:
        reponse = rechercher_reponse(question)

        resultats.append({
            "question": question,
            "reponse": reponse
        })

    return resultats

# Application du chatbot
try:
    supabase = connecter_supabase()
    st.success("Connexion à la base de données réussie.")

    texte = st.text_area(
        "Message du client",
        placeholder=(
            "Ex. : Entrer des commentaires ici..."
        ),
        height=120
    )

    if st.button("Obtenir les réponses", type="primary"):
        if not texte.strip():
            st.warning("Saisis d'abord un message.")
        else:
            try:
                with st.spinner("Recherche des réponses..."):
                    resultats = chatbot(texte)

                st.subheader("Résultats")

                for resultat in resultats:
                    st.markdown(
                        f"**Phrase saisie :** {resultat['question']}"
                    )

                    if resultat["reponse"] is not None:
                        st.success(
                            f"Réponse : {resultat['reponse']}"
                        )
                    else:
                        st.warning(
                            "Phrase non trouvée dans la base de données."
                        )

                    st.divider()

            except Exception as erreur:
                st.error("Erreur lors de la recherche.")
                st.code(str(erreur))

except Exception as erreur:
    st.error("Connexion impossible à Supabase.")
    st.code(str(erreur))
