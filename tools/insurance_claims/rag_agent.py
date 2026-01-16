"""
RAG Agent for Insurance Claims
Independent module for checking policy details using RAG.
"""
from common.llm.client import get_client
from config.settings import get_model_for_feature
from rank_bm25 import BM25Okapi
import string
import json

class InsurancePolicyAgent:
    """
    Agent that allows users to chat with their insurance policy.
    Uses an in-memory RAG approach (BM25) for simplicity and independence.
    """
    
    def __init__(self, policy_text: str):
        self.raw_text = policy_text
        self.chunks = self._chunk_text(policy_text)
        self.bm25 = self._build_index()
        self.client = get_client()
        self.model = get_model_for_feature("insurance_claims")

    def _chunk_text(self, text: str, chunk_size: int = 2000, overlap: int = 200) -> list:
        """Split text into chunks"""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunks.append(text[start:end])
            start += (chunk_size - overlap)
        return chunks

    def _tokenize(self, text: str) -> list:
        """Simple tokenizer"""
        text = text.lower()
        return text.translate(str.maketrans('', '', string.punctuation)).split()

    def _build_index(self):
        """Build BM25 index"""
        tokenized_corpus = [self._tokenize(chunk) for chunk in self.chunks]
        if not tokenized_corpus:
            return None
        return BM25Okapi(tokenized_corpus)

    def _retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant chunks"""
        if not self.bm25 or not self.chunks:
            return ""
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        relevant_chunks = [self.chunks[i] for i in top_indices]
        return "\n\n".join(relevant_chunks)

    def answer_question(self, question: str) -> str:
        """Answer user question using policy context"""
        context = self._retrieve_context(question)
        
        prompt = f"""
        You are a helpful Insurance Policy Assistant.
        Answer the user's question solely based on the policy context provided below.
        
        POLICY CONTEXT:
        {context}
        
        USER QUESTION:
        {question}
        
        If the answer is not in the context, say "I cannot find this information in the policy document."
        Provide a professional, clear response.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful insurance assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {str(e)}"
