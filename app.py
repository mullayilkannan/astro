import streamlit as st
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const, ephem
from geopy.geocoders import Nominatim
import pandas as pd

# --- GEOLOCATION LOGIC ---
def get_coords(place_name):
    geolocator = Nominatim(user_agent="kathamandapam_astro_app")
    location = geolocator.geocode(place_name)
    if location:
        return location.latitude, location.longitude, location.address
    return None, None, None

# --- KERALA GULIKAN LOGIC ---
def get_gulikan_sign(dt, pos):
    sunrise = ephem.next_sunrise(dt, pos)
    sunset = ephem.next_sunset(dt, pos)
    is_day = sunrise.jd < dt.jd < sunset.jd
    
    # Weekday adjustment (0=Sun, 6=Sat)
    weekday = (dt.date().weekday() + 1) % 7 
    
    # Segment where Gulikan (Saturn) appears
    day_target = {0:7, 1:6, 2:5, 3:4, 4:3, 5:2, 6:1} 
    night_target = {0:3, 1:2, 2:1, 3:7, 4:6, 5:5, 6:4}
    
    seg_idx = day_target[weekday] if is_day else night_target[weekday]
    
    duration = (sunset.jd - sunrise.jd) if is_day else (1.0 - (sunset.jd - sunrise.jd))
    seg_length = duration / 8
    target_jd = sunrise.jd + ((seg_idx - 1) * seg_length) if is_day else sunset.jd + ((seg_idx - 1) * seg_length)
    
    # Find Ascendant at that specific time
    g_dt = Datetime(dt.date().strftime('%Y/%m/%d'), dt.time().strftime('%H:%M'), dt.utcoffset)
    g_dt.jd = target_jd
    g_chart = Chart(g_dt, pos)
    return g_chart.get(const.ASC).sign

# --- UI SETUP ---
st.set_page_config(page_title="Kathamandapam Astro", layout="centered")
st.title("🌟 Kerala Rasi Chart")

with st.sidebar:
    st.header("Birth Details")
    dob = st.date_input("Date of Birth")
    tob = st.time_input("Time of Birth")
    place = st.text_input("Place of Birth", value="Vaikom, Kerala")
    tz = st.text_input("Timezone Offset", value="+05:30")

if st.button("Generate Chart"):
    # 1. Geocode the place
    lat, lon, full_address = get_coords(place)
    
    if lat is None:
        st.error("Could not find that location. Please try a nearby city.")
    else:
        st.info(f"Location Found: {full_address}")
        
        # 2. Initialize Calculations
        date_str = dob.strftime('%Y/%m/%d')
        time_str = tob.strftime('%H:%M')
        pos = GeoPos(lat, lon)
        dt = Datetime(date_str, time_str, tz)
        
        # 3. Create Chart
        chart = Chart(dt, pos, ayanamsa=const.AYAN_LAHIRI)
        
        house_data = {sign: [] for sign in range(1, 13)}
        for p in chart.objects:
            house_data[p.sign].append(p.id)
        
        house_data[chart.get(const.ASC).sign].append("Asc")
        
        # 4. Calculate Accurate Gulikan
        g_sign = get_gulikan_sign(dt, pos)
        house_data[g_sign].append("Gulikan")

        # --- RENDER TABLE ---
        def get_p(sign_idx):
            return "<br>".join(house_data[sign_idx]) if house_data[sign_idx] else ""

        chart_html = f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <table style="width:100%; max-width: 500px; border: 3px solid #4A148C; text-align: center; height: 400px; background-color: #ffffff;">
              <tr>
                <td style="border: 1px solid #ccc; width: 25%;">{get_p(12)}<br><small style="color: blue;">Pisces</small></td>
                <td style="border: 1px solid #ccc; width: 25%;">{get_p(1)}<br><small style="color: blue;">Aries</small></td>
                <td style="border: 1px solid #ccc; width: 25%;">{get_p(2)}<br><small style="color: blue;">Taurus</small></td>
                <td style="border: 1px solid #ccc; width: 25%;">{get_p(3)}<br><small style="color: blue;">Gemini</small></td>
              </tr>
              <tr>
                <td style="border: 1px solid #ccc;">{get_p(11)}<br><small style="color: blue;">Aquarius</small></td>
                <td colspan="2" rowspan="2" style="background-color: #f3e5f5; font-weight: bold; color: #4A148C;">KATHAMANDAPAM<br>ASTROLOGY</td>
                <td style="border: 1px solid #ccc;">{get_p(4)}<br><small style="color: blue;">Cancer</small></td>
              </tr>
              <tr>
                <td style="border: 1px solid #ccc;">{get_p(10)}<br><small style="color: blue;">Capricorn</small></td>
                <td style="border: 1px solid #ccc;">{get_p(5)}<br><small style="color: blue;">Leo</small></td>
              </tr>
              <tr>
                <td style="border: 1px solid #ccc;">{get_p(9)}<br><small style="color: blue;">Sagitt</small></td>
                <td style="border: 1px solid #ccc;">{get_p(8)}<br><small style="color: blue;">Scorpio</small></td>
                <td style="border: 1px solid #ccc;">{get_p(7)}<br><small style="color: blue;">Libra</small></td>
                <td style="border: 1px solid #ccc;">{get_p(6)}<br><small style="color: blue;">Virgo</small></td>
              </tr>
            </table>
        </div>
        """
        st.markdown(chart_html, unsafe_allow_html=True)
        st.success("Successfully generated!")  chart_html = f"""
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


