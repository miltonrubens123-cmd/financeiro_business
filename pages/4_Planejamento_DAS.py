import streamlit as st
from database import execute_query, fetch_dataframe
from auth import proteger_pagina, logout
from theme import aplicar_design_portal, render_header, render_sidebar_brand

aplicar_design_portal()
proteger_pagina()
render_sidebar_brand()
st.sidebar.write(f"Usuário: {st.session_state['usuario_nome']}")
render_header(
    "Planejamento DAS",
    "Gestão dos DAS atrasados e previsão de pagamento"
)
logout("logout_planejamento_das")
st.divider()

with st.expander("Novo planejamento DAS", expanded=False):
    with st.form("form_das"):
        mes_referente = st.text_input("Mês referente", placeholder="Ex: 2025-12")

        valor = st.number_input(
            "Valor",
            min_value=0.0,
            step=100.0,
            format="%.2f"
        )

        data_prevista_pagamento = st.date_input("Data prevista de pagamento")

        status = st.selectbox(
            "Status",
            ["pendente", "programado", "pago", "atrasado"]
        )

        observacao = st.text_area("Observação")

        salvar = st.form_submit_button("Salvar planejamento")

        if salvar:
            if not mes_referente or valor <= 0:
                st.error("Preencha mês referente e valor corretamente.")
            else:
                execute_query(
                    """
                    INSERT INTO planejamento_das (
                        mes_referente,
                        valor,
                        data_prevista_pagamento,
                        status,
                        observacao
                    )
                    VALUES (
                        :mes_referente,
                        :valor,
                        :data_prevista_pagamento,
                        :status,
                        :observacao
                    )
                    """,
                    {
                        "mes_referente": mes_referente,
                        "valor": valor,
                        "data_prevista_pagamento": data_prevista_pagamento,
                        "status": status,
                        "observacao": observacao,
                    }
                )

                st.success("Planejamento DAS cadastrado com sucesso.")
                st.rerun()

st.divider()

st.subheader("DAS cadastrados")

df = fetch_dataframe(
    """
    SELECT
        id,
        mes_referente,
        valor,
        data_prevista_pagamento,
        CASE
            WHEN status = 'pago' THEN 'pago'
            WHEN data_prevista_pagamento < CURRENT_DATE THEN 'atrasado'
            ELSE status
        END AS status,
        observacao
    FROM planejamento_das
    ORDER BY data_prevista_pagamento ASC
    """
)

if df.empty:
    st.info("Nenhum DAS cadastrado ainda.")
else:
    for _, row in df.iterrows():
        with st.expander(
            f"{row['mes_referente']} | R$ {row['valor']} | {row['status']}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"Mês referente: {row['mes_referente']}")
                st.write(f"Valor: R$ {row['valor']}")
                st.write(f"Data prevista: {row['data_prevista_pagamento']}")

            with col2:
                st.write(f"Status: {row['status']}")
                st.write(f"Observação: {row['observacao']}")

            col_pago, col_delete = st.columns(2)

            with col_pago:
                if row["status"] != "pago":
                    if st.button("Marcar como pago", key=f"pago_das_{row['id']}"):
                        execute_query(
                            """
                            UPDATE planejamento_das
                            SET status = 'pago',
                                atualizado_em = CURRENT_TIMESTAMP
                            WHERE id = :id
                            """,
                            {"id": row["id"]}
                        )
                        st.success("DAS marcado como pago.")
                        st.rerun()

            with col_delete:
                if st.button("Excluir", key=f"delete_das_{row['id']}"):
                    execute_query(
                        "DELETE FROM planejamento_das WHERE id = :id",
                        {"id": row["id"]}
                    )
                    st.warning("DAS excluído.")
                    st.rerun()