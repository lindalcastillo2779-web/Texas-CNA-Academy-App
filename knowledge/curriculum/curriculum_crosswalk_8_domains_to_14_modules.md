# Curriculum Crosswalk: 8 NATCEP Domains → 14 App Modules

This crosswalk aligns the domain-based curriculum documents in `knowledge/curriculum`
with the 14-module in-app course structure used in the learning app.

- **Domain doc IDs** use the `module_0x_...` naming in this folder.
- **App course IDs** use `M01`–`M14` from `src/features/courses/module-config.ts`.

## Domain-to-module mapping

### 1) Role of the Nurse Aide
- Domain doc: `module_01_role_and_scope`
- Primary modules: **M01 Role of the Nurse Aide**
- Reinforcement modules: M02 Legal & Ethical Behavior, M03 Communication & Interpersonal Skills, M14 Prometric Exam Preparation

### 2) Promotion of Safety
- Domain doc: `module_02_safety_and_emergency`
- Primary modules: **M05 Safety & Emergency Procedures**
- Reinforcement modules: M04 Infection Control, M07 Personal Care Skills, M08 Basic Nursing Skills, M10 Elimination, M11 Restorative Skills, M14 Prometric Exam Preparation

### 3) Promotion of Function and Health of Residents
- Domain doc: represented across foundational care content; no single dedicated `module_0x` file
- Primary modules: **M07 Personal Care Skills**, **M08 Basic Nursing Skills**, **M09 Nutrition & Hydration**, **M10 Elimination**
- Reinforcement modules: M11 Restorative Skills, M14 Prometric Exam Preparation

### 4) Care of Cognitively Impaired Residents
- Domain doc: `module_04_cognitively_impaired_care`
- Primary modules: **M12 Psychosocial Care**
- Reinforcement modules: M03 Communication & Interpersonal Skills, M06 Resident Rights, M13 Spiritual & Cultural Care, M14 Prometric Exam Preparation

### 5) Emotional and Mental Health Needs
- Domain doc: `module_05_emotional_and_mental_health`
- Primary modules: **M12 Psychosocial Care**
- Reinforcement modules: M03 Communication & Interpersonal Skills, M06 Resident Rights, M13 Spiritual & Cultural Care, M14 Prometric Exam Preparation

### 6) Spiritual and Cultural Needs
- Domain doc: `module_06_spiritual_and_cultural_needs`
- Primary modules: **M13 Spiritual & Cultural Care**
- Reinforcement modules: M03 Communication & Interpersonal Skills, M06 Resident Rights, M12 Psychosocial Care, M14 Prometric Exam Preparation

### 7) Basic Restorative Services
- Domain doc: `module_07_basic_restorative_services`
- Primary modules: **M11 Restorative Skills**
- Reinforcement modules: M05 Safety & Emergency Procedures, M07 Personal Care Skills, M08 Basic Nursing Skills, M14 Prometric Exam Preparation

### 8) Residents' Rights
- Domain doc: `module_08_residents_rights`
- Primary modules: **M06 Resident Rights**, **M02 Legal & Ethical Behavior**
- Reinforcement modules: M01 Role of the Nurse Aide, M03 Communication & Interpersonal Skills, M12 Psychosocial Care, M13 Spiritual & Cultural Care, M14 Prometric Exam Preparation

## Notes for curriculum planning

- NATCEP domain docs are organized by broad competency areas.
- App modules are organized by learning sequence and exam-focused topic grouping.
- This crosswalk supports consistency when expanding chapter content, quizzes, and skill checklists.
- Not every app course module has a one-to-one markdown document in this folder yet; this file is the bridging map.
