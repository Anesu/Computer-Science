# Resource Gap Analysis & Reading Plan

Working document, 2026-07-19. Companion to `resources/registry.yaml`.

Purpose: a per-course sourcing plan to execute while progressing through the
pathway. As each course comes up, find/ingest the open texts and buy the
personal-reading books listed below, then register them in
`resources/registry.yaml` (status `open` vs `identified`) and wire `used_in`.

Legend: **[have]** already in registry · **[ingest]** open-license, can be
ingested into the library · **[buy]** proprietary, personal reading / link
only · **[free-link]** free to read online but no open license stated — teach
from it, link it, do not mirror.

License statuses below were verified against official/author sites on
2026-07-19.

---

## 1. Gap analysis

**Courses with zero registry sources**

- `CS4101` Computing, Ethics & Society — a **core** course with `sources: []`.
- `CS4901` / `CS4902` Capstone I & II — nothing to guide project execution.

**Core courses with no ingestible open text** (proprietary only — linkable,
not ingestible)

- `CS1102` (nand2tetris book is all-rights-reserved), `CS1201` (CLRS only),
  `CS1203` (Pragmatic Programmer only), `CS2102` (CS:APP only),
  `CS2203` (Sipser only), `CS3201` (DDIA only).

**Courses resting on vendor docs or standards instead of teaching texts**

- `CS3202` (Anthropic docs only — vendor-specific), `AI-MLOPS` (same),
  `SEC-SSD` (ASVS is a checklist, not a textbook),
  `SEC-NET` (only NIST SP 800-41, a 2009 firewall guideline — dated),
  `SEC-PRIV` (only a framework doc), `SYS-CLOUD` / `EL-MOBILE` / `EL-ROBOT`
  (docs only).

**Level mismatches**

- `SYS-ADV` reuses OSTEP — the same *intro* text as `CS2201`.
- `SEC-CRYPTO` jumps straight to Boneh–Shoup, an explicitly *graduate* text —
  needs an undergrad bridge.
- `CS1201` uses CLRS as sole text — a reference work, too steep as a first
  DSA book.

**Structural**

- Phase 2/3 authoring is the real bottleneck (only CS1101 has concept docs).
  This plan assumes course specs get written per-semester, using the books
  below as primary sources.

---

## 2. Ingest list — open-license, ranked by impact

### P0 — fix empty or broken core courses

| Resource | License (verified) | Fixes |
|---|---|---|
| Barak, *Introduction to Theoretical Computer Science* — https://introtcs.org | CC BY-NC-ND 4.0 | CS2203 |
| Matthews, Newhall & Webb, *Dive into Systems* v1.2 — https://diveintosystems.org | CC BY-NC-ND 4.0 | CS1102, CS1202, CS2102 |
| Morin, *Open Data Structures* — https://opendatastructures.org | CC BY 2.5 CA | CS1201 |
| Miller & Ranum, *Problem Solving with Algorithms and Data Structures using Python* (Runestone) — https://runestone.academy/ns/books/published/pythonds3/index.html | CC BY-NC-SA 4.0 | CS1201 |
| Athalye, Gjengset & Gonzalez Ortiz, *The Missing Semester of Your CS Education* — https://missing.csail.mit.edu | CC BY-NC-SA 4.0 | CS1203 |
| Chacon & Straub, *Pro Git*, 2nd ed — https://git-scm.com/book/en/v2 | CC BY-NC-SA 3.0 | CS1203 |
| D'Ignazio & Klein, *Data Feminism* — https://data-feminism.mitpress.mit.edu | CC BY-NC-ND 4.0 (MIT Press OA) | CS4101 |
| Costanza-Chock, *Design Justice* — https://designjustice.mitpress.mit.edu | CC BY-NC-ND 4.0 (MIT Press OA) | CS4101 |
| Fogel, *Producing Open Source Software*, 2nd ed — https://producingoss.com | CC BY-SA 4.0 | CS4901, CS4902 |
| Winters, Manshreck & Wright (eds.), *Software Engineering at Google* — https://abseil.io/resources/swe-book | CC BY-NC-ND 4.0 | CS4901, CS2103, CS3203 |

### P1 — shore up thin, vendor-only, or mismatched courses

