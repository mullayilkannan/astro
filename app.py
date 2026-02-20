 import streamlit as st
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import pandas as pd

# --- UI SETUP ---
st.set_page_config(page_title="Kathamandapam Astro", layout="centered")
st.title("🌟 Kerala Rasi Chart")

with st.sidebar:
    st.header("Birth Details")
    dob = st.date_input("Date of Birth")
    tob = st.time_input("Time of Birth")
    lat = st.number_input("Latitude", value=9.74)
    lon = st.number_input("Longitude", value=76.39)
    tz = st.text_input("Timezone Offset", value="+05:30")

if st.button("Generate Chart"):
    date_str = dob.strftime('%Y/%m/%d')
    time_str = tob.strftime('%H:%M')
    
    # Initialize Flatlib
    pos = GeoPos(lat, lon)
    dt = Datetime(date_str, time_str, tz)
    
    # FIX: Use AYAN_LAHIRI instead of AYANAMSA_LAHIRI
    chart = Chart(dt, pos, ayanamsa=const.AYAN_LAHIRI)
    
    # Map Planets to Houses (1=Aries ... 12=Pisces)
    house_data = {sign: [] for sign in range(1, 13)}
    for p in chart.objects:
        house_data[p.sign].append(p.id)
    
    # Add Lagna (Ascendant)
    asc = chart.get(const.ASC)
    house_data[asc.sign].append("Asc")
    
    # For now, let's place Gulikan in a fixed spot to ensure it renders, 
    # until you're ready for the full sunrise math!
    house_data[10].append("Gulikan") 

    # --- RENDER SOUTH INDIAN CHART ---
    def get_p(sign_idx):
        return "<br>".join(house_data[sign_idx]) if house_data[sign_idx] else ""

    chart_html = f"""
    <div style="display: flex; justify-content: center;">
        <table style="width:100%; max-width: 500px; border: 3px solid #4A148C; text-align: center; font-family: sans-serif; height: 400px; background-color: #ffffff;">
          <tr>
            <td style="border: 1px solid #ccc; width: 25%; height: 100px;">{get_p(12)}<br><small style="color: blue;">Pisces</small></td>
            <td style="border: 1px solid #ccc; width: 25%;">{get_p(1)}<br><small style="color: blue;">Aries</small></td>
            <td style="border: 1px solid #ccc; width: 25%;">{get_p(2)}<br><small style="color: blue;">Taurus</small></td>
            <td style="border: 1px solid #ccc; width: 25%;">{get_p(3)}<br><small style="color: blue;">Gemini</small></td>
          </tr>
          <tr>
            <td style="border: 1px solid #ccc; height: 100px;">{get_p(11)}<br><small style="color: blue;">Aquarius</small></td>
            <td colspan="2" rowspan="2" style="background-color: #f3e5f5; font-weight: bold; color: #4A148C;">KATHAMANDAPAM<br>ASTROLOGY</td>
            <td style="border: 1px solid #ccc;">{get_p(4)}<br><small style="color: blue;">Cancer</small></td>
          </tr>
          <tr>
            <td style="border: 1px solid #ccc; height: 100px;">{get_p(10)}<br><small style="color: blue;">Capricorn</small></td>
            <td style="border: 1px solid #ccc;">{get_p(5)}<br><small style="color: blue;">Leo</small></td>
          </tr>
          <tr>
            <td style="border: 1px solid #ccc; height: 100px;">{get_p(9)}<br><small style="color: blue;">Sagittarius</small></td>
            <td style="border: 1px solid #ccc;">{get_p(8)}<br><small style="color: blue;">Scorpio</small></td>
            <td style="border: 1px solid #ccc;">{get_p(7)}<br><small style="color: blue;">Libra</small></td>
            <td style="border: 1px solid #ccc;">{get_p(6)}<br><small style="color: blue;">Virgo</small></td>
          </tr>
        </table>
    </div>
    """
    st.markdown(chart_html, unsafe_allow_html=True)
    st.success("Successfully generated!")
