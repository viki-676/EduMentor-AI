"""
Initial learning resources catalog and seed script for EduMentor AI.
Contains calibrated, production-grade educational material across 10 subject domains.
"""

import json
from models import db, LearningResource

INITIAL_RESOURCES = [
    # 1. Programming Languages - C
    {
        'category': 'Programming Languages',
        'subject': 'C Programming',
        'topic': 'Pointers, Dynamic Memory & Addresses',
        'slug': 'c-pointers-and-memory',
        'title': 'Mastering C Pointers and Dynamic Memory Allocation',
        'summary': 'Understand memory addresses, dereferencing, pointer arithmetic, and heap allocation via malloc, calloc, and free.',
        'difficulty': 'Intermediate',
        'estimated_reading_minutes': 12,
        'prerequisites': 'Basic C syntax, variables, and data types',
        'definitions_json': json.dumps([
            {'term': 'Pointer', 'definition': 'A variable that stores the hexadecimal memory address of another variable.'},
            {'term': 'Dereferencing (*)', 'definition': 'Accessing or mutating the value stored at the memory address pointed to by a pointer.'},
            {'term': 'Heap Memory', 'definition': 'Region of memory managed manually at runtime via dynamic allocation functions.'},
            {'term': 'Memory Leak', 'definition': 'Failure to deallocate dynamically allocated heap memory using free(), wasting system memory.'}
        ]),
        'concepts_markdown': """### What is a Pointer?
In C, every variable resides at a unique memory location with an address. While a regular variable holds a direct value (like an `int` holding `42`), a pointer stores the **address** of that memory location.

```c
int num = 42;
int *ptr = &num; // ptr holds the address of num
```

### The Stack vs. The Heap
1. **Stack Memory:** Fast, automatically allocated and freed when functions enter and exit. Fixed size at compile time.
2. **Heap Memory:** Flexible, dynamically requested at runtime. Must be explicitly released with `free(ptr)`.

### Dynamic Memory Allocation Functions
- `malloc(size_t size)`: Allocates uninitialized memory of specified bytes.
- `calloc(size_t n, size_t size)`: Allocates zero-initialized contiguous memory for `n` elements.
- `realloc(void *ptr, size_t new_size)`: Resizes previously allocated heap block.
- `free(void *ptr)`: Returns memory block back to the operating system heap pool.""",
        'step_by_step_examples': """#### Step-by-Step Dynamic Array Allocation:
1. Declare a pointer variable: `int *arr = NULL;`
2. Request heap space using `malloc`: `arr = (int *)malloc(n * sizeof(int));`
3. Always verify allocation succeeded: `if (arr == NULL) { /* handle error */ }`
4. Use array indexing or pointer arithmetic: `arr[i] = val;`
5. Free allocated memory when finished: `free(arr); arr = NULL;`""",
        'code_examples_json': json.dumps([
            {
                'title': 'Dynamic Array Allocation & Cleanup in C',
                'language': 'c',
                'code': """#include <stdio.h>
#include <stdlib.h>

int main() {
    int n = 5;
    int *arr = (int *)malloc(n * sizeof(int));
    if (arr == NULL) {
        printf("Memory allocation failed!\\n");
        return 1;
    }

    for (int i = 0; i < n; i++) {
        arr[i] = (i + 1) * 10;
        printf("arr[%d] = %d (address: %p)\\n", i, arr[i], (void*)&arr[i]);
    }

    free(arr);
    arr = NULL; // Prevent dangling pointer
    printf("Memory safely released.\\n");
    return 0;
}""",
                'explanation': 'Demonstrates safe heap allocation, validation against NULL, element traversal, and setting pointer to NULL after free.'
            }
        ]),
        'key_points_json': json.dumps([
            'The ampersand (&) operator yields a variable memory address.',
            'The asterisk (*) operator dereferences a pointer to access its target value.',
            'Always verify malloc/calloc return value is not NULL before dereferencing.',
            'Every malloc/calloc call must have a corresponding free() call to prevent memory leaks.',
            'Setting freed pointers to NULL prevents catastrophic dangling pointer bugs.'
        ]),
        'common_mistakes_json': json.dumps([
            'Dangling Pointer: Accessing memory through a pointer after calling free().',
            'Memory Leak: Overwriting a pointer without freeing its allocated heap block.',
            'Double Free: Calling free() twice on the same memory address.',
            'Forgetting sizeof(): Allocating malloc(5) instead of malloc(5 * sizeof(int)).'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'What is the value of *ptr if ptr points to an integer x with value 25?',
                'answer': '25',
                'explanation': 'Dereferencing (*ptr) retrieves the content stored at the address pointed to by ptr.'
            },
            {
                'question': 'What does free(ptr) do to the variable ptr itself?',
                'answer': 'It releases the heap memory pointed to by ptr, but does NOT reset ptr to NULL.',
                'explanation': 'ptr remains holding the old address (a dangling pointer) until explicitly set to NULL.'
            }
        ]),
        'related_topics': 'C Dynamic Data Structures, Linked Lists, Segmentation Faults',
        'order_index': 1
    },

    # 2. Programming Languages - C++
    {
        'category': 'Programming Languages',
        'subject': 'C++ Programming',
        'topic': 'OOP, RAII & Modern Smart Pointers',
        'slug': 'cpp-oop-smart-pointers',
        'title': 'C++ Object-Oriented Design and Modern Smart Pointers',
        'summary': 'Master classes, virtual functions, RAII (Resource Acquisition Is Initialization), unique_ptr, and shared_ptr in Modern C++.',
        'difficulty': 'Intermediate',
        'estimated_reading_minutes': 14,
        'prerequisites': 'Basic C++ syntax and references',
        'definitions_json': json.dumps([
            {'term': 'RAII', 'definition': 'Resource Acquisition Is Initialization: tying resource lifetime to object lifetime so destructors automatically release memory.'},
            {'term': 'std::unique_ptr', 'definition': 'A smart pointer that exclusively owns and manages another object through a pointer and disposes of it when exiting scope.'},
            {'term': 'std::shared_ptr', 'definition': 'A smart pointer that retains shared ownership of an object via reference counting.'},
            {'term': 'Virtual Function', 'definition': 'A member function in a base class that you expect to override in derived classes for runtime polymorphism.'}
        ]),
        'concepts_markdown': """### Modern C++ Philosophy: No Raw New / Delete
In Modern C++ (C++11 and beyond), manual `new` and `delete` are strongly discouraged in favor of **smart pointers** (`std::unique_ptr`, `std::shared_ptr`) residing in `<memory>`.

### The RAII Idiom
When an object is created on the stack, its constructor acquires resources (memory, file handles, mutex locks). When the object leaves its enclosing block scope, its destructor is **guaranteed** to run, releasing the resource even if an exception is thrown.

### Polymorphism with Virtual Destructors
Always declare a `virtual` destructor in base classes with virtual methods so deleting via a base pointer invokes the derived class destructor.""",
        'step_by_step_examples': """#### Choosing the Right Smart Pointer:
1. **Exclusive Ownership?** Use `std::unique_ptr<T>`. Fast, zero overhead compared to a raw pointer. Cannot be copied, only moved (`std::move`).
2. **Shared Ownership?** Use `std::shared_ptr<T>`. Uses atomic reference counting. Frees memory when the reference count drops to 0.
3. **Circular Reference Prevention?** Use `std::weak_ptr<T>` to observe a shared pointer without incrementing reference counts.""",
        'code_examples_json': json.dumps([
            {
                'title': 'Polymorphism and std::unique_ptr in Modern C++',
                'language': 'cpp',
                'code': """#include <iostream>
#include <memory>
#include <vector>

class Shape {
public:
    virtual void draw() const = 0; // Pure virtual
    virtual ~Shape() { std::cout << "Shape destroyed\\n"; }
};

class Circle : public Shape {
public:
    void draw() const override {
        std::cout << "Drawing Circle\\n";
    }
    ~Circle() override { std::cout << "Circle destroyed\\n"; }
};

int main() {
    // std::make_unique guarantees exception-safe allocation
    std::unique_ptr<Shape> s = std::make_unique<Circle>();
    s->draw();
    // Memory automatically freed when s exits scope!
    return 0;
}""",
                'explanation': 'Demonstrates pure virtual functions, override keyword, make_unique, and automatic destructor execution.'
            }
        ]),
        'key_points_json': json.dumps([
            'Use std::make_unique and std::make_shared instead of raw new.',
            'std::unique_ptr is move-only and incurs zero runtime memory overhead.',
            'Always make base class destructors virtual when using inheritance.',
            'RAII prevents resource leaks by tying cleanup to scope termination.'
        ]),
        'common_mistakes_json': json.dumps([
            'Non-virtual Base Destructor: Results in undefined behavior and sliced object cleanup.',
            'Circular shared_ptr: Two shared_ptrs pointing to each other create reference leaks.',
            'Calling get() on unique_ptr and manually calling delete on the raw pointer.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'Can std::unique_ptr be copied to another unique_ptr with operator=?',
                'answer': 'No, its copy constructor is deleted; it can only be transferred using std::move().',
                'explanation': 'std::unique_ptr models exclusive ownership, so copying is prohibited.'
            }
        ]),
        'related_topics': 'C++ Move Semantics, Standard Template Library (STL), Design Patterns',
        'order_index': 2
    },

    # 3. Programming Languages - JavaScript
    {
        'category': 'Programming Languages',
        'subject': 'JavaScript',
        'topic': 'Event Loop, Closures & Async/Await',
        'slug': 'javascript-event-loop-async',
        'title': 'The JavaScript Event Loop, Closures and Asynchronous Programming',
        'summary': 'Deep dive into single-threaded concurrency, the Call Stack, Web APIs, Microtask vs Macrotask queues, Closures, and Promises.',
        'difficulty': 'Intermediate',
        'estimated_reading_minutes': 15,
        'prerequisites': 'Basic JavaScript syntax and functions',
        'definitions_json': json.dumps([
            {'term': 'Closure', 'definition': 'A function bundled together with references to its surrounding lexical environment.'},
            {'term': 'Event Loop', 'definition': 'The runtime mechanism that coordinates the Call Stack, Microtask queue (Promises), and Task queue (setTimeout).'},
            {'term': 'Promise', 'definition': 'An object representing the eventual completion (or failure) of an asynchronous operation and its resulting value.'},
            {'term': 'Microtask Queue', 'definition': 'High-priority queue containing Promise callbacks (.then, queueMicrotask) executed immediately after call stack empties.'}
        ]),
        'concepts_markdown': """### Single-Threaded Non-Blocking Architecture
JavaScript is single-threaded: it has exactly **one Call Stack**. However, web browsers and Node.js provide asynchronous background workers (Web APIs, libuv) that run I/O operations concurrently.

### The Execution Lifecycle:
1. **Call Stack:** Synchronous code executes line by line.
2. **Web APIs / Node APIs:** Timers, fetch requests, and DOM events are handled outside the main thread.
3. **Microtask Queue:** Resolves Promise callbacks (`.then`, `await`).
4. **Macrotask Queue:** Resolves `setTimeout`, `setInterval`, and I/O callbacks.
5. **Event Loop Rule:** The Event Loop checks if the Call Stack is empty. If empty, it exhausts the **entire** Microtask queue before picking the next Macrotask!""",
        'step_by_step_examples': """#### Understanding Closures:
A closure is formed whenever an inner function accesses variables defined in its parent function scope, even after the parent function has finished executing.""",
        'code_examples_json': json.dumps([
            {
                'title': 'Event Loop Execution Order & Closure Demo',
                'language': 'javascript',
                'code': """console.log("1. Synchronous Start");

setTimeout(() => {
    console.log("4. Macrotask (setTimeout)");
}, 0);

Promise.resolve().then(() => {
    console.log("3. Microtask (Promise)");
});

// Closure example
function createCounter() {
    let count = 0; // Private state retained by closure
    return () => ++count;
}
const counter = createCounter();
console.log("2. Counter val:", counter()); // 1

// Output order: 1 -> 2 -> 3 -> 4""",
                'explanation': 'Shows synchronous execution first, microtask resolution second, and macrotask execution third.'
            }
        ]),
        'key_points_json': json.dumps([
            'JavaScript has a single call stack and handles concurrency via the Event Loop.',
            'Microtasks (Promises) always take precedence over Macrotasks (setTimeout, setInterval).',
            'Closures allow functions to maintain access to private enclosing variables.',
            'Async/Await is syntactic sugar over Promises, making asynchronous code read synchronously.'
        ]),
        'common_mistakes_json': json.dumps([
            'Assuming setTimeout(fn, 0) runs immediately; it only queues for the next macrotask turn.',
            'Creating memory leaks by unintentionally holding global references inside closures.',
            'Uncaught Promise rejections by omitting try/catch blocks around await.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'Which runs first after the call stack empties: Promise.then callback or setTimeout callback?',
                'answer': 'Promise.then callback (Microtask queue runs before Macrotask queue).',
                'explanation': 'The event loop clears all pending microtasks before processing the next macrotask.'
            }
        ]),
        'related_topics': 'Node.js Architecture, Web Workers, Prototypes & Prototypal Inheritance',
        'order_index': 3
    },

    # 4. Artificial Intelligence & Machine Learning
    {
        'category': 'Artificial Intelligence and Machine Learning',
        'subject': 'Machine Learning',
        'topic': 'Supervised Learning & Model Evaluation Metrics',
        'slug': 'ml-supervised-learning-metrics',
        'title': 'Supervised Learning Foundations & Rigorous Evaluation Metrics',
        'summary': 'Master regression vs classification, bias-variance tradeoff, cross-validation, Precision, Recall, F1-Score, and ROC-AUC.',
        'difficulty': 'Intermediate',
        'estimated_reading_minutes': 14,
        'prerequisites': 'Basic Python, linear algebra, and statistics',
        'definitions_json': json.dumps([
            {'term': 'Supervised Learning', 'definition': 'Training a model on labeled input-output pairs to learn a mapping function f(X) -> Y.'},
            {'term': 'Overfitting', 'definition': 'When a model learns training noise and details too closely, resulting in poor generalization on unseen test data.'},
            {'term': 'Precision', 'definition': 'True Positives / (True Positives + False Positives): measure of accuracy among positive predictions.'},
            {'term': 'Recall (Sensitivity)', 'definition': 'True Positives / (True Positives + False Negatives): proportion of actual positives correctly identified.'},
            {'term': 'F1-Score', 'definition': 'Harmonic mean of Precision and Recall: 2 * (P * R) / (P + R).'}
        ]),
        'concepts_markdown': """### The Supervised Learning Workflow
1. **Data Preprocessing & Splitting:** Divide into Train, Validation, and Test sets (e.g. 70/15/15 or 80/20).
2. **Feature Scaling:** Apply StandardScaler or MinMaxScaler to prevent magnitude bias.
3. **Training & Hyperparameter Tuning:** Fit model on training set, tune using K-Fold Cross-Validation.
4. **Generalization Evaluation:** Evaluate on held-out test set without data leakage.

### Bias-Variance Tradeoff
- **High Bias (Underfitting):** Model is too simplistic (e.g. linear model on non-linear data). High training and test errors.
- **High Variance (Overfitting):** Model is overly complex (e.g. deep unpruned decision tree). Low training error, high test error.

### When to Prioritize Precision vs. Recall
- **High Precision Priority:** Spam detection (better to send spam to inbox than legitimate email to spam folder).
- **High Recall Priority:** Cancer or disease detection, fraud alerts (better to have false alarms than miss a true positive).""",
        'step_by_step_examples': """#### Calculating Classification Metrics:
Suppose a medical model predicts 100 patient scans:
- True Positives (TP) = 20
- False Positives (FP) = 5
- False Negatives (FN) = 2
- True Negatives (TN) = 73

`Precision = 20 / (20 + 5) = 20 / 25 = 0.80 (80%)`
`Recall = 20 / (20 + 2) = 20 / 22 = 0.909 (90.9%)`
`F1 = 2 * (0.80 * 0.909) / (0.80 + 0.909) = 0.851`""",
        'code_examples_json': json.dumps([
            {
                'title': 'Model Training & Classification Report in Scikit-Learn',
                'language': 'python',
                'code': """from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.datasets import make_classification

# Generate sample dataset
X, y = make_classification(n_samples=500, n_features=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=['Class 0', 'Class 1']))""",
                'explanation': 'Demonstrates proper train-test split, model fitting, and evaluation with comprehensive classification metrics.'
            }
        ]),
        'key_points_json': json.dumps([
            'Never evaluate a model exclusively on accuracy when dealing with imbalanced datasets.',
            'F1-score provides a balanced metric between precision and recall.',
            'Cross-validation ensures model stability and shields against lucky data splits.',
            'Regularization (L1 Lasso, L2 Ridge) helps constrain weights and combat overfitting.'
        ]),
        'common_mistakes_json': json.dumps([
            'Data Leakage: Normalizing the full dataset before splitting into train/test sets.',
            'Evaluating solely on Accuracy when 95% of samples belong to the majority class.',
            'Tuning hyperparameters directly on the test set instead of validation folds.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'If a disease detection model predicts positive only when 100% sure, will precision or recall suffer?',
                'answer': 'Recall will suffer (drop significantly), while precision will be very high.',
                'explanation': 'Being overly conservative leads to many False Negatives, directly reducing Recall.'
            }
        ]),
        'related_topics': 'Neural Networks, Unsupervised Learning, Feature Engineering, Scikit-learn',
        'order_index': 4
    },

    # 5. Computer Science Fundamentals - OS
    {
        'category': 'Operating Systems',
        'subject': 'Operating Systems',
        'topic': 'Processes, Threads & Memory Paging',
        'slug': 'os-processes-threads-paging',
        'title': 'Operating Systems: Process Scheduling, Virtual Memory & Paging',
        'summary': 'Understand process control blocks (PCB), multi-threading, context switching, virtual addresses, page tables, and page faults.',
        'difficulty': 'Intermediate',
        'estimated_reading_minutes': 13,
        'prerequisites': 'Computer organization and basic systems concepts',
        'definitions_json': json.dumps([
            {'term': 'Process', 'definition': 'A program in execution, consisting of code (text), stack, heap, data, and a PCB.'},
            {'term': 'Thread', 'definition': 'The smallest sequence of programmed instructions that can be managed independently by a scheduler, sharing address space with sibling threads.'},
            {'term': 'Virtual Memory', 'definition': 'A memory management technique providing an idealized abstraction of storage resources for each process.'},
            {'term': 'Page Fault', 'definition': 'An interrupt raised by hardware (MMU) when a program accesses a virtual page that is not currently mapped into physical RAM.'}
        ]),
        'concepts_markdown': """### Process vs. Thread Comparison
| Feature | Process | Thread |
| :--- | :--- | :--- |
| **Address Space** | Isolated private address space | Shares address space with parent process |
| **Creation Overhead** | Heavy (fork/exec) | Lightweight |
| **Communication** | IPC (pipes, sockets, shared memory) | Direct memory access (requires synchronization) |
| **Failure Impact** | Crash does not crash other processes | Uncaught crash can terminate entire process |

### Virtual Memory and Paging
1. The CPU generates **Virtual Addresses** composed of a **Page Number** and an **Offset**.
2. The **Memory Management Unit (MMU)** uses the **Page Table** to translate Page Numbers into physical **Frame Numbers**.
3. If the present bit in the Page Table entry is 0, the CPU triggers a **Page Fault**.
4. The OS brings the missing page from disk swap into an available RAM frame and resumes the instruction.""",
        'step_by_step_examples': """#### Virtual Address Translation Calculation:
Given:
- Virtual address space = 32-bit
- Page size = 4 KB ($2^{12}$ bytes)

1. Offset bits = $\\log_2(4096) = 12$ bits.
2. Page number bits = $32 - 12 = 20$ bits.
3. Total virtual pages = $2^{20} = 1,048,576$ pages.
4. Physical address = Frame Number concatenated with Offset.""",
        'code_examples_json': json.dumps([
            {
                'title': 'POSIX Multithreading in C with Mutex Synchronization',
                'language': 'c',
                'code': """#include <stdio.h>
#include <pthread.h>

int counter = 0;
pthread_mutex_t lock;

void* increment(void* arg) {
    for (int i = 0; i < 10000; i++) {
        pthread_mutex_lock(&lock);
        counter++;
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_mutex_init(&lock, NULL);

    pthread_create(&t1, NULL, increment, NULL);
    pthread_create(&t2, NULL, increment, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    pthread_mutex_destroy(&lock);
    printf("Final synchronized counter: %d\\n", counter); // 20000
    return 0;
}""",
                'explanation': 'Demonstrates thread creation, mutual exclusion lock protection against race conditions, and thread joining.'
            }
        ]),
        'key_points_json': json.dumps([
            'Processes are isolated; threads share memory, open file descriptors, and global variables.',
            'Paging eliminates external fragmentation by using fixed-size blocks.',
            'TLB (Translation Lookaside Buffer) caches page-to-frame translations for fast memory lookups.',
            'Thrashing occurs when the system spends more time paging data to/from disk than executing code.'
        ]),
        'common_mistakes_json': json.dumps([
            'Confusing Concurrency (dealing with multiple things at once) with Parallelism (doing multiple things at once).',
            'Failing to lock shared variables across threads, causing non-deterministic race conditions.',
            'Assuming virtual memory increases physical RAM size; it allows execution using disk swap as backing store.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'What hardware component performs virtual-to-physical address translation at CPU speeds?',
                'answer': 'The MMU (Memory Management Unit), supported by the TLB cache.',
                'explanation': 'The MMU translates virtual page numbers to physical frame numbers using page tables.'
            }
        ]),
        'related_topics': 'CPU Scheduling Algorithms, Deadlocks & Banker Algorithm, File Systems',
        'order_index': 5
    },

    # 6. Computer Science Fundamentals - Networks
    {
        'category': 'Computer Networks',
        'subject': 'Computer Networks',
        'topic': 'OSI Model, TCP Handshake & DNS Resolution',
        'slug': 'networks-osi-tcp-dns',
        'title': 'Computer Networks: The OSI Model, TCP Handshake & DNS Architecture',
        'summary': 'Master the 7-layer OSI model vs TCP/IP, the SYN-SYN/ACK-ACK handshake, UDP vs TCP, and step-by-step DNS query resolution.',
        'difficulty': 'Intermediate',
        'estimated_reading_minutes': 13,
        'prerequisites': 'Basic understanding of Internet protocols',
        'definitions_json': json.dumps([
            {'term': 'OSI Model', 'definition': 'A 7-layer conceptual framework developed by ISO to standardize network communication functions.'},
            {'term': 'TCP (Transmission Control Protocol)', 'definition': 'A connection-oriented, reliable transport protocol with error checking, flow control, and ordered delivery.'},
            {'term': 'UDP (User Datagram Protocol)', 'definition': 'A connectionless, lightweight transport protocol prioritizing low latency over reliability.'},
            {'term': 'DNS', 'definition': 'Domain Name System: the hierarchical naming system resolving human-readable domain names to IP addresses.'}
        ]),
        'concepts_markdown': """### The 7 Layers of the OSI Model
1. **Application (Layer 7):** HTTP, HTTPS, FTP, DNS, SSH
2. **Presentation (Layer 6):** Data translation, encryption (TLS), compression
3. **Session (Layer 5):** Manages dialogues and connections
4. **Transport (Layer 4):** End-to-end delivery, segmentation, flow control (TCP, UDP)
5. **Network (Layer 3):** Routing, logical addressing (IP, ICMP, Routers)
6. **Data Link (Layer 2):** Framing, MAC addresses, error detection (Switches, Ethernet)
7. **Physical (Layer 1):** Raw transmission of bits over physical media (Cables, Radio frequencies)

### TCP Three-Way Handshake
Before sending data, TCP establishes a connection:
1. **Client -> Server (SYN):** Client sends Synchronize packet with initial sequence number $ISN_C$.
2. **Server -> Client (SYN-ACK):** Server acknowledges with $ACK = ISN_C + 1$ and sends its own $ISN_S$.
3. **Client -> Server (ACK):** Client acknowledges server sequence with $ACK = ISN_S + 1$. Connection Established!""",
        'step_by_step_examples': """#### Step-by-Step DNS Resolution for `example.com`:
1. **Browser Cache Check:** Browser checks internal DNS cache.
2. **OS Cache / Hosts File:** Checks local OS resolver cache.
3. **Recursive Resolver:** Queries ISP or configured DNS (e.g. 8.8.8.8, 1.1.1.1).
4. **Root Nameserver (.):** Directs query to the `.com` TLD nameserver.
5. **TLD Nameserver (.com):** Directs query to authoritative nameserver for `example.com`.
6. **Authoritative Nameserver:** Returns the canonical IPv4 (A record) or IPv6 (AAAA record).""",
        'code_examples_json': json.dumps([
            {
                'title': 'Python Socket Programming: Simple TCP Client',
                'language': 'python',
                'code': """import socket

def check_web_server(host='www.google.com', port=80):
    # Create TCP IPv4 socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    try:
        s.connect((host, port))
        print(f"Successfully connected to {host} on port {port} via TCP!")
        # Send basic HTTP HEAD request
        s.sendall(b"HEAD / HTTP/1.1\\r\\nHost: " + host.encode() + b"\\r\\n\\r\\n")
        response = s.recv(1024)
        print("Server Response Banner:\\n", response.decode().split('\\r\\n')[0])
    except Exception as e:
        print("Connection failed:", e)
    finally:
        s.close()

if __name__ == '__main__':
    check_web_server()""",
                'explanation': 'Demonstrates socket creation, TCP connection initiation, sending raw HTTP bytes, and safe socket cleanup.'
            }
        ]),
        'key_points_json': json.dumps([
            'TCP guarantees ordered, lossless packet delivery using sequence numbers and ACKs.',
            'UDP is connectionless and best for real-time applications (video streaming, gaming, VoIP).',
            'Routers operate at Layer 3 (Network); Switches typically operate at Layer 2 (Data Link).',
            'HTTPS encrypts Layer 7 data using TLS before passing it down to Layer 4 (TCP).'
        ]),
        'common_mistakes_json': json.dumps([
            'Confusing MAC addresses (local Layer 2 delivery) with IP addresses (end-to-end Layer 3 routing).',
            'Thinking UDP has lower throughput than TCP; UDP has lower latency and less protocol overhead.',
            'Forgetting that DNS queries typically use UDP port 53 for speed, switching to TCP for large responses.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'Which flags are exchanged in order during the TCP connection setup?',
                'answer': 'SYN, SYN-ACK, ACK',
                'explanation': 'The 3-way handshake begins with client SYN, followed by server SYN-ACK, and concluded with client ACK.'
            }
        ]),
        'related_topics': 'Subnetting & CIDR, HTTP/2 & HTTP/3 (QUIC), Network Security & Firewalls',
        'order_index': 6
    },

    # 7. Database Management - SQL & Normalization
    {
        'category': 'Database Management',
        'subject': 'Database Systems (DBMS)',
        'topic': 'Normalization (1NF to BCNF) & SQL Joins',
        'slug': 'dbms-normalization-sql-joins',
        'title': 'Relational Database Normalization and Advanced SQL Joins',
        'summary': 'Master database anomalies, Functional Dependencies, 1NF, 2NF, 3NF, BCNF, and INNER, LEFT, RIGHT, and FULL OUTER joins.',
        'difficulty': 'Intermediate',
        'estimated_reading_minutes': 14,
        'prerequisites': 'Basic SQL SELECT queries and relational table concepts',
        'definitions_json': json.dumps([
            {'term': 'Functional Dependency (X -> Y)', 'definition': 'Constraint where the value of attribute X uniquely determines the value of attribute Y.'},
            {'term': '1NF (First Normal Form)', 'definition': 'All table attributes contain atomic (indivisible) values and each row is unique.'},
            {'term': '2NF (Second Normal Form)', 'definition': 'In 1NF and no non-prime attribute is partially dependent on any candidate key.'},
            {'term': '3NF (Third Normal Form)', 'definition': 'In 2NF and no non-prime attribute is transitively dependent on candidate keys.'},
            {'term': 'BCNF (Boyce-Codd Normal Form)', 'definition': 'Strict version of 3NF where for every functional dependency X -> Y, X must be a super key.'}
        ]),
        'concepts_markdown': """### Why Normalize Databases?
Unnormalized schemas suffer from three critical data anomalies:
1. **Insertion Anomaly:** Cannot record student information without registering them for a course.
2. **Deletion Anomaly:** Deleting the last course enrollment unintentionally deletes the student record.
3. **Update Anomaly:** Updating a teacher's phone number requires modifying hundreds of redundant rows.

### Summary of Normal Forms:
- **1NF:** Atomic values only. No arrays, comma-separated lists, or nested records.
- **2NF:** Eliminate partial dependencies. Every non-key column must depend on the **entire** composite primary key.
- **3NF:** Eliminate transitive dependencies ($A \\to B$ and $B \\to C$). Non-key columns cannot depend on other non-key columns.
- **BCNF:** For every dependency $X \\to Y$, $X$ must be a super key.""",
        'step_by_step_examples': """#### Understanding SQL Join Types:
Consider tables `Students (id, name, dept_id)` and `Departments (id, dept_name)`:
- `INNER JOIN`: Returns rows that have matching values in both tables.
- `LEFT JOIN`: Returns all rows from left table, with matched rows from right table (NULL if no match).
- `RIGHT JOIN`: Returns all rows from right table, with matched rows from left table.
- `FULL OUTER JOIN`: Returns all rows when there is a match in either left or right table.""",
        'code_examples_json': json.dumps([
            {
                'title': 'Advanced SQL Joins and Aggregation',
                'language': 'sql',
                'code': """-- Find department names and student counts, including departments with 0 students
SELECT 
    d.dept_name,
    COUNT(s.id) AS total_students,
    COALESCE(AVG(s.gpa), 0.0) AS average_gpa
FROM departments d
LEFT JOIN students s ON d.id = s.dept_id
GROUP BY d.dept_name
HAVING COUNT(s.id) >= 0
ORDER BY total_students DESC;""",
                'explanation': 'Demonstrates LEFT JOIN to preserve unmatched parent records, GROUP BY, aggregation, and COALESCE fallback.'
            }
        ]),
        'key_points_json': json.dumps([
            'Normalization eliminates redundancy and prevents insertion, update, and deletion anomalies.',
            '3NF and BCNF are standard target normal forms for production transactional (OLTP) databases.',
            'Denormalization is intentionally used in data warehouses (OLAP) to accelerate read queries.',
            'Indexes (B-Trees) speed up JOIN operations by indexing Foreign Key columns.'
        ]),
        'common_mistakes_json': json.dumps([
            'Over-normalizing OLAP reporting databases, requiring 15+ slow table joins.',
            'Confusing WHERE filters with ON conditions in LEFT JOINs, accidentally converting them to INNER JOINs.',
            'Storing multi-valued comma-separated IDs in a single column (violating 1NF).'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'If a table is in 1NF and has a single-column primary key, is it automatically in 2NF?',
                'answer': 'Yes, because partial dependency can only occur when the primary key is composite.',
                'explanation': 'A single-column key cannot have partial dependencies since there are no multiple key components.'
            }
        ]),
        'related_topics': 'Database Indexing (B+ Trees), ACID Transactions, Query Optimization',
        'order_index': 7
    },

    # 8. Mathematics and Aptitude
    {
        'category': 'Mathematics and Aptitude',
        'subject': 'Quantitative Aptitude',
        'topic': 'Percentages, Profit & Loss and Time-Speed-Distance',
        'slug': 'quant-percentages-profit-loss-speed',
        'title': 'High-Yield Quantitative Aptitude Formulas and Shortcut Methods',
        'summary': 'Master percentage multiplier tricks, Cost Price vs Selling Price, markup, discount, and relative speed problems for competitive exams.',
        'difficulty': 'Beginner',
        'estimated_reading_minutes': 11,
        'prerequisites': 'Basic arithmetic and fractions',
        'definitions_json': json.dumps([
            {'term': 'Profit Percentage', 'definition': '((Selling Price - Cost Price) / Cost Price) * 100.'},
            {'term': 'Loss Percentage', 'definition': '((Cost Price - Selling Price) / Cost Price) * 100.'},
            {'term': 'Relative Speed (Opposite Direction)', 'definition': 'Speed1 + Speed2: sum of speeds when bodies travel toward each other.'},
            {'term': 'Relative Speed (Same Direction)', 'definition': '|Speed1 - Speed2|: difference of speeds when bodies travel in the same direction.'}
        ]),
        'concepts_markdown': """### The Multiplier Method for Percentages
Avoid setting up complex equations by using multiplying factors ($MF$):
- **Increase by $x\\%$:** Multiply by $(1 + \\frac{x}{100})$
  - Example: Increase by 20% $\\to$ multiply by $1.20$.
- **Decrease by $x\\%$:** Multiply by $(1 - \\frac{x}{100})$
  - Example: Decrease by 15% $\\to$ multiply by $0.85$.

### Successive Percentage Changes
If a quantity increases by $a\\%$ and then changes by $b\\%$, the net change is:
$$\\text{Net Change} = a + b + \\frac{a \\times b}{100}$$

### Time, Speed and Distance Fundamentals
$$\\text{Distance} = \\text{Speed} \\times \\text{Time}$$
- To convert **km/h to m/s**, multiply by $\\frac{5}{18}$.
- To convert **m/s to km/h**, multiply by $\\frac{18}{5}$.""",
        'step_by_step_examples': """#### Shortcut Example: Train Crossing Problem
A train 200m long is traveling at 72 km/h. How long does it take to pass a pole?

1. Convert speed to m/s: $72 \\times \\frac{5}{18} = 20 \\text{ m/s}$.
2. Total distance to clear pole = length of train = 200m.
3. Time taken = $\\frac{\\text{Distance}}{\\text{Speed}} = \\frac{200}{20} = 10 \\text{ seconds}$. Answer: 10s!""",
        'code_examples_json': json.dumps([
            {
                'title': 'Python Calculator for Aptitude Formulas',
                'language': 'python',
                'code': """def calculate_profit_loss(cost_price, selling_price):
    diff = selling_price - cost_price
    if diff > 0:
        profit_pct = (diff / cost_price) * 100
        return f"Profit: {profit_pct:.2f}%"
    elif diff < 0:
        loss_pct = (abs(diff) / cost_price) * 100
        return f"Loss: {loss_pct:.2f}%"
    return "No Profit, No Loss (Break Even)"

def relative_speed_time(dist_km, speed1_kmh, speed2_kmh, same_dir=False):
    rel_speed = abs(speed1_kmh - speed2_kmh) if same_dir else (speed1_kmh + speed2_kmh)
    time_hours = dist_km / rel_speed
    return time_hours * 60 # minutes

print(calculate_profit_loss(500, 625)) # Profit: 25.00%
print(f"Meeting time: {relative_speed_time(100, 60, 40):.1f} mins") # 60.0 mins""",
                'explanation': 'Python implementation verifying standard competitive exam aptitude formulas.'
            }
        ]),
        'key_points_json': json.dumps([
            'Profit and Loss percentages are always calculated on Cost Price (CP) unless explicitly stated otherwise.',
            'Discount percentage is always calculated on Marked Price (MP).',
            'When two trains cross each other, the distance traveled is the sum of both train lengths.',
            'Average speed for equal distances covered at speeds x and y is 2xy / (x + y).'
        ]),
        'common_mistakes_json': json.dumps([
            'Calculating profit percentage with respect to Selling Price instead of Cost Price.',
            'Forgetting to convert km/h to m/s when lengths are given in meters.',
            'Calculating average speed as the simple arithmetic mean (x + y)/2 for equal distance segments.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'If marked price is 100 and a 20% discount is applied, followed by a 10% discount, what is final price?',
                'answer': '72',
                'explanation': '100 * 0.80 = 80; then 80 * 0.90 = 72. (Not 30% off, which would be 70).'
            }
        ]),
        'related_topics': 'Ratio and Proportion, Simple & Compound Interest, Permutations & Combinations',
        'order_index': 8
    },

    # 9. Interview Preparation
    {
        'category': 'Interview Preparation',
        'subject': 'Technical Interview Prep',
        'topic': 'System Design & Technical Coding Strategy',
        'slug': 'interview-system-design-dsa-strategy',
        'title': 'Technical Interview Mastery: System Design Framework & DSA Strategy',
        'summary': 'Frameworks for crushing campus technical rounds: 4-step System Design blueprint, the STAR behavioral method, and coding interview time-management.',
        'difficulty': 'Advanced',
        'estimated_reading_minutes': 15,
        'prerequisites': 'Data structures and basic client-server architecture',
        'definitions_json': json.dumps([
            {'term': 'CAP Theorem', 'definition': 'A distributed system can deliver at most two of three properties: Consistency, Availability, and Partition Tolerance.'},
            {'term': 'Horizontal Scaling', 'definition': 'Adding more machines/nodes to your resource pool rather than upgrading CPU/RAM on a single server (Vertical Scaling).'},
            {'term': 'Load Balancer', 'definition': 'A reverse proxy distributing incoming network traffic across multiple backend application servers.'},
            {'term': 'STAR Method', 'definition': 'Behavioral interview framework: Situation, Task, Action, Result.'}
        ]),
        'concepts_markdown': """### The 4-Step System Design Interview Framework
When asked to design a large-scale system (e.g. "Design URL Shortener" or "Design WhatsApp"):

1. **Step 1: Scope & Clarify Requirements (5 mins)**
   - Functional: What core actions must users perform?
   - Non-Functional: Throughput, latency, availability (99.99%), durability.
   - Back-of-the-envelope estimations (QPS, storage over 5 years).
2. **Step 2: High-Level Architecture (10 mins)**
   - Client $\\to$ DNS $\\to$ CDN $\\to$ Load Balancer $\\to$ Web/API Servers $\\to$ Database / Cache.
3. **Step 3: Deep Dive into Core Bottlenecks (15 mins)**
   - Database schema (SQL vs NoSQL), primary keys, sharding strategies.
   - Caching layer (Redis/Memcached with LRU eviction).
4. **Step 4: Fault Tolerance & Scale (10 mins)**
   - Single points of failure (SPOF), rate limiting, replication, and telemetry.""",
        'step_by_step_examples': """#### The Coding Interview 5-Step Execution Plan:
1. **Clarify Constraints:** Ask about input size, null values, duplicates, and expected time complexity.
2. **Brute Force First:** State the naive $O(N^2)$ solution out loud to demonstrate problem comprehension.
3. **Optimize:** Identify bottlenecks using Hash Maps ($O(1)$ lookups) or Two Pointers / Binary Search.
4. **Clean Implementation:** Write modular, readable code with descriptive variable names.
5. **Dry Run:** Trace edge cases (empty input, single element, negative numbers) manually with pencil/screen before announcing completion!""",
        'code_examples_json': json.dumps([
            {
                'title': 'LRU Cache Design Pattern (Common Interview Question)',
                'language': 'python',
                'code': """from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Move accessed key to end to mark as recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Pop least recently used item (first element)
            self.cache.popitem(last=False)

cache = LRUCache(2)
cache.put(1, 100)
cache.put(2, 200)
print(cache.get(1)) # 100
cache.put(3, 300)   # Evicts key 2
print(cache.get(2)) # -1 (evicted)""",
                'explanation': 'Optimal O(1) get and put implementation using a hash map combined with a doubly linked list (OrderedDict).'
            }
        ]),
        'key_points_json': json.dumps([
            'Always communicate your thoughts continuously; interviewers evaluate your thought process over silent perfect code.',
            'Never jump immediately into writing code before verifying the problem constraints and edge cases.',
            'State both Time Complexity and Space Complexity using Big-O notation for every proposed solution.',
            'In behavioral questions, use the STAR framework with concrete metrics in the Result section.'
        ]),
        'common_mistakes_json': json.dumps([
            'Coding in complete silence without engaging the interviewer.',
            'Claiming a brute-force approach is optimal when hash tables could reduce complexity.',
            'Over-engineering a tiny system with microservices and Kafka when a simple monolithic architecture suffices.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'In a system design interview, what does the CAP theorem state regarding network partitions?',
                'answer': 'Since network partitions (P) are unavoidable in distributed physical networks, a system must choose between Consistency (C) and Availability (A).',
                'explanation': 'During a network partition, you must either reject requests (Consistent) or serve stale data (Available).'
            }
        ]),
        'related_topics': 'Distributed Caching (Redis), Database Sharding & Replication, Asynchronous Message Queues',
        'order_index': 9
    },

    # 10. Web Development
    {
        'category': 'Web Development',
        'subject': 'Web Technologies',
        'topic': 'RESTful API Architecture & HTTP Protocols',
        'slug': 'web-rest-api-architecture',
        'title': 'Architecting Modern RESTful APIs and HTTP Protocols',
        'summary': 'Master HTTP methods (GET, POST, PUT, PATCH, DELETE), status codes, idempotency, authentication (JWT vs Session), and API design best practices.',
        'difficulty': 'Beginner',
        'estimated_reading_minutes': 12,
        'prerequisites': 'Basic understanding of client-server web applications',
        'definitions_json': json.dumps([
            {'term': 'REST', 'definition': 'Representational State Transfer: an architectural style for stateless, client-server web services using standard HTTP verbs.'},
            {'term': 'Idempotence', 'definition': 'An HTTP method is idempotent if executing it multiple times produces the identical side-effect on the server as executing it once.'},
            {'term': 'JWT (JSON Web Token)', 'definition': 'A compact, URL-safe means of representing claims to be transferred between two parties, digitally signed with HMAC or RSA.'},
            {'term': 'CORS', 'definition': 'Cross-Origin Resource Sharing: browser security mechanism controlling access to resources outside the originating domain.'}
        ]),
        'concepts_markdown': """### Standard HTTP Methods & Idempotency
- **GET (Idempotent & Safe):** Retrieve a resource representation. No server state mutation.
- **POST (Not Idempotent):** Create a new subordinate resource.
- **PUT (Idempotent):** Replace the entire resource at the target URL.
- **PATCH (Not strictly Idempotent):** Apply partial modifications to a resource.
- **DELETE (Idempotent):** Remove the target resource.

### Essential HTTP Status Code Ranges
- **2xx Success:** `200 OK`, `201 Created`, `204 No Content`
- **3xx Redirection:** `301 Moved Permanently`, `304 Not Modified`
- **4xx Client Error:** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `429 Too Many Requests`
- **5xx Server Error:** `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`""",
        'step_by_step_examples': """#### RESTful Resource URL Design Best Practices:
- **Good:** `GET /api/v1/students` (plural nouns, clean versioning)
- **Good:** `GET /api/v1/students/42/quizzes` (nested relationship)
- **Bad:** `POST /api/getStudent` (do NOT use verbs in URLs; HTTP verbs define the action!)""",
        'code_examples_json': json.dumps([
            {
                'title': 'RESTful API Endpoint with Validation in Flask',
                'language': 'python',
                'code': """from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample in-memory store
STUDENTS = {1: {"name": "Aarav", "grade": "A"}}

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = STUDENTS.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"id": student_id, **student}), 200

@app.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json() or {}
    if 'name' not in data:
        return jsonify({"error": "Field 'name' is required"}), 400
    new_id = max(STUDENTS.keys(), default=0) + 1
    STUDENTS[new_id] = {"name": data['name'], "grade": data.get('grade', 'B')}
    return jsonify({"id": new_id, **STUDENTS[new_id]}), 201""",
                'explanation': 'Illustrates proper HTTP verbs, JSON body validation, status codes (200, 201, 400, 404), and error formatting.'
            }
        ]),
        'key_points_json': json.dumps([
            'REST APIs should be stateless: every request must contain all credentials needed to fulfill it.',
            'Use nouns for resource URIs and HTTP methods for actions.',
            'Always return semantic HTTP status codes rather than returning 200 OK with error messages inside the body.',
            'Secure endpoints using rate limiting and authorization headers.'
        ]),
        'common_mistakes_json': json.dumps([
            'Using GET requests to delete or update data on the server.',
            'Returning 200 OK when an exception occurred on the server.',
            'Leaking database stack traces and sensitive error details in 500 error responses.'
        ]),
        'practice_questions_json': json.dumps([
            {
                'question': 'Is the HTTP DELETE method considered idempotent?',
                'answer': 'Yes, deleting an already deleted resource multiple times leaves the server in the same state.',
                'explanation': 'Even if subsequent calls return 404 Not Found, the server state remains unchanged.'
            }
        ]),
        'related_topics': 'WebSockets, GraphQL, OAuth 2.0, Microservices Communication',
        'order_index': 10
    }
]

def seed_learning_resources(database):
    """
    Idempotently seeds the 10 production educational resources.
    Preserves existing user progress records and never duplicates rows.
    """
    created_count = 0
    updated_count = 0

    for item in INITIAL_RESOURCES:
        existing = LearningResource.query.filter_by(slug=item['slug']).first()
        if existing:
            # Update fields to ensure latest verified content
            for key, val in item.items():
                setattr(existing, key, val)
            updated_count += 1
        else:
            new_resource = LearningResource(**item)
            database.session.add(new_resource)
            created_count += 1

    database.session.commit()
    print(f"Learning Resources sync: {created_count} created, {updated_count} updated.")
