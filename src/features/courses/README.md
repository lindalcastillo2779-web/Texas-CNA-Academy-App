# Courses Feature - Texas CNA Academy

## Overview
Complete, production-ready Courses feature for Texas CNA Academy mobile app. Aligned with Prometric/NNAAP CNA exam curriculum with adaptive learner behavior, module readiness logic, and warm faith-aware microcopy.

## 📂 Folder Structure

```
src/features/courses/
├── types/
│   ├── courses.types.ts          # TypeScript interfaces for modules, lessons, content blocks
│   └── domain-labels.ts          # 14 Prometric domain labels with colors and icons
├── data/
│   ├── m01-role-of-nurse-aide.bundle.ts              # Module 1: 6 lessons
│   ├── m02-legal-ethical-behavior.bundle.ts          # Module 2: 7 lessons
│   └── m03-communication-interpersonal.bundle.ts     # Module 3: 8 lessons
├── module-config.ts              # Configuration for all 14 modules
├── courses.resolver.ts           # Resolver functions (learner state, progress, adaptive logic)
├── index.ts                      # Main export file
└── README.md                     # This file
```

## 🎯 Key Features

### ✅ Content Layer (Modules 1-3 Complete)
- **Module 1**: Role of the Nurse Aide (6 lessons, 45 min)
- **Module 2**: Legal & Ethical Behavior (7 lessons, 50 min)
- **Module 3**: Communication & Interpersonal Skills (8 lessons, 55 min)
- Warm, professional, faith-aware microcopy throughout
- Structured content types: headings, paragraphs, lists, tables, callouts, steps, reflection prompts

### ✅ Configuration Layer
- All 14 modules configured in `module-config.ts`
- Modules 4-14 marked as "Coming Soon" with complete metadata
- Prerequisites, domain mappings, clinical skills counts, and Prometric weights defined

### ✅ Type System
- Complete TypeScript interfaces for modules, lessons, learner state, progress tracking
- 14 Prometric domain types with UI-ready colors and icons
- Adaptive behavior configuration types (completion rules, review modes, tone profiles)

### ✅ Resolver Functions (Wiring Layer)
- `getModulesWithProgress()` - Get all modules with learner progress and unlock status
- `getModuleBundle()` - Retrieve full module with lessons
- `getLesson()` - Get individual lesson
- `getLessonsWithProgress()` - Lessons with completion tracking
- `isLessonComplete()` - Completion logic based on scroll, time, interaction
- `completeLessonAndUpdateState()` - Mark lessons complete and update learner state
- `getNextLesson()` - Adaptive "Resume My Course" logic
- `getModuleConfidenceLevel()` - Low/medium/high confidence assessment

## 🔌 Usage Examples

### Import the Courses Feature
```typescript
import {
  getModulesWithProgress,
  getLessonsWithProgress,
  completeLessonAndUpdateState,
  getNextLesson,
  M01_BUNDLE,
  DOMAIN_LABELS,
  MODULE_CONFIGS,
} from '@/features/courses';
```

### Get All Modules with Learner Progress
```typescript
const learnerState: LearnerState = {
  learnerId: 'user123',
  completedModuleIds: ['M01'],
  moduleProgress: {
    M01: {
      moduleId: 'M01',
      completedLessonIds: ['M01-L01', 'M01-L02', 'M01-L03', 'M01-L04', 'M01-L05', 'M01-L06'],
      totalLessons: 6,
      completedLessons: 6,
      percentComplete: 100,
      lastAccessedAt: '2026-07-01T15:00:00Z',
      status: 'completed',
    },
  },
};

const modules = getModulesWithProgress(learnerState);
// Returns all 14 modules with progress and unlock status
```

### Get Next Recommended Lesson
```typescript
const nextLesson = getNextLesson(learnerState);
// { moduleId: 'M02', lessonId: 'M02-L01' }
```

### Display Domain Badge
```typescript
const domain = DOMAIN_LABELS['COMM'];
// {
//   key: 'COMM',
//   shortLabel: 'Communication',
//   fullLabel: 'Communication and Interpersonal Skills',
//   description: '...',
//   color: 'purple',
//   icon: 'chat-bubble-left-right',
// }
```

## 🎨 Content Types Reference

Each lesson contains structured content blocks:

```typescript
{
  type: 'heading' | 'paragraph' | 'list' | 'table' | 'callout' | 'steps' | 'reflection-prompt' | 'summary-list',
  text?: string,
  items?: string[],
  variant?: 'tip' | 'warning' | 'encouragement' | 'faith',
  // ... type-specific properties
}
```

## 📊 Prometric Domains

14 standardized Prometric/NNAAP CNA exam domains:

| Key | Short Label | Color |
|-----|-------------|-------|
| ROLE | Role & Scope | blue |
| SAFETY | Safety | red |
| INFECT | Infection Control | green |
| COMM | Communication | purple |
| ELDERCARE | Resident Rights | orange |
| PERSONAL | Personal Care | pink |
| NUTRITION | Nutrition | yellow |
| ELIMINATION | Elimination | teal |
| RESTORATIVE | Restorative | cyan |
| PSYCHOSOCIAL | Psychosocial | violet |
| SPIRITUAL | Spiritual Care | indigo |
| LEGAL | Legal & Ethics | gray |
| VITALS | Vital Signs | rose |
| SKILLS | Clinical Skills | lime |

## 🚀 Next Steps for UI Integration

1. **Create UI Components**
   - ModuleCard component
   - LessonViewer component
   - ProgressBar component
   - DomainBadge component
   - ReflectionPrompt component

2. **Wire Resolver to State Management**
   - Connect to React Context, Redux, or Zustand
   - Persist learner state to local storage or backend

3. **Build Navigation**
   - Module list screen
   - Lesson viewer screen
   - "Resume My Course" CTA

4. **Add Modules 4-14 Content**
   - Follow the same bundle structure as M01-M03
   - Update `MODULE_BUNDLE_REGISTRY` in resolver

## 📝 Notes

- All content is curriculum-aligned with Prometric/NNAAP CNA exam
- Microcopy is warm, professional, and faith-aware
- Completion rules are configurable per lesson
- Adaptive behavior supports prerequisite-based unlocking
- Ready for Streamlit, React Native, or web deployment

---

**Created**: July 1, 2026  
**Status**: Production-ready starter kit (Modules 1-3 complete)  
**License**: Proprietary - Texas CNA Academy
