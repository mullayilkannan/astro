import streamlit as st
from geopy.geocoders import Nominatim
import math
from datetime import datetime, timedelta

# --- PURE PYTHON FALLBACK LOGIC (No Swiss Ephem required) ---
# This calculates approximate planetary positions to avoid the 3.13 crash
def get_approx_rasi(planet_name, jd):
    # Standard periods in days
    periods = {"Sun": 365.25, "Moon": 27.32, "Mars": 686.98, "Jupiter": 4332.59, "Saturn": 10759.22}
    # Approximate J2000 positions
    offsets = {"Sun": 280.46, "Moon": 218.31, "Mars": 355.45, "Jupiter": 34.40, "Saturn": 50.07}
    
    days_since_2000 = jd - 2451545.0
    pos = (offsets.get(planet_name, 0) + (360.0 / periods.get(planet_name, 365)) * days_since_2000) % 360
    # Lahiri Ayanamsa is roughly 24 degrees
    sidereal_pos = (pos - 24.0) % 360
    return int(sidereal_pos / 30) + 1

# --- UI SETUP ---
st.set_page_config(page_title="Kathamandapam Astro", layout="centered")
st.title("🌟 Kerala Rasi Chart")
st.info("Running in Hybrid Mode (Bypassing Python 3.13 compatibility issues)")

with st.sidebar:
    dob = st.date_input("Date of Birth")
    tob = st.time_input("Time of Birth")
    place = st.text_input("Place of Birth", value="Vaikom, Kerala")
    tz_offset = 5.5 # Fixed for India to simplify

if st.button("Generate Chart"):
    geolocator = Nominatim(user_agent="kathamandapam_fix")
    loc = geolocator.geocode(place)
    
    if loc:
        st.write(f"**Location:** {loc.address}")
        
        # Calculate Julian Day
        d = datetime.combine(dob, tob) - timedelta(hours=tz_offset)
        year, month, day = d.year, d.month, d.day
        hour = d.hour + d.minute/60.0 + d.second/3600.0
        if month <= 2:
            year -= 1
            month += 12
        A = int(year/100)
        B = 2 - A + int(A/4)
        jd = int(365.25*(year + 4716)) + int(30.6001*(month + 1)) + day + hour/24.0 + B - 1524.5

        # Populate Houses
        house_data = {i: [] for i in range(1, 13)}
        planets = ["Sun", "Moon", "Mars", "Jupiter", "Saturn"]
        
        for p in planets:
            sign = get_approx_rasi(p, jd)
            house_data[sign].append(p)

        # Approximate Ascendant based on Sunrise (Standard Kerala method)
        # In a real app, we'd use exact sunrise; here we use 6:00 AM local as base
        local_hour = tob.hour + tob.minute/60.0
        asc_sign = (int((local_hour - 6) / 2) + get_approx_rasi("Sun", jd))
        asc_sign = (asc_sign - 1) % 12 + 1
        house_data[asc_sign].append("Asc")
        
        # Gulikan (Static placement for demo logic to prevent crash)
        house_data[(asc_sign + 4) % 12 + 1].append("Gulikan")

        # --- RENDER TABLE ---
        def get_p(idx):
            return "<br>".join(house_data[idx]) if house_data[idx] else ""

        chart_html = f"""
        <div style="display: flex; justify-content: center;">
            <table style="width:100%; max-width: 500px; border: 3px solid #4A148C; text-align: center; height: 400px; background-color: white; font-weight: bold;">
              <tr>
                <td style="border:1px solid #ccc; width:25%;">{get_p(12)}<br><small>12</small></td>
                <td style="border:1px solid #ccc; width:25%;">{get_p(1)}<br><small>1</small></td>
                <td style="border:1px solid #ccc; width:25%;">{get_p(2)}<br><small>2</small></td>
                <td style="border:1px solid #ccc; width:25%;">{get_p(3)}<br><small>3</small></td>
              </tr>
              <tr>
                <td style="border:1px solid #ccc;">{get_p(11)}<br><small>11</small></td>
                <td colspan="2" rowspan="2" style="background-color:#f3e5f5;">KATHAMANDAPAM</td>
                <td style="border:1px solid #ccc;">{get_p(4)}<br><small>4</small></td>
              </tr>
              <tr>
                <td style="border:1px solid #ccc;">{get_p(10)}<br><small>10</small></td>
                <td style="border:1px solid #ccc;">{get_p(5)}<br><small>5</small></td>
              </tr>
              <tr>
                <td style="border:1px solid #ccc;">{get_p(9)}<br><small>9</small></td>
                <td style="border:1px solid #ccc;">{get_p(8)}<br><small>8</small></td>
                <td style="border:1px solid #ccc;">{get_p(7)}<br><small>7</small></td>
                <td style="border:1px solid #ccc;">{get_p(6)}<br><small>6</small></td>
              </tr>
            </table>
        </div>
        """
        st.markdown(chart_html, unsafe_allow_html=True)
