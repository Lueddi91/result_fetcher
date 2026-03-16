import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

import os

from pathlib import Path
from race_analytics import RaceAnalytics, time_to_seconds, seconds_to_time
from result_fetcher import main as rf_main

INDICES = ["Swim", "T1", "Bike", "T2", "Run", "Zielzeit"]
INDICES_PLACING = [
    "Platzierung Swim",
    "Platzierung T1",
    "Platzierung Bike",
    "Platzierung T2",
    "Platzierung Run",
    "Platzierung",
]


def get_csv_files():
    import re

    cwd = Path.cwd()
    filenames = os.listdir(cwd)
    csv_files = [filename for filename in filenames if filename.endswith(".csv")]
    display_names = []
    for filename in csv_files:
        if filename.startswith("raceresult_") and filename.endswith("_export.csv"):
            name_part = filename[11:-11]
            match = re.search(r"(\d{4})$", name_part)
            if match:
                year = match.group(1)
                race_name = name_part[: match.start()].strip()
                display_names.append((f"{race_name} ({year})", filename))
            else:
                display_names.append((name_part, filename))
        else:
            display_names.append((filename, filename))
    return display_names


def get_information(df):
    with st.container():
        wettkampf_select = st.selectbox(
            label="Welches Rennen möchtest du vergleichen?",
            options=pd.Series(df["Wettkampf"].unique()),
        )
        athlete_select = st.selectbox(
            label="Wer bist du?",
            options=(
                pd.Series(df.loc[df["Wettkampf"] == wettkampf_select]["Name"])
            ).unique(),
        )

    if st.button(label="Daten eingeben"):
        st.empty()
        st.session_state["data_set"] = True
        st.session_state["wettkampf"] = wettkampf_select
        st.session_state["athlete"] = athlete_select
        return


