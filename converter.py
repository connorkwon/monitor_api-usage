import json


def friendly_text(data_list):
    text = ""
    for item in data_list:
        for key, value in item.items():
            # Convert key from CamelCase to normal words
            key_formatted = ''.join([' ' + i.lower() if i.isupper() else i for i in key]).lstrip()
            # Append the key-value pair to the text, each on a new line
            text += f"{key_formatted}: {value}\n"
        text += "\n"  # Add a period after each dictionary's data
    return text.strip()  # Strip to remove any trailing newlines


def json_to_html(data_json):
    parsed_json = json.loads(data_json)
    text_content = parsed_json['text']

    # Convert text to HTML
    html_content = "<html><body><ul>"
    for line in text_content.split('\n'):
        if line:
            html_content += f"<li>{line}</li>"
    html_content += "</ul></body></html>"
    return html_content


def list_to_html(data_list):
    html_content = "<html><body><table border='1'>"

    # Adding table headers
    headers = data_list[0].keys()
    html_content += "<tr>"
    for header in headers:
        html_content += f"<th>{header}</th>"
    html_content += "</tr>"

    # Adding table rows
    for item in data_list:
        html_content += "<tr>"
        for value in item.values():
            html_content += f"<td>{value}</td>"
        html_content += "</tr>"

    # Closing tags for table, body, and HTML
    html_content += "</table></body></html>"

    return html_content
