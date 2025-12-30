"""
Concrete validator implementations.

Each validator extends BaseValidator and has a single responsibility (SRP).
New validators can be added without modifying existing code (OCP).
"""
import numpy as np
import pandas as pd
from .base import BaseValidator, ValidationResult


class MissingValuesValidator(BaseValidator):
    """
    Checks for columns with excessive missing values.
    
    SRP: Only responsible for missing value detection.
    """
    
    def __init__(self, threshold: float = 0.05):
        """
        Args:
            threshold: Maximum allowed missing ratio (default 5%)
        """
        self.threshold = threshold
    
    @property
    def name(self) -> str:
        return "missing_values"
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        missing_ratios = df.isnull().mean()
        problematic = missing_ratios[missing_ratios > self.threshold]
        
        if len(problematic) == 0:
            return ValidationResult(
                name=self.name,
                status="passed",
                message="No excessive missing values found"
            )
        
        return ValidationResult(
            name=self.name,
            status="failed",
            message=f"Found {len(problematic)} columns with >{self.threshold:.0%} missing",
            issues=[
                f"Column '{col}' has {ratio:.1%} missing values"
                for col, ratio in problematic.items()
            ],
            recommendations=[
                f"Consider imputation or removal for '{col}'"
                for col in problematic.index
            ],
            details={'missing_ratios': problematic.to_dict()}
        )


class DataTypeValidator(BaseValidator):
    """
    Checks for mixed data types within columns.
    
    SRP: Only responsible for type consistency detection.
    """
    
    @property
    def name(self) -> str:
        return "data_types"
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        issues = []
        
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_types = df[col].dropna().apply(type).unique()
                if len(unique_types) > 1:
                    issues.append(f"Column '{col}' has mixed types: {[t.__name__ for t in unique_types]}")
        
        if not issues:
            return ValidationResult(
                name=self.name,
                status="passed",
                message="All columns have consistent data types"
            )
        
        return ValidationResult(
            name=self.name,
            status="warning",
            message=f"Found {len(issues)} columns with mixed types",
            issues=issues,
            recommendations=["Consider explicit type conversion or data cleaning"]
        )


class OutlierValidator(BaseValidator):
    """
    Detects statistical outliers using IQR method.
    
    SRP: Only responsible for outlier detection.
    """
    
    def __init__(self, iqr_multiplier: float = 1.5, threshold: float = 0.05):
        """
        Args:
            iqr_multiplier: IQR multiplier for bounds (default 1.5)
            threshold: Maximum allowed outlier ratio (default 5%)
        """
        self.iqr_multiplier = iqr_multiplier
        self.threshold = threshold
    
    @property
    def name(self) -> str:
        return "outliers"
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_info = {}
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower = Q1 - self.iqr_multiplier * IQR
            upper = Q3 + self.iqr_multiplier * IQR
            
            outlier_mask = (df[col] < lower) | (df[col] > upper)
            outlier_ratio = outlier_mask.mean()
            
            if outlier_ratio > self.threshold:
                outlier_info[col] = {
                    'ratio': outlier_ratio,
                    'bounds': (lower, upper)
                }
        
        if not outlier_info:
            return ValidationResult(
                name=self.name,
                status="passed",
                message="Outlier levels are within acceptable range"
            )
        
        return ValidationResult(
            name=self.name,
            status="warning",
            message=f"Found {len(outlier_info)} columns with excessive outliers",
            issues=[
                f"Column '{col}' has {info['ratio']:.1%} outliers"
                for col, info in outlier_info.items()
            ],
            recommendations=[
                f"Consider winsorization or investigation for '{col}'"
                for col in outlier_info.keys()
            ],
            details={'outlier_info': outlier_info}
        )


class CorrelationValidator(BaseValidator):
    """
    Detects highly correlated feature pairs.
    
    SRP: Only responsible for correlation detection.
    """
    
    def __init__(self, threshold: float = 0.95):
        """
        Args:
            threshold: Correlation coefficient threshold (default 0.95)
        """
        self.threshold = threshold
    
    @property
    def name(self) -> str:
        return "correlations"
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return ValidationResult(
                name=self.name,
                status="passed",
                message="Not enough numeric columns for correlation analysis"
            )
        
        corr_matrix = numeric_df.corr()
        high_corr_pairs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = abs(corr_matrix.iloc[i, j])
                if corr_val > self.threshold:
                    high_corr_pairs.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        corr_val
                    ))
        
        if not high_corr_pairs:
            return ValidationResult(
                name=self.name,
                status="passed",
                message="No highly correlated feature pairs found"
            )
        
        return ValidationResult(
            name=self.name,
            status="warning",
            message=f"Found {len(high_corr_pairs)} highly correlated pairs",
            issues=[
                f"'{p[0]}' and '{p[1]}' correlation: {p[2]:.3f}"
                for p in high_corr_pairs
            ],
            recommendations=["Consider removing redundant features or using PCA"],
            details={'correlated_pairs': high_corr_pairs}
        )


class ConstantColumnValidator(BaseValidator):
    """
    Detects columns with zero variance (constant values).
    
    SRP: Only responsible for constant column detection.
    """
    
    @property
    def name(self) -> str:
        return "constant_columns"
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        constant_cols = [
            col for col in df.columns
            if df[col].nunique(dropna=True) <= 1
        ]
        
        if not constant_cols:
            return ValidationResult(
                name=self.name,
                status="passed",
                message="No constant columns found"
            )
        
        return ValidationResult(
            name=self.name,
            status="failed",
            message=f"Found {len(constant_cols)} constant columns",
            issues=[f"Column '{col}' has constant value" for col in constant_cols],
            recommendations=[
                f"Remove '{col}' as it provides no predictive information"
                for col in constant_cols
            ],
            details={'constant_columns': constant_cols}
        )


# Factory function for convenience
def get_default_validators() -> list[BaseValidator]:
    """
    Returns the standard set of validators with default settings.
    
    Applying KISS: Simple factory provides sensible defaults.
    """
    return [
        MissingValuesValidator(),
        DataTypeValidator(),
        OutlierValidator(),
        CorrelationValidator(),
        ConstantColumnValidator(),
    ]