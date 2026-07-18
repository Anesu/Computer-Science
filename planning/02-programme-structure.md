# Programme Structure — Open CS Degree 2026

Four years, eight semesters, ~117 credits of defined courses (plus free-elective
headroom to ~120). Spine: ACM/IEEE CS2023 knowledge areas — see
`03-coverage-matrix.md` for the coverage proof. Machine-readable form with all
prerequisite edges: `curriculum/pathway.yaml` (validated in CI).

Course descriptions here are one-liners; full one-page specs are the Phase 2
deliverable. AI-assisted software practice (prompting, agentic workflows, code
review of AI output) is woven into every programming course from CS1101 onward,
not siloed into one course.

## Year 1 — Foundations

**Semester 1**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS1101 | Programming Fundamentals | 4 | Python; problems → programs; AI-assisted practice from day one, including when *not* to trust the tool |
| MA1101 | Discrete Mathematics | 4 | Logic, proofs, sets, combinatorics, graphs — the language of the whole degree |
| CS1102 | Computer Systems Fundamentals | 4 | From transistors to a running program (Nand2Tetris-style); how computers actually work |
| MA1102 | Calculus for Computing | 3 | Single-variable calculus + intro multivariable, taught toward ML and analysis needs |

**Semester 2**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS1201 | Data Structures & Algorithms I | 4 | Core structures, complexity, implementation from scratch |
| CS1202 | Systems Programming | 4 | C and Rust; memory, pointers, undefined behavior, memory safety as a modern core competency |
| MA1201 | Linear Algebra | 3 | Vectors to SVD, computationally oriented |
| CS1203 | Software Construction & Tooling | 4 | Git, testing, debugging, build systems, web fundamentals, working with AI agents professionally |

## Year 2 — Core

**Semester 3**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS2101 | Algorithm Design & Analysis | 4 | Paradigms, proofs of correctness, NP-completeness in practice |
| CS2102 | Computer Architecture | 4 | Pipelines, caches, memory hierarchy, why performance behaves the way it does |
| MA2101 | Probability & Statistics for CS | 3 | Probability, inference, and the statistics needed to reason about ML and experiments |
| CS2103 | Software Engineering | 4 | Team project course: requirements, design, code review, CI/CD, engineering with AI teammates |

**Semester 4**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS2201 | Operating Systems | 4 | Processes, scheduling, memory, filesystems, concurrency — with a build-an-OS-component lab spine |
| CS2202 | Data Management & Databases | 4 | Relational model, SQL, transactions, plus modern NoSQL/streaming context |
| CS2203 | Theory of Computation | 3 | Automata, computability, complexity — what computers cannot do |
| CS2204 | HCI & Visual Computing | 3 | Human-computer interaction, interface design, and CS2023 graphics core |

## Year 3 — Advanced core, tracks open

**Semester 5**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS3101 | Computer Networks | 4 | Internet architecture, protocols, sockets — build real networked systems |
| CS3102 | Machine Learning | 4 | Classical ML through deep learning foundations, mathematically grounded |
| CS3103 | Programming Languages | 3 | Semantics, type systems, functional programming, interpreters |
| CS3104 | Security Fundamentals | 3 | Threat modeling, common vulnerabilities, cryptography basics, defensive mindset — core, not elective |

**Semester 6**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS3201 | Parallel & Distributed Computing | 4 | Concurrency at scale, consensus, fault tolerance, data-intensive system design |
| CS3202 | LLM Application Engineering | 3 | Building on foundation models: RAG, agents, evals, safety — the 2026 core competency |
| CS3203 | Large-Scale Software & DevOps | 3 | Cloud infrastructure, observability, SRE practice, MLOps context |
| — | Track elective 1 | 3 | |

## Year 4 — Specialization and capstone

**Semester 7**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS4101 | Computing, Ethics & Society | 3 | CS2023 SEP capstone-level treatment: AI ethics, privacy, professional responsibility |
| CS4901 | Capstone I | 4 | Substantial original project, proposal through working prototype |
| — | Track electives 2–3 | 6 | |

**Semester 8**

| ID | Course | Cr | Notes |
|---|---|---|---|
| CS4902 | Capstone II | 5 | Completion, evaluation, and public defense of the capstone |
| — | Track electives 4–5 | 6 | |
| — | Free elective | 3 | Any track or general elective |

## Tracks (choose one; 5 courses)

**AI / Machine Learning**

| ID | Course | Prereqs |
|---|---|---|
| AI-DL | Deep Learning | CS3102 |
| AI-NLP | NLP & Large Language Models | AI-DL |
| AI-RL | Reinforcement Learning | CS3102, MA2101 |
| AI-MLOPS | MLOps & Production ML | CS3102, CS3203 |
| AI-SAFE | AI Safety & Alignment | CS3102 |

**Systems**

| ID | Course | Prereqs |
|---|---|---|
| SYS-COMP | Compilers | CS3103 |
| SYS-ADV | Advanced Operating Systems | CS2201 |
| SYS-CLOUD | Cloud Infrastructure & Virtualization | CS3201 |
| SYS-PERF | Performance Engineering | CS2102, CS2201 |
| SYS-DBI | Database Internals | CS2202, CS2201 |

**Security** (defensive orientation; offensive techniques taught in authorized-testing framing)

| ID | Course | Prereqs |
|---|---|---|
| SEC-CRYPTO | Applied Cryptography | CS3104, MA1101 |
| SEC-SSD | Secure Software Development | CS3104, CS2103 |
| SEC-NET | Network Security | CS3104, CS3101 |
| SEC-PRIV | Privacy Engineering | CS3104 |
| SEC-OFFDEF | Offensive Security for Defenders | CS3104, CS3101 |

**General electives** (any track, or free elective)

| ID | Course | Prereqs |
|---|---|---|
| EL-GRAPH | Computer Graphics | MA1201, CS1201 |
| EL-QUANT | Quantum Computing | MA1201 |
| EL-MOBILE | Mobile & Cross-Platform Development | CS1203 |
| EL-ROBOT | Robotics & Embedded AI | CS3102 |

## Design notes

- **Math is not optional.** Four math courses in the first three semesters — the
  most common gap in self-taught pathways, and prerequisite to ML, graphics,
  crypto, and theory.
- **Security and AI are core, not tracks.** CS3104 and CS3102/CS3202 sit in the
  common core; tracks deepen them.
- **Prerequisites are edges, not chapters.** The graph in `pathway.yaml` is the
  single source of truth; this document is a rendering of it.
- **`/teach` sequencing:** a learner's next available courses = all courses whose
  prerequisite sets are satisfied by their completed set. Semester numbers are a
  suggested full-time pacing, not a constraint.
