# DataLint Landing Page Content

## Hero Section

### Headline
**Stop Data Quality Issues from Breaking Your ML Models**

### Subheadline
DataLint learns from your clean training data, then automatically catches problems in new data before they reach your models.

### CTA Button
`pip install datalint` | [View on GitHub]

---

## Problem Section

### Heading
**60% of ML projects fail. The culprit? Data.**

### Body
Not model architecture. Not hyperparameters. Data quality issues like missing values, type mismatches, and distribution drift silently degrade your models.

By the time you notice, you've already shipped bad predictions.

---

## Solution Section

### Heading
**Validation that learns from your data**

### Three Columns

**Zero Configuration**
Point DataLint at your clean dataset. No YAML. No schemas. No configuration files. It just works.

**Learn & Validate**
The profile command captures what "good" looks like. Then it validates new data against that baseline.

**CI/CD Ready**
JSON output integrates directly into your pipelines. Catch issues before deployment, not after.

---

## How It Works

```
Step 1: Install
pip install datalint

Step 2: Learn from clean data
datalint profile training.csv --learn

Step 3: Validate new data
datalint profile production.csv --profile training_profile.json
```

---

## Comparison Table

| Feature | DataLint | Great Expectations | Pandera |
|---------|----------|-------------------|---------|
| Zero config | Yes | No (YAML) | No (Schema) |
| Auto-learn rules | Yes | No | No |
| Setup time | 5 min | Hours | Hours |
| ML-focused | Yes | General | General |

---

## What It Catches

- Missing values exceeding thresholds
- Mixed data types in columns
- Statistical outliers
- Highly correlated feature pairs
- Constant/zero-variance columns
- Schema drift from training data

---

## Testimonials (Template)

> "We integrated DataLint into our pipeline and caught a data issue that would have cost us a week of debugging."
> — [Name], [Title] at [Company]

---

## Final CTA

### Heading
**Start validating your data in 5 minutes**

```bash
pip install datalint
datalint validate your_data.csv
```

[GitHub] | [Documentation] | [PyPI]
