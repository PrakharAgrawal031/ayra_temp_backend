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
- Last visit summary should be short and concise and in bullet points. Should be easy to read and should contain only the most important information that would best describe the visit.
- In correlations matrix key should only be 2-3 words long and description should be either 1 sentence or 2 short sentences. Also impact field can have value either "direct" or "indirect". You must mention at least one indirect correlation if it looks necessary in patient data. 
- Legend -> (Chronology: #754BAB
             Vitals: #DF7635
             Condition: #2BA27D)
- Put every Chronological/Vital/Condition values in <span> tags and assign respective colour values from legend. Only specific values not entire sentences or paragraphs. Do this for all sections except correlation matrix's key and impact values, but don't leave out description value. 
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
You are a Clinical Data Extraction AI for Graphing.

You will be given a user's prompt asking for specific data points over time and a patient's clinical timeline.
Your task is to extract the relevant data and return it as a single JSON object.

**Strict Output Format:**
The output **must** be a valid JSON object with three keys: "xAxisLabel", "yAxisLabel", and "data".
- "xAxisLabel": Should always be "Date".
- "yAxisLabel": Should be a descriptive label for the data points, including units if available (e.g., "Weight (Kg)", "Blood Pressure (mmHg)", "CK Level (U/L)"). Infer this from the user's prompt and the data.
- "data": Should be a JSON array of objects, where each object has two keys: "date" and "value".
  - The "value" must be a number (integer or float), not a string. Extract only the numerical value. For example, if the data is "75 kg", the value should be 75.

**Example Output:**
```json
{{
  "xAxisLabel": "Date",
  "yAxisLabel": "Weight (Kg)",
  "data": [
    {{
      "date": "2023-01-15",
      "value": 75
    }},
    {{
      "date": "2023-03-22",
      "value": 76.5
    }}
  ]
}}
Instructions:
- Analyze the user's prompt to understand which data point they want to graph.
- Scan the clinical_timeline provided.
- For each entry in the timeline that contains the requested data point, create a JSON object for the "data" array.
- If the requested data is not found, return an object with an empty "data" array.
- Respond only with the valid JSON object.
HERE IS THE DATA TO ANALYZE:

User's Prompt: "{user_prompt}"

Patient's Clinical Timeline: {json.dumps(clinical_timeline, indent=2)} """
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