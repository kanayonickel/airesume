# services.py - OPTIMIZED VERSION
import os
import json
import requests
from django.conf import settings
from .models import Resume


class OpenRouterService:
    """
    OpenRouter service with automatic fallback to free models.
    Primary: nousresearch/hermes-3.1 (your paid model)
    Fallback: Best free models → never shows "trouble connecting" again.
    """
    # Model priority list — paid first, then best free ones
    FALLBACK_MODELS = [
        "nousresearch/hermes-3.1",                    # Your main fast & smart model
        "meta-llama/llama-3.1-70b-instruct",           # Premium fallback (if you have credits)
        "mistralai/mistral-7b-instruct:free",          # Best free model
        "meta-llama/llama-3.1-8b-instruct:free",       # Excellent free alternative
        "google/gemma-2-9b-it:free",                   # Very stable
        "microsoft/phi-3-mini-128k-instruct:free",     # Fast & capable
        "qwen/qwen-2-7b-instruct:free",                # Often underused = instant response
        "openchat/openchat-3.5-0106:free",             # Great for chat
    ]

    def __init__(self):
        self.api_key = os.environ.get('OPENROUTER_API_KEY') or getattr(settings, 'OPENROUTER_API_KEY', None)
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment or settings")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = "nousresearch/hermes-3.1"

    def _make_request(self, messages, model=None, max_tokens=2000, max_retries=5):
        """
        Smart request with automatic model fallback.
        Tries your preferred model → instantly switches on failure.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            "X-Title": "Smartcv.ai - AI Cover Letter & Resume Builder",
        }

        preferred_model = model or self.default_model
        models_to_try = [preferred_model]
        # Add fallbacks (avoid duplicates)
        for m in self.FALLBACK_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        payload_base = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        for attempt in range(max_retries):
            current_model = models_to_try[attempt % len(models_to_try)]
            payload = payload_base.copy()
            payload["model"] = current_model

            print(f"\n→ Attempt {attempt + 1}: Using model → {current_model}")

            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ SUCCESS with {current_model}")
                    return data['choices'][0]['message']['content']

                # Rate limit → skip to next model immediately
                if response.status_code == 429:
                    print(f"⚡ Rate limited on {current_model} → switching model...")
                    continue

                # Server error → try next
                if response.status_code >= 500:
                    print(f"Server down on {current_model} → fallback...")
                    continue

                # Other HTTP errors
                print(f"HTTP {response.status_code} → {response.text[:200]}")
                response.raise_for_status()

            except requests.exceptions.Timeout:
                print(f"Timeout on {current_model} → trying next...")
                continue
            except requests.exceptions.RequestException as e:
                print(f"Request failed on {current_model}: {e}")
                continue

        # All models failed
        fallback_msg = (
            "I'm experiencing very high demand right now. "
            "The AI is temporarily slower than usual — please try again in 20-30 seconds. "
            "Your progress is saved!"
        )
        print("All models failed → returning graceful message")
        return fallback_msg

    # ═══════════════════════════════════════════════════════════
    # OPTIMIZED METHODS - CONCISE RESPONSES
    # ═══════════════════════════════════════════════════════════

    def generate_resume_section(self, user, section_type, user_data):
        """
        Generate CONCISE resume section questions.
        OPTIMIZED: Shorter prompts = faster, more focused responses.
        """
        # Extract user input
        user_input = user_data.get('user_input', '')
        
        # STEP-SPECIFIC PROMPTS (ultra-focused)
        prompts = {
            'personal info': {
                'system': "You are a resume assistant. Ask ONE clear question about contact details. Keep it under 30 words.",
                'user': f"User said: '{user_input}'. Ask for: full name, email, phone, location. Be brief and friendly."
            },
            'professional summary': {
                'system': "You are a resume assistant. Ask ONE question about career goals. Maximum 2 sentences.",
                'user': f"User said: '{user_input}'. Ask about their target role or career objective. Be concise."
            },
            'work experience': {
                'system': "You are a resume assistant. Ask ONE specific question about work history. Under 35 words.",
                'user': f"User said: '{user_input}'. Ask for job title, company, dates, OR key achievement. Focus on ONE thing."
            },
            'education': {
                'system': "You are a resume assistant. Ask ONE question about education. Maximum 25 words.",
                'user': f"User said: '{user_input}'. Ask for degree, school, and year. Be direct."
            },
            'skills & certifications': {
                'system': "You are a resume assistant. Ask for skills list. Maximum 20 words.",
                'user': f"User said: '{user_input}'. Ask them to list 5-10 key skills. Be brief."
            },
            'final review': {
                'system': "You are a resume assistant. Confirm completion. Maximum 30 words.",
                'user': f"User said: '{user_input}'. Confirm their resume is complete and offer to make changes. Be concise."
            }
        }
        
        # Get the right prompt for this section
        prompt_config = prompts.get(section_type, {
            'system': "You are a concise resume assistant. Ask ONE clear question.",
            'user': f"User said: '{user_input}'. Continue the conversation briefly."
        })
        
        messages = [
            {"role": "system", "content": prompt_config['system']},
            {"role": "user", "content": prompt_config['user']}
        ]
        
        # CRITICAL: Limit tokens to force conciseness
        section_content = self._make_request(messages, max_tokens=150)  # ← KEY CHANGE
        
        # Save section content
        resume = Resume.objects.filter(user=user, status='draft').exclude(title__exact='Cover Letter Draft').order_by('-created_at').first()
        if not resume:
            resume = Resume.objects.create(user=user, status='draft', sections={})
        
        resume.sections[section_type] = section_content
        resume.save()
        
        return section_content

    def get_resume_response(self, user_message, conversation_history=None, user_context=None):
        """
        OPTIMIZED: More focused system prompt for concise responses.
        """
        messages = []
        
        # SHORTER, MORE DIRECT SYSTEM PROMPT
        system_prompt = """You are a professional resume assistant. 

