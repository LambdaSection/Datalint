# DataLint - HackerNews & Reddit Posts

## Show HN Post

**Title:** Show HN: DataLint - Learn validation rules from your training data

---

Hi HN,

I built DataLint because I kept seeing ML projects fail due to data quality issues - missing values, type mismatches, distribution drift - that only surfaced after models were deployed.

The core idea: instead of writing validation rules manually, DataLint learns what "good data" looks like from your clean training dataset, then catches anomalies in new data.

**How it works:**

```bash
pip install datalint

# Learn from clean data
datalint profile training.csv --learn

# Validate new data
datalint profile production.csv --profile training_profile.json
```

**What it catches:**
- Missing values above learned thresholds
- Statistical outliers beyond training distribution
- New categories not seen in training
- Correlation changes between features
- Schema drift (missing/extra columns)

**Why not Great Expectations?**
GE is excellent for general data validation but requires writing expectations manually. DataLint auto-generates rules from your data - useful when you want quick validation without configuration.

GitHub: [link]

Looking for feedback, especially:
1. What validation checks would be most valuable?
2. How do you currently handle data quality in ML pipelines?

---

## r/MachineLearning Post

**Title:** [P] DataLint - Automatic data validation that learns from your training data

---

I built a tool to catch data quality issues before they break ML models.

**The problem:** 60% of ML projects fail due to data issues. Missing values, type mismatches, and distribution drift silently degrade model performance.

**The solution:** DataLint learns statistical patterns from your clean training data, then validates new data against that baseline.

```
datalint profile training.csv --learn
datalint profile production.csv --profile training_profile.json
```

Unlike schema-based validation (Great Expectations, Pandera), DataLint requires no manual rule writing. Point it at clean data, and it learns what "good" looks like.

Currently catches: missing values, outliers, type inconsistencies, high correlations, constant columns, and distribution drift.

GitHub: [link]

Feedback welcome - what data quality issues cause you the most pain?

---

## r/datascience Post

**Title:** Built a tool that learns validation rules from your data - would value feedback

---

Working on a side project called DataLint. The idea: instead of writing data validation rules manually, it learns from your training data what "normal" looks like.

Use case: you have clean training data, and want to catch issues in new production data before retraining.

Currently early stage. Looking for feedback from people who deal with data quality issues regularly.

GitHub: [link]

Questions for the community:
- What data quality issues cause the most problems in your work?
- What tools do you currently use for data validation?
- Would automatic rule learning be useful, or do you prefer explicit rules?

---

## Posting Strategy

| Platform | Best Time | Notes |
|----------|-----------|-------|
| HN | Tuesday-Thursday, 9am EST | "Show HN" format |
| r/MachineLearning | Weekdays | [P] tag for projects |
| r/datascience | Weekdays | Ask for feedback angle |
| r/Python | Weekends | Focus on library quality |
