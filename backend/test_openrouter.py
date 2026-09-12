import asyncio
import json
import sys
from app.core.config import settings
from app.services.ai_evaluator import (
    openai_client,
    evaluate_missed_reminder,
    ReminderTriageOutput
)

async def test_live_api():
    print("=" * 60)
    print("OPENROUTER API KEY & MODEL VERIFICATION TEST")
    print("=" * 60)

    # 1. Inspect Key Configuration
    api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("Please ensure your `.env` file in `backend/` has either:")
        print("  OPENROUTER_API_KEY=sk-or-v1-...")
        print("  or")
        print("  OPENAI_API_KEY=sk-or-v1-...")
        sys.exit(1)

    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"\n[1/3] Detected API Key: {masked_key}")
    print(f"      Target Base URL:  {settings.OPENROUTER_BASE_URL}")
    print(f"      Target Model:     {settings.AI_TEXT_MODEL}")

    if not openai_client:
        print("\n❌ Client was not initialized. Check your environment variables.")
        sys.exit(1)

    # 2. Raw Direct Ping Test to OpenRouter
    print("\n[2/3] Sending ping test directly to OpenRouter...")
    try:
        completion = await openai_client.chat.completions.create(
            model=settings.AI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": "Respond strictly with the single word: OK"}
            ],
            max_tokens=10,
            temperature=0.1
        )
        response_text = completion.choices[0].message.content.strip()
        print(f"      ✓ Connection successful! Received response: '{response_text}'")
        if hasattr(completion, "model"):
            print(f"      ✓ Routed upstream model: {completion.model}")
    except Exception as e:
        print(f"\n❌ Direct call to OpenRouter failed:")
        print(f"   Error: {e}")
        print("\nCommon reasons:")
        print("  - Invalid API key (check for spaces or typos)")
        print("  - openrouter/free temporary rate limit or capacity delay")
        sys.exit(1)

    # 3. Clinical Service Integration Test
    print("\n[3/3] Testing clinical evaluator (`evaluate_missed_reminder`)...")
    sample_patient = {
        "name": "Eleanor Vance",
        "age": 68,
        "gender": "Female",
        "primary_diagnosis": "Acute Coronary Syndrome, Post-PCI with DES in mid-LAD",
        "hospital_course_description": "Drug-eluting stent placed in mid-LAD. Strict dual antiplatelet required.",
        "medications_at_discharge": [
            {"medication_name": "Ticagrelor", "dosage": "90 mg", "frequency": "Twice daily"},
            {"medication_name": "Aspirin", "dosage": "81 mg", "frequency": "Once daily"}
        ]
    }

    try:
        result = await evaluate_missed_reminder(
            patient_summary=sample_patient,
            medication_info="Ticagrelor 90mg and Aspirin 81mg (Morning Dose)",
            scheduled_time="08:00"
        )

        print("\n" + "-" * 60)
        print("CLINICAL EVALUATION RESULT:")
        print(f"  Priority Level:     {result.priority.value.upper()}")
        print(f"  Alert Message:      {result.alert_content}")
        print(f"  Medical Rationale:  {result.clinical_rationale}")
        print("-" * 60)
        print("\n🎉 ALL TESTS PASSED! OpenRouter is configured and operational.")

    except Exception as e:
        print(f"\n❌ Clinical evaluation workflow failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_live_api())
