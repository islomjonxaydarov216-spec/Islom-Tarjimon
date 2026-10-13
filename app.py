
import streamlit as st
import requests
import html
import time

st.set_page_config(
    page_title="ISLOM TARJIMON",
    page_icon="📚",
    layout="centered"
)

st.title("📚 ISLOM TARJIMON")
st.caption("Matnlarni 15 ta tilga tarjima qilish")

TILLAR = {
    "O‘zbek": "uz",
    "Ingliz": "en",
    "Rus": "ru",
    "Turk": "tr",
    "Arab": "ar",
    "Nemis": "de",
    "Fransuz": "fr",
    "Ispan": "es",
    "Xitoy": "zh-CN",
    "Koreys": "ko",
    "Yapon": "ja",
    "Italyan": "it",
    "Qozoq": "kk",
    "Qirg‘iz": "ky",
    "Tojik": "tg"
}

def matnni_bol(matn, limit=450):
    sozlar = matn.split()
    bolaklar = []
    joriy = ""

    for soz in sozlar:
        if len(soz) > limit:
            if joriy:
                bolaklar.append(joriy)
                joriy = ""
            for i in range(0, len(soz), limit):
                bolaklar.append(soz[i:i + limit])
        elif len(joriy) + len(soz) + 1 <= limit:
            joriy = (joriy + " " + soz).strip()
        else:
            bolaklar.append(joriy)
            joriy = soz

    if joriy:
        bolaklar.append(joriy)

    return bolaklar

def tarjima_qil(matn, manba_kod, maqsad_kod):
    bolaklar = matnni_bol(matn)
    natijalar = []

    sessiya = requests.Session()
    sessiya.headers.update({
        "User-Agent": "ISLOM-TARJIMON/1.0"
    })

    for i, bolak in enumerate(bolaklar):
        muvaffaqiyat = False

        for urinish in range(3):
            try:
                javob = sessiya.get(
                    "https://api.mymemory.translated.net/get",
                    params={
                        "q": bolak,
                        "langpair": f"{manba_kod}|{maqsad_kod}"
                    },
                    timeout=25
                )

                if javob.status_code == 429:
                    time.sleep(2 + urinish * 3)
                    continue

                javob.raise_for_status()
                data = javob.json()

                if data.get("responseStatus") not in (None, 200, "200"):
                    xabar = data.get("responseDetails", "Tarjima xizmati xatoligi")
                    raise RuntimeError(str(xabar))

                tarjima = data.get("responseData", {}).get(
                    "translatedText", ""
                )

                if not tarjima:
                    raise RuntimeError("Tarjima natijasi bo‘sh.")

                natijalar.append(html.unescape(tarjima))
                muvaffaqiyat = True
                break

            except requests.RequestException:
                if urinish < 2:
                    time.sleep(2 + urinish * 2)
            except (ValueError, TypeError):
                if urinish < 2:
                    time.sleep(2)

        if not muvaffaqiyat:
            raise RuntimeError(
                f"{i + 1}-bo‘lak tarjima qilinmadi. "
                "Birozdan keyin qayta urinib ko‘ring."
            )

        if i < len(bolaklar) - 1:
            time.sleep(1)

    return "\n".join(natijalar)

col1, col2 = st.columns(2)

with col1:
    manba = st.selectbox(
        "Matn qaysi tilda?",
        list(TILLAR.keys()),
        index=0
    )

with col2:
    maqsad = st.selectbox(
        "Qaysi tilga tarjima qilinsin?",
        list(TILLAR.keys()),
        index=1
    )

matn = st.text_area(
    "Tarjima qilinadigan matn:",
    height=230,
    placeholder="Matningizni shu yerga yozing yoki joylashtiring..."
)

if st.button("🌐 TARJIMA QILISH", type="primary", use_container_width=True):
    if not matn.strip():
        st.warning("Avval tarjima qilinadigan matnni kiriting.")
    elif manba == maqsad:
        st.warning("Manba tili va tarjima tili har xil bo‘lishi kerak.")
    else:
        try:
            with st.spinner("Matn tarjima qilinmoqda. Kuting..."):
                natija = tarjima_qil(
                    matn.strip(),
                    TILLAR[manba],
                    TILLAR[maqsad]
                )

            st.success("Tarjima tayyor!")
            st.text_area(
                "Tarjima natijasi:",
                value=natija,
                height=250
            )
            st.download_button(
                "⬇️ Tarjimani TXT fayl qilib saqlash",
                data=natija,
                file_name="tarjima.txt",
                mime="text/plain"
            )

        except RuntimeError as e:
            st.error(str(e))
        except Exception:
            st.error(
                "Tarjima vaqtida xatolik yuz berdi. "
                "Internetni tekshirib, qayta urinib ko‘ring."
            )

st.divider()
st.caption(
    "ISLOM TARJIMON • Bepul tarjima xizmati internet talab qiladi. "
    "Xizmatda cheklovlar bo‘lishi mumkin."
)
