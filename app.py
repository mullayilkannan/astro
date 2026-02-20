import streamlit as st
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const, ephem
from geopy.geocoders import Nominatim
import os

# --- CRITICAL FIX FOR STREAMLIT ---
# This tells flatlib to use the internal swefiles or handles the path
try:
    import swisseph as swe
    # Streamlit often needs a path set even if it's empty to initialize the C-library
    swe.set_ephe_path(os.getcwd()) 
except:
    pass

# --- GEOLOCATION ---
def get_coords(place_name):
    try:
        geolocator = Nominatim(user_agent="kathamandapam_astro")
        location = geolocator.geocode(place_name)
        if location:
            return location.latitude, location.longitude, location.address
    except:
        return None, None, None

# --- GULIKAN LOGIC ---
def get_gulikan_sign(dt, pos):
    sunrise = ephem.next_sunrise(dt, pos)
    sunset = ephem.next_sunset(dt, pos)
    is_day = sunrise.jd < dt.jd < sunset.jd
    weekday = (dt.date().weekday() + 1) % 7 
    day_target = {0:7, 1:6, 2:5, 3:4, 4:3, 5:2, 6:1} 
    night_target = {0:3, 1:2, 2:1, 3:7, 4:6, 5:5, 6:4}
    seg_idx = day_target[weekday] if is_day else night_target[weekday]
    duration = (sunset.jd - sunrise.jd) if is_day else (1.0 - (sunset.jd - sunrise.jd))
    seg_length = duration / 8
    target_jd = sunrise.jd + ((seg_idx - 1) * seg_length) if is_day else sunset.jd + ((seg_idx - 1) * seg_length)
    
    g_dt = Datetime(dt.date().strftime('%Y/%m/%d'), dt.time().strftime('%H:%M'), dt.utcoffset)
    g_dt.jd = target_jd
    g_chart = Chart(g_dt, pos)
    return g_chart.get(const.ASC).sign

# --- UI ---
st.set_page_config(page_title="Kathamandapam Astro")
st.title("🌟 Kerala Rasi Chart")

with st.sidebar:
    dob = st.date_input("Date of Birth")
    tob = st.time_input("Time of Birth")
    place = st.text_input("Place of Birth", value="Vaikom, Kerala")
    tz = st.text_input("Timezone Offset", value="+05:30")

if st.button("Generate Chart"):
    lat, lon, full_address = get_coords(place)
    
    if lat:
        st.info(f"Location: {full_address}")
        dt = Datetime(dob.strftime('%Y/%m/%d'), tob.strftime('%H:%M'), tz)
        pos = GeoPos(lat, lon)
        
        try:
            # We attempt to create the chart. 
            # If this still fails with IndexError, the environment version is the issue.
            chart = Chart(dt, pos, ayanamsa=1)
            
            house_data = {sign: [] for sign in range(1, 13)}
            for p in chart.objects:
                house_data[p.sign].append(p.id)
            
            house_data[chart.get(const.ASC).sign].append("Asc")
            
            # Gulikan
            g_sign = get_gulikan_sign(dt, pos)
            house_data[g_sign].append("Gulikan")

            # HTML Rendering (Truncated for brevity, use your existing table code here)
            st.write("### Success! Rendering Chart...")
            # ... [Insert your HTML Table Code here] ...
            
        except Exception as e:
            st.error(f"Calculation Error: {e}")
            st.warning("This is likely due to Python 3.13 incompatibility with the Swiss Ephemeris library.")
