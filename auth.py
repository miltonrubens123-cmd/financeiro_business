import bcrypt
import streamlit as st
from database import fetch_dataframe
from theme import aplicar_estilo_login, carregar_logo_base64


def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(
        senha_digitada.encode("utf-8"),
        senha_hash.encode("utf-8")
    )


def login():
    aplicar_estilo_login()

    logo_b64 = carregar_logo_base64()

    col1, col2, col3 = st.columns([1.2, 1, 1.2])

    with col2:
        if logo_b64:
            st.markdown(
                f"""
                <div style="display:flex; justify-content:center; margin-bottom:18px;">
                    <img src="data:image/png;base64,{logo_b64}" width="140">
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="text-align:center; color:white; font-size:26px; font-weight:800;">
                FINANCEIRO BUSINESS VISION
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="text-align:center; color:#c7d7e6; font-size:15px; margin-top:5px;">
                Gestão financeira interna
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="text-align:center; color:#c7d7e6; font-size:13px; margin-bottom:22px;">
                Acesse sua conta
            </div>
            """,
            unsafe_allow_html=True,
        )

        email = st.text_input("E-mail", placeholder="Digite seu e-mail")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

        if st.button("ENTRAR →"):
            email_digitado = email.strip()
            senha_digitada = senha.strip()

            if not email_digitado or not senha_digitada:
                st.error("Informe e-mail e senha.")
                return False

            usuario = fetch_dataframe(
                """
                SELECT id, nome, email, senha_hash, perfil, ativo
                FROM usuarios
                WHERE email = :email
                LIMIT 1
                """,
                {"email": email_digitado}
            )

            if usuario.empty:
                st.error("Usuário ou senha inválidos.")
                return False

            user = usuario.iloc[0]

            if not user["ativo"]:
                st.error("Usuário inativo.")
                return False

            if verificar_senha(senha_digitada, user["senha_hash"]):
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


def logout(key="logout_button"):
    if st.sidebar.button("Sair", use_container_width=True, key=key):
        st.session_state.clear()
        st.rerun()