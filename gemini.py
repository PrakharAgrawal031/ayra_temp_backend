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


def evaluate_patient_record(patient_data):
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

    evaluation_prompt = f"""
You are a Doctor Record Evaluator AI.

You are given a patient's medical record or report data. 
You must return a JSON response structured strictly as follows:

{{
  "LastVisitSummary": "...",
  "CorrelationMatrix": {{
      "Observation": {{
                        "key": "...",
                        "description": "...",
                        "impact": "..."
                     }},
      "CorrelatedFactors": [
                            {{
                                "key": "...",
                                "description": "...",
                                "impact": "..."
                            }},
                            ....
                            ]
  }},
  "FamilyHistory": {{
      "Conditions": [
                    {{
                        "condition": "...",
                        "family-member":"..."
                    }}
                    ],
      "Remarks": "..."
  }},

  //This will be a table with following Columns: Data Points, Last Visit, Current Evaluation, Change, Connection to Symptoms. You are allowed to make changes in JSON format of ComparisonOfProminentDataPoints to achieve this 

  "ComparisonOfProminentDataPoints": [
      {{
          "DataPoint": "...",
          "Last Visit": "...",
          "Current Evaluation": "...",
          "Change": "...",
          "Connection": "..."
      }}
  ],

  "ImportantVitals": {{
      "BloodPressure": "...",
      "HeartRate": "...",
      "Temperature": "...",
      "OxygenLevel": "...",
      "OtherVitals": ["..."]
  }}

}}

Guidelines:
- Use the provided patient data to fill all sections. 
- If data is missing, use "Not Available".
- Be concise and factual.
- Last visit summary should be short and concise and in points. Should be easy to read and should contain only the most important information that would best describe the visit. This field should be a array of strings where each string represent a point.
- In correlations matrix key should only be 2-3 words long and description should be either 1 sentence or 2 short sentences. Also impact field can have value either "direct" or "indirect". You must mention at least one indirect correlation if it looks necessary in patient data. 
- Legend -> (Chronology: #754BAB
             Vitals: #DF7635
             Condition: #2BA27D)
- Put every Chronological/Vital/Condition values in <span> tags and assign respective colour values from legend,for example-> <span style="color: #754BAB;">25-12-2025</span>. Only specific values not entire sentences or paragraphs. Do this for all sections except correlation matrix's key and impact values, but don't leave out description value. 
- At the end of each section(Except ComparisonOfProminentDataPoints) you should add sources JSON Object as well which will have source of information marked. for ex: "Sources": ["Notes": "dd-mm-yyyy", "Blood Report": "dd-mm-yyyy"....] there might not be any sources listed for now so you can fabricate your own as example based on data provided.
- This is only for demo so generate fake Family history for demo purpose if it suits the patient's condition. It should also contain the relation of that family member to patient.
- Respond **only** with valid JSON (no extra text, explanation, or markdown).
Here is the patient data:
{json.dumps(patient_data, indent=2)}
"""

    try:
        # Use the defined client object
        response = client.generate_content(evaluation_prompt)

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

    - "xAxisLabel": Should always be "Date".
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
            {{"x": "2023-01-15", "y1": 120, "y2": null}},
            {{"x": "2023-03-22", "y1": 125, "y2": null}}
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
            {{"x": "2023-01-15", "y1": 75.0, "y2": 60.0}},
            {{"x": "2023-02-10", "y1": 76.5, "y2": null}},
            {{"x": "2023-03-22", "y1": null, "y2": 58.0}}
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
    5.  ** Legend: ** ( Chronology:  # 754BAB
                        Vitals:  # DF7635
                        Condition:  # 2BA27D)
    6.  ** Using Legend: ** Put every Chronological / Vital / Condition values in < span > tags and assign respective colour values from legend, for example-> < span style="color: #754BAB;" > 25-12-2025 < / span > in graph description section only.Only specific values not entire lines.
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