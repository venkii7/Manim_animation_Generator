from google import genai
from google.genai import types
from pydantic import BaseModel
import os
from typing import Optional
import asyncio

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"
    
    def _clean_schema_for_gemini(self, schema_dict: dict) -> dict:
        """Clean Pydantic schema to be compatible with Gemini API."""
        if isinstance(schema_dict, dict):
            # Remove additionalProperties
            if 'additionalProperties' in schema_dict:
                del schema_dict['additionalProperties']
            
            # Recursively clean nested schemas
            for key, value in schema_dict.items():
                if isinstance(value, dict):
                    schema_dict[key] = self._clean_schema_for_gemini(value)
                elif isinstance(value, list):
                    schema_dict[key] = [self._clean_schema_for_gemini(item) if isinstance(item, dict) else item for item in value]
        
        return schema_dict
    
    async def generate_structured(
        self,
        prompt: str,
        schema: BaseModel,
        system_instruction: str,
        temperature: float = 1.0
    ) -> BaseModel:
        """Generate structured output using Gemini with schema validation."""
        
        # Clean the schema for Gemini
        json_schema = schema.model_json_schema()
        cleaned_schema = self._clean_schema_for_gemini(json_schema)
        
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=cleaned_schema,
            temperature=temperature
        )
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=config
            )
            
            # Check finish reason
            if response.candidates[0].finish_reason != "STOP":
                raise Exception(f"Generation stopped: {response.candidates[0].finish_reason}")
            
            # Parse and validate
            return schema.model_validate_json(response.text)
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def chat_multi_turn(
        self,
        messages: list[dict],
        system_instruction: str,
        schema: Optional[BaseModel] = None
    ) -> str:
        """Multi-turn chat for plan refinement."""
        
        config_kwargs = {
            "system_instruction": system_instruction,
            "temperature": 1.0
        }
        
        if schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = schema.model_json_schema()
        
        config = types.GenerateContentConfig(**config_kwargs)
        
        try:
            chat = self.client.chats.create(model=self.model, config=config)
            
            # Send all messages
            for msg in messages:
                response = await asyncio.to_thread(
                    chat.send_message,
                    msg["content"]
                )
            
            if schema:
                return schema.model_validate_json(response.text)
            return response.text
        
        except Exception as e:
            raise Exception(f"Chat error: {str(e)}")
