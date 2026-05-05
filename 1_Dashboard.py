import streamlit as st
from datetime import date
from database import fetch_dataframe
from auth import proteger_pagina, logout
from theme import aplicar_design_portal, render_header, render_sidebar_brand

st.set_page_config(
    page_title="Financeiro Business Vision",
    layout="wide"
)

aplicar_design_portal()

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .stMetric {
        background-color: #0f172a;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1e293b;
    }

    .stDataFrame {
        border-radius: 10px;
    }

    .stAlert {
        border-radius: 8px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data):
    return data.strftime("%d/%m/%Y") if data else "-"


proteger_pagina()

render_sidebar_brand()

st.sidebar.write(f"Usuário: {st.session_state['usuario_nome']}")
logout()

render_header(
    "Financeiro Business Vision",
    "Dashboard financeiro executivo"
)
st.divider()

col_f1, col_f2 = st.columns(2)

with col_f1:
    data_inicio = st.date_input(
        "Data inicial",
        value=date.today().replace(day=1)
    )

with col_f2:
    data_fim = st.date_input(
        "Data final",
        value=date.today()
    )

params = {
    "data_inicio": data_inicio,
    "data_fim": data_fim,
}

st.divider()

df = fetch_dataframe(
    """
    SELECT
        COALESCE((
            SELECT SUM(valor)
            FROM receitas
            WHERE data_vencimento BETWEEN :data_inicio AND :data_fim
        ), 0) AS receita_prevista,

        COALESCE((
            SELECT SUM(valor)
            FROM receitas
            WHERE data_recebimento BETWEEN :data_inicio AND :data_fim
        ), 0) AS receita_recebida,

        COALESCE((
            SELECT SUM(valor)
            FROM despesas
            WHERE data_vencimento BETWEEN :data_inicio AND :data_fim
              AND data_pagamento IS NULL
        ), 0) AS despesas_abertas,

        COALESCE((
            SELECT SUM(valor)
            FROM despesas
            WHERE data_pagamento BETWEEN :data_inicio AND :data_fim
        ), 0) AS despesas_pagas,

        COALESCE((
            SELECT SUM(valor)
            FROM planejamento_das
            WHERE data_prevista_pagamento BETWEEN :data_inicio AND :data_fim
              AND status <> 'pago'
        ), 0) AS das_pendente
    """,
    params
)

dados = df.iloc[0]

receita_prevista = float(dados["receita_prevista"])
receita_recebida = float(dados["receita_recebida"])
despesas_abertas = float(dados["despesas_abertas"])
despesas_pagas = float(dados["despesas_pagas"])
das_pendente = float(dados["das_pendente"])

saldo_projetado = receita_prevista - despesas_abertas - das_pendente
saldo_realizado = receita_recebida - despesas_pagas

col1, col2, col3, col4 = st.columns(4)

col1.metric("Receita prevista", moeda(receita_prevista))
col2.metric("Receita recebida", moeda(receita_recebida))
col3.metric("Despesas abertas", moeda(despesas_abertas))
col4.metric("Despesas pagas", moeda(despesas_pagas))

col5, col6, col7 = st.columns(3)

col5.metric("DAS pendente", moeda(das_pendente))
col6.metric("Saldo projetado", moeda(saldo_projetado))
col7.metric("Saldo realizado", moeda(saldo_realizado))

st.divider()

st.subheader("Pendências críticas")

pendencias = fetch_dataframe(
    """
    SELECT
        'Receita atrasada' AS tipo,
        cliente AS descricao,
        valor,
        data_vencimento AS vencimento,
        'atrasado' AS status
    FROM receitas
    WHERE data_recebimento IS NULL
      AND data_vencimento < CURRENT_DATE

    UNION ALL

    SELECT
        'Despesa atrasada' AS tipo,
        fornecedor || ' - ' || descricao AS descricao,
        valor,
        data_vencimento AS vencimento,
        'atrasado' AS status
    FROM despesas
    WHERE data_pagamento IS NULL
      AND data_vencimento < CURRENT_DATE

    UNION ALL

    SELECT
        'DAS atrasado' AS tipo,
        mes_referente AS descricao,
        valor,
        data_prevista_pagamento AS vencimento,
        'atrasado' AS status
    FROM planejamento_das
    WHERE status <> 'pago'
      AND data_prevista_pagamento < CURRENT_DATE

    ORDER BY vencimento ASC
    LIMIT 20
    """
)

if pendencias.empty:
    st.success("Nenhuma pendência crítica encontrada.")
else:
    pendencias["valor"] = pendencias["valor"].apply(moeda)
    pendencias["vencimento"] = pendencias["vencimento"].apply(formatar_data)
    pendencias["status"] = "🔴 ATRASADO"

    st.dataframe(
        pendencias,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("Próximos vencimentos")

vencimentos = fetch_dataframe(
    """
    SELECT
        'Receita' AS tipo,
        cliente AS descricao,
        valor,
        data_vencimento AS vencimento,
        CASE
            WHEN data_recebimento IS NOT NULL THEN 'recebido'
            WHEN data_vencimento < CURRENT_DATE THEN 'atrasado'
            ELSE 'previsto'
        END AS status
    FROM receitas
    WHERE data_recebimento IS NULL

    UNION ALL

    SELECT
        'Despesa' AS tipo,
        fornecedor || ' - ' || descricao AS descricao,
        valor,
        data_vencimento AS vencimento,
        CASE
            WHEN data_pagamento IS NOT NULL THEN 'pago'
            WHEN data_vencimento < CURRENT_DATE THEN 'atrasado'
            ELSE 'aberto'
        END AS status
    FROM despesas
    WHERE data_pagamento IS NULL

    UNION ALL

    SELECT
        'DAS' AS tipo,
        mes_referente AS descricao,
        valor,
        data_prevista_pagamento AS vencimento,
        CASE
            WHEN status = 'pago' THEN 'pago'
            WHEN data_prevista_pagamento < CURRENT_DATE THEN 'atrasado'
            ELSE status
        END AS status
    FROM planejamento_das
    WHERE status <> 'pago'

    ORDER BY vencimento ASC
    LIMIT 20
    """
)

if vencimentos.empty:
    st.info("Nenhum vencimento pendente encontrado.")
else:
    def status_formatado(status):
        mapa = {
            "recebido": "🟢 RECEBIDO",
            "pago": "🟢 PAGO",
            "previsto": "🟡 PREVISTO",
            "aberto": "🟡 ABERTO",
            "atrasado": "🔴 ATRASADO",
            "pendente": "🟠 PENDENTE",
            "programado": "🔵 PROGRAMADO",
        }
        return mapa.get(status, status.upper())

    vencimentos["valor"] = vencimentos["valor"].apply(moeda)
    vencimentos["vencimento"] = vencimentos["vencimento"].apply(formatar_data)
    vencimentos["status"] = vencimentos["status"].apply(status_formatado)

    st.dataframe(
        vencimentos,
        use_container_width=True,
        hide_index=True
    )