"""
Unified LLM client that supports multiple providers.
"""
import os
import yaml
import time
import random
import json
from typing import Dict, Any, Optional


class LLMClient:
    """Unified client for different LLM providers."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the LLM client with configuration."""
        self.config = self._load_config(config_path)
        self.client = self._initialize_client()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                "Please copy config/config_template.yaml to config/config.yaml and fill in your values."
            )
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider."""
        provider = self.config['llm']['provider'].lower()
        
        if provider == "openai":
            from openai import OpenAI
            return OpenAI(
                api_key=self.config['llm']['api_key'],
                base_url=self.config['llm'].get('api_base')
            )
        
        elif provider == "azure_openai":
            from openai import AzureOpenAI
            return AzureOpenAI(
                api_key=self.config['llm']['api_key'],
                azure_endpoint=self.config['llm']['api_base'],
                api_version=self.config['llm']['api_version']
            )
        
        elif provider == "anthropic_vertex":
            from anthropic import AnthropicVertex
            return AnthropicVertex(
                project_id=self.config['llm']['project_id'],
                region=self.config['llm']['region']
            )
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_response(self, system_prompt: str, user_prompt: str, 
                         use_json_format: bool = False) -> str:
        """Generate response using the configured LLM."""
        provider = self.config['llm']['provider'].lower()
        
        if provider in ["openai", "azure_openai"]:
            return self._generate_openai_response(system_prompt, user_prompt, use_json_format)
        elif provider == "anthropic_vertex":
            return self._generate_anthropic_response(system_prompt, user_prompt)
        else:
            raise ValueError(f"Response generation not implemented for provider: {provider}")
    
    def _generate_openai_response(self, system_prompt: str, user_prompt: str, 
                                 use_json_format: bool = False) -> str:
        """Generate response using OpenAI API."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.config['llm']['model'],
            "messages": messages,
            "temperature": self.config['llm']['temperature'],
            "max_tokens": self.config['llm']['max_tokens']
        }
        
        if use_json_format:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def _generate_anthropic_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Anthropic API."""
        response = self.client.messages.create(
            model=self.config['llm']['model'],
            max_tokens=self.config['llm']['max_tokens'],
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self.config['llm']['temperature']
        )
        return response.content[0].text
    
    def generate_with_retry(self, system_prompt: str, user_prompt: str, 
                           use_json_format: bool = False) -> str:
        """Generate response with exponential backoff retry."""
        max_retries = self.config['processing']['max_retries']
        base_delay = self.config['processing']['base_delay']
        max_delay = self.config['processing']['max_delay']
        
        for attempt in range(max_retries):
            try:
                return self.generate_response(system_prompt, user_prompt, use_json_format)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = min(max_delay, base_delay * 2**attempt) + random.uniform(0, 1)
                print(f"Error occurred: {e}. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
        
        raise Exception("Max retries exceeded")


def create_llm_client(config_path: str = "config/config.yaml") -> LLMClient:
    """Factory function to create LLM client."""
    return LLMClient(config_path)
