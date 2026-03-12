import pandas as pd
import numpy as np
import os

def create_demo_files():
    print("Creating demo files...")
    
    # 1. Training Data (Clean)
    train_df = pd.DataFrame({
        'age': [25, 30, 35, 28, 32, 45, 22, 38, 41, 29],
        'income': [50000, 55000, 60000, 52000, 58000, 75000, 45000, 62000, 68000, 53000],
        'category': ['A', 'B', 'A', 'B', 'A', 'C', 'B', 'A', 'C', 'B']
    })
    train_df.to_csv('training_data.csv', index=False)
    print("✅ Created training_data.csv")

    # 2. Good New Data (Similar distribution)
    good_df = pd.DataFrame({
        'age': [27, 31, 29, 33, 40],
        'income': [51000, 56000, 53000, 59000, 69000],
        'category': ['A', 'B', 'A', 'A', 'C']
    })
    good_df.to_csv('new_data_good.csv', index=False)
    print("✅ Created new_data_good.csv")

    # 3. Bad New Data (Issues)
    bad_df = pd.DataFrame({
        'age': [27, -5, 29, 200, 33],  # Negative and extreme age
        'income': [51000, 9999999, 53000, 59000, None],  # Outlier and missing
        'category': ['A', 'X', 'A', 'Z', 'A']  # New categories
    })
    bad_df.to_csv('new_data_bad.csv', index=False)
    print("✅ Created new_data_bad.csv")
    
    print("\nReady for demo recording! Run the following commands:")
    print("---------------------------------------------------")
    print("datalint validate training_data.csv")
    print("datalint profile training_data.csv --learn")
    print("datalint profile new_data_good.csv --profile training_data_profile.json")
    print("datalint profile new_data_bad.csv --profile training_data_profile.json")

if __name__ == "__main__":
    create_demo_files()
