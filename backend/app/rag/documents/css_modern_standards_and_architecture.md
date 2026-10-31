# Modern CSS Layout, Performance, and Security Guidelines

Source URL: https://developer.mozilla.org/en-US/docs/Learn/CSS
Document Title: Modern CSS Layout, Performance, and Security Guidelines
Language: css

## Modern Layout and Responsive Design

### Flexbox and CSS Grid
Use CSS Grid for two-dimensional page structure and macroscopic component layouts.
Use Flexbox for one-dimensional alignments, navigation bars, toolbars, and content distribution along a single axis.
Avoid outdated layout techniques such as `float` positioning or `table-cell` hacks for layout structure.

### Responsive Breakpoints and Fluid Typography
Design responsive layouts using a mobile-first approach with `min-width` media queries.
Use relative units (`rem`, `em`, `%`, `ch`, `clamp()`) rather than fixed `px` values for typography and container sizing to respect user browser font scaling preferences.
Ensure images and media containers have `max-width: 100%` and `height: auto` to prevent horizontal viewport overflow.

## Maintainability and Specificity Management

### Specificity Control and Architecture
Avoid using `!important` to override styling conflicts. High specificity declarations create brittle stylesheets that are difficult to maintain or theme.
Keep CSS selector specificity as low and flat as possible by styling reusable classes rather than deep tag hierarchies (e.g. avoid `.sidebar div ul li a`).
Leverage CSS custom properties (CSS variables `--primary-color: #6366f1;`) for design tokens, color schemes, and theme switching.

## CSS Security and Performance

### Defensive CSS and Injection Risks
Do not allow untrusted user input into CSS property values or `url()` declarations.
Malicious CSS can be used to trigger unintended external requests (CSS data exfiltration) or execute scripts via legacy features like IE `expression()`.
Sanitize any user-customizable color or font settings before embedding them into inline style tags.

### Performance and Animations
Animate only hardware-accelerated properties (`transform` and `opacity`) using `transition` and CSS `@keyframes`.
Avoid animating layout-triggering properties (`width`, `height`, `margin`, `top`, `left`) inside scroll or hover events, as they trigger costly browser reflows and repaints.
Respect user motion accessibility preferences using the `@media (prefers-reduced-motion: reduce)` media query.
