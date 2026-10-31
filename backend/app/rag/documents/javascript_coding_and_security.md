# Modern JavaScript Quality and Security Guidelines

Source URL: https://owasp.org/www-community/attacks/xss/
Document Title: Modern JavaScript Quality and Security Guidelines
Language: javascript

## Cross-Site Scripting (XSS) Mitigation

### DOM-Based XSS Prevention
Never assign unsanitized user-controllable input directly to dangerous DOM sinks such as `element.innerHTML`, `outerHTML`, `document.write()`, or `eval()`.
Always use safe DOM APIs such as `element.textContent`, `element.setAttribute()`, or sanitize HTML content with a trusted library like DOMPurify before inserting it into the DOM tree.
Avoid `javascript:` pseudo-protocols in `href` and `src` attributes.

### Contextual Output Encoding
Ensure all dynamic values reflected into HTML elements, attributes, or script contexts are encoded according to their specific output context (HTML body, attribute, URL parameter, or JavaScript string).

## Asynchronous Safety and Error Handling

### Promise Error Handling and Unhandled Rejections
Always handle Promise rejections either by appending `.catch()` handlers or wrapping `await` calls in `try...catch` blocks.
Unhandled promise rejections can cause node processes to crash or leave client applications in unrecoverable loading states.
Avoid `async` functions passed directly to event listeners without error boundaries.

### Race Conditions in Async Operations
When triggering concurrent asynchronous operations, cancel stale requests or verify that the active view or component state is still mounted when the Promise resolves.

## Prototype Pollution and Object Safety

### Defending Against Prototype Pollution
When merging or cloning nested objects, validate object keys to ensure they do not contain `__proto__`, `constructor`, or `prototype`.
Freeze prototypes or use `Object.create(null)` for key-value dictionary maps that receive untrusted user keys.

## Code Quality and Scope Hygiene

### Strict Equality and Variable Declaration
Always use strict equality (`===` and `!==`) to prevent unexpected type coercion bugs common with loose equality (`==` and `!=`).
Always declare variables using `const` by default, and `let` only when reassignment is required. Never use `var` due to function scoping and hoisting hazards.
Avoid global variable pollution and adhere to strict mode (`'use strict';`).
