import re
from rank_bm25 import BM25Okapi
import string

class DocumentKnowledgeBase:
    def __init__(self):
        self.documents = [] # List of full text per file
        self.chunks = []    # List of all text chunks
        self.filenames = [] # Map chunk index to filename
        self.bm25 = None
        
    def add_documents(self, text_list, filename_list):
        """
        Ingest documents, chunk them, and build index.
        """
        self.documents = text_list
        self.chunks = []
        self.filenames = []
        
        # 1. Chunking
        for text, fname in zip(text_list, filename_list):
            file_chunks = self._chunk_text(text)
            self.chunks.extend(file_chunks)
            self.filenames.extend([fname] * len(file_chunks))
            
        # 2. Build Search Index (BM25)
        # Tokenize for BM25
        tokenized_corpus = [self._tokenize(chunk) for chunk in self.chunks]
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)
            
    def search(self, query, top_k=5):
        """
        Retrieve top_k most relevant chunks.
        """
        if not self.bm25 or not self.chunks:
            return []
            
        tokenized_query = self._tokenize(query)
        # Get top scores
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
             results.append({
                 "text": self.chunks[idx],
                 "source": self.filenames[idx],
                 "score": scores[idx]
             })
        return results
        
    def get_context(self, query, max_chars=100000):
        """
        Get a consolidated context string for LLM, limited by size.
        Prioritizes relevant chunks.
        """
        # If total content is small enough, return everything (Gemini 1M context)
        total_len = sum(len(c) for c in self.chunks)
        if total_len < 500000: # Safe limit for 1M token model (approx 4M chars, but being safe)
            return "\n\n".join([f"--- Source: {f} ---\n{c}" for f, c in zip(self.filenames, self.chunks)])
            
        # Otherwise, retrieve top N chunks until limit
        results = self.search(query, top_k=20) # Get top 20 chunks
        context_parts = []
        current_len = 0
        
        for res in results:
            part = f"--- Source: {res['source']} ---\n{res['text']}"
            if current_len + len(part) > max_chars:
                break
            context_parts.append(part)
            current_len += len(part)
            
        return "\n\n".join(context_parts)

    def _chunk_text(self, text, chunk_size=3000, overlap=500):
        """
        Split text into overlapping chunks.
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunks.append(text[start:end])
            start += (chunk_size - overlap)
            
        return chunks

    def _tokenize(self, text):
        """
        Simple tokenizer: lowercase + remove punctuation
        """
        text = text.lower()
        return text.translate(str.maketrans('', '', string.punctuation)).split()
