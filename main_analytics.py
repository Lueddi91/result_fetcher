import pandas as pd
from result_fetcher import process_event, EVENT_CONFIG, save_results
from race_analytics import (
    RaceAnalytics,
    generate_analytics_report,
    generate_multi_race_report,
)


def main_with_analytics():
    """
    Main function that fetches data and performs analytics
    """
    print("=" * 70)
    print(" RACERESULT ANALYTICS")
    print("=" * 70)

    # Event IDs to process
    event_ids = []
    for id in EVENT_CONFIG.keys():
        event_ids.append(id)
    # Store all race dataframes
    all_race_data = {}

    # Process each event
    for event_id in event_ids:
        print(f"\n{'=' * 70}")
        print(f" Processing Event: {EVENT_CONFIG[event_id]['name']}")
        print(f"{'=' * 70}")

        dataframes = process_event(event_id)

        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            race_name = EVENT_CONFIG[event_id]["name"]
            all_race_data[race_name] = combined_df

            # Save individual race data
            filename = f"raceresult_{race_name.replace(' ', '_')}"
            save_results(dataframes, output_format="csv", filename_prefix=filename)

    if not all_race_data:
        print("\n❌ No data collected!")
        return

    print(f"\n\n{'=' * 70}")
    print(" ANALYTICS REPORTS")
    print(f"{'=' * 70}\n")

    # Generate individual race reports
    print("=" * 70)
    print(" INDIVIDUAL RACE STATISTICS")
    print("=" * 70)

    for race_name, df in all_race_data.items():
        print(f"\n{'─' * 70}")
        print(f" {race_name}")
        print(f"{'─' * 70}")

        report = generate_analytics_report(df, race_name)

        print(f"\nTotal Participants: {report['total_participants']}")

        # Save detailed report
        report_filename = f"analytics_{race_name.replace(' ', '_')}.txt"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(f"ANALYTICS REPORT: {race_name}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total Participants: {report['total_participants']}\n\n")
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(report["overall_stats"].to_string(index=False) + "\n\n")

            if report["division_stats"] is not None:
                f.write("STATISTICS BY DIVISION\n")
                f.write("-" * 70 + "\n")
                f.write(report["division_stats"].to_string(index=False) + "\n\n")

            if report["division_gaps"] is not None:
                f.write("TIME GAPS BETWEEN DIVISIONS\n")
                f.write("-" * 70 + "\n")
                f.write(report["division_gaps"].to_string(index=False) + "\n\n")

        print(f"\n✅ Detailed report saved: {report_filename}")

    # Multi-race comparison
    print(f"\n\n{'=' * 70}")
    print(" MULTI-RACE COMPARISON")
    print(f"{'=' * 70}\n")

    multi_report, multi_analytics = generate_multi_race_report(all_race_data)

    # Race comparison
    print("📊 Race Comparison Statistics:")
    print(multi_report["race_comparison"].to_string(index=False))

    # Athletes in multiple races
    print(f"\n\n📊 Athletes Who Competed in Multiple Races:")
    multi_race_athletes = multi_report["multi_race_athletes"]

    if multi_race_athletes is not None and len(multi_race_athletes) > 0:
        multi_athlete_report_filename = (
            f"multi_race_athletes_analytics_{race_name.replace(' ', '_')}.txt"
        )
        print(
            f"\nFound {len(multi_race_athletes)} athletes who competed in multiple races:"
        )

        with open(multi_athlete_report_filename, "w", encoding="utf-8") as f:
            # Detailed comparison for top multi-race athletes
            f.write(f"\n\n{'=' * 70}")
            f.write(" ATHLETE PROGRESSION ANALYSIS")
            f.write(f"{'=' * 70}")

            # Show top 5 athletes with most races
            top_athletes = multi_race_athletes

            for _, athlete_row in top_athletes.iterrows():
                athlete_name = athlete_row["Name"]
                num_races = athlete_row["Num_Races"]

                f.write(f"\n{'─' * 70}")
                f.write(f" {athlete_name} ({num_races} races)")
                f.write(f"{'─' * 70}")

                comparison = multi_analytics.compare_athlete_performance(athlete_name)

                if comparison is not None:
                    f.write(comparison.to_string(index=False))

                    # Get progression summary
                    progression = multi_analytics.get_athlete_progression(athlete_name)
                    if progression:
                        f.write(f"\nProgression Summary:")
                        for key, value in progression.items():
                            if key not in [
                                "Athlete",
                                "Races",
                                "Num_Races",
                            ] and not isinstance(value, list):
                                f.write(f"  {key}: {value}")

    print("✅ Multi-race analytics saved: multi_race_analytics.txt")

    # Export all data to Excel with multiple sheets
    print("\n📊 Creating comprehensive Excel report...")

    with pd.ExcelWriter(
        "comprehensive_race_analytics.xlsx", engine="openpyxl"
    ) as writer:
        # Race comparison sheet
        multi_report["race_comparison"].to_excel(
            writer, sheet_name="Race Comparison", index=False
        )

        # Multi-race athletes sheet
        if multi_race_athletes is not None and len(multi_race_athletes) > 0:
            multi_race_athletes.to_excel(
                writer, sheet_name="Multi-Race Athletes", index=False
            )

        # Individual race statistics
        for race_name, df in all_race_data.items():
            analytics = RaceAnalytics(df)

            # Overall stats
            sheet_name = race_name[:25] + " Stats"  # Excel sheet name limit
            analytics.get_overall_stats().to_excel(
                writer, sheet_name=sheet_name, index=False
            )

            # Division stats
            division_stats = analytics.get_division_stats()
            if division_stats is not None:
                sheet_name = race_name[:22] + " Div"
                division_stats.to_excel(writer, sheet_name=sheet_name, index=False)

        # Raw data for each race
        for race_name, df in all_race_data.items():
            sheet_name = race_name[:27] + " Raw"
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print("✅ Comprehensive Excel report saved: comprehensive_race_analytics.xlsx")

    print(f"\n\n{'=' * 70}")
    print(" ✅ ANALYTICS COMPLETE!")
    print(f"{'=' * 70}")
    print("\nGenerated files:")
    print("  📄 Individual race CSV files")
    print("  📄 Individual race analytics reports (*.txt)")
    print(f"  📄 {multi_athlete_report_filename}")
    print("  📊 comprehensive_race_analytics.xlsx")


if __name__ == "__main__":
    main_with_analytics()
