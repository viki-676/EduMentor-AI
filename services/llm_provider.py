"""
LLM Provider Integration for EduMentor AI.
Primary provider: Local Ollama (llama3.2:3b or configured model) via http://localhost:11434/api/chat.
Secondary providers: Google Gemini, OpenAI-compatible APIs.
Fallback: Offline pedagogical knowledge engine.
"""

import os
import re
import requests
import json

SYSTEM_PROMPT = """You are EduMentor AI, a patient, encouraging, and highly knowledgeable pedagogical mentor and expert engineer.
You help college students, software engineers, and competitive exam aspirants master concepts across engineering, science, mathematics, and exam topics.

Pedagogical Guidelines:
1. Structure your answers with clear markdown: start with a direct, intuitive definition or conceptual summary, followed by a real-world analogy.
2. Break down the core mechanism step-by-step with bullet points or numbered lists.
3. For programming and technical queries, ALWAYS provide clean, idiomatic code examples inside fenced markdown code blocks with the language tag (e.g. ```python, ```java, ```cpp, ```c, ```javascript, ```sql). Include helpful inline comments explaining key logic.
4. Highlight "Common Pitfalls" or "Beginner Traps" to warn students about frequent mistakes.
5. Provide a short check-for-understanding practice question or next step where appropriate.
6. Support a broad spectrum of academic subjects: Python, Java, C, C++, JavaScript, Go, Rust, Data Structures & Algorithms, DBMS & SQL, Operating Systems, Computer Networks, Machine Learning & AI, Mathematics, Quantitative Aptitude, Logical Reasoning, and General Education.
7. Maintain an encouraging, precise, and supportive educational tone."""


def get_level_instruction(level='beginner'):
    """Generate level-tailored pedagogical guidance for the system prompt."""
    lvl = (level or 'beginner').lower().strip()
    if lvl == 'intermediate':
        return (
            "Target Depth: Intermediate. Include standard technical terminology, best practices, "
            "edge cases, practical real-world usage, and algorithmic complexity (Big-O time and space) notes."
        )
    elif lvl == 'advanced':
        return (
            "Target Depth: Advanced. Provide in-depth architectural breakdown, internal runtime mechanics, "
            "memory layout/concurrency/distributed trade-offs, optimization strategies, and rigorous edge cases."
        )
    else:  # beginner
        return (
            "Target Depth: Beginner. Use clear everyday analogies, simple language, and avoid unexplained jargon. "
            "Explain code and concepts step-by-step from fundamental principles."
        )


