import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from dotenv import load_dotenv

load_dotenv()

def deploy_to_adf(adf_json):
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    factory_name = os.getenv("ADF_FACTORY_NAME")

    if not all([subscription_id, resource_group, factory_name]):
        raise ValueError("Missing Azure environment variables. Check your .env file.")

    # Authenticate using your logged-in Azure CLI account
    credential = DefaultAzureCredential()
    client = DataFactoryManagementClient(credential, subscription_id)

    print(f"🚀 Deploying to Factory: {factory_name} in RG: {resource_group}...")

    # 1️⃣ Deploy Linked Services
    print("\n--- Deploying Linked Services ---")
    for ls in adf_json.get("linkedServices", []):
        # Ensure the structure matches what Azure SDK expects
        # The SDK expects the body to be the 'properties' object mostly, 
        # but create_or_update handles the wrapper if we pass the full object correctly.
        # However, to be safe, we ensure 'properties' exists.
        
        if "properties" not in ls:
            # Reconstruct the object if AI returned a flat structure
            ls_payload = {
                "properties": {
                    "type": ls.get("type", "AzureSqlDatabase"),
                    "typeProperties": {
                        "connectionString": ls.get("connectionString", "")
                    }
                }
            }
        else:
            ls_payload = ls

        try:
            client.linked_services.create_or_update(
                resource_group_name=resource_group,
                factory_name=factory_name,
                linked_service_name=ls["name"],
                linked_service=ls_payload
            )
            print(f"✅ Created Linked Service: {ls['name']}")
        except Exception as e:
            print(f"❌ Failed to create Linked Service {ls['name']}: {str(e)}")

    # 2️⃣ Deploy Datasets
    print("\n--- Deploying Datasets ---")
    for ds in adf_json.get("datasets", []):
        # Ensure 'properties' exists
        if "properties" not in ds:
            ds_payload = {
                "properties": {
                    "linkedServiceName": ds.get("linkedServiceName"),
                    "type": ds.get("type", "AzureSqlTable")
                }
            }
        else:
            ds_payload = ds

        try:
            client.datasets.create_or_update(
                resource_group_name=resource_group,
                factory_name=factory_name,
                dataset_name=ds["name"],
                dataset=ds_payload
            )
            print(f"✅ Created Dataset: {ds['name']}")
        except Exception as e:
            print(f"❌ Failed to create Dataset {ds['name']}: {str(e)}")

    # 3️⃣ Deploy Pipeline
    print("\n--- Deploying Pipeline ---")
    pipeline = adf_json.get("pipeline")
    if pipeline:
        # Ensure 'properties' exists
        if "properties" not in pipeline:
            pipeline_payload = {
                "properties": {
                    "activities": pipeline.get("activities", [])
                }
            }
        else:
            pipeline_payload = pipeline

        try:
            client.pipelines.create_or_update(
                resource_group_name=resource_group,
                factory_name=factory_name,
                pipeline_name=pipeline["name"],
                pipeline=pipeline_payload
            )
            print(f"✅ Created Pipeline: {pipeline['name']}")
        except Exception as e:
            print(f"❌ Failed to create Pipeline {pipeline['name']}: {str(e)}")
    
    print("\n🎉 Deployment process finished!")
    return True