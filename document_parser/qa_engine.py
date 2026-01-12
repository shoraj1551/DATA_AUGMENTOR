from config.settings import get_model_for_feature
from llm.client import get_client
import json

def generate_story_highlights(text, image_data=None):
    """
    Generate top 5 key insights/story from the document.
    """
    model = get_model_for_feature("document_parser")
    client = get_client()
    
    system_prompt = """You are an expert Analyst. 
    Analyze the provided document content and extract the "Top 5 Key Information" as a Story.
    Focus on the most valuable, high-level insights.
    
    Output Format:
    Return a list of 5 strings.
    Example:
    [
      "Revenue grew by 20% compared to last year.",
      "New product launch is scheduled for Q3.",
      ...
    ]
    Return ONLY valid JSON."""
    
    user_content = []
    if text:
        user_content.append({"type": "text", "text": f"Document Content:\n{text[:500000]}"}) # Limit to avoid overflow if massive
    
    # If image support is added later, we append image_url here
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content if len(user_content) > 0 else "No content"}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        # Handle various return formats
        if isinstance(data, list): return data
        if "highlights" in data: return data["highlights"]
        if "story" in data: return data["story"]
        # Fallback
        return list(data.values())[0] if data else []
        
    except Exception as e:
        return [f"Error generating highlights: {str(e)}"]

def ask_document_question(text, chat_history, question):
    """
    Q&A with the document using full context.
    """
    model = get_model_for_feature("document_parser")
    client = get_client()
    
    system_prompt = """You are a helpful Document Assistant.
    Answer the user's question based strictly on the provided document content.
    If the answer is not in the document, say so.
    Keep answers concise and professional."""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Inject Context (Limit to ~800k chars to be safe for 1M window)
    if text:
         messages.append({"role": "user", "content": f"Reference Document Content:\n{text[:800000]}"})
         
    # Add Chat History
    for msg in chat_history:
        messages.append(msg)
        
    messages.append({"role": "user", "content": question})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
