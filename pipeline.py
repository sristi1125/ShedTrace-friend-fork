"""
ShedTrace data pipeline.
"""

import pandas as pd
from datetime import datetime
from complaint_codes import describe_complaint_category
from safety_categories import classify_violation, classify_complaint

DATA_DIR = "data/"

SHED_FILE = DATA_DIR + "sidewalk_sheds.csv"
SHED_BIN_COL = "BIN Number"
SHED_ISSUE_COL = "First Permit Date"
SHED_EXPIRY_COL = "Permit Expiration Date"
SHED_HOUSE_COL = "House Number"
SHED_STREET_COL = "Street Name"

# Update these two to match your sidewalk-shed CSV's real coordinate columns.
SHED_LAT_COL = "Latitude Point"
SHED_LON_COL = "Longitude Point"

VIOLATIONS_FILE = DATA_DIR + "dob_violations.csv"
VIOL_BIN_COL = "BIN"
VIOL_DATE_COL = "Violation Issue Date"
VIOL_STATUS_COL = "Violation Status"
VIOL_DESC_COL = "Violation Remarks"

COMPLAINTS_FILE = DATA_DIR + "dob_complaints.csv"
COMP_BIN_COL = "BIN"
COMP_DATE_COL = "Date Entered"
COMP_TYPE_COL = "Complaint Category"

ELEVATOR_FILE = DATA_DIR + "elevator_safety.csv"
ELEV_BIN_COL = "BIN"
ELEV_DEVICE_NUM_COL = "Device Number"
ELEV_TYPE_COL = "Device Type"
ELEV_STATUS_COL = "Device Status"
ELEV_INSPECTION_COL = "Periodic Latest Inspection Date"
ELEV_CAT1_COL = "CAT1 Latest Report Filed Date"

FIRE_FILE = DATA_DIR + "fire_safety.csv"
FIRE_BIN_COL = "BIN"
FIRE_STATUS_COL = "LAST_INSP_STAT"
FIRE_VISIT_COL = "LAST_VISIT_DT"
FIRE_INSPECTION_COL = "LAST_FULL_INSP_DT"
FIRE_OWNER_COL = "OWNER_NAME"

# Map severity thresholds: open violations + complaints filed against a BIN.
SEVERITY_ORANGE_AT = 3
SEVERITY_RED_AT = 7

GREEN = [61, 149, 96, 200]
ORANGE = [200, 120, 0, 200]
RED = [217, 71, 58, 200]


def _clean_bin(series):
    """These BIN columns arrive as floats like 1001627.0 -- convert to a
    clean string '1001627' so it matches the shed/violation BIN strings."""
    return (
        pd.to_numeric(series, errors="coerce")
        .fillna(0)
        .astype(int)
        .astype(str)
    )


def load_data():
    sheds = pd.read_csv(SHED_FILE, low_memory=False)
    violations = pd.read_csv(VIOLATIONS_FILE, low_memory=False)
    complaints = pd.read_csv(COMPLAINTS_FILE, low_memory=False)
    elevator = pd.read_csv(ELEVATOR_FILE, low_memory=False)
    fire = pd.read_csv(FIRE_FILE, low_memory=False)

    sheds[SHED_BIN_COL] = sheds[SHED_BIN_COL].astype(str)
    violations[VIOL_BIN_COL] = violations[VIOL_BIN_COL].astype(str)
    complaints[COMP_BIN_COL] = complaints[COMP_BIN_COL].astype(str)
    elevator[ELEV_BIN_COL] = _clean_bin(elevator[ELEV_BIN_COL])
    fire[FIRE_BIN_COL] = _clean_bin(fire[FIRE_BIN_COL])

    return sheds, violations, complaints, elevator, fire


def find_bin_for_address(sheds_df, address: str):
    address_norm = address.strip().lower()
    combined = (
        sheds_df[SHED_HOUSE_COL].astype(str) + " " + sheds_df[SHED_STREET_COL].astype(str)
    ).str.lower()
    matches = sheds_df[combined.str.contains(address_norm, na=False)]
    if matches.empty:
        return None
    return matches.iloc[0][SHED_BIN_COL]


def get_address_for_bin(sheds_df, bin_number):
    rows = sheds_df[sheds_df[SHED_BIN_COL] == bin_number]
    if rows.empty:
        return None
    row = rows.iloc[0]
    return f"{row[SHED_HOUSE_COL]} {row[SHED_STREET_COL]}"


