# openmneme

> **Your AI mneme. The science of memory, open-sourced.**

[![npm version](https://img.shields.io/npm/v/openmneme.svg)](https://www.npmjs.com/package/openmneme)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/alanpaul1969/openmneme/blob/main/LICENSE)
[![npm provenance](https://img.shields.io/badge/npm-provenance-success)](https://docs.npmjs.com/generating-provenance-statements)

## What is OpenMneme?

**Mneme** (μνήμη) — Greek for *memory*; in ancient Greek medicine, the first of three functions of the mind (reception, retention, recall). In neuroscience, Richard Semon's 1921 term for an *engram* — a memory trace.

OpenMneme is an open-source AI memory layer for personal knowledge management. It draws from neuroscience, philosophy, and the practical reality of working with LLMs over years of accumulated context.

## Status

**Reserved namespace — project coming soon.** This package reserves the `openmneme` name on npm and provides a placeholder module. Real primitives will land in 0.1.0+.

## Install

```bash
npm install openmneme
# or
pnpm add openmneme
# or
yarn add openmneme
```

## Usage

```js
const openmneme = require('openmneme');

console.log(openmneme.meta);
// {
//   name: 'openmneme',
//   version: '0.0.1',
//   status: 'reserved',
//   homepage: 'https://github.com/alanpaul1969/openmneme',
//   license: 'Apache-2.0',
// }

console.log(openmneme.mnemonic);  // 'μνήμη'
```

## Roadmap

Confirmed primitives being explored:

- **Mnemonic agent loop** — agent that retains across sessions
- **Provenance DAG** — append-only audit trail for every claim
- **Reviewer gate** — blind adversarial audit of agent output
- **Recursive Language Model (RLM)** — artifact-by-reference to avoid context blow-up
- **Plan mode** — read-only planning before committing to actions

## Links

- **GitHub:** https://github.com/alanpaul1969/openmneme
- **PyPI:** https://pypi.org/project/openmneme/
- **Inspiration:** [OpenScience](https://github.com/synthetic-sciences/openscience)

## License

Apache-2.0 © 2026 Alan Huang
