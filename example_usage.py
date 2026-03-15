"""
Example usage of the race analytics system
"""

import pandas as pd
from race_analytics import RaceAnalytics, MultiRaceAnalytics


def example_single_race_analysis():
    """
    Example: Analyze a single race
    """
    print("=" * 70)
    print(" EXAMPLE: Single Race Analysis")
    print("=" * 70)
    
    # Create sample data (in real usage, load from CSV)
    data = {
        'Wettkampf': ['Landesliga Herren', 'Landesliga Herren', 'Verbandsliga', 'Verbandsliga'],
        'Name': ['Athlete A', 'Athlete B', 'Athlete C', 'Athlete D'],
        'Team': ['Team 1', 'Team 2', 'Team 3', 'Team 4'],
        'Platzierung': ['1', '2', '3', '4'],
        'Swim': ['10:30', '11:00', '12:15', '12:45'],
        'T1': ['1:15', '1:20', '1:30', '1:35'],
        'Bike': ['38:45', '40:00', '42:30', '43:15'],
        'T2': ['0:50', '0:55', '1:00', '1:05'],
        'Run': ['18:30', '19:15', '20:45', '21:30'],
        'Zielzeit': ['1:09:50', '1:12:30', '1:18:00', '1:20:10'],
    }
    
    df = pd.DataFrame(data)
    
    # Create analytics object
    analytics = RaceAnalytics(df)
    
    # Get overall statistics
    print("\n📊 Overall Statistics:")
    print(analytics.get_overall_stats())
    
    # Get division statistics
    print("\n📊 Statistics by Division:")
    print(analytics.get_division_stats())
    
    # Get division gaps
    print("\n📊 Time Gaps Between Divisions:")
    print(analytics.get_division_gaps())


def example_multi_race_analysis():
    """
    Example: Compare athletes across multiple races
    """
    print("\n\n" + "=" * 70)
    print(" EXAMPLE: Multi-Race Analysis")
    print("=" * 70)
    
    # Race 1 data
    race1_data = {
        'Name': ['Athlete A', 'Athlete B', 'Athlete C'],
        'Wettkampf': ['Landesliga Herren', 'Landesliga Herren', 'Verbandsliga'],
        'Swim': ['10:30', '11:00', '12:15'],
        'Bike': ['38:45', '40:00', '42:30'],
        'Run': ['18:30', '19:15', '20:45'],
        'Zielzeit': ['1:09:50', '1:12:30', '1:18:00'],
    }
    
    # Race 2 data (Athlete A and C improved)
    race2_data = {
        'Name': ['Athlete A', 'Athlete C', 'Athlete E'],
        'Wettkampf': ['Landesliga Herren', 'Verbandsliga', 'Verbandsliga'],
        'Swim': ['10:15', '12:00', '12:30'],  # Athlete A improved
        'Bike': ['38:30', '42:00', '43:00'],  # Both improved
        'Run': ['18:15', '20:30', '21:00'],   # Both improved
        'Zielzeit': ['1:09:05', '1:17:15', '1:19:30'],
    }
    
    df1 = pd.DataFrame(race1_data)
    df2 = pd.DataFrame(race2_data)
    
    # Create multi-race analytics
    multi_analytics = MultiRaceAnalytics({
        'Race 1': df1,
        'Race 2': df2
    })
    
    # Find multi-race athletes
    print("\n📊 Athletes in Multiple Races:")
    multi_race = multi_analytics.get_multi_race_athletes()
    print(multi_race)
    
    # Compare specific athlete
    print("\n📊 Detailed Comparison for Athlete A:")
    athlete_comp = multi_analytics.compare_athlete_performance('Athlete A')
    print(athlete_comp)
    
    # Get progression
    print("\n📊 Progression Analysis for Athlete A:")
    progression = multi_analytics.get_athlete_progression('Athlete A')
    for key, value in progression.items():
        if not isinstance(value, list):
            print(f"  {key}: {value}")
    
    # Compare races overall
    print("\n📊 Race Comparison:")
    race_comp = multi_analytics.get_race_comparison_stats()
    print(race_comp)


def example_custom_queries():
    """
    Example: Custom queries and filtering
    """
    print("\n\n" + "=" * 70)
    print(" EXAMPLE: Custom Queries")
    print("=" * 70)
    
    # Load data (example with sample data)
    data = {
        'Wettkampf': ['Landesliga Herren', 'Landesliga Herren', 'Landesliga Damen', 'Verbandsliga'],
        'Name': ['Athlete A', 'Athlete B', 'Athlete C', 'Athlete D'],
        'Team': ['Team 1', 'Team 1', 'Team 2', 'Team 3'],
        'Swim': ['10:30', '11:00', '11:30', '12:15'],
        'Bike': ['38:45', '40:00', '40:30', '42:30'],
        'Run': ['18:30', '19:15', '19:30', '20:45'],
        'Zielzeit': ['1:09:50', '1:12:30', '1:13:45', '1:18:00'],
    }
    
    df = pd.DataFrame(data)
    
    # Query 1: Find fastest swimmers
    print("\n🏊 Top Swimmers:")
    analytics = RaceAnalytics(df)
    df_sorted = df.sort_values('Swim')
    print(df_sorted[['Name', 'Swim', 'Wettkampf']].head(3))
    
    # Query 2: Team statistics
    print("\n👥 Team Performance (Team 1):")
    team_df = df[df['Team'] == 'Team 1']
    team_analytics = RaceAnalytics(team_df)
    print(team_analytics.get_overall_stats())
    
    # Query 3: Division-specific analysis
    print("\n🏆 Landesliga Herren Statistics:")
    ll_herren = df[df['Wettkampf'] == 'Landesliga Herren']
    ll_analytics = RaceAnalytics(ll_herren)
    print(ll_analytics.get_overall_stats())


def main():
    """
    Run all examples
    """
    print("\n" + "=" * 70)
    print(" RACE ANALYTICS EXAMPLES")
    print("=" * 70)
    
    # Run examples
    example_single_race_analysis()
    example_multi_race_analysis()
    example_custom_queries()
    
    print("\n\n" + "=" * 70)
    print(" ✅ Examples Complete!")
    print("=" * 70)
    print("\nTo use with real data:")
    print("  1. Run 'python main_analytics.py' to fetch and analyze all races")
    print("  2. Or load CSV files: df = pd.read_csv('your_race_data.csv')")
    print("  3. Then use RaceAnalytics(df) or MultiRaceAnalytics({...})")


if __name__ == "__main__":
    main()
