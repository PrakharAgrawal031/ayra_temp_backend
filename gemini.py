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
    Your task is to intelligently determine the X and Y axes from the prompt and extract the relevant data points for a graph.

    You must handle two different types of requests:

    1.  **Time-Series Request:** If the prompt asks for a value "overtime" or "against time" (e.g., "Generate graph for weight changes overtime").
        * **X-Axis:** Date
        * **Y-Axis:** The requested variable (e.g., Weight)

    2.  **Correlated Data Request:** If the prompt asks for one value against another (e.g., "Generate graph for weight changes with change in GFR" or "Weight vs. GFR").
        * **X-Axis:** One variable (e.g., GFR)
        * **Y-Axis:** The other variable (e.g., Weight)

    ---
    **Strict Output Format:**
    The output **must** be a valid JSON object with four keys: "xAxisLabel", "yAxisLabel", "description", and "data".

    - "xAxisLabel": A descriptive label for the X-axis (e.g., "Date", "GFR (mL/min/1.73m²)")
    - "yAxisLabel": A descriptive label for the Y-axis (e.g., "Weight (Kg)")
    - "description": "A concise 1-2 sentence factual summary of the data trend. **Strictly no suggestions or diagnosis.** (e.g., 'CK Level (U/L) shows a slight upward trend.', 'Weight (Kg) increased while GFR (mL/min/1.73m²) decreased.')"
    - "data": A JSON array of objects. Each object **must** have two keys: "x" and "y".
      - "x": The value for the X-axis (this can be a date string OR a number).
      - "y": The value for the Y-axis (this must be a number).

    ---
    **Example 1: Time-Series Request**
    * **User Prompt:** "Show me the patient's CK levels over time."
    * **Example Output:**
        ```json
        {{
          "xAxisLabel": "Date",
          "yAxisLabel": "CK Level (U/L)",
          "description": "Shows the patient's CK Level (U/L), which increased from 120 to 125 over this period.",
          "data": [
            {{"x": "2023-01-15", "y": 120}},
            {{"x": "2023-03-22", "y": 125}}
          ]
        }}
        ```

    **Example 2: Correlated Data Request**
    * **User Prompt:** "Plot weight against GFR."
    * **Source Data (Imagined):**
        * `{{ "date": "2023-03-22", "gfr": 58, "weight": 76.5 }}`
        * `{{ "date": "2023-01-15", "gfr": 60, "weight": 75 }}`
    * **Example Output:** (Note: data is sorted by date, so the "2023-01-15" entry comes first)
        ```json
        {{
          "xAxisLabel": "GFR (mL/min/1.73m²)",
          "yAxisLabel": "Weight (Kg)",
          "description": "Shows Weight (Kg) vs. GFR (mL/min/1.73m²). As GFR decreased from 60 to 58, Weight increased from 75 to 76.5.",
          "data": [
            {{"x": 60, "y": 75}},
            {{"x": 58, "y": 76.5}}
          ]
        }}
        ```

    ---
    **Instructions (CRITICAL):**
    1.  **Analyze the Prompt:** First, determine if it's a Time-Series or Correlated Data request.
    2.  **For Time-Series:** Scan the timeline. For each entry that contains the requested Y-axis data point, create a data object using the entry's `date` as `x` and the data point's numerical value as `y`.
    3.  **For Correlated Data:** Scan the timeline **chronologically**. Find single entries that contain **BOTH** the X-axis variable and the Y-axis variable. Create a data object for each pair and add it to the `data` array. The final `data` array **must be in chronological order** based on the visit dates.
    4.  **Data Extraction:** Always extract only the numerical value (e.g., "75 kg" -> 75).
    5.  **Legend:** (Chronology: #754BAB
                     Vitals: #DF7635
                     Condition: #2BA27D)
    6.  **Using Legend:** Put every Chronological/Vital/Condition values in <span> tags and assign respective colour values from legend,for example-> <span style="color: #754BAB;">25-12-2025</span> in graph description section only. Only specific values not entire lines. 
    7.  **Labels & Description:** Identify metrics and create labels. Generate a brief `description` that **factually summarizes the data trend**. **Do not provide any medical suggestions, diagnosis, or advice.**
    8.  **Empty Data:** If no data or no correlated data is found, return an object with the correct labels, an empty "data" array `[]`, and a description like "No data found for this request."
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