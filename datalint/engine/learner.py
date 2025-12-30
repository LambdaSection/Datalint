import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from scipy import stats


@dataclass
class DataProfile:
    """Statistical profile of a clean dataset."""

    column_profiles: Dict[str, dict]
    correlations: Dict[tuple, float]
    sample_size: int

    def to_dict(self) -> dict:
        return {
            "column_profiles": self.column_profiles,
            "correlations": {
                json.dumps([k[0], k[1]]): v for k, v in self.correlations.items()
            },
            "sample_size": self.sample_size,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DataProfile":
        """Deserialize from dictionary."""
        correlations = {tuple(json.loads(k)): v for k, v in d["correlations"].items()}
        return cls(
            column_profiles=d["column_profiles"],
            correlations=correlations,
            sample_size=d["sample_size"],
        )


class RuleLearner:
    """Learns validation rules from clean datasets."""

    def learn_from_clean_data(self, df: pd.DataFrame) -> DataProfile:
        """
        Analyze clean dataset to create statistical profile.

        Reference: Automated data profiling techniques
        "Data Profiling" by Olson (2003)
        """
        profiles = {}

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                profiles[col] = self._learn_numeric_profile(df[col])
            else:
                profiles[col] = self._learn_categorical_profile(df[col])

        # Learn correlation patterns
        numeric_df = df.select_dtypes(include=[np.number])
        correlations = {}
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.3:  # Significant correlations
                        correlations[
                            (corr_matrix.columns[i], corr_matrix.columns[j])
                        ] = corr_val

        return DataProfile(
            column_profiles=profiles, correlations=correlations, sample_size=len(df)
        )

    def _learn_numeric_profile(self, series: pd.Series) -> dict:
        """Learn statistical profile for numeric column."""
        clean_series = series.dropna()
        return {
            "type": "numeric",
            "mean": clean_series.mean(),
            "std": clean_series.std(),
            "min": clean_series.min(),
            "max": clean_series.max(),
            "quartiles": clean_series.quantile([0.25, 0.5, 0.75]).to_dict(),
            "outlier_bounds": self._calculate_outlier_bounds(clean_series),
        }

    def _learn_categorical_profile(self, series: pd.Series) -> dict:
        """Learn profile for categorical column."""
        clean_series = series.dropna()
        value_counts = clean_series.value_counts()
        return {
            "type": "categorical",
            "unique_count": clean_series.nunique(),
            "most_common": value_counts.head(5).to_dict(),
            "missing_ratio": series.isnull().mean(),
        }

    def _calculate_outlier_bounds(self, series: pd.Series) -> tuple:
        """Calculate outlier bounds using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        return (Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)

    def validate_against_profile(self, df: pd.DataFrame, profile: DataProfile) -> dict:
        """
        Validate new data against learned statistical profile.

        Reference: Statistical process control methods
        "Introduction to Statistical Quality Control" by Montgomery (2009)
        """
        results = {"overall_score": 0.0, "column_results": {}, "anomalies": []}

        total_checks = 0
        passed_checks = 0

        for col in df.columns:
            if col in profile.column_profiles:
                col_profile = profile.column_profiles[col]
                col_result = self._validate_column(df[col], col_profile)
                results["column_results"][col] = col_result

                total_checks += col_result["checks_run"]
                passed_checks += col_result["checks_passed"]

                if not col_result["passed"]:
                    results["anomalies"].extend(col_result["issues"])

        results["overall_score"] = (
            passed_checks / total_checks if total_checks > 0 else 0.0
        )
        results["passed"] = results["overall_score"] > 0.8  # 80% threshold

        return results

    def _validate_column(self, series: pd.Series, profile: dict) -> dict:
        """Validate single column against its profile."""
        result = {"checks_run": 0, "checks_passed": 0, "issues": [], "passed": True}

        if profile["type"] == "numeric":
            # Check distribution similarity using statistical tests
            result["checks_run"] += 1
            if self._check_distribution_similarity(series, profile):
                result["checks_passed"] += 1
            else:
                result["issues"].append(f"Distribution differs from training data")

            # Check for outliers
            result["checks_run"] += 1
            outlier_ratio = self._calculate_outlier_ratio(series, profile)
            if outlier_ratio < 0.05:  # Less than 5% outliers
                result["checks_passed"] += 1
            else:
                result["issues"].append(f"High outlier ratio: {outlier_ratio:.1%}")

        elif profile["type"] == "categorical":
            # Check categorical distribution
            result["checks_run"] += 1
            if self._check_categorical_similarity(series, profile):
                result["checks_passed"] += 1
            else:
                result["issues"].append(
                    "Categorical distribution differs significantly"
                )

        result["passed"] = result["checks_passed"] == result["checks_run"]
        return result

    def _check_distribution_similarity(self, series: pd.Series, profile: dict) -> bool:
        """
        Check if numeric distribution is similar to training data.
        Uses a simple range check with tolerance.
        """
        clean_series = series.dropna()
        if len(clean_series) == 0:
            return False

        # Check if values are within expected range (with 20% tolerance)
        tolerance = 0.2
        expected_min = profile["min"]
        expected_max = profile["max"]
        range_size = expected_max - expected_min if expected_max != expected_min else 1

        actual_min = clean_series.min()
        actual_max = clean_series.max()

        lower_ok = actual_min >= expected_min - (range_size * tolerance)
        upper_ok = actual_max <= expected_max + (range_size * tolerance)

        return lower_ok and upper_ok

    def _calculate_outlier_ratio(self, series: pd.Series, profile: dict) -> float:
        """
        Calculate ratio of values outside the learned outlier bounds.
        """
        clean_series = series.dropna()
        if len(clean_series) == 0:
            return 0.0

        lower_bound, upper_bound = profile["outlier_bounds"]
        outliers = clean_series[
            (clean_series < lower_bound) | (clean_series > upper_bound)
        ]
        return len(outliers) / len(clean_series)

    def _check_categorical_similarity(self, series: pd.Series, profile: dict) -> bool:
        """
        Check if categorical values match expected categories.
        Returns False if >10% of values are new categories.
        """
        clean_series = series.dropna()
        if len(clean_series) == 0:
            return True

        known_categories = set(profile["most_common"].keys())
        actual_categories = set(clean_series.unique())

        # Check what percentage of values are in unknown categories
        unknown_mask = ~clean_series.isin(known_categories)
        unknown_ratio = unknown_mask.sum() / len(clean_series)

        return unknown_ratio < 0.1  # Less than 10% unknown is acceptable
