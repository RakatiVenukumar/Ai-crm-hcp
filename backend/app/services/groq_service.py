import json
import os
from typing import Any, Dict, Optional

from groq import Groq


class GroqService:
    MODEL_NAME = "gemma2-9b-it"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.getenv("GROQ_API_KEY")
        self._client = None

    def _get_client(self) -> Groq:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is not configured")
        if self._client is None:
            self._client = Groq(api_key=self._api_key)
        return self._client

    def _chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.MODEL_NAME,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""

    @staticmethod
    def _safe_json_parse(text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = text[start : end + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
        return {}

    def extract_interaction_entities(self, user_input: str) -> Dict[str, Any]:
        system_prompt = (
            "You extract structured CRM interaction data from text. "
            "Return valid JSON only, with keys: "
            "hcp_name, products_discussed, sentiment, summary, "
            "follow_up_recommendation, key_topics."
        )
        user_prompt = f"Extract fields from this interaction note:\n\n{user_input}"
        result = self._chat(system_prompt=system_prompt, user_prompt=user_prompt)
        return self._safe_json_parse(result)

    def summarize_interaction(self, interaction_notes: str) -> str:
        system_prompt = (
            "You create concise, professional summaries for pharmaceutical CRM notes."
        )
        user_prompt = f"Summarize this interaction in 3-5 sentences:\n\n{interaction_notes}"
        return self._chat(system_prompt=system_prompt, user_prompt=user_prompt)

    def generate_followup_recommendation(self, interaction_notes: str) -> str:
        system_prompt = (
            "You suggest practical follow-up actions for a pharma field representative."
        )
        user_prompt = (
            "Based on this interaction, provide actionable next steps:\n\n"
            f"{interaction_notes}"
        )
        return self._chat(system_prompt=system_prompt, user_prompt=user_prompt)

    def generate_sales_insight(self, interaction_notes: str) -> Dict[str, Any]:
        system_prompt = (
            "You analyze CRM interactions for sentiment, objections, opportunities, "
            "and product interest. Return valid JSON only with keys: "
            "sentiment, objections, opportunities, product_interest."
        )
        user_prompt = f"Analyze this interaction:\n\n{interaction_notes}"
        result = self._chat(system_prompt=system_prompt, user_prompt=user_prompt)
        return self._safe_json_parse(result)
