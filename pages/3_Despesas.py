import streamlit as st
from database import execute_query, fetch_dataframe
from auth import proteger_pagina, logout
from theme import aplicar_design_portal, render_header, render_sidebar_brand


aplicar_design_portal()
proteger_pagina()
render_sidebar_brand()

st.sidebar.write(f"Usuário: {st.session_state['usuario_nome']}")

render_header(
    "Despesas",
    "Gestão de saídas financeiras"
)
logout("logout_despesas")

st.divider()


def carregar_categorias_despesa():
    df = fetch_dataframe(
        """
        SELECT nome
        FROM categorias
        WHERE ativo = TRUE
          AND tipo IN ('despesa', 'ambos')
        ORDER BY nome
        """
    )
    return df["nome"].tolist() if not df.empty else []


def carregar_contas():
    df = fetch_dataframe(
        """
        SELECT nome
        FROM contas_cartoes
        WHERE ativo = TRUE
        ORDER BY nome
        """
    )
    return df["nome"].tolist() if not df.empty else []


categorias = carregar_categorias_despesa()
contas = carregar_contas()


with st.expander("Nova despesa", expanded=False):
    with st.form("form_despesa"):
        fornecedor = st.text_input("Fornecedor")
        descricao = st.text_area("Descrição")

        if not categorias:
            st.warning("Cadastre ao menos uma categoria de despesa em Configurações.")
            categoria = None
        else:
            categoria = st.selectbox("Categoria", categorias)

        if not contas:
            st.warning("Cadastre ao menos uma conta/cartão em Configurações.")
            conta_cartao = None
        else:
            conta_cartao = st.selectbox("Conta / Cartão", contas)

        valor = st.number_input(
            "Valor",
            min_value=0.0,
            step=100.0,
            format="%.2f"
        )

        data_vencimento = st.date_input("Data de vencimento")

        pago = st.checkbox("Despesa já paga?")
        recorrente = st.checkbox("Despesa recorrente?")

        data_pagamento = None

        if pago:
            data_pagamento = st.date_input("Data de pagamento")

        salvar = st.form_submit_button("Salvar despesa")

        if salvar:
            if not fornecedor or not descricao or not categoria or not conta_cartao or valor <= 0:
                st.error("Preencha fornecedor, descrição, categoria, conta/cartão e valor corretamente.")
            else:
                status = "pago" if pago else "aberto"

                execute_query(
                    """
                    INSERT INTO despesas (
                        fornecedor,
                        descricao,
                        categoria,
                        conta_cartao,
                        valor,
                        data_vencimento,
                        data_pagamento,
                        status,
                        recorrente
                    )
                    VALUES (
                        :fornecedor,
                        :descricao,
                        :categoria,
                        :conta_cartao,
                        :valor,
                        :data_vencimento,
                        :data_pagamento,
                        :status,
                        :recorrente
                    )
                    """,
                    {
                        "fornecedor": fornecedor.strip(),
                        "descricao": descricao.strip(),
                        "categoria": categoria,
                        "conta_cartao": conta_cartao,
                        "valor": valor,
                        "data_vencimento": data_vencimento,
                        "data_pagamento": data_pagamento,
                        "status": status,
                        "recorrente": recorrente,
                    }
                )

                st.success("Despesa cadastrada com sucesso.")
                st.rerun()


st.divider()
st.subheader("Despesas cadastradas")

df = fetch_dataframe(
    """
    SELECT
        id,
        fornecedor,
        descricao,
        categoria,
        conta_cartao,
        valor,
        data_vencimento,
        data_pagamento,
        recorrente,
        CASE
            WHEN data_pagamento IS NOT NULL THEN 'pago'
            WHEN data_vencimento < CURRENT_DATE THEN 'atrasado'
            ELSE 'aberto'
        END AS status
    FROM despesas
    ORDER BY data_vencimento DESC
    """
)

if df.empty:
    st.info("Nenhuma despesa cadastrada ainda.")
