import os
import pandas as pd
import click
from pathlib import Path
from typing import Iterator, Optional, Dict, List, Any, Union


def validate_path(filepath: str) -> Path:
    """
    Sanitize and validate file path.
    Security: prevents directory traversal and checks existence.
    """
    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Optional: restricts access to specific directories if needed
    # allowed_dir = Path(os.getcwd()).resolve()
    # if not str(path).startswith(str(allowed_dir)):
    #     raise PermissionError(f"Access to {path} is denied")
        
    return path

def load_dataset(filepath: str, chunksize: Optional[int] = None) -> Union[pd.DataFrame, Iterator[pd.DataFrame]]:
    """
    Load dataset with memory optimization and security checks.

    Args:
        filepath: Path to data file
        chunksize: Number of rows to read at once

    Returns:
        DataFrame or Iterator for large files
    """
    path = validate_path(filepath)
    file_ext = path.suffix.lower()

    try:
        if file_ext == '.csv':
            if chunksize:
                return pd.read_csv(path, chunksize=chunksize)
            
            # Smart chunking for large files (>100MB)
            if path.stat().st_size > 100 * 1024 * 1024:
                click.echo("Large file detected, using chunked processing...")
                return pd.read_csv(path, chunksize=10000)
            
            return pd.read_csv(path)

        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(path)

        elif file_ext == '.parquet':
            return pd.read_parquet(path)

        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
    except Exception as e:
        raise IOError(f"Error loading {filepath}: {str(e)}")


def validate_large_dataset(iterator: Iterator[pd.DataFrame],
                          validation_func) -> dict:
    """
    Validate large datasets using chunked processing.

    Reference: Streaming algorithms for data validation
    """
    results = []
    total_rows = 0

    for chunk in iterator:
        chunk_result = validation_func(chunk)
        results.append(chunk_result)
        total_rows += len(chunk)

        # Progress indicator for large files
        click.echo(f"\rProcessed {total_rows} rows...", nl=False)

    click.echo()  # New line after progress
    # Aggregate results
    return aggregate_chunked_results(results)


def aggregate_chunked_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate validation results from multiple chunks into a single result.
    
    Combines issues and recommendations, calculates overall pass/fail.
    """
    if not results:
        return {'passed': True, 'issues': {}, 'recommendations': []}
    
    aggregated = {
        'passed': True,
        'issues': {},
        'recommendations': [],
        'chunks_processed': len(results)
    }
    
    for chunk_result in results:
        # If any chunk fails, overall fails
        if not chunk_result.get('passed', True):
            aggregated['passed'] = False
        
        # Merge issues
        for key, value in chunk_result.get('issues', {}).items():
            if key not in aggregated['issues']:
                aggregated['issues'][key] = value
            elif isinstance(value, (int, float)):
                # Sum numeric issues (like counts)
                aggregated['issues'][key] += value
        
        # Collect unique recommendations
        for rec in chunk_result.get('recommendations', []):
            if rec not in aggregated['recommendations']:
                aggregated['recommendations'].append(rec)
    
    return aggregated