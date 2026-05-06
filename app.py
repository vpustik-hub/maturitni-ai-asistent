import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="AI Maturant", page_icon="🎓", layout="wide")

# --- KONFIGURACE AI (KLÍČ) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("Chybí API klíč! Vlož ho do Streamlit Secrets jako GOOGLE_API_KEY.")
    st.stop()

# --- PAMĚŤ APLIKACE ---
if "knihovna" not in st.session_state:
    st.session_state.knihovna = {}

# --- FUNKCE PRO ZPRACOVÁNÍ TEXTU ---
def zpracuj_text_pomoci_ai(raw_text):
    prompt = f"""
    Jsi expert na tvorbu studijních materiálů. Tvým úkolem je vzít syrový text z PDF a přeformátovat ho.
    Hledej hlavní maturitní otázky a jejich podbody (odrážky).
    Výstup vrať v Markdown formátu (nadpisy pomocí ##, podbody pomocí - ).
    Text k analýze:
    {raw_text[:8000]}
    """
    response = model.generate_content(prompt)
    return response.text

# --- UI - BOČNÍ PANEL ---
with st.sidebar:
    st.title("📂 Nahrávání")
    nazev_predmetu = st.text_input("Název předmětu (např. Čeština)")
    soubor = st.file_uploader("Nahraj PDF s otázkami", type="pdf")
    
    if st.button("Uložit do aplikace") and soubor and nazev_predmetu:
        with st.spinner("AI analyzuje strukturu a odrážky..."):
            reader = PdfReader(soubor)
            text_z_pdf = ""
            for page in reader.pages:
                text_z_pdf += page.extract_text()
            
            struktura = zpracuj_text_pomoci_ai(text_z_pdf)
            st.session_state.knihovna[nazev_predmetu] = struktura
            st.success(f"Předmět '{nazev_predmetu}' je připraven!")

# --- HLAVNÍ PLOCHA ---
st.title("🧠 Tvůj maturitní asistent")

if not st.session_state.knihovna:
    st.info("Vlevo nahraj své první PDF a zadej název předmětu.")
else:
    vyber = st.selectbox("Vyber si předmět:", list(st.session_state.knihovna.keys()))
    
    tab1, tab2, tab3 = st.tabs(["📖 Studium (Struktura)", "📝 AI Testování", "🎙️ Podcast"])
    
    with tab1:
        st.markdown(st.session_state.knihovna[vyber])
        
    with tab2:
        st.subheader("Rychlý test")
        if st.button("Vygenerovat test na míru"):
            with st.spinner("Vymýšlím otázky..."):
                test_prompt = f"Na základě tohoto textu vytvoř krátký test (5 otázek) s výběrem odpovědí A, B, C a na konci uveď správné řešení: {st.session_state.knihovna[vyber]}"
                odpoved = model.generate_content(test_prompt)
                st.write(odpoved.text)
                
    with tab3:
        st.subheader("AI Podcast / Video skript")
        if st.button("Vytvořit scénář k poslechu"):
            with st.spinner("Píšu scénář..."):
                script_prompt = f"Vytvoř scénář pro krátký vzdělávací podcast (cca 2 minuty), kde moderátor vysvětluje hlavní body tohoto tématu: {st.session_state.knihovna[vyber]}. Mluv lidsky a srozumitelně."
                odpoved = model.generate_content(script_prompt)
                st.write(odpoved.text)
