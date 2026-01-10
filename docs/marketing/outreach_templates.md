# DataLint Direct Outreach Templates

## Cold Email to ML Team Leads

**Subject:** Quick question about your data validation workflow

---

Hi [Name],

I saw [company] is doing interesting work with [specific ML use case]. Quick question: how do you currently catch data quality issues before they affect model performance?

I built DataLint specifically for this problem - it learns from your training data and automatically validates new data against that baseline. No schemas to write, no YAML to configure.

Would love 15 minutes to show you how it works and get your feedback. We're in early development and looking for input from teams like yours.

[Your name]

---

## Follow-up Email

**Subject:** Re: Quick question about your data validation workflow

---

Hi [Name],

Following up on my previous email. Here's a 2-minute demo showing how it works:

1. Profile your training data: `datalint profile train.csv --learn`
2. Validate new data: `datalint profile new.csv --profile train_profile.json`

It catches missing values, type issues, outliers, and distribution drift automatically.

Happy to jump on a quick call if useful. Also open to feedback if you've solved this differently.

[Your name]

---

## LinkedIn DM Template

Hi [Name], saw your post about [ML topic]. I'm building a tool that catches data quality issues before they break ML models - would value your feedback if you have 10 minutes. No pitch, just looking for input from practitioners.

---

## Conference/Meetup Intro

"I'm [name], I built DataLint - it's a data validation tool that learns from your training data. Basically, you point it at clean data once, and it catches issues in new data automatically. We're looking for early users to help shape the product."

---

## Target Personas

1. **ML Engineers** - Care about model reliability, pipeline automation
2. **Data Scientists** - Care about data quality, reproducibility
3. **MLOps Engineers** - Care about CI/CD integration, monitoring
4. **Data Engineers** - Care about data pipelines, quality gates

---

## Objection Handling

**"We already use Great Expectations"**
"Great choice for general data validation. DataLint is specifically for ML - it learns statistical patterns from training data rather than requiring manual rule definition. Happy to show how they compare."

**"We built something internal"**
"Makes sense for custom needs. Is maintaining it taking engineering time? DataLint could handle the common cases while your custom tool handles edge cases."

**"Data quality isn't our biggest problem"**
"Got it. What would you say is the biggest pain point in your ML pipeline right now?"