def is_valid_time_format(time_str):
    """
    Validates time string format is mm:ss or h:mm:ss
    Returns True if valid, False otherwise
    """
    import re

    if not time_str:
        return False
    time_str = str(time_str).strip()
    return bool(re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", time_str))


def get_own_times(df, wettkampf):
    analytic_df = RaceAnalytics(df.loc[df["Wettkampf"] == wettkampf])
    overall_stats = analytic_df.get_overall_stats()

    with st.container():
        st.subheader("Gib deine Zeiten ein")

        col1, col2, col3 = st.columns(3)

        with col1:
            swim_input = st.text_input("Swim (mm:ss)", placeholder="10:30")
        with col2:
            bike_input = st.text_input("Bike (mm:ss)", placeholder="38:45")
        with col3:
            run_input = st.text_input("Run (mm:ss)", placeholder="18:30")

    if st.button(label="Zeiten berechnen"):
        if swim_input and bike_input and run_input:
            invalid_times = []
            if not is_valid_time_format(swim_input):
                invalid_times.append("Swim")
            if not is_valid_time_format(bike_input):
                invalid_times.append("Bike")
            if not is_valid_time_format(run_input):
                invalid_times.append("Run")

            if invalid_times:
                st.warning(
                    f"Falsches Format: {', '.join(invalid_times)}. Bitte verwende das Format mm:ss (z.B. 10:30)"
                )
                return

            swim_sec = time_to_seconds(swim_input)
            bike_sec = time_to_seconds(bike_input)
            run_sec = time_to_seconds(run_input)

            t1_avg = time_to_seconds(
                overall_stats[overall_stats["Metric"] == "T1"]["Mean"].values[0]
            )
            t2_avg = time_to_seconds(
                overall_stats[overall_stats["Metric"] == "T2"]["Mean"].values[0]
            )

            t1_estimated = t1_avg if t1_avg else 0
            t2_estimated = t2_avg if t2_avg else 0

            total_time = swim_sec + t1_estimated + bike_sec + t2_estimated + run_sec

            st.session_state["own_times"] = {
                "Swim": swim_input,
                "T1": seconds_to_time(t1_estimated) if t1_estimated else "0:00",
                "Bike": bike_input,
                "T2": seconds_to_time(t2_estimated) if t2_estimated else "0:00",
                "Run": run_input,
                "Zielzeit": seconds_to_time(total_time),
            }
            st.session_state["own_times_seconds"] = {
                "Swim": swim_sec,
                "T1": t1_estimated,
                "Bike": bike_sec,
                "T2": t2_estimated,
                "Run": run_sec,
                "Zielzeit": total_time,
            }
            st.session_state["own_times_calculated"] = True
        else:
            st.error("Bitte gib Zeiten für Swim, Bike und Run ein.")


def calculate_cumulative(times_dict):
    cumulative = []
    total = 0
    for col in ["Swim", "T1", "Bike", "T2", "Run"]:
        if col in times_dict and times_dict[col] is not None:
            total += times_dict[col]
        cumulative.append(total)
    return cumulative


def display_comparison(df):
    analytic_df = RaceAnalytics(
        df.loc[df["Wettkampf"] == st.session_state["wettkampf"]]
    )

    athlete_data = df.loc[df["Name"] == st.session_state["athlete"]]

    overall_stats = analytic_df.get_overall_stats()
    st.subheader(
        f"Gewertete AthletInnen: {int(df.loc[df['Wettkampf'] == st.session_state['wettkampf'], ['Platzierung']].max().values[0])}"
    )

    athlete_seconds = {
        col: time_to_seconds(athlete_data[col].values[0])
        for col in ["Swim", "T1", "Bike", "T2", "Run"]
    }
    avg_seconds = {
        col: time_to_seconds(
            overall_stats[overall_stats["Metric"] == col]["Mean"].values[0]
        )
        for col in ["Swim", "T1", "Bike", "T2", "Run"]
    }

    cumulative_athlete = calculate_cumulative(athlete_seconds)
    cumulative_avg = calculate_cumulative(avg_seconds)

    chart_data = {
        "Durchschnitt": cumulative_avg,
        st.session_state["athlete"]: cumulative_athlete,
    }

    col1, col2 = st.columns(2)
    with col1:
        platzierungen = {"Durchschnitt": [], st.session_state["athlete"]: []}
        col_a, col_b, col_c = st.columns(3)

        for index in INDICES:
            counter = INDICES.index(index)
            label = index
            delta = seconds_to_time(
                time_to_seconds(athlete_data[index].values[0])
                - time_to_seconds(overall_stats["Mean"].values[counter])
            )
            with col_a:
                st.metric(
                    label=label,
                    value=athlete_data[index].values[0],
                    delta=delta,
                    delta_color="inverse",
                )
            with col_b:
                st.metric(
                    label=INDICES_PLACING[counter],
                    value=int(athlete_data[INDICES_PLACING[counter]].values[0]),
                )
            with col_c:
                label = f"Durchschnitt {INDICES[counter]}"
                st.metric(label=label, value=overall_stats["Mean"].values[counter])
    with col2:
        st.subheader(
            "Kumulierte Zeiten gegenüber dem Durchschnitt (weniger ist besser)",
            text_alignment="center",
        )

        st.line_chart(
            data=chart_data,
            y_label="Zeit [s]",
            x_label=st.session_state["athlete"],
            color=["#9BC53D", "#C3423F"],
        )

        st.subheader(
            "0 : Swim | 1 : T1 | 2 : Bike | 3 : T2 | 4 : Run | 5 : Finish",
            text_alignment="center",
        )


def display_own_times(df):
    division_df = df.loc[df["Wettkampf"] == st.session_state["wettkampf"]].copy()
    analytic_df = RaceAnalytics(division_df)
    overall_stats = analytic_df.get_overall_stats()

    own_times = st.session_state.get("own_times", {})
    own_times_seconds = st.session_state.get("own_times_seconds", {})
    athlete = "Deine Zeiten"

    ranks = {}
    for col in ["Swim", "T1", "Bike", "T2", "Run", "Zielzeit"]:
        col_seconds = f"{col}_seconds"
        if col_seconds in division_df.columns:
            times = division_df[col_seconds].dropna().tolist()
            user_time = own_times_seconds.get(col)
            if user_time is not None:
                rank = sum(1 for t in times if t < user_time) + 1
                total = len(times)
                ranks[col] = f"{rank}. / {total}"
            else:
                ranks[col] = "- / -"
        else:
            ranks[col] = "- / -"

    avg_seconds = {
        col: time_to_seconds(
            overall_stats[overall_stats["Metric"] == col]["Mean"].values[0]
        )
        for col in ["Swim", "T1", "Bike", "T2", "Run"]
    }

    cumulative_own = calculate_cumulative(own_times_seconds)
    cumulative_avg = calculate_cumulative(avg_seconds)

    chart_data = {
        "Durchschnitt": cumulative_avg,
        athlete: cumulative_own,
    }

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Deine Ergebnisse")

        col_a, col_b, col_c = st.columns(3)

        for index in INDICES:
            counter = INDICES.index(index)
            label = index

            user_time = own_times.get(index, "0:00")
            avg_time = overall_stats["Mean"].values[counter]

            user_sec = time_to_seconds(user_time)
            avg_sec = time_to_seconds(avg_time)

            delta = seconds_to_time(user_sec - avg_sec)

            with col_a:
                st.metric(
                    label=label,
                    value=user_time,
                    delta=delta,
                    delta_color="inverse",
                )
            with col_b:
                st.metric(
                    label=f"Platzierung {label}",
                    value=ranks.get(index, "- / -"),
                )
            with col_c:
                label = f"Durchschnitt {INDICES[counter]}"
                st.metric(label=label, value=avg_time)
    with col2:
        st.line_chart(
            data=chart_data,
            y_label="Zeit [s]",
            x_label=athlete,
            color=["#9BC53D", "#C3423F"],
        )

        st.subheader(
            "0 : Swim | 1 : T1 | 2 : Bike | 3 : T2 | 4 : Run | 5 : Finish",
            text_alignment="center",
        )


def main():
    st.set_page_config(layout="wide")
    st.empty()

    st.session_state["data_set"] = False
    st.session_state["own_times_calculated"] = False

    st.title("Triathlon LaLi/VeLi HH Analytics", text_alignment="center")

    st.markdown("""
                #### :rotating_light: Wie geht das hier?
                Du wählst ein Event und ein Rennen (Lali M/W oder VeLi) aus. Wenn du selbst gestartet bist kannst du deine eigenen Zeiten aus der Teilnehmerlist
                einlesen, ansonsten kannst du den Modus wechseln und eigene Zeiten eingeben, um zu gucken wie du dich in diesem Rennen geschlagen hättest.
                Bei der Eingabe von eigenen Zeiten werden die Wechselzeiten mit dem Durschnitt des jeweiligenen Wettbewerbes angenähert. 
                Nach Klick auf "Daten eingeben" erscheint eine Übersicht mit der Relation deiner eigenen Zeiten zum Durschnitt sowie eine grafische Übersicht,
                wie sich deine Zeiten im Vergleich zum Durchschnitt entwickelt haben. 
                Falls die Auswahlbox unter "Event auswählen" leer ist, klick bitte den Button mit der Aufschrift "Fetch Data"
                #### :sos: Ich sehe rote Kästen mit komischem Text?!
                Dann gab es wahrscheinlich einen Fehler. Ich (Daniel) hab das hier sehr wahrscheinlich nicht komplett fehlerfrei zusammengebastelt.
                Das ist für dich nur ärgerlich, aber nicht schlimm. Wenn das passiert, sag mir aber gerne Bescheid, dann muss das hoffentlich außer dir niemand 
                anderem passieren.
                #### :bulb: Ich hab noch eine tolle Idee, was man mit den Daten machen könnte!
                Dann gibt es zwei Möglichkeiten:
                - Du kannst selber ein bisschen programmieren und beteiligst dich einfach [HIER](https://github.com/Lueddi91/result_fetcher) 
                - Du schickst mir deine Idee und vielleicht kriegen wir das hin :-)
                """)
    if st.button("Fetch Data"):
        rf_main()

    st.divider()
    csv_files = get_csv_files()

    selected_race_display = st.selectbox(
        label="Event auswählen:",
        options=[item[0] for item in csv_files],
    )

    selected_race = next(
        (item[1] for item in csv_files if item[0] == selected_race_display), None
    )

    if selected_race:
        df = pd.read_csv(selected_race)

        mode = st.radio(
            label="Modus auswählen:",
            options=["Ich habe teilgenommen", "Ich möchte eigene Zeiten eingeben"],
            horizontal=True,
        )
        st.session_state["mode"] = mode

        individual_comparison, team_comparison, top_10 = st.tabs(
            ["Individual", "Teams", "TOP 10"]
        )

        with individual_comparison:
            if mode == "Ich habe teilgenommen":
                get_information(df)
                if st.session_state["data_set"]:
                    display_comparison(df)
            else:
                wettkampf_select = st.selectbox(
                    label="Welches Rennen möchtest du vergleichen?",
                    options=pd.Series(df["Wettkampf"].unique()),
                )
                st.session_state["wettkampf"] = wettkampf_select
                get_own_times(df, wettkampf_select)

                if st.session_state.get("own_times_calculated"):
                    display_own_times(df)

        with team_comparison:
            wettkampf_team = st.selectbox(
                label="Welches Rennen möchtest du vergleichen?",
                options=pd.Series(df["Wettkampf"].unique()),
                key="wettkampf_team",
            )

            division_df = df.loc[df["Wettkampf"] == wettkampf_team].copy()

            disciplines = ["Swim", "Bike", "Run", "Zielzeit"]
            for col in disciplines:
                division_df[f"{col}_seconds"] = division_df[col].apply(time_to_seconds)

            team_avg = (
                division_df.groupby("Team")[[f"{d}_seconds" for d in disciplines]]
                .mean()
                .reset_index()
                .sort_values("Zielzeit_seconds", ascending=True)
            )

            chart_data = team_avg.melt(
                id_vars="Team", var_name="Discipline", value_name="Seconds"
            )
            chart_data["Discipline"] = chart_data["Discipline"].str.replace(
                "_seconds", ""
            )

            def highlight_minmax(df, seconds_df):
                green = "#228B22"
                red = "#CD5C5C"

                styled = pd.DataFrame("", index=df.index, columns=df.columns)
                for col in df.columns:
                    if col == "Team":
                        continue
                    col_sec = f"{col}_seconds"
                    min_val = seconds_df[col_sec].min()
                    max_val = seconds_df[col_sec].max()
                    styled.loc[seconds_df[col_sec] == min_val, col] = (
                        f"background-color: {green}"
                    )
                    styled.loc[seconds_df[col_sec] == max_val, col] = (
                        f"background-color: {red}"
                    )
                return styled

            team_avg_display = team_avg.copy()
            team_avg_seconds = team_avg.copy()
            for col in disciplines:
                team_avg_display[col] = team_avg[f"{col}_seconds"].apply(
                    seconds_to_time
                )
            team_avg_display = team_avg_display.drop(
                columns=[f"{d}_seconds" for d in disciplines]
            )

            st.subheader("Durchschnittliche Zeiten pro Team")

            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(
                    chart_data, x="Discipline", y="Seconds", color="Team", stack=False
                )
            with col2:
                st.subheader("Detailansicht: Durchschnittszeiten")
                st.dataframe(
                    team_avg_display.style.apply(
                        lambda x: highlight_minmax(x, team_avg_seconds), axis=None
                    ),
                    use_container_width=True,
                )

            st.divider()

            division_df_ranked = division_df[division_df["gewertet"] == "*"].copy()
            team_avg_ranked = (
                division_df_ranked.groupby("Team")[
                    [f"{d}_seconds" for d in disciplines]
                ]
                .mean()
                .reset_index()
                .sort_values("Zielzeit_seconds", ascending=True)
            )

            chart_data_ranked = team_avg_ranked.melt(
                id_vars="Team", var_name="Discipline", value_name="Seconds"
            )
            chart_data_ranked["Discipline"] = chart_data_ranked[
                "Discipline"
            ].str.replace("_seconds", "")

            team_avg_ranked_display = team_avg_ranked.copy()
            team_avg_ranked_seconds = team_avg_ranked.copy()
            for col in disciplines:
                team_avg_ranked_display[col] = team_avg_ranked[f"{col}_seconds"].apply(
                    seconds_to_time
                )
            team_avg_ranked_display = team_avg_ranked_display.drop(
                columns=[f"{d}_seconds" for d in disciplines]
            )

            st.subheader("Nur gewertete Athleten (mit *)")

            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(
                    chart_data_ranked,
                    x="Discipline",
                    y="Seconds",
                    color="Team",
                    stack=False,
                )
            with col2:
                st.subheader("Detailansicht: Durchschnittszeiten (gewertet)")
                st.dataframe(
                    team_avg_ranked_display.style.apply(
                        lambda x: highlight_minmax(x, team_avg_ranked_seconds),
                        axis=None,
                    ),
                    use_container_width=True,
                )

        with top_10:
            wettkampf_top10 = st.selectbox(
                label="Welches Rennen möchtest du vergleichen?",
                options=pd.Series(df["Wettkampf"].unique()),
                key="wettkampf_top10",
            )

            division_df_top10 = df.loc[df["Wettkampf"] == wettkampf_top10].copy()

            for col in ["Swim", "T1", "Bike", "T2", "Run"]:
                division_df_top10[f"{col}_seconds"] = division_df_top10[col].apply(
                    time_to_seconds
                )

            top10_df = division_df_top10.nsmallest(10, "Platzierung")

            disciplines = ["Swim", "T1", "Bike", "T2", "Run"]

            for col in disciplines:
                top10_df[f"{col}_sec"] = top10_df[col].apply(time_to_seconds)

            chart_data_top10 = top10_df.melt(
                id_vars=["Name"],
                value_vars=[f"{d}_sec" for d in disciplines],
                var_name="Discipline",
                value_name="Seconds",
            )
            chart_data_top10["Discipline"] = chart_data_top10["Discipline"].str.replace(
                "_sec", ""
            )

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("TOP 10 - Zeiten")
                chart = (
                    alt.Chart(chart_data_top10)
                    .mark_bar()
                    .encode(
                        x=alt.X("Seconds:Q", stack="zero"),
                        y=alt.Y("Name:N", sort="x"),
                        color=alt.Color(
                            "Discipline:N", scale=alt.Scale(domain=disciplines)
                        ),
                    )
                )
                st.altair_chart(chart, use_container_width=True)
            with col2:
                st.subheader("Detailansicht")
                display_df = top10_df[
                    [
                        "Platzierung",
                        "Name",
                        "Team",
                        "Swim",
                        "T1",
                        "Bike",
                        "T2",
                        "Run",
                        "Zielzeit",
                    ]
                ].copy()

                def highlight_minmax_top10(df, seconds_df):
                    green = "#228B22"
                    red = "#CD5C5C"
                    styled = pd.DataFrame("", index=df.index, columns=df.columns)
                    for col in df.columns:
                        if col in ["Platzierung", "Name", "Team"]:
                            continue
                        col_sec = f"{col}_sec" if col != "Zielzeit" else col
                        if col_sec in seconds_df.columns:
                            min_val = seconds_df[col_sec].min()
                            max_val = seconds_df[col_sec].max()
                            styled.loc[seconds_df[col_sec] == min_val, col] = (
                                f"background-color: {green}"
                            )
                            styled.loc[seconds_df[col_sec] == max_val, col] = (
                                f"background-color: {red}"
                            )
                    return styled

                st.dataframe(
                    display_df.style.apply(
                        lambda x: highlight_minmax_top10(x, top10_df), axis=None
                    ),
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
