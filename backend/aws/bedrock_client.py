import boto3
import json
from typing import Optional
import os

class BedrockClient:
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", mock_mode: bool = False):
        self.model_id = model_id
        self.mock_mode = mock_mode
        
        if not mock_mode:
            # Initialize Bedrock client
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate response using AWS Bedrock or mock response
        """
        if self.mock_mode:
            return self._generate_mock_response(prompt)
        
        try:
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Make API call
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            return content.strip()
            
        except Exception as e:
            print(f"Error calling Bedrock: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _generate_mock_response(self, prompt: str) -> str:
        """
        Generate mock responses for testing without AWS
        """
        prompt_lower = prompt.lower()
        
        # Check if this is a RAG prompt with context
        if "knowledge base context:" in prompt_lower and "user question:" in prompt_lower:
            # Extract the question from the RAG prompt
            question_start = prompt_lower.find("user question:")
            if question_start != -1:
                question = prompt[question_start:].split("\n")[0].replace("user question:", "").strip()
                question_lower = question.lower()
                
                # Answer based on the specific question
                if "employee" in question_lower or "employees" in question_lower or "how many" in question_lower:
                    return "Based on the knowledge base, TechCorp Solutions has 150 employees."
                elif "company" in question_lower and "name" in question_lower:
                    return "Based on the knowledge base, the company name is TechCorp Solutions."
                elif "product" in question_lower and "price" in question_lower:
                    return "Based on the knowledge base, the products and their prices are:\n- CloudSync Pro: $299.99\n- DataViz Analytics: $499.99\n- SecureChat: $199.99"
                elif "ceo" in question_lower:
                    return "Based on the knowledge base, the CEO is Sarah Johnson with 15 years of experience."
                elif "revenue" in question_lower:
                    return "Based on the knowledge base, the company revenue is $5.2M."
                elif "customer" in question_lower:
                    return "Based on the knowledge base, the company has 2,500 customers with a 94.5% satisfaction rate."
                else:
                    return "Based on the knowledge base, I can provide information about TechCorp Solutions. Please ask a specific question about the company, products, team, or customers."
        
        # Direct queries (non-RAG)
        if "company" in prompt_lower and "name" in prompt_lower:
            return "Based on the knowledge base, the company name is TechCorp Solutions."
        
        elif "employee" in prompt_lower or "employees" in prompt_lower:
            return "TechCorp Solutions has 150 employees."
        
        elif "product" in prompt_lower and "price" in prompt_lower:
            return "The products and their prices are:\n- CloudSync Pro: $299.99\n- DataViz Analytics: $499.99\n- SecureChat: $199.99"
        
        elif "ceo" in prompt_lower:
            return "The CEO is Sarah Johnson with 15 years of experience and a background as a former Google executive."
        
        elif "revenue" in prompt_lower:
            return "The company revenue is $5.2M."
        
        elif "headquarters" in prompt_lower:
            return "The company headquarters is located in San Francisco, CA."
        
        elif "founded" in prompt_lower:
            return "TechCorp Solutions was founded in 2020."
        
        elif "customer" in prompt_lower:
            return "The company has 2,500 customers with a 94.5% satisfaction rate."
        
        elif "partnership" in prompt_lower:
            return "TechCorp has partnerships with Microsoft (Technology) and Salesforce (CRM Integration)."
        
        else:
            return "I can help you with information about TechCorp Solutions. Please ask about the company, products, team, customers, or partnerships."
    
    async def extract_structured_data(self, text: str, schema: dict) -> dict:
        """
        Extract structured data from text using Bedrock or mock
        """
        if self.mock_mode:
            return self._extract_mock_structured_data(text, schema)
        
        prompt = f"""Extract structured data from the following text according to the schema provided.

Text: {text}

Schema: {json.dumps(schema, indent=2)}

Please extract the data and return it as a valid JSON object:"""
        
        response = await self.generate_response(prompt)
        
        try:
            # Try to parse JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"error": "Could not extract JSON from response"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response"}
    
    def _extract_mock_structured_data(self, text: str, schema: dict) -> dict:
        """
        Mock structured data extraction
        """
        return {
            "company_name": "TechCorp Solutions",
            "founded": "2020",
            "employees": 150,
            "revenue": "$5.2M"
        }
    
    async def extract_named_entities(self, text: str) -> dict:
        """
        Extract named entities from text
        """
        if self.mock_mode:
            return self._extract_mock_named_entities(text)
        
        prompt = f"""Extract named entities from the following text. Return the results as JSON with categories: PERSON, ORGANIZATION, LOCATION, DATE, MONEY, PERCENTAGE.

Text: {text}

Return JSON in this format:
{{
  "PERSON": ["names"],
  "ORGANIZATION": ["organizations"],
  "LOCATION": ["locations"],
  "DATE": ["dates"],
  "MONEY": ["monetary amounts"],
  "PERCENTAGE": ["percentages"]
}}"""
        
        response = await self.generate_response(prompt)
        
        try:
            # Try to parse JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"error": "Could not extract JSON from response"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response"}
    
    def _extract_mock_named_entities(self, text: str) -> dict:
        """
        Mock named entity extraction
        """
        return {
            "PERSON": ["Sarah Johnson", "Michael Chen", "Emily Rodriguez"],
            "ORGANIZATION": ["TechCorp Solutions", "Google", "Microsoft", "Salesforce"],
            "LOCATION": ["San Francisco, CA"],
            "DATE": ["2020", "2021-03-15", "2021-08-22", "2022-01-10"],
            "MONEY": ["$5.2M", "$299.99", "$499.99", "$199.99"],
            "PERCENTAGE": ["94.5%"]
        } 