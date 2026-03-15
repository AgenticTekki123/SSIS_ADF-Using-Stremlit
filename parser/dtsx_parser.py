from lxml import etree

# Define the SSIS XML Namespace
NS = {'DTS': 'www.microsoft.com/SqlServer/Dts'}

def parse_dtsx(xml_content):
    """
    Parses SSIS .dtsx XML content and extracts Tasks and Connections.
    Filters out invalid/unknown entries to ensure clean AI input.
    """
    try:
        root = etree.fromstring(xml_content)
        tasks = []
        connections = []

        # 1. Extract Tasks (Executables)
        # We look for direct executables to avoid duplicates from nested loops in simple POC
        for exe in root.xpath("//DTS:Executable", namespaces=NS):
            name = exe.attrib.get("{www.microsoft.com/SqlServer/Dts}ObjectName")
            type_val = exe.attrib.get("{www.microsoft.com/SqlServer/Dts}ExecutableType")
            
            if name and type_val:
                tasks.append({
                    "name": name,
                    "type": type_val
                })

        # 2. Extract Connection Managers
        # We specifically look inside the ConnectionManagers node to avoid nested definitions
        for conn in root.xpath("//DTS:ConnectionManagers/DTS:ConnectionManager", namespaces=NS):
            name = conn.attrib.get("{www.microsoft.com/SqlServer/Dts}ObjectName")
            type_val = conn.attrib.get("{www.microsoft.com/SqlServer/Dts}CreationName")
            
            # Try to find the connection string in the nested ObjectData
            conn_string = ""
            obj_data = conn.find(".//DTS:ConnectionManager", namespaces=NS)
            if obj_data is not None:
                conn_string = obj_data.attrib.get("{www.microsoft.com/SqlServer/Dts}ConnectionString", "")

            # CRITICAL: Only add if we have a valid name (filter out 'Unknown' or empty)
            if name and name != "Unknown":
                connections.append({
                    "name": name,
                    "type": type_val,
                    "connectionString": conn_string
                })

        return {"tasks": tasks, "connections": connections}

    except Exception as e:
        raise Exception(f"Parsing failed: {str(e)}")