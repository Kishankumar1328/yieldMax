import streamlit as st
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
import plotly.graph_objs as go

# Crop categories
food_grains = [
    'Wheat', 'Rice', 'Corn', 'Barley', 'Soybean', 'Millet', 'Sorghum',
    'Oats', 'Rye', 'Buckwheat', 'Quinoa', 'Teff', 'Lentils', 'Chickpeas',
    'Black Gram', 'Green Gram', 'Pigeon Pea', 'Peanuts', 'Sesame', 'Mustard'
]

fruits = [
    'Apple', 'Banana', 'Mango', 'Orange', 'Grapes', 'Pineapple', 'Papaya',
    'Watermelon', 'Strawberry', 'Peach', 'Guava', 'Pomegranate', 'Cherry',
    'Blueberry', 'Lemon', 'Lime', 'Coconut', 'Kiwi', 'Fig', 'Avocado'
]

vegetables = [
    'Potato', 'Tomato', 'Onion', 'Carrot', 'Cabbage', 'Broccoli', 'Cauliflower',
    'Spinach', 'Lettuce', 'Pumpkin', 'Zucchini', 'Cucumber', 'Eggplant',
    'Bell Pepper', 'Chili', 'Sweet Corn', 'Okra', 'Peas', 'Radish', 'Turnip',
    'Beetroot', 'Garlic', 'Ginger', 'Mint', 'Basil', 'Parsley', 'Coriander',
    'Turmeric', 'Celery'
]

# Combine all crop types
all_crops = food_grains + fruits + vegetables


# Function to generate training data based on crop type
def generate_crop_data(crop_types):
    data = {
        'Crop_Type': crop_types,
        'Soil_Type': np.random.choice(['Sandy', 'Clay', 'Loamy', 'Silty'], len(crop_types)),
        'pH_Level': [
            np.round(np.random.uniform(6.0, 7.5), 2) if crop in food_grains else
            np.round(np.random.uniform(5.5, 6.5), 2) if crop in fruits else
            np.round(np.random.uniform(5.5, 7.0), 2)
            for crop in crop_types
        ],
        'Moisture_Content (%)': np.round(np.random.uniform(10, 40, len(crop_types)), 2),
        'Weather_Condition': np.random.choice(['Dry', 'Wet', 'Humid', 'Cold'], len(crop_types)),
        'Temperature (°C)': [
            np.round(np.random.uniform(20, 30), 2) if crop in food_grains else
            np.round(np.random.uniform(25, 35), 2) if crop in fruits else
            np.round(np.random.uniform(15, 25), 2)
            for crop in crop_types
        ],
        'Rainfall (mm)': [
            np.round(np.random.uniform(150, 300), 2) if crop in food_grains else
            np.round(np.random.uniform(100, 250), 2) if crop in fruits else
            np.round(np.random.uniform(50, 200), 2)
            for crop in crop_types
        ],
        'Fertilizer_Recommendation': [
            'Organic' if crop in food_grains else
            'Inorganic' if crop in fruits else
            'Mixed'
            for crop in crop_types
        ],
        'Irrigation_Recommendation': [
            'Drip' if crop in food_grains else
            'Sprinkler' if crop in fruits else
            'Flood'
            for crop in crop_types
        ]
    }

    return pd.DataFrame(data)


# Function to train models
def prepare_models(crop_category=None):
    # Select crop types based on category
    if crop_category == 'Food Grains':
        selected_crops = food_grains
    elif crop_category == 'Fruits':
        selected_crops = fruits
    elif crop_category == 'Vegetables':
        selected_crops = vegetables
    else:  # All crops
        selected_crops = all_crops

    # Generate data for selected crops
    crop_types = np.random.choice(selected_crops, 1000)
    df = generate_crop_data(crop_types)

    # Preprocess the data
    label_encoders = {}
    for column in ['Soil_Type', 'Weather_Condition', 'Crop_Type']:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le

    features = ['Soil_Type', 'pH_Level', 'Moisture_Content (%)', 'Weather_Condition', 'Temperature (°C)',
                'Rainfall (mm)']

    X = df[features]
    y_fertilizer = df['Fertilizer_Recommendation']
    y_irrigation = df['Irrigation_Recommendation']

    # Train models
    dt_fertilizer = lgb.LGBMClassifier(random_state=42)
    dt_fertilizer.fit(X, y_fertilizer)

    dt_irrigation = lgb.LGBMClassifier(random_state=42)
    dt_irrigation.fit(X, y_irrigation)

    return dt_fertilizer, dt_irrigation, label_encoders, selected_crops


