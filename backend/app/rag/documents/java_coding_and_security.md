# Java Coding Standards and OWASP Security Guidelines

Source URL: https://owasp.org/www-project-top-ten/
Document Title: Java Coding Standards and OWASP Security Guidelines
Language: java

## Null Safety and Defensive Programming

### Avoiding NullPointerExceptions
Null pointer exceptions remain the most frequent source of runtime crashes in Java applications.
Use defensive null checking or modern Java `Optional<T>` idioms for values that may be legitimately absent.
Avoid returning raw `null` collections or arrays; prefer returning empty collections such as `Collections.emptyList()` or `Collections.emptyMap()`.
Enforce method preconditions using `Objects.requireNonNull(arg, "arg must not be null")` at public API boundaries.

### Defensive Copying
When accepting or returning mutable objects (such as `Date`, arrays, or mutable collections), create defensive copies to prevent callers from corrupting internal class invariants.
Prefer immutable collections (`List.of()`, `Set.of()`) introduced in modern Java (Java 9+).

## Resource Management and Exception Handling

### Try-With-Resources Statement
Always use the `try-with-resources` statement for any resource implementing `AutoCloseable` (such as `InputStream`, `OutputStream`, `Connection`, `PreparedStatement`, `ResultSet`, and `Reader`).
Manual closing inside a `finally` block is error-prone because exceptions thrown during close can suppress the original exception or leak resources if an intermediate statement fails.

### Exception Hygiene
Never catch generic `Throwable` or swallow exceptions silently in empty catch blocks (`catch (Exception e) {}`).
Always log the exception stack trace or wrap and rethrow a domain-specific exception.
Avoid using exceptions for control flow.

## OWASP Java Security Guidelines

### SQL Injection Prevention
Never concatenate untrusted user input directly into SQL strings. Always use `PreparedStatement` with parameterized placeholders (`?`) or modern ORMs (JPA/Hibernate) with parameter binding.
Never construct dynamic query clauses by formatting strings with raw parameters.

### Insecure Deserialization
Do not use Java native object deserialization (`ObjectInputStream.readObject()`) on untrusted data.
Native deserialization allows remote code execution (RCE) via gadget chains. Use safe serialization formats like JSON with validated schemas and strict type bindings.

### XML External Entity (XXE) Prevention
When parsing XML documents with `DocumentBuilderFactory` or `SAXParserFactory`, explicitly disable external DTDs and entities:
`factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);`

## Concurrency and Thread Safety

### Synchronization and Volatile
Avoid manual synchronization on publicly accessible objects or `String` literals.
Use thread-safe data structures from `java.util.concurrent` (such as `ConcurrentHashMap`, `CopyOnWriteArrayList`, and atomic classes like `AtomicInteger`) instead of naive method-level synchronization.
Mark shared state variables `volatile` only when memory visibility without atomic compounding is needed.
