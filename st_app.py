import streamlit as st
import pandas as pd

import os

from pathlib import Path
from race_analytics import RaceAnalytics, time_to_seconds, seconds_to_time

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
    cwd = Path.cwd()
    filenames = os.listdir(cwd)
    csv_files = [filename for filename in filenames if filename.endswith(".csv")]
    return csv_files


def get_information(df):
    with st.container():
        wettkampf_select = st.radio(
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
                st.warning(f"Falsches Format: {', '.join(invalid_times)}. Bitte verwende das Format mm:ss (z.B. 10:30)")
                return

            swim_sec = time_to_seconds(swim_input)
            bike_sec = time_to_seconds(bike_input)
            run_sec = time_to_seconds(run_input)

            t1_avg = time_to_seconds(overall_stats[overall_stats["Metric"] == "T1"]["Mean"].values[0])
            t2_avg = time_to_seconds(overall_stats[overall_stats["Metric"] == "T2"]["Mean"].values[0])

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

    platzierungen = {"Durchschnitt": [], st.session_state["athlete"]: []}
    col1, col2, col3 = st.columns(3)

    for index in INDICES:
        counter = INDICES.index(index)
        label = index
        delta = seconds_to_time(
            time_to_seconds(athlete_data[index].values[0])
            - time_to_seconds(overall_stats["Mean"].values[counter])
        )
        with col1:
            st.metric(
                label=label,
                value=athlete_data[index].values[0],
                delta=delta,
                delta_color="inverse",
            )
        with col2:
            st.metric(
                label=INDICES_PLACING[counter],
                value=int(athlete_data[INDICES_PLACING[counter]].values[0]),
            )
        with col3:
            label = f"Durchschnitt {INDICES[counter]}"
            st.metric(label=label, value=overall_stats["Mean"].values[counter])

    athlete_seconds = {
        col: time_to_seconds(athlete_data[col].values[0])
        for col in ["Swim", "T1", "Bike", "T2", "Run"]
    }
    avg_seconds = {
        col: time_to_seconds(overall_stats[overall_stats["Metric"] == col]["Mean"].values[0])
        for col in ["Swim", "T1", "Bike", "T2", "Run"]
    }

    cumulative_athlete = calculate_cumulative(athlete_seconds)
    cumulative_avg = calculate_cumulative(avg_seconds)

    chart_data = {
        "Durchschnitt": cumulative_avg,
        st.session_state["athlete"]: cumulative_athlete,
    }

    st.line_chart(
        data=chart_data,
        y_label="Zeit [s]",
        x_label=st.session_state["athlete"],
        color=["#9BC53D", "#C3423F"],
    )

    placing_data = {
        "Platzierung": {
            i: int(athlete_data[INDICES_PLACING[i]].values[0])
            for i in range(5)
        }
    }
    st.bar_chart(data=placing_data, y_label="Platz", color="#C3423F")

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

    st.subheader("Deine Ergebnisse")

    col1, col2, col3 = st.columns(3)

    for index in INDICES:
        counter = INDICES.index(index)
        label = index

        user_time = own_times.get(index, "0:00")
        avg_time = overall_stats["Mean"].values[counter]

        user_sec = time_to_seconds(user_time)
        avg_sec = time_to_seconds(avg_time)

        delta = seconds_to_time(user_sec - avg_sec)

        with col1:
            st.metric(
                label=label,
                value=user_time,
                delta=delta,
                delta_color="inverse",
            )
        with col2:
            st.metric(
                label=f"Platzierung {label}",
                value=ranks.get(index, "- / -"),
            )
        with col3:
            label = f"Durchschnitt {INDICES[counter]}"
            st.metric(label=label, value=avg_time)

    avg_seconds = {
        col: time_to_seconds(overall_stats[overall_stats["Metric"] == col]["Mean"].values[0])
        for col in ["Swim", "T1", "Bike", "T2", "Run"]
    }

    cumulative_own = calculate_cumulative(own_times_seconds)
    cumulative_avg = calculate_cumulative(avg_seconds)

    chart_data = {
        "Durchschnitt": cumulative_avg,
        athlete: cumulative_own,
    }

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

    with st.container(border=True, width="content"):
        st.header("LaLi Hamburg Analytics")

    csv_files = get_csv_files()

    selected_race = st.radio(
        label="Select the event:",
        options=csv_files,
    )

    if selected_race:
        df = pd.read_csv(selected_race)

        mode = st.radio(
            label="Modus auswählen:",
            options=["Comparison mode", "Enter own Times"],
            horizontal=True,
        )
        st.session_state["mode"] = mode

        if mode == "Comparison mode":
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


if __name__ == "__main__":
    main()
