import google.generativeai as genai
import re
import json
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY")

if not GEMINI_KEY:
    raise ValueError("GEMINI_KEY environment variable is not set. Please add it to your .env file.")

try:
    genai.configure(api_key=GEMINI_KEY)
    client = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    raise RuntimeError(f"Failed to configure Gemini API: {e}")


def evaluate_patient_record(patient_data):

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
      "Conditions": ["...","..."],
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
- Last visit summary should be in 2 paragraphs separated by break line tag in same element. Do not compromise ease of readability and understandability.
- In correlations matrix key should only be 2-3 words long and description should be either 1 sentence or 2 short sentences. Also impact field can have value either "direct" or "indirect". 
- Legend -> (Chronology: #754BAB
             Vitals: #DF7635
             Condition: #2BA27D)
- Put every Chronological/Vital/Condition values in <span> tags and assign respective colour values from legend. Only specific values not entire sentences or paragraphs. Do this for all sections except correlation matrix's key and impact values, but don't leave out description value. 
- At the end of each section(Except ComparisonOfProminentDataPoints) you should add sources JSON Object as well which will have source of information marked. for ex: "Sources": ["Notes": "dd-mm-yyyy", "Blood Report": "dd-mm-yyyy"....] there might not be any sources listed for now so you can fabricate your own as example based on data provided.
- This is only for demo so generate fake Family history for demo purpose if it suits the patient's condition.
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
        print(f"Error evaluating patient record: {e}")
        raise RuntimeError(f"Failed to evaluate patient record: {str(e)}")