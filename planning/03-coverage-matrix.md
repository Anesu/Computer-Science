# CS2023 Coverage Matrix

Proof that every ACM/IEEE CS2023 knowledge area is owned by core courses, with
track courses shown as deepening. Machine-checked by rule 4 of
`scripts/validate_pathway.py` (every KA must appear in ≥1 core course).

| KA | Knowledge area | Core coverage | Deepened by |
|----|----------------|---------------|-------------|
| AI | Artificial Intelligence | CS3102 Machine Learning; CS3202 LLM Application Engineering | AI track (AI-DL, AI-NLP, AI-RL, AI-MLOPS, AI-SAFE), EL-ROBOT |
| AL | Algorithmic Foundations | CS1201 DS&A I; CS2101 Algorithm Design; CS2203 Theory of Computation | EL-QUANT |
| AR | Architecture and Organization | CS1102 Systems Fundamentals; CS2102 Computer Architecture | SYS-PERF |
| DM | Data Management | CS2202 Data Management & Databases | SYS-DBI |
| FPL | Foundations of Programming Languages | CS1202 Systems Programming; CS3103 Programming Languages | SYS-COMP |
| GIT | Graphics and Interactive Techniques | CS2204 HCI & Visual Computing (graphics core hours) | EL-GRAPH |
| HCI | Human-Computer Interaction | CS2204 HCI & Visual Computing | EL-MOBILE |
| MSF | Mathematical and Statistical Foundations | MA1101, MA1102, MA1201, MA2101; reinforced in CS3102 | SEC-CRYPTO, EL-QUANT |
| NC | Networking and Communication | CS3101 Computer Networks | SEC-NET |
| OS | Operating Systems | CS2201 Operating Systems | SYS-ADV, SYS-DBI |
| PDC | Parallel and Distributed Computing | CS3201 Parallel & Distributed Computing | SYS-CLOUD |
| SDF | Software Development Fundamentals | CS1101, CS1201, CS1203; capstones | — |
| SE | Software Engineering | CS2103 Software Engineering; CS3203 Large-Scale Software & DevOps; capstones | AI-MLOPS, SEC-SSD |
| SEC | Security | CS3104 Security Fundamentals (core, not elective) | Security track (all five courses) |
| SEP | Society, Ethics and the Profession | CS4101 Computing, Ethics & Society; woven into CS1101, CS2103, CS4902 | AI-SAFE, SEC-PRIV |
| SF | Systems Fundamentals | CS1102, CS1202 | SYS-COMP, SYS-PERF |
| SPD | Specialized Platform Development | CS1203 (web), CS3202 (LLM platforms), CS3203 (cloud) | EL-MOBILE, EL-ROBOT, SYS-CLOUD, AI-MLOPS |

## Phase 2 refinement

This matrix is course-level. During Phase 2 (course specs), each course spec
must list which CS2023 *knowledge units* within its KA it covers, so coverage
is auditable at core-hour granularity — that finer matrix becomes an appendix
here, and gaps found at that level are fixed by editing unit breakdowns, not by
adding courses.
