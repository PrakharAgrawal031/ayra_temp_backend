import google.generativeai as genai
import re
import json
from dotenv import load_dotenv
import os
from typing import List, Dict, Any

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY") or "AIzaSyCzVYKe8ROV0e-7E3flTm_2Xm1uQjwWbvw"

if not GEMINI_KEY:
    raise ValueError("GEMINI_KEY environment variable is not set. Please add it to your .env file.")

try:
    genai.configure(api_key=GEMINI_KEY)
    client = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    raise RuntimeError(f"Failed to configure Gemini API: {e}")


def evaluate_patient_record(all_emr_data):
    GEMINI_KEY = os.getenv("GEMINI_KEY")
    try:
        # Replace "YOUR_API_KEY_HERE" with your key from Google AI Studio
        genai.configure(api_key=GEMINI_KEY)
    except Exception as e:
        print(f"Error configuring API. Make sure you've replaced 'YOUR_API_KEY_HERE'. Error: {e}")

    """
    Evaluates patient record using Gemini API and structures it into fixed UI sections:
    - Last Visit Summary
    - Correlation Matrix 
    - Family History
    - Comparison of Prominent Data Points
    - Important Vitals
    """

    prompt = f"""
    You are a Doctor Record Evaluator AI.

    You are given a patient's medical record or report data. 
    You must return a JSON response structured strictly as follows:

    {{
      "LastVisitSummary": ["...", "...", "..."],
      "CorrelationMatrix": {{
          "Observation": {{
                            "key": "...",
                            "description": "...",
                            "impact": "direct|indirect"
                         }},
          "CorrelatedFactors": [
                                {{
                                    "key": "...",
                                    "description": "...",
                                    "impact": "direct|indirect"
                                }}
                                ]
      }},
      "FamilyHistory": {{
          "Conditions": [
                        {{
                            "condition": "...",
                            "family-member":"..."
                        }}
                        ],
          "Remarks": "...",
          "Sources": ["Notes: dd-mm-yyyy", "Blood Report: dd-mm-yyyy"]
      }},

      "ComparisonOfProminentDataPoints": [
          {{
              "DataPoint": "...",
              "LastVisit": "...",
              "CurrentEvaluation": "...",
              "Change": "...",
              "Connection": "..."
          }}
      ],

      "ImportantVitals": {{
          "BloodPressure": "...",
          "HeartRate": "...",
          "Temperature": "...",
          "OxygenLevel": "...",
          "OtherVitals": ["..."],
          "Sources": ["Notes: dd-mm-yyyy", "Blood Report: dd-mm-yyyy"]
      }}
    }}

    CRITICAL COLOR CODING RULES - FOLLOW EXACTLY:

    1. COLOR CODE LEGEND:
       - Chronology (dates/times): #754BAB
       - Vitals/Numerical Values (BP, heart rate, lab values, measurements): #DF7635
       - Prescriptions (medications, vaccinations, treatments): #12909B

    2. WHAT TO COLOR CODE:
       ✓ Dates in format DD-MM-YYYY or MM/DD/YYYY → #754BAB
       ✓ Numerical measurements (120/80, 98.6°F, 58 U/L, 150 mg/dL) → #DF7635
       ✓ Medication names and dosages (Aspirin 100mg, Metformin) → #12909B

    3. WHAT NOT TO COLOR CODE:
       ✗ Medical condition names (hypertension, diabetes, fever)
       ✗ Symptoms (headache, nausea, fatigue)
       ✗ Body parts or organs (heart, liver, kidney)
       ✗ Test names (blood test, ECG, X-ray)
       ✗ General descriptive text
       ✗ Keys in CorrelationMatrix (key and impact fields)

    4. SPECIFIC SECTION RULES:

       LastVisitSummary:
       - Color code: dates (#754BAB), vital values (#DF7635), medications (#12909B)
       - DO NOT color code: condition names, symptoms, test names
       - Example: "Patient presented with elevated BP of <span style='color: #DF7635;'>140/90</span> on <span style='color: #754BAB;'>15-10-2024</span>"

       CorrelationMatrix:
       - In "description" field: color code dates, values, and medications
       - DO NOT color code: "key" field or "impact" field
       - Example description: "BP elevated to <span style='color: #DF7635;'>145/95</span> correlating with stress"

       ComparisonOfProminentDataPoints:
       - DO NOT color code dates in "LastVisit" and "CurrentEvaluation" columns
       - DO color code vital/numerical values in "LastVisit" and "CurrentEvaluation" columns
       - Example LastVisit: "<span style='color: #DF7635;'>120/80</span>" NOT "<span style='color: #754BAB;'>12-10-2024</span>"

       ImportantVitals:
       - Color code all numerical values → #DF7635
       - Example: "BloodPressure": "<span style='color: #DF7635;'>120/80 mmHg</span>"

       FamilyHistory:
       - Color code dates if mentioned → #754BAB
       - DO NOT color code condition names
       - Example: "Mother diagnosed with diabetes in <span style='color: #754BAB;'>2010</span>"

    5. HTML FORMAT (NO SPACES IN TAGS):
       Correct: <span style="color: #DF7635;">58 U/L</span>
       Wrong: < span style="color: #DF7635;" > 58 U/L < / span >

    GENERAL GUIDELINES:
    - Date format: MM/DD/YYYY throughout the response
    - LastVisitSummary: Array of 3-5 concise bullet points, most critical information only
    - CorrelationMatrix keys: 2-3 words maximum
    - CorrelationMatrix descriptions: 1-2 short sentences maximum
    - Include at least one "indirect" correlation if relevant
    - Use "Not Available" for missing data
    - Generate 2-3 realistic family history conditions for demo (if appropriate)
    - Add "Sources" object to all sections except ComparisonOfProminentDataPoints
    - Be factual and concise

    VALIDATION CHECKLIST BEFORE RESPONDING:
    □ No condition names are color coded
    □ All numerical vital values use #DF7635
    □ All dates use #754BAB
    □ All medications use #12909B
    □ CorrelationMatrix "key" and "impact" have NO color codes
    □ ComparisonOfProminentDataPoints dates are NOT color coded
    □ No spaces in <span> tags
    □ Valid JSON only (no markdown, no explanation)

    Patient Data:
    {json.dumps(all_emr_data, indent=2)}

    Respond ONLY with valid JSON. No additional text, explanation, or markdown formatting.
    """

    try:
        # Use the defined client object
        response = client.generate_content(prompt)

        cleaned_text = response.text.strip()

        # Remove markdown code fences if present
        if cleaned_text.startswith("```json"):
            # Using re.sub for robust removal of code fences
            cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        elif cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

        result = json.loads(cleaned_text)
        return result

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {cleaned_text[:500]}...")
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")

    except Exception as e:
        print("Error evaluating patient record:", e)
        # Re-raise the exception after printing, or return an error structure
        # raise
        return {"error": str(e)}  # Return a simple error structure for demonstration



