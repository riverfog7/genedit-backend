#!/usr/bin/env python3
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import argparse, urllib.parse


def main():
    parser = argparse.ArgumentParser(description="Test ChatOpenAI with vLLM backend")
    parser.add_argument(
        "--url", type=str, help="server URL", required=True,
    )
    args = parser.parse_args()

    print("Testing ChatOpenAI with vLLM backend at", args.url)
    chat = ChatOpenAI(
        model="model",
        api_key="EMPTY",
        base_url=urllib.parse.urljoin(args.url, "/vllm/v1"),
        max_tokens=8192,
    )

    prompt = "Hello, how are you today? Please write me a short story."
    chats = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=prompt),
    ]
    print("Response:", end=" ", flush=True)
    for chunk in chat.stream(chats):
        print(chunk.content, end="", flush=True)

if __name__ == "__main__":
    main()
