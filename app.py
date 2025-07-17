import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic

st.title("Distanzrechner: Kundenadresse vs. Parkposition")

uploaded_file = st.file_uploader("Excel-Datei hochladen", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    if not all(col in df.columns for col in ["Kunden-ID", "Adresse", "Latitude", "Longitude"]):
        st.error("Die Datei muss die Spalten: Kunden-ID, Adresse, Latitude, Longitude enthalten.")
    else:
        geolocator = Nominatim(user_agent="geo-app")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        def get_coords(adresse):
            try:
                location = geocode(adresse)
                if location:
                    return pd.Series([location.latitude, location.longitude])
            except:
                pass
            return pd.Series([None, None])

        st.info("Adressen werden in Koordinaten umgerechnet...")

        df[["Ziel_Lat", "Ziel_Lon"]] = df["Adresse"].apply(get_coords)

        def berechne_entfernung(row):
            try:
                p1 = (row["Latitude"], row["Longitude"])
                p2 = (row["Ziel_Lat"], row["Ziel_Lon"])
                return geodesic(p1, p2).meters
            except:
                return None

        df["Entfernung (m)"] = df.apply(berechne_entfernung, axis=1).round(1)

        # Adresse aus Datenschutz entfernen
        df = df.drop(columns=["Adresse"])

        st.success("Fertig! Hier ist deine Tabelle:")

        st.dataframe(df)

        # Datei zum Download anbieten
        st.download_button(
            label="Ergebnis als Excel herunterladen",
            data=df.to_excel(index=False),
            file_name="distanz_ergebnis.xlsx"
        )
