import streamlit as st
from database import fetch_dataframe
from auth import proteger_pagina, logout

proteger_pagina()
logout()

st.title("Saldos por Conta / Cartão")

st.markdown("Visão consolidada de saldo inicial, receitas recebidas, despesas pagas e saldo atual por conta/cartão.")

st.divider()

df = fetch_dataframe(
    """
    SELECT
        cc.nome AS conta_cartao,
        cc.tipo,
        COALESCE(cc.saldo_inicial, 0) AS saldo_inicial,

        COALESCE((
            SELECT SUM(r.valor)
            FROM receitas r
            WHERE r.data_recebimento IS NOT NULL
        ), 0) AS receitas_recebidas,

        COALESCE((
            SELECT SUM(d.valor)
            FROM despesas d
            WHERE d.data_pagamento IS NOT NULL
              AND d.conta_cartao = cc.nome
        ), 0) AS despesas_pagas,

        COALESCE(cc.saldo_inicial, 0)
        + COALESCE((
            SELECT SUM(r.valor)
            FROM receitas r
            WHERE r.data_recebimento IS NOT NULL
        ), 0)
        - COALESCE((
            SELECT SUM(d.valor)
            FROM despesas d
            WHERE d.data_pagamento IS NOT NULL
              AND d.conta_cartao = cc.nome
        ), 0) AS saldo_atual

    FROM contas_cartoes cc
    WHERE cc.ativo = TRUE
    ORDER BY cc.nome
    """
)

if df.empty:
    st.info("Nenhuma conta/cartão cadastrada.")
else:
    saldo_total = float(df["saldo_atual"].sum())

    st.metric("Saldo total consolidado", f"R$ {saldo_total:,.2f}")

    st.divider()

    st.dataframe(df, use_container_width=True, hide_index=True)