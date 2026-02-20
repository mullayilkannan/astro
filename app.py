import streamlit as st
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import pandas as pd

# --- GULIKAN CALCULATION LOGIC ---
def calculate_gulikan(chart_date, chart_time, lat, lon):
    # Simplified segment logic based on Kerala Tradition
    # Day/Night segments start from day lord. 8th segment is lordless.
    # Saturday's segment is Gulikan.
    
    # Standard segment order: 1st segment of Sun is Sun, Mon is Mon...
    # For day birth, Saturn's segment: Sun(7), Mon(6), Tue(5), Wed(4), Thu(3), Fri(2), Sat(1)
    day_segments = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1} # 0=Sun, 6=Sat
    
    # For night birth, 1st segment starts from 5th day from weekday.
    # Night segment for Saturn: Sun(3), Mon(2), Tue(1), Wed(7), Thu(6), Fri(5), Sat(4)
    night_segments = {0: 3, 1: 2, 2: 1, 3: 7, 4: 6, 5: 5, 6: 4}

    # Note: For high precision, use sunrise/sunset times. 
    # Here we use a standard 6AM-6PM logic for the demo engine.
    # In a full app, use flatlib.ephem.next_sunrise() for exactness.
    return "Calculated Gulikan"

# --- UI SETUP ---
st.set_page_config(page_title="Kerala Rasi Chart", layout="centered")
st.title("🌟 South Indian Rasi Chart")
st.subheader("Including Gulikan & Traditional Layout")

with st.sidebar:
    st.header("Birth Details")
    dob = st.date_input("Date of Birth")
    tob = st.time_input("Time of Birth")
    lat = st.number_input("Latitude (e.g., 9.75 for Vaikom)", value=9.74)
    lon = st.number_input("Longitude (e.g., 76.40)", value=76.39)
    tz = st.text_input("Timezone Offset", value="+05:30")

if st.button("Generate Chart"):
    # Convert inputs
    date_str = dob.strftime('%Y/%m/%d')
    time_str = tob.strftime('%H:%M')
    
    # Initialize Flatlib Chart
    pos = GeoPos(lat, lon)
    dt = Datetime(date_str, time_str, tz)
    chart = Chart(dt, pos, ayanamsa=const.AYANAMSA_LAHIRI)
    
    # Get Planets
    planets = chart.objects
    house_data = {sign: [] for sign in range(1, 13)}
    
    # Map Planets to Houses (1=Aries, 12=Pisces)
    for p in planets:
        house_data[p.sign].append(p.id)
    
    # Add Lagna
    asc = chart.get(const.ASC)
    house_data[asc.sign].append("Asc")
    
    # Add Gulikan (Dummy placement for demo - needs exact degree calculation)
    house_data[2].append("Gulikan") 

    # --- RENDER SOUTH INDIAN CHART ---
    # Layout: 4x4 Grid
    # Top: Pisces(12), Aries(1), Taurus(2), Gemini(3)
    # Mid: Aquarius(11), [Empty], [Empty], Cancer(4)
    # Mid: Capricorn(10), [Empty], [Empty], Leo(5)
    # Bot: Sagitt(9), Scorpio(8), Libra(7), Virgo(6)
    
    def get_p(sign_idx):
        return ", ".join(house_data[sign_idx]) if house_data[sign_idx] else ""

    chart_html = f"""
    <table style="width:100%; border: 2px solid black; text-align: center; font-weight: bold; height: 400px; background-color: #fff9f0; color: #333;">
      <tr>
        <td style="border: 1px solid gray; width: 25%;">{get_p(12)}<br><small>Pisces</small></td>
        <td style="border: 1px solid gray; width: 25%;">{get_p(1)}<br><small>Aries</small></td>
        <td style="border: 1px solid gray; width: 25%;">{get_p(2)}<br><small>Taurus</small></td>
        <td style="border: 1px solid gray; width: 25%;">{get_p(3)}<br><small>Gemini</small></td>
      </tr>
      <tr>
        <td style="border: 1px solid gray;">{get_p(11)}<br><small>Aquarius</small></td>
        <td colspan="2" rowspan="2" style="background-color: #eee;">Kathamandapam<br>Astro Engine</td>
        <td style="border: 1px solid gray;">{get_p(4)}<br><small>Cancer</small></td>
      </tr>
      <tr>
        <td style="border: 1px solid gray;">{get_p(10)}<br><small>Capricorn</small></td>
        <td style="border: 1px solid gray;">{get_p(5)}<br><small>Leo</small></td>
      </tr>
      <tr>
        <td style="border: 1px solid gray;">{get_p(9)}<br><small>Sagitt</small></td>
        <td style="border: 1px solid gray;">{get_p(8)}<br><small>Scorpio</small></td>
        <td style="border: 1px solid gray;">{get_p(7)}<br><small>Libra</small></td>
        <td style="border: 1px solid gray;">{get_p(6)}<br><small>Virgo</small></td>
      </tr>
    </table>
    """
    st.markdown(chart_html, unsafe_allow_stdio=True, unsafe_allow_html=True)
    st.success("Chart generated successfully!")