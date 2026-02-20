import streamlit as st
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import math

# --- DATA ---
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# --- PRECISION MATH ---
def get_julian_date(day, month, year, time_obj):
    # IST to UTC offset
    dt = datetime(year, month, day, time_obj.hour, time_obj.minute) - timedelta(hours=5.5)
    y, m, d = dt.year, dt.month, dt.day
    h = dt.hour + dt.minute/60.0
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y/100)
    B = 2 - A + math.floor(A/4)
    jd = math.floor(365.25*(y + 4716)) + math.floor(30.6001*(m + 1)) + d + h/24.0 + B - 1524.5
    return jd

def get_precise_positions(jd):
    planets = {
        "Sun": (280.460, 0.9856474), "Moon": (218.316, 13.176396),
        "Mars": (355.453, 0.5240207), "Mercury": (174.794, 4.09233),
        "Jupiter": (34.404, 0.08308), "Venus": (181.979, 1.60213),
        "Saturn": (50.077, 0.033459), "Rahu": (125.122, -0.0529539)
    }
    days_since_2000 = jd - 2451545.0
    ayanamsa = 24.1 
    pos_results = {}
    for p, (base, motion) in planets.items():
        pos = (base + (motion * days_since_2000)) % 360
        sidereal_pos = (pos - ayanamsa) % 360
        pos_results[p] = int(sidereal_pos / 30) + 1
        if p == "Moon": pos_results["moon_long"] = sidereal_pos
    pos_results["Kethu"] = (pos_results["Rahu"] + 6 - 1) % 12 + 1
    return pos_results

# --- UI SETUP ---
st.set_page_config(page_title="Personal Rasi Chart", layout="centered")
st.title("🕉️ Vedic Rasi Chart")

with st.container():
    st.subheader("Enter Birth Details")
    name = st.text_input("Full Name")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    
    st.write("**Date of Birth (DD-MM-YYYY)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        d_day = st.number_input("Day (DD)", min_value=1, max_value=31, value=1)
    with c2:
        d_month = st.number_input("Month (MM)", min_value=1, max_value=12, value=1)
    with c3:
        d_year = st.number_input("Year (YYYY)", min_value=1900, max_value=2100, value=1990)

    c4, c5 = st.columns(2)
    with c4:
        tob = st.time_input("Time of Birth")
    with c5:
        place_input = st.text_input("Place of Birth", placeholder="e.g. Vaikom, Kerala")

if place_input:
    geolocator = Nominatim(user_agent="my_astro_app")
    location = geolocator.geocode(place_input)
    
    if location:
        st.success(f"✅ **Location Confirmed:** {location.address}")
        
        if st.button("Generate Rasi Chart"):
            jd = get_julian_date(d_day, d_month, d_year, tob)
            pos = get_precise_positions(jd)
            
            # Nakshatra Logic
            moon_long = pos["moon_long"]
            star_idx = int(moon_long / 13.333333)
            star_name = NAKSHATRAS[star_idx % 27]
            padam = int((moon_long % 13.333333) / 3.333333) + 1
            
            # Chart Data
            house_data = {i: [] for i in range(1, 13)}
            for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Kethu"]:
                house_data[pos[p]].append(p)
            
            # Lagna (Approx)
            local_hour = tob.hour + tob.minute/60.0
            asc_sign = (int((local_hour - 6) / 2) + pos["Sun"] - 1) % 12 + 1
            house_data[asc_sign].append("ASC")

            def get_p(idx):
                return "<br>".join(house_data[idx]) if house_data[idx] else ""

            # Display DD/MM/YYYY Format
            disp_date = f"{d_day:02d}/{d_month:02d}/{d_year}"

            chart_html = f"""
            <div style="display: flex; justify-content: center; margin-top: 30px;">
                <table style="width:100%; max-width: 550px; border: 3px solid #000; text-align: center; height: 500px; background-color: #fff; border-collapse: collapse; font-family: sans-serif;">
                  <tr style="height: 25%;">
                    <td style="border:1px solid #000; width:25%;">{get_p(12)}</td>
                    <td style="border:1px solid #000; width:25%;">{get_p(1)}</td>
                    <td style="border:1px solid #000; width:25%;">{get_p(2)}</td>
                    <td style="border:1px solid #000; width:25%;">{get_p(3)}</td>
                  </tr>
                  <tr style="height: 25%;">
                    <td style="border:1px solid #000;">{get_p(11)}</td>
                    <td colspan="2" rowspan="2" style="background-color: #fcfcfc; padding: 10px;">
                        <div style="font-weight: bold; font-size: 1.2em; color: #2c3e50;">{name.upper()}</div>
                        <div style="font-size: 0.85em; margin-bottom: 5px;">{sex} | {disp_date} | {tob.strftime('%I:%M %p')}</div>
                        <div style="background-color: #f4f6f7; padding: 12px; border-radius: 8px; border: 1px solid #eee; margin-top: 15px;">
                            <span style="font-size: 0.7em; color: #7f8c8d; display: block; letter-spacing: 1px;">NAKSHATRA & PADAM</span>
                            <b style="font-size: 1.4em; color: #d35400;">{star_name}</b><br>
                            <span style="font-size: 1em; color: #2c3e50;">Padam: {padam}</span>
                        </div>
                    </td>
                    <td style="border:1px solid #000;">{get_p(4)}</td>
                  </tr>
                  <tr style="height: 25%;">
                    <td style="border:1px solid #000;">{get_p(10)}</td>
                    <td style="border:1px solid #000;">{get_p(5)}</td>
                  </tr>
                  <tr style="height: 25%;">
                    <td style="border:1px solid #000;">{get_p(9)}</td>
                    <td style="border:1px solid #000;">{get_p(8)}</td>
                    <td style="border:1px solid #000;">{get_p(7)}</td>
                    <td style="border:1px solid #000;">{get_p(6)}</td>
                  </tr>
                </table>
            </div>
            """
            st.markdown(chart_html, unsafe_allow_html=True)
    else:
        st.error("❌ Place not found. Please re-enter the City and State.")
