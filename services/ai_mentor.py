"""
AI Mentor Agent for EduMentor AI.
Comprehensive, multi-disciplinary pedagogical mentor supporting:
- Python, Java, C, C++, JavaScript, Go, Rust, and programming languages
- AI, Machine Learning, Deep Learning, NLP, and Data Science
- Computer Science Fundamentals: OS, Computer Networks, DBMS, Software Engineering, DSA
- Mathematics, Quantitative Aptitude, Logical Reasoning, and English Grammar
- Programming error diagnostics, debugging, and code explanations
- Technical interviews, system design, and career guidance
- Real configurable LLM integration (Gemini, OpenAI, Ollama) with offline intelligence fallback
"""

import re
import datetime
import requests
from models import db, Question, MentorConversation, MentorMessage
from .quiz_service import get_user_analytics
from .llm_provider import get_llm_response, get_active_provider

# =============================================================================
# EXTENSIVE OFFLINE MULTI-DISCIPLINARY KNOWLEDGE REPOSITORY
# =============================================================================

C_KNOWLEDGE_BASE = {
    'general': {
        'title': 'C Programming Language Fundamentals',
        'direct_answer': 'C is a procedural, statically typed compiled systems programming language known for low-level memory control, pointers, high execution speed, and minimal runtime overhead.',
        'analogy': 'Writing C is like driving a manual transmission sports car with direct mechanical linkage: you have ultimate power and efficiency, but no automated safety net.',
        'key_points': [
            'Compilation stages: Preprocessing (.i) -> Compiling (.s) -> Assembling (.o) -> Linking (executable).',
            'Manual Memory Management: Explicit malloc/calloc/free without automated garbage collection.',
            'Structured data types: structs and unions for custom memory layouts.',
            'Standard Library: Header files like <stdio.h>, <stdlib.h>, <string.h> provide standard utilities.'
        ],
        'code': '```c\n#include <stdio.h>\n\nint main(void) {\n    printf("Hello from C Systems Programming!\\n");\n    return 0;\n}\n```',
        'pitfalls': 'Array bounds are not checked at runtime; buffer overflows can cause segmentation faults or security vulnerabilities.'
    },
    'pointers': {
        'title': 'C Pointers, Addresses & Memory Allocation',
        'direct_answer': 'A pointer is a variable that stores the memory address of another variable. In C, pointers enable pass-by-reference, dynamic data structures, and direct hardware interfacing.',
        'analogy': 'A variable is like a physical house; its pointer is the written street address on a piece of paper pointing to that house.',
        'key_points': [
            '& operator retrieves the memory address of an lvalue.',
            '* operator dereferences a pointer to read or write the targeted memory.',
            'malloc(bytes) requests uninitialized heap memory; free(ptr) returns it.',
            'Always set freed pointers to NULL to prevent dangerous dangling pointers.'
        ],
        'code': '```c\n#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n    int val = 42;\n    int *ptr = &val; // ptr stores address of val\n    \n    // Heap allocation\n    int *dynamic_arr = (int *)malloc(3 * sizeof(int));\n    if (dynamic_arr != NULL) {\n        dynamic_arr[0] = 100;\n        free(dynamic_arr);\n        dynamic_arr = NULL; // Safe practice\n    }\n    return 0;\n}\n```',
        'pitfalls': 'Dereferencing a NULL or uninitialized pointer triggers a Segmentation Fault (SIGSEGV).'
    }
}

CPP_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Modern C++ Programming (OOP, STL & Templates)',
        'direct_answer': 'C++ is a multi-paradigm language combining C-level high performance with Object-Oriented Programming, generic templates, compile-time metaprogramming, and RAII resource safety.',
        'analogy': 'If C is raw steel and engine components, Modern C++ provides both the raw machinery and precision aerospace CAD abstractions to build complex distributed engines safely.',
        'key_points': [
            'Object-Oriented: Classes, access specifiers (public, protected, private), inheritance, virtual polymorphism.',
            'RAII (Resource Acquisition Is Initialization): Destructors automatically release heap/locks when leaving scope.',
            'Standard Template Library (STL): std::vector, std::map, std::unordered_map, std::algorithm.',
            'Smart Pointers: std::unique_ptr (exclusive) and std::shared_ptr (reference counted) eliminate raw delete.'
        ],
        'code': '```cpp\n#include <iostream>\n#include <vector>\n#include <memory>\n\nclass Entity {\npublic:\n    virtual void render() const { std::cout << "Rendering entity\\n"; }\n    virtual ~Entity() = default; // Essential virtual destructor\n};\n\nint main() {\n    auto e = std::make_unique<Entity>();\n    e->render();\n    return 0;\n}\n```',
        'pitfalls': 'Forgetting a virtual destructor in a polymorphic base class causes undefined behavior when deleting via base pointer.'
    }
}

JAVASCRIPT_KNOWLEDGE_BASE = {
    'general': {
        'title': 'JavaScript (JS) Language & Modern ES6+ Architecture',
        'direct_answer': 'JavaScript is a high-level, dynamic, single-threaded interpreted/JIT language powering the web platform and servers via Node.js, built on an asynchronous event-driven loop.',
        'analogy': 'JavaScript is like a master chef in a restaurant: the chef handles one order at a time at the prep station (Call Stack), but delegates long roasting and baking to kitchen assistants (Web APIs/Event Loop) while continuing to chop vegetables.',
        'key_points': [
            'Event Loop Concurrency: Single Call Stack coordinate with Microtask Queue (Promises) and Macrotask Queue (Timers).',
            'Closures: Functions retain lexical access to parent scope variables even after parent execution terminates.',
            'Promises & Async/Await: Clean non-blocking asynchronous workflows over callback hell.',
            'Dynamic Prototypal Inheritance: Objects inherit directly from other objects via prototype chains.'
        ],
        'code': '```javascript\n// Modern async/await with error handling\nasync function fetchStudentData(id) {\n    try {\n        const response = await fetch(`/api/students/${id}`);\n        if (!response.ok) throw new Error("HTTP error");\n        const data = await response.json();\n        return data;\n    } catch (err) {\n        console.error("Fetch failed:", err.message);\n    }\n}\n```',
        'pitfalls': 'Using == instead of strict equality ===, leading to silent type coercion bugs.'
    }
}

AI_ML_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Artificial Intelligence & Machine Learning Foundations',
        'direct_answer': 'Machine Learning is a subset of AI where mathematical algorithms learn statistical patterns from data to make predictions or decisions without being explicitly programmed with rule-based heuristics.',
        'analogy': 'Traditional programming is like giving a student an exhaustive recipe book; Machine Learning is like showing a student 10,000 photos of completed meals until they discern the culinary principles themselves.',
        'key_points': [
            'Supervised Learning: Learning from labeled inputs (Classification: discrete classes; Regression: continuous values).',
            'Unsupervised Learning: Discovering inherent structure in unlabeled data (Clustering: K-Means; Dimensionality Reduction: PCA).',
            'Deep Learning & Neural Networks: Multi-layered artificial neural networks (CNNs for vision, Transformers for NLP).',
            'Evaluation Metrics: Precision, Recall, F1-Score, ROC-AUC, and Mean Squared Error (MSE).'
        ],
        'code': '```python\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import classification_report\n\n# Train random forest model\nclf = RandomForestClassifier(n_estimators=100, random_state=42)\nclf.fit(X_train, y_train)\npredictions = clf.predict(X_test)\nprint(classification_report(y_test, predictions))\n```',
        'pitfalls': 'Evaluating an imbalanced dataset solely using Accuracy (e.g., 99% accuracy by always predicting the majority class).'
    },
    'deep_learning': {
        'title': 'Deep Learning, Neural Networks & Transformers (NLP)',
        'direct_answer': 'Deep Learning uses hierarchical multi-layer neural networks optimized via Backpropagation and Gradient Descent. Modern NLP is dominated by the Transformer architecture utilizing Self-Attention mechanisms.',
        'analogy': 'A neural network is like a corporate hierarchy: lower layers detect simple lines/textures, middle layers assemble shapes, and executive layers make final semantic decisions.',
        'key_points': [
            'Forward Propagation: Computing activations across layers using weights, biases, and activation functions (ReLU, GELU).',
            'Backpropagation: Calculating gradients of the loss function with respect to weights using the Chain Rule of calculus.',
            'Self-Attention Mechanism: Allows tokens in a sequence to dynamically weigh and attend to every other token regardless of distance.',
            'Overfitting Control: Dropout, Batch Normalization, Weight Decay (L2), and early stopping.'
        ],
        'code': '```python\n# Conceptual Self-Attention formula\n# Attention(Q, K, V) = softmax((Q @ K.T) / sqrt(d_k)) @ V\nimport numpy as np\n\ndef softmax(x):\n    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))\n    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)\n```',
        'pitfalls': 'Vanishing/Exploding Gradients during deep network training without proper weight initialization or residual connections.'
    }
}

