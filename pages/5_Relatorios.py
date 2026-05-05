import streamlit as st
from datetime import date
from database import fetch_dataframe
import pandas as pd
from io import BytesIO

st.title("Relatórios")

st.markdown("Análise financeira por período, categoria e resultado consolidado.")

st.divider()

col_f1, col_f2 = st.columns(2)

with col_f1:
    data_inicio = st.date_input("Data inicial", value=date.today().replace(day=1))

with col_f2:
    data_fim = st.date_input("Data final", value=date.today())

params = {
    "data_inicio": data_inicio,
    "data_fim": data_fim,
}

st.divider()

# =====================
# DADOS
# =====================

receitas = fetch_dataframe(
    """
    SELECT *
    FROM receitas
    WHERE data_vencimento BETWEEN :data_inicio AND :data_fim
       OR data_recebimento BETWEEN :data_inicio AND :data_fim
    ORDER BY data_vencimento ASC
    """,
    params
)

despesas = fetch_dataframe(
    """
    SELECT *
    FROM despesas
    WHERE data_vencimento BETWEEN :data_inicio AND :data_fim
       OR data_pagamento BETWEEN :data_inicio AND :data_fim
    ORDER BY data_vencimento ASC
    """,
    params
)

das = fetch_dataframe(
    """
    SELECT *
    FROM planejamento_das
    WHERE data_prevista_pagamento BETWEEN :data_inicio AND :data_fim
    ORDER BY data_prevista_pagamento ASC
    """,
    params
)

# =====================
# RESUMO
# =====================

receita_total = receitas["valor"].sum() if not receitas.empty else 0
despesa_total = despesas["valor"].sum() if not despesas.empty else 0
resultado = receita_total - despesa_total

col1, col2, col3 = st.columns(3)

col1.metric("Receitas", f"R$ {receita_total:,.2f}")
col2.metric("Despesas", f"R$ {despesa_total:,.2f}")
col3.metric("Resultado", f"R$ {resultado:,.2f}")

st.divider()

# =====================
# TABELAS
# =====================

st.subheader("Receitas")
st.dataframe(receitas, use_container_width=True)

st.subheader("Despesas")
st.dataframe(despesas, use_container_width=True)

st.subheader("DAS")
st.dataframe(das, use_container_width=True)

st.divider()

# =====================
# EXPORTAÇÃO EXCEL
# =====================

def gerar_excel():
    output = BytesIO()

    with pd.ExcelWriter(output) as writer:
        receitas.to_excel(writer, sheet_name="Receitas", index=False)
        despesas.to_excel(writer, sheet_name="Despesas", index=False)
        das.to_excel(writer, sheet_name="DAS", index=False)

        resumo = pd.DataFrame({
            "Indicador": ["Receitas", "Despesas", "Resultado"],
            "Valor": [receita_total, despesa_total, resultado]
        })

        resumo.to_excel(writer, sheet_name="Resumo", index=False)

    return output.getvalue()

excel_data = gerar_excel()

st.download_button(
    label="📥 Baixar relatório em Excel",
    data=excel_data,
    file_name=f"relatorio_financeiro_{data_inicio}_{data_fim}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)