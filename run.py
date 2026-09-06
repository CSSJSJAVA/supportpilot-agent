import asyncio
import sys
from pathlib import Path


SRC_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC_DIR))


from agents import Runner

from supportpilot.agent import create_support_agent
from supportpilot.db import init_db


MAX_HISTORY_MESSAGES = 10


async def main():
    init_db()

    agent = create_support_agent()

    print("SupportPilot 已启动。输入 exit 退出。\n")

    conversation = []

    while True:
        user_input = input("你：").strip()

        if user_input.lower() == "exit":
            print("SupportPilot：再见！")
            break

        conversation.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        if len(conversation) > MAX_HISTORY_MESSAGES:
            conversation = conversation[-MAX_HISTORY_MESSAGES:]

        result = await Runner.run(
            agent,
            input=conversation,
        )

        assistant_output = result.final_output

        print("\nSupportPilot：")
        print(assistant_output)
        print()

        conversation.append(
            {
                "role": "assistant",
                "content": assistant_output,
            }
        )

        if len(conversation) > MAX_HISTORY_MESSAGES:
            conversation = conversation[-MAX_HISTORY_MESSAGES:]


if __name__ == "__main__":
    asyncio.run(main())