# PEP 8 — Style Guide for Python Code

Source URL: https://peps.python.org/pep-0008/
Document Title: PEP 8 Style Guide for Python Code
Language: python

## Code Layout and Formatting

### Indentation and Line Length
Use 4 spaces per indentation level. Never mix tabs and spaces for indentation; Python disallows mixing tabs and spaces in modern versions.
Limit all lines to a maximum of 79 characters for code, and 72 characters for docstrings or comments.
Continuation lines should align wrapped elements either vertically using Python's implicit line joining inside parentheses, brackets and braces, or using a hanging indent.
When using a hanging indent, there should be no arguments on the first line and further indentation should be used to clearly distinguish itself as a continuation line.

### Blank Lines
Surround top-level function and class definitions with two blank lines.
Method definitions inside a class are surrounded by a single blank line.
Extra blank lines may be used sparingly to separate groups of related functions or logical sections within a function.

### Imports
Imports should usually be on separate lines:
```python
import os
import sys
```
Imports should always be placed at the top of the file, just after any module comments and docstrings, and before module globals and constants.
Group imports in the following order:
1. Standard library imports
2. Related third party imports
3. Local application/library specific imports
Put a blank line between each group of imports. Avoid wildcard imports (`from module import *`) as they make it unclear which names are present in the namespace.

## Naming Conventions

### Function and Variable Names
Function names should be lowercase, with words separated by underscores as necessary to improve readability (snake_case).
Variable names follow the same convention as function names.
Always use `self` for the first argument to instance methods.
Always use `cls` for the first argument to class-methods.

### Class and Exception Names
Class names should normally use the CapWords convention (also called PascalCase or UpperCamelCase).
Because exceptions should be classes, the class naming convention applies here. However, you should use the suffix `Error` on your exception names if the exception is an error.

### Constants and Private Attributes
Constants are usually defined on a module level and written in all capital letters with underscores separating words (UPPER_CASE_WITH_UNDERSCORES).
Use one leading underscore only for non-public methods and instance variables (`_single_leading_underscore`).
Use two leading underscores to invoke Python's name mangling rules when naming an attribute to avoid name clashes in subclasses (`__double_leading_underscore`).

## Programming Recommendations

### Comparisons and None
Comparisons to singletons like `None` should always be done with `is` or `is not`, never the equality operators (`==` or `!=`).
Write `if x is not None:` rather than `if not x is None:`.
Do not compare boolean values to `True` or `False` using `==`. Write `if greeting:` instead of `if greeting == True:`.

### Exception Handling
When catching exceptions, mention specific exceptions whenever possible instead of using a bare `except:`.
A bare `except:` clause will catch `SystemExit` and `KeyboardInterrupt` exceptions, making it harder to interrupt a program with Control-C, and can disguise other problems.
Use `raise ... from ...` for exception chaining to preserve original tracebacks.
Keep try blocks minimal: limit the `try` clause to the absolute minimum amount of code necessary to avoid masking unexpected bugs.
