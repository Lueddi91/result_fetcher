# Quick Reference Guide

## Quick Start

### 1. Run Complete Analysis
```bash
python main_analytics.py
```

This fetches all race data and generates comprehensive analytics.

### 2. Analyze Existing Data
```python
import pandas as pd
from race_analytics import RaceAnalytics

df = pd.read_csv('your_race_data.csv')
analytics = RaceAnalytics(df)

# Get statistics
print(analytics.get_overall_stats())
print(analytics.get_division_stats())
print(analytics.get_division_gaps())
```

### 3. Compare Multiple Races
```python
from race_analytics import MultiRaceAnalytics

multi = MultiRaceAnalytics({
    'Race 1': df1,
    'Race 2': df2
})

# Find multi-race athletes
print(multi.get_multi_race_athletes())

# Compare athlete
print(multi.compare_athlete_performance('John Doe'))
```

## Key Metrics

### Overall Statistics
- **Mean**: Average time
- **Median**: Middle value (better for outliers)
- **Min/Max**: Fastest/slowest times
- **Std**: Variation in performance

### Division Analysis
- Statistics per division (Landesliga Herren/Damen, Verbandsliga)
- Time gaps between divisions
- Participant counts

### Multi-Race Tracking
- Athletes competing in multiple races
- Performance progression over time
- Improvement/decline trends
- Best/worst/average performances

## Common Tasks

### Find Fastest Times
```python
df_sorted = df.sort_values('Swim')
print(df_sorted[['Name', 'Swim']].head(5))
```

### Team Analysis
```python
team_df = df[df['Team'] == 'Your Team']
analytics = RaceAnalytics(team_df)
print(analytics.get_overall_stats())
```

### Division Filtering
```python
ll_herren = df[df['Wettkampf'] == 'Landesliga Hamburg Herren']
print(RaceAnalytics(ll_herren).get_overall_stats())
```

### Athlete Search
```python
athlete = df[df['Name'].str.contains('Smith', case=False)]
print(athlete)
```

### Track Improvement
```python
multi = MultiRaceAnalytics({'Race1': df1, 'Race2': df2})
progression = multi.get_athlete_progression('Athlete Name')
print(f"Swim improvement: {progression.get('Swim_Change')}")
```

## Output Files

### CSV Files
- `raceresult_[race_name]_export.csv` - Raw data per race

### Text Reports
- `analytics_[race_name].txt` - Individual race statistics
- `multi_race_analytics.txt` - Cross-race comparisons

### Excel Workbook
- `comprehensive_race_analytics.xlsx` - All data and analytics
  - Sheet 1: Race Comparison
  - Sheet 2: Multi-Race Athletes  
  - Sheet 3+: Individual race statistics
  - Last sheets: Raw data per race

## Time Format

### Input Format
- "mm:ss" → minutes:seconds (e.g., "12:34")
- "h:mm:ss" → hours:minutes:seconds (e.g., "1:23:45")

### Output Format
- Same as input format
- Internally converted to seconds for calculations

## Data Requirements

### Minimum Required Columns
- Name
- Wettkampf (Division)
- At least one time column (Swim, Bike, Run, or Zielzeit)

### Optional Columns
- Team
- Platzierung (Overall rank)
- Individual split rankings
- Transition times (T1, T2)

## Troubleshooting

### No athletes found in multiple races
→ Check name spelling (case-sensitive)

### Missing statistics
→ Ensure time columns are in correct format ("mm:ss")

### Empty results
→ Check that CSV has required columns

### API fetch fails
→ Verify internet connection and EVENT_CONFIG

## Advanced Usage

### Custom Analysis Function
```python
def custom_analysis(df):
    analytics = RaceAnalytics(df)
    
    # Your custom logic
    stats = analytics.get_overall_stats()
    
    # Process and return
    return stats

result = custom_analysis(df)
```

### Filter and Analyze
```python
# Filter by criteria
filtered = df[
    (df['Wettkampf'] == 'Landesliga Herren') & 
    (df['Team'] == 'Your Team')
]

# Analyze filtered data
analytics = RaceAnalytics(filtered)
print(analytics.get_overall_stats())
```

### Export Specific Metrics
```python
analytics = RaceAnalytics(df)
stats = analytics.get_division_stats()

# Export only specific columns
stats[['Division', 'Swim_Median', 'Bike_Median', 'Run_Median']].to_csv(
    'division_medians.csv', 
    index=False
)
```

## Tips

1. **Use Median over Mean** - More resistant to outliers
2. **Check Participant Counts** - Low counts = less reliable stats
3. **Watch for DNF/DNS** - Excluded from calculations
4. **Name Consistency** - Ensure athlete names match across races
5. **Time Format** - Always use "mm:ss" or "h:mm:ss"

## Getting Help

1. Check README.md for detailed documentation
2. Run example_usage.py for working examples
3. Check function docstrings: `help(RaceAnalytics)`
4. Review generated .txt reports for insights
