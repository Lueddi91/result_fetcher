import pandas as pd
import re


def time_to_seconds(time_str):
    """
    Converts time string to seconds
    Formats: "m:ss", "mm:ss", "h:mm:ss"
    """
    if pd.isna(time_str) or not time_str:
        return None

    time_str = str(time_str).strip()

    # Handle DNF, DNS, DSQ etc.
    if not re.match(r"^[\d:]+$", time_str):
        return None

    parts = time_str.split(":")

    try:
        if len(parts) == 2:  # mm:ss
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # h:mm:ss
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return None
    except (ValueError, IndexError):
        return None


def seconds_to_time(seconds):
    """
    Converts seconds back to time string
    """
    if pd.isna(seconds) or seconds is None:
        return None
    if seconds < 0:
        seconds = abs(seconds)
        sign = "-"
    else:
        sign = ""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{sign}{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{sign}{minutes}:{secs:02d}"


class RaceAnalytics:
    """
    Class for analyzing race results
    """

    def __init__(self, dataframe):
        """
        Initialize with race results dataframe
        """
        self.df = dataframe.copy()
        self._convert_times_to_seconds()

    def _convert_times_to_seconds(self):
        """
        Convert all time columns to seconds for analysis
        """
        time_columns = ["Swim", "T1", "Bike", "T2", "Run", "Zielzeit"]

        for col in time_columns:
            if col in self.df.columns:
                self.df[f"{col}_seconds"] = self.df[col].apply(time_to_seconds)

    def get_division_stats(self):
        """
        Calculate mean and median times for each division (Wettkampf)
        """
        if "Wettkampf" not in self.df.columns:
            return None

        time_cols = [
            "Swim_seconds",
            "T1_seconds",
            "Bike_seconds",
            "T2_seconds",
            "Run_seconds",
            "Zielzeit_seconds",
        ]
        available_cols = [col for col in time_cols if col in self.df.columns]

        stats = []

        for division in self.df["Wettkampf"].unique():
            division_data = self.df[self.df["Wettkampf"] == division]

            stat_row = {"Division": division, "Teilnehmer": len(division_data)}

            for col in available_cols:
                col_name = col.replace("_seconds", "")
                values = division_data[col].dropna()

                if len(values) > 0:
                    stat_row[f"{col_name}_Mean"] = seconds_to_time(values.mean())
                    stat_row[f"{col_name}_Median"] = seconds_to_time(values.median())
                    stat_row[f"{col_name}_Min"] = seconds_to_time(values.min())
                    stat_row[f"{col_name}_Max"] = seconds_to_time(values.max())
                else:
                    stat_row[f"{col_name}_Mean"] = None
                    stat_row[f"{col_name}_Median"] = None
                    stat_row[f"{col_name}_Min"] = None
                    stat_row[f"{col_name}_Max"] = None

            stats.append(stat_row)

        return pd.DataFrame(stats)

    def get_division_gaps(self):
        """
        Calculate time gaps between divisions
        """
        if (
            "Wettkampf" not in self.df.columns
            or "Zielzeit_seconds" not in self.df.columns
        ):
            return None

        division_medians = {}

        for division in self.df["Wettkampf"].unique():
            division_data = self.df[self.df["Wettkampf"] == division]
            median_time = division_data["Zielzeit_seconds"].median()
            division_medians[division] = median_time

        gaps = []
        divisions = list(division_medians.keys())

        for i in range(len(divisions)):
            for j in range(i + 1, len(divisions)):
                div1, div2 = divisions[i], divisions[j]
                gap_seconds = abs(division_medians[div1] - division_medians[div2])

                gaps.append(
                    {
                        "Division_1": div1,
                        "Division_2": div2,
                        "Median_Diff": seconds_to_time(gap_seconds),
                        "Median_Diff_Seconds": gap_seconds,
                    }
                )

        return pd.DataFrame(gaps).sort_values("Median_Diff_Seconds", ascending=False)

    def get_overall_stats(self):
        """
        Calculate overall statistics across all participants
        """
        time_cols = [
            "Swim_seconds",
            "T1_seconds",
            "Bike_seconds",
            "T2_seconds",
            "Run_seconds",
            "Zielzeit_seconds",
        ]
        available_cols = [col for col in time_cols if col in self.df.columns]

        stats = {"Metric": []}

        for col in available_cols:
            col_name = col.replace("_seconds", "")
            stats["Metric"].append(col_name)

        # Calculate statistics
        stat_types = ["Mean", "Median", "Std", "Min", "Max"]
        for stat_type in stat_types:
            stats[stat_type] = []

            for col in available_cols:
                values = self.df[col].dropna()

                if len(values) > 0:
                    if stat_type == "Mean":
                        stats[stat_type].append(seconds_to_time(values.mean()))
                    elif stat_type == "Median":
                        stats[stat_type].append(seconds_to_time(values.median()))
                    elif stat_type == "Std":
                        stats[stat_type].append(seconds_to_time(values.std()))
                    elif stat_type == "Min":
                        stats[stat_type].append(seconds_to_time(values.min()))
                    elif stat_type == "Max":
                        stats[stat_type].append(seconds_to_time(values.max()))
                else:
                    stats[stat_type].append(None)

        return pd.DataFrame(stats)


class MultiRaceAnalytics:
    """
    Class for comparing athletes across multiple races
    """

    def __init__(self, race_dataframes):
        """
        Initialize with dictionary of race dataframes
        race_dataframes: dict like {'Race Name': dataframe}
        """
        self.races = {}

        for race_name, df in race_dataframes.items():
            df_copy = df.copy()
            # Convert times to seconds
            time_columns = ["Swim", "T1", "Bike", "T2", "Run", "Zielzeit"]
            for col in time_columns:
                if col in df_copy.columns:
                    df_copy[f"{col}_seconds"] = df_copy[col].apply(time_to_seconds)

            df_copy["Race"] = race_name
            self.races[race_name] = df_copy

        # Combine all races
        self.combined_df = pd.concat(self.races.values(), ignore_index=True)

    def get_multi_race_athletes(self):
        """
        Find athletes who participated in multiple races
        """
        if "Name" not in self.combined_df.columns:
            return None

        athlete_races = (
            self.combined_df.groupby("Name")["Race"].apply(list).reset_index()
        )
        athlete_races["Num_Races"] = athlete_races["Race"].apply(len)

        multi_race = athlete_races[athlete_races["Num_Races"] > 1].sort_values(
            "Num_Races", ascending=False
        )

        return multi_race

    def compare_athlete_performance(self, athlete_name):
        """
        Compare performance of a specific athlete across races
        """
        athlete_data = self.combined_df[self.combined_df["Name"] == athlete_name]

        if len(athlete_data) == 0:
            return None

        comparison = []

        for _, row in athlete_data.iterrows():
            race_stats = {
                "Race": row.get("Race"),
                "Division": row.get("Wettkampf"),
                "Platzierung": row.get("Platzierung"),
                "Team": row.get("Team"),
            }

            # Add times
            for col in ["Swim", "T1", "Bike", "T2", "Run", "Zielzeit"]:
                if col in row:
                    race_stats[col] = row[col]

                # Add rankings
                rank_col = f"Platzierung {col}"
                if rank_col in row:
                    race_stats[rank_col] = row[rank_col]

            comparison.append(race_stats)

        df_comparison = pd.DataFrame(comparison)

        # Calculate improvements/changes
        if len(df_comparison) > 1:
            time_cols = [
                "Swim_seconds",
                "T1_seconds",
                "Bike_seconds",
                "T2_seconds",
                "Run_seconds",
                "Zielzeit_seconds",
            ]

            for col in time_cols:
                if col in athlete_data.columns:
                    times = athlete_data[col].dropna().tolist()
                    if len(times) >= 2:
                        improvement = times[0] - times[-1]  # Negative = faster
                        col_name = col.replace("_seconds", "")
        #                        print(f"\n{col_name} improvement: {seconds_to_time(abs(improvement))} {'faster' if improvement > 0 else 'slower'}")

        return df_comparison

    def get_athlete_progression(self, athlete_name):
        """
        Get detailed progression analysis for an athlete
        """
        athlete_data = self.combined_df[self.combined_df["Name"] == athlete_name].copy()

        if len(athlete_data) < 2:
            return None

        # Sort by race (assuming races are in chronological order)
        athlete_data = athlete_data.sort_values("Race")

        progression = {
            "Athlete": athlete_name,
            "Races": list(athlete_data["Race"]),
            "Num_Races": len(athlete_data),
        }

        # Calculate average times across all races
        time_cols = [
            "Swim_seconds",
            "T1_seconds",
            "Bike_seconds",
            "T2_seconds",
            "Run_seconds",
            "Zielzeit_seconds",
        ]

        for col in time_cols:
            if col in athlete_data.columns:
                col_name = col.replace("_seconds", "")
                values = athlete_data[col].dropna()

                if len(values) > 0:
                    progression[f"{col_name}_Avg"] = seconds_to_time(values.mean())
                    progression[f"{col_name}_Best"] = seconds_to_time(values.min())
                    progression[f"{col_name}_Worst"] = seconds_to_time(values.max())

                    if len(values) >= 2:
                        improvement = values.iloc[0] - values.iloc[-1]
                        progression[f"{col_name}_Change"] = seconds_to_time(
                            abs(improvement)
                        )
                        progression[f"{col_name}_Trend"] = (
                            "Improved" if improvement > 0 else "Declined"
                        )

        return progression

    def get_race_comparison_stats(self):
        """
        Compare overall statistics between races
        """
        race_stats = []

        for race_name, df in self.races.items():
            stats = {
                "Race": race_name,
                "Participants": len(df),
                "Divisions": df["Wettkampf"].nunique()
                if "Wettkampf" in df.columns
                else 0,
            }

            time_cols = [
                "Swim_seconds",
                "T1_seconds",
                "Bike_seconds",
                "T2_seconds",
                "Run_seconds",
                "Zielzeit_seconds",
            ]

            for col in time_cols:
                if col in df.columns:
                    col_name = col.replace("_seconds", "")
                    values = df[col].dropna()

                    if len(values) > 0:
                        stats[f"{col_name}_Median"] = seconds_to_time(values.median())
                        stats[f"{col_name}_Mean"] = seconds_to_time(values.mean())

            race_stats.append(stats)

        return pd.DataFrame(race_stats)


def generate_analytics_report(dataframe, race_name="Race"):
    """
    Generate a comprehensive analytics report for a single race
    """
    analytics = RaceAnalytics(dataframe)

    report = {
        "race_name": race_name,
        "total_participants": len(dataframe),
        "overall_stats": analytics.get_overall_stats(),
        "division_stats": analytics.get_division_stats(),
        "division_gaps": analytics.get_division_gaps(),
    }

    return report


def generate_multi_race_report(race_dataframes):
    """
    Generate a comprehensive report comparing multiple races

    race_dataframes: dict like {'Race Name': dataframe}
    """
    multi_analytics = MultiRaceAnalytics(race_dataframes)

    report = {
        "race_comparison": multi_analytics.get_race_comparison_stats(),
        "multi_race_athletes": multi_analytics.get_multi_race_athletes(),
    }

    return report, multi_analytics
