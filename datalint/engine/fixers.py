"""
DataLint Fixers - logic for automatically resolving data quality issues.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Any

from .base import ValidationResult

class BaseFixer(ABC):
    """
    Abstract base class for all data fixers.
    
    A Fixer is responsible for resolving a specific type of ValidationResult.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this fixer."""
        pass
        
    @abstractmethod
    def can_fix(self, result: ValidationResult) -> bool:
        """
        Check if this fixer can handle the given validation failure.
        
        Args:
            result: The validation failure to check.
            
        Returns:
            True if this fixer knows how to handle this error type.
        """
        pass
        
    @abstractmethod
    def apply(self, df: pd.DataFrame, result: ValidationResult) -> pd.DataFrame:
        """
        Apply the fix to the dataframe.
        
        Args:
            df: The dataframe to clean.
            result: The specific validation result containing failure details.
            
        Returns:
            A new, cleaned DataFrame.
        """
        pass

class DropMissingRowsFixer(BaseFixer):
    """Fixes missing values by dropping rows."""
    
    @property
    def name(self) -> str:
        return "drop_missing_rows"
        
    def can_fix(self, result: ValidationResult) -> bool:
        return result.name == "missing_values" and result.status == "failed"
        
    def apply(self, df: pd.DataFrame, result: ValidationResult) -> pd.DataFrame:
        # Get columns with missing values from details or assume all
        if "missing_ratios" in result.details:
            cols_to_fix = list(result.details["missing_ratios"].keys())
            return df.dropna(subset=cols_to_fix)
        return df.dropna()

class FillMissingMeanFixer(BaseFixer):
    """Fixes missing numeric values by filling with mean."""
    
    @property
    def name(self) -> str:
        return "fill_missing_mean"
        
    def can_fix(self, result: ValidationResult) -> bool:
        return result.name == "missing_values" and result.status == "failed"
        
    def apply(self, df: pd.DataFrame, result: ValidationResult) -> pd.DataFrame:
        df_clean = df.copy()
        cols_to_fix = result.details.get("missing_ratios", {}).keys()
        
        for col in cols_to_fix:
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                mean_val = df_clean[col].mean()
                df_clean[col] = df_clean[col].fillna(mean_val)
                
        return df_clean

class RemoveOutliersFixer(BaseFixer):
    """Fixes outliers by removing rows outside bounds."""
    
    @property
    def name(self) -> str:
        return "remove_outliers"
        
    def can_fix(self, result: ValidationResult) -> bool:
        return result.name == "outliers" and result.status == "warning"
        
    def apply(self, df: pd.DataFrame, result: ValidationResult) -> pd.DataFrame:
        df_clean = df.copy()
        outlier_info = result.details.get("outlier_info", {})
        
        for col, info in outlier_info.items():
            lower, upper = info["bounds"]
            # Filter to keep only values within bounds (or NaN, which this fixer ignores)
            mask = (df_clean[col] >= lower) & (df_clean[col] <= upper) | df_clean[col].isna()
            df_clean = df_clean[mask]
            
        return df_clean
