import requests
import pandas as pd
import json
import re

# Gewünschte Spalten (0-basiert: 3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 18)
SPALTEN_INDICES = [3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 18]
SPALTEN_INDICES_NAMES = [
    "StatusPlatz([MWPl.P])",
    "LL_gewertet_Listen",
    "NAME",
    "Teamname",
    "LL_Teamname",
    "AGEGROUP1.NAMESHORT",
    '[TIME21.TEXT] & if([MWPlSwim]\u003e0;" (" & [MWPlSwim.P] & ")";"")',
    '[TIME22.TEXT] & if([MWPlT1]\u003e0;" (" & [MWPlT1.P] & ")";"")',
    '[TIME23.TEXT] & if([MWPlBike]\u003e0;" (" & [MWPlBike.P] & ")";"")',
    '[TIME24.TEXT] & if([MWPlT2]\u003e0;" (" & [MWPlT2.P] & ")";"")',
    '[TIME25.TEXT] & if([MWPlRun]\u003e0;" (" & [MWPlRun.P] & ")";"")',
    "StatusZeit([Ergebnis])",
    "StatusZeit([TIME1])",
]
# Benutzerdefinierte Überschriften (nur für die extrahierten Spalten)
SPALTEN_HEADER = [
    "Platzierung",
    "gewertet",
    "Name",
    "Team",
    "AK",
    "Swim",
    "T1",
    "Bike",
    "T2",
    "Run",
    "Zielzeit",
]

# Spalten, die Zeit und Platzierung enthalten (Format: "m:ss (##.)")
# Index bezieht sich auf die Position in SPALTEN_HEADER (NACH Extraktion, VOR Gruppenspalte)
# Format: Spaltenname → Name der neuen Platzierungsspalte
SPALTEN_MIT_PLATZIERUNG = {
    "Swim": "Platzierung Swim",
    "T1": "Platzierung T1",
    "Bike": "Platzierung Bike",
    "T2": "Platzierung T2",
    "Run": "Platzierung Run",
}

page_url = [
    "https://my.raceresult.com/307956/#0_E521CB",  # Stadtparktriathlon
    "https://my.raceresult.com/316831/#0_3F32F2",  # Vierlandentriathlon
    "https://my.raceresult.com/329031/#0_25101B",  # Itzehoe
    "https://my.raceresult.com/306109/#0_1CF814",  # Elbe
    "https://my.raceresult.com/329307/#0_C79D14",  # Norderstedt
]

# Event-spezifische Konfiguration
EVENT_CONFIG = {
    "307956": {
        "name": "Stadtparktriathlon 2025",
        "key": "d38c380bbe8499b4ef9e3336612e74ff",
        "listname": "B Landes-/Verbandsliga HH|TLL/TVL HH Ergebnisliste",
        "groups": [
            "#1_Landesliga Hamburg Herren (8:30 Uhr)",
            "#2_Landesliga Hamburg Damen (8:50 Uhr)",
            "#3_Verbandsliga Hamburg Herren (8:40 Uhr)",
        ],
    },
    "316831": {
        "name": "Vierlandentriathlon 2025",
        "key": "79eb1ce669668eb982fd47653ba6b8bf",
        "listname": "a Landes-/Verbandsliga HH|Ergebnisliste MW+AK",
        "groups": [
            "#1_Landesliga Hamburg Herren",
            "#2_Landesliga Hamburg Damen",
            "#3_Verbandsliga Hamburg",
        ],
    },
    "329031": {
        "name": "Itzehoe Triathlon 2025",
        "key": "e88d73af43f47926db771a86c3393005",
        "listname": "a Landes-/Verbandsliga HH|TLL HH Ergebnisliste",
        "groups": [
            "#1_Landesliga Hamburg Herren",
            "#2_Landesliga Hamburg Damen",
            "#3_Verbandsliga Hamburg",
        ],
    },
    "306109": {
        "name": "Elbe Triathlon 2025",
        "key": "43d0247d6e5ddb6068552d0ff30ff492",
        "listname": "a Landes-/Verbandsliga HH|TLL/TVL HH Ergebnisliste",
        "groups": [
            "#1_Landesliga Hamburg Herren",
            "#2_Landesliga Hamburg Damen",
            "#3_Verbandsliga Hamburg Herren",
        ],
    },
    "329307": {
        "name": "Norderstedt Triathlon 2025",
        "key": "91cbfd78b9c883f0524e6e1bc83500f3",
        "listname": "A Landes-/Verbandsliga HH|TLL/TVL HH Ergebnisliste",
        "groups": [
            "#1_Landesliga Hamburg Herren",
            "#2_Landesliga Hamburg Damen",
            "#3_Verbandsliga Hamburg Herren",
        ],
    },
}


