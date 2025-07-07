# 🧠 copilot-instructions.md

## 👨‍💻 General Coding Philosophy

- Write clean, readable, and modular code.
- Follow best practices for the language and framework.
- Prioritize simplicity and maintainability over clever tricks.
- Use meaningful variable, method, and file names.
- Avoid unnecessary dependencies or boilerplate unless explicitly needed.

---

## ✅ Output Expectations

- Always generate only the code unless otherwise requested.
- Code must be:
  - Runnable and self-contained
  - Easy to test and debug
  - Properly structured for the project type
- Include inline comments for complex logic or non-obvious decisions.
- Avoid "Hello World" or placeholder code unless asked.

---

## 📦 Project Structure

- Use standard project layout:
  - `/src`, `/tests`, `/utils`, `/config`, etc.
- Place reusable logic in separate modules or functions.
- Group related functionality appropriately (e.g., `services`, `models`, `controllers`).

---

## 🧪 Testing

- Add unit tests for each function or module created.
- Use mocks/stubs for I/O, external APIs, and databases.
- Follow the AAA pattern: Arrange, Act, Assert.
- Tests go in a `tests/` directory or alongside the source file (e.g., `filename_test.py`).

---

## 🔧 Style and Standards

- Follow project-specific linters and formatters:
  - Python: PEP8 + Black
  - JavaScript: ESLint + Prettier
  - Java: Oracle Java Guidelines
- Use type annotations and docstrings where supported.
- Avoid long functions — break logic into smaller pieces.

---

## 💡 Prompt Handling

Expect prompts to include:
- Building features (e.g., UI components, APIs, CLI tools)
- Parsing files or handling data
- Writing test automation scripts
- Refactoring or improving performance
- Explaining or documenting existing code

---

## 📎 Prompt Examples

| ❌ Bad Prompt                  | ✅ Good Prompt |
|-------------------------------|----------------|
| "Write a function"            | "Write a function in Python that takes a list of integers and returns only the even numbers using list comprehension." |
| "Fix this"                    | "Fix the null pointer exception in the `getUserDetails()` method when no user is found." |
| "Create test"                 | "Write a unit test using JUnit 5 for the `calculateTax()` method in `TaxService.java`." |

---

## 🛑 Avoid

- Hardcoding values unless explicitly requested
- Writing code that relies on external files, APIs, or services unless prompted
- Making assumptions about business logic
- Adding unrelated functionality

---

## 🌍 Language-Specific Add-ons

### Python
- Use type hints: `def func(x: int) -> str:`
- Use `with open(...)` for file I/O
- Prefer `logging` over `print`

### Java
- Use `private`, `public`, `protected` appropriately
- Follow class/method naming conventions
- Keep methods small and testable

### JavaScript/TypeScript
- Prefer `const` and `let`, avoid `var`
- Use `async/await` for async code
- Include error handling for all Promises

---

## 🤖 AI Agent Behavior

This AI assistant should:
- Respect existing code style and structure
- Minimize unnecessary output
- Focus on solving the user's actual intent
- Add comments only when logic needs explanation
- Avoid assumptions — ask for clarification when the prompt is ambiguous

---