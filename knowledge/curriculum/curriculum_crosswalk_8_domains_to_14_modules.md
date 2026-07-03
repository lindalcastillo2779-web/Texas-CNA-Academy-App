# Curriculum Crosswalk: 8 NATCEP Domains → 14 In-App Modules

This alignment map connects the **domain-based Streamlit curriculum docs** in `knowledge/curriculum`
with the **14-module in-app learning model** in `src/features/courses/module-config.ts`.

## Master alignment matrix

| NATCEP domain doc | Domain focus | Primary in-app modules | Reinforcement modules |
|---|---|---|---|
| `module_01_role_and_scope` | Role and scope | M01 Role of the Nurse Aide | M02 Legal & Ethical, M03 Communication, M14 Exam Prep |
| `module_02_safety_and_emergency` | Promotion of safety | M05 Safety & Emergency Procedures | M04 Infection Control, M07 Personal Care, M08 Basic Nursing Skills, M10 Elimination, M11 Restorative, M14 |
| `module_03_infection_control` | Infection prevention | M04 Infection Control | M05 Safety & Emergency, M07 Personal Care, M08 Basic Nursing Skills, M14 |
| `module_04_cognitively_impaired_care` | Cognitive impairment care | M12 Psychosocial Care | M03 Communication, M06 Resident Rights, M13 Spiritual & Cultural, M14 |
| `module_05_emotional_and_mental_health` | Emotional and mental health | M12 Psychosocial Care | M03 Communication, M06 Resident Rights, M13 Spiritual & Cultural, M14 |
| `module_06_spiritual_and_cultural_needs` | Spiritual and cultural care | M13 Spiritual & Cultural Care | M03 Communication, M06 Resident Rights, M12 Psychosocial, M14 |
| `module_07_basic_restorative_services` | Basic restorative services | M11 Restorative Skills | M05 Safety & Emergency, M07 Personal Care, M08 Basic Nursing Skills, M14 |
| `module_08_residents_rights` | Residents' rights | M06 Resident Rights, M02 Legal & Ethical | M01 Role, M03 Communication, M12 Psychosocial, M13 Spiritual & Cultural, M14 |

## 14-module coverage reference

| App module | Primary mapped domain doc(s) |
|---|---|
| M01 Role of the Nurse Aide | `module_01_role_and_scope` |
| M02 Legal & Ethical Behavior | `module_08_residents_rights`, `module_01_role_and_scope` |
| M03 Communication & Interpersonal Skills | `module_01_role_and_scope`, `module_04_cognitively_impaired_care`, `module_05_emotional_and_mental_health`, `module_06_spiritual_and_cultural_needs`, `module_08_residents_rights` |
| M04 Infection Control | `module_03_infection_control` |
| M05 Safety & Emergency Procedures | `module_02_safety_and_emergency` |
| M06 Resident Rights | `module_08_residents_rights` |
| M07 Personal Care Skills | `module_02_safety_and_emergency`, `module_03_infection_control` |
| M08 Basic Nursing Skills | `module_02_safety_and_emergency`, `module_03_infection_control`, `module_07_basic_restorative_services` |
| M09 Nutrition & Hydration | `module_02_safety_and_emergency` (function and health reinforcement) |
| M10 Elimination | `module_02_safety_and_emergency` (function and health reinforcement) |
| M11 Restorative Skills | `module_07_basic_restorative_services` |
| M12 Psychosocial Care | `module_04_cognitively_impaired_care`, `module_05_emotional_and_mental_health` |
| M13 Spiritual & Cultural Care | `module_06_spiritual_and_cultural_needs` |
| M14 Prometric Exam Preparation | Comprehensive reinforcement across all domain docs |

## Notes for implementation

- Streamlit markdown remains domain-organized for regulatory clarity.
- In-app learning remains module-sequenced for learner progression and exam prep.
- Chapter-level checklists, assessment banks, remediation notes, and pacing now support bridgeable content reuse between both structures.
