# Modern C++ Core Guidelines and Memory Safety Standards

Source URL: https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines
Document Title: Modern C++ Core Guidelines and Memory Safety Standards
Language: cpp

## Resource Management (RAII) and Smart Pointers

### Resource Acquisition Is Initialization (RAII)
Encapsulate every resource (heap memory, file handles, sockets, mutex locks) inside an RAII owner object.
Avoid manual `new` and `delete` expressions in modern application code.
Use `std::unique_ptr` for exclusive resource ownership and `std::shared_ptr` only when shared ownership is genuinely required.
Construct smart pointers using `std::make_unique` and `std::make_shared` to guarantee exception safety and prevent memory leaks during construction.

### Avoiding Raw Pointer Ownership
Never use raw pointers (`T*`) for managing ownership or deletion.
Raw pointers should only represent non-owning references or observation points, and their lifetime must not exceed that of the owning object.
Prefer passing parameters by `const &` (const reference) or `std::string_view` / `std::span` for efficient, non-owning views.

## Exception Safety and Const Correctness

### Exception Guarantees
Strive for the strong exception guarantee (commit-or-rollback) or at least the basic guarantee (no resource leaks, invariants preserved) in state-mutating operations.
Mark functions that cannot throw with `noexcept` (especially move constructors, move assignment operators, swap functions, and destructors). Destructors must never throw exceptions.

### Const Correctness
Declare member functions `const` if they do not modify the observable state of the object.
Mark variables `const` or `constexpr` whenever their values do not change after initialization.

## Container Safety and Modern Idioms

### Bounds Checking with Containers
Prefer `std::vector::at()` or explicit size checks when index bounds cannot be statically proven.
Avoid C-style arrays (`T arr[N]`); prefer `std::array<T, N>` or `std::vector<T>`.
Be cautious of iterator invalidation when modifying standard library containers inside loops.

### Move Semantics and Perfect Forwarding
Implement move semantics using `std::move` to transfer ownership of heavy resources without unnecessary deep copies.
Avoid using an object after it has been moved from, except to assign to it or destroy it.
