import streamlit as st
from database import execute_query, fetch_dataframe
from auth import proteger_pagina, logout
from theme import aplicar_design_portal, render_header, render_sidebar_brand

aplicar_design_portal()
proteger_pagina()
render_sidebar_brand()

st.sidebar.write(f"Usuário: {st.session_state['usuario_nome']}")
render_header(
    "Configurações",
    "Cadastros auxiliares para padronizar categorias, contas e cartões."
)
logout("logout_configuracoes")

st.divider()


col1, col2 = st.columns(2)

with col1:
    st.subheader("Categorias")

    with st.expander("Nova categoria", expanded=False):
        with st.form("form_categoria"):
            nome = st.text_input("Nome da categoria")
            tipo = st.selectbox("Tipo", ["receita", "despesa", "ambos"])

            salvar = st.form_submit_button("Salvar categoria")

            if salvar:
                if not nome:
                    st.error("Informe o nome da categoria.")
                else:
                    execute_query(
                        """
                        INSERT INTO categorias (nome, tipo, ativo)
                        VALUES (:nome, :tipo, TRUE)
                        ON CONFLICT (nome) DO UPDATE
                        SET tipo = EXCLUDED.tipo,
                            ativo = TRUE
                        """,
                        {"nome": nome.strip(), "tipo": tipo}
                    )
                    st.success("Categoria salva com sucesso.")
                    st.rerun()

    categorias = fetch_dataframe(
        """
        SELECT id, nome, tipo, ativo
        FROM categorias
        ORDER BY nome
        """
    )

    if categorias.empty:
        st.info("Nenhuma categoria cadastrada.")
    else:
        for _, row in categorias.iterrows():
            with st.expander(f"{row['nome']} | {row['tipo']}"):
                st.write(f"Ativo: {'Sim' if row['ativo'] else 'Não'}")

                if row["ativo"]:
                    if st.button("Inativar", key=f"inativar_cat_{row['id']}"):
                        execute_query(
                            "UPDATE categorias SET ativo = FALSE WHERE id = :id",
                            {"id": row["id"]}
                        )
                        st.rerun()
                else:
                    if st.button("Reativar", key=f"reativar_cat_{row['id']}"):
                        execute_query(
                            "UPDATE categorias SET ativo = TRUE WHERE id = :id",
                            {"id": row["id"]}
                        )
                        st.rerun()

with col2:
    st.subheader("Contas / Cartões")

    with st.expander("Nova conta/cartão", expanded=False):
        with st.form("form_conta_cartao"):
            nome = st.text_input("Nome da conta/cartão")
            tipo = st.selectbox(
                "Tipo",
                ["conta corrente", "cartão crédito", "cartão débito", "dinheiro", "outro"]
            )

            salvar = st.form_submit_button("Salvar conta/cartão")

            if salvar:
                if not nome:
                    st.error("Informe o nome da conta/cartão.")
                else:
                    execute_query(
                        """
                        INSERT INTO contas_cartoes (nome, tipo, ativo)
                        VALUES (:nome, :tipo, TRUE)
                        ON CONFLICT (nome) DO UPDATE
                        SET tipo = EXCLUDED.tipo,
                            ativo = TRUE
                        """,
                        {"nome": nome.strip(), "tipo": tipo}
                    )
                    st.success("Conta/cartão salvo com sucesso.")
                    st.rerun()

    contas = fetch_dataframe(
        """
        SELECT id, nome, tipo, ativo
        FROM contas_cartoes
        ORDER BY nome
        """
    )

    if contas.empty:
        st.info("Nenhuma conta/cartão cadastrada.")
    else:
        for _, row in contas.iterrows():
            with st.expander(f"{row['nome']} | {row['tipo']}"):
                st.write(f"Ativo: {'Sim' if row['ativo'] else 'Não'}")

                if row["ativo"]:
                    if st.button("Inativar", key=f"inativar_conta_{row['id']}"):
                        execute_query(
                            "UPDATE contas_cartoes SET ativo = FALSE WHERE id = :id",
                            {"id": row["id"]}
                        )
                        st.rerun()
                else:
                    if st.button("Reativar", key=f"reativar_conta_{row['id']}"):
                        execute_query(
                            "UPDATE contas_cartoes SET ativo = TRUE WHERE id = :id",
                            {"id": row["id"]}
                        )
                        st.rerun()