else:
    for _, row in df.iterrows():
        with st.expander(
            f"{row['fornecedor']} | {row['descricao']} | R$ {row['valor']:,.2f} | {row['status']}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"Fornecedor: {row['fornecedor']}")
                st.write(f"Descrição: {row['descricao']}")
                st.write(f"Categoria: {row['categoria']}")
                st.write(f"Conta / Cartão: {row['conta_cartao']}")

            with col2:
                st.write(f"Valor: R$ {row['valor']:,.2f}")
                st.write(f"Vencimento: {row['data_vencimento']}")
                st.write(f"Pagamento: {row['data_pagamento']}")
                st.write(f"Status: {row['status']}")
                st.write(f"Recorrente: {'Sim' if row['recorrente'] else 'Não'}")

            st.divider()

            with st.expander("Editar despesa", expanded=False):
                with st.form(f"form_editar_despesa_{row['id']}"):
                    edit_fornecedor = st.text_input(
                        "Fornecedor",
                        value=row["fornecedor"],
                        key=f"edit_fornecedor_{row['id']}"
                    )

                    edit_descricao = st.text_area(
                        "Descrição",
                        value=row["descricao"],
                        key=f"edit_descricao_{row['id']}"
                    )

                    categoria_atual = row["categoria"]

                    if categorias:
                        index_categoria = (
                            categorias.index(categoria_atual)
                            if categoria_atual in categorias
                            else 0
                        )

                        edit_categoria = st.selectbox(
                            "Categoria",
                            categorias,
                            index=index_categoria,
                            key=f"edit_categoria_{row['id']}"
                        )
                    else:
                        edit_categoria = None
                        st.warning("Cadastre categorias em Configurações.")

                    conta_atual = row["conta_cartao"]

                    if contas:
                        index_conta = (
                            contas.index(conta_atual)
                            if conta_atual in contas
                            else 0
                        )

                        edit_conta_cartao = st.selectbox(
                            "Conta / Cartão",
                            contas,
                            index=index_conta,
                            key=f"edit_conta_{row['id']}"
                        )
                    else:
                        edit_conta_cartao = None
                        st.warning("Cadastre conta/cartão em Configurações.")

                    edit_valor = st.number_input(
                        "Valor",
                        min_value=0.0,
                        step=100.0,
                        format="%.2f",
                        value=float(row["valor"]),
                        key=f"edit_valor_{row['id']}"
                    )

                    edit_data_vencimento = st.date_input(
                        "Data de vencimento",
                        value=row["data_vencimento"],
                        key=f"edit_vencimento_{row['id']}"
                    )

                    edit_pago = st.checkbox(
                        "Despesa paga?",
                        value=row["data_pagamento"] is not None,
                        key=f"edit_pago_{row['id']}"
                    )

                    edit_data_pagamento = None

                    if edit_pago:
                        edit_data_pagamento = st.date_input(
                            "Data de pagamento",
                            value=row["data_pagamento"] or row["data_vencimento"],
                            key=f"edit_pagamento_{row['id']}"
                        )

                    edit_recorrente = st.checkbox(
                        "Despesa recorrente?",
                        value=bool(row["recorrente"]),
                        key=f"edit_recorrente_{row['id']}"
                    )

                    salvar_edicao = st.form_submit_button("Salvar alterações")

                    if salvar_edicao:
                        if (
                            not edit_fornecedor
                            or not edit_descricao
                            or not edit_categoria
                            or not edit_conta_cartao
                            or edit_valor <= 0
                        ):
                            st.error("Preencha fornecedor, descrição, categoria, conta/cartão e valor corretamente.")
                        else:
                            edit_status = "pago" if edit_pago else "aberto"

                            execute_query(
                                """
                                UPDATE despesas
                                SET fornecedor = :fornecedor,
                                    descricao = :descricao,
                                    categoria = :categoria,
                                    conta_cartao = :conta_cartao,
                                    valor = :valor,
                                    data_vencimento = :data_vencimento,
                                    data_pagamento = :data_pagamento,
                                    status = :status,
                                    recorrente = :recorrente,
                                    atualizado_em = CURRENT_TIMESTAMP
                                WHERE id = :id
                                """,
                                {
                                    "id": row["id"],
                                    "fornecedor": edit_fornecedor.strip(),
                                    "descricao": edit_descricao.strip(),
                                    "categoria": edit_categoria,
                                    "conta_cartao": edit_conta_cartao,
                                    "valor": edit_valor,
                                    "data_vencimento": edit_data_vencimento,
                                    "data_pagamento": edit_data_pagamento,
                                    "status": edit_status,
                                    "recorrente": edit_recorrente,
                                }
                            )

                            st.success("Despesa atualizada com sucesso.")
                            st.rerun()

            st.divider()

            col_pay, col_delete = st.columns(2)

            with col_pay:
                if row["status"] != "pago":
                    if st.button("Marcar como pago", key=f"pay_{row['id']}"):
                        execute_query(
                            """
                            UPDATE despesas
                            SET data_pagamento = CURRENT_DATE,
                                status = 'pago',
                                atualizado_em = CURRENT_TIMESTAMP
                            WHERE id = :id
                            """,
                            {"id": row["id"]}
                        )
                        st.success("Despesa marcada como paga.")
                        st.rerun()

            with col_delete:
                if st.button("Excluir despesa", key=f"delete_despesa_{row['id']}"):
                    execute_query(
                        "DELETE FROM despesas WHERE id = :id",
                        {"id": row["id"]}
                    )
                    st.warning("Despesa excluída.")
                    st.rerun()