def get_shed_history(sheds_df, bin_number):
    rows = sheds_df[sheds_df[SHED_BIN_COL] == bin_number]
    if rows.empty:
        return None

    events = []
    for _, row in rows.iterrows():
        issue = pd.to_datetime(row[SHED_ISSUE_COL], errors="coerce")
        if pd.notnull(issue):
            events.append({"date": issue, "type": "shed_installed_or_renewed"})

    if not events:
        return None

    earliest = min(e["date"] for e in events)
    duration_days = (datetime.now() - earliest).days

    return {
        "first_permit_date": earliest,
        "duration_days": duration_days,
        "duration_years": round(duration_days / 365, 1),
        "renewal_count": len(events),
        "events": events,
    }


def get_violations(violations_df, bin_number):
    rows = violations_df[violations_df[VIOL_BIN_COL] == bin_number]
    result = []
    for _, row in rows.iterrows():
        result.append({
            "date": pd.to_datetime(row[VIOL_DATE_COL], errors="coerce"),
            "status": row.get(VIOL_STATUS_COL),
            "description": row.get(VIOL_DESC_COL),
        })
    return result


def get_complaints(complaints_df, bin_number):
    rows = complaints_df[complaints_df[COMP_BIN_COL] == bin_number]
    result = []
    for _, row in rows.iterrows():
        result.append({
            "date": pd.to_datetime(row[COMP_DATE_COL], errors="coerce"),
            "type": row.get(COMP_TYPE_COL),
            "type_label": describe_complaint_category(row.get(COMP_TYPE_COL)),
        })
    return result


def get_elevator_safety(elevator_df, bin_number):
    rows = elevator_df[elevator_df[ELEV_BIN_COL] == bin_number]
    result = []
    for _, row in rows.iterrows():
        result.append({
            "device_number": row.get(ELEV_DEVICE_NUM_COL),
            "device_type": row.get(ELEV_TYPE_COL),
            "status": row.get(ELEV_STATUS_COL),
            "last_inspection": pd.to_datetime(row.get(ELEV_INSPECTION_COL), errors="coerce"),
            "last_cat1_filed": pd.to_datetime(row.get(ELEV_CAT1_COL), errors="coerce"),
        })
    return result


def get_fire_safety(fire_df, bin_number):
    rows = fire_df[fire_df[FIRE_BIN_COL] == bin_number]
    result = []
    for _, row in rows.iterrows():
        result.append({
            "owner": row.get(FIRE_OWNER_COL),
            "status": row.get(FIRE_STATUS_COL),
            "last_visit": pd.to_datetime(row.get(FIRE_VISIT_COL), errors="coerce"),
            "last_full_inspection": pd.to_datetime(row.get(FIRE_INSPECTION_COL), errors="coerce"),
        })
    return result


def get_elevator_related_violations(violations_df, bin_number):
    all_v = get_violations(violations_df, bin_number)
    return [v for v in all_v if classify_violation(v["description"]) == "elevator"]


def get_elevator_related_complaints(complaints_df, bin_number):
    all_c = get_complaints(complaints_df, bin_number)
    return [c for c in all_c if classify_complaint(c["type"]) == "elevator"]


def get_fire_related_violations(violations_df, bin_number):
    all_v = get_violations(violations_df, bin_number)
    return [v for v in all_v if classify_violation(v["description"]) == "fire"]


def get_fire_related_complaints(complaints_df, bin_number):
    all_c = get_complaints(complaints_df, bin_number)
    return [c for c in all_c if classify_complaint(c["type"]) == "fire"]


def build_timeline(shed_history, violations, complaints):
    timeline = []

    for e in shed_history["events"]:
        timeline.append((e["date"], "Shed installed/renewed"))

    for v in violations:
        if pd.notnull(v["date"]):
            label = f"Violation: {v['description']}"
            if v["status"] and "open" in str(v["status"]).lower():
                label += " (still open)"
            timeline.append((v["date"], label))

    for c in complaints:
        if pd.notnull(c["date"]):
            timeline.append((c["date"], f"Complaint: {c['type_label']}"))

    timeline.sort(key=lambda x: x[0])
    return timeline