def check_ollama_health(base_url=None, model=None, timeout=2.5):
    """
    Check if local Ollama daemon is reachable and whether the target model is installed.
    Returns (is_available: bool, model_name: str, message: str).
    """
    base_url = (base_url or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')).rstrip('/')
    target_model = model or os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')

    tags_url = f"{base_url}/api/tags"
    try:
        resp = requests.get(tags_url, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            models_installed = [m.get('name', '') for m in data.get('models', [])]

            # Match exact name (e.g., 'llama3.2:3b') or tag prefix
            matched_model = None
            for m in models_installed:
                if m == target_model or m.startswith(f"{target_model}:") or target_model.startswith(f"{m}:"):
                    matched_model = m
                    break
                if m.split(':')[0] == target_model.split(':')[0]:
                    matched_model = m
                    break

            if matched_model:
                return True, matched_model, f"Ollama is online with model '{matched_model}'."
            elif models_installed:
                # Use first available model if target not matched
                return True, models_installed[0], f"Ollama is online with alternative model '{models_installed[0]}'."
            else:
                return False, target_model, "Ollama is running, but no models are installed."
        return False, target_model, f"Ollama returned HTTP status {resp.status_code}."
    except requests.exceptions.Timeout:
        return False, target_model, f"Connection to Ollama at {base_url} timed out."
    except requests.exceptions.ConnectionError:
        return False, target_model, f"Could not connect to Ollama at {base_url}."
    except Exception as e:
        return False, target_model, f"Ollama health check error: {str(e)}"


DEFAULT_OLLAMA_TIMEOUT = 120


def get_configured_ollama_timeout():
    """
    Retrieve configured Ollama timeout in seconds.
    Priority: Flask current_app config['OLLAMA_TIMEOUT'] -> os.environ['OLLAMA_TIMEOUT'] -> 120.
    """
    try:
        from flask import current_app, has_app_context
        if has_app_context() and current_app and 'OLLAMA_TIMEOUT' in current_app.config:
            val = current_app.config.get('OLLAMA_TIMEOUT')
            if val is not None:
                return int(val)
    except Exception:
        pass
    env_val = os.environ.get('OLLAMA_TIMEOUT')
    if env_val is not None and str(env_val).strip():
        try:
            return int(env_val)
        except ValueError:
            pass
    return DEFAULT_OLLAMA_TIMEOUT


def call_ollama(base_url, model, user_query, level='beginner', history=None, timeout=None):
    """
    Call Ollama native chat endpoint: POST http://localhost:11434/api/chat
    Payload schema:
    {
        "model": "llama3.2:3b",
        "stream": false,
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "options": { "temperature": 0.7 }
    }
    Response schema: data["message"]["content"]
    """
    base_url = (base_url or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')).rstrip('/')
    model_name = model or os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
    if timeout is None:
        timeout = get_configured_ollama_timeout()

    endpoint = f"{base_url}/api/chat"
    level_instruction = get_level_instruction(level)
    full_system = f"{SYSTEM_PROMPT}\n\n{level_instruction}"

    messages = [{'role': 'system', 'content': full_system}]

    # Append recent conversation turns
    if history:
        for msg in history[-8:]:
            sender = msg.get('sender', '')
            role = 'user' if sender == 'user' else 'assistant'
            text = (msg.get('text') or msg.get('content') or '').strip()
            if text:
                # Strip out previous UI telemetry badges from assistant turns
                clean_text = re.sub(r'\*⚡ Answered by Live AI.*?\*', '', text).strip()
                if clean_text:
                    messages.append({'role': role, 'content': clean_text})

    messages.append({'role': 'user', 'content': user_query})

    payload = {
        'model': model_name,
        'stream': False,
        'messages': messages,
        'options': {
            'temperature': 0.7
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            message_obj = data.get('message', {})
            content = message_obj.get('content', '')
            if content and content.strip():
                return content.strip()
        return None
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException):
        return None
    except Exception:
        return None


def call_gemini(api_key, user_query, level='beginner', history=None):
    """Call Google Gemini REST API."""
    model = os.environ.get('AI_MODEL', 'gemini-1.5-flash')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    level_instruction = get_level_instruction(level)

    contents = []
    if history:
        for msg in history[-6:]:
            role = 'user' if msg.get('sender') == 'user' else 'model'
            text = (msg.get('text') or msg.get('content') or '').strip()
            if text:
                contents.append({'role': role, 'parts': [{'text': text}]})

    full_query = f"{level_instruction}\n\nStudent Question:\n{user_query}"
    contents.append({'role': 'user', 'parts': [{'text': full_query}]})

    payload = {
        'contents': contents,
        'systemInstruction': {
            'parts': [{'text': SYSTEM_PROMPT}]
        },
        'generationConfig': {
            'temperature': 0.7,
            'maxOutputTokens': 1500
        }
    }

    try:
        resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get('candidates', [])
            if candidates and 'content' in candidates[0]:
                parts = candidates[0]['content'].get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text'].strip()
    except Exception:
        pass
    return None


def call_openai_compatible(api_key, user_query, level='beginner', history=None):
    """Call OpenAI or OpenAI-compatible endpoint (Groq, OpenRouter, vLLM)."""
    base_url = os.environ.get('AI_API_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    model = os.environ.get('AI_MODEL', 'gpt-4o-mini')
    url = f"{base_url}/chat/completions"

    level_instruction = get_level_instruction(level)
    messages = [{'role': 'system', 'content': f"{SYSTEM_PROMPT}\n\n{level_instruction}"}]

    if history:
        for msg in history[-6:]:
            role = 'user' if msg.get('sender') == 'user' else 'assistant'
            text = (msg.get('text') or msg.get('content') or '').strip()
            if text:
                messages.append({'role': role, 'content': text})

    messages.append({'role': 'user', 'content': user_query})

    payload = {
        'model': model,
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 1500
    }

    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json'
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get('choices', [])
            if choices and 'message' in choices[0]:
                return choices[0]['message'].get('content', '').strip()
    except Exception:
        pass
    return None


def get_active_provider():
    """
    Detect configured LLM provider and available models/keys.
    Checks Flask current_app config when inside request context, otherwise os.environ.
    Returns (provider_name, model_or_key).
    """
    provider_pref = 'ollama'
    base_url = 'http://localhost:11434'
    model = 'llama3.2:3b'
    gemini_key = None
    openai_key = None

    try:
        from flask import current_app, has_app_context
        if has_app_context() and current_app:
            provider_pref = current_app.config.get('AI_PROVIDER') or os.environ.get('AI_PROVIDER', 'ollama')
            base_url = current_app.config.get('OLLAMA_BASE_URL') or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            model = current_app.config.get('OLLAMA_MODEL') or os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
            gemini_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
            openai_key = current_app.config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY') or os.environ.get('AI_API_KEY')
        else:
            provider_pref = os.environ.get('AI_PROVIDER', 'ollama')
            base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
            gemini_key = os.environ.get('GEMINI_API_KEY')
            openai_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('AI_API_KEY')
    except Exception:
        provider_pref = os.environ.get('AI_PROVIDER', 'ollama')
        base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
        gemini_key = os.environ.get('GEMINI_API_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('AI_API_KEY')

    provider_pref = (provider_pref or 'ollama').lower().strip()

    if provider_pref == 'offline':
        return 'offline', None

    if provider_pref in ('ollama', 'local', 'auto'):
        is_up, found_model, _ = check_ollama_health(base_url, model, timeout=2.5)
        if is_up:
            return 'ollama', found_model
        elif provider_pref == 'ollama':
            return 'ollama_offline', None

    if provider_pref in ('gemini', 'auto') and gemini_key:
        return 'gemini', gemini_key

    if provider_pref in ('openai', 'groq', 'openrouter', 'auto') and openai_key:
        return 'openai', openai_key

    return 'offline', None


def get_provider_status():
    """
    Returns full status dictionary suitable for API responses and frontend badges.
    """
    provider, key_or_model = get_active_provider()
    base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')

    if provider == 'ollama':
        return {
            'is_live': True,
            'provider': 'ollama',
            'model': key_or_model,
            'status_badge': f"Live AI: Ollama ({key_or_model})",
            'endpoint': f"{base_url}/api/chat",
            'message': f"Connected to local Ollama with model '{key_or_model}'."
        }
    elif provider == 'ollama_offline':
        return {
            'is_live': False,
            'provider': 'ollama',
            'model': model,
            'status_badge': "Offline: Ollama Unavailable",
            'endpoint': f"{base_url}/api/chat",
            'message': f"Ollama daemon is not reachable at {base_url}. Start Ollama with 'ollama serve'."
        }
    elif provider in ('gemini', 'openai'):
        display = 'Google Gemini' if provider == 'gemini' else 'OpenAI'
        return {
            'is_live': True,
            'provider': provider,
            'model': os.environ.get('AI_MODEL', 'default'),
            'status_badge': f"Live AI: {display}",
            'endpoint': 'cloud',
            'message': f"Connected to {display}."
        }
    else:
        return {
            'is_live': False,
            'provider': 'offline',
            'model': 'local-knowledge-engine',
            'status_badge': "Online: Local Knowledge Engine",
            'endpoint': 'local',
            'message': "Operating with built-in educational knowledge engine."
        }


def get_llm_response(user_query, level='beginner', history=None):
    """
    Attempts to get a response from configured LLM provider.
    Returns (response_text, provider_display_name, is_live_llm).
    If provider is offline or errors occur, returns (None, reason, False).
    """
    provider, key_or_model = get_active_provider()
    if provider == 'offline' or not key_or_model:
        return None, 'offline_knowledge_engine', False

    base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    timeout = get_configured_ollama_timeout()

    try:
        if provider == 'ollama':
            ans = call_ollama(base_url, key_or_model, user_query, level=level, history=history, timeout=timeout)
            if ans:
                return ans, f"Ollama ({key_or_model})", True
            return None, 'ollama_error', False
        elif provider == 'gemini':
            ans = call_gemini(key_or_model, user_query, level=level, history=history)
            if ans:
                return ans, 'Google Gemini', True
        elif provider == 'openai':
            ans = call_openai_compatible(key_or_model, user_query, level=level, history=history)
            if ans:
                return ans, 'OpenAI Compatible', True
    except Exception:
        pass

    return None, 'offline_knowledge_engine', False
