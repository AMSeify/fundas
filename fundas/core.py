"""
Fundas - AI-powered data import library using OpenRouter API

Core functionality for communicating with OpenRouter API to extract
structured data from various file types.
"""

import os
import requests
from typing import Dict, Any, Optional, List


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-3.5-turbo"):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If not provided, reads from OPENROUTER_API_KEY env variable.
            model: The AI model to use for processing. Default is gpt-3.5-turbo.
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def process_content(
        self, 
        content: str, 
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send content to OpenRouter API for processing.
        
        Args:
            content: The content to process (text, description, etc.)
            prompt: User prompt describing what to extract
            system_prompt: Optional system prompt to guide the AI
            
        Returns:
            Response from the API containing extracted data
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({
            "role": "user",
            "content": f"{prompt}\n\nContent to analyze:\n{content}"
        })
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with OpenRouter API: {str(e)}")
    
    def extract_structured_data(
        self,
        content: str,
        prompt: str,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from content based on user prompt.
        
        Args:
            content: The content to analyze
            prompt: User prompt describing what to extract
            columns: Optional list of column names to extract
            
        Returns:
            Dictionary containing extracted structured data
        """
        system_prompt = (
            "You are a data extraction assistant. Extract structured data from the provided content "
            "and return it in a JSON format that can be easily converted to a pandas DataFrame. "
            "Each key should be a column name and each value should be a list of values."
        )
        
        if columns:
            system_prompt += f"\n\nExtract the following columns: {', '.join(columns)}"
        
        full_prompt = (
            f"{prompt}\n\n"
            "Return the data as a JSON object where keys are column names and values are lists. "
            "If extracting single values, wrap them in a list. Example format:\n"
            '{"column1": ["value1"], "column2": ["value2"]}'
        )
        
        response = self.process_content(content, full_prompt, system_prompt)
        
        # Extract the response text
        if "choices" in response and len(response["choices"]) > 0:
            response_text = response["choices"][0]["message"]["content"]
            
            # Try to parse JSON from the response
            import json
            try:
                # Look for JSON in the response (it might be wrapped in markdown code blocks)
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    json_str = response_text.strip()
                
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw text in a structured format
                return {"content": [response_text]}
        
        return {"content": ["No response from API"]}
