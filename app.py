from datetime import datetime

import streamlit as st

from core.database import ensure_db


st.set_page_config(
    page_title="Chamadinha - Streamlit",
    page_icon=":brain:",
    layout="wide",
)

ensure_db()

st.title("Chamadinha - Reconhecimento Facial")
st.caption("Versao Streamlit para deploy sem alterar os scripts locais originais.")

st.markdown(
    """
### Como usar
1. Acesse `Cadastro e Reconhecimento` para enviar imagem e salvar rostos.
2. Use `Galeria e Edicao` para revisar, filtrar e atualizar registros.
3. Gere arquivos em `Planilha de Presenca`.
4. Valide conflitos em `Validar Duplicados`.
"""
)

st.info(
    "Banco SQLite desta versao: `streamlit_deploy/data/rostos.db`. "
    "Em deploy cloud, use storage persistente para nao perder dados."
)

st.write(f"Horario local: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
