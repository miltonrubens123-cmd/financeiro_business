import base64
from pathlib import Path
import streamlit as st


BASE_DIR = Path(__file__).parent

LOGO_CANDIDATES = [
    BASE_DIR / "imagens" / "logo.png",
    BASE_DIR / "imagens" / "Logo.png",
    BASE_DIR / "logo.png",
    BASE_DIR / "Logo.png",
]


def carregar_logo_base64():
    logo_path = next((p for p in LOGO_CANDIDATES if p.exists()), None)

    if not logo_path:
        return None

    try:
        return base64.b64encode(logo_path.read_bytes()).decode()
    except Exception:
        return None


def aplicar_estilo_login():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #061C33 0%, #0B3A63 100%);
        }

        section[data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .stTextInput label {
            color: #dfeaf5 !important;
            font-weight: 600 !important;
        }

        .stTextInput > div > div > input {
            background-color: rgba(255,255,255,0.06) !important;
            color: white !important;
            border: 1px solid rgba(173, 216, 255, 0.22) !important;
            border-radius: 10px !important;
        }

        .stButton > button {
            width: 100%;
            border-radius: 12px;
            font-weight: 700;
            background: linear-gradient(180deg, #17427A 0%, #10335F 100%);
            color: #FFFFFF;
            border: 1px solid rgba(120,166,255,0.20);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def aplicar_design_portal():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #020b16 0%, #04111f 100%);
            color: #EAF2FF;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            max-width: 1380px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #03101d 0%, #051424 100%);
            border-right: 1px solid rgba(120,145,170,0.12);
        }

        section[data-testid="stSidebar"] * {
            color: #EAF2FF !important;
        }

        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stSelectbox > div > div,
        .stNumberInput input,
        .stDateInput input {
            background: rgba(255,255,255,0.03) !important;
            color: #EAF2FF !important;
            border: 1px solid rgba(120,145,170,0.18) !important;
            border-radius: 10px !important;
            box-shadow: none !important;
        }

        .stMetric {
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(120,145,170,0.16);
            border-radius: 14px;
            padding: 16px;
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
            border: 1px solid rgba(84,138,226,0.28);
            background: linear-gradient(180deg, #17427A 0%, #10335F 100%);
            color: #FFFFFF;
            box-shadow: none;
        }

        .stDownloadButton > button {
            border-radius: 12px;
            font-weight: 700;
            border: 1px solid rgba(84,138,226,0.28);
            background: linear-gradient(180deg, #17427A 0%, #10335F 100%);
            color: #FFFFFF;
        }

        .stDataFrame {
            border-radius: 14px;
            overflow: hidden;
        }

        .stAlert {
            border-radius: 12px;
        }

        h1, h2, h3 {
            color: #F7FBFF !important;
            letter-spacing: -0.02em;
        }

        p, span, label {
            color: #EAF2FF;
        }

        .bv-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 4px;
        }

        .bv-header-logo {
            max-width: 72px;
            max-height: 72px;
        }

        .bv-header-title {
            font-size: 34px;
            font-weight: 800;
            color: #F7FBFF;
            margin: 0;
            line-height: 1.1;
        }

        .bv-header-subtitle {
            color: #9FB4CA;
            font-size: 14px;
            margin-top: 4px;
        }

        .bv-divider {
            height: 1px;
            background: rgba(120,145,170,0.14);
            margin: 18px 0 24px 0;
        }

        .bv-sidebar-title {
            font-size: 16px;
            font-weight: 700;
            color: #F7FBFF;
            line-height: 1.2;
        }

        .bv-sidebar-logo {
            width: 34px;
            height: 34px;
            object-fit: contain;
        }

        .bv-sidebar-top {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 4px 0 18px 0;
        }

        .bv-user-card {
            border-top: 1px solid rgba(120,145,170,0.16);
            padding-top: 16px;
            margin-top: 20px;
        }

        .bv-user-label {
            font-size: 12px;
            color: #8FA5BC;
        }

        .bv-user-name {
            font-size: 15px;
            font-weight: 700;
            color: #EAF2FF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(titulo: str, subtitulo: str = ""):
    logo_b64 = carregar_logo_base64()

    if logo_b64:
        st.markdown(
            f"""
            <div class="bv-header">
                <img class="bv-header-logo" src="data:image/png;base64,{logo_b64}">
                <div>
                    <div class="bv-header-title">{titulo}</div>
                    <div class="bv-header-subtitle">{subtitulo}</div>
                </div>
            </div>
            <div class="bv-divider"></div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div>
                <div class="bv-header-title">{titulo}</div>
                <div class="bv-header-subtitle">{subtitulo}</div>
            </div>
            <div class="bv-divider"></div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_brand():
    logo_b64 = carregar_logo_base64()

    if logo_b64:
        st.sidebar.markdown(
            f"""
            <div class="bv-sidebar-top">
                <img class="bv-sidebar-logo" src="data:image/png;base64,{logo_b64}">
                <div class="bv-sidebar-title">Financeiro<br>Business Vision</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            """
            <div class="bv-sidebar-top">
                <div class="bv-sidebar-title">Financeiro<br>Business Vision</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data):
    return data.strftime("%d/%m/%Y") if data else "-"


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

    return mapa.get(str(status).lower(), str(status).upper())