def generate_graph_data(clinical_timeline: List[Dict[str, Any]], user_prompt: str):
    GEMINI_KEY = os.getenv("GEMINI_KEY")
    try:
        # Replace "YOUR_API_KEY_HERE" with your key from Google AI Studio
        genai.configure(api_key=GEMINI_KEY)
    except Exception as e:
        print(f"Error configuring API. Make sure you've replaced 'YOUR_API_KEY_HERE'. Error: {e}")

    """
    Generates data for a graph based on a user prompt and clinical timeline.
    """
    graph_prompt = f"""
    You are an advanced Clinical Data Extraction AI for Graphing.

    You will be given a user's prompt and a patient's clinical timeline.
    Your task is to extract relevant data points and return a single JSON object.

    **Graph Types:**

    1.  **Single-Metric Request:** If the prompt asks for one value over time (e.g., "Generate graph for weight changes overtime").
    2.  **Dual-Metric Request:** If the prompt asks for two values (e.g., "Generate graph for weight changes with change in GFR").

    ---
    **Strict Output Format:**
    The output **must** be a valid JSON object.

    - "xAxisLabel": Should always be "Date" in this format "MM/DD/YYYY".
    - "y1AxisLabel": A descriptive label for the first data metric (e.g., "Weight (Kg)").
    - "y2AxisLabel": A descriptive label for the second metric. Send `null` if it's a Single-Metric Request.
    - "y1AxisMin": The minimum value for the Y1-axis, *only if* specified by the user. Send `null` if not specified.
    - "y1AxisMax": The maximum value for the Y1-axis, *only if* specified by the user. Send `null` if not specified.
    - "y2AxisMin": The minimum value for the Y2-axis, *only if* specified by the user. Send `null` if not specified.
    - "y2AxisMax": The maximum value for the Y2-axis, *only if* specified by the user. Send `null` if not specified.
    - "description": "A concise 1-2 sentence factual summary..."
    - "description": "A concise 1-2 sentence factual summary of the data trend. **Strictly no suggestions or diagnosis.** (e.g., 'CK Level (U/L) shows a slight upward trend.', 'Weight (Kg) increased while GFR (mL/min/1.73m²) decreased.')"
    - "data": A JSON array of objects. Each object **must** have "x", "y1", and "y2" keys.
      - "x": The date of the timeline entry.
      - "y1": The numerical value for the first metric on that date. Send `null` if it's not present.
      - "y2": The numerical value for the second metric on that date. Send `null` if it's not present or if it's a Single-Metric Request.

    ---
    **Example 1: Single-Metric Request**
    * **User Prompt:** "Show me the patient's CK levels over time."
    * **Example Output:**
        ```json
        {{
          "xAxisLabel": "Date",
          "y1AxisLabel": "CK Level (U/L)",
          "y2AxisLabel": null,
          "description": "Shows the patient's CK Level (U/L), which increased from 120 to 125 over this period.",
          "data": [
            {{"x": "01/15/2023", "y1": 120, "y2": null}},
            {{"x": "03/22/2023", "y1": 125, "y2": null}}
          ]
        }}
        ```

    **Example 2: Dual-Metric Request (with Custom Y-Axis Range)**
    * **User Prompt:** "Plot weight against GFR. **Please set the weight axis from 70 to 80.**"
    * **Example Output:**
        ```json
        {{
          "xAxisLabel": "Date",
          "y1AxisLabel": "Weight (Kg)",
          "y2AxisLabel": "GFR (mL/min/1.73m²)",
          "y1AxisMin": 70.0,
          "y1AxisMax": 80.0,
          "y2AxisMin": null,
          "y2AxisMax": null,
          "description": "Shows Weight (Kg) and GFR (mL/min/1.73m²). Weight is shown increasing from 75.0 to 76.5, while GFR decreased from 60.0 to 58.0.",
          "data": [
            {{"x": "01/15/2023", "y1": 75.0, "y2": 60.0}},
            {{"x": "02/10/2023", "y1": 76.5, "y2": null}},
            {{"x": "03/22/2023", "y1": null, "y2": 58.0}}
          ]
        }}
        ```

    ---
    **Instructions (CRITICAL):**
    1.  **Analyze the Prompt:** Determine if it's a Single-Metric or Dual-Metric request.
    2.  **Scan the Timeline:** Go through the *entire* `clinical_timeline`.
    3.  **Merge by Date:** Create a *single* `data` object for **each date** in the timeline that contains *at least one* of the requested metrics.
    4.  **Populate Data:**
        * For a Single-Metric request, fill `y1` and set `y2` to `null`.
        * For a Dual-Metric request, fill both `y1` and `y2`. If a metric is missing on a specific date, set its value to `null` for that date.
    5.  **Legend:** (Chronology: #754BAB,
                     Vitals/Values: #DF7635,
                     Rx (Medications, Vaccinations): #12909B)
    6.  ** Using Legend: ** Put every Chronological / Vital / Condition values in < span > tags and assign respective colour values from legend, for example->< span style="color: #DF7635;" > 58 U/L < / span > on < span style="color: #754BAB;" > 25-12-2025 < / span > in graph description section only.Only specific values not entire lines.
    7.  **Labels, Range & Description:** Identify metrics and create labels. **Scan the user's prompt for explicit Y-axis range requests (e.g., "from 70 to 80", "set weight axis 75-100").** If found, extract the numbers and populate the corresponding `y1AxisMin/Max` or `y2AxisMin/Max` fields. If not found, set them all to `null`. Generate the factual `description` and provide no medical advice.
    8.  **Data Extraction:** Always extract only the numerical value (e.g., "75 kg" -> 75).
    9.  **Response:** Respond **only** with the valid JSON object.

    ---
    HERE IS THE DATA TO ANALYZE:

    **User's Prompt:**
    "{user_prompt}"

    **Patient's Clinical Timeline:**
    {json.dumps(clinical_timeline, indent=2)}
    """
    try:
        response = client.generate_content(graph_prompt)

        # --- START DEBUGGING ---
        # Add this print statement to see the raw API response
        print("--- RAW GEMINI RESPONSE ---")
        print(response)
        print("---------------------------")
        # --- END DEBUGGING ---

        cleaned_text = response.text.strip()

        if cleaned_text.startswith("```json"):
            cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        elif cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

        if not cleaned_text:
            # CORRECTED LINE: Return a valid object, not an empty list.
            return {"xAxisLabel": "Date", "yAxisLabel": "Not Available", "data": []}

        result = json.loads(cleaned_text)
        return result

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {cleaned_text[:500]}...")
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")

    except Exception as e:
        print(f"Error generating graph data: {e}")
        return {"error": str(e)}