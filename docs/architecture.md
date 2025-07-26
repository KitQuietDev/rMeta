# 🏗️ rMeta Architecture Overview

rMeta isn’t monolithic — it’s modular, intentional, and designed to be legible even under a magnifying glass. This guide is a bird’s eye tour of how the major parts fit together, why they were built this way, and where they might evolve.

## 📦 Core Components


| Module            | Description                                                                       | Notes                                                 |
| ------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `app.py`          | Entry point. Manages CLI args, sets up environment, invokes handlers.             | Think of it as the conductor, light but critical.     |
| `handlers/`       | Filetype-specific logic for parsing, scrubbing, and postprocessing.               | Each file is a mini-expert in its format.             |
| `postprocessors/` | Optional final tweaks after core scrubbing (deduping, ordering, pretty-printing). | Composable extras, not assumptions.                   |
| `utils/`          | Helper functions used across modules (logging, hashing, error patterns).          | Low-level glue.                                       |
| `workspace/`      | Temporary scratch space for processing docs before final output.                  | Destroyed after timeout in`.env` (user configurable). |

## 🧭 Data Flow Overview

User Input
→ `app.py`
→ Select Handler Based on Filetype
→ Scrubbing Logic
→ Optional Postprocessors
→ Workspace Output

The system is linear with graceful fallback. If a handler fails, rMeta logs verbosely and skips the file — no silent errors.

## 🔐 Privacy-First Design

* No external calls: all processing is local.
* SHA256 hashes used to identify sensitive content without revealing it.
* Temporary files auto-destroyed after a user-defined timeout (set in `.env`). Workspace isn’t preserved unless explicitly configured.
* Optional GPG integration for encrypting outputs or signing logs.

The guiding principle: **You control your data. Always.**

## 🧰 Modularity and Extensibility

* Want to support a new format? Drop a new handler in `handlers/` and follow the pattern.
* Postprocessors are optional and chainable — plug in only what you need.
* Logging is consistent and designed to integrate easily into broader systems.

## 🛠️ Philosophy Under the Hood

This isn’t a black box. Every module earns its existence.

We favor clarity over cleverness, separation of concern over abstraction guilt, and graceful failure over brittle success. When you read the code, it should explain itself — not audition for a job interview.
