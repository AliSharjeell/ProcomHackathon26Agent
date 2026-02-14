import re
import json

def test_json_extraction():
    log_file = "verification_result.txt"
    try:
        # Simulate the user's error string
        error_dict = {
            'error': {
                'message': 'Failed to call a function. Please adjust your prompt.',
                'code': 'tool_use_failed',
                'failed_generation': '{\n  "voice": "Here are your cards: ",\n  "visual": {\n    "type": "SELECTION_LIST",\n    "data": {\n      "title": "Select a card",\n      "items": [\n        {\n          "id": "7b95eaeb-bbb0-4df7-a1ba-9bd364de64b7",\n          "title": "Card ending with 9002"\n        }\n      ]\n    }\n  }\n}'
            }
        }
        
        error_str = str(error_dict)
        
        regex = r"['\"]failed_generation['\"]\s*:\s*(['\"])(.*?)\1\s*}}"
        match = re.search(regex, error_str, re.DOTALL)
        
        with open(log_file, "w") as f:
            if match:
                f.write("MATCH FOUND\n")
                content = match.group(2)
                f.write(f"Content Length: {len(content)}\n")
                
                json_content = content.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
                try:
                    data = json.loads(json_content)
                    f.write("JSON PARSE SUCCESS\n")
                    f.write(json.dumps(data, indent=2))
                except Exception as e:
                    f.write(f"JSON PARSE FAILED: {str(e)}\n")
            else:
                f.write("MATCH FAILED\n")

    except Exception as e:
        with open(log_file, "w") as f:
            f.write(f"SCRIPT_ERROR: {str(e)}\n")

if __name__ == "__main__":
    test_json_extraction()
