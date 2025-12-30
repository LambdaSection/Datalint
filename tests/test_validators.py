import pytest
import pandas as pd
import numpy as np
from datalint.engine.validators import (
    MissingValuesValidator, DataTypeValidator,
    OutlierValidator, CorrelationValidator
)

class TestMissingValues:
    def test_no_missing_values(self):
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        validator = MissingValuesValidator()
        result = validator.validate(df)
        assert result.passed is True
        assert len(result.issues) == 0

    def test_excessive_missing_values(self):
        df = pd.DataFrame({
            'good_col': [1, 2, 3, 4, 5],
            'bad_col': [1, None, None, None, None]  # 60% missing
        })
        validator = MissingValuesValidator(threshold=0.5)
        result = validator.validate(df)
        assert result.passed is False
        assert "found 1 columns" in result.message.lower()

class TestDataTypes:
    def test_consistent_types(self):
        df = pd.DataFrame({
            'numeric': [1, 2, 3],
            'text': ['a', 'b', 'c']
        })
        validator = DataTypeValidator()
        result = validator.validate(df)
        assert result.passed is True

    def test_mixed_types(self):
        df = pd.DataFrame({
            'mixed': [1, 'text', 3.14, None]
        })
        validator = DataTypeValidator()
        result = validator.validate(df)
        assert result.passed is False # Warning is effectively "not passed" for test
        assert len(result.issues) > 0

class TestOutliers:
    def test_normal_distribution(self):
        # Generate normal data
        np.random.seed(42)
        data = np.random.normal(0, 1, 100)
        df = pd.DataFrame({'values': data})
        validator = OutlierValidator()
        result = validator.validate(df)
        assert result.passed is True

    def test_with_outliers(self):
        data = [1, 2, 3, 4, 5, 100]  # 100 is outlier
        df = pd.DataFrame({'values': data})
        validator = OutlierValidator()
        result = validator.validate(df)
        assert result.status == 'warning'
        assert any('values' in issue for issue in result.issues)

class TestCorrelations:
    def test_uncorrelated_data(self):
        np.random.seed(42)
        df = pd.DataFrame({
            'x': np.random.randn(100),
            'y': np.random.randn(100)
        })
        validator = CorrelationValidator()
        result = validator.validate(df)
        assert result.passed is True

    def test_highly_correlated(self):
        x = np.random.randn(100)
        y = x + 0.01 * np.random.randn(100)  # Highly correlated
        df = pd.DataFrame({'x': x, 'y': y})
        validator = CorrelationValidator(threshold=0.95)
        result = validator.validate(df)
        assert result.status == 'warning'
        assert len(result.issues) > 0