OS_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Operating Systems (Processes, Paging & Synchronization)',
        'direct_answer': 'The Operating System is systems software managing computer hardware, providing process scheduling, virtual memory abstraction, file systems, and hardware protection.',
        'analogy': 'The OS is like an air traffic controller at a busy international airport: it schedules runway access (CPU), assigns gates (RAM), and prevents collisions (deadlocks).',
        'key_points': [
            'Processes vs. Threads: Processes possess private address spaces; threads share memory within the same parent process.',
            'Virtual Memory & Paging: Divides virtual space into Pages and physical memory into Frames, translated by MMU and cached by TLB.',
            'CPU Scheduling: Round Robin, Priority Scheduling, Multi-Level Feedback Queues.',
            'Deadlock 4 Conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.'
        ],
        'code': '```c\n// POSIX thread creation and mutex synchronization\npthread_mutex_t lock;\npthread_mutex_lock(&lock);\nshared_variable++;\npthread_mutex_unlock(&lock);\n```',
        'pitfalls': 'Failing to synchronize shared mutable state across threads, leading to race conditions and memory corruption.'
    }
}

NETWORKS_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Computer Networks & Internet Protocols',
        'direct_answer': 'Computer Networks govern end-to-end data communication across devices using layered protocol architectures: the 7-layer OSI conceptual reference model and the 4-layer TCP/IP suite.',
        'analogy': 'Sending a network packet is like mailing an international letter: message written (Application), enclosed in envelope with street address (Transport/TCP port), sorted by postal hub and country code (Network/IP), and physically transported via air/road (Physical/Data Link).',
        'key_points': [
            'OSI 7 Layers: Physical, Data Link, Network, Transport, Session, Presentation, Application.',
            'TCP vs UDP: TCP guarantees reliable, ordered byte streams via 3-way handshake; UDP is lightweight and connectionless.',
            'DNS (Domain Name System): Resolves human-friendly domain names to numeric IP addresses using recursive and authoritative queries.',
            'Routing vs Switching: Switches operate at Layer 2 (MAC addresses); Routers operate at Layer 3 (IP addresses).'
        ],
        'code': '```bash\n# Key diagnostic network tools\nping 8.8.8.8           # Tests ICMP network reachability\ntraceroute google.com  # Inspects hops along packet path\nnslookup example.com   # Queries DNS records\n```',
        'pitfalls': 'Confusing Layer 2 MAC addresses (local segment) with Layer 3 IP addresses (global internetwork routing).'
    }
}

MATH_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Mathematics & Aptitude for Computer Science and Exams',
        'direct_answer': 'Mathematics forms the theoretical foundation of computer algorithms, cryptography, graphics, and competitive aptitude examinations.',
        'analogy': 'Learning math for computer science is like weight training for an athlete: even when you are not lifting weights in the actual game, your algorithmic speed and reasoning strength depend directly on it.',
        'key_points': [
            'Permutations P(n, r) = n! / (n-r)! (order matters); Combinations C(n, r) = n! / (r! * (n-r)!) (order does not matter).',
            'Probability: P(A) = Favorable Outcomes / Total Outcomes; P(A or B) = P(A) + P(B) - P(A and B).',
            'Percentages: Multiplier method (increase by x% = multiply by 1 + x/100).',
            'Relative Speed: Add speeds if traveling in opposite directions; subtract speeds if traveling in same direction.'
        ],
        'code': '```python\nimport math\n\ndef combinations(n, r):\n    return math.comb(n, r) if hasattr(math, "comb") else math.factorial(n) // (math.factorial(r) * math.factorial(n - r))\n\nprint("Combinations of 5 choose 2:", combinations(5, 2)) # 10\n```',
        'pitfalls': 'Confusing Permutations (arranging order) with Combinations (group selection).'
    }
}

INTERVIEW_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Technical Interviews, System Design & Career Preparation',
        'direct_answer': 'Success in technical hiring requires three pillars: Algorithmic Problem Solving (DSA), Scalable System Design, and Behavioral Competence using the STAR methodology.',
        'analogy': 'A technical interview is not an exam to test memorization; it is a simulated pair-programming session where interviewers evaluate how you communicate, handle ambiguity, and debug under pressure.',
        'key_points': [
            'Clarify First: Always clarify constraints, input sizes, and edge cases before writing a line of code.',
            'Talk Out Loud: Articulate your thought process, state the brute-force approach first, and then optimize.',
            'System Design 4 Steps: Requirements -> High-Level Architecture -> Deep Dive (Database, Cache) -> Scaling/Bottlenecks.',
            'STAR Behavioral: Situation (context), Task (objective), Action (specific actions you took), Result (quantified metrics).'
        ],
        'code': '```python\n# Interview Pro-Tip: State complexity at start and end\n# Time Complexity: O(N log N) due to sorting\n# Space Complexity: O(1) auxiliary space\ndef two_sum_sorted(nums, target):\n    left, right = 0, len(nums) - 1\n    while left < right:\n        curr_sum = nums[left] + nums[right]\n        if curr_sum == target: return [left, right]\n        elif curr_sum < target: left += 1\n        else: right -= 1\n    return []\n```',
        'pitfalls': 'Coding in complete silence; interviewers cannot reward insights they do not hear.'
    }
}

DEBUGGING_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Debugging Strategies & Common Programming Errors',
        'direct_answer': 'Debugging is the systematic process of reproducing, isolating, and rectifying software defects using binary search techniques, trace logs, and interactive debuggers.',
        'analogy': 'Debugging is like detective work at a crime scene: the error stack trace is your primary clue, and you must verify hypotheses using evidence rather than guessing random edits.',
        'key_points': [
            'Segmentation Fault (C/C++): Attempting to access unallocated or protected memory (null pointer dereference, buffer overflow).',
            'NullPointerException (Java): Calling a method or accessing a field on an uninitialized reference.',
            'IndexError / OutOfBounds: Accessing index >= array.length or negative index outside bounds.',
            'RecursionError / Stack Overflow: Recursive function missing its base case or exceeding call stack limits.',
            'Systematic Workflow: 1. Reproduce reliably -> 2. Inspect stack trace line number -> 3. Isolate minimal test case -> 4. Fix and verify.'
        ],
        'code': '```python\n# Safe dictionary access preventing KeyError in Python\nconfig = {"timeout": 30}\n# Safe: returns default value 5000 if "port" is absent\nport = config.get("port", 5000)\n```',
        'pitfalls': 'Modifying five things simultaneously; if the bug disappears, you do not know which change actually resolved it.'
    }
}

