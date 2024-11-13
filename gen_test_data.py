import pandas as pd
import numpy as np
np.random.seed(42)

# Helper function to generate dates in a year
def generate_dates(year, n):
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'
    return pd.date_range(start=start_date, end=end_date, periods=n)

# Base columns (2018-2020)
def create_base_data(year, n_samples=1000):
    df = pd.DataFrame({
        'patient_id': range(1, n_samples + 1),
        'age': np.random.randint(18, 90, n_samples),
        'blood_pressure': np.random.randint(90, 180, n_samples),  # This will later split into systolic/diastolic
        'glucose_level': np.random.normal(100, 15, n_samples),    # This will later split into fasting/post-meal
        'cholesterol': np.random.normal(200, 30, n_samples),      # This will later split into HDL/LDL
        'weight_kg': np.random.normal(70, 15, n_samples),
        'visit_date': generate_dates(year, n_samples)
    })
    return df

# 2021-2022 data with split blood pressure
def create_extended_data_1(year, n_samples=1000):
    df = pd.DataFrame({
        'patient_id': range(1, n_samples + 1),
        'age': np.random.randint(18, 90, n_samples),
        'systolic_bp': np.random.randint(100, 160, n_samples),    # Split from blood_pressure
        'diastolic_bp': np.random.randint(60, 100, n_samples),    # Split from blood_pressure
        'glucose_level': np.random.normal(100, 15, n_samples),
        'cholesterol': np.random.normal(200, 30, n_samples),
        'weight_kg': np.random.normal(70, 15, n_samples),
        'bmi': np.random.normal(25, 5, n_samples),                # New column
        'visit_date': generate_dates(year, n_samples)
    })
    return df

# 2023 data with split blood pressure and glucose
def create_extended_data_2(year, n_samples=1000):
    df = pd.DataFrame({
        'patient_id': range(1, n_samples + 1),
        'age': np.random.randint(18, 90, n_samples),
        'systolic_bp': np.random.randint(100, 160, n_samples),
        'diastolic_bp': np.random.randint(60, 100, n_samples),
        'fasting_glucose': np.random.normal(95, 10, n_samples),    # Split from glucose_level
        'postmeal_glucose': np.random.normal(120, 20, n_samples),  # Split from glucose_level
        'cholesterol': np.random.normal(200, 30, n_samples),
        'weight_kg': np.random.normal(70, 15, n_samples),
        'bmi': np.random.normal(25, 5, n_samples),
        'visit_date': generate_dates(year, n_samples)
    })
    return df

# Create and save all datasets
df_2018 = create_base_data(2018)
df_2020 = create_base_data(2020)
df_2021 = create_extended_data_1(2021)
df_2022 = create_extended_data_1(2022)
df_2023 = create_extended_data_2(2023)

# Save to CSV files
df_2018.to_csv('data/health_data_2018.csv', index=False)
df_2020.to_csv('data/health_data_2020.csv', index=False)
df_2021.to_csv('data/health_data_2021.csv', index=False)
df_2022.to_csv('data/health_data_2022.csv', index=False)
df_2023.to_csv('data/health_data_2023.csv', index=False)

# Print column evolution information
# print("\nColumn Evolution:\n")
# print("2018-2020 Columns:")
# print(df_2018.columns.tolist())
# print("\n2021-2022 Columns (Added BMI, Split Blood Pressure):")
# print(df_2021.columns.tolist())
# print("\n2023 Columns (Split Glucose):")
# print(df_2023.columns.tolist())