| Resource | License (verified) | Fixes |
|---|---|---|
| Prince, *Understanding Deep Learning* — https://udlbook.github.io/udlbook/ | CC BY-NC-ND 4.0 | CS3102, AI-DL |
| Bekman, *Machine Learning Engineering* — https://github.com/stas00/ml-engineering | CC BY-SA 4.0 | AI-MLOPS |
| Mohandas, *Made With ML* (repo) — https://github.com/GokuMohandas/Made-With-ML | MIT | AI-MLOPS |
| Hugging Face *LLM Course*, *NLP Course*, *smol-course* — github.com/huggingface | Apache-2.0 | CS3202, AI-NLP, AI-MLOPS |
| Achiam, *Spinning Up in Deep RL* (OpenAI) — https://spinningup.openai.com | MIT | AI-RL |
| Adkins et al., *Building Secure and Reliable Systems* — https://sre.google/books | CC BY 4.0 | SEC-SSD, CS3203 |
| Van Houtven, *Crypto 101* — https://crypto101.io | CC BY-NC 4.0 | SEC-CRYPTO, CS3104 |
| OWASP *Top 10* (2025) — https://owasp.org/www-project-top-ten/ | CC BY-SA 4.0 | CS3104, SEC-OFFDEF |
| Peterson & Davie, *Computer Networks: A Systems Approach* — https://book.systemsapproach.org | CC BY 4.0 | CS3101, SEC-NET |
| Dordal, *An Introduction to Computer Networks* — https://intronetworks.cs.luc.edu | CC BY-NC-ND | CS3101, SEC-NET |
| Cox, Kaashoek & Morris, *xv6: a simple, Unix-like teaching operating system* — github.com/mit-pdos/xv6-riscv-book | MIT | SYS-ADV, CS2201 |
| McKenney, *Is Parallel Programming Hard...?* (perfbook) | CC BY-SA 3.0 (code GPLv2) | SYS-PERF, CS3201 |
| Bailis, Hellerstein & Stonebraker (eds.), *Readings in Database Systems*, 5th ed — http://redbook.io | CC BY-NC-SA 4.0 | CS2202, SYS-DBI |
| Hammack, *Book of Proof*, 3rd ed — https://richardhammack.github.io/BookOfProof/ | CC BY-NC-ND 4.0 | MA1101 |
| Axler, *Linear Algebra Done Right*, 4th ed — https://linear.axler.net (Springer OA) | CC BY-NC 4.0 | MA1201 |
| Downey, *Think Stats*, 2nd ed — https://greenteapress.com/wp/think-stats-2e/ | CC BY-NC-SA 4.0 | MA2101 |
| Correll, Hayes, Heckman & Roncone, *Introduction to Autonomous Robots* — github.com/correll/Introduction-to-Autonomous-Robots | CC BY-NC-ND 4.0 (LaTeX source; **compile the PDF yourself — authors forbid redistributing a free PDF**) | EL-ROBOT |
| Tay, *Tech Interview Handbook* — github.com/yangshun/tech-interview-handbook | MIT | CS4902 |
| van Steen & Tanenbaum, *Distributed Systems*, 4th ed — https://www.distributed-systems.net/index.php/books/ds4/ | Free PDF from authors, **no license stated** — teach from it, do not mirror | CS3201, SYS-CLOUD |

### Free-to-read but not open-licensed — link only

