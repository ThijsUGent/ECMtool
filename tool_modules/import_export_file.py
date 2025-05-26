import json
import streamlit as st


def export_to_txt(df, title):
    """
    Converts a DataFrame of configurations and route weights into a text format 
    with a header and a JSON body, and returns the content as a string.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'configuration_id' and 'route_weight'.
        title (str): Title of the pathway, used in the header.

    Returns:
        str: Text content combining a header and a JSON-formatted dictionary.
    """

    # Build a dictionary with configuration_id as string keys and route_weight as values
    result_dict = {
        str(row["configuration_id"]): row["route_weight"]
        for _, row in df.iterrows()
    }

    # Create a header string with the pathway title
    header = f"Pathway file : {title}\n"

    # Convert the dictionary to a pretty-printed JSON string
    body = json.dumps(result_dict, indent=4)

    # Combine header and JSON body
    content = header + body

    # Return the combined content (this can be written to a file or downloaded)
    return content


def import_to_dict(uploaded_file):
    """
    Extracts the dictionary and pathway title from a Streamlit uploaded .txt file.
    Assumes the first line is the header in the format 'Pathway file : <title>'.
    Returns:
        result_dict (dict): Dictionary parsed from the JSON body.
        pathway_name (str): Extracted title from the header line.
    """
    lines = [line.decode("utf-8").strip() for line in uploaded_file]

    # Extract and clean title from the header line
    header_line = lines[0]
    if header_line.lower().startswith("pathway file :"):
        pathway_name = header_line.split(":", 1)[1].strip()
    else:
        st.error(
            "Header line is not in the expected format: 'Pathway file : <title>'")
        return {}, None
    # Parse JSON from the remaining lines
    json_str = "\n".join(lines[1:])
    result_dict = json.loads(json_str)

    return result_dict, pathway_name