def extract_event_id(url):
    """
    Extrahiert die Event-ID aus der URL
    """
    match = re.search(r"/(\d+)", url)
    if match:
        return match.group(1)
    return None


def build_api_url(event_id, group_name=None):
    """
    Erstellt die vollständige API-URL mit allen Parametern
    """
    if event_id not in EVENT_CONFIG:
        print(f"⚠ Event {event_id} nicht in Konfiguration gefunden")
        return None, None

    config = EVENT_CONFIG[event_id]
    base_url = f"https://my1.raceresult.com/{event_id}/RRPublish/data/list"

    params = {
        "key": config["key"],
        "listname": config["listname"],
        "page": "results",
        "contest": "0",
        "r": "group",
        "f": "",
    }

    if group_name:
        params["name"] = group_name

    return base_url, params


def fetch_raceresult_data(url, params):
    """
    Ruft die Raceresult-API ab und gibt die Daten zurück
    """
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print(f"  ✗ HTTP-Fehler: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON-Fehler: {e}")
        return None


def parse_time_and_rank(value):
    """
    Parst Werte im Format "m:ss (##.)" oder "mm:ss (##.)"
    Gibt Tupel zurück: (Zeit, Platzierung)
    """
    if not value or pd.isna(value):
        return None, None

    value_str = str(value).strip()

    # Regex-Pattern für "Zeit (Platzierung.)"
    # Beispiele: "1:21 (6.)", "12:34 (10.)", "1:21:34 (5.)"
    pattern = r"^([\d:]+)\s*\((\d+)\.\)$"
    match = re.match(pattern, value_str)

    if match:
        time = match.group(1)
        rank = match.group(2)
        return time, rank

    # Falls kein Match, gib Originalwert zurück
    return value_str, None


def split_time_rank_columns(df):
    """
    Trennt Zeit und Platzierung in separaten Spalten
    """
    # Erstelle eine Kopie des DataFrames
    df_processed = df.copy()

    # Für jede Spalte mit Zeit und Platzierung
    for time_col_name, rank_col_name in SPALTEN_MIT_PLATZIERUNG.items():
        # Wenn die Spalte existiert
        if time_col_name in df_processed.columns:
            # Parse jede Zeile
            parsed_data = df_processed[time_col_name].apply(parse_time_and_rank)

            # Extrahiere Zeit und Platzierung
            times = [item[0] for item in parsed_data]
            ranks = [item[1] for item in parsed_data]

            # Aktualisiere die Zeitspalte (nur die Zeit)
            df_processed[time_col_name] = times

            # Füge die Platzierungsspalte direkt nach der Zeitspalte ein
            col_position = df_processed.columns.get_loc(time_col_name) + 1
            df_processed.insert(col_position, rank_col_name, ranks)

    return df_processed


def extract_specific_columns(data, column_indices, spalten_header, group_name=""):
    """
    Extrahiert nur die gewünschten Spalten und benennt sie um
    """
    if not data:
        return None

    # Daten-Array finden
    if "data" in data:
        rows = data["data"]
    elif "rows" in data:
        rows = data["rows"]
    elif isinstance(data, list):
        rows = data
    else:
        return None

    if not rows:
        print(f"  ⚠ Keine Daten vorhanden")
        return None

    # Extrahiere gewünschte Spalten
    extracted_data = []

    for row in rows:
        if isinstance(row, list):
            selected_values = []
            for idx in column_indices:
                if idx < len(row):
                    selected_values.append(row[idx])
                else:
                    selected_values.append(None)
            extracted_data.append(selected_values)

        elif isinstance(row, dict):
            values = list(row.values())
            selected_values = []
            for idx in column_indices:
                if idx < len(values):
                    selected_values.append(values[idx])
                else:
                    selected_values.append(None)
            extracted_data.append(selected_values)

    # DataFrame erstellen
    df = pd.DataFrame(extracted_data, columns=spalten_header)

    # Trenne Zeit und Platzierung
    df = split_time_rank_columns(df)

    # Füge Gruppennamen als erste Spalte hinzu
    if group_name:
        df.insert(0, "Wettkampf", group_name)

    return df


