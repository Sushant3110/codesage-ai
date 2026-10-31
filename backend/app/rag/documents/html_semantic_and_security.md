# HTML5 Semantic Standards, Accessibility, and Security Guidelines

Source URL: https://www.w3.org/WAI/standards-guidelines/wcag/
Document Title: HTML5 Semantic Standards, Accessibility, and Security Guidelines
Language: html

## Cross-Site Scripting (XSS) Prevention

### Escaping and Safe Attributes
Never insert untrusted user input directly into HTML tags, attributes, or inline event handlers (such as `onload`, `onclick`, `onerror`).
Avoid using `href="javascript:..."` links, as they execute arbitrary script when clicked.
For user-uploaded URLs, validate the protocol strictly (allow only `http:`, `https:`, or `mailto:`).

### Secure Resource Loading
When linking external stylesheets, scripts, or fonts from third-party CDNs, include Subresource Integrity (SRI) attributes (`integrity="..."` and `crossorigin="anonymous"`).
Ensure all `<form>` elements transmitting sensitive credentials or tokens specify `method="POST"` and use HTTPS endpoints.

## Semantic Markup and Document Structure

### Proper Semantic Elements
Use semantic HTML5 container elements (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`) instead of generic unsemantic `<div>` containers.
Semantic elements provide landmarks for search engines, assistive technologies, and screen readers.
Ensure there is exactly one `<h1>` per page representing the principal page topic, with an unbroken heading hierarchy (`h1` -> `h2` -> `h3`).

### Document Metadata
Every HTML document must begin with a proper `<!DOCTYPE html>` declaration and an `<html>` tag with a valid `lang` attribute (e.g. `<html lang="en">`).
Include `<meta charset="utf-8">` and `<meta name="viewport" content="width=device-width, initial-scale=1.0">` inside the `<head>` section.

## Web Accessibility (WCAG 2.1)

### Image Text Alternatives and ARIA
Every `<img>` element must have an `alt` attribute. Provide descriptive text for informative images; provide empty `alt=""` for purely decorative images.
Use standard interactive HTML elements (`<button>`, `<a href="...">`) rather than attaching click handlers to `<div>` or `<span>`.
Associate form controls with `<label for="...">` elements to ensure screen readers can announce input fields clearly.
