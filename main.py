import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO

st.set_page_config(page_title="VARUNA TC Waveform", layout="wide")

st.title("VARUNA TC Waveform Generator")

# User Inputs
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Select TC Start Date")

with col2:
    start_time = st.time_input("Select TC Start Time")

generate = st.button("Generate Waveform")

if generate:

    # Initial Conditions
    room_temp = 25
    low_temp = -30
    high_temp = 50

    cooling_rate = 1  # °C per minute
    heating_rate = 1  # °C per minute

    dwell_minutes = 10
    cycles = 12

    start_datetime = datetime.combine(start_date, start_time)

    timestamps = []
    temperatures = []

    dwell_annotations = []

    current_time = start_datetime
    current_temp = room_temp

    # Add initial point
    timestamps.append(current_time)
    temperatures.append(current_temp)

    for cycle in range(1, cycles + 1):

        # --------------------------------
        # COOLING: 25 -> -30
        # --------------------------------
        while current_temp > low_temp:
            current_temp -= 1
            current_time += timedelta(minutes=1)

            timestamps.append(current_time)
            temperatures.append(current_temp)

        # Dwell at -30
        dwell_start_low = current_time

        for _ in range(dwell_minutes):
            current_time += timedelta(minutes=1)

            timestamps.append(current_time)
            temperatures.append(current_temp)

        dwell_end_low = current_time

        dwell_annotations.append({
            "label": f"Cycle {cycle} Low Dwell",
            "start": dwell_start_low,
            "end": dwell_end_low,
            "temp": low_temp
        })

        # --------------------------------
        # HEATING: -30 -> 50
        # --------------------------------
        while current_temp < high_temp:
            current_temp += 1
            current_time += timedelta(minutes=1)

            timestamps.append(current_time)
            temperatures.append(current_temp)

        # Dwell at 50
        dwell_start_high = current_time

        for _ in range(dwell_minutes):
            current_time += timedelta(minutes=1)

            timestamps.append(current_time)
            temperatures.append(current_temp)

        dwell_end_high = current_time

        dwell_annotations.append({
            "label": f"Cycle {cycle} High Dwell",
            "start": dwell_start_high,
            "end": dwell_end_high,
            "temp": high_temp
        })

    # --------------------------------
    # RETURN TO ROOM TEMP (25°C)
    # --------------------------------
    while current_temp > room_temp:
        current_temp -= 1
        current_time += timedelta(minutes=1)

        timestamps.append(current_time)
        temperatures.append(current_temp)

    tc_end_time = current_time

    # --------------------------------
    # CREATE DATAFRAME
    # --------------------------------
    df = pd.DataFrame({
        "Time": timestamps,
        "Temperature": temperatures
    })

    # --------------------------------
    # PLOT
    # --------------------------------
    fig, ax = plt.subplots(figsize=(20, 8))

    ax.plot(df["Time"], df["Temperature"],
            color="blue",
            linewidth=2)

    ax.set_title("VARUNA TC Waveform",
                 fontsize=20,
                 fontweight="bold")

    ax.set_xlabel("Time", fontsize=14)
    ax.set_ylabel("Temperature (°C)", fontsize=14)

    ax.grid(True)

    # Start/End markers
    ax.axhline(y=room_temp, color='green',
               linestyle='--', alpha=0.5)

    # Add dwell annotations
    for ann in dwell_annotations:

        midpoint = ann["start"] + \
                   (ann["end"] - ann["start"]) / 2

        text = (
            f"{ann['label']}\n"
            f"Start: {ann['start'].strftime('%d-%m %H:%M')}\n"
            f"End: {ann['end'].strftime('%d-%m %H:%M')}"
        )

        ax.annotate(
            text,
            xy=(midpoint, ann["temp"]),
            xytext=(0, 25),
            textcoords='offset points',
            fontsize=8,
            ha='center',
            arrowprops=dict(arrowstyle='->', lw=0.8)
        )

    # TC Start and End Labels
    fig.text(
        0.01,
        0.01,
        f"TC Start: {start_datetime.strftime('%d-%m-%Y %H:%M')}",
        fontsize=12,
        color='green'
    )

    fig.text(
        0.75,
        0.01,
        f"TC End: {tc_end_time.strftime('%d-%m-%Y %H:%M')}",
        fontsize=12,
        color='red'
    )

    st.pyplot(fig)

    # --------------------------------
    # DOWNLOAD IMAGE
    # --------------------------------
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)

    st.download_button(
        label="Download Waveform Image",
        data=buf,
        file_name="VARUNA_TC_Waveform.png",
        mime="image/png"
    )