def process_event(event_id):
    """
    Verarbeitet alle Gruppen eines Events
    """
    if event_id not in EVENT_CONFIG:
        print(f"✗ Event {event_id} nicht konfiguriert")
        print(f"  Verfügbare Events: {', '.join(EVENT_CONFIG.keys())}")
        return []

    config = EVENT_CONFIG[event_id]
    groups = config["groups"]

    print(f"\nEvent: {config.get('name', event_id)}")
    print(f"Verarbeite {len(groups)} Gruppe(n):\n")
    all_dataframes = []

    for i, group_name in enumerate(groups, 1):
        print(f"[{i}/{len(groups)}] {group_name}")

        # Erstelle API-URL
        base_url, params = build_api_url(event_id, group_name)

        if not base_url:
            print("  ✗ Konnte URL nicht erstellen")
            continue

        # Daten abrufen
        data = fetch_raceresult_data(base_url, params)

        if data:
            SPALTEN_INDICES_SORTED = []
            for key in SPALTEN_INDICES_NAMES:
                try:
                    SPALTEN_INDICES_SORTED.append(data["DataFields"].index(key))
                except ValueError:
                    pass
            df = extract_specific_columns(
                data, SPALTEN_INDICES_SORTED, SPALTEN_HEADER, group_name
            )

            if df is not None and not df.empty:
                all_dataframes.append(df)
                print(f"  ✓ {len(df)} Datensätze")
            else:
                print(f"  ⚠ Keine Daten")
        else:
            print(f"  ✗ Abruf fehlgeschlagen")

        print()

    return all_dataframes


def save_results(dataframes, output_format="csv", filename_prefix="raceresult"):
    """
    Speichert die Ergebnisse
    """
    if not dataframes:
        print("✗ Keine Daten zum Speichern")
        return None

    combined_df = pd.concat(dataframes, ignore_index=True)

    if output_format == "csv":
        filename = f"{filename_prefix}_export.csv"
        combined_df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"✓ Gespeichert: {filename}")

    elif output_format == "excel":
        filename = f"{filename_prefix}_export.xlsx"

        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            combined_df.to_excel(writer, sheet_name="Alle Gruppen", index=False)

            for df in dataframes:
                if not df.empty and "Wettkampf" in df.columns:
                    group_name = df["Wettkampf"].iloc[0]
                    sheet_name = re.sub(r"[^\w\s-]", "", group_name)[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✓ Gespeichert: {filename}")

    return combined_df


def add_event_config(event_id, key, listname, groups):
    """
    Fügt eine neue Event-Konfiguration hinzu
    """
    EVENT_CONFIG[event_id] = {"key": key, "listname": listname, "groups": groups}
    print(f"✓ Event {event_id} konfiguriert")


def main():
    print("=" * 70)
    print(" RACERESULT DATEN-EXTRAKTOR")
    print("=" * 70)

    # KONFIGURATION: Geben Sie die Raceresult-URL ein

    # Extrahiere Event-ID
    event_id = []

    for url in page_url:
        event_id.append(extract_event_id(url))

    if not event_id:
        print("✗ Konnte Event-ID nicht extrahieren")
        return

    print(f"\nEvent-ID: {event_id}")
    print(f"URL: {page_url}\n")

    # ============================================================================
    # WICHTIG: Für neue Events müssen Sie die Konfiguration hinzufügen
    # ============================================================================
    # Beispiel für ein neues Event:
    # add_event_config(
    #     event_id='IHRE_EVENT_ID',
    #     key='IHR_API_KEY',
    #     listname='IHR_LISTENNAME',
    #     groups=['#1_Gruppe1', '#2_Gruppe2', '#3_Gruppe3']
    # )
    # ============================================================================

    # Verarbeite Event
    for id in event_id:
        dataframes = process_event(id)

        if dataframes:
            print("=" * 70)
            total_rows = sum(len(df) for df in dataframes)
            print(f"✓ {len(dataframes)} Gruppe(n) | {total_rows} Datensätze extrahiert")

            print("\nSpeichere Daten...")
            combined_df = save_results(
                dataframes,
                output_format="csv",
                filename_prefix=f"raceresult_{EVENT_CONFIG[id]['name']}",
            )
            # save_results(dataframes, output_format='excel', filename_prefix=f'raceresult_{event_id}')

            print("\n" + "=" * 70)
            print("✓ FERTIG!")
            print("=" * 70)
        else:
            print("=" * 70)
            print("✗ KEINE DATEN EXTRAHIERT")
            print("=" * 70)
            print("\nHinweis: Für neue Events müssen Sie die Konfiguration hinzufügen.")
            print(
                "Verwenden Sie die Browser DevTools (F12 → Network), um die Parameter"
            )
            print("key, listname und groups zu ermitteln, und fügen Sie sie mit")
            print("add_event_config() hinzu.")


if __name__ == "__main__":
    main()
