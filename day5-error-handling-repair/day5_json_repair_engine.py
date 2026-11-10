import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

MODEL = "openrouter/free"


def repair_json_payload(malformed_output, error_msg, attempt=1, max_attempts=3):

    if attempt > max_attempts:
        raise Exception(
            "Maximum repair attempts reached. "
            "JSON could not be repaired."
        )

    print(f"\n[Repair Engine] Attempt {attempt}")
    print("[Repair Engine] Invalid JSON detected. Repairing...")

    repair_prompt = f"""
You are a JSON Repair Service.

The following output is not valid JSON.

Parsing Error:
{error_msg}

Malformed Output:
{malformed_output}

Repair the JSON.

Return ONLY valid JSON.
Do not return markdown.
Do not return explanations.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": repair_prompt
            }
        ],
        temperature=0
    )

    repaired_output = response.choices[0].message.content.strip()

    try:
        valid_json = json.loads(repaired_output)

        print("[Repair Engine] JSON repaired successfully.")

        return valid_json

    except json.JSONDecodeError as e:

        return repair_json_payload(
            repaired_output,
            str(e),
            attempt + 1,
            max_attempts
        )


def generate_json(user_input):

    prompt = f"""
Convert the following user input into JSON.

User Input:
{user_input}

Return ONLY valid JSON.
Do not use markdown.
Do not add explanations.

Example format:
{{
    "name": "example",
    "age": 25,
}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    print("\n[Model Output]")
    print(raw_output)

    # Validate initial output
    try:
        valid_json = json.loads(raw_output)

        print("\n[Validator] Valid JSON.")
        return valid_json

    except json.JSONDecodeError as e:

        print("\n[Validator] Invalid JSON.")
        print("[Validator] Starting repair process...")

        return repair_json_payload(
            raw_output,
            str(e)
        )


# ---------------- MAIN PROGRAM ----------------

if __name__ == "__main__":

    print("====================================")
    print("   JSON REPAIR ENGINE")
    print("====================================")

    user_input = input("\nEnter your input: ")

    try:

        result = generate_json(user_input)

        print("\n========== FINAL JSON ==========")
        print(json.dumps(result, indent=4))

    except Exception as e:

        print("\n========== ERROR ==========")
        print(e)