import streamlit as st
from database import execute_query, fetch_dataframe
from auth import proteger_pagina, logout
from theme import aplicar_design_portal, render_header, render_sidebar_brand

aplicar_design_portal()
proteger_pagina()
render_sidebar_brand()

st.sidebar.write(f"Usuário: {st.session_state['usuario_nome']}")

render_header(
    "Receitas",
    "Gestão de entradas financeiras"
)
logout("logout_receitas")

st.divider()

def carregar_categorias_receita():
    df = fetch_dataframe(
        """
        SELECT nome
        FROM categorias
        WHERE ativo = TRUE
          AND tipo IN ('receita', 'ambos')
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


categorias = carregar_categorias_receita()
contas = carregar_contas()

with st.expander("Nova receita", expanded=False):
    with st.form("form_receita"):
        cliente = st.text_input("Cliente")
        descricao = st.text_area("Descrição")

        if not categorias:
            st.warning("Cadastre ao menos uma categoria de receita em Configurações.")
            categoria = None
        else:
            categoria = st.selectbox("Categoria", categorias)

        valor = st.number_input("Valor", min_value=0.0, step=100.0, format="%.2f")
        data_vencimento = st.date_input("Data de vencimento")

        recebido = st.checkbox("Receita já recebida?")

        data_recebimento = None
        conta_recebimento = None

        if recebido:
            data_recebimento = st.date_input("Data de recebimento")

            if not contas:
                st.warning("Cadastre ao menos uma conta/cartão em Configurações.")
            else:
                conta_recebimento = st.selectbox("Conta de recebimento", contas)

        salvar = st.form_submit_button("Salvar receita")

        if salvar:
            if not cliente or not descricao or not categoria or valor <= 0:
                st.error("Preencha cliente, descrição, categoria e valor corretamente.")
            elif recebido and not conta_recebimento:
                st.error("Informe a conta de recebimento.")
            else:
                status = "recebido" if recebido else "previsto"

                execute_query(
                    """
                    INSERT INTO receitas (
                        cliente,
                        descricao,
                        categoria,
                        valor,
                        data_vencimento,
                        data_recebimento,
                        conta_recebimento,
                        status
                    )
                    VALUES (
                        :cliente,
                        :descricao,
                        :categoria,
                        :valor,
                        :data_vencimento,
                        :data_recebimento,
                        :conta_recebimento,
                        :status
                    )
                    """,
                    {
                        "cliente": cliente.strip(),
                        "descricao": descricao.strip(),
                        "categoria": categoria,
                        "valor": valor,
                        "data_vencimento": data_vencimento,
                        "data_recebimento": data_recebimento,
                        "conta_recebimento": conta_recebimento,
                        "status": status,
                    }
                )

                st.success("Receita cadastrada com sucesso.")
                st.rerun()

st.divider()
st.subheader("Receitas cadastradas")

df = fetch_dataframe(
    """
    SELECT
        id,
        cliente,
        descricao,
        categoria,
        valor,
        data_vencimento,
        data_recebimento,
        conta_recebimento,
        CASE
            WHEN data_recebimento IS NOT NULL THEN 'recebido'
            WHEN data_vencimento < CURRENT_DATE THEN 'atrasado'
            ELSE 'previsto'
        END AS status
    FROM receitas
    ORDER BY data_vencimento DESC
    """
)

if df.empty:
    st.info("Nenhuma receita cadastrada ainda.")
else:
    for _, row in df.iterrows():
        with st.expander(
            f"{row['cliente']} | R$ {row['valor']:,.2f} | {row['status']}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"Cliente: {row['cliente']}")
                st.write(f"Descrição: {row['descricao']}")
                st.write(f"Categoria: {row['categoria']}")
                st.write(f"Valor: R$ {row['valor']:,.2f}")

            with col2:
                st.write(f"Vencimento: {row['data_vencimento']}")
                st.write(f"Recebimento: {row['data_recebimento']}")
                st.write(f"Conta recebimento: {row['conta_recebimento']}")
                st.write(f"Status: {row['status']}")

            st.divider()

            with st.expander("Editar receita", expanded=False):
                with st.form(f"form_editar_receita_{row['id']}"):
                    edit_cliente = st.text_input(
                        "Cliente",
                        value=row["cliente"],
                        key=f"edit_cliente_{row['id']}"
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

                    edit_recebido = st.checkbox(
                        "Receita recebida?",
                        value=row["data_recebimento"] is not None,
                        key=f"edit_recebido_{row['id']}"
                    )

                    edit_data_recebimento = None
                    edit_conta_recebimento = None

                    if edit_recebido:
                        edit_data_recebimento = st.date_input(
                            "Data de recebimento",
                            value=row["data_recebimento"] or row["data_vencimento"],
                            key=f"edit_recebimento_{row['id']}"
                        )

                        conta_atual = row["conta_recebimento"]

                        if contas:
                            index_conta = (
                                contas.index(conta_atual)
                                if conta_atual in contas
                                else 0
                            )

                            edit_conta_recebimento = st.selectbox(
                                "Conta de recebimento",
                                contas,
                                index=index_conta,
                                key=f"edit_conta_{row['id']}"
                            )
                        else:
                            st.warning("Cadastre conta/cartão em Configurações.")
                    else:
                        edit_data_recebimento = None
                        edit_conta_recebimento = None

                    salvar_edicao = st.form_submit_button("Salvar alterações")

                    if salvar_edicao:
                        if not edit_cliente or not edit_descricao or not edit_categoria or edit_valor <= 0:
                            st.error("Preencha cliente, descrição, categoria e valor corretamente.")
                        elif edit_recebido and not edit_conta_recebimento:
                            st.error("Informe a conta de recebimento.")
                        else:
                            edit_status = "recebido" if edit_recebido else "previsto"

                            execute_query(
                                """
                                UPDATE receitas
                                SET cliente = :cliente,
                                    descricao = :descricao,
                                    categoria = :categoria,
                                    valor = :valor,
                                    data_vencimento = :data_vencimento,
                                    data_recebimento = :data_recebimento,
                                    conta_recebimento = :conta_recebimento,
                                    status = :status,
                                    atualizado_em = CURRENT_TIMESTAMP
                                WHERE id = :id
                                """,
                                {
                                    "id": row["id"],
                                    "cliente": edit_cliente.strip(),
                                    "descricao": edit_descricao.strip(),
                                    "categoria": edit_categoria,
                                    "valor": edit_valor,
                                    "data_vencimento": edit_data_vencimento,
                                    "data_recebimento": edit_data_recebimento,
                                    "conta_recebimento": edit_conta_recebimento,
                                    "status": edit_status,
                                }
                            )

                            st.success("Receita atualizada com sucesso.")
                            st.rerun()

            st.divider()

            col_receber, col_delete = st.columns(2)

            with col_receber:
                if row["status"] != "recebido":
                    if contas:
                        conta_baixa = st.selectbox(
                            "Conta de recebimento para baixa",
                            contas,
                            key=f"conta_recebimento_baixa_{row['id']}"
                        )

                        if st.button("Marcar como recebido", key=f"btn_receber_{row['id']}"):
                            execute_query(
                                """
                                UPDATE receitas
                                SET data_recebimento = CURRENT_DATE,
                                    conta_recebimento = :conta_recebimento,
                                    status = 'recebido',
                                    atualizado_em = CURRENT_TIMESTAMP
                                WHERE id = :id
                                """,
                                {
                                    "id": row["id"],
                                    "conta_recebimento": conta_baixa,
                                }
                            )
                            st.success("Receita marcada como recebida.")
                            st.rerun()
                    else:
                        st.warning("Cadastre uma conta/cartão antes de marcar como recebido.")

            with col_delete:
                if st.button("Excluir receita", key=f"delete_receita_{row['id']}"):
                    execute_query(
                        "DELETE FROM receitas WHERE id = :id",
                        {"id": row["id"]}
                    )
                    st.warning("Receita excluída.")
                    st.rerun()