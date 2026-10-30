
import streamlit as st
import requests

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Bale Zone Solar Radiation Predictor",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f5f8fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #15365c;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 16px;
        color: #64748b;
        text-align: center;
        margin-bottom: 25px;
    }

    .section-title {
        color: #15365c;
        font-size: 20px;
        font-weight: 700;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
        margin-top: 15px;
    }

    .result-card {
        background: linear-gradient(135deg, #0f766e, #164e63);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-top: 20px;
    }

    .result-label {
        font-size: 17px;
        color: #d1fae5;
    }

    .result-value {
        font-size: 38px;
        font-weight: 800;
        color: white;
    }

    .result-unit {
        font-size: 15px;
        color: #ccfbf1;
    }

    div.stButton > button {
        background-color: #0f766e;
        color: white;
        font-size: 17px;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px 25px;
        border: none;
        width: 100%;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #115e59;
        color: white;
    }

    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------
st.markdown(
    '<div class="main-title">☀️ Bale Zone Solar Radiation Predictor</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Global Horizontal Radiation (GHR) Prediction '
    'Using an XGBoost Machine Learning Model'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# SIDEBAR INFORMATION
# --------------------------------------------------
with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/869/869869.png",
        width=85
    )

    st.title("About the Application")

    st.write(
        """
        This application predicts Global Horizontal
        Radiation (GHR) using meteorological parameters
        and an XGBoost machine learning model.
        """
    )

    st.info(
        """
        **Study Area**

        - Bale Robe
        - Ginir
        - Dello Mena
        """
    )

    st.caption("Solar Radiation Prediction System | XGBoost")


# --------------------------------------------------
# LOCATION SELECTION
# --------------------------------------------------
st.markdown(
    '<div class="section-title">📍 Study Area Information</div>',
    unsafe_allow_html=True
)

neigh_list = ["Bale Robe", "Ginir", "Dello Mena"]

neighbourhood = st.selectbox(
    "Select your study area",
    options=neigh_list,
    help="Choose the town for which you want to predict GHR."
)

st.success(f"Selected study area: {neighbourhood}")


# --------------------------------------------------
# METEOROLOGICAL INPUTS
# --------------------------------------------------
st.markdown(
    '<div class="section-title">🌦️ Meteorological Parameters</div>',
    unsafe_allow_html=True
)

st.caption(
    "Enter the meteorological data below to estimate "
    "Global Horizontal Radiation."
)

# Precipitation and humidity
st.markdown("**Atmospheric Conditions**")

col1, col2 = st.columns(2)

with col1:
    precipitation = st.number_input(
        "Precipitation (mm/day)",
        min_value=0.0,
        max_value=1500.0,
        value=0.0,
        step=0.1,
        help="Daily precipitation amount."
    )

with col2:
    REHumidity = st.number_input(
        "Relative Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
        help="Daily relative humidity."
    )

st.markdown("**Solar and Temperature Conditions**")

col3, col4, col5 = st.columns(3)

with col3:
    SunshineHours = st.number_input(
        "Sunshine Hours (hours/day)",
        min_value=0.0,
        max_value=24.0,
        value=0.0,
        step=0.1
    )

with col4:
    MaxTemp = st.number_input(
        "Maximum Temperature (°C)",
        min_value=-15.0,
        max_value=45.0,
        value=0.0,
        step=0.1
    )

with col5:
    MinTemp = st.number_input(
        "Minimum Temperature (°C)",
        min_value=-15.0,
        max_value=45.0,
        value=0.0,
        step=0.1
    )

st.markdown("**Wind and Temperature Range**")

col6, col7 = st.columns(2)

with col6:
    TempR = st.number_input(
        "Temperature Range (°C)",
        min_value=0.0,
        max_value=60.0,
        value=0.0,
        step=0.1,
        help="Difference between maximum and minimum temperature."
    )

with col7:
    WindSeed = st.number_input(
        "Wind Speed (m/s)",
        min_value=0.0,
        max_value=25.0,
        value=0.0,
        step=0.1
    )


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------
st.divider()

st.markdown(
    '<div class="section-title">🔍 Generate Prediction</div>',
    unsafe_allow_html=True
)

st.write(
    "Please review your meteorological inputs before "
    "generating the solar radiation prediction."
)

calculator = st.button(
    "☀️ Calculate Global Horizontal Radiation",
    use_container_width=True
)

if calculator:

    # Input validation
    if MaxTemp < MinTemp:
        st.error(
            "Maximum temperature cannot be lower than "
            "minimum temperature. Please correct your inputs."
        )

    elif round(MaxTemp - MinTemp, 1) != round(TempR, 1):
        st.warning(
            "The entered temperature range does not match "
            "Maximum Temperature minus Minimum Temperature."
        )

    else:

        input_data = {
            "P": precipitation,
            "RH": REHumidity,
            "SH": SunshineHours,
            "MaxTem": MaxTemp,
            "MinTem": MinTemp,
            "TemR": TempR,
            "WS": WindSeed
        }

        url = st.secrets["API_URL"]

        try:
            with st.spinner(
                "Analyzing meteorological parameters and generating prediction..."
            ):

                response = requests.post(
                    url,
                    json=input_data,
                    timeout=60
                )

                response.raise_for_status()

                result = response.json()

                if "H" not in result:
                    raise ValueError(
                        "The prediction service returned an unexpected response."
                    )

                GlobalHR = float(result["H"])

            # Display prediction
            st.balloons()

            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-label">
                        Predicted Global Horizontal Radiation
                    </div>
                    <div class="result-value">
                        {GlobalHR:.3f}
                    </div>
                    <div class="result-unit">
                        kWh/m²/day
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.success(
                f"Prediction successfully generated for {neighbourhood}."
            )

            # Display input summary
            with st.expander("View Prediction Input Summary"):
                st.json({
                    "Study Area": neighbourhood,
                    "Precipitation": precipitation,
                    "Relative Humidity": REHumidity,
                    "Sunshine Hours": SunshineHours,
                    "Maximum Temperature": MaxTemp,
                    "Minimum Temperature": MinTemp,
                    "Temperature Range": TempR,
                    "Wind Speed": WindSeed
                })

        except requests.exceptions.Timeout:
            st.error(
                "The prediction server took too long to respond. "
                "Please try again."
            )

        except requests.exceptions.RequestException as e:
            st.error(
                f"Unable to connect to the prediction service: {e}"
            )

        except (ValueError, KeyError, TypeError) as e:
            st.error(f"Prediction processing error: {e}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#64748b; padding:15px;">
        <b>Bale Zone Solar Radiation Prediction System</b><br>
        Powered by XGBoost Machine Learning<br>
        <small>Global Horizontal Radiation (GHR) Prediction</small>
    </div>
    """,
    unsafe_allow_html=True
)
