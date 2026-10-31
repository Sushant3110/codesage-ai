# Defensive Programming and Resource Safety in Python

Source URL: https://docs.python.org/3/tutorial/errors.html
Document Title: Python Defensive Programming and Robustness Guide
Language: python

## Resource Management

### Context Managers and With Statements
Always use `with` statements (context managers) when managing system resources such as files, database connections, locks, or network sockets.
Context managers guarantee that `__exit__` is executed and resources are properly closed, even if an exception is raised inside the block.
```python
# Bad practice:
f = open("data.txt", "r")
content = f.read()
f.close()  # Skipped if f.read() raises an error!

# Good practice:
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
```
For custom resources, use the `@contextlib.contextmanager` decorator or implement `__enter__` and `__exit__`.

## Function Arguments and State

### Mutable Default Arguments
Never use mutable objects (such as lists `[]`, dictionaries `{}`, or custom instances) as default parameter values in function signatures.
Default arguments in Python are evaluated once when the function definition is executed, not each time the function is called.
Mutating a default parameter modifies that single object across subsequent function calls, creating subtle state leaks and shared state bugs.
```python
# Insecure / Buggy:
def append_item(item, target_list=[]):
    target_list.append(item)
    return target_list

# Correct pattern:
def append_item(item, target_list: list | None = None):
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list
```

## Type Checking and Input Validation

### Defensive Type Checks and Preconditions
Functions should validate preconditions and argument types early, failing fast if unexpected data is provided.
Use `isinstance()` checks or Pydantic validation models for input data coming across system boundaries.
When working with dictionaries, prefer `dict.get(key, default)` over direct indexing `dict[key]` unless the key is strictly required to be present, in which case `KeyError` should be caught or documented.

## Concurrency and Thread Safety

### Race Conditions and Shared State
Python's Global Interpreter Lock (GIL) does not prevent race conditions.
Operations that appear atomic in Python (such as checking a condition and then updating state) are not thread-safe.
Use `threading.Lock` or `threading.RLock` to synchronize access to shared data across threads.
In asynchronous code using `asyncio`, use `asyncio.Lock` to coordinate tasks and prevent interleaved state modifications during `await` pauses.
