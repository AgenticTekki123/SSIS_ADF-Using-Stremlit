import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# 🔴 CRITICAL: Load .env HERE, before creating the client
load_dotenv() 

# Now these will actually have values
api_key = os.getenv("AZURE_OPENAI_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not api_key or not endpoint:
    raise ValueError("Missing Azure OpenAI credentials. Check your .env file.")

client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-02-15-preview",
    azure_endpoint=endpoint
)

def convert_ssis_to_adf(ssis_json):
    # Left-aligned prompt for clarity and better AI parsing
    prompt = f"""
You are an expert Azure Data Factory engineer.
Convert the following SSIS package structure into valid ADF JSON artifacts.

SSIS Structure:
{json.dumps(ssis_json, indent=2)}

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON with keys: "linkedServices", "datasets", "pipeline".
2. For LINKED SERVICES: Use 'AzureSqlDatabase' for OLEDB and 'AzureBlobStorage' for FlatFile.
3. For DATASETS:
   - If SQL: Use type 'AzureSqlTable'.
   - If FlatFile/Blob: You MUST use type 'DelimitedText' AND include this exact structure for location:
     "typeProperties": {{
       "location": {{
         "type": "AzureBlobStorageLocation",
         "container": "ssis-packages"
       }},
       "columnDelimiter": ",",
       "firstRowAsHeader": true
     }}
4. For PIPELINE: Map tasks correctly. Ensure 'inputs' and 'outputs' reference the EXACT dataset names you created.
5. Do not use generic types. Be specific.
"""

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a precise JSON generator for ADF migration."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    
    # Clean markdown if AI adds it
    if "```json" in content:
        content = content.replace("```json", "").replace("```", "")
    
    return json.loads(content)