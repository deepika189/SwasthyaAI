"""
RAG system orchestration module for Ayurvedic remedy recommendations.
"""

import logging
from typing import List, Optional
import os

logger = logging.getLogger(__name__)


class RAGInitializationError(Exception):
    """Raised when RAG system initialization fails."""
    pass


class RAGQueryError(Exception):
    """Raised when RAG query fails."""
    pass


class AyurvedicRAGSystem:
    """Orchestrates document retrieval and remedy generation for Ayurvedic remedies."""
    
    def __init__(
        self,
        pdf_path: str,
        embeddings_model_id: str = "amazon.titan-embed-text-v1",
        llm_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
        region: str = "us-east-1",
        index_path: str = "data/faiss_index",
        top_k: int = 3,
        max_chunks: int = 100
    ):
        """
        Initialize RAG system with configuration.
        
        Args:
            pdf_path: Path to Ayurvedic remedies PDF
            embeddings_model_id: Bedrock embeddings model ID
            llm_model_id: Bedrock LLM model ID
            region: AWS region
            index_path: Path to persist FAISS index
            top_k: Number of chunks to retrieve
            max_chunks: Maximum number of chunks to process from PDF (default 100)
        """
        self.pdf_path = pdf_path
        self.embeddings_model_id = embeddings_model_id
        self.llm_model_id = llm_model_id
        self.region = region
        self.index_path = index_path
        self.top_k = top_k
        self.max_chunks = max_chunks
        
        # Components (initialized in initialize())
        self.pdf_processor = None
        self.embeddings = None
        self.remedy_generator = None
        self.vector_store = None
        
        logger.info(f"AyurvedicRAGSystem initialized with config: pdf={pdf_path}, top_k={top_k}, max_chunks={max_chunks}")
    
    def initialize(self) -> None:
        """
        Initialize RAG system: process PDF, create embeddings, build index.
        
        Raises:
            RAGInitializationError: If initialization fails
        """
        try:
            logger.info("Starting RAG system initialization...")
            
            # Import required modules
            from app.pdf_processor import PDFProcessor
            from app.bedrock_embeddings import BedrockEmbeddingsWrapper
            from app.remedy_generator import RemedyGenerator
            
            # Initialize PDF processor
            logger.info("Initializing PDF processor...")
            self.pdf_processor = PDFProcessor(
                self.pdf_path,
                max_chunks=self.max_chunks
            )
            
            # Initialize embeddings wrapper
            logger.info("Initializing embeddings wrapper...")
            self.embeddings = BedrockEmbeddingsWrapper(
                model_id=self.embeddings_model_id,
                region=self.region
            )
            
            # Initialize remedy generator
            logger.info("Initializing remedy generator...")
            self.remedy_generator = RemedyGenerator(
                model_id=self.llm_model_id,
                region=self.region
            )
            
            # Check if index already exists
            if os.path.exists(os.path.join(self.index_path, "index.faiss")):
                logger.info("Loading existing FAISS index...")
                self._load_existing_index()
            else:
                logger.info("Building new FAISS index...")
                self._build_new_index()
            
            logger.info(f"RAG system initialized successfully with {self._get_index_size()} chunks")
            
        except Exception as e:
            logger.error(f"RAG initialization failed: {e}", exc_info=True)
            raise RAGInitializationError(f"Failed to initialize RAG system: {e}")
    
    def _load_existing_index(self) -> None:
        """Load existing FAISS index from disk."""
        try:
            from langchain_community.vectorstores import FAISS
            
            # Load the index
            self.vector_store = FAISS.load_local(
                self.index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            logger.info("Successfully loaded existing FAISS index")
            
        except Exception as e:
            logger.error(f"Failed to load existing index: {e}")
            raise RAGInitializationError(f"Failed to load FAISS index: {e}")
    
    def _build_new_index(self) -> None:
        """Build new FAISS index from PDF."""
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_core.documents import Document
            
            # Process PDF and get chunks
            logger.info("Processing PDF...")
            chunks = self.pdf_processor.load_and_chunk()
            
            if not chunks:
                raise RAGInitializationError("No chunks extracted from PDF")
            
            logger.info(f"Extracted {len(chunks)} chunks from PDF")
            
            # Convert to LangChain Document objects
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk["page_content"],
                    metadata=chunk["metadata"]
                )
                documents.append(doc)
            
            # Create FAISS index
            logger.info("Creating embeddings and building FAISS index...")
            self.vector_store = FAISS.from_documents(
                documents,
                self.embeddings
            )
            
            # Persist to disk
            logger.info(f"Persisting index to {self.index_path}...")
            os.makedirs(self.index_path, exist_ok=True)
            self.vector_store.save_local(self.index_path)
            
            logger.info("Successfully built and saved FAISS index")
            
        except Exception as e:
            logger.error(f"Failed to build new index: {e}")
            raise RAGInitializationError(f"Failed to build FAISS index: {e}")
    
    def get_remedies(self, symptom_query: str) -> str:
        """
        Retrieve relevant content and generate remedy recommendations.
        
        Args:
            symptom_query: User's symptom description
            
        Returns:
            Generated remedy recommendations as formatted text
        """
        try:
            if not symptom_query or not symptom_query.strip():
                logger.warning("Empty symptom query provided")
                return "Please provide symptom description to get remedy recommendations."
            
            logger.info(f"Processing remedy query: {symptom_query[:50]}...")
            
            # Retrieve relevant context
            context_docs = self._retrieve_context(symptom_query)
            
            if not context_docs:
                logger.warning("No relevant context found")
                return "No relevant Ayurvedic remedies found for these symptoms."
            
            # Extract text from documents
            context_chunks = [doc.page_content for doc in context_docs]
            
            # Generate remedies
            remedies = self._generate_remedies(symptom_query, context_chunks)
            
            return remedies
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)
            return "Ayurvedic remedies temporarily unavailable. Please try again later."
    
    def _retrieve_context(self, query: str) -> List:
        """
        Retrieve top-k relevant chunks from vector store.
        
        Args:
            query: Search query
            
        Returns:
            List of Document objects
        """
        try:
            if self.vector_store is None:
                raise RAGQueryError("Vector store not initialized")
            
            logger.info(f"Retrieving top {self.top_k} relevant chunks...")
            
            # Perform similarity search
            docs = self.vector_store.similarity_search(query, k=self.top_k)
            
            logger.info(f"Retrieved {len(docs)} relevant chunks")
            return docs
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []
    
    def _generate_remedies(self, query: str, context: List[str]) -> str:
        """
        Generate remedy recommendations using LLM.
        
        Args:
            query: User's symptom query
            context: Retrieved context chunks
            
        Returns:
            Generated remedy text
        """
        try:
            if self.remedy_generator is None:
                raise RAGQueryError("Remedy generator not initialized")
            
            logger.info("Generating remedy recommendations...")
            
            remedies = self.remedy_generator.generate(query, context)
            
            return remedies
            
        except Exception as e:
            logger.error(f"Remedy generation failed: {e}")
            return "Unable to generate remedy recommendations at this time."
    
    def _get_index_size(self) -> int:
        """Get number of documents in the index."""
        try:
            if self.vector_store is not None:
                return self.vector_store.index.ntotal
            return 0
        except:
            return 0
