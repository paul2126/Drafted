from openai import OpenAI
import environ
import tiktoken
from supabase import create_client, Client
from pathlib import Path
import os
from datetime import datetime

tokenizer = tiktoken.get_encoding("cl100k_base")  # For embedding-3 models
env = environ.Env()

environ.Env.read_env(env_file=os.path.join(os.path.dirname(__file__), ".env"))
# print(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = env("DB_URL")
SUPABASE_KEY = env("DB_KEY")

client = OpenAI(api_key=env("OPENAI_KEY"))
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

embedding_response = client.embeddings.create(
    input="협업 과정, 강점 경험, 단점 극복",
    model="text-embedding-3-small",
)
query_embedding = embedding_response.data[0].embedding
response = supabase.rpc(
    "match_documents",
    {
        "query_embedding": query_embedding,
        "match_threshold": 0.3,
        "match_count": 3,
    },
).execute()

print(response)
