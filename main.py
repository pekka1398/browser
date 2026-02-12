import os
import asyncio
from dotenv import load_dotenv
from browser_use import Agent, ChatGoogle

load_dotenv()

async def main():
    # 1. 使用 browser_use 內建的 ChatGoogle
    llm = ChatGoogle(
        model="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 2. 定義任務
    task = (
        f"前往 {os.getenv('MOODLE_URL')} (請注意網址後面的空格)，"
        f"使用帳號 {os.getenv('MOODLE_USER')} 和密碼 {os.getenv('MOODLE_PASS')} 登入，"
        "然後總結最新的公告或訊息。"
    )

    # 3. 初始化 Agent
    agent = Agent(
        task=task,
        llm=llm,
    )

    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())