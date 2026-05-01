import json
import os
import subprocess
import requests
import sys
import time


def load_file(path):
    with open(path, "r") as f:
        return f.read()


def get_changed_terraform_code():
    try:
        base_ref = os.environ.get("GITHUB_BASE_REF", "main")
        subprocess.run(["git", "fetch", "origin"], check=True)

        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_ref}"],
            capture_output=True,
            text=True,
            check=True
        )

        files = result.stdout.splitlines()

        content = ""
        for f in files:
            if f.startswith("terraform/") and f.endswith(".tf") and os.path.exists(f):
                with open(f) as tf_file:
                    content += f"\nFile: {f}\n{tf_file.read()}\n"

        return content.strip()

    except Exception as e:
        print(f"Error collecting Terraform files: {e}")
        return ""


def call_ai(prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise Exception("ANTHROPIC_API_KEY not set")

    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 3000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Claude API failed: {response.text}")

    data = response.json()
    text = data["content"][0]["text"]

    if not text.strip().endswith("}"):
        raise Exception("Truncated response detected")

    return text


def call_ai_with_retry(prompt, retries=2):
    for attempt in range(retries + 1):
        try:
            return call_ai(prompt)
        except Exception as e:
            print(f"⚠️ AI call failed (attempt {attempt+1}): {e}")
            if attempt == retries:
                print("❌ All retries failed")
                sys.exit(1)
            time.sleep(2)


def validate_json(response_text):
    try:
        cleaned = response_text.strip()

        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        return json.loads(cleaned)

    except json.JSONDecodeError:
        print("❌ AI output is not valid JSON")
        print(response_text)
        sys.exit(1)


def save_json(review):
    with open("ai_output.json", "w") as f:
        json.dump(review, f, indent=2)


def format_comment(review):
    comment = f"""
## 🤖 AI Security Review

**Verdict:** {review.get('verdict')}
**Score:** {review.get('score')}/100  
**Risk Level:** {review.get('risk_level')}

### Summary
{review.get('summary')}

### Findings
"""

    findings = review.get("findings", [])
    if not findings:
        comment += "\nNo significant issues detected.\n"

    for fnd in findings:
        comment += f"""
- **{fnd.get('severity')}** – {fnd.get('title')}
  - {fnd.get('description')}
  - Impact: {fnd.get('impact')}
  - Fix: {fnd.get('recommendation')}
"""

    policy_violations = review.get("policy_violations", [])
    if policy_violations:
        comment += "\n### 🚨 Policy Violations\n"
        for p in policy_violations:
            comment += f"- **{p.get('policy_id')}** – {p.get('policy_name')} ({p.get('severity')})\n"

    positives = review.get("positives", [])
    if positives:
        comment += "\n### Positives\n"
        for p in positives:
            comment += f"- {p}\n"

    comment += "\n### Recommendation\n" + review.get("final_recommendation", "")

    return comment


def save_comment(comment):
    with open("pr_comment.txt", "w") as f:
        f.write(comment)


def main():
    print("🚀 Starting AI Review...")

    base_prompt = load_file("ai/prompt.txt")
    policy = load_file("ai/policy.md")

    prompt = base_prompt + "\n\nSecurity Policies:\n" + policy

    tf_code = get_changed_terraform_code()

    if not tf_code:
        save_comment("No Terraform changes to review.")
        return

    full_prompt = prompt + "\n\nTerraform Code:\n" + tf_code

    response_text = call_ai_with_retry(full_prompt)
    review = validate_json(response_text)

    save_json(review)

    comment = format_comment(review)
    save_comment(comment)

    print("📝 Comment generated successfully")

    # 🔥 ENFORCEMENT (AFTER COMMENT GENERATION)
    should_fail = False

    if review.get("verdict") == "DO_NOT_MERGE":
        print("🚫 Blocking PR: Verdict is DO_NOT_MERGE")
        should_fail = True

    for p in review.get("policy_violations", []):
        if p.get("severity") == "CRITICAL":
            print(f"🚫 Blocking PR: CRITICAL policy violation {p.get('policy_id')}")
            should_fail = True

    if should_fail:
        print("❌ Failing pipeline AFTER posting comment")
        sys.exit(1)

    print("✅ AI Review completed successfully")


if __name__ == "__main__":
    main()