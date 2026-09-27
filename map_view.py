"""
ShedTrace 3D map.

Renders active sidewalk sheds as extruded columns:
  - height  = how many days the shed has been up (older = taller)
  - color   = severity, stoplight-coded from open violations + complaints
  - the searched building is rendered oversized in gold so it's easy to spot

Requires SHED_LAT_COL / SHED_LON_COL to exist in the sheds CSV (see pipeline.py).
"""

import pydeck as pdk

SELECTED_COLOR = [212, 175, 55, 230]  # gold highlight for the searched building

CONTEXT_LAYER_ID = "context-sheds"
SELECTED_LAYER_ID = "selected-shed"


def build_deck(map_df):
    """map_df comes from pipeline.get_map_context(). Returns a pdk.Deck."""
    selected = map_df[map_df["is_selected"]]
    context = map_df[~map_df["is_selected"]]

    center_lat = selected.iloc[0]["lat"] if not selected.empty else map_df["lat"].mean()
    center_lon = selected.iloc[0]["lon"] if not selected.empty else map_df["lon"].mean()

    layers = []

    if not context.empty:
        layers.append(pdk.Layer(
            "ColumnLayer",
            id=CONTEXT_LAYER_ID,
            data=context,
            get_position="[lon, lat]",
            get_elevation="duration_days",
            elevation_scale=1.2,
            radius=18,
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
        ))

    if not selected.empty:
        layers.append(pdk.Layer(
            "ColumnLayer",
            id=SELECTED_LAYER_ID,
            data=selected,
            get_position="[lon, lat]",
            get_elevation="duration_days + 120",  # pop up above its neighbors
            elevation_scale=1.2,
            radius=28,
            get_fill_color=SELECTED_COLOR,
            pickable=True,
            auto_highlight=True,
        ))

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=16.5,
        pitch=55,
        bearing=15,
    )

    tooltip = {
        "html": (
            "<b>{address}</b><br/>"
            "Shed up: {duration_days} days<br/>"
            "Open violations: {open_violation_count}<br/>"
            "Complaints: {complaint_count}"
        ),
        "style": {"backgroundColor": "#1e1e1e", "color": "white"},
    }

    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_provider="carto",
        map_style="dark",  # Carto's free basemap - no API token needed
    )


def get_clicked_bin(selection_event):
    """
    Pull the BIN out of a st.pydeck_chart selection event, regardless of
    which layer (context vs. selected) was clicked. Returns None if nothing
    new was clicked.
    """
    if selection_event is None:
        return None
    selection = getattr(selection_event, "selection", None)
    if not selection:
        return None
    objects = selection.get("objects", {}) if hasattr(selection, "get") else {}
    for layer_id in (CONTEXT_LAYER_ID, SELECTED_LAYER_ID):
        picked = objects.get(layer_id) or []
        if picked:
            return picked[0].get("bin")
    return None