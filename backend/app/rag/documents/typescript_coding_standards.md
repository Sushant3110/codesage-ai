# TypeScript Strict Typing and Defensive Engineering Guidelines

Source URL: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html
Document Title: TypeScript Strict Typing and Defensive Engineering Guidelines
Language: typescript

## Type Safety and Strictness

### Avoiding `any` and Preferring `unknown`
Avoid the use of the `any` type, as it disables all compile-time type checking and propagates unsafety across the codebase.
When dealing with truly unknown external data (e.g. API responses, JSON parse results), use `unknown` and perform runtime narrowing or schema validation (using tools like Zod or Typebox) before accessing properties.

### Strict Compiler Flags
Ensure `strict: true` is enabled in `tsconfig.json`. This enables `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, and `strictBindCallApply`.
Never use non-null assertions (`!`) unless an invariant has been verified immediately prior.

## Narrowing and Discriminated Unions

### Type Guards and Discriminated Unions
Model distinct domain states using discriminated unions with a common literal discriminator tag (e.g. `kind: 'success' | 'error'`).
Use custom type guards (`value is Type`) or built-in operators (`typeof`, `instanceof`, `'property' in obj`) to safely narrow union types before usage.

### Exhaustive Pattern Matching
When switching over discriminated union variants, use the `never` type in the `default` branch to ensure that adding new union members causes compile-time errors if not handled.

## Interface and Type Architecture

### Interface vs Type Aliases
Prefer `interface` for defining public contracts, object shapes, and extensible API declarations.
Use `type` aliases for unions, primitives, tuples, and complex mapped/conditional types.
Mark immutable properties with `readonly` modifiers to enforce functional integrity and prevent unexpected mutations.
