import streamlit as st
from deep_translator import GoogleTranslator

# 1. App configuratie
st.set_page_config(page_title="WandrWays", page_icon="🎒", layout="centered")

# 2. Titel en Styling
st.title("🎒 WandrWays")
st.subheader("Jouw ultieme reispartner")

# 3. Initialiseer de opslag (session_state)
if 'landen' not in st.session_state: st.session_state.landen = []
if 'dagboek' not in st.session_state: st.session_state.dagboek = []
if 'inpaklijst' not in st.session_state: st.session_state.inpaklijst = []

# 4. DEFINIEER DE TABS (Hier ging het mis: we maken er exact 5 aan)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🈯 Vertaler", 
    "📋 Inpaklijst", 
    "🗺️ Landen Tracker", 
    "✍️ Dagboek", 
    "💡 Tips & Tricks"
])

# --- TAB 1: VERTALER ---
with tab1:
    st.header("🈯 Wereldvertaler")
    st.write("Vertaal naar bijna elke taal ter wereld.")

    # Haal automatisch alle ondersteunde talen op
    try:
        ondersteunde_talen = GoogleTranslator().get_supported_languages(as_dict=True)
        # We draaien de dictionary om voor de selectbox: "Nederlands": "nl"
        talen_weergave = {naam.capitalize(): code for naam, code in ondersteunde_talen.items()}
    except:
        # Fallback als er geen internet is
        talen_weergave = {"Engels": "en", "Spaans": "es", "Frans": "fr", "Duits": "de"}

    zin = st.text_area("Wat wil je vertalen?", placeholder="Typ hier je tekst...", key="vertaal_area")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        doeltaal_naam = st.selectbox("Naar welke taal?", sorted(talen_weergave.keys()))
    with col2:
        st.write(" ") # Voor uitlijning
        st.write(" ") 
        vertaal_knop = st.button("Vertaal nu 🚀")

    if vertaal_knop:
        if zin:
            with st.spinner('Vertalen...'):
                try:
                    code = talen_weergave[doeltaal_naam]
                    vertaling = GoogleTranslator(source='auto', target=code).translate(zin)
                    
                    st.success(f"**Vertaling naar het {doeltaal_naam}:**")
                    st.info(vertaling)
                    
                    # Knop om de vertaling naar het klembord te kopiëren (in browser)
                    st.button("Kopieer tekst", on_click=lambda: st.write("Tip: Houd de tekst ingedrukt om te kopiëren op je telefoon!"))
                except Exception as e:
                    st.error(f"Oeps, er ging iets mis: {e}")
        else:
            st.warning("Voer eerst een tekst in.")
# --- TAB 2: INPAKLIJST ---
with tab2:
    st.header("Wat moet er mee?")
    nieuw_item = st.text_input("Voeg iets toe aan je lijst", key="inpak_in")
    if st.button("Toevoegen aan lijst"):
        if nieuw_item:
            st.session_state.inpaklijst.append(nieuw_item)
    
    for i, spul in enumerate(st.session_state.inpaklijst):
        st.checkbox(spul, key=f"check_{i}")

# --- TAB 3: LANDEN TRACKER ---
import pandas as pd
from geopy.geocoders import Nominatim

# We maken een 'geocoder' aan om locaties te vinden
geolocator = Nominatim(user_agent="wandrways_app")

with tab3:
    st.header("🗺️ Jouw Wereldkaart")
    
    # Initialiseer de lijst voor coördinaten als die nog niet bestaat
    if 'coords_list' not in st.session_state:
        st.session_state.coords_list = []

    with st.form(key='map_form', clear_on_submit=True):
        plek_naam = st.text_input("Voeg een land of stad toe aan de kaart:")
        submit_plek = st.form_submit_button("Pin plaatsen 📍")

        if submit_plek and plek_naam:
            try:
                # Zoek de coördinaten op
                location = geolocator.geocode(plek_naam)
                if location:
                    # Sla de coördinaten op in een lijstje
                    st.session_state.coords_list.append({
                        "name": plek_naam,
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    })
                    st.toast(f"Pin geplaatst op {plek_naam}!")
                else:
                    st.error("Locatie niet gevonden. Probeer een andere naam.")
            except Exception as e:
                st.error("Er is een verbindingsfout. Probeer het later opnieuw.")

    # Als er pins zijn, toon dan de kaart
    if st.session_state.coords_list:
        # Maak een tabel (DataFrame) van de coördinaten
        df = pd.DataFrame(st.session_state.coords_list)
        
        # Toon de interactieve kaart
        st.map(df, latitude="latitude", longitude="longitude", zoom=1)
        
        st.write(f"Je hebt al **{len(st.session_state.coords_list)}** unieke plekken ontdekt!")
    else:
        st.info("Typ hierboven een land of stad om je eerste pin te zetten!")
# --- TAB 4: DAGBOEKJE ---
with tab4:
    st.header("Mijn Herinneringen")
    st.write("Leg je avonturen vast met tekst en beeld.")

    with st.form(key='dagboek_foto_form', clear_on_submit=True):
        datum_keuze = st.date_input("Datum van je avontuur")
        verhaal_tekst = st.text_area("Hoe was je dag?", height=100)
        
        # NIEUW: Foto uploader functie
        geuploade_foto = st.file_uploader("Voeg een foto toe aan je herinnering", type=['png', 'jpg', 'jpeg'])
        
        submit_dagboek = st.form_submit_button("Herinnering met foto opslaan 📸")

        if submit_dagboek:
            if verhaal_tekst or geuploade_foto:
                # We slaan de foto (indien aanwezig) op in de sessie
                foto_data = geuploade_foto.read() if geuploade_foto is not None else None
                
                nieuwe_entry = {
                    "datum": datum_keuze, 
                    "tekst": verhaal_tekst,
                    "foto": foto_data
                }
                st.session_state.dagboek.append(nieuwe_entry)
                st.toast("Je avontuur is opgeslagen!")
            else:
                st.warning("Voeg tekst of een foto toe.")

    st.divider()
    
    # Weergave van de opgeslagen verhalen
    if st.session_state.dagboek:
        for entry in reversed(st.session_state.dagboek):
            with st.expander(f"📖 {entry['datum']}"):
                # Als er een foto is, toon deze
                if entry['foto']:
                    st.image(entry['foto'], use_container_width=True)
                
                if entry['tekst']:
                    st.write(entry['tekst'])
    else:
        st.info("Je dagboek is nog leeg.")
# --- TAB 5: TIPS & TRICKS ---
with tab5:
    st.header("WandrWays Reisadvies")
    st.write("De gouden regels voor een zorgeloze start van je reis:")

    # Jouw specifieke tips in een mooie layout
    st.info("1. **Check je lijstje 3x voor vertrek.** 📝")
    st.info("2. **Check je tassen en/of koffers goed na.** 🧳")
    st.info("3. **Leg je paspoort/ID-kaart op een plek waar je het ziet liggen wanneer je vertrekt.** 🛂")

    st.divider()
    
    # Extra tip sectie voor inspiratie
    st.subheader("Extra WandrWays Inspiratie")
    st.write("💡 *Tip: Maak ook altijd even een foto van je belangrijke documenten als backup op je telefoon.*")