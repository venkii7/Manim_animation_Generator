import boto3
import json
import os
import asyncio
from botocore.config import Config
from pydantic import BaseModel
from typing import Optional


class ClaudeClient:
    def __init__(self):
        # AWS credentials must be set via env vars
        bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        if bearer_token:
            os.environ["AWS_BEARER_TOKEN_BEDROCK"] = bearer_token

        # LLM responses with large token limits can take several minutes.
        # read_timeout must be >> max generation time; connect_timeout is short.
        read_timeout = int(os.getenv("CLAUDE_READ_TIMEOUT", "600"))  # 10 min default
        self.bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
            config=Config(
                read_timeout=read_timeout,
                connect_timeout=10,
                retries={"max_attempts": 2, "mode": "standard"},
            ),
        )

        self.model_id = os.getenv("CLAUDE_MODEL_ID", "us.anthropic.claude-sonnet-4-6")

        # Per-task max_tokens — Claude generates UP TO this limit.
        # Use generous limits to prevent truncation of complex animations.
        # Planning JSON: complex animations can be 10k+ tokens with detailed timelines
        # Code generation: complex Manim scenes can be 10k+ tokens
        # Chat refinement: similar to planning.
        self.planning_max_tokens = int(os.getenv("CLAUDE_PLANNING_MAX_TOKENS", "16000"))
        self.code_max_tokens     = int(os.getenv("CLAUDE_CODE_MAX_TOKENS",     "16000"))
        self.chat_max_tokens     = int(os.getenv("CLAUDE_CHAT_MAX_TOKENS",     "8000"))

        # Per-task temperature defaults
        self.planning_temperature = float(os.getenv("CLAUDE_PLANNING_TEMPERATURE", "1.0"))
        self.code_temperature     = float(os.getenv("CLAUDE_CODE_TEMPERATURE",     "0.7"))
        self.chat_temperature     = float(os.getenv("CLAUDE_CHAT_TEMPERATURE",     "1.0"))

    def _invoke(self, messages: list[dict], system: str, temperature: float, max_tokens: int) -> str:
        """Stream from Bedrock and return the full assembled text.
        
        Uses invoke_model_with_response_stream so large responses are never
        truncated by HTTP payload size limits.
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
            "temperature": temperature,
        }

        response = self.bedrock.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=json.dumps(body),
        )

        chunks = []
        for event in response["body"]:
            chunk = event.get("chunk")
            if not chunk:
                continue
            data = json.loads(chunk["bytes"].decode("utf-8"))
            # Collect text deltas from content blocks
            if data.get("type") == "content_block_delta":
                delta = data.get("delta", {})
                if delta.get("type") == "text_delta":
                    chunks.append(delta.get("text", ""))
        return "".join(chunks)

    def _extract_json(self, text: str) -> str:
        """Extract the first complete JSON object from Claude's response.
        
        Handles:
        - Raw JSON with no wrapper
        - ```json ... ``` / ``` ... ``` code fences
        - Surrounding prose (bracket-match to find the object)
        """
        text = text.strip()

        # Strip code fences first
        if text.startswith("```"):
            lines = text.splitlines()
            inner_lines = lines[1:]
            # Remove closing fence if present
            if inner_lines and inner_lines[-1].strip() == "```":
                inner_lines = inner_lines[:-1]
            text = "\n".join(inner_lines).strip()

        # If it already starts with { we're done
        if text.startswith("{"):
            return text

        # Bracket-match: find the first { and its matching }
        start = text.find("{")
        if start == -1:
            return text  # let pydantic surface the error
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[start:], start):
            if escape:
                escape = False
                continue
            if ch == "\\" and in_string:
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return text[start:]  # fallback: return from first { to end

    async def generate_structured(
        self,
        prompt: str,
        schema: BaseModel,
        system_instruction: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
    ) -> BaseModel:
        """Generate structured output validated against the given Pydantic schema."""

        json_schema = json.dumps(schema.model_json_schema(), indent=2)

        system = (
            f"{system_instruction}\n\n"
            "RESPONSE FORMAT:\n"
            "You MUST respond with ONLY valid JSON that strictly conforms to the schema below.\n"
            "Do NOT include any explanation, markdown, or text outside the JSON object.\n\n"
            f"JSON Schema:\n{json_schema}"
        )

        messages = [{"role": "user", "content": prompt}]
        tokens = max_tokens or self.planning_max_tokens

        try:
            raw = await asyncio.to_thread(self._invoke, messages, system, temperature, tokens)
            json_text = self._extract_json(raw)
            return schema.model_validate_json(json_text)
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    async def chat_multi_turn(
        self,
        messages: list[dict],
        system_instruction: str,
        schema: Optional[BaseModel] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> "str | BaseModel":
        """Multi-turn conversation for plan refinement."""

        if temperature is None:
            temperature = self.chat_temperature
        tokens = max_tokens or self.chat_max_tokens

        if schema:
            json_schema = json.dumps(schema.model_json_schema(), indent=2)
            system = (
                f"{system_instruction}\n\n"
                "RESPONSE FORMAT:\n"
                "You MUST respond with ONLY valid JSON that strictly conforms to the schema below.\n"
                "Do NOT include any explanation, markdown, or text outside the JSON object.\n\n"
                f"JSON Schema:\n{json_schema}"
            )
        else:
            system = system_instruction

        # Convert messages to Bedrock format (role must alternate user/assistant)
        bedrock_messages = [
            {"role": m.get("role", "user"), "content": m["content"]}
            for m in messages
        ]

        try:
            raw = await asyncio.to_thread(self._invoke, bedrock_messages, system, temperature, tokens)
            if schema:
                json_text = self._extract_json(raw)
                return schema.model_validate_json(json_text)
            return raw
        except Exception as e:
            raise Exception(f"Claude chat error: {str(e)}")
