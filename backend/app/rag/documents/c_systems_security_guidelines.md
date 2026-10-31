# ISO C Systems Safety and Secure Coding Standards

Source URL: https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard
Document Title: ISO C Systems Safety and Secure Coding Standards
Language: c

## Memory Management and Buffer Safety

### Preventing Buffer Overflows
Never use unbounded string copy and input functions such as `strcpy()`, `strcat()`, `gets()`, and `sprintf()`.
Always use bounds-checked alternatives such as `snprintf()`, `strncpy()` (with explicit null-termination guarantee), or `strlcpy()`/`strlcat()` where available.
Always verify destination buffer capacities against source string lengths before performing copies.

### Dynamic Allocation Safety
Always verify that `malloc()`, `calloc()`, or `realloc()` returned a non-null pointer before dereferencing.
Every dynamically allocated memory block must have exactly one corresponding call to `free()`.
After freeing a pointer, immediately set it to `NULL` to prevent dangling pointer dereferences and use-after-free vulnerabilities.

## Pointer Safety and Undefined Behavior

### Null Pointer Dereference and Initialization
Always initialize pointer variables upon declaration, setting them to `NULL` if no valid target address is available.
Never dereference a pointer without checking for `NULL` unless an explicit caller contract or prior check guarantees non-nullness.

### Out-of-Bounds Indexing
Always enforce array boundary checks when iterating or accessing array elements.
Ensure integer loop counters match the array dimension type (prefer `size_t` for indexing to avoid negative index vulnerabilities).

## Integer Arithmetic and Format String Safety

### Integer Overflow Prevention
Check for arithmetic overflow and underflow before performing additions, subtractions, or multiplications that affect buffer sizes or memory allocations (e.g. `size * sizeof(element)`).
An integer overflow in an allocation size check often results in undersized buffer allocation followed by severe heap corruption.

### Format String Vulnerabilities
Never pass user-controlled strings as the format argument to `printf()`, `fprintf()`, `sprintf()`, or `syslog()`.
Always pass an explicit format specifier: `printf("%s", user_str);` rather than `printf(user_str);`.
