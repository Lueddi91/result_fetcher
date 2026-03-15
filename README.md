# Race Result Analytics System

## Overview
This system fetches triathlon race results from RaceResult.com and performs comprehensive analytics including:
- Mean and median split times (Swim, T1, Bike, T2, Run)
- Division comparisons and gaps
- Multi-race athlete tracking and progression analysis

## Files

### Core Modules
- **result_fetcher.py** - Original data fetching module
- **race_analytics.py** - Analytics engine with statistical calculations
- **main_analytics.py** - Main execution script with integrated analytics

### Output Files
- **raceresult_[race_name]_export.csv** - Raw race data per event
- **analytics_[race_name].txt** - Individual race statistics
- **multi_race_analytics.txt** - Cross-race comparisons
- **comprehensive_race_analytics.xlsx** - Excel workbook with all data and analytics

## Usage

### Basic Usage
```python
python main_analytics.py
```

This will:
1. Fetch data for all configured races
2. Calculate statistics for each race
3. Compare athletes across races
4. Generate comprehensive reports

### Custom Analysis

#### Analyze a Single Race
```python
from race_analytics import RaceAnalytics
import pandas as pd

# Load your race data
df = pd.read_csv('raceresult_export.csv')

# Create analytics object
analytics = RaceAnalytics(df)

# Get statistics
overall_stats = analytics.get_overall_stats()
division_stats = analytics.get_division_stats()
division_gaps = analytics.get_division_gaps()

print(overall_stats)
print(division_stats)
print(division_gaps)
```

#### Compare Multiple Races
```python
from race_analytics import MultiRaceAnalytics
import pandas as pd

# Load race data
race1 = pd.read_csv('race1.csv')
race2 = pd.read_csv('race2.csv')

# Create multi-race analytics
multi_analytics = MultiRaceAnalytics({
    'Race 1': race1,
    'Race 2': race2
})

# Find athletes in multiple races
multi_race_athletes = multi_analytics.get_multi_race_athletes()
print(multi_race_athletes)

# Compare specific athlete
athlete_comparison = multi_analytics.compare_athlete_performance('John Doe')
print(athlete_comparison)

# Get athlete progression
progression = multi_analytics.get_athlete_progression('John Doe')
print(progression)

# Compare race statistics
race_comparison = multi_analytics.get_race_comparison_stats()
print(race_comparison)
```

## Metrics Calculated

### 1. Overall Statistics (per race)
- **Mean** - Average time across all participants
- **Median** - Middle value (better for outlier resistance)
- **Std** - Standard deviation (variation in times)
- **Min** - Fastest time
- **Max** - Slowest time

Calculated for:
- Swim
- T1 (Transition 1)
- Bike
- T2 (Transition 2)
- Run
- Total Time (Zielzeit)

### 2. Division Statistics
Same metrics as above, but calculated per division:
- Landesliga Hamburg Herren
- Landesliga Hamburg Damen
- Verbandsliga Hamburg (Herren)

### 3. Division Gaps
- Median time difference between divisions
- Shows competitive level differences

### 4. Multi-Race Analysis
For athletes competing in multiple races:
- **Performance comparison** - Side-by-side times across races
- **Progression tracking** - Improvement/decline over time
- **Best/Worst/Average** - Performance ranges
- **Trend analysis** - Overall direction (improving/declining)

## Example Output

### Individual Race Statistics
```
📊 Overall Statistics:
   Metric    Mean    Median     Std      Min      Max
   Swim    12:34    12:30    1:15    10:45    15:30
   Bike    45:20    45:00    3:45    38:15    55:30
   Run     22:15    22:00    2:30    18:45    28:30
```

### Division Gaps
```
📊 Time Gaps Between Divisions:
   Division_1                          Division_2                    Median_Diff
   Landesliga Hamburg Herren          Verbandsliga Hamburg          5:45
   Landesliga Hamburg Damen           Verbandsliga Hamburg          3:20
```

### Multi-Race Athletes
```
📊 Athletes Who Competed in Multiple Races:
   Name              Race                                    Num_Races
   John Doe          [Race1, Race2, Race3]                  3
   Jane Smith        [Race1, Race2]                         2
```

## Data Structure

### Input Data (from result_fetcher.py)
Required columns:
- Wettkampf (Division)
- Name
- Team
- Platzierung (Overall placement)
- Swim, T1, Bike, T2, Run, Zielzeit (Times)
- Platzierung Swim/Bike/Run (Split placements)

### Time Format
Times are stored as strings: "mm:ss" or "h:mm:ss"
- Examples: "12:34", "1:23:45"
- Internally converted to seconds for calculations
- Output converted back to time format

## Technical Details

### RaceAnalytics Class
Main analytics engine for single races.

**Methods:**
- `get_overall_stats()` - Overall race statistics
- `get_division_stats()` - Statistics by division
- `get_division_gaps()` - Time gaps between divisions

### MultiRaceAnalytics Class
Engine for comparing multiple races and tracking athletes.

**Methods:**
- `get_multi_race_athletes()` - Find athletes in multiple races
- `compare_athlete_performance(name)` - Side-by-side comparison
- `get_athlete_progression(name)` - Progression analysis
- `get_race_comparison_stats()` - Compare races overall

### Helper Functions
- `time_to_seconds(time_str)` - Convert time string to seconds
- `seconds_to_time(seconds)` - Convert seconds back to time string
- `generate_analytics_report(df, name)` - Generate full report for one race
- `generate_multi_race_report(dfs)` - Generate cross-race report

## Extending the System

### Add New Metrics
To add custom metrics, extend the `RaceAnalytics` class:

```python
class RaceAnalytics:
    # ... existing code ...
    
    def get_custom_metric(self):
        """Your custom analysis"""
        # Your code here
        return result
```

### Add New Comparisons
Extend `MultiRaceAnalytics` for cross-race analysis:

```python
class MultiRaceAnalytics:
    # ... existing code ...
    
    def compare_custom(self):
        """Your custom comparison"""
        # Your code here
        return result
```

## Requirements
```
pandas
numpy
requests
openpyxl
```

Install with:
```bash
pip install pandas numpy requests openpyxl
```

## Event Configuration

To add new events, update `EVENT_CONFIG` in `result_fetcher.py`:

```python
EVENT_CONFIG = {
    "event_id": {
        "name": "Event Name",
        "key": "api_key",
        "listname": "list_name",
        "groups": ["#1_Group1", "#2_Group2"]
    }
}
```

## Notes

- Times marked as DNF, DNS, DSQ are excluded from calculations
- Missing data is handled gracefully (not included in averages)
- Athlete matching is based on exact name matches
- Divisions must match exactly for gap analysis

## Troubleshooting

**No data fetched:**
- Check internet connection
- Verify EVENT_CONFIG has correct API keys
- Ensure event URLs are valid

**Athletes not matched across races:**
- Names must match exactly (case-sensitive)
- Check for spelling variations
- Check for extra spaces

**Missing metrics:**
- Ensure all time columns are present in source data
- Check for data format issues (should be "mm:ss")

## License
This is a utility tool for analyzing triathlon race results.
