"""
DataLint CLI - Command-line interface for data validation.

Usage:
    datalint validate mydata.csv
    datalint profile training.csv --learn
    datalint profile newdata.csv --profile training_profile.json
"""

import json
import click
from pathlib import Path
from datalint.utils.io import load_dataset
from datalint.engine.base import ValidationRunner
from datalint.engine.validators import get_default_validators
from datalint.engine.learner import RuleLearner, DataProfile
from datalint.utils.reporting import FormatterFactory


@click.group()
def cli():
    """DataLint - Automated data validation for ML teams."""
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "html"]),
    default="text",
    help="Output format",
)
@click.option("--output", type=click.Path(), help="Output file path")
def validate(filepath, output_format, output):
    """
    Validate dataset for ML training readiness.

    FILEPATH: Path to the dataset file (CSV, Excel, or Parquet)
    """
    try:
        df = load_dataset(filepath)
        click.echo(f"Loaded dataset: {len(df)} rows x {len(df.columns)} columns")

        validators = get_default_validators()
        runner = ValidationRunner(validators)
        results = runner.run(df)

        formatter = FormatterFactory.get_formatter(output_format)
        report = formatter.format(results)

        if output:
            Path(output).write_text(report, encoding="utf-8")
            click.echo(f"Report saved to {output}")
        else:
            click.echo(report)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--learn", is_flag=True, help="Learn profile from clean dataset")
@click.option("--profile", "profile_path", type=click.Path(), help="Path to existing profile for validation")
@click.option("--output", type=click.Path(), help="Output path for learned profile")
def profile(filepath, learn, profile_path, output):
    """
    Learn from or validate against a data profile.

    FILEPATH: Path to the dataset file

    Examples:
        datalint profile training.csv --learn
        datalint profile newdata.csv --profile training_profile.json
    """
    try:
        df = load_dataset(filepath)
        learner = RuleLearner()

        if learn:
            # Learn mode: create profile from clean data
            click.echo(f"Learning profile from {filepath}...")
            data_profile = learner.learn_from_clean_data(df)

            # Determine output path
            output_path = output or Path(filepath).stem + "_profile.json"
            Path(output_path).write_text(
                json.dumps(data_profile.to_dict(), indent=2, default=str),
                encoding="utf-8"
            )
            click.echo(f"Profile saved to {output_path}")
            click.echo(f"Learned patterns from {len(df)} rows, {len(df.columns)} columns")

        elif profile_path:
            # Validate mode: check data against existing profile
            click.echo(f"Validating {filepath} against profile...")
            with open(profile_path, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            data_profile = DataProfile.from_dict(profile_data)

            results = learner.validate_against_profile(df, data_profile)

            if results["passed"]:
                click.echo(f"Validation PASSED (score: {results['overall_score']:.1%})")
            else:
                click.echo(f"Validation FAILED (score: {results['overall_score']:.1%})")
                click.echo("\nAnomalies detected:")
                for anomaly in results["anomalies"]:
                    click.echo(f"  - {anomaly}")

        else:
            click.echo("Please specify --learn or --profile <path>", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
