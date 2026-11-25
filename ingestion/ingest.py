import sys
 
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import pandas as pd

import os
from pathlib import Path
from tqdm import tqdm
import pickle
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

raw_document_paths = ["documents_raw/" + d for d in os.listdir("documents_raw")]

load_dotenv()

EMBED_MODEL_ID = "google/embeddinggemma-2"
MAX_TOKENS = 512 # move to config.py later

tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained(EMBED_MODEL_ID),
    max_tokens=MAX_TOKENS,
)

embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    openai_api_base=os.getenv("EMBEDDINGS_API_BASE_URL"),
    openai_api_key=os.getenv("EMBEDDINGS_API_KEY"),
    check_embedding_ctx_length=False
)

converter = DocumentConverter()
chunker = HybridChunker(tokenizer=tokenizer)

faolex_df = pd.read_csv('data_download/faolex-ph.csv')
docs = []

for doc_path in tqdm(raw_document_paths):
    conv_doc = converter.convert(doc_path).document
    faolex_id = Path(doc_path).stem
    title = faolex_df[faolex_df["FAOLEX ID"] == faolex_id].iloc[0]["Title"]
    with open(f"documents_md/{faolex_id}.md",  "w+", encoding="utf-8") as md_file:
        md_file.write(conv_doc.export_to_markdown())

    for chunk in chunker.chunk(conv_doc):
        ctx_chunk = chunker.contextualize(chunk=chunk)
        chunk_doc = Document(
            page_content = ctx_chunk,
            metadata = {
                "source_file": f"{faolex_id}.md",
                "title": title
            }
        )
        
        docs.append(chunk_doc)


vectorstore = Chroma.from_documents(
    documents = docs,
    embedding = embeddings,
    collection_name = "agripolicy_kb",
    persist_directory = "./chroma_agripolicy_kb"
)

DOC_CACHE = Path('doc_cache/docs.pkl')
if not DOC_CACHE.exists():
    with open(DOC_CACHE, "wb") as doc_cache_file:
        pickle.dump(docs, doc_cache_file)


