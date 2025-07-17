import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic

st.title("Distanzrechner: Kundenadresse vs. Parkposition")

uploaded_file = st.file_uploader("Excel-Datei hochladen", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Prüfen, ob alle nötigen Spalten da sind
    required_cols = ["Kunden-ID", "Geo-Lat", "Geo-Lon", "Lieferadresse"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"Die Datei muss folgende Spalten enthalten: {', '.join(required_cols)}")
    else:
        # Geocoder initialisieren
        geolocator = Nominatim(user_agent="geo-app")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        # Adresse in Koordinaten umwandeln
        def get_coords(adresse):
            try:
                location = geocode(adresse)
                if location:
                    return pd.Series([location.latitude, location.longitude])
            except:
                pass
            return pd.Series([None, None])

        df[["Liefer_Lat", "Liefer_Lon"]] = df["Lieferadresse"].apply(get_coords)

        # Entfernung berechnen (in Metern)
        def berechne_entfernung(row):
            try:
                p1 = (row["Geo-Lat"], row["Geo-Lon"])
                p2 = (row["Liefer_Lat"], row["Liefer_Lon"])
                return round(geodesic(p1, p2).meters, 1)
            except:
                return None

        df["Entfernung (m)"] = df.apply(berechne_entfernung, axis=1)

        # Unnötige Spalten entfernen
        df = df.drop(columns=["Lieferadresse"])
        if "PLZ" in df.columns:
            df = df.drop(columns=["PLZ"])

        # Ergebnis anzeigen
        st.success("Fertig! Hier ist deine Tabelle:")
        st.dataframe(df)

  from io import BytesIO

# Excel in Speicher schreiben
output = BytesIO()
df.to_excel(output, index=False)
output.seek(0)

# Download-Button anzeigen
st.download_button(
    label="Ergebnis als Excel herunterladen",
    data=output,
    file_name="entfernungsergebnis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