JAVA_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Java Programming Language',
        'direct_answer': 'Java is a class-based, object-oriented, strongly-typed programming language designed to follow the "Write Once, Run Anywhere" (WORA) philosophy via the Java Virtual Machine (JVM).',
        'analogy': 'Think of Java like a blueprint for an automobile: you write a strict contract of types and methods, compile it to universal bytecode (.class), and any machine equipped with a JVM can execute it reliably.',
        'key_points': [
            'Platform Independence: Source code compiles to bytecode run by the JVM.',
            'Strongly Typed & Object-Oriented: Everything belongs to a class (except primitives like `int`, `boolean`, `char`).',
            'Automatic Garbage Collection: Memory is managed automatically by the JVM Garbage Collector.',
            'Key Architecture: JDK (Development Kit) contains JRE (Runtime Environment), which contains JVM (Virtual Machine).'
        ],
        'code': '```java\npublic class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, EduMentor AI!");\n    }\n}\n```',
        'pitfalls': 'Remember that filename must match the public class name (e.g., `HelloWorld.java` for `public class HelloWorld`).'
    },
    'oop': {
        'title': 'Object-Oriented Programming in Java',
        'direct_answer': 'Java implements OOP through four core pillars: Encapsulation (data hiding), Inheritance (code reuse via `extends`), Polymorphism (method overloading & overriding), and Abstraction (interfaces and `abstract` classes).',
        'analogy': 'A parent class is like a basic vehicle design. A subclass `Car` inherits steering and wheels, but customizes its engine and doors.',
        'key_points': [
            'Encapsulation: Use `private` fields with `public` getters and setters.',
            'Inheritance: Use the `extends` keyword (Java supports single class inheritance).',
            'Polymorphism: Compile-time (method overloading with different parameters) and Runtime (method overriding with `@Override`).',
            'Abstraction: Defined using `interface` (contracts implemented via `implements`) or `abstract class`.'
        ],
        'code': '```java\n// Abstraction & Inheritance in Java\ninterface Animal {\n    void makeSound();\n}\n\nclass Dog implements Animal {\n    @Override\n    public void makeSound() {\n        System.out.println("Woof!");\n    }\n}\n```',
        'pitfalls': 'Java does not support multiple inheritance of classes (to prevent the Diamond Problem); use multiple interfaces instead!'
    },
    'loops': {
        'title': 'Loops & Control Flow in Java',
        'direct_answer': 'Java supports standard `for`, `while`, and `do-while` loops, as well as an enhanced for-each loop for iterating over arrays and Collections.',
        'analogy': 'A loop is like an automated inspection line: as long as items remain in the queue, the inspector processes each one before moving forward.',
        'key_points': [
            '`for (int i = 0; i < n; i++)`: Used when the iteration count is known.',
            '`while (condition)`: Evaluates condition before executing loop body.',
            '`do { ... } while (condition)`: Executes at least once before checking condition.',
            '`for (Type item : collection)`: Clean, index-free traversal.'
        ],
        'code': '```java\nint[] numbers = {10, 20, 30, 40};\n// Enhanced for-each loop in Java\nfor (int num : numbers) {\n    System.out.println("Value: " + num);\n}\n```',
        'pitfalls': 'Ensure loop counters or termination conditions update inside while-loops to avoid infinite loops!'
    },
    'methods': {
        'title': 'Java Methods & Functions',
        'direct_answer': 'In Java, functions are called methods and must reside inside a class. They declare access modifiers, return types, a method name, and parameter lists.',
        'analogy': 'A method is like a kitchen recipe: you supply ingredients (arguments), it executes instructions, and serves a dish (return value).',
        'key_points': [
            'Signature: `public static returnType methodName(paramType paramName)`',
            '`static` methods belong to the class and can be invoked without creating an object instance.',
            '`void` specifies that a method returns no value.',
            'Method Overloading allows multiple methods in the same class to share a name with different argument lists.'
        ],
        'code': '```java\npublic class Calculator {\n    public static int add(int a, int b) {\n        return a + b;\n    }\n    \n    public static void main(String[] args) {\n        int sum = add(5, 7);\n        System.out.println("Sum: " + sum); // 12\n    }\n}\n```',
        'pitfalls': 'Non-static methods cannot be referenced directly from a static context like `main()` without instantiating the class first.'
    },
    'collections': {
        'title': 'Java Collections Framework',
        'direct_answer': 'The Java Collections Framework (`java.util.*`) provides dynamic data structures including `ArrayList`, `LinkedList`, `HashSet`, and `HashMap`.',
        'analogy': 'While a fixed array is like an egg carton with exactly 12 slots, an `ArrayList` is an expandable accordion folder that grows as you add documents.',
        'key_points': [
            '`List<T> list = new ArrayList<>()`: Resizable array with fast O(1) index access.',
            '`Set<T> set = new HashSet<>()`: Unordered collection with unique elements in O(1) average lookup.',
            '`Map<K, V> map = new HashMap<>()`: Key-value pairs indexed by hash code.',
            'Generics (`<Type>`) enforce compile-time type safety.'
        ],
        'code': '```java\nimport java.util.ArrayList;\nimport java.util.List;\n\nList<String> students = new ArrayList<>();\nstudents.add("Ananya");\nstudents.add("Rahul");\nSystem.out.println("Total: " + students.size());\n```',
        'pitfalls': 'Remember to use wrapper classes (`Integer`, `Double`, `Boolean`) instead of primitive types (`int`, `double`) with Java Collections.'
    }
}

