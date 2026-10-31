# OWASP Python Security Guidelines

Source URL: https://cheatsheetseries.owasp.org/cheatsheets/Python_Security_Cheat_Sheet.html
Document Title: OWASP Python Security Cheat Sheet
Language: python

## Injection Prevention

### Command Injection
Executing system commands with user-controlled input can lead to command injection.
Never pass unsanitized user input to `os.system()`, `os.popen()`, or `subprocess.Popen(..., shell=True)`.
If system interaction is required, use `subprocess.run()` with argument lists and `shell=False`:
```python
# Insecure:
os.system(f"ping -c 1 {user_ip}")

# Secure:
subprocess.run(["ping", "-c", "1", user_ip], shell=False, check=True)
```
Do not invoke shell interpreters when standard library functions can accomplish the same task safely.

### SQL and Query Injection
Never concatenate or format strings to construct SQL queries with untrusted variables.
Always use parameterized queries or an ORM with bound parameters.
```python
# Insecure:
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")

# Secure:
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```
This applies to raw SQLite, PostgreSQL, MySQL queries, as well as NoSQL queries where JSON query operators might be injected.

## Insecure Deserialization

### Safe vs Unsafe Deserializers
The Python `pickle` module is not secure against erroneous or maliciously constructed data.
Never unpickle data received from an untrusted source or that could have been tampered with.
Remote code execution can be achieved during unpickling via `__reduce__`.
Prefer safe serialization formats such as JSON, Protocol Buffers, or MessagePack.
```python
# Insecure:
data = pickle.loads(user_input)

# Secure:
data = json.loads(user_input)
```
When using YAML, always use `yaml.safe_load()` instead of `yaml.load()` to prevent arbitrary object instantiation.

## Cryptography and Secrets Management

### Hardcoded Credentials
Secrets, tokens, API keys, database passwords, and cryptographic keys must never be hardcoded in source code or committed to version control.
Use environment variables, secret managers (such as AWS Secrets Manager, HashiCorp Vault), or configuration files that are excluded from version control via `.gitignore`.
```python
# Insecure:
SECRET_KEY = "super-secret-key-12345"

# Secure:
SECRET_KEY = os.environ.get("APP_SECRET_KEY")
```

### Insecure Randomness and Cryptography
Do not use the standard `random` module for security-sensitive purposes (e.g., token generation, session IDs, salt generation, password reset tokens).
The `random` module produces pseudo-random numbers that are predictable.
Use `secrets` or `os.urandom()` for cryptographically secure pseudo-random numbers:
```python
import secrets
token = secrets.token_hex(32)
```
Use modern cryptographic algorithms such as AES-GCM or ChaCha20-Poly1305 for symmetric encryption and Argon2id or bcrypt for password hashing. Avoid MD5 and SHA1 for security controls.

## File and Path Traversal

### Path Traversal Defense
When constructing file paths from user input, an attacker can use `../` directory traversal sequences to access sensitive files outside the target directory.
Always canonicalize paths using `os.path.realpath()` or `pathlib.Path.resolve()` and verify that the target path begins with the allowed base directory:
```python
base_dir = Path("/safe/directory").resolve()
target_file = (base_dir / user_supplied_filename).resolve()
if not target_file.is_relative_to(base_dir):
    raise PermissionError("Access denied: path traversal attempt")
```
Validate filenames against strict whitelists of allowed characters (e.g., alphanumeric, underscores, hyphens, and single dots).
