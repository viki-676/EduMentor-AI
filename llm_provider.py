"""LLM provider integration for EduMentor AI.
Supports Google Gemini, OpenAI-compatible APIs, and local Ollama.
"""
import os
import requests

SYSTEM_PROMPT = """You are EduMentor AI, a patient, encouraging, knowledgeable educational mentor and software engineer.
Help college students, software engineers, and competitive-exam aspirants understand concepts.
Answer the user's actual question directly. Use simple language for beginners, clear Markdown headings and lists,
and code fences for code. Give accurate examples and step-by-step explanations when useful. If you are unsure,
say so instead of inventing facts. Support a broad range of academic, programming, general knowledge, and reasoning topics."""


def get_active_provider():
    """Choose a configured hosted provider, or local Ollama by default."""
    provider_pref = os.environ.get('AI_PROVIDER', 'auto').strip().lower()
    gemini_key = os.environ.get('GEMINI_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('AI_API_KEY')

    if provider_pref == 'offline':
        return 'offline', None
    if provider_pref == 'ollama':
        return 'ollama', None
    if provider_pref == 'gemini' and gemini_key:
        return 'gemini', gemini_key
    if provider_pref in ('openai', 'groq', 'openrouter') and openai_key:
        return 'openai', openai_key
    if provider_pref == 'auto':
        if gemini_key:
            return 'gemini', gemini_key
        if openai_key:
            return 'openai', openai_key
        return 'ollama', None
    # Unknown/misconfigured preference: try the local model rather than silently going offline.
    return 'ollama', None


def _level_instruction(level):
    level = (level or 'beginner').lower()
    if level == 'beginner':
        detail = 'Use simple language, everyday analogies, and avoid unexplained jargon.'
    elif level == 'intermediate':
        detail = 'Use standard technical terminology, best practices, and complexity notes.'
    else:
        detail = 'Give a detailed technical explanation, edge cases, and relevant trade-offs.'
    return f'Target learning level: {level.capitalize()}. {detail}'


def call_gemini(api_key, user_query, level='beginner', history=None):
    model = os.environ.get('AI_MODEL', 'gemini-2.5-flash')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    contents = []
    for msg in (history or [])[-6:]:
        text = str(msg.get('text', '')).strip()
        if text:
            contents.append({'role': 'user' if msg.get('sender') == 'user' else 'model', 'parts': [{'text': text}]})
    contents.append({'role': 'user', 'parts': [{'text': f"{_level_instruction(level)}\n\nStudent question:\n{user_query}"}]})
    payload = {'contents': contents, 'systemInstruction': {'parts': [{'text': SYSTEM_PROMPT}]}, 'generationConfig': {'temperature': 0.5, 'maxOutputTokens': 1500}}
    resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=45)
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get('candidates', [])
    if candidates:
        parts = candidates[0].get('content', {}).get('parts', [])
        return '\n'.join(p.get('text', '') for p in parts if p.get('text')).strip() or None
    return None


def call_openai_compatible(api_key, user_query, level='beginner', history=None):
    base_url = os.environ.get('AI_API_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    model = os.environ.get('AI_MODEL', 'gpt-4o-mini')
    messages = [{'role': 'system', 'content': f'{SYSTEM_PROMPT}\n{_level_instruction(level)}'}]
    for msg in (history or [])[-6:]:
        text = str(msg.get('text', '')).strip()
        if text:
            messages.append({'role': 'user' if msg.get('sender') == 'user' else 'assistant', 'content': text})
    messages.append({'role': 'user', 'content': user_query})
    resp = requests.post(f'{base_url}/chat/completions', json={'model': model, 'messages': messages, 'temperature': 0.5, 'max_tokens': 1500}, headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}, timeout=45)
    resp.raise_for_status()
    choices = resp.json().get('choices', [])
    return choices[0].get('message', {}).get('content', '').strip() if choices else None


def call_ollama(user_query, level='beginner', history=None):
    """Call the local Ollama chat API; no API key is required."""
    base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
    model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
    messages = [{'role': 'system', 'content': f'{SYSTEM_PROMPT}\n{_level_instruction(level)}'}]
    for msg in (history or [])[-6:]:
        content = str(msg.get('text', '')).strip()
        if content:
            messages.append({'role': 'user' if msg.get('sender') == 'user' else 'assistant', 'content': content})
    messages.append({'role': 'user', 'content': user_query})
    resp = requests.post(f'{base_url}/api/chat', json={'model': model, 'messages': messages, 'stream': False, 'options': {'temperature': 0.5, 'num_predict': 1500}}, timeout=(5, 180))
    resp.raise_for_status()
    return resp.json().get('message', {}).get('content', '').strip() or None


def get_llm_response(user_query, level='beginner', history=None):
    """Return (answer, provider label, is_live_llm)."""
    provider, key = get_active_provider()
    try:
        if provider == 'gemini' and key:
            answer = call_gemini(key, user_query, level, history)
            if answer:
                return answer, 'Google Gemini', True
        elif provider == 'openai' and key:
            answer = call_openai_compatible(key, user_query, level, history)
            if answer:
                return answer, 'OpenAI Compatible', True
        elif provider == 'ollama':
            answer = call_ollama(user_query, level, history)
            if answer:
                return answer, 'Ollama (Local)', True
    except requests.RequestException:
        # Keep the existing offline fallback available if the local model/server is unavailable.
        pass
    except (ValueError, KeyError, TypeError):
        pass
    return None, 'offline_knowledge_engine', False
