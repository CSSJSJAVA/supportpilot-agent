import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")
model_name = os.getenv("DEEPSEEK_MODEL")

client = AsyncOpenAI(
    api_key=api_key,
    base_url=base_url,
)

model = OpenAIChatCompletionsModel(
    model=model_name,
    openai_client=client,
)

agent = Agent(
    name="SupportPilot",
    instructions=(
        "你是 SupportPilot，一名企业客服 AI Agent。"
        "请用简洁、专业、友好的方式回答用户问题。"
        "如果你不知道答案，请明确说明，不要编造。"
    ),
    model=model,
)
MAX_HISTORY_MESSAGES = 10

async def main():
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