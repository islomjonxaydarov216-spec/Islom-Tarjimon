import streamlit as st
import requests

st.set_page_config(
    page_title="ISLOM TARJIMON",
    page_icon="📚",
    layout="centered"
)

st.title("📚 ISLOM TARJIMON")
st.write("Matnni 6 ta tilga tarjima qilish")

TILLAR = {
    "O‘zbek": "uz",
    "Ingliz": "en",
    "Rus": "ru",
    "Turk": "tr",
    "Arab": "ar",
    "Nemis": "de"
}

manba = st.selectbox("Matn qaysi tilda?", list(TILLAR.keys()), index=0)
maqsad = st.selectbox("Qaysi tilga tarjima qilinsin?", list(TILLAR.keys()), index=1)

matn = st.text_area("Tarjima qilinadigan matnni kiriting:", height=200)

if st.button("🌐 TARJIMA QILISH", type="primary"):
    if not matn.strip():
        st.warning("Iltimos, avval matn kiriting.")
    elif manba == maqsad:
        st.warning("Iltimos, boshqa tarjima tilini tanlang.")
    else:
        try:
            javob = requests.get(
                "https://api.mymemory.translated.net/get",
                params={
                    "q": matn[:500],
                    "langpair": f"{TILLAR[manba]}|{TILLAR[maqsad]}"
                },
                timeout=20
            )
            javob.raise_for_status()
            natija = javob.json()
            tarjima = natija.get("responseData", {}).get("translatedText", "")

            if tarjima:
                st.subheader("Tarjima natijasi")
                st.text_area("Tayyor tarjima:", value=tarjima, height=200)
            else:
                st.error("Tarjima topilmadi. Birozdan keyin qayta urinib ko‘ring.")
        except requests.RequestException:
            st.error("Internet yoki tarjima xizmati bilan bog‘lanishda xatolik.")
        except (ValueError, TypeError):
            st.error("Tarjima xizmatidan noto‘g‘ri javob keldi.")
