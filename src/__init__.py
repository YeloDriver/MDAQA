"""
MDAQA: Multi-Document Academic Question Answering Dataset Generation Framework

This package provides tools for generating complex, multi-document question-answering
pairs from academic paper communities.
"""

__version__ = "1.0.0"
__author__ = "Hui HUANG"
__email__ = "hui.huang@univ-lyon2.fr"

from .llm_client import LLMClient, create_llm_client
from .data_loader import DataLoader
from .question_generator import QuestionGenerator
from .quality_evaluator import QualityEvaluator

__all__ = [
    "LLMClient",
    "create_llm_client", 
    "DataLoader",
    "QuestionGenerator",
    "QualityEvaluator"
]
