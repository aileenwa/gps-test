import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Datei einlesen
df = pd.read_excel("deine_datei.xlsx")  # oder von Streamlit-Dateiupload

# Geocoder initialisieren
geolocator = Nominatim(user_agent="geo-app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Funktion zur Umwandlung von Adresse zu Koordinaten
def get_coordinates(address):
    try:
        location = geocode(address)
        if location:
            return pd.Series([location.latitude, location.longitude])
    except:
        pass
    return pd.Series([None, None])

# Geodaten berechnen
df[["Liefer_Lat", "Liefer_Lon"]] = df["Lieferadresse"].apply(get_coordinates)

# Lieferadresse entfernen (Datenschutz)
df = df.drop(columns=["Lieferadresse"])

# Datei speichern oder zurückgeben
df.to_excel("Geodaten_output.xlsx", index=False)