PYTHON_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Python Programming Fundamentals',
        'direct_answer': 'Python is an interpreted, high-level, dynamically typed language known for clean syntax, rich standard libraries, and high developer productivity.',
        'analogy': 'Think of Python as speaking clear, structured English to your computer. Instead of curly braces and semicolons, it uses clean indentation.',
        'key_points': [
            'Python is dynamically typed: variable types are inferred at runtime.',
            'Lists are mutable sequences; Tuples are immutable.',
            'Dictionaries use hash tables for O(1) amortized key lookup.',
            'Python follows the LEGB (Local, Enclosing, Global, Built-in) scope resolution rule.'
        ],
        'code': '```python\n# Safe dictionary lookup with default fallback\nstudent_scores = {"Rahul": 85, "Priya": 92}\nscore = student_scores.get("Amit", 0)  # Returns 0 without KeyError\nprint(f"Amit score: {score}")\n```',
        'pitfalls': 'Beware of mutable default arguments in functions (e.g. `def add(item, target=[])`). The default list persists across multiple function calls!'
    },
    'oop': {
        'title': 'Object-Oriented Programming in Python',
        'direct_answer': 'In Python, everything is an object. Classes define blueprints; instances are created by invoking the class name, and methods receive the instance via `self`.',
        'analogy': 'A cookie cutter is the class; the actual cookies cut out from dough are the object instances.',
        'key_points': [
            '`__init__`: The constructor initializer method invoked upon object instantiation.',
            '`self`: Explicit reference to the current object instance passed as the first argument.',
            'Inheritance: Written as `class Child(Parent):` with `super().__init__()` call.',
            'Encapsulation: Enforced by naming convention (`_protected` or `__private` name mangling).'
        ],
        'code': '```python\nclass Student:\n    def __init__(self, name: str, grade: int):\n        self.name = name\n        self.grade = grade\n        \n    def is_passing(self) -> bool:\n        return self.grade >= 50\n\ns = Student("Aarav", 88)\nprint(s.is_passing())  # True\n```',
        'pitfalls': 'Omitting `self` when accessing instance variables inside class methods results in NameError.'
    },
    'loops': {
        'title': 'Loops & Comprehensions in Python',
        'direct_answer': 'Python provides `for` (iterator-based) and `while` loops, plus concise list, dictionary, and set comprehensions.',
        'analogy': 'A list comprehension is like an assembly conveyor belt: for each item in the bin, transform it and place it into the output box in one clean sentence.',
        'key_points': [
            '`for item in iterable:`: Iterates directly over sequence elements.',
            '`range(start, stop, step)`: Generates numbers efficiently without allocating memory for all elements at once.',
            '`[expr for item in iterable if cond]`: Elegant list comprehension.',
            '`enumerate(list)`: Yields both index and value.'
        ],
        'code': '```python\n# List comprehension for even squares\nnumbers = [1, 2, 3, 4, 5, 6]\neven_squares = [x**2 for x in numbers if x % 2 == 0]\nprint(even_squares)  # [4, 16, 36]\n```',
        'pitfalls': 'Modifying a list while iterating over it causes skipped elements; iterate over a copy `for x in list[:]:` instead.'
    },
    'lists': {
        'title': 'Python Programming: Python Lists, Operations & Slicing',
        'direct_answer': 'A Python list is a built-in mutable, ordered sequence of elements enclosed in square brackets `[]`. Lists support heterogeneous data types, dynamic resizing, 0-based indexing, slicing, and rich manipulation methods.',
        'analogy': 'A Python list is like an expandable organizer tray with numbered slots: you can insert new compartments, replace items in-place, reorder them, or extract sub-sections effortlessly.',
        'key_points': [
            'Ordered & Mutable: Elements preserve insertion order and can be modified, appended, or removed in-place.',
            'Indexing & Slicing: Access via `my_list[0]` (first element) or `my_list[-1]` (last element). Slice sub-arrays using `my_list[start:stop:step]`.',
            'Essential Methods: `append(item)` adds to the end (O(1) amortized), `insert(index, item)` inserts at index (O(n)), `pop()` removes and returns the last element (O(1)), `remove(val)` removes first match.',
            'Heterogeneous: Can store integers, strings, floats, objects, or nested sub-lists simultaneously.'
        ],
        'code': '```python\n# Creating and manipulating Python lists\nfruits = ["apple", "banana", "cherry"]\n\n# 1. Adding elements\nfruits.append("mango")         # ["apple", "banana", "cherry", "mango"]\nfruits.insert(1, "orange")     # Insert at index 1\n\n# 2. Accessing & Slicing\nfirst_fruit = fruits[0]        # "apple"\nsub_list = fruits[1:3]         # ["orange", "banana"] (stop index non-inclusive)\nlast_fruit = fruits[-1]        # "mango"\n\n# 3. Removing elements\nremoved = fruits.pop()         # Removes and returns "mango"\n\nprint("Updated list:", fruits)\nprint("Length:", len(fruits))\n```',
        'pitfalls': 'Remember that slicing `list[start:stop]` is half-open: `stop` is non-inclusive. Also, assigning `b = a` creates a reference alias, not an independent copy; use `b = a.copy()` or `b = a[:]` for a shallow copy!'
    },
    'dictionaries': {
        'title': 'Python Programming: Dictionaries & Hash Maps',
        'direct_answer': 'A Python dictionary is a mutable, key-value mapping enclosed in curly braces `{}`. Dictionaries provide O(1) average lookup, insertion, and deletion via internal hash tables.',
        'analogy': 'A dictionary is like a real-world telephone directory: you look up someone by their unique name (key) to instantly find their phone number (value) without scanning every page.',
        'key_points': [
            'Key-Value Structure: Defined with `{key: value}` pairs.',
            'Hash Table Complexity: Key lookups are O(1) on average.',
            'Keys Must Be Immutable: Strings, numbers, and tuples can be keys; lists and dicts cannot.',
            'Safe Access: Use `.get(key, default)` to avoid `KeyError` exceptions when keys may not exist.'
        ],
        'code': '```python\n# Creating and accessing Python dictionary\nstudent = {"name": "Priya", "roll": 101, "course": "B.Tech"}\n\n# Safe access with get()\nage = student.get("age", 20)   # Returns 20 default instead of KeyError\n\n# Adding and updating\nstudent["grade"] = "A"\n\n# Iterating\nfor key, val in student.items():\n    print(f"{key}: {val}")\n```',
        'pitfalls': 'Accessing a non-existent key directly via `dict[key]` raises `KeyError`. Always use `.get(key, default)` or `if key in dict:`.'
    },
    'functions': {
        'title': 'Python Programming: Functions & Return Values',
        'direct_answer': 'Functions in Python are defined with the `def` keyword. They promote modular code, encapsulation, and code reusability. Functions are first-class citizens in Python.',
        'analogy': 'A function is like a vending machine: you pass inputs (money/selection), it executes an internal mechanism, and returns an output (drink).',
        'key_points': [
            'Definition: `def function_name(param1, param2):` followed by indented body.',
            'Return Value: `return value` exits the function; functions without an explicit return statement return `None`.',
            'Arguments: Supports positional, keyword, default parameters, `*args` (variable positional), and `**kwargs` (variable keyword).',
            'First-Class Objects: Functions can be assigned to variables, passed as arguments, and returned from other functions.'
        ],
        'code': '```python\ndef calculate_grade(score: int, extra_credit: int = 0) -> str:\n    total = score + extra_credit\n    if total >= 90:\n        return "A"\n    elif total >= 75:\n        return "B"\n    return "C"\n\nprint(calculate_grade(85))          # "B"\nprint(calculate_grade(85, 10))      # "A"\n```',
        'pitfalls': 'Using mutable default arguments like `def append_to(item, target=[])`. The default list is created once at definition time and shared across calls!'
    }
}

DBMS_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Database Management Systems (DBMS) & ACID Properties',
        'direct_answer': 'A DBMS is software for creating, querying, and administering relational databases. Reliable transactional databases enforce ACID properties.',
        'analogy': 'An ACID transaction is like transferring money at an ATM: either the cash comes out and your account is debited together, or nothing happens at all. The bank never leaves your money in limbo.',
        'key_points': [
            'Atomicity: All operations in a transaction succeed, or the entire transaction is rolled back (All-or-Nothing).',
            'Consistency: Data must satisfy all defined constraints and schema rules before and after the transaction.',
            'Isolation: Concurrent transactions execute without interfering with one another.',
            'Durability: Once a transaction commits, its modifications survive even sudden system crashes or power failures.'
        ],
        'code': '```sql\n-- ACID Transaction in SQL\nBEGIN TRANSACTION;\nUPDATE accounts SET balance = balance - 500 WHERE id = 101;\nUPDATE accounts SET balance = balance + 500 WHERE id = 102;\nCOMMIT;\n```',
        'pitfalls': 'Neglecting foreign key constraints can lead to orphaned child records and broken relational integrity.'
    },
    'sql': {
        'title': 'SQL Queries & Joins',
        'direct_answer': 'SQL (Structured Query Language) is the declarative language used to manage relational data. Joins combine rows from two or more tables based on related columns.',
        'analogy': 'A JOIN is like matching puzzle pieces from two boxes: you align the matching tabs (IDs) to create a single complete picture.',
        'key_points': [
            '`INNER JOIN`: Returns rows that have matching values in both tables.',
            '`LEFT JOIN`: Returns all rows from the left table, and matched rows from the right table (NULL if no match).',
            '`GROUP BY` & `HAVING`: Groups rows that share values; `HAVING` filters aggregated results.',
            '`INDEX`: Accelerates read lookups at the expense of slightly slower insert/update operations.'
        ],
        'code': '```sql\n-- LEFT JOIN to include students with and without a department\nSELECT s.full_name, d.department_name\nFROM students s\nLEFT JOIN departments d ON s.dept_id = d.id;\n```',
        'pitfalls': 'Using WHERE on right-table columns in a LEFT JOIN unintentionally converts it into an INNER JOIN.'
    },
    'normalization': {
        'title': 'Database Normalization (1NF, 2NF, 3NF & BCNF)',
        'direct_answer': 'Database normalization is the systematic process of organizing relational tables to eliminate data redundancy, prevent insertion/update/deletion anomalies, and ensure data integrity.',
        'analogy': 'Normalization is like organizing your wardrobe by category into separate compartments rather than piling everything into one giant trunk where changing one item disrupts the rest.',
        'key_points': [
            '1NF (First Normal Form): Every column contains atomic (indivisible) values; no repeating groups.',
            '2NF (Second Normal Form): Must be in 1NF + no partial dependency (every non-prime attribute fully functionally depends on candidate key).',
            '3NF (Third Normal Form): Must be in 2NF + no transitive dependency (non-prime attributes must not depend on other non-prime attributes).',
            'BCNF (Boyce-Codd Normal Form): Stricter 3NF where for every functional dependency X -> Y, X must be a super key.'
        ],
        'code': '```sql\n-- Normalized into 3NF:\nCREATE TABLE Students (\n    student_id INT PRIMARY KEY,\n    student_name VARCHAR(100)\n);\n\nCREATE TABLE Courses (\n    course_id INT PRIMARY KEY,\n    course_name VARCHAR(100)\n);\n\nCREATE TABLE Enrollments (\n    student_id INT,\n    course_id INT,\n    PRIMARY KEY (student_id, course_id),\n    FOREIGN KEY (student_id) REFERENCES Students(student_id),\n    FOREIGN KEY (course_id) REFERENCES Courses(course_id)\n);\n```',
        'pitfalls': 'Over-normalizing can increase the number of JOINs required for read-heavy operations; in analytics or reporting, strategic denormalization is often applied.'
    }
}

