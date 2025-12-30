import click
from pathlib import Path
from datalint.utils.io import load_dataset
from datalint.engine.base import ValidationRunner
from datalint.engine.validators import get_default_validators
from datalint.utils.reporting import FormatterFactory

@click.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['text', 'json', 'html']), 
              default='text', help='Output format')
@click.option('--output', type=click.Path(), help='Output file path')
def validate(filepath, format, output):
    """
    Validate dataset for ML training readiness.
    Uses Dependency Injection Principle to loosely couple components.
    """
    try:
        # 1. Load Data
        df = load_dataset(filepath)
        
        # 2. Setup Validation Runner (DIP: runner doesn't care which validators)
        validators = get_default_validators()
        runner = ValidationRunner(validators)
        
        # 3. Run Validations
        results = runner.run(df)
        
        # 4. Format Output (DIP: CLI doesn't care how it's formatted)
        formatter = FormatterFactory.get_formatter(format)
        report = formatter.format(results)
        
        # 5. Output Result
        if output:
            Path(output).write_text(report, encoding='utf-8')
            click.echo(f"Report saved to {output}")
        else:
            click.echo(report)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()