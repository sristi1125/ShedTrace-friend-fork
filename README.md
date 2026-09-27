# 🏗️ ShedTrace

**The paper trail behind every shed.**

ShedTrace is a NYC building-safety evidence tool built for **DivHacks 2026**. Enter an address, and it connects real NYC public records for that building — sidewalk shed history, DOB violations, DOB complaints, elevator safety records, and FDNY fire inspections — into one evidence timeline, joined by the building's **BIN (Building Identification Number)**.

## 🔴 Live Demo

**Try it here: [https://8j2cd7ekjnmf3dmnphzsch.streamlit.app/](https://8j2cd7ekjnmf3dmnphzsch.streamlit.app/)**

No setup needed — just open the link and enter an address (see "How to Use" below).

## The Problem

This information already exists, but it's scattered across separate NYC public datasets.

Investigating one building means searching multiple systems by hand, understanding different datasets, matching records to the same building, and piecing the timeline together yourself.

**ShedTrace brings that information together.**

## The Solution

**Enter an address → Find the building's BIN → Confirm an active shed → Pull five public datasets → Join by BIN → Build one evidence timeline.**

Instead of five disconnected sources, ShedTrace presents one building-level profile showing the documented history associated with the shed and building.

## 📖 How to Use

1. Open the [live app](https://8j2cd7ekjnmf3dmnphzsch.streamlit.app/) (or run it locally — see "Getting Started" below).
2. Type a NYC address into the input box. **Try `900 Grand Concourse`** — our tested demo building with a rich record.
3. Click **Investigate Building**.
4. If the building has an active sidewalk shed on file, you'll see the top-level metrics (shed duration, open violations, complaints filed) plus a **3D Map View** of the building.
5. Explore the four tabs:
   - **Shed Timeline** — chronological history of the shed and related violations/complaints
   - **Elevator Safety** — real device records and elevator-specific history
   - **Fire Safety** — real FDNY inspection records, decoded into plain English
   - **Ask AI** — type a question about this specific building and get an answer grounded only in its real data
6. If an address doesn't have a shed on file, ShedTrace will tell you rather than guessing — that's an intentional scope decision (see below).

## Features

### 🏗️ Shed Timeline

* Shed installation and renewal history
* Shed-related records
* DOB violations
* DOB complaints
* Chronological evidence timeline

### 🛗 Elevator Safety

Real elevator device records from **DOB NOW: Elevator Safety Compliance**, including:

* Device type
* Device status
* Last inspection
* Last CAT1 filing
* Elevator-specific violations
* Elevator-related complaints

### 🔥 Fire Safety

Real **FDNY Bureau of Fire Prevention inspection records**, including:

* Inspection records
* Inspection status
* Plain-English explanations of raw status codes
* Fire-related violations
* Fire-related complaints

For example:

`NOT APPROVAL(W/REASON)`

is presented in a more understandable form such as:

**Failed inspection (reason noted)**

### 🗺️ 3D Map View

The investigated building is rendered as a 3D bar on an interactive map.

Bar height reflects the volume of recorded violations and complaints, allowing users to visualize the building's public-record activity spatially.

### 🤖 Ask AI

ShedTrace includes a **Google Gemini-powered assistant** scoped to the currently investigated building.

The assistant receives only that building's retrieved data as context and is instructed to:

* Answer questions using the available evidence
* Explain records in plain English
* Stay within the building's actual data
* Say when the available data does not answer a question
* Never invent missing information

## 🎯 Why Only Buildings With Sidewalk Sheds?

This is an intentional product decision.

ShedTrace's core question is:

> **"Why is this specific shed still standing, and what does the public record show about the building behind it?"**

Rather than building a generic citywide building lookup tool, we focused the hackathon version on buildings with an active sidewalk shed.

The underlying **BIN-based architecture** could be extended to additional buildings and datasets in the future.

## 🏛️ Data Sources

ShedTrace uses public government data from **NYC Open Data and FDNY**.

### NYC Open Data

* Sidewalk Shed Permits
* DOB Violations
* DOB Complaints Received
* DOB NOW: Elevator Safety Compliance — `e5aq-a4j2`

### FDNY

* Bureau of Fire Prevention Inspections — `ssq6-fkht`

The datasets are joined at the building level using the **BIN (Building Identification Number)**.

## 🧪 Demo Building

Our primary demo building is:

### 900 Grand Concourse

* **14.8-year-old active shed**
* **106 violations**
* **215 complaints**
* Elevator safety records
* FDNY fire inspection records
* Unified evidence timeline

## 🛠️ Tech Stack

* **Python** + **pandas** — data processing and pipeline
* **Streamlit** — application UI
* **Google Gemini API** — building-specific AI assistant
* **Docker** + **Docker Compose** — containerized development environment

## 🚀 Getting Started

Want to run it locally instead of using the live demo?

### Clone the repository

```bash
git clone https://github.com/sristi1125/ShedTrace-friend-fork.git
cd ShedTrace-friend-fork
```

### Create your `.env` file

```env
GEMINI_API_KEY=your_api_key_here
```

**Do not commit your API key or `.env` file to GitHub.**

### Run with Docker

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

## ⚠️ Known Limitations

* Data is currently a **snapshot downloaded during development**, not a live feed.
* The application currently works only for buildings with an **active sidewalk shed on file**.
* The elevator dataset provides the **current device status**, but does not provide a complete historical record of status changes.
* Public datasets may have different coverage periods and update schedules.

## 🔮 Future Work

* Live data refresh from NYC Open Data APIs
* Citywide building lookup
* 3D map showing multiple buildings simultaneously
* Historical elevator status tracking
* Additional NYC building-safety datasets
* More detailed source-level record links

## 🤝 AI-Assisted Development

ShedTrace was developed with assistance from several AI tools:

* **Cursor** — AI-assisted coding, development, debugging, and iteration
* **Grok** — research, brainstorming, and development assistance
* **Google Gemini API** — integrated into the application as the building-specific AI assistant

The application and its data pipeline were developed and integrated as part of the ShedTrace project.

---

### 🏗️ Built for DivHacks 2026

**ShedTrace — The paper trail behind every shed.**
