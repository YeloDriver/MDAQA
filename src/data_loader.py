"""
Data loading utilities for MDAQA project.
"""
import json
import os
import yaml
from typing import Dict, List, Tuple, Optional, Any


class DataLoader:
    """Handles loading and processing of input data files."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize data loader with configuration."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def load_community_data(self) -> List[Dict[str, Any]]:
        """Load community detection results."""
        community_path = self.config['data']['community_data']
        try:
            with open(community_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single community and list of communities
            if isinstance(data, dict) and 'community_id' in data:
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise ValueError("Invalid community data format")
                
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Community data file not found: {community_path}\n"
                "Please provide the community detection results file."
            )
    
    def load_semantic_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load semantic ID to arXiv ID mapping."""
        mapping_path = self.config['data']['semantic_mapping']
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Semantic mapping file not found: {mapping_path}\n"
                "Please provide the semantic to arXiv ID mapping file."
            )
    
    def get_paper_content(self, arxiv_ids: List[Tuple[str, str]]) -> Tuple[Optional[str], List[Tuple[str, str]]]:
        """
        Load paper content from SPIQA dataset.
        
        Args:
            arxiv_ids: List of (arxiv_id, title) tuples
            
        Returns:
            Tuple of (combined_content, valid_arxiv_ids)
        """
        contents = ""
        spiqa_path = self.config['data']['spiqa_path']
        min_size = self.config['processing']['min_file_size'] * 1024  # Convert to bytes
        max_size = self.config['processing']['max_file_size'] * 1024
        
        valid_arxiv_ids = []
        
        for arxiv_id, title in arxiv_ids:
            content = self._load_single_paper(arxiv_id, spiqa_path, min_size, max_size)
            if content:
                contents += f"**title**: {title}\n**arxiv_id**: {arxiv_id}\n**content**: {content}\n\n"
                valid_arxiv_ids.append((arxiv_id, title))
        
        # Need at least 2 papers for multi-document QA
        if len(valid_arxiv_ids) <= 1:
            return None, None
        
        # Check total content length
        max_content_length = self.config['processing']['max_content_length']
        if len(contents) > max_content_length:
            return None, None
        
        return contents, valid_arxiv_ids
    
    def _load_single_paper(self, arxiv_id: str, spiqa_path: str, 
                          min_size: int, max_size: int) -> Optional[str]:
        """Load content for a single paper."""
        # Try different version numbers
        for version in range(1, 15):
            file_name = f"{arxiv_id}v{version}.txt"
            file_path = os.path.join(spiqa_path, file_name)
            
            if not os.path.exists(file_path):
                continue
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size < min_size or file_size > max_size:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    
                    # Skip files that start with LaTeX sections
                    if "\\section" in first_line:
                        continue
                    
                    # Read the rest of the content
                    f.seek(0)  # Reset to beginning
                    content = f.read().replace("\n\n", "\n")
                    return content
                    
            except (UnicodeDecodeError, IOError):
                continue
        
        return None
    
    def load_progress(self, file_path: str) -> Dict[str, Any]:
        """Load progress from a JSON file."""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_progress(self, data: Dict[str, Any], file_path: str) -> None:
        """Save progress to a JSON file."""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
