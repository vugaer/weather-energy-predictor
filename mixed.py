import pandas as pd
import xgboost as xgb
import pickle
import requests
from datetime import datetime

# Function to fetch weather data from WeatherAPI
def fetch_weather_data(latitude, longitude, api_key='7ad5ad710b31461d827104159242710', forecast=False):
    if forecast:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={latitude},{longitude}&days=2&aqi=no&alerts=no"
    else:
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={latitude},{longitude}&aqi=no"
    
    response = requests.get(url)
    data = response.json()
    return data

# Combined function to predict current or tomorrow's weather
def predict_weather(latitude, longitude, period='current', hour=None, model_path="xgboost_model.pkl"):
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)  # Load your model

    if period == 'current':
        weather_data = fetch_weather_data(latitude, longitude, forecast=False)  # Fetch current weather data
        if hour is None:
            hour = pd.to_datetime(weather_data['location']['localtime']).hour  # Get the current hour if not specified

        # Extract relevant data from the API response for current weather
        sky_condition_percent = weather_data['current']['cloud']
        visibility = weather_data['current']['vis_miles']
        temperature_c = weather_data['current']['temp_c']
        dew_point_c = weather_data['current']['dewpoint_c']
        relative_humidity = weather_data['current']['humidity']
        wind_speed_mph = weather_data['current']['wind_mph']
        station_pressure_inchHg = weather_data['current']['pressure_in']
        altimeter = weather_data['current']['pressure_mb'] / 33.8639  # Convert mb to inchHg

    elif period == 'tomorrow':
        weather_data = fetch_weather_data(latitude, longitude, forecast=True)  # Fetch tomorrow's forecast data
        if hour is None:
            hour = 0  # Default to midnight if hour is not specified

        # Extract relevant data from the forecast response for tomorrow
        tomorrow_forecast = weather_data['forecast']['forecastday'][1]  # Index 1 is tomorrow
        sky_condition_percent = tomorrow_forecast['day'].get('cloud', 0)  # Cloud cover percentage
        visibility = tomorrow_forecast['day'].get('avgvis_miles', 0)  # Average visibility for the day
        temperature_c = tomorrow_forecast['day'].get('avgtemp_c', 0)  # Average temperature for the day
        dew_point_c = tomorrow_forecast['day'].get('avghumidity', 0)  # Humidity as a proxy for dew point
        relative_humidity = tomorrow_forecast['day'].get('avghumidity', 0)  # Average relative humidity for the day
        wind_speed_mph = tomorrow_forecast['day'].get('maxwind_mph', 0)  # Maximum wind speed for the day
        station_pressure_inchHg = tomorrow_forecast['day'].get('pressure_in', 0)  # Pressure in inches of mercury
        altimeter = tomorrow_forecast['day'].get('pressure_mb', 0) / 33.8639  # Convert mb to inchHg

    else:
        raise ValueError("Invalid period. Choose 'current' or 'tomorrow'.")

    # Prepare the input data as a DataFrame
    input_data = pd.DataFrame({
        'Hour': [hour],
        'Sky condition %': [sky_condition_percent],
        'Visibility': [visibility],
        'Temperature C': [temperature_c],
        'Dew point C': [dew_point_c],
        'Relative humidity %': [relative_humidity],
        'Wind speed mph': [wind_speed_mph],
        'Station pressure inchHg': [station_pressure_inchHg],
        'Altimeter': [altimeter]
    })

    # Make predictions directly on the DataFrame without DMatrix
    predictions = model.predict(input_data)

    # Output the predictions
    return predictions

# Example usage
BAKU_LATITUDE = 40.4093
BAKU_LONGITUDE = 49.8671

# # Predict current weather
# print("Current Weather Prediction:", predict_weather(BAKU_LATITUDE, BAKU_LONGITUDE))

# # Predict tomorrow's weather at 8 AM
# print("Tomorrow's Weather Prediction at 8 AM:", predict_weather(BAKU_LATITUDE, BAKU_LONGITUDE, period='tomorrow', hour=8))
# Function to calculate power values based on weather predictions
def calculate_power_values(latitude, longtitude, period='current'):
    power_values = []
    weather_values = []

    for i in range(0, 25, 8):
        prediction = predict_weather(latitude, longtitude, hour=i, period=period)
        weather_values.append(float(prediction[0]))
    for j in range(len(weather_values) - 1):
        power_value = 4 * (weather_values[j] + weather_values[j + 1])
        power_values.append(float(power_value))

    return power_values

# Main calculation and output
# current_values = calculate_power_values(period='current', latitude, longtitude)
# tomorrow_values = calculate_power_values(period='tomorrow', latitude, longtitude)
