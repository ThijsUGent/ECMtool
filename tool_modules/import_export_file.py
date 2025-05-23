import json


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
    Extracts the dictionary from a Streamlit uploaded .txt file using line iteration.
    Skips the header and loads the JSON.
    """
    lines = []

    # Decode each line as UTF-8
    for line in uploaded_file:
        lines.append(line.decode("utf-8").strip())

    # Skip header (first line), join the rest
    json_str = "\n".join(lines[1:])

    # Load JSON content
    result_dict = json.loads(json_str)
    print('test')
    return result_dict
