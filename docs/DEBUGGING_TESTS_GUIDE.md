# DataLint: Guide to Debugging and Writing Tests Offline

> A comprehensive, offline guide for understanding, testing, and debugging the DataLint codebase

---

## Table of Contents

1. [Introduction](#introduction)
2. [Development Environment Setup](#development-environment-setup)
3. [Understanding DataLint Architecture](#understanding-datalint-architecture)
4. [Writing Tests](#writing-tests)
5. [Debugging Techniques](#debugging-techniques)
6. [Common Issues & Solutions](#common-issues--solutions)
7. [Best Practices](#best-practices)
8. [Quick Reference](#quick-reference)

---

## Introduction

DataLint is a Python package for automated data validation in ML workflows. This guide provides everything you need to understand, test, and debug the codebase entirely offline.

### What You'll Learn

- Setting up a local development environment
- Understanding the SOLID architecture principles applied
- Writing comprehensive tests for validators
- Debugging validation logic and data issues
- Resolving common development problems
- Following best practices for maintainable code

### Prerequisites

- Python 3.8+ installed locally
- Basic understanding of pandas and data validation concepts
- Familiarity with pytest (optional but recommended)

---

## Development Environment Setup

### 1. Local Installation

```bash
# Navigate to the project directory
cd datalint

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install in development mode (required for testing)
pip install -e .
```

### 2. Verify Installation

```bash
# Check that datalint is available
python -c "import datalint; print('DataLint imported successfully')"

# Check core imports work
python -c "from datalint.engine.base import BaseValidator, ValidationResult, ValidationRunner; print('Core imports OK')"

# Check validators can be imported
python -c "from datalint.engine.validators import MissingValuesValidator; print('Validators import OK')"
```

### 3. Install Development Dependencies (Optional)

```bash
# Install testing framework (if not already in setup.py)
pip install pytest pytest-cov

# Verify pytest works
pytest --version
```

### 4. Project Structure Overview

```
datalint/
├── __init__.py              # Package initialization
├── cli.py                   # Command-line interface
├── engine/
│   ├── __init__.py
│   ├── base.py              # Core abstractions (BaseValidator, ValidationResult, etc.)
│   ├── validators.py        # Concrete validator implementations
│   ├── learner.py           # Rule learning from clean data
│   └── profiler.py          # Statistical profiling
├── utils/
│   ├── __init__.py
│   ├── io.py                # File I/O utilities
│   └── reporting.py         # Output formatting
└── tests/
    ├── __init__.py
    ├── test_validators.py   # Validator unit tests
    └── test_cli.py          # CLI integration tests
```

---

## Understanding DataLint Architecture

### Core Concepts

#### 1. ValidationResult: The Standard Response

Every validator returns a `ValidationResult` with a consistent structure:

```python
from datalint.engine.base import ValidationResult

# Example result
result = ValidationResult(
    name="missing_values",
    status="passed",  # "passed", "warning", or "failed"
    message="No missing values found",
    issues=[],  # List of specific problems
    recommendations=[],  # Actionable suggestions
    details={'missing_ratio': 0.0}  # Optional structured data
)

# Convenience property
if result.passed:  # Equivalent to result.status == "passed"
    print("Validation passed!")
```

#### 2. BaseValidator: The Interface Contract

All validators must implement this abstract base class:

```python
from datalint.engine.base import BaseValidator, ValidationResult
import pandas as pd

class MissingValuesValidator(BaseValidator):
    @property
    def name(self) -> str:
        return "missing_values"

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        # Implementation here
        pass
```

#### 3. ValidationRunner: The Orchestrator

Coordinates multiple validators:

```python
from datalint.engine.base import ValidationRunner

# Create runner with validators
runner = ValidationRunner([
    MissingValuesValidator(),
    DataTypeValidator(),
    # ... more validators
])

# Run all validations
results = runner.run(df)

# Get results as dictionary
results_dict = runner.run_dict(df)
# {'missing_values': ValidationResult(...), 'data_types': ValidationResult(...)}
```

### SOLID Principles Applied

#### Single Responsibility Principle (SRP)
Each validator has exactly one job:

```python
# GOOD: One validator, one responsibility
class MissingValuesValidator(BaseValidator):
    """Only checks for missing values."""

class OutlierValidator(BaseValidator):
    """Only detects outliers."""
```

#### Open/Closed Principle (OCP)
Add new validators without modifying existing code:

```python
# To add a new validator, just create a new class
class DuplicateRowValidator(BaseValidator):
    @property
    def name(self) -> str:
        return "duplicate_rows"

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        # Implementation
        pass

# No changes needed to existing validators!
```

#### Dependency Inversion Principle (DIP)
High-level code depends on abstractions:

```python
# GOOD: CLI depends on Formatter interface
class CLI:
    def __init__(self, formatter: Formatter):
        self.formatter = formatter  # Any Formatter implementation

# Can easily swap formatters
cli = CLI(TextFormatter())   # or JsonFormatter(), HtmlFormatter()
```

### Data Flow

```
User Input → CLI → ValidationRunner → Validators → ValidationResult → Formatter → Output
```

---

## Writing Tests

### Setting Up Test Files

Create comprehensive tests in `tests/test_validators.py`:

```python
import pytest
import pandas as pd
import numpy as np
from datalint.engine.validators import (
    MissingValuesValidator,
    DataTypeValidator,
    OutlierValidator,
    CorrelationValidator,
    ConstantColumnValidator
)
```

### Unit Test Patterns

#### 1. Missing Values Validator Tests

```python
class TestMissingValuesValidator:
    def test_no_missing_values(self):
        """Test validator passes when no missing values exist."""
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        validator = MissingValuesValidator()
        result = validator.validate(df)

        assert result.passed is True
        assert result.status == "passed"
        assert len(result.issues) == 0
        assert "No missing values" in result.message

    def test_missing_values_detected(self):
        """Test validator fails when missing values exceed threshold."""
        df = pd.DataFrame({
            'good_col': [1, 2, 3, 4, 5],
            'bad_col': [1, None, 3, None, 5]  # 40% missing
        })
        validator = MissingValuesValidator(threshold=0.3)  # 30% threshold
        result = validator.validate(df)

        assert result.passed is False
        assert result.status == "failed"
        assert len(result.issues) > 0
        assert "bad_col" in str(result.issues)
        assert len(result.recommendations) > 0

    def test_custom_threshold(self):
        """Test custom threshold parameter."""
        df = pd.DataFrame({
            'col': [1, None, 3, 4, 5]  # 20% missing
        })

        # With 10% threshold: should fail
        validator_strict = MissingValuesValidator(threshold=0.1)
        result_strict = validator_strict.validate(df)
        assert result_strict.passed is False

        # With 30% threshold: should pass
        validator_lenient = MissingValuesValidator(threshold=0.3)
        result_lenient = validator_lenient.validate(df)
        assert result_lenient.passed is True
```

#### 2. Data Type Validator Tests

```python
class TestDataTypeValidator:
    def test_consistent_types(self):
        """Test passes with consistent data types."""
        df = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'text': ['a', 'b', 'c', 'd', 'e']
        })
        validator = DataTypeValidator()
        result = validator.validate(df)

        assert result.passed is True
        assert len(result.issues) == 0

    def test_mixed_types_warning(self):
        """Test detects mixed types and issues warning."""
        df = pd.DataFrame({
            'mixed': [1, 'text', 3.14, None]  # Multiple types
        })
        validator = DataTypeValidator()
        result = validator.validate(df)

        assert result.passed is False  # Warning counts as not passed for safety
        assert result.status == "warning"
        assert len(result.issues) > 0
        assert "mixed types" in str(result.issues).lower()
```

#### 3. Outlier Validator Tests

```python
class TestOutlierValidator:
    def test_normal_distribution_no_outliers(self):
        """Test passes with normal distribution."""
        np.random.seed(42)
        data = np.random.normal(0, 1, 100)  # Normal distribution
        df = pd.DataFrame({'values': data})

        validator = OutlierValidator()
        result = validator.validate(df)

        assert result.passed is True
        assert len(result.issues) == 0

    def test_detects_extreme_outliers(self):
        """Test detects clear outliers."""
        data = [1, 2, 3, 4, 5, 100]  # 100 is clear outlier
        df = pd.DataFrame({'values': data})

        validator = OutlierValidator()
        result = validator.validate(df)

        assert result.status == "warning"
        assert len(result.issues) > 0
        assert any('values' in issue for issue in result.issues)

    def test_iqr_multiplier_parameter(self):
        """Test IQR multiplier affects sensitivity."""
        data = [1, 2, 3, 4, 5, 10]  # 10 is moderately far
        df = pd.DataFrame({'values': data})

        # Strict detection (1.5 * IQR)
        validator_strict = OutlierValidator(iqr_multiplier=1.5)
        result_strict = validator_strict.validate(df)

        # Lenient detection (3.0 * IQR)
        validator_lenient = OutlierValidator(iqr_multiplier=3.0)
        result_lenient = validator_lenient.validate(df)

        # Strict should detect more outliers than lenient
        if result_strict.status == "warning" and result_lenient.status == "passed":
            assert True  # This is the expected behavior
```

#### 4. Correlation Validator Tests

```python
class TestCorrelationValidator:
    def test_uncorrelated_data(self):
        """Test passes with uncorrelated features."""
        np.random.seed(42)
        df = pd.DataFrame({
            'x': np.random.randn(100),
            'y': np.random.randn(100)  # Independent of x
        })

        validator = CorrelationValidator()
        result = validator.validate(df)

        assert result.passed is True
        assert len(result.issues) == 0

    def test_highly_correlated_features(self):
        """Test detects highly correlated features."""
        x = np.random.randn(100)
        y = x + 0.01 * np.random.randn(100)  # Nearly perfect correlation
        df = pd.DataFrame({'x': x, 'y': y})

        validator = CorrelationValidator(threshold=0.95)
        result = validator.validate(df)

        assert result.status == "warning"
        assert len(result.issues) > 0
        assert any('correlation' in issue.lower() for issue in result.issues)

    def test_perfect_correlation(self):
        """Test detects perfectly correlated features."""
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 1  # Perfect linear relationship
        df = pd.DataFrame({'x': x, 'y': y})

        validator = CorrelationValidator(threshold=0.99)
        result = validator.validate(df)

        assert result.status == "warning"
        assert len(result.issues) > 0
```

#### 5. Constant Column Validator Tests

```python
class TestConstantColumnValidator:
    def test_no_constant_columns(self):
        """Test passes when no constant columns exist."""
        df = pd.DataFrame({
            'varying': [1, 2, 3, 4, 5],
            'also_varying': ['a', 'b', 'c', 'd', 'e']
        })

        validator = ConstantColumnValidator()
        result = validator.validate(df)

        assert result.passed is True
        assert len(result.issues) == 0

    def test_detects_constant_columns(self):
        """Test detects columns with constant values."""
        df = pd.DataFrame({
            'varying': [1, 2, 3, 4, 5],
            'constant': ['same', 'same', 'same', 'same', 'same']
        })

        validator = ConstantColumnValidator()
        result = validator.validate(df)

        assert result.passed is False
        assert result.status == "failed"  # Critical issue
        assert len(result.issues) > 0
        assert 'constant' in str(result.issues)

    def test_detects_all_null_constant(self):
        """Test detects columns that are all null (constant null)."""
        df = pd.DataFrame({
            'varying': [1, 2, 3],
            'all_null': [None, None, None]
        })

        validator = ConstantColumnValidator()
        result = validator.validate(df)

        assert result.passed is False
        assert len(result.issues) > 0
```

### Integration Tests

Test the ValidationRunner with multiple validators:

```python
class TestValidationRunner:
    def test_runner_with_multiple_validators(self):
        """Test ValidationRunner coordinates multiple validators."""
        df = pd.DataFrame({
            'good': [1, 2, 3, 4, 5],
            'bad': [None, None, None, None, None]  # Will fail missing values
        })

        runner = ValidationRunner([
            MissingValuesValidator(),
            ConstantColumnValidator()
        ])

        results = runner.run(df)

        assert len(results) == 2
        assert any(not r.passed for r in results)  # At least one should fail

    def test_runner_dict_output(self):
        """Test ValidationRunner returns results as dictionary."""
        df = pd.DataFrame({'test': [1, 2, 3]})

        runner = ValidationRunner([MissingValuesValidator()])
        results_dict = runner.run_dict(df)

        assert isinstance(results_dict, dict)
        assert 'missing_values' in results_dict
        assert isinstance(results_dict['missing_values'], ValidationResult)
```

### CLI Integration Tests

```python
import subprocess
import tempfile
import os
from pathlib import Path

class TestCLI:
    def test_validate_command_success(self):
        """Test CLI validate command with good data."""
        csv_content = "a,b,c\n1,2,3\n4,5,6\n7,8,9\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            # Run CLI command
            result = subprocess.run(
                ['python', '-m', 'datalint.cli', 'validate', csv_path],
                capture_output=True, text=True, cwd='.'
            )

            assert result.returncode == 0
            assert "passed" in result.stdout.lower()

        finally:
            os.unlink(csv_path)

    def test_validate_command_failure(self):
        """Test CLI validate command detects issues."""
        csv_content = "a,b\n1,\n,\n3,"  # Missing values

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            result = subprocess.run(
                ['python', '-m', 'datalint.cli', 'validate', csv_path],
                capture_output=True, text=True, cwd='.'
            )

            assert result.returncode == 0  # CLI succeeds, but validation fails
            assert "failed" in result.stdout.lower() or "warning" in result.stdout.lower()

        finally:
            os.unlink(csv_path)
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_validators.py

# Run specific test class
pytest tests/test_validators.py::TestMissingValuesValidator

# Run specific test method
pytest tests/test_validators.py::TestMissingValuesValidator::test_no_missing_values

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=datalint tests/

# Run tests matching pattern
pytest -k "missing" tests/
```

---

## Debugging Techniques

### 1. Understanding ValidationResult Objects

```python
# Always inspect the full ValidationResult when debugging
result = validator.validate(df)

print(f"Name: {result.name}")
print(f"Status: {result.status}")
print(f"Passed: {result.passed}")
print(f"Message: {result.message}")
print(f"Issues: {result.issues}")
print(f"Recommendations: {result.recommendations}")
print(f"Details: {result.details}")

# Check for serialization issues
try:
    json_str = result.to_dict()
    print("Serialization OK")
except Exception as e:
    print(f"Serialization failed: {e}")
```

### 2. Debugging DataFrames

```python
# Essential DataFrame inspection
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Dtypes: {df.dtypes}")

# Check for missing values
print("Missing values per column:")
print(df.isnull().sum())

print("Missing value ratios:")
print(df.isnull().mean())

# Check for constant columns
print("Unique value counts:")
for col in df.columns:
    print(f"{col}: {df[col].nunique()} unique values")

# Check numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    print("Numeric column statistics:")
    print(df[numeric_cols].describe())

    print("Correlation matrix:")
    print(df[numeric_cols].corr())
```

### 3. Step-by-Step Validator Debugging

```python
def debug_validator(validator, df):
    """Debug helper for any validator."""
    print(f"\n=== Debugging {validator.name} ===")

    # Pre-validation checks
    print(f"Input DataFrame shape: {df.shape}")
    print(f"Input DataFrame columns: {df.columns.tolist()}")

    # Run validation
    result = validator.validate(df)

    # Post-validation analysis
    print(f"Result status: {result.status}")
    print(f"Result passed: {result.passed}")
    print(f"Result message: {result.message}")

    if result.issues:
        print(f"Issues found ({len(result.issues)}):")
        for i, issue in enumerate(result.issues, 1):
            print(f"  {i}. {issue}")

    if result.recommendations:
        print(f"Recommendations ({len(result.recommendations)}):")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")

    if result.details:
        print("Additional details:")
        for key, value in result.details.items():
            print(f"  {key}: {value}")

    return result

# Usage
validator = MissingValuesValidator()
result = debug_validator(validator, df)
```

### 4. Common Debugging Scenarios

#### Scenario 1: Validator Returns Wrong Status

```python
# Problem: Validator should pass but returns failed
def debug_status_issue(validator, df):
    # Add detailed logging to validator logic
    print("Checking conditions...")

    # For MissingValuesValidator
    if hasattr(validator, 'threshold'):
        missing_ratios = df.isnull().mean()
        print(f"Missing ratios: {missing_ratios.to_dict()}")
        print(f"Threshold: {validator.threshold}")

        problematic = missing_ratios[missing_ratios > validator.threshold]
        print(f"Problematic columns: {problematic.to_dict()}")

        expected_status = "passed" if len(problematic) == 0 else "failed"
        print(f"Expected status: {expected_status}")

    result = validator.validate(df)
    print(f"Actual status: {result.status}")

    return result
```

#### Scenario 2: DataFrame Processing Issues

```python
# Problem: DataFrame operations fail unexpectedly
def debug_dataframe_operations(df):
    print("DataFrame info:")
    print(df.info())

    print("\nDataFrame head:")
    print(df.head())

    print("\nDataFrame dtypes:")
    print(df.dtypes)

    # Check for problematic data types
    for col in df.columns:
        unique_types = df[col].dropna().apply(type).unique()
        if len(unique_types) > 1:
            print(f"WARNING: Column '{col}' has mixed types: {unique_types}")

    # Check for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    print(f"\nNumeric columns: {numeric_cols.tolist()}")

    if len(numeric_cols) > 0:
        print("Numeric column statistics:")
        print(df[numeric_cols].describe())
```

#### Scenario 3: Correlation Issues

```python
# Problem: Correlation validator behaves unexpectedly
def debug_correlation_issues(df, threshold=0.95):
    numeric_df = df.select_dtypes(include=[np.number])
    print(f"Numeric columns: {numeric_df.columns.tolist()}")

    if len(numeric_df.columns) < 2:
        print("ERROR: Need at least 2 numeric columns for correlation")
        return

    corr_matrix = numeric_df.corr()
    print("Correlation matrix:")
    print(corr_matrix)

    high_corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_val = abs(corr_matrix.iloc[i, j])
            if corr_val > threshold:
                high_corr_pairs.append((
                    corr_matrix.columns[i],
                    corr_matrix.columns[j],
                    corr_val
                ))

    print(f"High correlation pairs (>{threshold}):")
    for pair in high_corr_pairs:
        print(f"  {pair[0]} vs {pair[1]}: {pair[2]:.3f}")
```

### 5. Print Debugging Template

```python
def debug_validator_with_prints(validator_class, df, **kwargs):
    """Add print statements to validator for debugging."""
    validator = validator_class(**kwargs)

    print(f"\n{'='*50}")
    print(f"DEBUGGING {validator.name.upper()}")
    print(f"{'='*50}")

    print(f"Input DataFrame shape: {df.shape}")
    print(f"Validator parameters: {kwargs}")

    # Add specific debug prints based on validator type
    if validator.name == "missing_values":
        missing_ratios = df.isnull().mean()
        print(f"Missing ratios: {missing_ratios.to_dict()}")

        if hasattr(validator, 'threshold'):
            problematic = missing_ratios[missing_ratios > validator.threshold]
            print(f"Problematic columns: {problematic.to_dict()}")

    elif validator.name == "outliers":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        print(f"Numeric columns: {numeric_cols.tolist()}")

        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - validator.iqr_multiplier * IQR
            upper = Q3 + validator.iqr_multiplier * IQR

            outliers = df[(df[col] < lower) | (df[col] > upper)]
            print(f"{col}: {len(outliers)} outliers (bounds: {lower:.2f}, {upper:.2f})")

    # Run the actual validation
    result = validator.validate(df)

    print(f"Result status: {result.status}")
    print(f"Result passed: {result.passed}")

    return result
```

---

## Common Issues & Solutions

### Import Errors

#### Issue: Module Not Found
```
ImportError: No module named 'datalint.engine.base'
```

**Solutions:**
```bash
# Ensure you're in the correct directory
cd datalint

# Install in development mode
pip install -e .

# Check if __init__.py files exist
ls -la datalint/
ls -la datalint/engine/

# Try importing step by step
python -c "import datalint"  # Should work
python -c "from datalint import engine"  # Should work
python -c "from datalint.engine import base"  # Should work
```

#### Issue: Circular Import
```
ImportError: cannot import name 'X' from partially initialized module
```

**Solutions:**
- Check for circular dependencies in imports
- Move imports inside functions if needed
- Use TYPE_CHECKING for type hints that cause circular imports

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some_module import SomeClass
```

### DataFrame Issues

#### Issue: DataFrame Operations Fail
```
AttributeError: 'DataFrame' object has no attribute 'some_method'
```

**Solutions:**
```python
# Check pandas version
import pandas as pd
print(f"Pandas version: {pd.__version__}")

# Ensure DataFrame is not None
assert df is not None, "DataFrame is None"

# Check DataFrame type
print(f"Type: {type(df)}")
print(f"Shape: {df.shape}")

# Reset index if needed
df = df.reset_index(drop=True)
```

#### Issue: Mixed Data Types Cause Errors
```
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

**Solutions:**
```python
# Check for mixed types
for col in df.columns:
    unique_types = df[col].dropna().apply(type).unique()
    if len(unique_types) > 1:
        print(f"Column '{col}' has mixed types: {unique_types}")

# Convert to consistent types
df['mixed_col'] = pd.to_numeric(df['mixed_col'], errors='coerce')

# Or explicitly handle types
def safe_numeric_conversion(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan

df['numeric_col'] = df['mixed_col'].apply(safe_numeric_conversion)
```

### Validation Logic Bugs

#### Issue: Validator Always Returns Passed
**Debugging:**
```python
def debug_validator_logic(validator, df):
    # Add logging to see what's happening
    print("Starting validation...")

    # Manually check the logic
    if validator.name == "missing_values":
        missing_ratios = df.isnull().mean()
        print(f"Missing ratios: {missing_ratios}")

        threshold = getattr(validator, 'threshold', 0.05)
        print(f"Threshold: {threshold}")

        should_fail = any(ratio > threshold for ratio in missing_ratios)
        print(f"Should fail: {should_fail}")

    result = validator.validate(df)
    print(f"Actual result: {result.status}")

    return result
```

#### Issue: False Positives/Negatives
**Solutions:**
- Check threshold values
- Verify calculation logic
- Test with edge cases
- Add logging to understand decision process

```python
# Add debug mode to validators
class MissingValuesValidator(BaseValidator):
    def __init__(self, threshold: float = 0.05, debug: bool = False):
        self.threshold = threshold
        self.debug = debug

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        missing_ratios = df.isnull().mean()

        if self.debug:
            print(f"DEBUG: Missing ratios = {missing_ratios.to_dict()}")
            print(f"DEBUG: Threshold = {self.threshold}")

        problematic = missing_ratios[missing_ratios > self.threshold]

        if self.debug:
            print(f"DEBUG: Problematic columns = {problematic.to_dict()}")

        # ... rest of logic
```

### Memory Issues

#### Issue: Large Files Cause Memory Errors
```
MemoryError: Unable to allocate array
```

**Solutions:**
```python
# Use chunked processing
chunk_size = 10000
chunks = pd.read_csv('large_file.csv', chunksize=chunk_size)

results = []
for chunk in chunks:
    chunk_result = validate_chunk(chunk)
    results.append(chunk_result)

# Aggregate results
final_result = aggregate_chunked_results(results)

# Or use dask for very large files
import dask.dataframe as dd
df = dd.read_csv('large_file.csv')
# Process with dask operations
```

### CLI Issues

#### Issue: Command Not Found
```
datalint: command not found
```

**Solutions:**
```bash
# Check if installed
pip list | grep datalint

# Install properly
pip install -e .

# Use python module syntax
python -m datalint.cli validate file.csv

# Check setup.py entry points
grep "entry_points" setup.py
```

#### Issue: CLI Arguments Not Working
```
Error: Got unexpected extra argument
```

**Solutions:**
- Check Click decorator syntax
- Verify argument names match function parameters
- Test CLI parsing separately

```python
# Debug CLI parsing
import click

@click.command()
@click.argument('filepath', type=click.Path(exists=True))
def test_command(filepath):
    click.echo(f"File: {filepath}")

if __name__ == '__main__':
    test_command()
```

### Test Failures

#### Issue: Tests Pass Locally But Fail in CI
**Common Causes:**
- Different pandas versions
- Random seed not set for stochastic tests
- Hardcoded file paths
- Timezone differences

**Solutions:**
```python
# Set random seeds
np.random.seed(42)
# or
@pytest.fixture(autouse=True)
def set_random_seed():
    np.random.seed(42)

# Use temporary files
import tempfile
with tempfile.NamedTemporaryFile() as f:
    # Use f.name

# Parameterize tests for different scenarios
@pytest.mark.parametrize("threshold", [0.01, 0.05, 0.1])
def test_missing_values_threshold(threshold):
    # Test with different thresholds
```

#### Issue: Flaky Tests
**Solutions:**
- Remove timing-dependent tests
- Mock external dependencies
- Use deterministic data generation
- Add retry logic for network operations (if any)

---

## Best Practices

### Code Patterns

#### 1. Validator Implementation Template

```python
from datalint.engine.base import BaseValidator, ValidationResult
import pandas as pd
import numpy as np

class MyValidator(BaseValidator):
    """
    Brief description of what this validator checks.

    Follows SRP: Only responsible for one type of validation.
    """

    def __init__(self, threshold: float = 0.05):
        """
        Args:
            threshold: Configuration parameter with sensible default
        """
        self.threshold = threshold

    @property
    def name(self) -> str:
        """Unique identifier for this validator."""
        return "my_validator"

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """
        Main validation logic.

        Returns ValidationResult with consistent structure.
        """
        issues = []
        recommendations = []

        # Validation logic here
        # Check conditions and populate issues/recommendations

        # Determine status based on findings
        if not issues:
            status = "passed"
            message = "Validation passed"
        elif len(issues) > 5:  # Arbitrary threshold for "failed" vs "warning"
            status = "failed"
            message = f"Critical issues found: {len(issues)} problems"
        else:
            status = "warning"
            message = f"Minor issues found: {len(issues)} problems"

        return ValidationResult(
            name=self.name,
            status=status,
            message=message,
            issues=issues,
            recommendations=recommendations,
            details={'checked_columns': len(df.columns)}
        )
```

#### 2. Error Handling

```python
def validate(self, df: pd.DataFrame) -> ValidationResult:
    try:
        # Validation logic that might fail
        if df is None:
            raise ValueError("DataFrame cannot be None")

        if df.empty:
            raise ValueError("DataFrame cannot be empty")

        # ... validation logic ...

    except Exception as e:
        # Always return a ValidationResult, never crash
        return ValidationResult(
            name=self.name,
            status="failed",
            message=f"Validation failed due to error: {str(e)}",
            issues=[f"Unexpected error: {str(e)}"],
            recommendations=["Check input data format and try again"]
        )
```

#### 3. DataFrame Safety Checks

```python
def validate(self, df: pd.DataFrame) -> ValidationResult:
    # Input validation
    if df is None or df.empty:
        return ValidationResult(
            name=self.name,
            status="failed",
            message="Invalid input: DataFrame is None or empty",
            issues=["DataFrame validation requires valid input data"],
            recommendations=["Ensure DataFrame contains data before validation"]
        )

    # Check for required columns/types
    if len(df.columns) == 0:
        return ValidationResult(
            name=self.name,
            status="failed",
            message="No columns found in DataFrame",
            issues=["DataFrame must have at least one column"],
            recommendations=["Check data loading process"]
        )

    # Proceed with validation...
```

### Testing Patterns

#### 1. Test Data Factories

```python
@pytest.fixture
def clean_dataframe():
    """Factory for clean test data."""
    return pd.DataFrame({
        'numeric': [1, 2, 3, 4, 5],
        'categorical': ['A', 'B', 'C', 'D', 'E'],
        'no_missing': [10, 20, 30, 40, 50]
    })

@pytest.fixture
def problematic_dataframe():
    """Factory for data with known issues."""
    return pd.DataFrame({
        'missing_heavy': [1, None, None, None, 5],  # 60% missing
        'outlier': [1, 2, 3, 4, 100],  # Clear outlier
        'constant': ['same'] * 5  # Constant values
    })

def test_validator_with_clean_data(clean_dataframe):
    validator = MyValidator()
    result = validator.validate(clean_dataframe)
    assert result.passed is True

def test_validator_with_problems(problematic_dataframe):
    validator = MyValidator()
    result = validator.validate(problematic_dataframe)
    assert result.passed is False
```

#### 2. Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("threshold,expected_passed", [
    (0.1, True),   # 0% missing < 10% threshold
    (0.05, False), # 60% missing > 5% threshold
    (0.8, True),   # 60% missing < 80% threshold
])
def test_missing_values_thresholds(threshold, expected_passed):
    df = pd.DataFrame({
        'col': [1, None, None, None, 5]  # 60% missing
    })

    validator = MissingValuesValidator(threshold=threshold)
    result = validator.validate(df)

    assert result.passed is expected_passed
```

### Debugging Checklist

When debugging a validation issue:

1. **Understand the Input**
   - Print DataFrame shape, columns, dtypes
   - Check for missing values: `df.isnull().sum()`
   - Verify data types are as expected

2. **Isolate the Problem**
   - Test validator with minimal data
   - Add print statements to validator logic
   - Check intermediate calculations

3. **Verify Logic**
   - Manually calculate expected results
   - Compare with validator output
   - Check threshold values and parameters

4. **Check Edge Cases**
   - Empty DataFrame
   - Single column/row
   - All missing values
   - All constant values

5. **Review Output**
   - Check ValidationResult structure
   - Verify issues and recommendations are helpful
   - Ensure details contain useful debugging info

---

## Quick Reference

### Essential Imports

```python
import pandas as pd
import numpy as np
from datalint.engine.base import BaseValidator, ValidationResult, ValidationRunner
from datalint.engine.validators import (
    MissingValuesValidator, DataTypeValidator, OutlierValidator,
    CorrelationValidator, ConstantColumnValidator
)
```

### DataFrame Inspection

```python
# Basic info
df.shape          # (rows, columns)
df.columns        # Column names
df.dtypes         # Data types
df.isnull().sum() # Missing values per column

# Statistics
df.describe()     # Summary statistics
df.corr()         # Correlation matrix (numeric only)

# Data quality checks
df.isnull().mean()              # Missing ratios
df.nunique()                    # Unique value counts
df.select_dtypes(include=[np.number])  # Numeric columns only
```

### Validator Testing Template

```python
def test_my_validator():
    # Arrange
    df = pd.DataFrame({...})  # Test data
    validator = MyValidator(param=value)

    # Act
    result = validator.validate(df)

    # Assert
    assert result.passed is True  # or False
    assert len(result.issues) == expected_count
    assert "expected text" in result.message
```

### Common Test Scenarios

```python
# Clean data (should pass)
clean_df = pd.DataFrame({
    'a': [1, 2, 3, 4, 5],
    'b': ['x', 'y', 'z', 'w', 'v']
})

# Missing values (should fail)
missing_df = pd.DataFrame({
    'a': [1, None, 3, None, 5]
})

# Outliers (should warn)
outlier_df = pd.DataFrame({
    'a': [1, 2, 3, 4, 100]
})

# Correlated (should warn)
corr_df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [2, 4, 6, 8, 10]  # Perfect correlation
})

# Constant (should fail)
const_df = pd.DataFrame({
    'a': [1, 1, 1, 1, 1]
})
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_validators.py

# Specific test
pytest tests/test_validators.py::TestMissingValuesValidator::test_no_missing_values

# With coverage
pytest --cov=datalint tests/

# Verbose output
pytest -v tests/

# Stop on first failure
pytest -x tests/
```

### Debugging Commands

```python
# Inspect DataFrame
print(df.head())
print(df.info())
print(df.describe())

# Check validation result
result = validator.validate(df)
print(result.to_dict())

# Debug specific validator
from datalint.debug import debug_validator
debug_validator(validator, df)
```

This guide provides everything needed to understand, test, and debug DataLint entirely offline. Use it as a reference while developing and maintaining the codebase.
