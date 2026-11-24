import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from utilities.utilities import log 

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

EMBED_MODEL = os.getenv("EMBED_MODEL")
KB_FOLDER = os.getenv("KB_FOLDER")

chroma = chromadb.PersistentClient(path="./chromadbStorage")    

zorvex_collection = chroma.get_or_create_collection(
    name = "zorvex_technology",
    configuration={
        "hnsw":{
            "space":"cosine",
        }
    }
)

# loading documents from the KB Folder
def load_documents(folder):
    documents = []

    for filename in sorted(os.listdir(folder)):

        if not filename.endswith(".txt"):  
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            documents.append(
                {
                    "source" : filename,
                    "text" : f.read()
                }
            )

    return documents

def get_embedding(text):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding

# chunking the document
def chunk_document(document):
    chunks = []

    chunk_id = 0
    for part in document["text"].split("\n\n"):
        part = part.strip()

        if part:
            chunks.append({
                "source" : document["source"],
                "chunk_id":chunk_id,
                "text":part
            }
        )
        chunk_id += 1
    return chunks

# creating chunks from the chunked document
def create_chunks(KB_FOLDER):
    documents = load_documents(KB_FOLDER)
    chunks = []

    for document in documents:
        chunks.extend(chunk_document(document))

    return chunks


def create_update_collection(KB_FOLDER):

    chunks = create_chunks(KB_FOLDER)

    ids = []
    embeddings = []
    metadatas = []
    texts = []

    for c in chunks:
        id = c["chunk_id"]
        text = c["text"]
        source = c["source"]

        texts.append(text)
        ids.append(f"{source}_{id}")
        metadatas.append({"source": source, "chunk_id": id})
        embeddings.append(get_embedding(text))

    zorvex_collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

def search_collection(query, top_k):
    log(f"In the search collection from chromadb.py")
    query_embedding = get_embedding(query)

    results = zorvex_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    ) 

    return_results = []

    #score, source, chunk_id

    for i in range(len(results["documents"][0])):
        source = results["metadatas"][0][i]["source"]
        chunk_id = results["metadatas"][0][i]["chunk_id"]
        score = results["distances"][0][i]
        text = results["documents"][0][i]

        return_results.append({
            "source" : source,
            "chunk_id" : chunk_id,
            "score" : 1-score,
            "text" : text
        })


    return return_results[:top_k]

if __name__ == "__main__":
    create_update_collection(KB_FOLDER)
    print("Collection updated successfully!")