def get_building_report_by_bin(bin_number, sheds_df, violations_df, complaints_df, elevator_df, fire_df):
    """Same report as get_building_report(), but starting from a known BIN
    instead of an address string. Used when the map's click handler hands
    back the BIN of a different building the user clicked on."""

    shed_history = get_shed_history(sheds_df, bin_number)
    if shed_history is None:
        return None

    violations = get_violations(violations_df, bin_number)
    complaints = get_complaints(complaints_df, bin_number)
    timeline = build_timeline(shed_history, violations, complaints)

    elevator_records = get_elevator_safety(elevator_df, bin_number)
    fire_records = get_fire_safety(fire_df, bin_number)

    elevator_related_violations = get_elevator_related_violations(violations_df, bin_number)
    elevator_related_complaints = get_elevator_related_complaints(complaints_df, bin_number)

    fire_related_violations = get_fire_related_violations(violations_df, bin_number)
    fire_related_complaints = get_fire_related_complaints(complaints_df, bin_number)

    open_violations = [
        v for v in violations
        if v["status"] and "open" in str(v["status"]).lower()
    ]

    return {
        "bin": bin_number,
        "address": get_address_for_bin(sheds_df, bin_number),
        "shed": shed_history,
        "violations": violations,
        "open_violation_count": len(open_violations),
        "complaint_count": len(complaints),
        "timeline": timeline,
        "elevator_records": elevator_records,
        "fire_records": fire_records,
        "elevator_related_violations": elevator_related_violations,
        "elevator_related_complaints": elevator_related_complaints,
        "fire_related_violations": fire_related_violations,
        "fire_related_complaints": fire_related_complaints,
    }


def get_building_report(address: str, sheds_df, violations_df, complaints_df, elevator_df, fire_df):
    bin_number = find_bin_for_address(sheds_df, address)
    if bin_number is None:
        return None

    return get_building_report_by_bin(
        bin_number, sheds_df, violations_df, complaints_df, elevator_df, fire_df
    )


def get_map_context(bin_number, sheds_df, violations_df, complaints_df):
    """
    Builds the DataFrame consumed by map_view.build_deck(): one row per
    currently-active sidewalk shed, with duration, violation/complaint
    counts, a stoplight severity color, and an is_selected flag marking
    the building currently under investigation.

    Returns None if the sheds CSV has no lat/lon columns, or if no active
    shed has usable coordinates.
    """

    if SHED_LAT_COL not in sheds_df.columns or SHED_LON_COL not in sheds_df.columns:
        return None

    df = sheds_df.copy()
    df["_issue_date"] = pd.to_datetime(df[SHED_ISSUE_COL], errors="coerce")
    df["_expiry_date"] = pd.to_datetime(df[SHED_EXPIRY_COL], errors="coerce")

    now = datetime.now()
    active = df[df["_expiry_date"].isna() | (df["_expiry_date"] >= now)]

    if active.empty:
        return None

    earliest_by_bin = active.groupby(SHED_BIN_COL)["_issue_date"].min()
    first_rows = active.drop_duplicates(subset=[SHED_BIN_COL], keep="first").set_index(SHED_BIN_COL)

    open_mask = violations_df[VIOL_STATUS_COL].astype(str).str.contains("open", case=False, na=False)
    open_counts = violations_df[open_mask].groupby(VIOL_BIN_COL).size()
    complaint_counts = complaints_df.groupby(COMP_BIN_COL).size()

    rows = []

    for bin_num, issue_date in earliest_by_bin.items():
        if pd.isnull(issue_date):
            continue

        row = first_rows.loc[bin_num]
        lat = row.get(SHED_LAT_COL)
        lon = row.get(SHED_LON_COL)
        if pd.isnull(lat) or pd.isnull(lon):
            continue

        open_violation_count = int(open_counts.get(bin_num, 0))
        complaint_count = int(complaint_counts.get(bin_num, 0))
        severity = open_violation_count + complaint_count

        if severity >= SEVERITY_RED_AT:
            color = RED
        elif severity >= SEVERITY_ORANGE_AT:
            color = ORANGE
        else:
            color = GREEN

        rows.append({
            "bin": bin_num,
            "lat": float(lat),
            "lon": float(lon),
            "duration_days": (now - issue_date).days,
            "open_violation_count": open_violation_count,
            "complaint_count": complaint_count,
            "color": color,
            "address": f"{row.get(SHED_HOUSE_COL, '')} {row.get(SHED_STREET_COL, '')}".strip(),
            "is_selected": bin_num == bin_number,
        })

    if not rows:
        return None

    return pd.DataFrame(rows)


if __name__ == "__main__":
    sheds, violations, complaints, elevator, fire = load_data()
    print("Loaded", len(sheds), "sheds,", len(violations), "violations,", len(complaints), "complaints,",
          len(elevator), "elevator records,", len(fire), "fire records")

    sample_address = sheds.iloc[0][SHED_HOUSE_COL] + " " + str(sheds.iloc[0][SHED_STREET_COL])
    print("Testing with address:", sample_address)

    report = get_building_report(sample_address, sheds, violations, complaints, elevator, fire)
    print(report)