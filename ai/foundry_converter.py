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
    prompt = f"""
    You are an expert Azure Data Factory engineer.
    Convert the following SSIS package structure into valid ADF JSON artifacts.
    
    SSIS Structure:
    {json.dumps(ssis_json, indent=2)}
    
    Requirements:
    1. Create 'linkedServices' based on the connections provided. Use 'AzureSqlDatabase' for OLEDB/SQL and 'AzureBlobStorage' for FlatFile.
    2. Create 'datasets' referencing those linked services. Name them dynamically.
    3. Create a 'pipeline' with activities mapping the SSIS tasks.
    4. Return ONLY valid JSON with keys: "linkedServices", "datasets", "pipeline".
    5. Ensure 'properties' and 'typeProperties' wrappers are included.
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