import os
import json
import requests
from django.conf import settings


class OpenRouterService:
    """
    Service class to handle OpenRouter API interactions for resume building.
    """
    
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.environ.get('OPENROUTER_API_KEY') or getattr(settings, 'OPENROUTER_API_KEY', None)
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment or settings")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Or use "openai/gpt-4" or other models
        # self.default_model = "anthropic/claude-3.5-sonnet" 
        self.default_model = "google/gemma-2-9b-it:free"  
        
        
        
    def _make_request(self, messages, model=None, max_tokens=2000):
        """
        Internal method to make API requests to OpenRouter.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens in response
            
        Returns:
            str: AI response content
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            "X-Title": "AI Resume Builder",
        }
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"OpenRouter API Error: {e}")
            return f"I apologize, but I'm having trouble connecting right now. Please try again in a moment."
    
    def get_resume_response(self, user_message, conversation_history=None, user_context=None):
        """
        Get AI response for resume building conversation.
        
        Args:
            user_message: Current user message
            conversation_history: List of previous messages (optional)
            user_context: Dict with user info like name, profile, etc.
            
        Returns:
            str: AI response
        """
        messages = []
        
        # System prompt for resume building
        system_prompt = """You are an expert resume builder assistant helping users create professional, ATS-friendly resumes. 

Your role:
- Ask relevant questions to gather information about their work experience, education, skills
- Provide helpful suggestions for improving resume content
- Be conversational and encouraging
- Keep responses concise but helpful
- Focus on one section at a time (contact info, summary, experience, education, skills)

Guidelines:
- Use professional but friendly language
- Ask follow-up questions to get detailed information
- Suggest strong action verbs and quantifiable achievements
- Help users structure their experience effectively"""

        if user_context:
            system_prompt += f"\n\nUser context: {json.dumps(user_context)}"
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return self._make_request(messages)
    
    def generate_resume_section(self, section_type, user_data):
        """
        Generate a specific resume section based on user data.
        
        Args:
            section_type: Type of section (e.g., 'summary', 'experience', 'skills')
            user_data: Dict containing relevant information
            
        Returns:
            str: Generated section content
        """
        prompts = {
            'summary': f"Write a professional resume summary for someone with this background: {json.dumps(user_data)}. Keep it to 2-3 sentences, focusing on key strengths and career goals.",
            
            'experience': f"Format this work experience professionally: {json.dumps(user_data)}. Use strong action verbs and include quantifiable achievements where possible.",
            
            'skills': f"Organize these skills into categories (Technical, Soft Skills, etc.): {json.dumps(user_data)}. Present them in a clean, scannable format.",
            
            'education': f"Format this education information professionally: {json.dumps(user_data)}. Include degree, institution, dates, and any relevant honors or achievements."
        }
        
        prompt = prompts.get(section_type, f"Help format this resume section: {json.dumps(user_data)}")
        
        messages = [
            {"role": "system", "content": "You are a professional resume writer. Format content clearly and professionally."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1000)
    
    def improve_resume_content(self, current_content, improvement_focus=None):
        """
        Improve existing resume content.
        
        Args:
            current_content: The resume content to improve
            improvement_focus: Specific area to focus on (optional)
            
        Returns:
            str: Improved content with suggestions
        """
        focus_text = f" Focus especially on: {improvement_focus}" if improvement_focus else ""
        
        messages = [
            {"role": "system", "content": "You are an expert resume reviewer. Provide constructive feedback and improvements."},
            {"role": "user", "content": f"Review and improve this resume content:{focus_text}\n\n{current_content}"}
        ]
        
        return self._make_request(messages, max_tokens=1500)
    
    
    
    # conversation steps flow

def get_current_conversation_step(self, conversation_history=None, user_context=None):
    """
    Determine the current step in the resume building conversation.
    
    Args:
        conversation_history: List of previous messages
        user_context: Dict with user info
        
    Returns:
        dict: Step information
    """
    # Define conversation flow steps
    steps = [
        {"id": 1, "title": "Personal Info", "description": "Tell me your name, contact info, and location"},
        {"id": 2, "title": "Professional Summary", "description": "What's your career objective or professional summary?"},
        {"id": 3, "title": "Work Experience", "description": "Let's detail your work history and achievements"},
        {"id": 4, "title": "Education", "description": "Share your educational background"},
        {"id": 5, "title": "Skills & Certifications", "description": "What are your key skills and certifications?"},
        {"id": 6, "title": "Final Review", "description": "Review and finalize your resume"}
    ]
    
    # Default to step 1 if no conversation history
    if not conversation_history or len(conversation_history) < 2:
        return {
            "current_step": 1,
            "total_steps": len(steps),
            "steps": steps,
            "percentage": 16  # 1/6 * 100
        }
    
    # Analyze conversation to determine current step
    # Count user messages as rough progress indicator
    user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
    step_count = len(user_messages)
    
    # Cap at total steps
    current_step = min(step_count + 1, len(steps))
    
    return {
        "current_step": current_step,
        "total_steps": len(steps),
        "steps": steps,
        "percentage": int((current_step / len(steps)) * 100)
    }

def get_next_question(self, current_step, user_context=None):
    """
    Get the appropriate question for the current step.
    """
    questions = {
        1: "Let's start with your personal information. What is your full name, email, phone number, and location?",
        2: "Great! Now, tell me about your professional background. What kind of role are you targeting, and what's your career summary?",
        3: "Now let's detail your work experience. Please share:\n- Job titles\n- Companies\n- Dates of employment\n- Key responsibilities\n- Major achievements (use numbers when possible)",
        4: "What about your education? Please include:\n- Degrees/Certificates\n- Institutions\n- Graduation dates\n- Honors or relevant coursework",
        5: "What skills, technologies, or certifications do you have? Include both technical and soft skills.",
        6: "Perfect! Let's review your resume. Would you like to:\n1. Add any additional sections?\n2. Adjust formatting?\n3. Optimize for a specific job title?"
    }
    
    return questions.get(current_step, "What would you like to add or modify about your resume?")

def get_system_prompt_with_progress(self, current_step, user_context=None):
    """
    Get system prompt adjusted for current conversation step.
    """
    base_prompt = """You are an expert resume builder assistant helping users create professional, ATS-friendly resumes."""
    
    step_focus = {
        1: "Focus on gathering personal contact information (name, email, phone, location, LinkedIn). Be friendly and welcoming.",
        2: "Focus on extracting career objectives, professional summary, and target roles. Help them articulate their value proposition.",
        3: "Focus on work experience. Ask for specific achievements, quantify results, and identify relevant skills used.",
        4: "Focus on education details, certifications, and relevant coursework or projects.",
        5: "Focus on categorizing skills (technical, soft, tools), proficiency levels, and certifications.",
        6: "Focus on reviewing completeness, suggesting improvements, and offering customization options."
    }
    
    focus = step_focus.get(current_step, "Continue the conversation naturally to complete their resume.")
    
    return f"{base_prompt}\n\nCurrent Phase: {focus}\n\nGuidelines:\n- Keep responses concise but helpful\n- Ask one focused question at a time\n- Provide examples if user seems unsure\n- Validate information received\n- Move to next phase when current one is complete"