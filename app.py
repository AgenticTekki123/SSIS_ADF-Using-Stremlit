import streamlit as st
import os
import json
from dotenv import load_dotenv
from parser.dtsx_parser import parse_dtsx
from ai.foundry_converter import convert_ssis_to_adf
from deploy.deploy_adf import deploy_to_adf



# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="SSIS to ADF Migrator", layout="wide")
st.title("🚀 SSIS to ADF Migration POC")
st.markdown("Upload a **.dtsx** file to automatically generate & deploy ADF artifacts using Azure AI.")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    st.info("Ensure you are logged in via `az login` in your terminal.")
    
    # Read from .env instead of st.secrets
    rg = os.getenv("AZURE_RESOURCE_GROUP", "Not Set")
    factory = os.getenv("ADF_FACTORY_NAME", "Not Set")
    
    st.write(f"**Resource Group:** {rg}")
    st.write(f"**Data Factory:** {factory}")

uploaded_file = st.file_uploader("Choose a SSIS Package (.dtsx)", type="dtsx")

if uploaded_file is not None:
    try:
        # 1. Read File
        xml_content = uploaded_file.read()
        st.success("✅ File uploaded successfully!")
        
        # 2. Parse SSIS
        with st.spinner("🔍 Parsing SSIS Package..."):
            ssis_data = parse_dtsx(xml_content)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Extracted Tasks")
                st.json(ssis_data['tasks'])
            with col2:
                st.subheader("Extracted Connections")
                st.json(ssis_data['connections'])
        
        # 3. Convert via AI
        if st.button("🤖 Convert & Deploy to ADF", type="primary"):
            with st.spinner("🧠 AI is generating ADF JSON (this may take a few seconds)..."):
                try:
                    adf_json = convert_ssis_to_adf(ssis_data)
                    st.write("### 📄 Generated ADF JSON Preview")
                    st.json(adf_json)
                
                    # 4. Deploy
                    with st.spinner("☁️ Deploying to Azure Data Factory..."):
                        deploy_to_adf(adf_json)
                        
                        st.balloons()
                        st.success("🎉 Successfully deployed to ADF!")
                        st.info(f"**Pipeline Name:** `{adf_json['pipeline']['name']}`")
                        st.info(f"**Linked Services Created:** {len(adf_json.get('linkedServices', []))}")
                        st.info(f"**Datasets Created:** {len(adf_json.get('datasets', []))}")
                        
                except Exception as e:
                    st.error(f"❌ AI Conversion or Deployment Failed: {str(e)}")
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
else:
    st.info("👆 Please upload a .dtsx file to begin.")