import bcrypt
import streamlit as st
from database import fetch_dataframe


def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(
        senha_digitada.encode("utf-8"),
        senha_hash.encode("utf-8")
    )


def login():
    st.title("Financeiro Business Vision")
    st.markdown("Acesso restrito")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        usuario = fetch_dataframe(
            """
            SELECT id, nome, email, senha_hash, perfil, ativo
            FROM usuarios
            WHERE email = :email
            LIMIT 1
            """,
            {"email": email}
        )

        if usuario.empty:
            st.error("Usuário ou senha inválidos.")
            return False

        user = usuario.iloc[0]

        if not user["ativo"]:
            st.error("Usuário inativo.")
            return False

        if verificar_senha(senha, user["senha_hash"]):
            st.session_state["logado"] = True
            st.session_state["usuario_id"] = int(user["id"])
            st.session_state["usuario_nome"] = user["nome"]
            st.session_state["usuario_email"] = user["email"]
            st.session_state["usuario_perfil"] = user["perfil"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    return False


def proteger_pagina():
    if "logado" not in st.session_state or not st.session_state["logado"]:
        login()
        st.stop()


def logout():
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()