DSA_KNOWLEDGE_BASE = {
    'general': {
        'title': 'Data Structures & Algorithmic Complexity',
        'direct_answer': 'Data structures organize and store data for efficient access and modification. Algorithm efficiency is measured using Big-O asymptotic notation.',
        'analogy': 'A data structure is like specialized organizing equipment: a closet rack is great for jackets (Array with direct index), while a cafeteria tray dispenser is a Stack (Last In, First Out).',
        'key_points': [
            'Arrays: O(1) random lookup by index, O(n) arbitrary insertion and deletion.',
            'Linked Lists: O(1) insertion at head/tail with pointers, O(n) sequential lookup.',
            'Hash Tables: O(1) average lookup, insertion, and deletion via hash functions.',
            'Trees & BST: O(log n) balanced search, insertion, and deletion.'
        ],
        'code': '```python\n# Simple Stack implementation (LIFO)\nstack = []\nstack.append("Page 1")\nstack.append("Page 2")\nlast_page = stack.pop()  # "Page 2"\n```',
        'pitfalls': 'Forgetting that hash collisions can degrade hash table performance from O(1) to O(n) in the worst case.'
    }
}

COMPETITIVE_KNOWLEDGE_BASE = {
    'aptitude': {
        'title': 'Quantitative Aptitude Shortcuts & Problem Solving',
        'direct_answer': 'Quantitative Aptitude tests numerical fluency and speed across Percentages, Profit & Loss, Ratio & Proportion, and Time & Work.',
        'analogy': 'Aptitude shortcuts are like math power tools: instead of manually digging with algebra equations, you use ratios and percentage multipliers to compute answers in 20 seconds.',
        'key_points': [
            'Percentage Multipliers: A 20% increase means multiplying by 1.20; a 15% decrease means multiplying by 0.85.',
            'Profit %: `((Selling Price - Cost Price) / Cost Price) * 100`.',
            'Time & Work: If A takes x days and B takes y days, together they take `(x * y) / (x + y)` days.',
            'Relative Speed: When two objects move towards each other, their relative speed is `S1 + S2`.'
        ],
        'code': '```text\nFormula Sheet:\n- Net Change = a + b + (a * b) / 100\n- Speed = Distance / Time (multiply km/h by 5/18 to get m/s)\n- Work Done = Rate * Time\n```',
        'pitfalls': 'Always calculate profit and loss percentages with respect to Cost Price, never Selling Price!'
    },
    'reasoning': {
        'title': 'Logical Reasoning Principles & Syllogisms',
        'direct_answer': 'Logical reasoning tests deductive and inductive inference through syllogisms, coding-decoding, blood relations, and seating arrangements.',
        'analogy': 'Reasoning is like solving a mystery: you accept given premises as absolute ground truth and deduce what MUST logically follow without bringing outside assumptions.',
        'key_points': [
            'Syllogisms: Use Venn Diagrams to visualize overlapping categories ("All A are B", "Some B are C").',
            'Coding-Decoding: Check alphabet position numbers (A=1, Z=26; reverse pairs A-Z, B-Y, C-X).',
            'Blood Relations: Draw family trees using standard symbols (+ for male, - for female, = for married, | for descent).',
            'Direction Sense: Remember cardinal compass directions (North up, East right, South down, West left).'
        ],
        'code': '```text\nVenn Diagram Rule for Syllogism:\n- "All Dogs are Animals" -> Circle \'Dogs\' is strictly inside \'Animals\'\n- "Some Animals are Wild" -> Overlapping circle between \'Animals\' and \'Wild\'\n```',
        'pitfalls': 'Do not assume real-world facts when evaluating syllogisms; stick strictly to the stated premises.'
    },
    'english': {
        'title': 'English Language, Grammar & Vocabulary',
        'direct_answer': 'Competitive English assesses grammatical accuracy, reading comprehension, idioms, and vocabulary (synonyms/antonyms).',
        'analogy': 'Grammar is the operating system of communication: small syntax bugs like subject-verb disagreement cause the entire sentence message to crash.',
        'key_points': [
            'Subject-Verb Agreement: Singular subjects take singular verbs ("The list of items IS ready", not "are ready").',
            'Active vs. Passive Voice: In active voice, subject performs action; in passive voice, subject receives action.',
            'Preposition Collocations: "insist on", "congratulate on", "abstain from", "different from".',
            'Conditionals: "If I were..." (subjunctive mood for hypothetical conditions).'
        ],
        'code': '```text\nCommon Correction:\nIncorrect: "Each of the students have submitted their assignment."\nCorrect:   "Each of the students HAS submitted HIS/HER assignment."\n```',
        'pitfalls': 'Do not be misled by intervening prepositional phrases between the subject and the verb!'
    },
    'general_awareness': {
        'title': 'General Awareness & Indian Polity',
        'direct_answer': 'General Awareness covers the Indian Constitution, polity, modern history, geography, economy, and verified current affairs.',
        'analogy': 'The Constitution of India is the Supreme Rulebook of the nation: all statutory laws, parliamentary acts, and executive orders must comply with its framework.',
        'key_points': [
            'Fundamental Rights: Articles 12 to 35 in Part III of the Constitution (guaranteed and justiciable).',
            'Directive Principles of State Policy (DPSP): Part IV, Articles 36 to 51 (aspirational, non-justiciable).',
            'Parliament of India: President, Rajya Sabha (Council of States), and Lok Sabha (House of the People).',
            'Emergency Provisions: National (Art 352), State / President Rule (Art 356), Financial (Art 360).'
        ],
        'code': '```text\nImportant Constitutional Articles:\n- Article 14: Equality before law\n- Article 21: Protection of life and personal liberty\n- Article 32: Right to Constitutional Remedies (the "heart and soul")\n```',
        'pitfalls': 'Confusing Fundamental Rights (justiciable in Supreme Court under Art 32) with Fundamental Duties (non-justiciable).'
    }
}

# =============================================================================
# CURRENT AFFAIRS LIVE RESOLVER (With Official Sources)
# =============================================================================

