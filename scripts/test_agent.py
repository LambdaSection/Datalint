import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datalint.engine.validators import get_default_validators
from datalint.engine.fixers import DropMissingRowsFixer, FillMissingMeanFixer, RemoveOutliersFixer
from datalint.engine.agent import DataAgent
from datalint.engine.base import ValidationRunner

def test_agent_autofix():
    print("Test: Agent Auto-Fix Capabilities")
    print("=================================")
    
    # 1. Create Dirty Data
    # - Age: Missing values
    # - Salary: Outliers
    # - Category: Clean
    df = pd.DataFrame({
        'age': [25, 30, np.nan, 28, 35, np.nan], 
        'salary': [50000, 60000, 55000, 1000000, 52000, 58000], # 1M is outlier
        'category': ['A', 'B', 'A', 'B', 'B', 'A']
    })
    
    print("\nOriginal Data:")
    print(df)
    
    # 2. Setup Agent
    validators = get_default_validators()
    runner = ValidationRunner(validators)
    
    # Strategy: Fix missing values by dropping, fix outliers by removing
    fixers = [
        DropMissingRowsFixer(),
        # FillMissingMeanFixer(), # Could use this instead
        RemoveOutliersFixer()
    ]
    
    agent = DataAgent(runner, fixers)
    
    # 3. Run Agent
    print("\nStarting Agent Cleaning Loop...")
    clean_df, audit_log = agent.clean(df)
    
    # 4. Result
    print("\nCleaned Data:")
    print(clean_df)
    
    print("\nAudit Log:")
    for entry in audit_log:
        print(f"[{entry.step}] {entry.action}: {entry.description}")
        
    # 5. Assertions
    assert len(clean_df) < len(df), "Should have dropped rows"
    assert clean_df['age'].isnull().sum() == 0, "Should have no missing values"
    assert clean_df['salary'].max() < 200000, "Should have removed outlier salary"
    
    print("\n✅ Agent Test Passed!")

if __name__ == "__main__":
    test_agent_autofix()
