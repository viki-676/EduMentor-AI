from services.ai_mentor import get_mentor_response

def test_ai_mentor_python_lookup():
    response = get_mentor_response(user_id=None, query_text="Explain Python mutability and dictionaries")
    assert "Python Programming" in response
    assert "def " in response or "Lists are mutable" in response or "dict" in response
    assert "System.out.println" not in response

def test_ai_mentor_java_routing():
    """Verify asking about Java returns Java syntax and NOT Python code."""
    response = get_mentor_response(user_id=None, query_text="Explain Java syntax and main method")
    assert "Java" in response
    assert "public static void main" in response or "System.out.println" in response
    assert "```java" in response
    assert "def main():" not in response

def test_ai_mentor_java_oop():
    """Verify asking about Java OOP returns Java class/extends syntax."""
    response = get_mentor_response(user_id=None, query_text="How does Java OOP inheritance work?")
    assert "Java" in response
    assert "```java" in response
    assert "extends" in response or "implements" in response

def test_ai_mentor_dbms_lookup():
    response = get_mentor_response(user_id=None, query_text="What are ACID properties in database?")
    assert "Database Management Systems" in response
    assert "Atomicity" in response

def test_ai_mentor_current_affairs_prime_minister():
    """Verify answering current affairs about PM of India with official source citation."""
    response = get_mentor_response(user_id=None, query_text="Who is the current Prime Minister of India?")
    assert "Narendra Modi" in response
    assert "https://www.pmindia.gov.in/en/" in response
    assert "Official Source" in response or "Source:" in response

def test_ai_mentor_ambiguous_query_prompts_clarification():
    """Verify generic query prompts clarification rather than guessing wrong language."""
    response = get_mentor_response(user_id=None, query_text="Explain loops and syntax")
    assert "Clarification" in response or "Java" in response or "Python" in response

def test_ai_mentor_unsupported_topic_honest_fallback():
    """Verify unsupported topic admits boundaries instead of random fallback."""
    response = get_mentor_response(user_id=None, query_text="Explain advanced quantum topological quantum field theory")
    assert "offline knowledge base" in response or "EduMentor AI Assistant" in response
    assert "def " not in response