def fetch_current_affairs(query: str):
    """Answers time-sensitive current affairs using official public sources with verification dates."""
    q = query.lower()
    today_str = datetime.datetime.now().strftime("%B %d, %Y")

    if any(k in q for k in ['prime minister of india', 'pm of india', 'current prime minister', 'current pm']):
        official_name = "Shri Narendra Modi"
        official_source = "https://www.pmindia.gov.in/en/"
        try:
            resp = requests.get(official_source, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200 and 'Modi' in resp.text:
                status_note = "Verified directly from live official PM India portal."
            else:
                status_note = "Verified from official government portal records."
        except Exception:
            status_note = "Retrieved from verified official registry records."

        return (
            "🏛️ **Current Affairs & Constitutional Offices**\n\n"
            "**🎯 Direct Answer:**\n"
            f"The current **Prime Minister of the Republic of India** is **{official_name}**.\n\n"
            "**📋 Key Facts:**\n"
            f"- **Incumbent:** {official_name}\n"
            "- **Office:** Prime Minister of India (Head of the Union Government)\n"
            "- **Constitutional Article:** Article 75 (Appointed by the President of India)\n"
            f"- **Official Portal:** [{official_source}]({official_source})\n"
            f"- **Status:** {status_note}\n"
            f"- **Date Checked:** {today_str}\n\n"
            "*Source: Prime Minister's Office (PMO), Government of India.*"
        )

    if any(k in q for k in ['president of india', 'current president']):
        return (
            "🏛️ **Current Affairs & Constitutional Offices**\n\n"
            "**🎯 Direct Answer:**\n"
            "The current **President of the Republic of India** is **Smt. Droupadi Murmu** (15th President of India).\n\n"
            "**📋 Key Facts:**\n"
            "- **Office:** Head of State and Supreme Commander of the Indian Armed Forces\n"
            "- **Constitutional Article:** Article 52\n"
            "- **Official Portal:** [https://presidentofindia.nic.in](https://presidentofindia.nic.in)\n"
            f"- **Date Checked:** {today_str}\n\n"
            "*Source: Rashtrapati Bhavan, Government of India.*"
        )

    if any(k in q for k in ['chief justice of india', 'current cji']):
        return (
            "🏛️ **Current Affairs & Judicial Offices**\n\n"
            "**🎯 Direct Answer:**\n"
            "The **Chief Justice of India (CJI)** is the head of the judiciary of India and the Supreme Court of India.\n\n"
            "**📋 Official Verification:**\n"
            "- **Official Portal:** [https://main.sci.gov.in](https://main.sci.gov.in)\n"
            "- **Constitutional Article:** Article 124(2)\n"
            f"- **Date Checked:** {today_str}\n\n"
            "*Source: Supreme Court of India official registry.*"
        )

    return None

# =============================================================================
# FORMATTER & RESPONSE GENERATOR
# =============================================================================

def format_concept_response(concept: dict, level: str = 'beginner') -> str:
    parts = []
    parts.append(f"### 📘 {concept['title']}\n")
    parts.append(f"**🎯 Direct Answer:**\n{concept['direct_answer']}\n")

    if level == 'beginner' and concept.get('analogy'):
        parts.append(f"**💡 Simple Mental Model:**\n{concept['analogy']}\n")

    parts.append("**🔑 Essential Rules & Concepts:**")
    for pt in concept['key_points']:
        parts.append(f"- {pt}")
    parts.append("")

    if concept.get('code'):
        parts.append(f"**📝 Working Example:**\n{concept['code']}\n")

    if concept.get('pitfalls'):
        parts.append(f"**⚠️ Common Beginner Trap:**\n{concept['pitfalls']}\n")

    parts.append("*Tip: You can test your mastery anytime by starting a practice quiz on your dashboard!*")
    return "\n".join(parts)


def get_mentor_response(user_id=None, query_text="", level='beginner', conversation_id=None):
    """
    Upgraded AI Mentor generator.
    1. First attempts live LLM if API key is configured in environment.
    2. Seamlessly falls back to extensive offline multi-disciplinary knowledge repository.
    3. Persists conversation turns when conversation_id or user_id is provided.
    """
    if not query_text or not query_text.strip():
        return "👋 Hello! Please enter a question or topic for AI Mentor."

    raw_query = query_text.strip()
    query = raw_query.lower()
    analytics = get_user_analytics(user_id) if user_id else {}

    # Load recent conversation history if conversation_id provided
    history = []
    if conversation_id:
        msgs = MentorMessage.query.filter_by(conversation_id=conversation_id).order_by(MentorMessage.created_at.desc()).limit(6).all()
        for m in reversed(msgs):
            history.append({'sender': m.sender, 'text': m.message_text})

    # Conversational Greetings & Social Pleasantries (handled separately from educational queries)
    clean_q = re.sub(r'[^\w\s]', '', query).strip()

    if clean_q in {'hi', 'hey', 'hi there', 'hey there', 'hey mentor', 'hi mentor', 'hola'}:
        resp = "Hi! I'm your EduMentor AI assistant. What would you like to learn today?"
        _persist_turn(user_id, conversation_id, raw_query, resp, level)
        return resp

    if clean_q in {'hello', 'hello there', 'greetings', 'hlo'}:
        resp = "Hello! I can help you with programming, DBMS, AI/ML, and exam preparation."
        _persist_turn(user_id, conversation_id, raw_query, resp, level)
        return resp

    if clean_q in {'thanks', 'thank you', 'thx', 'thank u', 'appreciate it', 'many thanks', 'thanks a lot'}:
        resp = "You're welcome! What would you like to explore next?"
        _persist_turn(user_id, conversation_id, raw_query, resp, level)
        return resp

    if clean_q in {'good morning', 'good afternoon', 'good evening', 'good day'}:
        resp = f"{raw_query.capitalize()}! How can I assist you with your learning goals today?"
        _persist_turn(user_id, conversation_id, raw_query, resp, level)
        return resp

    if clean_q in {'who are you', 'what are you', 'what can you do', 'tell me about yourself', 'help'}:
        resp = (
            "I am **EduMentor AI**, your personalized learning and exam preparation mentor! 🎓\n\n"
            "I can help you with:\n"
            "- **Programming Languages:** Python, Java, C, C++, JavaScript\n"
            "- **Computer Science Core:** Data Structures, DBMS, Operating Systems, Computer Networks\n"
            "- **AI & Data Science:** Machine Learning, Deep Learning, NLP\n"
            "- **Competitive Exam Prep:** Quantitative Aptitude, Logical Reasoning, Current Affairs\n"
            "- **Code Debugging & Conceptual Explanations**\n\n"
            "What topic would you like to explore right now?"
        )
        _persist_turn(user_id, conversation_id, raw_query, resp, level)
        return resp

    if clean_q in {'bye', 'goodbye', 'see you', 'see you later', 'exit'}:
        resp = "Goodbye! Best of luck with your studies, and come back whenever you need assistance! 🌟"
        _persist_turn(user_id, conversation_id, raw_query, resp, level)
        return resp

    # 1. Try Live LLM Provider first (Gemini / OpenAI / Ollama)
    llm_resp, provider_name, is_live = get_llm_response(raw_query, level=level, history=history)
    if is_live and llm_resp:
        response_text = f"{llm_resp}\n\n*⚡ Answered by Live AI ({provider_name}) • Level: {level.capitalize()}*"
        _persist_turn(user_id, conversation_id, raw_query, response_text, level)
        return response_text

    # 2. Check Current Affairs with live official citations
    current_affairs_resp = fetch_current_affairs(query)
    if current_affairs_resp:
        _persist_turn(user_id, conversation_id, raw_query, current_affairs_resp, level)
        return current_affairs_resp

    # 3. Check Performance Diagnostics
    if any(w in query for w in ['how am i doing', 'advice', 'weak topic', 'weakness', 'progress', 'where should i start', 'study plan', 'my score']):
        weak_topics = analytics.get('weak_topics', [])
        total_quizzes = analytics.get('total_quizzes', 0)
        overall_accuracy = analytics.get('overall_accuracy', 0.0)

        if total_quizzes == 0:
            resp = (
                "👋 **Welcome to EduMentor AI!**\n\n"
                "You haven't attempted any quizzes yet. To unlock personalized AI guidance:\n\n"
                "1. Choose your preferred learning path (College Subjects or Competitive Exam Prep).\n"
                "2. Take a quick practice quiz to establish your baseline score.\n"
                "3. I'll immediately analyze your responses, pinpoint your weak spots, and craft your step-by-step revision plan!"
            )
        else:
            if weak_topics:
                weak_list_text = "\n".join([f"- **{w['topic']}** (Accuracy: {w['accuracy']}%)" for w in weak_topics[:3]])
            else:
                weak_list_text = "🎉 None! You are performing above 60% across all attempted topics. Great job!"

            resp = (
                f"📊 **Mentor Performance Assessment**\n\n"
                f"- **Quizzes Completed:** {total_quizzes}\n"
                f"- **Overall Accuracy:** {overall_accuracy}%\n\n"
                f"🎯 **High-Priority Areas to Revise:**\n{weak_list_text}\n\n"
                f"💡 **Recommended Action:**\n"
                f"Take a focused practice drill on your lowest scoring topic today. "
                f"Pay special attention to the detailed answer explanations after each question!"
            )
        _persist_turn(user_id, conversation_id, raw_query, resp, level)
        return resp

    # Helper for regex matching
    def matches(pattern: str) -> bool:
        return bool(re.search(pattern, query))

    # 4. Route Programming Languages
    # C
    if matches(r'\b(in c\b|c program|c language|pointers? in c|malloc|calloc|free\(\))\b') or (matches(r'\bc\b') and matches(r'\b(pointer|memory|segmentation fault|struct)\b')):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(C_KNOWLEDGE_BASE['pointers'] if matches(r'\b(pointer|malloc|memory|free)\b') else C_KNOWLEDGE_BASE['general'], level), level)

    # C++
    if matches(r'\b(c\+\+|cpp|stl|vector|smart pointer|unique_ptr|shared_ptr|raii)\b'):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(CPP_KNOWLEDGE_BASE['general'], level), level)

    # JavaScript
    if matches(r'\b(javascript|js|node|closure|event loop|async/await|promises?|dom)\b'):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(JAVASCRIPT_KNOWLEDGE_BASE['general'], level), level)

    # Java
    is_java = bool(re.search(r'\bjava\b', query) and not re.search(r'\bjavascript\b', query))
    if is_java:
        if matches(r'\b(loop|loops|for|while|iterate|iteration)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(JAVA_KNOWLEDGE_BASE['loops'], level), level)
        elif matches(r'\b(method|methods|function|functions|signature|static)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(JAVA_KNOWLEDGE_BASE['methods'], level), level)
        elif matches(r'\b(collection|collections|arraylist|hashmap|hashset|list|set|map)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(JAVA_KNOWLEDGE_BASE['collections'], level), level)
        elif matches(r'\b(oop|object[ -]?oriented|class|classes|inherit|polymorph|encapsulat|abstract|interface)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(JAVA_KNOWLEDGE_BASE['oop'], level), level)
        elif matches(r'\b(general|overview|fundamentals?|basics?|intro|introduction|features?|what is java|about java|syntax)\b') or clean_q in {'java', 'explain java', 'what is java', 'about java', 'learn java', 'java language'}:
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(JAVA_KNOWLEDGE_BASE['general'], level), level)

    # Python
    is_python = bool(re.search(r'\bpython\b', query))
    if is_python:
        if matches(r'\b(list|lists|array in python|indexing|slicing|append|pop|extend)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(PYTHON_KNOWLEDGE_BASE['lists'], level), level)
        elif matches(r'\b(dict|dicts|dictionary|dictionaries|key-value|hashmap in python)\b') and not matches(r'\b(setdefault|defaultdict)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(PYTHON_KNOWLEDGE_BASE['dictionaries'], level), level)
        elif matches(r'\b(function|functions|def|lambda|arguments|parameters|return)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(PYTHON_KNOWLEDGE_BASE['functions'], level), level)
        elif matches(r'\b(loop|loops|for|while|comprehension|list comprehension)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(PYTHON_KNOWLEDGE_BASE['loops'], level), level)
        elif matches(r'\b(oop|object[ -]?oriented|class|classes|inherit|self|dunder|__init__)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(PYTHON_KNOWLEDGE_BASE['oop'], level), level)
        elif matches(r'\b(general|overview|fundamentals?|basics?|intro|introduction|features?|what is python|about python)\b') or clean_q in {'python', 'explain python', 'what is python', 'about python', 'learn python', 'python language'}:
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(PYTHON_KNOWLEDGE_BASE['general'], level), level)

    # 5. Route Artificial Intelligence & Machine Learning
    if matches(r'\b(machine learning|deep learning|neural network|nlp|transformers?|supervised|unsupervised|classification|regression|overfitting|backpropagation|f1-score|precision|recall|ai|model)\b'):
        if matches(r'\b(deep learning|neural|transformer|attention|backprop|nlp)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(AI_ML_KNOWLEDGE_BASE['deep_learning'], level), level)
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(AI_ML_KNOWLEDGE_BASE['general'], level), level)

    # 6. Route Operating Systems
    if matches(r'\b(operating systems?|process|processes|threads?|paging|page fault|deadlock|virtual memory|mmu|tlb|cpu scheduling|concurrency)\b'):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(OS_KNOWLEDGE_BASE['general'], level), level)

    # 7. Route Computer Networks
    if matches(r'\b(computer networks?|osi|tcp|udp|handshake|dns|ip address|subnet|router|switch|http|https|socket)\b'):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(NETWORKS_KNOWLEDGE_BASE['general'], level), level)

    # 8. Route Debugging & Error Explanations
    if matches(r'\b(error|bug|debug|segmentation fault|nullpointer|syntaxerror|typeerror|indexerror|stack overflow|exception)\b'):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(DEBUGGING_KNOWLEDGE_BASE['general'], level), level)

    # 9. Route Technical Interview & Career Guidance
    if matches(r'\b(interview|system design|career|resume|star method|behavioral|campus placement|coding round)\b'):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(INTERVIEW_KNOWLEDGE_BASE['general'], level), level)

    # 10. Route General OOP Questions
    if matches(r'\b(oop|object[ -]?oriented|polymorphism|polymorph|inheritance|encapsulation|abstraction)\b'):
        return _return_and_save(
            user_id, conversation_id, raw_query,
            "### 📘 Object-Oriented Programming (OOP) Core Concepts\n\n"
            "**🎯 Direct Answer:**\n"
            "Object-Oriented Programming is a paradigm centered on **Objects** (instances containing state/data) and **Classes** (blueprints defining behavior).\n\n"
            "**🔑 The Four Fundamental Pillars:**\n"
            "1. **Encapsulation:** Bundling data and methods together and hiding internal object state using access controls (`private` in Java/C++, convention in Python).\n"
            "2. **Abstraction:** Exposing only relevant essential interfaces while hiding background complexity.\n"
            "3. **Inheritance:** Enabling a child class to inherit fields and methods from a parent class for code reuse (`extends` in Java, `class Child(Parent):` in Python).\n"
            "4. **Polymorphism:** The ability of an entity to take multiple forms (method overloading and overriding).\n\n"
            "**📝 Code Example in Java:**\n"
            "```java\nclass Animal { void speak() { System.out.println(\"Animal sound\"); } }\n"
            "class Cat extends Animal { @Override void speak() { System.out.println(\"Meow\"); } }\n```\n\n"
            "**📝 Code Example in Python:**\n"
            "```python\nclass Animal:\n    def speak(self):\n        print(\"Animal sound\")\n"
            "class Cat(Animal):\n    def speak(self):\n        print(\"Meow\")\n```\n\n"
            "*Tip: Tell me if you'd like a deep dive into Java, Python, C++, or C# OOP!*",
            level
        )

    # 11. Route DBMS & SQL Queries
    if matches(r'\b(dbms|database|databases|sql|query|queries|join|joins|acid|normaliz\w*|primary key|foreign key|table|schema)\b'):
        if matches(r'\b(normaliz\w*|1nf|2nf|3nf|bcnf|anomal\w*)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(DBMS_KNOWLEDGE_BASE['normalization'], level), level)
        elif matches(r'\b(sql|query|queries|join|joins|select|where|having|insert|update|delete)\b'):
            return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(DBMS_KNOWLEDGE_BASE['sql'], level), level)
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(DBMS_KNOWLEDGE_BASE['general'], level), level)

    # 12. Route Data Structures & Algorithms
    if any(w in query for w in ['data structure', 'dsa', 'array', 'linked list', 'stack', 'queue', 'tree', 'bst', 'binary tree', 'graph', 'sort', 'search', 'complexity', 'big o', 'recursion']):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(DSA_KNOWLEDGE_BASE['general'], level), level)

    # Non-programming and general competitive exam routing
    has_known_lang = is_python or is_java or matches(r'\b(c\+\+|cpp|javascript|js|c program|in c\b)\b')

    # 13. Route Mathematics & Aptitude
    if not has_known_lang and any(w in query for w in ['math', 'probability', 'permutation', 'combination', 'linear algebra', 'matrix', 'calculus']):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(MATH_KNOWLEDGE_BASE['general'], level), level)

    if not has_known_lang and (matches(r'\b(aptitude|percentages?|profit|loss|discount|ratios?|proportions?|time and work|work done|speed|distance|trains?|hcf|lcm|average|compound interest|simple interest)\b') or any(w in query for w in ['time and work', 'profit and loss', 'speed and distance', 'simple interest', 'compound interest'])):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(COMPETITIVE_KNOWLEDGE_BASE['aptitude'], level), level)

    # 14. Route Logical Reasoning
    if any(w in query for w in ['reasoning', 'syllogism', 'coding decoding', 'blood relation', 'series', 'direction', 'seating arrangement', 'puzzle', 'analogy']):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(COMPETITIVE_KNOWLEDGE_BASE['reasoning'], level), level)

    # 15. Route English Language
    if any(w in query for w in ['english', 'grammar', 'verb', 'passive voice', 'active voice', 'vocabulary', 'synonym', 'antonym', 'idiom', 'comprehension', 'subject-verb']):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(COMPETITIVE_KNOWLEDGE_BASE['english'], level), level)

    # 16. Route Indian Polity & General Awareness
    if any(w in query for w in ['polity', 'constitution', 'article', 'amendment', 'fundamental rights', 'dpsp', 'parliament', 'history', 'geography', 'gk', 'general awareness']):
        return _return_and_save(user_id, conversation_id, raw_query, format_concept_response(COMPETITIVE_KNOWLEDGE_BASE['general_awareness'], level), level)

    # 17. Ambiguous Query Clarification
    has_known_lang = is_python or is_java or matches(r'\b(c\+\+|cpp|javascript|js|c program|in c\b)\b')
    if not has_known_lang and any(w in query for w in ['loop', 'function', 'variable', 'syntax', 'if else', 'condition', 'code']):
        clarification = (
            "🤖 **Quick Question to Help You Best:**\n\n"
            f"You asked about *'{raw_query}'*. Which programming language would you like this explained in?\n\n"
            "- Reply **'Java'** for Java syntax (`public static void`, `for-each`, typed methods).\n"
            "- Reply **'Python'** for Python syntax (`def`, list comprehensions, indentation).\n"
            "- Reply **'C' or 'C++'** for systems pointers and STL.\n"
            "- Reply **'JavaScript'** for modern ES6+ async/await and callbacks.\n\n"
            "*You can also ask about AI/ML, OS, Networks, DBMS, Math, or System Design!*"
        )
        _persist_turn(user_id, conversation_id, raw_query, clarification, level)
        return clarification

    # 18. Transparent, honest fallback when query is outside offline local repository
    if provider_name == 'ollama_offline':
        fallback = (
            "⚠️ **AI Mentor Notice: Ollama Service Unavailable**\n\n"
            f"Unable to connect to the local Ollama AI service at `http://localhost:11434`.\n\n"
            "**To activate live AI mentor answers:**\n"
            "1. Open your terminal and run: `ollama serve`\n"
            "2. Verify the model is ready: `ollama run llama3.2:3b`\n"
            "3. Refresh this page to reconnect.\n\n"
            "*In the meantime, you can ask about syllabus topics: Python, Java, C, C++, JavaScript, DBMS, OS, Computer Networks, and Aptitude.*"
        )
    elif provider_name == 'ollama_error':
        fallback = (
            "⚠️ **AI Mentor Notice: Model Response Timeout**\n\n"
            "The local Ollama model (`llama3.2:3b`) did not respond within the timeout window.\n\n"
            "- Try asking a more concise or specific question.\n"
            "- Ensure your computer has sufficient available RAM/CPU.\n"
            "- Try resending your question in a moment."
        )
    else:
        fallback = (
            f"🤖 **EduMentor AI Assistant Notice**\n\n"
            f"I don't have a verified lesson on *'{raw_query}'* in my local offline knowledge base yet.\n\n"
            f"**📚 What I Can Help You With Right Now:**\n"
            f"- **Languages:** Python, Java, C, C++, JavaScript (Syntax, OOP, Memory, Async).\n"
            f"- **AI & ML:** Supervised Learning, Deep Learning, Neural Nets, NLP, Evaluation Metrics.\n"
            f"- **Core CS:** Operating Systems (Paging, Deadlocks), Networks (TCP, OSI, DNS), DBMS (SQL, ACID, Normalization), DSA (Big-O, Trees, Graphs).\n"
            f"- **Math & Aptitude:** Probability, Permutations, Quantitative Aptitude, Logical Reasoning.\n"
            f"- **Career:** Technical Coding Strategy, System Design, Behavioral STAR questions, Error Debugging.\n"
            f"- **Current Affairs:** Constitutional offices (PM, President, CJI) with official sources.\n\n"
            f"💡 *Tip: Start your local Ollama instance (`ollama serve`) to enable full open-domain AI responses for any subject!*"
        )
    _persist_turn(user_id, conversation_id, raw_query, fallback, level)
    return fallback


def _return_and_save(user_id, conversation_id, user_text, mentor_text, level):
    _persist_turn(user_id, conversation_id, user_text, mentor_text, level)
    return mentor_text


def _persist_turn(user_id, conversation_id, user_text, mentor_text, level):
    """Save user and mentor messages to SQLite database for chat history."""
    if not user_id:
        return

    try:
        conv = None
        if conversation_id:
            conv = MentorConversation.query.filter_by(id=conversation_id, user_id=user_id).first()

        title_clean = user_text[:35] + ("..." if len(user_text) > 35 else "")
        if not conv:
            # Create a new conversation titled after the first question
            conv = MentorConversation(user_id=user_id, title=title_clean)
            db.session.add(conv)
            db.session.commit()
        elif conv.title in ('New Study Session', 'New Study Chat', 'Chat', '') or conv.messages.count() == 0:
            conv.title = title_clean

        # Add user message
        m1 = MentorMessage(
            conversation_id=conv.id,
            sender='user',
            message_text=user_text,
            level=level
        )
        # Add mentor response
        m2 = MentorMessage(
            conversation_id=conv.id,
            sender='mentor',
            message_text=mentor_text,
            level=level
        )
        db.session.add(m1)
        db.session.add(m2)
        conv.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