*Shape Up* (Basecamp), *Physically Based Rendering* 3rd/4th ed online
(pbrt.org), *Quantum Computing for the Very Curious* (quantum.country),
*Learn OpenGL* prose (learnopengl.com — code is CC BY-NC, media CC BY),
PortSwigger *Web Security Academy* (free account, standard site terms),
*What We've Learned from a Year of Building with LLMs* Parts I–III
(O'Reilly Radar / applied-llms.org), Dasgupta/Papadimitriou/Vazirani
*Algorithms* pre-publication draft (author-hosted, no license stated),
*The Encyclopedia of Human-Computer Interaction*, 2nd ed (IDF — per-asset
rights), *Immersive Linear Algebra* (immersivemath.com).

---

## 3. Personal reading list (buy/borrow), in pathway order

1. **CS:APP** — Bryant & O'Hallaron, 3rd ed. Single best investment in the
   degree (CS1102 → CS1202 → CS2102). [have]
2. **SICP** — free online; read slowly during CS1101. [have]
3. **The Pragmatic Programmer** (Thomas & Hunt) + **A Philosophy of Software
   Design** (Ousterhout) — CS1203/CS2103. [have]
4. **CLRS**, *Introduction to Algorithms*, 4th ed — lifetime reference,
   CS1201/CS2101. [have]
5. **Sipser**, *Introduction to the Theory of Computation*, 3rd ed — CS2203.
   [have]
6. **Patterson & Hennessy**, *Computer Organization and Design*, RISC-V 2nd
   ed (2020) — CS2102. [buy]
7. **Kurose & Ross**, *Computer Networking: A Top-Down Approach*, 8th ed —
   CS3101. [have]
8. **Kleppmann & Riccomini**, *Designing Data-Intensive Applications*, 2nd
   ed — CS2202/CS3201/SYS-DBI. [have]
9. **Kerrisk**, *The Linux Programming Interface* — SYS-ADV. [buy]
10. **Aumasson**, *Serious Cryptography* — SEC-CRYPTO. [buy]
11. **Huyen**, *AI Engineering* (O'Reilly 2025) + *Designing Machine Learning
    Systems* (O'Reilly 2022) — CS3202/AI-MLOPS. [buy]
12. **Raschka**, *Build a Large Language Model (From Scratch)* (Manning
    2024) — AI-NLP/CS3202; companion code repo is Apache-2.0. [buy]
13. **Quinn**, *Ethics for the Information Age*, 9th ed (Pearson 2024) —
    CS4101. [buy]
14. **Forsgren/Humble/Kim**, *Accelerate* + **Kim et al.**, *The DevOps
    Handbook* — CS3203. [buy]
15. **Shostack**, *Threat Modeling: Designing for Security* — SEC-SSD. [buy]
16. **Nielsen & Chuang**, *Quantum Computation and Quantum Information* —
    EL-QUANT, only if taking the elective. [have]
17. CS4101 enrichment: *Weapons of Math Destruction* (O'Neil), *Race After
    Technology* (Benjamin), *Atlas of AI* (Crawford). [buy]

---

## 4. Per-course ranked recommendations, with reasoning

### Year 1

- **CS1101 Programming Fundamentals**: 1. Think Python [have] —
  exercise-driven, right level. 2. Composing Programs [have] — SICP ideas in
  Python, feeds CS3103. 3. SICP [have] — profound but steep; second pass.
- **MA1101 Discrete Mathematics**: 1. Mathematics for Computer Science (MIT)
  [have] — primary. 2. Book of Proof [ingest] — proofs are where students
  fail; gentler on-ramp. 3. Rosen [have] — breadth reference.
- **CS1102 Computer Systems Fundamentals**: 1. Dive into Systems [ingest] —
  modern C+asm+arch, fixes the open-text gap. 2. nand2tetris [have] —
  project spine. 3. CS:APP [have] — stretch; also add `CS1102` to its
  `used_in`.
- **MA1102 Calculus for Computing**: 1. OpenStax Calculus [have] — primary.
  2. Calculus Made Easy (Thompson, Project Gutenberg #33283) [ingest —
  public domain] — intuition. Sufficient as-is.
- **CS1201 Data Structures & Algorithms I**: 1. Open Data Structures
  [ingest] — structures-first, course level. 2. Miller & Ranum (Runestone)
  [ingest] — interactive Python, matches CS1101. 3. CLRS [have] — demote to
  reference.
- **CS1202 Systems Programming**: 1. Dive into Systems [ingest] — the C
  teaching text the course lacks. 2. K&R [have] — terse classic reference.
  3. Rust Book [have] — second language. 4. CS:APP [have] — labs.
- **MA1201 Linear Algebra**: 1. Axler, Linear Algebra Done Right 4e
  [ingest] — open access, proof-based. 2. Strang + MIT OCW 18.06 [have] —
  intuition. 3. MML ch. 2 [have] — ML bridge.
- **CS1203 Software Construction & Tooling**: 1. The Missing Semester
  [ingest] — exactly the shell/git/CLI tooling content. 2. Pro Git [ingest]
  — version-control depth. 3. Pragmatic Programmer [have] — habits.

### Year 2

- **CS2101 Algorithm Design & Analysis**: 1. Erickson [have] — free and
  rigorous. 2. Dasgupta/Papadimitriou/Vazirani [free-link] — concise
  intuition. 3. CLRS [have] — reference. Optional: Skiena, *The Algorithm
  Design Manual* [buy] for war stories.
- **CS2102 Computer Architecture**: 1. Patterson & Hennessy, RISC-V ed
  [buy] — datapath/pipelining design that CS:APP doesn't cover. 2. Dive into
  Systems [ingest] — free primary. 3. CS:APP [have] — machine-level view.
- **MA2101 Probability & Statistics for CS**: 1. OpenIntro Statistics
  [have]. 2. Think Stats [ingest] — computational, Python. 3. MML ch. 6
  [have].
- **CS2103 Software Engineering**: 1. A Philosophy of Software Design
  [have] — design taste. 2. Software Engineering at Google [ingest] —
  engineering over time/scale. 3. Pragmatic Programmer [have].
- **CS2201 Operating Systems**: 1. OSTEP [have] — primary. 2. xv6 book
  [ingest] — real kernel source + labs. 3. Anderson & Dahlin, *Operating
  Systems: Principles and Practice* [buy, optional] — breadth.
- **CS2202 Data Management & Databases**: 1. Database System Concepts
  [have] — theory + SQL. 2. DDIA [have] — tradeoffs. 3. Readings in Database
  Systems [ingest] — seminal papers.
- **CS2203 Theory of Computation**: 1. Barak, Intro to TCS [ingest] —
  modern, free. 2. Sipser [have] — clearest classic. 3. Savage, *Models of
  Computation* [ingest, CC BY-NC-ND — cs.brown.edu/people/jsavage/book/] —
  alternate, adds circuits.
- **CS2204 HCI & Visual Computing**: 1. Norman [have] — design thinking.
  2. Computer Graphics from Scratch [have] — build a raytracer. 3. IDF
  Encyclopedia of HCI [free-link] — survey breadth. Optional: Sharp/Preece/
  Rogers, *Interaction Design* [buy].

### Year 3

- **CS3101 Computer Networks**: 1. Kurose & Ross [have] — pedagogy +
  Wireshark labs. 2. Computer Networks: A Systems Approach [ingest] — open
  modern text. 3. Beej's Guide [have] — sockets. 4. High Performance Browser
  Networking (hpbn.co, CC BY-NC-ND) [ingest] — perf angle.
- **CS3102 Machine Learning**: 1. MML [have] — math. 2. AIMA [have] —
  breadth. 3. D2L [have] — practice. 4. Understanding Deep Learning
  [ingest] — modern neural depth. Grad reference: Murphy, *Probabilistic
  Machine Learning* drafts [free-link, CC BY-NC-ND].
- **CS3103 Programming Languages**: 1. Crafting Interpreters [have] — build
  two interpreters. 2. SICP [have] — abstraction. 3. TAPL [have] — type
  theory, advanced.
- **CS3104 Security Fundamentals**: 1. Security Engineering [have] — the
  survey bible. 2. Crypto 101 [ingest] — accessible crypto. 3. OWASP Top 10
  [ingest] — vuln taxonomy + labs.
- **CS3201 Parallel & Distributed Computing**: 1. van Steen & Tanenbaum
  [free-link] — the missing teaching text. 2. DDIA [have]. 3. perfbook
  [ingest] — shared-memory parallelism.
- **CS3202 LLM Application Engineering**: 1. Huyen, AI Engineering [buy] —
  written for exactly this course. 2. Anthropic docs [have] — agent
  patterns. 3. HF LLM Course + smol-course [ingest] — open models /
  fine-tuning. 4. "What We've Learned from a Year of Building with LLMs"
  [free-link] — practitioner heuristics.
- **CS3203 Large-Scale Software & DevOps**: 1. SRE Book [have]. 2. Building
  Secure and Reliable Systems [ingest]. 3. Accelerate + DevOps Handbook
  [buy] — evidence + playbook. 4. SWE at Google [ingest].

### Year 4

- **CS4101 Computing, Ethics & Society**: 1. Quinn, Ethics for the
  Information Age 9e [buy] — the standard structured course text. 2. Data
  Feminism [ingest] — data power/justice. 3. Design Justice [ingest] —
  design-practice lens. 4. ACM Code of Ethics [free doc] + WMD / Race After
  Technology [buy] as cases.
- **CS4901 Capstone I**: 1. Producing Open Source Software [ingest] —
  running a real project. 2. Shape Up [free-link] — scoping/shipping. 3. SWE
  at Google [ingest] — reviews/code health.
- **CS4902 Capstone II**: 1. Tech Interview Handbook [ingest] —
  portfolio → job. 2. Mythical Man-Month [buy] — timeless project essays.
  3. Revisit Pragmatic Programmer [have].

### Track: AI / Machine Learning

- **AI-DL Deep Learning**: 1. Understanding Deep Learning [ingest] —
  becomes primary; current. 2. D2L [have] — code-first. 3. Goodfellow
  [have] — theory reference.
- **AI-NLP NLP & LLMs**: 1. SLP3 [have] — primary. 2. NLP with Transformers
  [buy] — applied. 3. HF NLP Course [ingest] — labs.
- **AI-RL Reinforcement Learning**: 1. Sutton & Barto [have] — definitive.
  2. Spinning Up [ingest] — practical deep RL. 3. Deep RL Hands-On (Lapan)
  [buy, optional].
- **AI-MLOPS MLOps & Production ML**: 1. Designing ML Systems [buy] —
  canonical. 2. ML Engineering (Bekman) [ingest] — engineering depth.
  3. Made With ML [ingest] — end-to-end project. 4. Anthropic docs [have].
- **AI-SAFE AI Safety & Alignment**: 1. Hendrycks, *Introduction to AI
  Safety, Ethics, and Society* [have] — primary. 2. Christian, *The
  Alignment Problem* [buy]. 3. Russell, *Human Compatible* [buy].

### Track: Systems

- **SYS-COMP Compilers**: 1. Crafting Interpreters [have] — front-to-back
  implementation. 2. Cooper & Torczon, *Engineering a Compiler* [buy] —
  optimization/backends. 3. Appel, *Modern Compiler Implementation* [buy,
  alt].
- **SYS-ADV Advanced Operating Systems**: 1. Kerrisk, *The Linux
  Programming Interface* [buy] — real advanced depth; fixes the OSTEP
  repeat. 2. xv6 book [ingest] — kernel hacking. 3. OSTEP [have] —
  refresher only.
- **SYS-CLOUD Cloud Infrastructure & Virtualization**: 1. Kubernetes docs
  [have] — hands-on. 2. van Steen & Tanenbaum [free-link] — distributed
  theory. 3. Burns, *Designing Distributed Systems* [buy] — patterns.
- **SYS-PERF Performance Engineering**: 1. Systems Performance (Gregg)
  [have]. 2. perfbook [ingest] — parallel perf theory. 3. BPF Performance
  Tools (Gregg) [buy].
- **SYS-DBI Database Internals**: 1. Database Internals (Petrov) [have].
  2. DDIA [have]. 3. Readings in Database Systems [ingest].

### Track: Security

- **SEC-CRYPTO Applied Cryptography**: 1. Aumasson, *Serious Cryptography*
  [buy] — undergrad bridge. 2. Crypto 101 [ingest] — free intro.
  3. Boneh–Shoup [have] — rigorous cap.
- **SEC-SSD Secure Software Development**: 1. Building Secure and Reliable
  Systems [ingest] — the actual textbook. 2. Shostack, *Threat Modeling*
  [buy] — method. 3. ASVS [have] — checklist.
- **SEC-NET Network Security**: 1. Kaufman/Perlman/Speciner, *Network
  Security: Private Communication in a Public World* [buy] — the classic.
  2. Bejtlich, *The Practice of Network Security Monitoring* [buy] —
  defense ops. 3. CN: A Systems Approach [ingest] — protocol refresh.
  4. NIST SP 800-41 [have] — dated; policy reference only.
- **SEC-PRIV Privacy Engineering**: 1. NIST Privacy Framework [have].
  2. Hoepman, *Strategic Privacy by Design* [buy] — privacy-engineering
  method. 3. Data Feminism [ingest] + GDPR text [public] — context.
- **SEC-OFFDEF Offensive Security for Defenders**: 1. PortSwigger Web
  Security Academy [free-link] — where the hands-on hours go. 2. WSTG
  [have] — methodology. 3. Tsai, *Real-World Bug Hunting* [buy] — modern
  practitioner view.

### General electives

- **EL-GRAPH Computer Graphics**: 1. Computer Graphics from Scratch [have].
  2. Learn OpenGL [free-link] — practical API. 3. PBRT [free-link] —
  advanced rendering.
- **EL-QUANT Quantum Computing**: 1. Quantum Computing for the Very Curious
  [free-link] — best on-ramp. 2. Nielsen & Chuang [have] — reference.
  3. Qiskit textbook repo [Apache-2.0, archived Jan 2024] — hands-on.
- **EL-MOBILE Mobile & Cross-Platform Development**: 1. Flutter docs
  [have] — sufficient for a platform course. 2. Apple HIG + Material Design
  guidelines [free docs] — design side.
- **EL-ROBOT Robotics & Embedded AI**: 1. Introduction to Autonomous Robots
  [ingest — compile from LaTeX source]. 2. ROS 2 docs [have] — tooling.
  3. Thrun/Burgard/Fox, *Probabilistic Robotics* [buy] — algorithm depth.

---

## 5. Execution workflow

Per course, as it comes up in the pathway:

1. Source the books listed in §4 (download open texts; buy/borrow [buy]).
2. Hand open texts to the agent for ingestion; add each to
   `resources/registry.yaml` with `status: open` and the verified license,
   or `status: identified` for proprietary/free-link items.
3. Wire `used_in` on new entries (and extend existing ones, e.g. `csapp` →
   CS1102).
4. Author/refresh the course spec's units against the ranked #1–#2 texts.
