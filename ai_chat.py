"""
Handles talking to Gemini about the currently investigated building.
Only uses the real data already loaded for that building -- it's told
not to make anything up.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.8-flash"


def build_context(address, report):
    """Turn the building report into plain text the AI can read."""
    shed = report["shed"]
    lines = []
    lines.append(f"Building address: {address}")
    lines.append(f"BIN: {report['bin']}")
    lines.append(f"Sidewalk shed has been active for {shed['duration_years']} years.")
    lines.append(f"Shed permit renewals: {shed['renewal_count']}")
    lines.append(f"Open DOB violations: {report['open_violation_count']}")
    lines.append(f"Total complaints filed: {report['complaint_count']}")

    lines.append("\nRecent timeline events:")
    for date, label in report["timeline"][-20:]:
        lines.append(f"- {date.date()}: {label}")

    lines.append(f"\nElevator devices on file: {len(report['elevator_records'])}")
    for e in report["elevator_records"]:
        lines.append(f"- {e['device_type']} (Device #{e['device_number']}): status {e['status']}")

    lines.append(f"\nFire inspection records on file: {len(report['fire_records'])}")
    for f in report["fire_records"]:
        lines.append(f"- Status {f['status']} on visit date {f['last_visit']}")

    return "\n".join(lines)


def ask_ai(address, report, question):
    context = build_context(address, report)

    system_instruction = (
        "You are a helpful assistant inside ShedTrace, a NYC building safety "
        "lookup tool. Answer the user's question using ONLY the building data "
        "provided below. Do not make up information. If the data doesn't "
        "answer the question, say so honestly instead of guessing.\n\n"
        f"BUILDING DATA:\n{context}"
    )

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_instruction,
    )

    response = model.generate_content(question)
    return response.text