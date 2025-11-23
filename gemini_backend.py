import os
import json
import google.genai as genai
from google.genai import types
from config import API_KEY
#from dotenv import load_dotenv

# Load API Key

# Initialize Client - YAHI CHANGE HAI
client = genai.Client(api_key=API_KEY)

def analyze_resume(file_bytes, mime_type):
    """
    Analyzes the resume using Gemini 2.5 Flash.
    Returns a structured dictionary.
    """
    prompt = """
    You are an expert HR Resume Screener. Analyze the attached resume.
    Provide a structured JSON response with:
    1. The candidate's full name (Extract carefully from the header).
    2. A score from 0-100 based on professional standards.
    3. A brief professional summary of the candidate (Write in implied first-person "Resume Voice", e.g., "Ambitious Software Engineer...", do NOT use "He is" or "The candidate is").
    4. Top 3 strengths.
    5. Top 3 weaknesses or areas for improvement.
    6. The most suitable job role for this profile - provide ONLY ONE CLEAR JOB TITLE like "Frontend Developer", "Data Analyst", "Marketing Manager" etc. Keep it short and industry standard.
    7. A list of technical and soft skills found.

    IMPORTANT: For job role, return only one concise job title that best matches the candidate's experience. Do not add descriptions or multiple roles.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING"},
                        "score": {"type": "NUMBER"},
                        "summary": {"type": "STRING"},
                        "strengths": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "weaknesses": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "suggestedRole": {"type": "STRING"},
                        "skillsFound": {"type": "ARRAY", "items": {"type": "STRING"}}
                    }
                }
            )
        )
        
        if response.text:
            result = json.loads(response.text)
            
            # CLEAN THE JOB TITLE - Remove extra descriptions
            if 'suggestedRole' in result:
                role = result['suggestedRole']
                # Keep only the main job title (first part before any comma or lengthy description)
                if ',' in role:
                    role = role.split(',')[0]
                if ' with ' in role:
                    role = role.split(' with ')[0]
                if ' - ' in role:
                    role = role.split(' - ')[0]
                # Remove extra words and keep it clean
                role = role.strip()
                result['suggestedRole'] = role
            
            return result
        return None

    except Exception as e:
        print(f"Error in analysis: {e}")
        return None

def suggest_improvements(weaknesses):
    """
    Generates actionable fixes for the detected weaknesses.
    """
    prompt = f"""
    You are a career coach. For each of the following resume weaknesses, provide one specific, actionable tip on how to fix it or phrase it better.
    Weaknesses: {json.dumps(weaknesses)}
    
    Return a JSON object with a property "improvements" which is an array of strings. The order must match the input.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "improvements": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        }
                    }
                }
            )
        )

        if response.text:
            data = json.loads(response.text)
            return data.get("improvements", [])
        return []
    except Exception as e:
        print(f"Error in improvements: {e}")
        return []

def find_jobs(query, location, mode):
    """
    Uses Gemini with Google Search Grounding to find real-time jobs.
    """
    search_prompt = f'Find active job listings for "{query}" in "{location}".'
    if mode and mode != "Any":
        search_prompt += f" The job type must be {mode}."
    
    search_prompt += " List 5 specific job openings with company names. Focus on jobs posted in the last 30 days."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=search_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        # Parse Grounding Metadata to get links
        sources = []
        if response.candidates and response.candidates[0].grounding_metadata:
            chunks = response.candidates[0].grounding_metadata.grounding_chunks
            for chunk in chunks:
                if chunk.web:
                    sources.append({
                        "title": chunk.web.title,
                        "company": "External Site",
                        "url": chunk.web.uri,
                        "snippet": "Click to view details"
                    })
        
        return {"text": response.text, "sources": sources}

    except Exception as e:
        print(f"Error in job search: {e}")
        return {"text": "Error fetching jobs.", "sources": []}