# Streamlit App
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Crop Recommendation System",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 30px;
    }
    .sub-header {
        color: #34495E;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #3498DB;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980B9;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main title
    st.markdown('<h1 class="main-title">🌾 Intelligent Crop Recommendation System</h1>', unsafe_allow_html=True)

    # Crop Category Selection
    crop_category = st.selectbox(
        'Select Crop Category',
        ['All Crops', 'Food Grains', 'Fruits', 'Vegetables']
    )

    # Prepare models based on selected category
    model_fertilizer, model_irrigation, label_encoders, selected_crops = prepare_models(crop_category)

    # Sidebar for input
    st.sidebar.header('🌿 Crop Condition Parameters')

    # Crop Selection
    selected_crop = st.sidebar.selectbox('Select Specific Crop', selected_crops)

    # Input features
    soil_type = st.sidebar.selectbox('Soil Type', ['Sandy', 'Clay', 'Loamy', 'Silty'])
    ph_level = st.sidebar.slider('pH Level', 5.0, 7.5, 6.5)
    moisture = st.sidebar.slider('Moisture Content (%)', 10.0, 40.0, 25.0)
    weather = st.sidebar.selectbox('Weather Condition', ['Dry', 'Wet', 'Humid', 'Cold'])
    temperature = st.sidebar.slider('Temperature (°C)', 10.0, 40.0, 25.0)
    rainfall = st.sidebar.slider('Rainfall (mm)', 50.0, 300.0, 150.0)

    # Prepare input data for prediction
    input_data = pd.DataFrame({
        'Soil_Type': [label_encoders['Soil_Type'].transform([soil_type])[0]],
        'pH_Level': [ph_level],
        'Moisture_Content (%)': [moisture],
        'Weather_Condition': [label_encoders['Weather_Condition'].transform([weather])[0]],
        'Temperature (°C)': [temperature],
        'Rainfall (mm)': [rainfall]
    })

    # Prediction button
    if st.sidebar.button('Get Recommendations'):
        # Make predictions
        predicted_fertilizer = model_fertilizer.predict(input_data)[0]
        predicted_irrigation = model_irrigation.predict(input_data)[0]

        # Display results
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<h2 class="sub-header">🌱 Fertilizer Recommendation</h2>', unsafe_allow_html=True)
            st.info(f"Crop: {selected_crop}")
            st.info(f"Fertilizer Type: {predicted_fertilizer}")

            # Create pie chart for fertilizer recommendation
            fig_fertilizer = px.pie(
                names=['Recommended Fertilizer'],
                values=[1],
                title=f'Fertilizer Recommendation for {selected_crop}'
            )
            st.plotly_chart(fig_fertilizer)

        with col2:
            st.markdown('<h2 class="sub-header">💧 Irrigation Recommendation</h2>', unsafe_allow_html=True)
            st.info(f"Crop: {selected_crop}")
            st.info(f"Irrigation Method: {predicted_irrigation}")

            # Create pie chart for irrigation recommendation
            fig_irrigation = px.pie(
                names=['Recommended Irrigation'],
                values=[1],
                title=f'Irrigation Method for {selected_crop}'
            )
            st.plotly_chart(fig_irrigation)

        # Additional insights section
        st.markdown('<h2 class="sub-header">🌍 Crop Insights</h2>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.metric(label="Recommended pH Range", value=f"{ph_level:.2f}")
            st.metric(label="Moisture Requirement", value=f"{moisture}%")

        with col4:
            st.metric(label="Temperature", value=f"{temperature}°C")
            st.metric(label="Rainfall Requirement", value=f"{rainfall} mm")


# Run the app
if __name__ == '__main__':
    main()
