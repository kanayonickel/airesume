import os
import json
import requests
from django.conf import settings
from .models import Resume


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
        self.default_model = "mistralai/mistral-7b-instruct:free"
    
    def _make_request(self, messages, model=None, max_tokens=2000):
        """
        Internal method to make API requests to OpenRouter.
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
            # Debug output
            print(f"\n{'='*50}")
            print(f"DEBUG: Using model: {model or self.default_model}")
            print(f"DEBUG: API Key exists: {bool(self.api_key)}")
            if self.api_key:
                print(f"DEBUG: API Key first 10 chars: {self.api_key[:10]}...")
            print(f"DEBUG: Sending request to: {self.base_url}")
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"DEBUG: Status Code: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"\n{'='*50}")
            print(f"ERROR: OpenRouter API Error: {e}")
            
            if hasattr(e, 'response') and e.response is not None:
                print(f"ERROR: Response status: {e.response.status_code}")
                print(f"ERROR: Response text: {e.response.text[:500]}")
            
            print(f"{'='*50}\n")
            
            return f"I apologize, but I'm having trouble connecting right now. Please try again in a moment."
    
    def get_resume_response(self, user_message, conversation_history=None, user_context=None):
        """
        Get AI response for resume building conversation.
        """
        messages = []
        
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
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        return self._make_request(messages)
    
   
    
    def generate_resume_section(self, user, section_type, user_data):
        """
        Generate a specific resume section based on user data.
        Automatically saves it in the user's latest draft Resume.
        """
        prompts = {
            'summary': f"Write a professional resume summary for someone with this background: {json.dumps(user_data)}. Keep it concise, 2-3 sentences.",
            'experience': f"Format this work experience professionally: {json.dumps(user_data)}. Use strong action verbs and quantifiable achievements.",
            'skills': f"Organize these skills into categories (Technical, Soft Skills, etc.): {json.dumps(user_data)}.",
            'education': f"Format this education info professionally: {json.dumps(user_data)}. Include degree, institution, dates, and honors."
        }

        prompt = prompts.get(section_type, f"Help format this resume section: {json.dumps(user_data)}")
        messages = [
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt}
        ]

        # Call AI
        section_content = self._make_request(messages, max_tokens=1000)

        # Get latest draft Resume or create new
        resume = Resume.objects.filter(user=user, status='draft').order_by('-created_at').first()
        if not resume:
            resume = Resume.objects.create(user=user, status='draft', sections={})

        # Save section content
        resume.sections[section_type] = section_content
        resume.save()

        return section_content

    
    
  
    
    def improve_resume_content(self, user, section_type, current_content, improvement_focus=None):
        """
        Improve existing resume content and save to latest draft Resume.
        """
        focus_text = f" Focus on: {improvement_focus}" if improvement_focus else ""
        messages = [
            {"role": "system", "content": "You are an expert resume reviewer."},
            {"role": "user", "content": f"Improve this content:{focus_text}\n\n{current_content}"}
        ]

        improved_content = self._make_request(messages, max_tokens=1500)

        # Get latest draft Resume or create new
        resume = Resume.objects.filter(user=user, status='draft').order_by('-created_at').first()
        if not resume:
            resume = Resume.objects.create(user=user, status='draft', sections={})

        resume.sections[section_type] = improved_content
        resume.save()

        return improved_content


    
    def get_current_conversation_step(self, conversation_history=None, user_context=None):
        """
        Determine the current step in the resume building conversation.
        """
        steps = [
            {"id": 1, "title": "Personal Info", "description": "Tell me your name, contact info, and location"},
            {"id": 2, "title": "Professional Summary", "description": "What's your career objective or professional summary?"},
            {"id": 3, "title": "Work Experience", "description": "Let's detail your work history and achievements"},
            {"id": 4, "title": "Education", "description": "Share your educational background"},
            {"id": 5, "title": "Skills & Certifications", "description": "What are your key skills and certifications?"},
            {"id": 6, "title": "Final Review", "description": "Review and finalize your resume"}
        ]
        
        if not conversation_history or len(conversation_history) < 2:
            return {
                "current_step": 1,
                "total_steps": len(steps),
                "steps": steps,
                "percentage": 16
            }
        
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        step_count = len(user_messages)
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
    
    #deleting all chat conversations in the resume builder, Britney spears
    
    def reset_user_conversation(self, user, request=None):
        """
        Reset the current AI conversation and remove all draft resumes for a user.
        If `request` is provided, also clears session-based conversation data.
        """
        # 1. Clear session data
        if request:
            if 'resume_conversation' in request.session:
                del request.session['resume_conversation']
            if 'resume_data' in request.session:
                del request.session['resume_data']
            request.session.modified = True

        # 2. Delete all draft resumes for this user
        try:
            Resume.objects.filter(user=user, status='draft').delete()
        except Exception as e:
            print(f"Error deleting draft resumes for user {user.username}: {e}")
            return False

        return True
    
    #recommend jobs service
    def recommend_jobs(self, user, current_job_title, user_context=None, max_results=10):
        """
        Recommend jobs based on the user's current job title.
        Returns a structured list of job titles with descriptions.
        """
        prompt = f"""
        User is currently a {current_job_title}.
        Recommend {max_results} suitable job titles they could consider next.
        Include a brief description for each recommended role.
        Return the response in a numbered list format.
        """
        
        messages = [
            {"role": "system", "content": "You are a career advisor AI. Suggest jobs that fit the user's experience."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=1200)

