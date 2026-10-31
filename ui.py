import streamlit as st
import requests

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="XGBoost Global Horizontal Radiation Predictor for Bale Zone",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# CUSTOM CSS (TIGHT / FRAMED / TIMES NEW ROMAN)
# ==========================================================
st.markdown(
    """
    <style>
        /* Global font: Times New Roman */
        html, body, [class*="css"], .stApp, .stMarkdown, .stText,
        div, p, span, label, input, textarea, select, button,
        h1, h2, h3, h4, h5, h6, .stButton > button,
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            font-family: "Times New Roman", Times, serif !important;
        }

        .main { background-color: #f5f8fc; }

        /* More top padding so header clears the browser bar */
        .block-container {
            max-width: 1100px;
            padding-top: 2.2rem !important;
            padding-bottom: 0.8rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        /* Top header - forced visible */
        .top-header {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            text-align: center !important;
            color: #15365c !important;
            font-family: "Times New Roman", Times, serif !important;
            font-size: 26px !important;
            font-weight: 800 !important;
            line-height: 1.25 !important;
            margin: 0 0 6px 0 !important;
            padding: 12px 8px !important;
            letter-spacing: 0.3px !important;
            background: #eaf1fb !important;
            border-radius: 8px !important;
        }

        .section-title {
            color:#15365c; font-size:17px; font-weight:700;
            border-bottom:2px solid #e2e8f0;
            padding-bottom:4px; margin-top:6px; margin-bottom:6px;
        }
        .result-card {
            background:linear-gradient(135deg,#0f766e,#164e63);
            color:white; padding:16px; border-radius:12px;
            text-align:center; margin-top:8px;
        }
        .result-label { font-size:15px; color:#d1fae5; }
        .result-value { font-size:32px; font-weight:800; margin:2px 0; }
        .result-unit { font-size:14px; color:#ccfbf1; }

        div.stButton > button {
            background-color:#0f766e; color:white; font-size:15px;
            font-weight:bold; border-radius:8px; padding:8px 18px;
            border:none; width:100%;
        }
        div.stButton > button:hover { background-color:#115e59; color:white; }

        /* Input readability */
        .stNumberInput input, .stTextInput input, .stSelectbox div {
            font-size:15px !important;
        }
        label, .stSelectbox label {
            font-size:14.5px !important;
            font-weight:600;
        }

        /* Compact widget spacing */
        div[data-testid="stVerticalBlock"] > div { margin-bottom: 0.2rem; }
        .stNumberInput, .stTextInput, .stSelectbox { margin-bottom: 0.1rem; }
        hr { margin: 6px 0; }

        /* Frame the main content (below the header) */
        div[data-testid="stAppViewContainer"] > section.main > div.block-container {
            border: 2px solid #15365c;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-top: 12px;
        }

        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# TOP HEADER (RENDERED FIRST, WITH CLEAR TOP SPACING)
# ==========================================================
st.markdown(
    '<div class="top-header">XGBoost Global Horizontal Radiation Predictor for Bale Zone</div>',
    unsafe_allow_html=True
)
st.divider()

# ==========================================================
# DEFAULT VALUES
# ==========================================================
DEFAULT_STUDY_AREA = "Bale Robe"
DEFAULT_PRECIPITATION = 0.0
DEFAULT_RELATIVE_HUMIDITY = 50.0
DEFAULT_SUNSHINE_HOURS = 11.3
DEFAULT_MAX_TEMP = 23.7
DEFAULT_MIN_TEMP = 5.5
DEFAULT_WIND_SPEED = 3.0

# ==========================================================
# MODEL PERFORMANCE METRICS PER STUDY AREA
# ==========================================================
MODEL_METRICS = {
    "Bale Robe": {"RMSE": 0.2038, "MAE": 0.1519, "MAPE": 2.8643, "$R^2$": 0.9665},
    "Dello Mena": {"RMSE": 0.577, "MAE": 0.315, "MAPE": 11.49, "$R^2$": 0.838},
    "Ginir": {"RMSE": 0.443, "MAE": 0.268, "MAPE": 6.84, "$R^2$": 0.878},
}

# ==========================================================
# INITIALIZE SESSION STATE (FIRST RUN ONLY)
# ==========================================================
if "study_area" not in st.session_state:
    st.session_state["study_area"] = DEFAULT_STUDY_AREA
if "precip" not in st.session_state:
    st.session_state["precip"] = DEFAULT_PRECIPITATION
if "rh" not in st.session_state:
    st.session_state["rh"] = DEFAULT_RELATIVE_HUMIDITY
if "sh" not in st.session_state:
    st.session_state["sh"] = DEFAULT_SUNSHINE_HOURS
if "maxt" not in st.session_state:
    st.session_state["maxt"] = DEFAULT_MAX_TEMP
if "mint" not in st.session_state:
    st.session_state["mint"] = DEFAULT_MIN_TEMP
if "ws" not in st.session_state:
    st.session_state["ws"] = DEFAULT_WIND_SPEED
if "prediction_result" not in st.session_state:
    st.session_state["prediction_result"] = None
if "predicted_area" not in st.session_state:
    st.session_state["predicted_area"] = None
if "show_metrics" not in st.session_state:
    st.session_state["show_metrics"] = False

# ==========================================================
# RESET CALLBACK (FULL RESET)
# ==========================================================
def reset_values():
    st.session_state["study_area"] = DEFAULT_STUDY_AREA
    st.session_state["precip"] = DEFAULT_PRECIPITATION
    st.session_state["rh"] = DEFAULT_RELATIVE_HUMIDITY
    st.session_state["sh"] = DEFAULT_SUNSHINE_HOURS
    st.session_state["maxt"] = DEFAULT_MAX_TEMP
    st.session_state["mint"] = DEFAULT_MIN_TEMP
    st.session_state["ws"] = DEFAULT_WIND_SPEED
    st.session_state["prediction_result"] = None
    st.session_state["predicted_area"] = None
    st.session_state["show_metrics"] = False

# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/869/869869.png", width=70)
    st.title("About the Application")
    st.write("""
        This application predicts Global Horizontal Radiation
        (GHR) using meteorological parameters and an XGBoost
        machine learning model. The predication accuracy of the application for Bale Robe  RMSE = 0.2038, MAE = 0.1519, 
        MAPE = 2.8643, and R-square = 0.9665. The model was trained on historical meteorological data from the Bale Robe. 
        The model performance metrics for other study areas are as follows: for Dello Mena RMSE = 0.577, MAE = 0.315, MAPE = 11.49, 
        and R-square = 0.838; for Ginir RMSE = 0.443, MAE = 0.268, MAPE = 6.84, and R-square = 0.878. 
    """)
    st.info("""
        **Study Areas**

        • Bale Robe  
        • Ginir  
        • Dello Mena
        """)
    st.caption("Solar Radiation Prediction System | XGBoost")

# ==========================================================
# STUDY AREA (title removed)
# ==========================================================
study_areas = ["Bale Robe", "Ginir", "Dello Mena"]
neighbourhood = st.selectbox(
    "Select your study area",
    study_areas,
    index=study_areas.index(st.session_state["study_area"]),
    help="Choose the town for which you want to predict GHR.",
    key="study_area"
)
st.success(f"Selected study area: {neighbourhood}")

# ==========================================================
# MODEL METRICS BUTTON
# ==========================================================
if st.button("Show Model Metrics for Selected Area", use_container_width=True, key="metrics_btn"):
    st.session_state["show_metrics"] = True

if st.session_state["show_metrics"]:
    metrics = MODEL_METRICS.get(neighbourhood)
    if metrics is None:
        st.warning(f"No model metrics available for {neighbourhood}.")
    else:
        st.markdown(f"**Model Performance Metrics for {neighbourhood}**")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("RMSE $kWh/m^2/day$", f"{metrics['RMSE']}")
        m2.metric("MAE $kWh/m^2/day$", f"{metrics['MAE']}")
        m3.metric("MAPE (%)", f"{metrics['MAPE']}")
        m4.metric("$R^2$", f"{metrics['$R^2$']}")

# ==========================================================
# METEOROLOGICAL INPUTS
# ==========================================================
st.markdown('<div class="section-title">Meteorological Parameters</div>', unsafe_allow_html=True)
st.caption("Enter the meteorological data below to estimate Global Horizontal Radiation.")

col1, col2 = st.columns(2)
with col1:
    precipitation = st.number_input(
        "Precipitation (mm/day) [0.00 to 25]", min_value=0.0,
        max_value=25.0, step=0.1, key="precip"
    )
with col2:
    relative_humidity = st.number_input(
        "Relative Humidity (%) [0.00 to 100]", min_value=0.0,
        max_value=100.0, step=0.1, key="rh"
    )

col3, col4, col5 = st.columns(3)
with col3:
    sunshine_hours = st.number_input(
        "Sunshine Hours (hours/day) [0.00 to 12.1]", min_value=0.0,
        max_value=12.1, step=0.1, key="sh"
    )
with col4:
    max_temp = st.number_input(
        "Maximum Temperature (°C) [14 to 35]", min_value=14.0,
        max_value=35.0, step=0.1, key="maxt"
    )
with col5:
    min_temp = st.number_input(
        "Minimum Temperature (°C) [-2 to 15]", min_value=-2.0,
        max_value=15.0, step=0.1, key="mint"
    )

# ==========================================================
# AUTOMATIC TEMPERATURE RANGE
# ==========================================================
temperature_range = round(max_temp - min_temp, 1)
temperature_valid = max_temp >= min_temp

col6, col7 = st.columns(2)
with col6:
    st.text_input(
        "Temperature Range (°C)",
        value=f"{temperature_range:.1f}" if temperature_valid else "—",
        disabled=True,
        help="Automatically calculated: Maximum Temperature - Minimum Temperature.",
        key="temprange_display"
    )
with col7:
    wind_speed = st.number_input(
        "Wind Speed (m/s) [0.0 to 15]", min_value=0.0,
        max_value=15.0, step=0.1, key="ws"
    )

# ==========================================================
# TEMPERATURE VALIDATION
# ==========================================================
if not temperature_valid:
    st.error("Maximum Temperature cannot be lower than Minimum Temperature.")

# ==========================================================
# BUTTONS
# ==========================================================
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    predict_button = st.button("Calculate Global Horizontal Radiation", use_container_width=True)
with btn_col2:
    st.button("Reset Values", on_click=reset_values, use_container_width=True)

# ==========================================================
# PREDICTION
# ==========================================================
if predict_button:
    if not temperature_valid:
        st.error("Please correct the temperature values before generating the prediction.")
    else:
        input_data = {
            "P": precipitation,
            "RH": relative_humidity,
            "SH": sunshine_hours,
            "MaxTem": max_temp,
            "MinTem": min_temp,
            "TemR": temperature_range,
            "WS": wind_speed,
        }

        try:
            api_url = st.secrets["API_URL"]
        except (KeyError, FileNotFoundError):
            st.error(
                "API_URL was not found in Streamlit secrets. "
                "Please add API_URL to your secrets configuration."
            )
            st.stop()

        try:
            with st.spinner("Analyzing meteorological parameters..."):
                response = requests.post(api_url, json=input_data, timeout=60)
                response.raise_for_status()
                result = response.json()

            if "H" not in result:
                raise ValueError("The prediction API did not return the expected 'H' value.")

            st.session_state["prediction_result"] = float(result["H"])
            st.session_state["predicted_area"] = neighbourhood

            st.balloons()

        except requests.exceptions.Timeout:
            st.error("The prediction server took too long to respond. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the prediction server. Please check that your API is running.")
        except requests.exceptions.HTTPError as error:
            st.error(f"The prediction server returned an error: {error}")
        except requests.exceptions.RequestException as error:
            st.error(f"Unable to connect to the prediction service: {error}")
        except (ValueError, TypeError, KeyError) as error:
            st.error(f"Prediction processing error: {error}")

# ==========================================================
# DISPLAY PREDICTION RESULT (PERSISTS ACROSS RERUNS)
# ==========================================================
if st.session_state["prediction_result"] is not None:
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">Predicted Global Horizontal Radiation</div>
            <div class="result-value">{st.session_state["prediction_result"]:.3f}</div>
            <div class="result-unit">kWh/m²/day</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# FOOTER
# ==========================================================
st.divider()
st.markdown(
    """
    <div style="text-align:center; color:#64748b; padding:6px;">
        <b>Bale Zone Solar Radiation Prediction System</b><br>
        Powered by XGBoost Machine Learning<br>
        <small>Deployed by Tolossa Kebede Tulu; Lecturer and Researcher at Madda Walabu University</small>
    </div>
    """,
    unsafe_allow_html=True
)