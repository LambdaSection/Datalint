# DataLint Demo Recording Script

## Setup Before Recording

1. Create sample CSV files:
```bash
# training_data.csv - clean data
echo "age,income,category
25,50000,A
30,55000,B
35,60000,A
28,52000,B
32,58000,A" > training_data.csv

# new_data_good.csv - similar distribution
echo "age,income,category
27,51000,A
31,56000,B
29,53000,A" > new_data_good.csv

# new_data_bad.csv - with issues
echo "age,income,category
27,51000,A
-5,999999,X
,55000,B
200,52000,A" > new_data_bad.csv
```

2. Clear terminal, set font size to large

---

## Recording Script (Terminal Commands)

### Scene 1: Basic Validation (30 seconds)
```bash
# Show the problem
echo "Let's validate some ML training data..."
datalint validate training_data.csv
```

### Scene 2: Learn from Clean Data (30 seconds)
```bash
# Learn what good data looks like
echo "Now let's learn from this clean dataset..."
datalint profile training_data.csv --learn
cat training_data_profile.json | head -20
```

### Scene 3: Validate Good Data (20 seconds)
```bash
# Validate similar data - should pass
echo "Validating new data against the profile..."
datalint profile new_data_good.csv --profile training_data_profile.json
```

### Scene 4: Catch Bad Data (30 seconds)
```bash
# Validate bad data - should fail
echo "Now let's try data with issues..."
datalint profile new_data_bad.csv --profile training_data_profile.json
```

### Scene 5: Call to Action (10 seconds)
```bash
echo "pip install datalint"
echo "github.com/STABLE-TURBO/datalint"
```

---

## Voiceover Script (Optional)

**Scene 1:** "DataLint validates your data for machine learning. Here's a quick check on our training data."

**Scene 2:** "The learn command profiles your clean data - capturing statistics, distributions, and expected patterns."

**Scene 3:** "Now when new data comes in, we validate it against that learned profile. Similar data passes."

**Scene 4:** "But when we have problematic data - negative ages, extreme values, missing fields - DataLint catches it before your model does."

**Scene 5:** "pip install datalint. Link in description."

---

## Recording Tools

- **Terminal**: Windows Terminal with dark theme
- **Recording**: OBS Studio or ScreenToGif
- **Format**: GIF for Twitter, MP4 for LinkedIn
- **Duration**: Target 2 minutes total
