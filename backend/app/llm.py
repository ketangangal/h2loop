import os
import re
import textwrap
from typing import Optional

from langchain_openai import AzureChatOpenAI


def extract_mermaid(text: str) -> str:
    """
    Extract Mermaid diagram from markdown code fence.
    Falls back to returning raw text if no fence found.
    """
    fence = re.search(r"```(?:mermaid)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return text.strip()


class LLMClient:
    """
    Azure OpenAI via LangChain; falls back to stub if not configured.
    Expected env: AZURE_API_KEY, AZURE_API_ENDPOINT, AZURE_DEPLOYMENT, optional AZURE_API_VERSION.
    """

    def __init__(self):
        """
        Initialize LLM client from environment variables.
        Falls back to stub mode if Azure credentials not configured.
        """
        self.deployment = os.getenv("AZURE_DEPLOYMENT")
        self.endpoint = os.getenv("AZURE_API_ENDPOINT")
        self.api_key = os.getenv("AZURE_API_KEY")
        self.api_version = os.getenv("AZURE_API_VERSION", "2024-06-01")

    def _client(self) -> Optional[AzureChatOpenAI]:
        """
        Lazy Azure OpenAI client creation.
        Returns None if credentials missing (triggers stub mode).
        """
        if not (self.deployment and self.endpoint and self.api_key):
            return None
        return AzureChatOpenAI(
            azure_deployment=self.deployment,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            temperature=0,
        )

    async def generate_from_code(self, code: str) -> str:
        """
        Generate Mermaid flowchart from C code using Azure OpenAI (async).
        Returns stub flowchart if credentials not configured.
        Sanitizes quotes from output to prevent Mermaid parse errors.
        TODO: Add timeout to prevent indefinite waits on slow LLM responses.
        TODO: Add cost tracking or usage limits if exposing publicly.
        TODO: Consider using ast-grep to pre-parse C code structure.
        """
        prompt = textwrap.dedent(
            f"""
            Analyze the following C code and produce a Mermaid flowchart representing the program flow.
            
            IMPORTANT RULES for valid Mermaid syntax:
            - Use flowchart TD syntax
            - NEVER use quotes inside node labels
            - Use simple descriptive text without quotes
            - Example: A[Read input] not A[Read "input"]
            
            Return ONLY a mermaid fenced block.
            
            C code:
            {code}
            """
        ).strip()

        client = self._client()
        if not client:
            print("No client")
            return self.stub_flowchart()

        try:
            # Use ainvoke for async LangChain call
            message = await client.ainvoke(
                [
                    (
                        "system",
                        "You generate valid Mermaid flowcharts for C code. CRITICAL: Never use quotes inside node labels. Use simple text without quotes or special characters. Focus on main program flow.",
                    ),
                    ("user", prompt),
                ]
            )
            content: str = getattr(message, "content", "") or ""
            mermaid_text = extract_mermaid(content)
            # Clean up any quotes that might cause parse errors
            mermaid_text = self._sanitize_mermaid(mermaid_text)
            return mermaid_text
        except Exception as exc:
            raise RuntimeError(f"LLM call failed: {exc}") from exc
    
    def _sanitize_mermaid(self, mermaid_text: str) -> str:
        """
        Remove quotes from inside node labels to prevent Mermaid parse errors.
        Applies regex twice per line to handle multiple quotes.
        """
        lines = []
        for line in mermaid_text.split('\n'):
            # Remove quotes from inside brackets and parentheses
            # Pattern: find content between [ ] or ( ) and remove quotes
            line = re.sub(r'\[([^\]]*)"([^\]]*)\]', r'[\1\2]', line)
            line = re.sub(r'\[([^\]]*)"([^\]]*)\]', r'[\1\2]', line)  # Apply twice for multiple quotes
            line = re.sub(r'\(([^\)]*)"([^\)]*)\)', r'(\1\2)', line)
            line = re.sub(r'\(([^\)]*)"([^\)]*)\)', r'(\1\2)', line)  # Apply twice for multiple quotes
            lines.append(line)
        return '\n'.join(lines)

    def stub_flowchart(self) -> str:
        """
        Fallback stub when LLM is not configured.
        Returns a minimal valid Mermaid flowchart for testing.
        """
        return textwrap.dedent(
            """
            flowchart TD
              Start([Start]) --> Process{{Analyze Code}}
              Process --> End([End])
            """
        ).strip()

