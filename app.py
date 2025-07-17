import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.title("Distanzrechner: Kundenadresse vs. Parkposition")

uploaded_file = st.file_uploader("Excel-Datei hochladen", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    geolocator = Nominatim(user_agent="geo-app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    def get_coordinates(address):
        try:
            location = geocode(address)
            if location:
                return pd.Series([location.latitude, location.longitude])
        except:
            pass
        return pd.Series([None, None])

    df[["Liefer_Lat", "Liefer_Lon"]] = df["Lieferadresse"].apply(get_coordinates)
    df = df.drop(columns=["Lieferadresse"])

    st.success("Fertig! Hier ist deine Tabelle:")
    st.dataframe(df)

    st.download_button(
        label="Ergebnis als Excel herunterladen",
        data=df.to_excel(index=False),
        file_name="ergebnis_geokoordinaten.xlsx"
    )
