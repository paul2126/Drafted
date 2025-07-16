import json


def extract_relevant_data(json_data):
    result_lines = []

    for item in json_data:
        name = item.get("name", "")
        description = item.get("description", "")
        position = item.get("position", "")
        for evt in item.get("event", []):
            role = evt.get("role", "")
            category = evt.get("category", [])
            data = evt.get("data", {})

            result_lines.append(
                f"Name: {name}\n"
                f"Description: {description}\n"
                f"Position: {position}\n"
                f"Event Role: {role}\n"
                f"Event Category: {', '.join(category)}\n"
                f"Event Data:\n"
                f"  Background: {data.get('background', '')}\n"
                f"  My Action: {data.get('my_action', '')}\n"
                f"  Result: {data.get('result', '')}\n"
                f"  Reflection: {data.get('reflection', '')}\n"
                # f"{'-'*40}"
            )
    print(result_lines)
    return "\n".join(result_lines)


# Example usage
# json_input = <paste your JSON data here>
# print(extract_relevant_data(json_input))

with open("backend/dummy.json", "r", encoding="utf-8") as f:
    json_input = json.load(f)

output = extract_relevant_data(json_input)
# print(output)
