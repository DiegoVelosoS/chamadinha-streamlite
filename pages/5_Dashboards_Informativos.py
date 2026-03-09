from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from core.database import ensure_db, fetch_df
from core.theme import get_theme_tokens, setup_theme


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _build_dashboard_data(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    base["nome"] = base["nome"].apply(_normalize_text)
    base["id_rosto"] = base["id_rosto"].apply(_normalize_text)
    base["turma"] = base["turma"].apply(_normalize_text)
    base["identificador"] = base.apply(
        lambda row: row["nome"] if row["nome"] else f"SEM_NOME::{row['id_rosto']}",
        axis=1,
    )

    base = base.dropna(subset=["numero_imagem"])
    base["numero_imagem"] = pd.to_numeric(base["numero_imagem"], errors="coerce")
    base = base.dropna(subset=["numero_imagem"])
    base["numero_imagem"] = base["numero_imagem"].astype(int)

    # Remove repeticoes da mesma pessoa na mesma chamada para evitar dupla contagem.
    presencas = base.drop_duplicates(subset=["turma", "identificador", "numero_imagem"], keep="first")

    total_alunos = (
        base[["turma", "identificador"]]
        .drop_duplicates()
        .groupby("turma", as_index=False)
        .size()
        .rename(columns={"size": "total_alunos"})
    )

    total_aulas = (
        base[["turma", "numero_imagem"]]
        .drop_duplicates()
        .groupby("turma", as_index=False)
        .size()
        .rename(columns={"size": "total_aulas"})
    )

    total_presencas = (
        presencas.groupby("turma", as_index=False)
        .size()
        .rename(columns={"size": "total_presencas"})
    )

    resumo = total_alunos.merge(total_aulas, on="turma", how="outer").merge(total_presencas, on="turma", how="outer")
    resumo = resumo.fillna(0)

    resumo["total_alunos"] = resumo["total_alunos"].astype(int)
    resumo["total_aulas"] = resumo["total_aulas"].astype(int)
    resumo["total_presencas"] = resumo["total_presencas"].astype(int)
    resumo["total_faltas"] = (resumo["total_alunos"] * resumo["total_aulas"] - resumo["total_presencas"]).astype(int)
    resumo = resumo.sort_values(by="turma", ascending=True).reset_index(drop=True)

    return resumo


def _build_face_dashboard_data(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    base["nome"] = base["nome"].apply(_normalize_text)
    base["id_rosto"] = base["id_rosto"].apply(_normalize_text)
    base["turma"] = base["turma"].apply(_normalize_text)
    base["identificador"] = base.apply(
        lambda row: row["nome"] if row["nome"] else f"SEM_NOME::{row['id_rosto']}",
        axis=1,
    )

    base = base.dropna(subset=["numero_imagem"])
    base["numero_imagem"] = pd.to_numeric(base["numero_imagem"], errors="coerce")
    base = base.dropna(subset=["numero_imagem"])
    base["numero_imagem"] = base["numero_imagem"].astype(int)

    pessoas = (
        base[["turma", "identificador"]]
        .drop_duplicates()
        .sort_values(by=["turma", "identificador"], ascending=True)
        .reset_index(drop=True)
    )

    total_aulas_turma = (
        base[["turma", "numero_imagem"]]
        .drop_duplicates()
        .groupby("turma", as_index=False)
        .size()
        .rename(columns={"size": "total_aulas_turma"})
    )

    presencas_unicas = base.drop_duplicates(subset=["turma", "identificador", "numero_imagem"], keep="first")
    total_presencas = (
        presencas_unicas.groupby(["turma", "identificador"], as_index=False)
        .size()
        .rename(columns={"size": "presencas"})
    )

    resumo_rosto = pessoas.merge(total_aulas_turma, on="turma", how="left").merge(
        total_presencas,
        on=["turma", "identificador"],
        how="left",
    )
    resumo_rosto = resumo_rosto.fillna(0)

    resumo_rosto["total_aulas_turma"] = resumo_rosto["total_aulas_turma"].astype(int)
    resumo_rosto["presencas"] = resumo_rosto["presencas"].astype(int)
    resumo_rosto["faltas"] = (resumo_rosto["total_aulas_turma"] - resumo_rosto["presencas"]).clip(lower=0).astype(int)
    resumo_rosto["taxa_presenca_pct"] = (
        (resumo_rosto["presencas"] / resumo_rosto["total_aulas_turma"].replace(0, pd.NA)) * 100
    ).fillna(0).round(1)

    return resumo_rosto


def _style_chart(chart: alt.Chart, theme_tokens: dict[str, str]) -> alt.Chart:
    return (
        chart.configure_axis(
            labelColor=theme_tokens["chart_axis"],
            titleColor=theme_tokens["chart_axis"],
            gridColor=theme_tokens["chart_grid"],
            tickColor=theme_tokens["chart_axis"],
            domainColor=theme_tokens["chart_axis"],
        )
        .configure_legend(
            titleColor=theme_tokens["chart_axis"],
            labelColor=theme_tokens["chart_axis"],
        )
        .configure_view(strokeOpacity=0)
        .configure(background=theme_tokens["chart_background"])
    )


ensure_db()
current_theme = setup_theme(show_toggle=True, toggle_location="sidebar")
theme_tokens = get_theme_tokens(current_theme)
st.title("Dashboards Informativos")

df = fetch_df(
    """
    SELECT id_rosto, nome, turma, numero_imagem
    FROM rostos
    ORDER BY ord_id ASC
    """
)

if df.empty:
    st.info("Ainda nao ha dados para montar os dashboards.")
    st.stop()

resumo_turma = _build_dashboard_data(df)
resumo_rosto = _build_face_dashboard_data(df)

if resumo_turma.empty:
    st.warning("Nao foi possivel consolidar os indicadores com os dados atuais.")
    st.stop()

st.subheader("Total de presenças e faltas")

total_presencas_geral = int(resumo_turma["total_presencas"].sum())
total_faltas_geral = int(resumo_turma["total_faltas"].sum())
total_alunos_geral = int(resumo_turma["total_alunos"].sum())
total_aulas_geral = int(resumo_turma["total_aulas"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Presenças", total_presencas_geral)
c1.markdown(
    f"<p style='margin:0; font-size:0.78rem; color:{theme_tokens['text_muted']};'>geral</p>",
    unsafe_allow_html=True,
)
c2.metric("Faltas", total_faltas_geral)
c2.markdown(
    f"<p style='margin:0; font-size:0.78rem; color:{theme_tokens['text_muted']};'>geral</p>",
    unsafe_allow_html=True,
)
c3.metric("Alunos", total_alunos_geral)
c3.markdown(
    f"<p style='margin:0; font-size:0.78rem; color:{theme_tokens['text_muted']};'>soma por turma</p>",
    unsafe_allow_html=True,
)
c4.metric("Aulas", total_aulas_geral)
c4.markdown(
    f"<p style='margin:0; font-size:0.78rem; color:{theme_tokens['text_muted']};'>soma por turma</p>",
    unsafe_allow_html=True,
)

st.subheader("Dados por turma")

table_df = resumo_turma.rename(
    columns={
        "turma": "turma",
        "total_alunos": "alunos",
        "total_aulas": "aulas",
        "total_presencas": "presencas",
        "total_faltas": "faltas",
    }
)
st.dataframe(table_df, use_container_width=True)

st.subheader("Gráfico horizontal de presenças e faltas por turma")

chart_base = resumo_turma[["turma", "total_presencas", "total_faltas"]].rename(
    columns={"total_presencas": "presencas", "total_faltas": "faltas"}
)
chart_long = chart_base.melt(id_vars="turma", var_name="tipo", value_name="quantidade")
chart_long["quantidade"] = chart_long["quantidade"].astype(int)

chart = (
    alt.Chart(chart_long)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X(
            "quantidade:Q",
            title="Quantidade",
            axis=alt.Axis(format="d", tickMinStep=1),
            scale=alt.Scale(domainMin=0, nice=False),
        ),
        y=alt.Y("turma:N", title="Turma", sort="-x"),
        color=alt.Color(
            "tipo:N",
            title="Tipo",
            scale=alt.Scale(
                domain=["presencas", "faltas"],
                range=[theme_tokens["chart_presence"], theme_tokens["chart_absence"]],
            ),
        ),
        xOffset="tipo:N",
        tooltip=["turma:N", "tipo:N", alt.Tooltip("quantidade:Q", format=".0f")],
    )
    .properties(height=420)
)

chart = _style_chart(chart, theme_tokens)

st.altair_chart(chart, use_container_width=True)

st.subheader("Dados por rosto cadastrado (geral)")

face_table_df_geral = resumo_rosto.rename(
    columns={
        "turma": "turma",
        "identificador": "rosto",
        "total_aulas_turma": "aulas_turma",
        "presencas": "presencas",
        "faltas": "faltas",
        "taxa_presenca_pct": "taxa_presenca_pct",
    }
)
st.dataframe(face_table_df_geral, use_container_width=True)

st.subheader("Grafico horizontal de presencas e faltas por rosto (geral)")

face_chart_base_geral = resumo_rosto[["turma", "identificador", "presencas", "faltas"]].copy()
face_chart_base_geral["rosto"] = face_chart_base_geral.apply(
    lambda row: f"{row['identificador']} ({row['turma']})",
    axis=1,
)
face_chart_long_geral = face_chart_base_geral[["rosto", "presencas", "faltas"]].melt(
    id_vars="rosto",
    var_name="tipo",
    value_name="quantidade",
)
face_chart_long_geral["quantidade"] = face_chart_long_geral["quantidade"].astype(int)

chart_height_geral = max(320, min(1200, int(len(face_chart_base_geral) * 34)))

face_chart_geral = (
    alt.Chart(face_chart_long_geral)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X(
            "quantidade:Q",
            title="Quantidade",
            axis=alt.Axis(format="d", tickMinStep=1),
            scale=alt.Scale(domainMin=0, nice=False),
        ),
        y=alt.Y("rosto:N", title="Rosto", sort="-x"),
        color=alt.Color(
            "tipo:N",
            title="Tipo",
            scale=alt.Scale(
                domain=["presencas", "faltas"],
                range=[theme_tokens["chart_presence"], theme_tokens["chart_absence"]],
            ),
        ),
        xOffset="tipo:N",
        tooltip=["rosto:N", "tipo:N", alt.Tooltip("quantidade:Q", format=".0f")],
    )
    .properties(height=chart_height_geral)
)

face_chart_geral = _style_chart(face_chart_geral, theme_tokens)

st.altair_chart(face_chart_geral, use_container_width=True)

st.subheader("Presenca e falta por rosto separado por turma")

turmas_disponiveis = sorted(resumo_rosto["turma"].dropna().unique().tolist())
turma_selecionada = st.selectbox("Selecione a turma", turmas_disponiveis)

resumo_rosto_turma = (
    resumo_rosto[resumo_rosto["turma"] == turma_selecionada]
    .copy()
    .sort_values(by=["presencas", "identificador"], ascending=[False, True])
    .reset_index(drop=True)
)

face_total_presencas = int(resumo_rosto_turma["presencas"].sum())
face_total_faltas = int(resumo_rosto_turma["faltas"].sum())
face_total_rostos = int(len(resumo_rosto_turma))

f1, f2, f3 = st.columns(3)
f1.metric("Presencas da turma", face_total_presencas)
f2.metric("Faltas da turma", face_total_faltas)
f3.metric("Rostos cadastrados", face_total_rostos)

face_table_df = resumo_rosto_turma.rename(
    columns={
        "identificador": "rosto",
        "total_aulas_turma": "aulas_turma",
        "presencas": "presencas",
        "faltas": "faltas",
        "taxa_presenca_pct": "taxa_presenca_pct",
    }
)[["rosto", "aulas_turma", "presencas", "faltas", "taxa_presenca_pct"]]
st.dataframe(face_table_df, use_container_width=True)

st.subheader("Grafico horizontal de presencas e faltas por rosto da turma")

face_chart_base = resumo_rosto_turma[["identificador", "presencas", "faltas"]].rename(
    columns={"identificador": "rosto"}
)
face_chart_long = face_chart_base.melt(
    id_vars="rosto",
    var_name="tipo",
    value_name="quantidade",
)
face_chart_long["quantidade"] = face_chart_long["quantidade"].astype(int)

chart_height = max(320, min(1200, int(len(face_chart_base) * 34)))

face_chart = (
    alt.Chart(face_chart_long)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X(
            "quantidade:Q",
            title="Quantidade",
            axis=alt.Axis(format="d", tickMinStep=1),
            scale=alt.Scale(domainMin=0, nice=False),
        ),
        y=alt.Y("rosto:N", title="Rosto", sort="-x"),
        color=alt.Color(
            "tipo:N",
            title="Tipo",
            scale=alt.Scale(
                domain=["presencas", "faltas"],
                range=[theme_tokens["chart_presence"], theme_tokens["chart_absence"]],
            ),
        ),
        xOffset="tipo:N",
        tooltip=["rosto:N", "tipo:N", alt.Tooltip("quantidade:Q", format=".0f")],
    )
    .properties(height=chart_height)
)

face_chart = _style_chart(face_chart, theme_tokens)

st.altair_chart(face_chart, use_container_width=True)
