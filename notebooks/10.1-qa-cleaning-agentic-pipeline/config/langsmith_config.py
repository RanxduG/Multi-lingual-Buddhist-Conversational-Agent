import os
from dotenv import load_dotenv


def setup_langsmith():
    load_dotenv()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv(
        "LANGSMITH_PROJECT", "buddhist-qa-pipeline-stage2"
    )
    langsmith_key = os.getenv("LANGSMITH_API_KEY")
    if langsmith_key:
        os.environ["LANGCHAIN_API_KEY"] = langsmith_key
