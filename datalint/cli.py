import click
import json
import pandas as pd
from pathlib import Path
from .engine.validators import (
    check_missing_values, check_data_types,
    check_outliers, check_correlations, check_constant_columns
)
from .engine.learner import RuleLearner, DataProfile
from .utils.io import load_dataset
from .utils.reporting import generate_report

@click.group()
@click.version_option(version="0.1.0")
def main():
    """DataLint: Automated data validation for ML teams."""
    pass

@main.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['text', 'json', 'html']),
              default='text', help='Output format')
@click.option('--output', type=click.Path(),
              help='Output file path')
@click.option('--threshold', type=float, default=0.05,
              help='Missing value threshold')
def validate(filepath, format, output, threshold):
    """
    Validate dataset for ML training readiness.

    FILEPATH: Path to CSV, Excel, or other supported format
    """
    try:
        # Load data
        df = load_dataset(filepath)
        click.echo(f"Loaded dataset: {df.shape[0]} rows × {df.shape[1]} columns")

        # Run validations
        results = run_all_validations(df, threshold)

        # Generate report
        report = generate_report(results, format=format)

        if output:
            Path(output).write_text(report)
            click.echo(f"Report saved to {output}")
        else:
            click.echo(report)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@main.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--learn', is_flag=True,
              help='Learn validation rules from this clean dataset')
@click.option('--profile', type=click.Path(),
              help='Path to existing profile for validation')
def profile(filepath, learn, profile):
    """
    Generate detailed dataset profile or learn validation rules.

    FILEPATH: Path to dataset
    """
    df = load_dataset(filepath)

    if learn:
        # Learn rules from clean data
        learner = RuleLearner()
        profile_data = learner.learn_from_clean_data(df)

        # Save profile
        output_path = Path(filepath).stem + '_profile.json'
        with open(output_path, 'w') as f:
            json.dump(profile_data.to_dict(), f, indent=2)

        click.echo(f"Validation profile saved to {output_path}")

    elif profile:
        # Validate against existing profile
        with open(profile) as f:
            profile_dict = json.load(f)

        profile_obj = DataProfile.from_dict(profile_dict)
        
        learner = RuleLearner()
        results = learner.validate_against_profile(df, profile_obj)
        report = generate_report(results, format='text')
        click.echo(report)

    else:
        # Generate basic profile
        profile_report = generate_basic_profile(df)
        click.echo(profile_report)

def run_all_validations(df, threshold):
    """Run all validation checks."""
    return {
        'missing_values': check_missing_values(df, threshold),
        'data_types': check_data_types(df),
        'outliers': check_outliers(df),
        'correlations': check_correlations(df),
        'constant_columns': check_constant_columns(df)
    }

def generate_basic_profile(df: pd.DataFrame) -> str:
    """
    Generate a basic statistical profile of the dataset.
    
    Returns a human-readable summary of the dataset structure.
    """
    lines = []
    lines.append(f"Dataset Profile: {df.shape[0]} rows × {df.shape[1]} columns")
    lines.append("=" * 50)
    lines.append("")
    
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_pct = null_count / len(df) * 100
        unique_count = df[col].nunique()
        
        lines.append(f"Column: {col}")
        lines.append(f"  Type: {dtype}")
        lines.append(f"  Missing: {null_count} ({null_pct:.1f}%)")
        lines.append(f"  Unique values: {unique_count}")
        
        if pd.api.types.is_numeric_dtype(df[col]):
            lines.append(f"  Range: [{df[col].min():.2f}, {df[col].max():.2f}]")
            lines.append(f"  Mean: {df[col].mean():.2f}")
        else:
            top_values = df[col].value_counts().head(3)
            lines.append(f"  Top values: {dict(top_values)}")
        
        lines.append("")
    
    return "\n".join(lines)