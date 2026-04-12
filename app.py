from datetime import datetime

import streamlit as st

from core.database import ensure_db, export_db_bytes, import_db_bytes, reset_db
from core.theme import get_theme_tokens, setup_theme


st.set_page_config(
    page_title="TCC-Diego",
    page_icon=":brain:",
    layout="wide",
)

current_theme = setup_theme(show_toggle=True, toggle_location="main")
theme_tokens = get_theme_tokens(current_theme)

ensure_db()

st.title("VISÃO COMPUTACIONAL PARA PROCESSAMENTO ASSÍNCRONO DE IMAGENS E EMBEDDINGS FACIAIS NO CONTROLE DE FREQUÊNCIAS: UMA ABORDAGEM DE APLICAÇÃO PRÁTICA DA INDÚSTRIA 4.0")
st.markdown(
    f"""
<p style="margin:0; line-height:1.35; color:{theme_tokens['text_muted']}; font-size:0.95rem;">
Sistema para registro de presença por meio de Reconhecimento Facial em fotos de grupo.<br>
TCC - Diego Veloso - UFRR/ECAI 2026.1<br>
Versao em Streamlit
</p>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
### Como usar
1. Comece em `Cadastro e Reconhecimento`: envie a foto da turma e confirme os rostos detectados.
2. Acesse `Galeria e Edicao` para revisar cadastros, corrigir nomes e ajustar registros quando necessario.
3. Em `Planilha de Presenca`, selecione o periodo/turma e gere a planilha consolidada.
4. Antes de fechar o fluxo, use `Validar Duplicados` para identificar e resolver possiveis cadastros repetidos.
5. Consulte `Dashboards Informativos` para acompanhar metricas gerais e evolucao dos registros.
"""
)

st.info(
    "Banco SQLite desta versao: `streamlit_deploy/data/rostos.db`. "
    "Em deploy cloud, use storage persistente para nao perder dados."
)

with st.expander("Backup e restauracao do banco (SQLite)", expanded=False):
    st.write(
        "Use esta opcao minima para continuar de onde parou: "
        "baixe um backup (`rostos.db`) ao encerrar a sessao e envie esse arquivo no proximo acesso."
    )
    st.caption(
        "Observacao: esse fluxo nao evita conflitos de edicao simultanea entre varias sessoes. "
        "Ele funciona como backup/restore manual."
    )


    backup_bytes = export_db_bytes()
    st.download_button(
        label="Baixar backup do banco (.db)",
        data=backup_bytes,
        file_name=f"rostos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
        mime="application/octet-stream",
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader(":warning: Resetar sistema (apagar todos os dados)")
    st.caption("Esta ação irá apagar **todos os registros** do banco de dados, sem possibilidade de recuperação. Faça backup antes!")
    if st.button("Resetar banco de dados", type="secondary", use_container_width=True):
        if st.confirm("Tem certeza que deseja apagar **todos os dados** do sistema? Esta ação é irreversível."):
            try:
                reset_db()
            except Exception as exc:
                st.error(f"Erro ao resetar banco: {exc}")
            else:
                st.success("Todos os dados foram apagados com sucesso.")
                st.info("Recarregue a página para refletir o banco limpo.")

    uploaded_backup = st.file_uploader(
        "Restaurar de backup (.db)",
        type=["db", "sqlite", "sqlite3"],
        accept_multiple_files=False,
        help="Envie um arquivo de backup SQLite previamente baixado pelo sistema.",
    )

    if uploaded_backup is not None:
        if st.button("Aplicar backup enviado", type="primary", use_container_width=True):
            try:
                restore_point = import_db_bytes(uploaded_backup.getvalue(), create_restore_point=True)
            except Exception as exc:
                st.error(f"Falha ao restaurar backup: {exc}")
            else:
                if restore_point:
                    st.success(
                        "Backup restaurado com sucesso. "
                        f"Foi criado um ponto de restauracao local em: `{restore_point}`"
                    )
                else:
                    st.success("Backup restaurado com sucesso.")
                st.info("Recarregue a pagina para refletir os dados restaurados em todas as telas.")

st.write(f"Horario local: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