Rules:
- Keep ALL responses under 50 words
- Ask ONE question at a time
- Be direct and friendly
- Focus on gathering facts, not giving advice
- No lengthy explanations

Current focus: Collect information for ATS-friendly resume."""

        if user_context:
            current_step = user_context.get('current_step_title', 'resume')
            system_prompt += f"\n\nCurrent section: {current_step}. Ask a focused question about this section only."
        
        messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            # Only include last 4 messages to keep context short
            messages.extend(conversation_history[-4:])
        
        messages.append({"role": "user", "content": user_message})
        
        # Limit response length
        return self._make_request(messages, max_tokens=150)

    def improve_resume_content(self, user, section_type, current_content, improvement_focus=None):
        """
        OPTIMIZED: Shorter improvement prompts.
        """
        focus_text = f" Focus: {improvement_focus}" if improvement_focus else ""
        messages = [
            {"role": "system", "content": "You are a resume editor. Improve this content. Keep response under 100 words."},
            {"role": "user", "content": f"Improve:{focus_text}\n\n{current_content[:300]}"}  # Limit input too
        ]
        
        improved_content = self._make_request(messages, max_tokens=250)
        
        resume = Resume.objects.filter(user=user, status='draft').exclude(title__exact='Cover Letter Draft').order_by('-created_at').first()
        if not resume:
            resume = Resume.objects.create(user=user, status='draft', sections={})
        
        resume.sections[section_type] = improved_content
        resume.save()
        
        return improved_content

    def get_next_question(self, current_step, user_context=None):
        """
        OPTIMIZED: Much shorter default questions.
        """
        questions = {
            1: "What's your full name, email, phone, and location?",
            2: "What type of role are you targeting? What's your professional background?",
            3: "Tell me about your most recent job: title, company, dates, and 2-3 key achievements.",
            4: "What's your highest degree, institution, and graduation year?",
            5: "List 5-10 of your most relevant skills or certifications.",
            6: "Great! Your resume is ready. Want to make any changes?"
        }
        return questions.get(current_step, "What would you like to add?")

    def get_system_prompt_with_progress(self, current_step, user_context=None):
        """
        OPTIMIZED: Shorter system prompts for each step.
        """
        base_prompt = "You are a resume assistant. Keep responses under 40 words."
        
        step_focus = {
            1: "Ask for: name, email, phone, location. Be brief.",
            2: "Ask about target role and career summary. One question only.",
            3: "Ask for job title, company, dates, OR achievements. Focus on one.",
            4: "Ask for degree, school, year. Be direct.",
            5: "Ask for 5-10 key skills. Simple list.",
            6: "Confirm completion. Offer to make edits. Be concise."
        }
        
        focus = step_focus.get(current_step, "Continue briefly.")
        return f"{base_prompt} {focus}"

    # ═══════════════════════════════════════════════════════════
    # UNCHANGED METHODS (Keep as-is)
    # ═══════════════════════════════════════════════════════════

    def get_current_conversation_step(self, conversation_history=None, user_context=None):
        steps = [
            {"id": 1, "title": "Personal Info", "description": "Tell me your name, contact info, and location"},
            {"id": 2, "title": "Professional Summary", "description": "What's your career objective or professional summary?"},
            {"id": 3, "title": "Work Experience", "description": "Let's detail your work history and achievements"},
            {"id": 4, "title": "Education", "description": "Share your educational background"},
            {"id": 5, "title": "Skills & Certifications", "description": "What are your key skills and certifications?"},
            {"id": 6, "title": "Final Review", "description": "Review and finalize your resume"}
        ]
        if not conversation_history or len(conversation_history) < 2:
            return {"current_step": 1, "total_steps": len(steps), "steps": steps, "percentage": 16}
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        step_count = len(user_messages)
        current_step = min(step_count + 1, len(steps))
        return {
            "current_step": current_step,
            "total_steps": len(steps),
            "steps": steps,
            "percentage": int((current_step / len(steps)) * 100)
        }

    def reset_user_conversation(self, user, request=None):
        if request:
            if 'resume_conversation' in request.session:
                del request.session['resume_conversation']
            if 'resume_data' in request.session:
                del request.session['resume_data']
            request.session.modified = True
        try:
            Resume.objects.filter(user=user, status='draft').exclude(title__exact='Cover Letter Draft').delete()
        except Exception as e:
            print(f"Error deleting draft resumes for user {user.username}: {e}")
            return False
        return True

    def recommend_jobs(self, user, current_job_title, user_context=None, max_results=10):
        prompt = f"User is a {current_job_title}. List {max_results} suitable next job titles with brief descriptions. Numbered list format."
        messages = [
            {"role": "system", "content": "You are a career advisor. Be concise."},
            {"role": "user", "content": prompt}
        ]
        return self._make_request(messages, max_tokens=800)