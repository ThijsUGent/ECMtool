import json
from datetime import datetime


def export_to_txt(df, title, date=None):
    result_dict = {str(row["configuration_id"]): row["route_weight"]
                   for _, row in df.iterrows()}

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Format content
    header = f"Pathway file : {title}, created {date}\n"
    body = json.dumps(result_dict, indent=4)
    content = header + body

    return content
