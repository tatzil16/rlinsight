from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

print("🧪 Testing GPT-5-mini with Rocket League coaching prompt\n")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt = """You are an expert Rocket League coach. Provide brief, actionable feedback."""

user_prompt = """Analyze this match:

**Match:** Ranked Doubles - WIN

**Stats:**
- Goals: 2, Assists: 0, Saves: 2
- Shots: 3 (67% accuracy)
- Avg Boost: 46.7
- Defensive positioning: 50%
- Offensive positioning: 20%

Provide 2-3 sentences of coaching feedback."""

print("Sending coaching prompt to GPT-5-mini...")
print("="*60)

try:
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    print("\n✅ Response received!")
    print(f"Model: {response.model}")
    print(f"Finish reason: {response.choices[0].finish_reason}")
    print(f"Message content length: {len(response.choices[0].message.content or '')}")
    
    print("\n" + "="*60)
    print("FEEDBACK:")
    print(response.choices[0].message.content)
    print("="*60)
    
    # Check for refusal
    if response.choices[0].message.refusal:
        print(f"\n⚠️ Refusal detected: {response.choices[0].message.refusal}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()