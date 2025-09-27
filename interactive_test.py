#!/usr/bin/env python3
"""
Interactive testing console for AI agents
Run: python interactive_test.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from router_agent.agent import ROUTER_AGENT

def interactive_test():
    print("🤖 INTERACTIVE AGENT TESTER")
    print("=" * 40)
    print("Type emergency requests to test the router agent")
    print("Type 'quit' or 'exit' to stop")
    print("-" * 40)

    while True:
        try:
            # Get user input
            request_text = input("\n💬 Enter emergency request: ").strip()

            # Check for exit
            if request_text.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not request_text:
                print("❌ Please enter a request")
                continue

            # Test router agent
            print("🤖 Processing...")
            result = ROUTER_AGENT.run(request_text)

            # Display results
            print(f"\n✅ Results:")
            print(f"   📂 Category: {result.get('category', 'Unknown')}")
            print(f"   ⚡ Urgency: {result.get('urgency', 'Unknown')}")
            print(f"   🎯 Confidence: {result.get('confidence', 0):.2f}")
            print(f"   🧠 Reasoning: {result.get('reasoning', 'No reasoning')}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    interactive_test()