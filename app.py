import streamlit as st
from geopy.geocoders import Nominatim
import math
from datetime import datetime, timedelta

# --- NAKSHATRA & DASA DATA ---
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

DASA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

# --- CALCULATIONS ---
def get_moon_long(jd):
    days_since_2000 = jd - 2451545.0
    moon_pos = (218.31 + 13.17639 * days_since_2000) % 360
    return (moon_pos - 24.1) % 360 

def get_dasa_info(moon_long):
    star_pos = moon_long / 13.3333
    star_index = int(star_pos) % 27
    lord_index = star_index % 9
    star_start = int(star_pos) * 13.3333
    consumed = moon_long - star_start
    percent_left = (13.3333 - consumed) / 13.3333
    balance_years = percent_left * DASA_YEARS[lord_index]
    return DASA_LORDS[lord_index], round(balance_years, 2)

def get_rasi_positions(jd):
    periods = {"Sun": 365.25, "Moon": 27.32, "Mars": 686.98, "Mercury": 87.97, "Jupiter": 4332.59, "Venus": 224.7, "Saturn": 10759.22, "Rahu": 6793.5}
    offsets = {"Sun": 280.46, "Moon": 218.31, "Mars": 355.45, "Mercury": 174.79, "Jupiter": 34.40, "Venus": 181.98, "Saturn": 50.07, "Rahu": 125.12}
    days_since_2000 = jd - 2451545.0
    results = {}
    for p, period in periods.items():
        pos = (offsets[p] + (360.0 / period) * days_since_2000) % 360
        if p == "Rahu": pos = (offsets[p] - (360.0 / period) * days_since_2000) % 360
        sidereal_pos = (pos - 24.1) % 360
        results[p] = int(sidereal_pos / 30) + 1
    results["Kethu"] = (results["Rahu"] + 6 - 1) % 12 + 1
    return results

# --- UI SETUP ---
st.set_page_config(page_title="Personal Vedic Chart", layout="centered")
st.title("🌟 Personal Rasi Chart")

with st.form("user_details"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", value="User")
        gender = st.selectbox("Sex", ["Male", "Female", "Other"])
    with col2:
        dob = st.date_input("Date of Birth", value=datetime(1995, 1, 1), min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31))
        tob = st.time_input("Time of Birth")
    place = st.text_input("Place of Birth", value="Vaikom, Kerala")
    submitted = st.form_submit_button("Generate Report")

if submitted:
    geolocator = Nominatim(user_agent="personal_astro_pro")
    loc = geolocator.geocode(place)
    
    if loc:
        dt_obj = datetime.combine(dob, tob) - timedelta(hours=5.5)
        jd = 2451545.0 + (dt_obj - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0
        
        moon_long = get_moon_long(jd)
        star = NAKSHATRAS[int(moon_long / 13.3333) % 27]
        padam = int((moon_long % 13.3333) / 3.3333) + 1
        dasa_lord, balance = get_dasa_info(moon_long)
        positions = get_rasi_positions(jd)
        
        # Calculate ASC and Gulikan (Simplified placement)
        local_hour = tob.hour + tob.minute/60.0
        asc_sign = (int((local_hour - 6) / 2) + positions["Sun"] - 1) % 12 + 1
        gulikan_sign = (positions["Saturn"] + 2 - 1) % 12 + 1
        
        house_data = {i: [] for i in range(1, 13)}
        for p, sign in positions.items(): house_data[sign].append(p)
        house_data[asc_sign].append("ASC")
        house_data[gulikan_sign].append("Gulikan")

        # --- DATE FORMATTING ---
        formatted_date = dob.strftime('%d/%m/%y')
        formatted_time = tob.strftime('%I:%M %p')

        def get_p(idx):
            return "<br>".join(house_data[idx]) if house_data[idx] else ""

        # --- HTML CHART ---
        chart_html = f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <table style="width:100%; max-width: 550px; border: 3px solid #2c3e50; text-align: center; height: 500px; background-color: white; font-family: sans-serif;">
              <tr style="height: 25%;">
                <td style="border:1px solid #ddd; width:25%;">{get_p(12)}</td>
                <td style="border:1px solid #ddd; width:25%;">{get_p(1)}</td>
                <td style="border:1px solid #ddd; width:25%;">{get_p(2)}</td>
                <td style="border:1px solid #ddd; width:25%;">{get_p(3)}</td>
              </tr>
              <tr style="height: 25%;">
                <td style="border:1px solid #ddd;">{get_p(11)}</td>
                <td colspan="2" rowspan="2" style="background-color:#fafafa; padding: 20px;">
                    <div style="font-weight: bold; font-size: 1.2em;">{name.upper()}</div>
                    <div style="font-size: 0.8em; color: #555;">{gender} | {formatted_date} | {formatted_time}</div>
                    <div style="margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px;">
                        <small style="letter-spacing: 1px; color: #777;">NAKSHATRA</small><br>
                        <b style="font-size: 1.4em; color: #e67e22;">{star}</b><br>
                        <span style="font-size: 1em;">Padam: {padam}</span>
                    </div>
                </td>
                <td style="border:1px solid #ddd;">{get_p(4)}</td>
              </tr>
              <tr style="height: 25%;">
                <td style="border:1px solid #ddd;">{get_p(10)}</td>
                <td style="border:1px solid #ddd;">{get_p(5)}</td>
              </tr>
              <tr style="height: 25%;">
                <td style="border:1px solid #ddd;">{get_p(9)}</td>
                <td style="border:1px solid #ddd;">{get_p(8)}</td>
                <td style="border:1px solid #ddd;">{get_p(7)}</td>
                <td style="border:1px solid #ddd;">{get_p(6)}</td>
              </tr>
            </table>
        </div>
        """
        st.markdown(chart_html, unsafe_allow_html=True)
        st.write(f"**Born in {dasa_lord} Dasa.** Balance: {balance} years.")
    else:
        st.error("Location error. Try entering City, Country.")
