import httpx
from openai import OpenAI

class AIService:
    def __init__(self, api_key: str):
        """
        Initializes the OpenAI client with a fresh HTTP client to sidestep local proxy keyword issues.
        """
        # Explicitly passing a clean Client prevents the internal architecture from injecting conflicting arguments
        clean_http_client = httpx.Client() 
        self.client = OpenAI(api_key=api_key, http_client=clean_http_client)

    def query_repo(self, repo_context: str, user_question: str) -> str:
        """
        Sends the repository code base context and the user's question to the LLM.
        """
        try:
            # We construct a system prompt instructing the AI how to behave
            system_instruction = (
                "You are an expert code assistant specialized in analyzing repositories.\n"
                "You are given the contents of a GitHub repository below. Use this context "
                "to answer the user's question accurately. If the answer cannot be found in the "
                "code, explain what is missing rather than making things up.\n\n"
                f"--- REPOSITORY CONTEXT ---\n{repo_context}"
            )

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and efficient for handling code contexts
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.2  # Lower temperature makes the AI stick closer to facts
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")