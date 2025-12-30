# .pre-commit-hooks/datalint

# DataLint pre-commit hook for automatic data validation

# Find all data files in the repository
find . -name "*.csv" -o -name "*.xlsx" -o -name "*.parquet" | while read file; do
    if git diff --cached --name-only | grep -q "$file"; then
        echo "🔍 Validating $file"
        if ! datalint validate "$file" --format json > /dev/null; then
            echo "Data validation failed for $file"
            echo "Run 'datalint validate $file' to see details"
            exit 1
        fi
    fi
done

echo "All data files passed validation"