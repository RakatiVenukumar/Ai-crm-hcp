import json
import os
from typing import Any, Dict, Optional

from groq import Groq


class GroqService:
    MODEL_NAME = "llama-3.3-70b-versatile"

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
            "follow_up_recommendation, key_topics, time, attendees, "
            "materials_shared, samples_distributed, outcomes. "
            "For 'time': Extract any specific time mentioned (e.g., '3:30 PM', '14:30', 'afternoon', '10 AM'). "
            "If a time phrase is mentioned, convert it to HH:MM format (24-hour) or keep the exact phrasing if ambiguous. "
            "For follow_up_recommendation, suggest 1-2 concrete next steps. "
            "Use null for unknown fields. Never leave follow_up_recommendation as null if sentiment is positive or neutral."
        )
        user_prompt = f"Extract fields from this interaction note:\n\n{user_input}"
        result = self._chat(system_prompt=system_prompt, user_prompt=user_prompt)
        parsed = self._safe_json_parse(result)
        
        # Ensure follow_up_recommendation has a value if not provided
        if not parsed.get('follow_up_recommendation') and parsed.get('sentiment') in ['positive', 'neutral']:
            parsed['follow_up_recommendation'] = 'Send product documentation and schedule follow-up call'
        
        return parsed

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
    
    def generate_response_message(self, extracted_data: Dict[str, Any], is_correction: bool = False) -> str:
        """
        Generate a natural language response acknowledging the extraction.
        """
        hcp_name = extracted_data.get('hcp_name', 'HCP')
        sentiment = extracted_data.get('sentiment', 'neutral')
        followup = extracted_data.get('follow_up_recommendation', '')
        products = extracted_data.get('products_discussed', [])
        
        product_list = ", ".join(products) if products else "products discussed"
        
        if is_correction:
            message = f"✓ Updated: HCP is {hcp_name}, sentiment is {sentiment.capitalize()}. Discussed {product_list}."
        else:
            message = f"✓ Recorded: {hcp_name} - Sentiment: {sentiment.capitalize()}. Discussed {product_list}."
        
        if followup:
            message += f" Next step: {followup}"
        
        return message
