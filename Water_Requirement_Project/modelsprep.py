import pandas as pd 
import numpy as np 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder 
from sklearn.ensemble import RandomForestRegressor 
from sklearn.metrics import mean_absolute_error, mean_squared_error 
import joblib 
import pickle

# Load Dataset
df = pd.read_csv(r"C:\Users\K SAMHITHA\OneDrive\Desktop\Water_Requirement_Project\synthetic_water_management_data.csv")  

# Encode Crop_Type (Categorical Feature)
crop_labels = ["Cotton", "rice", "Sugarcane", "Wheat"]  # Define crop categories
label_encoder = LabelEncoder()
label_encoder.fit(crop_labels)

# Apply transformation to Crop_Type
df['Crop_Type'] = label_encoder.transform(df['Crop_Type'])

# Save LabelEncoder
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

# Define Features and Target Variable
X = df[['Crop_Type', 'temperature', 'Humidity', 'Soil_Moisture', 'Rainfall', 'pH', 'Evaporation_Rate', 'Area']]
y = df['Water_Requirement']

# Split into Training and Testing Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate Model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print(f"Model Performance:\nMean Absolute Error: {mae}\nMean Squared Error: {mse}")

# Save Model and Preprocessing Objects
with open("water_prediction_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print("Model training completed and saved.")
