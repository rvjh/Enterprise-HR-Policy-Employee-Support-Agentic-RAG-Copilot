import time
from typing import List

from huggingface_hub import InferenceClient
from langchain_core.embeddings import Embeddings
from pinecone import Pinecone as PineconeClient, ServerlessSpec

try:
    from langchain_pinecone import PineconeVectorStore
except ImportError:
    from langchain_pinecone import Pinecone as PineconeVectorStore

from app.core.config import get_settings


settings = get_settings()

_embeddings = None
_vectorstore = None


# ---------------------------------------------------------------------------
# Hugging Face InferenceClient Embeddings
# ---------------------------------------------------------------------------

class HFInferenceClientEmbeddings(Embeddings):
    """LangChain Embeddings wrapper using huggingface_hub.InferenceClient."""

    def __init__(self, model: str, token: str):
        self.model = model
        self.client = InferenceClient(token=token)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.feature_extraction(texts, model=self.model)

        if hasattr(response, "tolist"):
            response = response.tolist()

        if isinstance(response, list) and len(response) > 0 and not isinstance(response[0], list):
            return [[float(x) for x in response]]

        return [[float(x) for x in vec] for vec in response]

    def embed_query(self, text: str) -> List[float]:
        response = self.client.feature_extraction(text, model=self.model)

        if hasattr(response, "tolist"):
            response = response.tolist()

        if isinstance(response, list) and len(response) > 0 and isinstance(response[0], list):
            return [float(x) for x in response[0]]

        return [float(x) for x in response]


# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------

def get_embeddings() -> HFInferenceClientEmbeddings:
    """Create and cache the Hugging Face Inference embedding client."""
    global _embeddings

    if _embeddings is None:
        if not settings.embedding_model:
            raise RuntimeError("EMBEDDING_MODEL is not configured in settings")

        token = settings.hf_token.strip() if settings.hf_token else ""
        if not token:
            raise RuntimeError(
                "HF_TOKEN is empty. Generate a token at https://huggingface.co/settings/tokens "
                "and paste it into your .env file."
            )

        _embeddings = HFInferenceClientEmbeddings(
            model=settings.embedding_model,
            token=token,
        )

    return _embeddings


# ---------------------------------------------------------------------------
# Dynamic Dimension Lookup
# ---------------------------------------------------------------------------

def get_embedding_dimension() -> int:
    """Determine embedding dimension directly from the Hugging Face API."""
    embeddings = get_embeddings()
    vector = embeddings.embed_query("dimension check")
    return len(vector)


# ---------------------------------------------------------------------------
# Pinecone Index Management
# ---------------------------------------------------------------------------

def ensure_index():
    """Create or verify the Pinecone index matches the embedding dimension."""
    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is missing")

    if not settings.pinecone_index_name:
        raise RuntimeError("PINECONE_INDEX_NAME is not configured")

    desired_dimension = get_embedding_dimension()
    pc = PineconeClient(api_key=settings.pinecone_api_key)

    existing_indexes = [
        getattr(idx, "name", idx.get("name") if isinstance(idx, dict) else idx)
        for idx in pc.list_indexes()
    ]

    index_name = settings.pinecone_index_name

    # Check and handle dimension mismatches
    if index_name in existing_indexes:
        index_info = pc.describe_index(index_name)
        current_dimension = getattr(index_info, "dimension", None)
        if current_dimension is None and isinstance(index_info, dict):
            current_dimension = index_info.get("dimension")

        if current_dimension is not None and current_dimension != desired_dimension:
            print(
                f"Pinecone dimension mismatch: "
                f"existing={current_dimension}, required={desired_dimension}"
            )
            print(f"Deleting Pinecone index: {index_name}")
            pc.delete_index(name=index_name)

            while index_name in [
                getattr(i, "name", i.get("name") if isinstance(i, dict) else i)
                for i in pc.list_indexes()
            ]:
                time.sleep(1)

    existing_indexes = [
        getattr(idx, "name", idx.get("name") if isinstance(idx, dict) else idx)
        for idx in pc.list_indexes()
    ]

    if index_name not in existing_indexes:
        print(f"Creating Pinecone index '{index_name}' with dimension {desired_dimension}")
        pc.create_index(
            name=index_name,
            dimension=desired_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            ),
        )

        while True:
            index_info = pc.describe_index(index_name)
            status = getattr(index_info, "status", None)
            if status is None and isinstance(index_info, dict):
                status = index_info.get("status", {})

            ready = (
                status.get("ready", False)
                if isinstance(status, dict)
                else getattr(status, "ready", False)
            )
            if ready:
                break
            time.sleep(1)

    return pc.Index(index_name)


# ---------------------------------------------------------------------------
# Vector Store & Retriever
# ---------------------------------------------------------------------------

def get_vectorstore() -> PineconeVectorStore:
    """Create and cache the Pinecone vector store."""
    global _vectorstore

    if _vectorstore is None:
        index = ensure_index()
        embeddings = get_embeddings()

        _vectorstore = PineconeVectorStore(
            index=index,
            embedding=embeddings,
            namespace=settings.pinecone_namespace,
        )

    return _vectorstore


def get_retriever():
    """Return a Pinecone retriever."""
    return get_vectorstore().as_retriever(
        search_kwargs={
            "k": settings.top_k,
        }
    )


def add_documents(chunks):
    """Add LangChain Document chunks to Pinecone."""
    if not chunks:
        return []

    store = get_vectorstore()
    return store.add_documents(chunks)