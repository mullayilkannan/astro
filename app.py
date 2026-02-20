import streamlit as st
from geopy.geocoders import Nominatim
import math
from datetime import datetime, timedelta

# --- NAKSHATRA DATA ---
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def get_nakshatra_info(jd):
    # Mean motion of Moon: ~13.176 degrees per day
    # J2000 Moon position offset
    days_since_2000 = jd - 2451545.0
    moon_pos = (218.31 + 13.17639 * days_since_2000) % 360
    sidereal_moon = (moon_pos - 24.1) % 360 # Lahiri Ayanamsa
    
    # Each Nakshatra is 13° 20' (13.333 degrees)
    star_index = int(sidereal_moon / 13.333)
    # Each Padam is 3° 20' (3.333 degrees)
    padam = int((sidereal_moon % 13.333) / 3.333) + 1
    
    return NAKSHATRAS[star_index], padam

def get_rasi_positions(jd):
    periods = {
        "Sun": 365.25, "Moon": 27.32, "Mars": 686.98, "Mercury": 87.97,
        "Jupiter": 4332.59, "Venus": 224.7, "Saturn": 10759.22, "Rahu": 6793.5
    }
    offsets = {
        "Sun": 280.46, "Moon": 218.31, "Mars": 355.45, "Mercury": 174.79,
        "Jupiter": 34.40, "Venus": 181.98, "Saturn": 50.07, "Rahu": 125.12
    }
    days_since_2000 = jd - 2451545.0
    results = {}
    for planet, period in periods.items():
        pos = (offsets[planet] + (360.0 / period) * days_since_2000) % 360
        if planet == "Rahu": pos = (offsets[planet] - (360.0 / period) * days_since_2000) % 360
        sidereal_pos = (pos - 24.1) % 360
        results[planet] = int(sidereal_pos / 30) + 1
    results["Kethu"] = (results["Rahu"] + 6 - 1) % 12 + 1
    return results

# --- UI SETUP ---
st.set_page_config(page_title="Personal Vedic Chart", layout="centered")
st.title("🪐 Detailed Rasi Chart")

with st.form("user_details"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value="Guest")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
        dob = st.date_input("Date of Birth")
        tob = st.time_input("Time of Birth")
    place = st.text_input("Place of Birth", value="Vaikom, Kerala")
    submitted = st.form_submit_button("Generate Personal Chart")

if submitted:
    geolocator = Nominatim(user_agent="astro_v2")
    loc = geolocator.geocode(place)
    
    if loc:
        dt_obj = datetime.combine(dob, tob) - timedelta(hours=5.5)
        year, month, day = dt_obj.year, dt_obj.month, dt_obj.day
        hour = dt_obj.hour + dt_obj.minute/60.0
        if month <= 2: year -= 1; month += 12
        A = int(year/100); B = 2 - A + int(A/4)
        jd = int(365.25*(year + 4716)) + int(30.6001*(month + 1)) + day + hour/24.0 + B - 1524.5

        # Data Retrieval
        positions = get_rasi_positions(jd)
        star, padam = get_nakshatra_info(jd)
        
        # Lagna & Gulikan Calculation
        local_hour = tob.hour + tob.minute/60.0
        asc_sign = (int((local_hour - 6) / 2) + positions["Sun"] - 1) % 12 + 1
        gulikan_sign = (positions["Saturn"] + 2 - 1) % 12 + 1
        
        house_data = {i: [] for i in range(1, 13)}
        for p, sign in positions.items(): house_data[sign].append(p)
        house_data[asc_sign].append("ASC")
        house_data[gulikan_sign].append("Gulikan")

        def get_p(idx):
            return "<br>".join(house_data[idx]) if house_data[idx] else ""

        # --- HTML TABLE RENDERING ---
        chart_html = f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <table style="width:100%; max-width: 550px; border: 2px solid #2c3e50; text-align: center; height: 500px; background-color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
              <tr style="height: 25%;">
                <td style="border:1px solid #bdc3c7; width:25%;">{get_p(12)}</td>
                <td style="border:1px solid #bdc3c7; width:25%;">{get_p(1)}</td>
                <td style="border:1px solid #bdc3c7; width:25%;">{get_p(2)}</td>
                <td style="border:1px solid #bdc3c7; width:25%;">{get_p(3)}</td>
              </tr>
              <tr style="height: 25%;">
                <td style="border:1px solid #bdc3c7;">{get_p(11)}</td>
                <td colspan="2" rowspan="2" style="background-color:#fdfefe; padding: 15px; border: 1px solid #bdc3c7;">
                    <div style="font-size: 1.1em; color: #2c3e50; font-weight: bold; border-bottom: 1px solid #eee; margin-bottom: 5px;">{name.upper()}</div>
                    <div style="font-size: 0.85em; color: #7f8c8d;">{gender} | {dob.strftime('%d-%m-%Y')}</div>
                    <div style="margin-top: 15px; padding: 10px; background-color: #f4f6f7; border-radius: 5px;">
                        <span style="font-size: 0.8em; color: #34495e; display: block; text-transform: uppercase; letter-spacing: 1px;">Nakshatra</span>
                        <b style="font-size: 1.2em; color: #e67e22;">{star}</b><br>
                        <span style="font-size: 0.9em; color: #2c3e50;">Padam: {padam}</span>
                    </div>
                </td>
                <td style="border:1px solid #bdc3c7;">{get_p(4)}</td>
              </tr>
              <tr style="height: 25%;">
                <td style="border:1px solid #bdc3c7;">{get_p(10)}</td>
                <td style="border:1px solid #bdc3c7;">{get_p(5)}</td>
              </tr>
              <tr style="height: 25%;">
                <td style="border:1px solid #bdc3c7;">{get_p(9)}</td>
                <td style="border:1px solid #bdc3c7;">{get_p(8)}</td>
                <td style="border:1px solid #bdc3c7;">{get_p(7)}</td>
                <td style="border:1px solid #bdc3c7;">{get_p(6)}</td>
              </tr>
            </table>
        </div>
        """
        st.markdown(chart_html, unsafe_allow_html=True)
        st.balloons()
