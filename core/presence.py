from __future__ import annotations

from io import BytesIO

import pandas as pd


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text


def build_presence_sheet(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    required = ["id_rosto", "nome", "turma", "numero_imagem", "data_imagem"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes: {missing}")

    base = df.copy()
    base["nome_limpo"] = base["nome"].apply(_normalize_text)
    base["id_rosto"] = base["id_rosto"].apply(_normalize_text)
    base["turma"] = base["turma"].apply(_normalize_text)
    base["data_imagem"] = base["data_imagem"].apply(_normalize_text)
    base["identificador"] = base.apply(
        lambda row: row["nome_limpo"] if row["nome_limpo"] else f"SEM_NOME::{row['id_rosto']}",
        axis=1,
    )

    image_numbers = sorted(
        {
            int(n)
            for n in base["numero_imagem"].tolist()
            if pd.notna(n) and str(n).strip() != ""
        }
    )

    records: list[dict[str, object]] = []
    for ident, group in base.groupby("identificador", sort=False):
        group = group.copy()
        group["data_imagem_dt"] = pd.to_datetime(group["data_imagem"], errors="coerce")
        group = group.sort_values(by=["data_imagem_dt", "ord_id"], ascending=True, na_position="last")

        names = [n for n in group["nome_limpo"].tolist() if n]
        classes = [t for t in group["turma"].tolist() if t]
        ids = [i for i in group["id_rosto"].tolist() if i]

        row = {
            "id_rosto": ", ".join(ids),
            "nome": names[0] if names else "",
            "turma": classes[0] if classes else "",
        }

        first_by_image = group.drop_duplicates(subset=["numero_imagem"], keep="first")
        map_image_date = {
            int(r["numero_imagem"]): r["data_imagem"]
            for _, r in first_by_image.iterrows()
            if pd.notna(r["numero_imagem"]) and str(r["numero_imagem"]).strip() != ""
        }

        occurrences: list[object] = []
        total_presence = 0
        for img_num in image_numbers:
            if img_num in map_image_date:
                total_presence += 1
                occurrences.extend([img_num, map_image_date[img_num]])
            else:
                occurrences.extend(["", ""])

        row["_occ"] = occurrences
        row["total_presencas"] = total_presence
        records.append(row)

    if not records:
        return pd.DataFrame()

    cols = ["id_rosto", "nome", "turma"]
    for img_num in image_numbers:
        cols.extend([f"numero_imagem_{img_num}", f"data_imagem_{img_num}"])
    cols.append("total_presencas")

    out_rows = []
    for rec in records:
        row = [rec["id_rosto"], rec["nome"], rec["turma"]]
        row.extend(rec["_occ"])
        row.append(rec["total_presencas"])
        out_rows.append(row)

    out = pd.DataFrame(out_rows, columns=cols)
    out = out.sort_values(by=["nome", "id_rosto"], ascending=True).reset_index(drop=True)
    return out


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def dataframe_to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output.read()