def test_ai_mentor_chat_api(auth_client):
    res = auth_client.post('/api/mentor/chat', json={
        'message': 'Explain Time and Work shortcuts'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'response' in data
    assert len(data['response']) > 20

def test_ai_mentor_chat_api_empty_message(auth_client):
    res = auth_client.post('/api/mentor/chat', json={
        'message': '   '
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "Please enter a question" in data['response']


def test_ai_mentor_python_lists_with_example(auth_client):
    """Regression test: verify 'Explain Python lists with an example' returns dedicated list operations and code."""
    res = auth_client.post('/api/mentor/chat', json={
        'message': 'Explain Python lists with an example',
        'level': 'beginner'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'response' in data
    response_text = data['response']
    assert len(response_text) > 100
    assert 'Python Lists' in response_text
    assert 'append' in response_text or 'fruits' in response_text
    assert '```python' in response_text


def test_ai_mentor_view_includes_mentor_script(auth_client):
    """Regression test: ensure /mentor view includes the mentor.js script so chat submits via fetch."""
    res = auth_client.get('/mentor')
    assert res.status_code == 200
    assert b'mentor.js' in res.data
    assert b'mentorChatForm' in res.data
    assert b'mentorChatInput' in res.data


def test_ai_mentor_dbms_normalization(auth_client):
    """Verify asking about normalization returns 1NF 2NF 3NF and SQL schema."""
    res = auth_client.post('/api/mentor/chat', json={
        'message': 'Explain database normalization 1NF 2NF 3NF with schema'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'Normalization' in data['response']
    assert '1NF' in data['response']
    assert '```sql' in data['response']


def test_ai_mentor_chat_api_unauthenticated(client):
    """Verify unauthenticated API calls receive 401 JSON instead of HTML redirect."""
    res = client.post('/api/mentor/chat', json={
        'message': 'Hello mentor'
    })
    assert res.status_code == 401
    data = res.get_json()
    assert 'Authentication required' in data['error']


def test_ai_mentor_greetings():
    """Verify greetings receive friendly responses instead of unsupported topic notices."""
    res_hi = get_mentor_response(user_id=None, query_text="hi")
    assert "Hi! I'm your EduMentor AI assistant. What would you like to learn today?" in res_hi
    assert "offline knowledge base" not in res_hi

    res_hello = get_mentor_response(user_id=None, query_text="hello")
    assert "Hello! I can help you with programming, DBMS, AI/ML, and exam preparation." in res_hello
    assert "offline knowledge base" not in res_hello

    res_thanks = get_mentor_response(user_id=None, query_text="thanks")
    assert "You're welcome! What would you like to explore next?" in res_thanks
    assert "offline knowledge base" not in res_thanks

    res_thank_you = get_mentor_response(user_id=None, query_text="Thank you!")
    assert "You're welcome! What would you like to explore next?" in res_thank_you


def test_ai_mentor_chat_api_greetings(auth_client):
    """Verify conversational greetings through the JSON API endpoint."""
    res = auth_client.post('/api/mentor/chat', json={'message': 'hi'})
    assert res.status_code == 200
    data = res.get_json()
    assert "Hi! I'm your EduMentor AI assistant" in data['response']

    res2 = auth_client.post('/api/mentor/chat', json={'message': 'hello'})
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert "Hello! I can help you with programming" in data2['response']


def test_ai_mentor_greeting_with_educational_question():
    """Verify educational questions starting with a greeting are routed to educational knowledge base."""
    res = get_mentor_response(user_id=None, query_text="hi, explain python lists with an example")
    assert "Python Lists" in res
    assert "```python" in res

def test_ai_mentor_status_indicator_online(auth_client):
    """Verify that the AI Mentor page and sidebar display Online status when local mentor is active."""
    res = auth_client.get('/mentor')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Online' in html
    # Ensure it does not present itself as disconnected/offline
    assert '<span class="badge bg-info-subtle text-info small border border-info" style="font-size: 0.65rem;">Offline</span>' not in html

def test_ai_mentor_autoscroll_script_behavior(auth_client):
    """Verify mentor.js implements auto-scroll logic, preserving user scroll when reading older messages."""
    res = auth_client.get('/static/js/mentor.js')
    assert res.status_code == 200
    js_code = res.data.decode('utf-8')

    # Core auto-scroll function and scrollHeight reference
    assert 'scrollToBottom' in js_code
    assert 'scrollHeight' in js_code
    # Preserves scroll when user scrolls up to read older messages
    assert 'userScrolledUp' in js_code
    assert 'distanceFromBottom' in js_code
    # Layout reflow accommodation for long answers with code blocks and headings
    assert 'requestAnimationFrame' in js_code
    assert 'setTimeout' in js_code
    assert 'scroll-behavior' in open('static/css/styles.css').read()

def test_ai_mentor_chat_history_switching(auth_client):
    """Verify creating two conversations (Python and DBMS), switching between them, and confirming message preservation."""
    # 1. Create Conversation A (Python)
    res_a = auth_client.post('/api/mentor/new')
    assert res_a.status_code == 200
    conv_a_id = res_a.get_json()['conversation_id']
    chat_a = auth_client.post('/api/mentor/chat', json={
        'message': 'Explain Python lists',
        'conversation_id': conv_a_id
    })
    assert chat_a.status_code == 200
    data_a = chat_a.get_json()
    assert 'Python' in data_a.get('response', '')

    # 2. Create Conversation B (DBMS)
    res_b = auth_client.post('/api/mentor/new')
    assert res_b.status_code == 200
    conv_b_id = res_b.get_json()['conversation_id']
    chat_b = auth_client.post('/api/mentor/chat', json={
        'message': 'Explain DBMS normalization',
        'conversation_id': conv_b_id
    })
    assert chat_b.status_code == 200
    data_b = chat_b.get_json()
    assert 'Normalization' in data_b.get('response', '')

    # 3. Select Conversation A and verify Python response appears
    page_a = auth_client.get(f'/mentor?c={conv_a_id}')
    assert page_a.status_code == 200
    html_a = page_a.data.decode('utf-8')
    cw_start_a = html_a.find('mentorChatWindow')
    cw_content_a = html_a[cw_start_a:cw_start_a+3000]
    assert 'Explain Python lists' in cw_content_a
    assert 'Python Lists' in cw_content_a
    assert '1NF' not in cw_content_a

    # 4. Select Conversation B and verify DBMS response appears
    page_b = auth_client.get(f'/mentor?c={conv_b_id}')
    assert page_b.status_code == 200
    html_b = page_b.data.decode('utf-8')
    cw_start_b = html_b.find('mentorChatWindow')
    cw_content_b = html_b[cw_start_b:cw_start_b+3000]
    assert 'Explain DBMS normalization' in cw_content_b
    assert 'Normalization' in cw_content_b
    assert 'fruits' not in cw_content_b

    # 5. Switch back to Conversation A and confirm messages are preserved
    page_a_again = auth_client.get(f'/mentor?c={conv_a_id}')
    assert page_a_again.status_code == 200
    html_a_again = page_a_again.data.decode('utf-8')
    cw_start_a2 = html_a_again.find('mentorChatWindow')
    cw_content_a2 = html_a_again[cw_start_a2:cw_start_a2+3000]
    assert 'Explain Python lists' in cw_content_a2
    assert 'Python Lists' in cw_content_a2


import unittest.mock as mock
import requests
import pytest
from services.llm_provider import (
    call_ollama, check_ollama_health, get_provider_status,
    get_level_instruction, DEFAULT_OLLAMA_TIMEOUT, get_configured_ollama_timeout,
    get_llm_response
)


def test_ollama_chat_payload_and_response_parsing():
    """Verify call_ollama formats POST payload to /api/chat and parses data['message']['content']."""
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'model': 'llama3.2:3b',
        'message': {
            'role': 'assistant',
            'content': 'A binary search tree is a node-based data structure where the left subtree contains keys smaller than the node.'
        }
    }

    history = [
        {'sender': 'user', 'text': 'What is a tree?'},
        {'sender': 'mentor', 'text': 'A tree is a hierarchical data structure.'}
    ]

    with mock.patch('requests.post', return_value=mock_response) as mock_post:
        result = call_ollama(
            base_url='http://localhost:11434',
            model='llama3.2:3b',
            user_query='Explain BST properties',
            level='intermediate',
            history=history,
            timeout=10
        )

        assert result is not None
        assert 'binary search tree' in result
        mock_post.assert_called_once()
        url = mock_post.call_args[0][0]
        assert url == 'http://localhost:11434/api/chat'

        kwargs = mock_post.call_args[1]
        payload = kwargs['json']
        assert payload['model'] == 'llama3.2:3b'
        assert payload['stream'] is False
        assert len(payload['messages']) == 4  # system + user1 + assistant1 + user2
        assert payload['messages'][0]['role'] == 'system'
        assert 'Intermediate' in payload['messages'][0]['content']
        assert payload['messages'][1]['role'] == 'user'
        assert payload['messages'][1]['content'] == 'What is a tree?'
        assert payload['messages'][2]['role'] == 'assistant'
        assert payload['messages'][2]['content'] == 'A tree is a hierarchical data structure.'
        assert payload['messages'][3]['role'] == 'user'
        assert payload['messages'][3]['content'] == 'Explain BST properties'


def test_ollama_level_instructions():
    """Verify beginner, intermediate, and advanced levels inject appropriate instructions."""
    beginner_text = get_level_instruction('beginner')
    interm_text = get_level_instruction('intermediate')
    adv_text = get_level_instruction('advanced')

    assert 'Beginner' in beginner_text
    assert 'analogies' in beginner_text.lower()
    assert 'Intermediate' in interm_text
    assert 'complexity' in interm_text.lower()
    assert 'Advanced' in adv_text
    assert 'architectural' in adv_text.lower() or 'internals' in adv_text.lower()


def test_ollama_health_check_success():
    """Verify check_ollama_health returns True when target model is present."""
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        'models': [
            {'name': 'llama3.2:3b', 'size': 2019393189},
            {'name': 'mistral:latest', 'size': 4109865159}
        ]
    }
    with mock.patch('requests.get', return_value=mock_resp):
        is_up, model, msg = check_ollama_health('http://localhost:11434', 'llama3.2:3b')
        assert is_up is True
        assert model == 'llama3.2:3b'
        assert 'online' in msg.lower()


def test_ollama_health_check_unreachable():
    """Verify check_ollama_health handles ConnectionError gracefully without crashing."""
    with mock.patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection refused")):
        is_up, model, msg = check_ollama_health('http://localhost:11434', 'llama3.2:3b')
        assert is_up is False
        assert 'could not connect' in msg.lower()


def test_ollama_timeout_handling():
    """Verify call_ollama returns None gracefully upon network timeout."""
    with mock.patch('requests.post', side_effect=requests.exceptions.Timeout("Read timed out")):
        res = call_ollama('http://localhost:11434', 'llama3.2:3b', 'Deep learning question', timeout=1)
        assert res is None


def test_ai_mentor_status_endpoint(auth_client):
    """Verify /api/mentor/status returns accurate provider metadata."""
    res = auth_client.get('/api/mentor/status')
    assert res.status_code == 200
    data = res.get_json()
    assert 'provider' in data
    assert 'status_badge' in data
    assert 'is_live' in data


def test_live_ollama_query_generation():
    """Live integration test: Call running local Ollama model llama3.2:3b to confirm genuine answer generation."""
    is_up, model, _ = check_ollama_health('http://localhost:11434', 'llama3.2:3b', timeout=2)
    if not is_up:
        pytest.skip("Local Ollama daemon is not running on localhost:11434")

    response = call_ollama(
        base_url='http://localhost:11434',
        model='llama3.2:3b',
        user_query='What is a queue in data structures? Answer in one short sentence.',
        level='beginner',
        timeout=30
    )
    assert response is not None
    assert len(response) > 10
    assert 'queue' in response.lower() or 'fifo' in response.lower() or 'first-in' in response.lower()


def test_ollama_timeout_configuration():
    """Verify DEFAULT_OLLAMA_TIMEOUT is 120 and custom OLLAMA_TIMEOUT is honored."""
    import os
    assert DEFAULT_OLLAMA_TIMEOUT == 120

    # Test honoring explicit env var
    old_env = os.environ.get('OLLAMA_TIMEOUT')
    try:
        os.environ['OLLAMA_TIMEOUT'] = '45'
        assert get_configured_ollama_timeout() == 45

        # Test fallback to 120 when env var is cleared
        del os.environ['OLLAMA_TIMEOUT']
        assert get_configured_ollama_timeout() == 120
    finally:
        if old_env is not None:
            os.environ['OLLAMA_TIMEOUT'] = old_env
        else:
            os.environ.pop('OLLAMA_TIMEOUT', None)

    # Verify call_ollama uses get_configured_ollama_timeout when timeout=None
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        'message': {'role': 'assistant', 'content': 'Test response'}
    }
    with mock.patch('requests.post', return_value=mock_resp) as mock_post:
        call_ollama('http://localhost:11434', 'llama3.2:3b', 'Test query', timeout=None)
        assert mock_post.call_args[1]['timeout'] == get_configured_ollama_timeout()


def test_specific_python_question_honest_fallback_when_llm_unavailable():
    """Verify specific unmapped Python question does NOT return generic Python fundamentals."""
    query = "Explain the difference between Python setdefault() and defaultdict. Use the word mango and the number 47 in a working code example, and show the output."

    # When LLM is offline or errored
    with mock.patch('services.ai_mentor.get_llm_response', return_value=(None, 'offline_knowledge_engine', False)):
        response = get_mentor_response(user_id=None, query_text=query)

        # Must NOT return general Python fundamentals
        assert "Python Programming Fundamentals" not in response
        # Must NOT return basic dictionary lesson
        assert "student = {" not in response
        # Must NOT ask which programming language
        assert "Which programming language would you like this explained in?" not in response
        # Must return honest fallback message
        assert ("offline knowledge base" in response or "EduMentor AI Assistant Notice" in response or "AI Mentor Notice" in response)

    # When Ollama had a response timeout
    with mock.patch('services.ai_mentor.get_llm_response', return_value=(None, 'ollama_error', False)):
        response = get_mentor_response(user_id=None, query_text=query)
        assert "Python Programming Fundamentals" not in response
        assert "Model Response Timeout" in response or "timeout window" in response


def test_relevant_offline_answers_preserved():
    """Verify syllabus questions genuinely covered by the offline knowledge base are preserved."""
    with mock.patch('services.ai_mentor.get_llm_response', return_value=(None, 'offline_knowledge_engine', False)):
        # 1. Lists
        resp_list = get_mentor_response(user_id=None, query_text="Explain Python lists with an example")
        assert "Python Lists" in resp_list
        assert "fruits.append" in resp_list or "fruits" in resp_list
        assert "```python" in resp_list

        # 2. Dictionaries
        resp_dict = get_mentor_response(user_id=None, query_text="Explain Python dictionaries")
        assert "Dictionaries & Hash Maps" in resp_dict
        assert "student = {" in resp_dict
        assert "```python" in resp_dict

        # 3. What is Python / General
        resp_gen = get_mentor_response(user_id=None, query_text="What is Python?")
        assert "Python Programming Fundamentals" in resp_gen
        assert "dynamically typed" in resp_gen

        # 4. Functions
        resp_fn = get_mentor_response(user_id=None, query_text="Explain Python functions")
        assert "Functions & Return Values" in resp_fn
        assert "def calculate_grade" in resp_fn

        # 5. Loops
        resp_loop = get_mentor_response(user_id=None, query_text="Explain Python loops")
        assert "Loops & Comprehensions" in resp_loop
        assert "even_squares" in resp_loop

        # 6. OOP
        resp_oop = get_mentor_response(user_id=None, query_text="Explain Python OOP")
        assert "Object-Oriented Programming in Python" in resp_oop
        assert "class Student" in resp_oop


def test_successful_ollama_response_mocked():
    """Verify get_mentor_response formats successful Ollama answer with telemetry badge."""
    mock_llm_text = (
        "### `setdefault()` vs `defaultdict` in Python\n\n"
        "**`setdefault()`** is a method on standard Python dicts.\n"
        "**`defaultdict`** is a class from the `collections` module.\n\n"
        "```python\nfrom collections import defaultdict\n"
        "basket = defaultdict(int)\nbasket['mango'] += 47\nprint(basket['mango'])\n```"
    )
    with mock.patch('services.ai_mentor.get_llm_response', return_value=(mock_llm_text, "Ollama (llama3.2:3b)", True)):
        resp = get_mentor_response(
            user_id=None,
            query_text="Explain the difference between Python setdefault() and defaultdict."
        )
        assert "setdefault()" in resp
        assert "defaultdict" in resp
        assert "mango" in resp
        assert "47" in resp
        assert "Answered by Live AI (Ollama (llama3.2:3b))" in resp


def test_live_ollama_setdefault_defaultdict():
    """Live integration test: Query local Ollama llama3.2:3b for setdefault vs defaultdict with mango and 47."""
    is_up, model, _ = check_ollama_health('http://localhost:11434', 'llama3.2:3b', timeout=2)
    if not is_up:
        pytest.skip("Local Ollama daemon is not running on localhost:11434")

    prompt = "Explain the difference between Python setdefault() and defaultdict. Use the word mango and the number 47 in a working code example, and show the output."
    response = call_ollama(
        base_url='http://localhost:11434',
        model='llama3.2:3b',
        user_query=prompt,
        level='intermediate',
        timeout=120
    )
    assert response is not None
    assert len(response) > 50
    assert ('setdefault' in response.lower() or 'defaultdict' in response.lower())
    assert ('mango' in response.lower() or '47' in response or 'python' in response.lower())






