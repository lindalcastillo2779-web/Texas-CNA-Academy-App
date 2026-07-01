# Texas CNA Academy - Complete Architecture Documentation

**Created**: July 1, 2026  
**Status**: Production-Ready Foundation (Modules 1-3)  
**Version**: 1.0.0

---

## Table of Contents

1. [Project Vision](#project-vision)
2. [Architectural Decisions](#architectural-decisions)
3. [Feature Priority](#feature-priority)
4. [Courses Feature Specification](#courses-feature-specification)
5. [Design System](#design-system)
6. [Data Structure](#data-structure)
7. [Content Strategy](#content-strategy)
8. [UI/UX Patterns](#uiux-patterns)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Technical Stack](#technical-stack)

---

## 1. Project Vision

### Mission
Texas CNA Academy is a mobile-friendly educational platform designed to prepare Texas nurse aide students for Prometric/NNAAP CNA certification while supporting active CNAs, Directors of Nursing, instructors, and healthcare facilities with exam prep, renewal readiness, CEU tracking, and staffing compliance.

### Core Values
- **Curriculum-First**: Aligned with Prometric/NNAAP CNA exam standards
- **Faith-Aware**: Warm, encouraging microcopy with spiritual sensitivity
- **Adaptive**: Learner-state driven, prerequisite-based progression
- **Professional**: Clinical accuracy with compassionate tone
- **Accessible**: Mobile-optimized, works offline, supports assistive technologies

### Target Users
1. **Primary**: Pre-certification CNA students (Texas)
2. **Secondary**: Active CNAs seeking CEUs or renewal
3. **Tertiary**: Instructors, DONs, and healthcare facility administrators

---

## 2. Architectural Decisions

### Mixed Strategy: Separate Content and Configuration

**Decision**: Use a **balanced, mixed implementation strategy** where content and configuration are separated but related.

**Rationale**:
- **Maintainability**: Content updates don't affect UI structure
- **Scalability**: Easy to add new modules following established patterns
- **Flexibility**: UI can adapt based on learner state without touching content
- **Type Safety**: Strong TypeScript interfaces ensure consistency

**Implementation**:
```
src/features/courses/
├── types/              # TypeScript interfaces
├── data/               # Content bundles (M01-M14)
├── module-config.ts    # Configuration layer
├── courses.resolver.ts # Business logic / wiring
└── index.ts            # Public API
```

### Adaptive Learner Behavior

**Decision**: Implement **prerequisite-based module unlocking** with learner state tracking.

**Key Behaviors**:
1. **Module Readiness**: Modules unlock only when prerequisites are complete
2. **Progress Persistence**: Track completed lessons, time spent, confidence levels
3. **Resume Logic**: "Resume My Course" CTA directs to next incomplete lesson
4. **Coming Soon Teasers**: Future modules visible but locked with motivational badges

### Reflection as Contextual Support

**Decision**: Reflection prompts integrated **within course content**, not as separate quizzes.

**Rationale**:
- More authentic to learning experience
- Reduces cognitive load (no mode switching)
- Encourages genuine introspection vs. performance anxiety
- Optional: Learners can skip if not ready

**Implementation**:
- Reflection prompts appear as special content blocks in review lessons
- No forced responses
- Saves to learner journal (optional feature for v2)

---

## 3. Feature Priority

### Phase 1: Core Education (Current)
1. **Courses** (✅ Modules 1-3 Complete)
   - 14 curriculum-aligned modules
   - Adaptive prerequisite-based unlocking
   - Warm, faith-aware microcopy
   - Structured content types (headings, lists, tables, callouts, steps)

### Phase 2: Practice & Assessment
2. **Clinical Skills Lab** (Next)
   - 21 Prometric clinical skills
   - Video demonstrations
   - Step-by-step checklists
   - Practice mode with self-evaluation

3. **Flashcards** (Third)
   - Domain-organized card decks
   - Spaced repetition algorithm
   - Custom deck creation
   - Progress tracking

### Phase 3: Extended Features
4. **Practice Exams**
5. **CEU Tracking**
6. **Renewal Readiness**
7. **Community Features**

---

## 4. Courses Feature Specification

### Module Structure

**14 Modules Aligned with Prometric Domains:**

| Module | Title | Lessons | Minutes | Status |
|--------|-------|---------|---------|--------|
| M01 | Role of the Nurse Aide | 6 | 45 | ✅ Complete |
| M02 | Legal & Ethical Behavior | 7 | 50 | ✅ Complete |
| M03 | Communication & Interpersonal Skills | 8 | 55 | ✅ Complete |
| M04 | Infection Control | 8 | 60 | 🟡 Coming Soon |
| M05 | Safety & Emergency Procedures | 9 | 65 | 🟡 Coming Soon |
| M06 | Resident Rights | 7 | 50 | 🟡 Coming Soon |
| M07 | Personal Care Skills | 10 | 75 | 🟡 Coming Soon |
| M08 | Basic Nursing Skills | 11 | 80 | 🟡 Coming Soon |
| M09 | Nutrition & Hydration | 7 | 55 | 🟡 Coming Soon |
| M10 | Elimination | 7 | 55 | 🟡 Coming Soon |
| M11 | Restorative Skills | 8 | 60 | 🟡 Coming Soon |
| M12 | Psychosocial Care | 9 | 65 | 🟡 Coming Soon |
| M13 | Spiritual & Cultural Care | 6 | 45 | 🟡 Coming Soon |
| M14 | Prometric Exam Preparation | 14 | 120 | 🟡 Coming Soon |

### Content Types

Each lesson supports these structured content blocks:

```typescript
type ContentBlockType =
  | 'heading'           // Section titles
  | 'paragraph'         // Body text
  | 'list'              // Bulleted or numbered lists
  | 'table'             // Structured data (headers + rows)
  | 'callout'           // Highlighted tips, warnings, encouragement, faith
  | 'steps'             // Numbered procedural steps
  | 'reflection-prompt' // Introspective questions
  | 'summary-list';     // Key takeaways
```

### Lesson Completion Rules

**Three Modes**:

1. **scroll-and-time**: Lesson complete when scrolled to bottom AND minimum time reached
   - Used for: Standard content lessons
   - Example: `{ mode: 'scroll-and-time', minimumSeconds: 30 }`

2. **explicit-complete**: Requires explicit "Mark Complete" action
   - Used for: Review lessons, reflection prompts
   - Example: `{ mode: 'explicit-complete', minimumSeconds: 0 }`

3. **interaction**: Requires interaction with content element
   - Used for: Quizzes, exercises (future)
   - Example: `{ mode: 'interaction', minimumSeconds: 0 }`

---

## 5. Design System

### Color Palette

**Prometric Domain Colors** (Tailwind-based):

| Domain | Color | Hex | Usage |
|--------|-------|-----|-------|
| ROLE | Blue | #3B82F6 | Role & Scope badges |
| SAFETY | Red | #EF4444 | Safety alerts, procedures |
| INFECT | Green | #10B981 | Infection control |
| COMM | Purple | #8B5CF6 | Communication lessons |
| ELDERCARE | Orange | #F97316 | Resident rights |
| PERSONAL | Pink | #EC4899 | Personal care |
| NUTRITION | Yellow | #EAB308 | Nutrition/hydration |
| ELIMINATION | Teal | #14B8A6 | Elimination care |
| RESTORATIVE | Cyan | #06B6D4 | Restorative skills |
| PSYCHOSOCIAL | Violet | #7C3AED | Mental health |
| SPIRITUAL | Indigo | #6366F1 | Spiritual care |
| LEGAL | Gray | #6B7280 | Legal/ethics |
| VITALS | Rose | #F43F5E | Vital signs |
| SKILLS | Lime | #84CC16 | Clinical skills |

### Typography

- **Headings**: Bold, clear hierarchy
- **Body**: Readable, 16-18px base
- **Microcopy**: Warm, encouraging, concise
- **Tone**: Professional but compassionate, faith-aware without being preachy

### UI Components (To Build)

1. **ModuleCard**
   - Displays: Module title, subtitle, progress, unlock status, badge
   - States: Locked, Available, In Progress, Complete, Coming Soon
   - CTA: "Start", "Continue", "Review", or "Coming Soon" (disabled)

2. **LessonViewer**
   - Renders structured content blocks dynamically
   - Tracks scroll position and time spent
   - Shows progress indicator
   - "Mark Complete" button (for explicit-complete lessons)

3. **ProgressBar**
   - Visual representation of module/lesson completion
   - Color-coded by confidence level

4. **DomainBadge**
   - Small pill with domain icon and label
   - Color matches domain

5. **CalloutBox**
   - Variants: tip, warning, encouragement, faith
   - Icons and colors differentiate types

6. **ReflectionPrompt**
   - Styled differently from regular content
   - Optional text input for journaling
   - "Skip" and "Reflect" buttons

---

## 6. Data Structure

### Learner State (Tracked in App State)

```typescript
interface LearnerState {
  learnerId: string;
  completedModuleIds: string[];  // ['M01', 'M02']
  moduleProgress: Record<string, ModuleProgress>;
  confidenceLevels?: Record<string, 'low' | 'medium' | 'high'>;
  lastAccessedLesson?: { moduleId: string; lessonId: string };
  totalTimeSpentMinutes?: number;
}

interface ModuleProgress {
  moduleId: string;
  completedLessonIds: string[];  // ['M01-L01', 'M01-L02', ...]
  totalLessons: number;
  completedLessons: number;
  percentComplete: number;       // 0-100
  lastAccessedAt: string | null; // ISO date string
  status: 'not-started' | 'in-progress' | 'completed';
}
```

### Persistence Strategy

- **Local Storage**: For offline-first capability
- **Backend Sync**: Optional for cross-device sync (Phase 2)
- **Format**: JSON
- **Encryption**: Consider for sensitive data (Phase 2)

---

## 7. Content Strategy

### Microcopy Tone Principles

1. **Warm**: Use "you" language, friendly but professional
2. **Encouraging**: Motivational without being condescending
3. **Faith-Aware**: Occasional spiritual references ("calling", "ministry", reverence)
4. **Honest**: Acknowledge difficulty, celebrate progress
5. **Action-Oriented**: Clear next steps

### Example Microcopy

**Good**:
- "You are more than a job title. CNAs are often the primary human connection a resident experiences each day. Your presence matters deeply."
- "You have prepared for this. Every lesson brings you one step closer to your certification and your calling."
- "Service with excellence is a form of honor. How you treat the most vulnerable reflects the values you carry."

**Avoid**:
- ❌ Overly casual ("Hey there!")
- ❌ Condescending ("Good job, kiddo!")
- ❌ Preachy ("God will bless you if...")
- ❌ Medical jargon without explanation

---

## 8. UI/UX Patterns

### Navigation Flow

```
Home Dashboard
  |
  ├─ Courses (Primary)
  |   ├─ Module List
  |   └─ Lesson Viewer
  |       └─ Next Lesson (auto-navigate)
  |
  ├─ Skills Lab (Secondary)
  ├─ Flashcards (Tertiary)
  └─ Profile / Settings
```

### Primary CTA: "Resume My Course"

- Appears on dashboard if user has started courses
- Uses `getNextLesson()` resolver function
- Navigates directly to next incomplete lesson
- Shows module and lesson title in button

### "Coming Soon" Treatment

- Modules 4-14 visible but locked
- Badge: "Coming Soon" (not clickable)
- Shows estimated time and lesson count
- Brief description teases content
- **Purpose**: Build anticipation, show full curriculum scope

---

## 9. Implementation Roadmap

### ✅ Phase 1A: Backend Foundation (COMPLETE)

- [x] TypeScript type system
- [x] 14 Prometric domain labels
- [x] Module configuration for all 14 modules
- [x] Content bundles for M01-M03
- [x] Resolver functions (learner state, progress, adaptive logic)
- [x] Export API (index.ts)
- [x] Documentation (README.md)

### 🚧 Phase 1B: Frontend Components (NEXT)

- [ ] ModuleCard component
- [ ] LessonViewer component
- [ ] ProgressBar component
- [ ] DomainBadge component
- [ ] CalloutBox component (4 variants)
- [ ] ReflectionPrompt component
- [ ] Navigation structure
- [ ] State management integration

### 📋 Phase 1C: Content Completion

- [ ] Module 4: Infection Control (8 lessons)
- [ ] Module 5: Safety & Emergency (9 lessons)
- [ ] Module 6: Resident Rights (7 lessons)
- [ ] Module 7: Personal Care (10 lessons)
- [ ] Module 8: Basic Nursing Skills (11 lessons)
- [ ] Module 9-14: Remaining modules

### 📋 Phase 2: Skills Lab

- [ ] 21 Prometric clinical skills
- [ ] Video integration
- [ ] Step-by-step checklists
- [ ] Self-evaluation mode

### 📋 Phase 3: Flashcards & Extended Features

- [ ] Flashcard system
- [ ] Practice exams
- [ ] CEU tracking
- [ ] Renewal readiness dashboard

---

## 10. Technical Stack

### Current

- **Language**: TypeScript
- **Framework**: TBD (Streamlit noted, but React Native or Next.js recommended for mobile)
- **State Management**: TBD (Context API, Redux, or Zustand)
- **Storage**: LocalStorage (with optional backend sync)
- **Styling**: Tailwind CSS (implied by color tokens)

### Recommendations

- **Mobile-First**: React Native or Progressive Web App (PWA)
- **Offline Support**: Service Workers + IndexedDB
- **Analytics**: Track learner progress, completion rates, confidence levels
- **Accessibility**: WCAG 2.1 AA compliance

---

## Decision Log

### Key Decisions Made

1. **Courses First, Skills Second, Flashcards Third** (Priority)
2. **Mixed Strategy**: Separate content/config layers (Architecture)
3. **Prerequisite-Based Unlocking** (Behavior)
4. **Reflection Integrated, Not Separate** (UX)
5. **Coming Soon Badges** for M4-M14 (Transparency)
6. **Resume My Course" as Primary CTA** (Navigation)
7. **Domain-Based Color System** (Design)
8. **Warm, Faith-Aware Microcopy** (Tone)
9. **Scroll + Time Completion Rules** (Engagement)
10. **Module Bundles Over Single Config** (Maintainability)

---


## 3. Feature Priority

### Phase 1: Foundation (Modules 1-3) ✅ COMPLETE

**Status**: Production-ready, committed to repository

**Completed Work**:
- ✅ Domain labels (Prometric alignment)
- ✅ Type system (courses.types.ts)
- ✅ Module configuration (module-config.ts)
- ✅ M01: Role of the Nurse Aide (6 lessons)
- ✅ M02: Legal and Ethical Behavior (7 lessons)
- ✅ M03: Communication and Interpersonal Skills (8 lessons)
- ✅ Courses resolver (adaptive logic, progress tracking)
- ✅ Public API (index.ts exports)
- ✅ Architecture documentation

### Phase 2: Skills Lab + Flashcards (Modules 4-7)

**Priority**: High (exam-critical practical skills)

**Scope**:
- M04: Infection Control
- M05: Safety and Emergency Procedures
- M06: Basic Nursing Skills
- M07: Personal Care Skills
- Interactive skills demonstrations
- Video integration for procedural content
- Flashcard system with spaced repetition

### Phase 3: Clinical Domains (Modules 8-14)

**Priority**: Medium (completes curriculum)

**Scope**:
- M08: Restorative Care
- M09: Mental Health and Social Service Needs
- M10: Care of Cognitively Impaired Residents
- M11: Basic Restorative Services
- M12: Resident Rights
- M13: Exam Preparation Strategies
- M14: Final Review and Practice Tests

### Phase 4: Advanced Features

**Priority**: Low (post-launch enhancements)

**Scope**:
- CEU tracking
- Instructor dashboard
- Facility compliance reporting
- Advanced analytics
- Social learning features

---

## 4. Courses Feature Specification

### Data Architecture

**File Structure**:
```
src/features/courses/
├── types/
│   ├── index.ts                    # Re-exports all types
│   ├── courses.types.ts            # Core interfaces
│   └── domain-labels.ts            # Prometric domains
├── data/
│   ├── m01-role-of-nurse-aide.bundle.ts
│   ├── m02-legal-ethical-behavior.bundle.ts
│   ├── m03-communication-interpersonal.bundle.ts
│   └── [M04-M14 coming soon]
├── module-config.ts                # Module metadata
├── courses.resolver.ts             # Business logic
└── index.ts                        # Public API
```

### Core Types

**Prometric Domain Keys**:
```typescript
export type PrometricDomainKey =
  | 'roleResponsibilities'    // I. Role and Responsibilities
  | 'infectionControl'        // II. Infection Control
  | 'safetyEmergency'         // III. Safety and Emergency
  | 'communication'           // IV. Communication
  | 'basicNursing'            // V. Basic Nursing Skills
  | 'personalCare'            // VI. Personal Care
  | 'mentalHealth'            // VII. Mental Health
  | 'basicRestorative'        // VIII. Basic Restorative
  | 'residentRights';         // IX. Resident Rights
```

**Content Block Types**:
```typescript
export type ContentBlockType =
  | 'heading'
  | 'paragraph'
  | 'list'
  | 'callout'
  | 'reflection'
  | 'image'
  | 'video'
  | 'quiz'
  | 'skill-demo';
```

### Adaptive Behavior

**Prerequisite Logic**:
- Modules are locked until prerequisites are completed
- Progress is tracked per lesson
- Confidence levels inform next-lesson recommendations
- "Resume My Course" CTA surfaces the next uncompleted lesson

**Resolver Functions**:
```typescript
// Get adaptive next lesson
export function getNextLesson(learnerState: LearnerState): Lesson | null

// Check prerequisite completion
export function canAccessModule(moduleId: string, learnerState: LearnerState): boolean

// Calculate module confidence
export function getModuleConfidenceLevel(moduleId: string, learnerState: LearnerState): ConfidenceLevel

// Update progress and state
export function completeLessonAndUpdateState(
  lessonId: string,
  confidence: ConfidenceLevel,
  learnerState: LearnerState
): LearnerState
```

---

## 5. Design System

### Color Palette

**Primary Colors** (Faith-aware, warm, professional):
```
Primary Blue: #1E40AF (trust, professionalism)
Primary Purple: #7C3AED (wisdom, faith-aware)
Success Green: #059669 (progress, achievement)
Warning Amber: #D97706 (attention, reflection)
Error Red: #DC2626 (alerts, critical info)
```

**Domain Colors** (from domain-labels.ts):
```
Role & Responsibilities: #3B82F6 (blue-500)
Infection Control: #10B981 (emerald-500)
Safety & Emergency: #EF4444 (red-500)
Communication: #8B5CF6 (violet-500)
Basic Nursing: #06B6D4 (cyan-500)
Personal Care: #EC4899 (pink-500)
Mental Health: #F59E0B (amber-500)
Basic Restorative: #14B8A6 (teal-500)
Resident Rights: #6366F1 (indigo-500)
```

**Neutral Colors**:
```
Background: #FFFFFF (white)
Surface: #F9FAFB (gray-50)
Border: #E5E7EB (gray-200)
Text Primary: #111827 (gray-900)
Text Secondary: #6B7280 (gray-500)
Text Disabled: #9CA3AF (gray-400)
```

### Typography

**Font Families**:
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-heading: 'Inter', sans-serif;
--font-mono: 'Fira Code', 'Courier New', monospace;
```

**Type Scale**:
```
Heading 1 (h1): 2.25rem / 36px - bold - modules titles
Heading 2 (h2): 1.875rem / 30px - bold - lesson titles
Heading 3 (h3): 1.5rem / 24px - semibold - section headers
Heading 4 (h4): 1.25rem / 20px - semibold - subsection headers
Body Large: 1.125rem / 18px - regular - intro text
Body: 1rem / 16px - regular - main content
Body Small: 0.875rem / 14px - regular - captions, meta
Caption: 0.75rem / 12px - regular - timestamps, labels
```

### Spacing System

**Scale** (Tailwind-inspired):
```
0: 0px
1: 0.25rem / 4px
2: 0.5rem / 8px
3: 0.75rem / 12px
4: 1rem / 16px
5: 1.25rem / 20px
6: 1.5rem / 24px
8: 2rem / 32px
10: 2.5rem / 40px
12: 3rem / 48px
16: 4rem / 64px
20: 5rem / 80px
```

### Component Patterns

**Module Card**:
- Rounded corners: 12px
- Shadow: 0 1px 3px rgba(0,0,0,0.1)
- Padding: 24px
- Border: 1px solid domain color
- Hover state: shadow increases, subtle scale (1.02)

**Progress Bar**:
- Height: 8px
- Rounded: 9999px (fully rounded)
- Background: gray-200
- Fill: gradient (domain color to lighter shade)
- Animation: smooth transition (300ms)

**Badge**:
- Small: 20px height, 12px font, 8px padding
- Medium: 24px height, 14px font, 12px padding
- Rounded: 9999px (pill shape)
- Colors: semantic (success, warning, info, coming-soon)

**Callout Box**:
- Background: domain color at 10% opacity
- Border-left: 4px solid domain color
- Padding: 16px
- Border-radius: 8px
- Icon: left-aligned, domain color

**Button Variants**:
```
Primary: solid bg, white text, hover darken
Secondary: outline, domain color text/border, hover fill
Ghost: transparent, hover bg at 10% opacity
Text: no bg, no border, hover underline
```

---

## 6. Data Structure

### Module Bundle Schema

Each module follows this structure:

```typescript
export const M01_ROLE_OF_NURSE_AIDE: ModuleBundle = {
  meta: {
    moduleId: 'M01',
    title: 'Role of the Nurse Aide',
    description: 'Comprehensive overview...',
    estimatedMinutes: 180,
    icon: '🏥',
    coverImage: '/images/modules/m01-cover.jpg',
  },
  lessons: [
    {
      lessonId: 'M01-L01',
      title: 'Introduction to the CNA Role',
      slug: 'introduction-cna-role',
      orderIndex: 1,
      estimatedMinutes: 30,
      contentBlocks: [
        {
          blockId: 'M01-L01-B01',
          type: 'heading',
          content: 'What is a Certified Nursing Assistant?',
          level: 2,
        },
        {
          blockId: 'M01-L01-B02',
          type: 'paragraph',
          content: 'A Certified Nursing Assistant (CNA)...'
        },
        {
          blockId: 'M01-L01-B03',
          type: 'callout',
          calloutType: 'tip',
          content: 'Remember: Your role as a CNA...'
        },
        {
          blockId: 'M01-L01-B04',
          type: 'reflection',
          prompt: 'How do you see yourself serving others...?',
          placeholder: 'Type your reflection here...'
        }
      ],
      progressDefaults: {
        completed: false,
        confidence: 'not-started',
        timeSpentSeconds: 0,
        lastAccessedAt: null,
      },
      domainMapping: {
        primary: 'roleResponsibilities',
        secondary: ['communication'],
      },
    },
    // ... more lessons
  ],
};
```

### Learner State Schema

```typescript
interface LearnerState {
  userId: string;
  moduleProgress: {
    [moduleId: string]: {
      startedAt: Date | null;
      completedAt: Date | null;
      currentLessonId: string | null;
      lessonsCompleted: number;
      totalLessons: number;
      overallConfidence: ConfidenceLevel;
    };
  };
  lessonProgress: {
    [lessonId: string]: {
      completed: boolean;
      confidence: ConfidenceLevel;
      timeSpentSeconds: number;
      lastAccessedAt: Date | null;
      attempts: number;
      reflectionSubmitted: boolean;
    };
  };
  domainMastery: {
    [domainKey in PrometricDomainKey]: {
      lessonsCompleted: number;
      averageConfidence: number;
      prometricReadiness: number; // 0-100%
    };
  };
  preferences: {
    preferredLearningPace: 'slow' | 'medium' | 'fast';
    enableReflections: boolean;
    enableAudio: boolean;
    fontSizeMultiplier: number;
  };
}
```

### Module Configuration Schema

```typescript
interface ModuleConfig {
  moduleId: string;
  title: string;
  shortLabel: string;          // e.g., "M01"
  status: 'available' | 'coming-soon' | 'locked';
  order: number;
  domains: PrometricDomainKey[];
  prerequisites: string[];      // moduleIds
  estimatedHours: number;
  lessonCount: number;
  skillDemos?: number;
  hasQuiz: boolean;
  hasReview: boolean;
  prometricWeight: number;      // 0-100 (exam importance)
  certificationType: 'core' | 'elective' | 'ceu';
}
```

---

## 7. Content Strategy

### Microcopy Principles

**Tone**: Warm, encouraging, faith-aware (not preachy), professional

**Examples**:
- ✅ "You're making great progress! Keep going."
- ✅ "Remember, every resident deserves dignity and respect."
- ✅ "Take a moment to reflect on how this applies to your calling."
- ❌ "You failed this quiz. Try again."
- ❌ "Incorrect answer."

**CTAs**:
- Primary: "Resume My Course" (adaptive, shows next uncompleted lesson)
- Secondary: "Continue Learning", "Start Module", "Review Lesson"
- Encouragement: "You're doing great!", "Almost there!", "Way to go!"

### Content Block Guidelines

**Headings**: Clear, descriptive, actionable
- Good: "How to Perform Hand Hygiene"
- Bad: "Hand Hygiene"

**Paragraphs**: Short (2-4 sentences), scannable
- Use simple language (8th grade reading level)
- Avoid medical jargon unless defined
- Include practical examples

**Lists**: Numbered for procedures, bulleted for features
- Keep items parallel in structure
- Use action verbs

**Callouts**: 4 types
- **Tip** (blue): Helpful hints, best practices
- **Warning** (amber): Important cautions, safety alerts
- **Note** (purple): Additional context, definitions
- **Faith** (green): Reflection prompts, spiritual sensitivity

**Reflections**: Open-ended, thought-provoking
- Connect clinical skills to personal values
- Encourage self-assessment
- Optional but encouraged

### Localization Strategy

**Phase 1**: Texas-specific content
- Texas DADS regulations
- Texas CNA registry requirements
- Local facility examples

**Future**: Multi-state support
- Conditional content based on state
- Configurable regulatory references
- State-specific exam prep

---

## 8. UI/UX Patterns

### Navigation Patterns

**Primary Nav**: Bottom bar (mobile-first)
```
[🏠 Home] [📚 Courses] [🎯 Skills] [📊 Progress] [👤 Profile]
```

**Module Nav**: Vertical sidebar (desktop), horizontal scroll (mobile)
- Shows all 14 modules
- Active module highlighted
- Locked modules grayed out with lock icon
- "Coming Soon" badge on unavailable modules

**Lesson Nav**: Breadcrumb trail
```
Courses > M01: Role of the Nurse Aide > L01: Introduction to the CNA Role
```

### Interaction Patterns

**Progress Tracking**:
- Auto-save on scroll (debounced)
- Manual "Mark as Complete" button at lesson end
- Confidence self-assessment (3 levels):
  - 🔴 "Need more practice"
  - 🟡 "Getting it"
  - 🟢 "Got it!"

**Adaptive "Resume" CTA**:
- Analyzes learner state
- Surfaces next uncompleted lesson
- If all complete, suggests review or next module
- Prominent placement on home screen

**Module Unlock Animation**:
- Smooth fade-in
- Brief celebratory message
- Unlock sound (optional)

**Scroll + Time Tracking**:
- Track time spent per lesson
- Detect idle time (pause timer after 2 min inactive)
- Report engagement metrics

### Responsive Breakpoints

```css
/* Mobile-first approach */
sm: 640px   /* Small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large desktops */
```

**Layout Shifts**:
- Mobile: Single column, stacked cards
- Tablet: 2-column grid for modules
- Desktop: Sidebar + main content

### Accessibility (WCAG 2.1 AA)

**Requirements**:
- Keyboard navigation (tab, arrow keys, enter, space)
- Screen reader support (ARIA labels, landmarks, live regions)
- Color contrast: 4.5:1 for normal text, 3:1 for large text
- Focus indicators: 2px outline, domain color
- Skip links: "Skip to main content", "Skip to navigation"
- Alt text for all images
- Captions/transcripts for videos

**Testing Tools**:
- axe DevTools
- NVDA/JAWS screen readers
- Keyboard-only navigation testing

---

## 9. Implementation Roadmap

### Sprint 1: UI Foundation (Week 1-2)

**Goals**: Build core UI components

**Tasks**:
- [ ] Set up Tailwind CSS with custom theme
- [ ] Create design tokens (colors, spacing, typography)
- [ ] Build atomic components:
  - [ ] Button (4 variants)
  - [ ] Badge (4 sizes, semantic colors)
  - [ ] Card (module card, lesson card)
  - [ ] Progress bar
  - [ ] Callout box (4 types)
- [ ] Build layout components:
  - [ ] Page container
  - [ ] Navigation (primary, breadcrumb)
  - [ ] Sidebar
- [ ] Accessibility audit

### Sprint 2: Courses Feature UI (Week 3-4)

**Goals**: Wire up courses data to UI

**Tasks**:
- [ ] Module list view
  - [ ] Display all modules (M01-M14)
  - [ ] Show status (available, locked, coming soon)
  - [ ] Domain badges
  - [ ] Progress indicators
- [ ] Module detail view
  - [ ] Lesson list
  - [ ] Prerequisites check
  - [ ] "Start Module" / "Continue" CTA
- [ ] Lesson viewer
  - [ ] Render content blocks dynamically
  - [ ] Progress tracking
  - [ ] Confidence self-assessment
  - [ ] "Mark as Complete" button
- [ ] Reflection component
  - [ ] Text area with character limit
  - [ ] Save/skip options
  - [ ] Private note indicator

### Sprint 3: State Management (Week 5)

**Goals**: Integrate resolver logic with UI

**Tasks**:
- [ ] Set up state management (Context API / Zustand / Redux)
- [ ] Wire up courses resolver
- [ ] Implement adaptive logic:
  - [ ] getNextLesson()
  - [ ] canAccessModule()
  - [ ] completeLessonAndUpdateState()
- [ ] Build "Resume My Course" CTA
- [ ] Progress persistence (LocalStorage / backend API)

### Sprint 4: Polish & Testing (Week 6)

**Goals**: QA, accessibility, performance

**Tasks**:
- [ ] Cross-browser testing (Chrome, Safari, Firefox, Edge)
- [ ] Mobile testing (iOS, Android)
- [ ] Accessibility audit (axe, NVDA)
- [ ] Performance optimization:
  - [ ] Lazy load lesson content
  - [ ] Image optimization
  - [ ] Code splitting
- [ ] Bug fixes
- [ ] Documentation updates

### Sprint 5+: Phase 2 Features

**Flashcards** (Week 7-8):
- [ ] Card component
- [ ] Spaced repetition algorithm
- [ ] Domain-specific decks
- [ ] Progress tracking

**Skills Lab** (Week 9-12):
- [ ] Video player component
- [ ] Step-by-step skill demos
- [ ] Interactive checklists
- [ ] Skill assessment quizzes

---

## 10. Technical Stack

### Frontend Framework

**Primary**: React 18+ with TypeScript
- Why: Component-based, strong typing, large ecosystem

**Build Tool**: Vite
- Why: Fast HMR, modern dev experience

**Alternative**: React Native (if considering mobile apps)

### Styling

**Primary**: Tailwind CSS (implied by color tokens)
- Why: Utility-first, highly customizable, excellent docs

**Component Library** (optional): Headless UI / Radix UI
- Why: Accessible primitives, unstyled, composable

**Alternative**: Styled Components / Emotion (if CSS-in-JS preferred)

### State Management

**Recommendation**: TBD (Context API, Redux, or Zustand)

**Comparison**:
- **Context API**: Built-in, simple, good for small/medium apps
- **Redux Toolkit**: Mature, devtools, good for complex state
- **Zustand**: Lightweight, minimal boilerplate, growing popularity

**Decision Criteria**:
- App complexity (lean toward Context or Zustand for MVP)
- Team familiarity
- Devtools requirements

### Storage

**Phase 1**: LocalStorage (with optional backend sync)
- Learner progress
- Preferences
- Reflection notes

**Phase 2**: Backend API + Database
- PostgreSQL / Supabase (if open-source)
- Firebase (if rapid prototyping)
- Custom REST/GraphQL API

### Analytics

**Track**: Learner progress, completion rates, confidence levels
**Tools**: Mixpanel, Amplitude, or custom dashboard

### Offline Support

**Service Workers** + **IndexedDB**:
- Cache module content
- Sync progress when online
- Progressive Web App (PWA) capabilities

### Accessibility

**Testing**: axe DevTools, WAVE, manual screen reader testing
**Compliance**: WCAG 2.1 AA compliance

### Recommendations

- **Mobile-First**: React Native or Progressive Web App (PWA)
- **Offline Support**: Service Workers + IndexedDB
- **Analytics**: Track learner progress, completion rates, confidence levels
- **Accessibility**: WCAG 2.1 AA compliance

---

## Appendix A: File Inventory

### Created Files (Phase 1 - Complete)

**Types Layer**:
- ✅ `src/features/courses/types/courses.types.ts` - Core interfaces and types
- ✅ `src/features/courses/types/domain-labels.ts` - Prometric domain taxonomy
- ✅ `src/features/courses/types/index.ts` - Type exports

**Configuration Layer**:
- ✅ `src/features/courses/module-config.ts` - Module metadata for M01-M14

**Content Layer**:
- ✅ `src/features/courses/data/m01-role-of-nurse-aide.bundle.ts` - 6 lessons
- ✅ `src/features/courses/data/m02-legal-ethical-behavior.bundle.ts` - 7 lessons
- ✅ `src/features/courses/data/m03-communication-interpersonal.bundle.ts` - 8 lessons

**Business Logic Layer**:
- ✅ `src/features/courses/courses.resolver.ts` - Adaptive logic, progress tracking

**Public API**:
- ✅ `src/features/courses/index.ts` - Centralized exports

**Documentation**:
- ✅ `src/features/courses/README.md` - Feature documentation
- ✅ `docs/ARCHITECTURE.md` - This document

### Pending Files (Phase 2+)

**Content Bundles**:
- ⏳ M04: Infection Control
- ⏳ M05: Safety and Emergency
- ⏳ M06: Basic Nursing Skills
- ⏳ M07: Personal Care Skills
- ⏳ M08: Restorative Care
- ⏳ M09: Mental Health
- ⏳ M10: Cognitively Impaired Care
- ⏳ M11: Basic Restorative Services
- ⏳ M12: Resident Rights
- ⏳ M13: Exam Strategies
- ⏳ M14: Final Review

**UI Components** (to be created):
- ⏳ `src/components/ui/Button.tsx`
- ⏳ `src/components/ui/Badge.tsx`
- ⏳ `src/components/ui/Card.tsx`
- ⏳ `src/components/ui/ProgressBar.tsx`
- ⏳ `src/components/ui/CalloutBox.tsx`
- ⏳ `src/components/courses/ModuleCard.tsx`
- ⏳ `src/components/courses/LessonViewer.tsx`
- ⏳ `src/components/courses/ReflectionPrompt.tsx`
- ⏳ `src/components/courses/DomainBadge.tsx`
- ⏳ `src/components/navigation/Breadcrumb.tsx`

**State Management**:
- ⏳ `src/store/courses-context.tsx` (or zustand/redux setup)
- ⏳ `src/hooks/useCourses.ts`
- ⏳ `src/hooks/useLearnerProgress.ts`

---

## Appendix B: Key Terms & Abbreviations

**CNA**: Certified Nursing Assistant
**DON**: Director of Nursing
**CEU**: Continuing Education Unit
**NNAAP**: National Nurse Aide Assessment Program
**DADS**: Texas Department of Aging and Disability Services
**PWA**: Progressive Web App
**WCAG**: Web Content Accessibility Guidelines
**ARIA**: Accessible Rich Internet Applications
**CTA**: Call to Action
**UI**: User Interface
**UX**: User Experience
**API**: Application Programming Interface
**HMR**: Hot Module Replacement

---

## Appendix C: Decision Rationale Summary

All major architectural decisions were made based on the following principles:

1. **Curriculum-First**: Aligned with Prometric/NNAAP standards before adding peripheral features
2. **Content/Config Separation**: Maintainability and scalability for future content updates
3. **Adaptive Learning**: Prerequisite-based unlocking and confidence-driven recommendations
4. **Faith-Aware Tone**: Warm, encouraging microcopy with spiritual sensitivity (not preachy)
5. **Accessibility**: WCAG 2.1 AA compliance from day one
6. **Mobile-First**: Optimized for learners on phones and tablets
7. **Offline Support**: Service workers for uninterrupted learning
8. **Type Safety**: Strong TypeScript interfaces prevent runtime errors
9. **Module Bundles Over Single Config**: Maintainability and code organization
10. **Resume My Course CTA**: Primary navigation action surfaces next uncompleted lesson

---

## Appendix D: Future Considerations

### Multi-Tenancy
- Support for multiple training organizations
- White-label branding options
- Custom domain mapping

### Internationalization (i18n)
- Multi-language support (Spanish, Vietnamese, etc.)
- RTL language support
- Localized content bundles

### Advanced Analytics
- Predictive modeling for exam success
- Cohort analysis
- Instructor dashboards
- Facility compliance reports

### Social Learning
- Study groups
- Peer-to-peer support
- Discussion forums
- Mentorship matching

### Gamification
- Badges and achievements
- Leaderboards (opt-in)
- Streaks and milestones
- Certificate of completion

### Integration Ecosystem
- LMS integration (Canvas, Blackboard, Moodle)
- State registry APIs
- Facility management systems
- Calendar/scheduling tools

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|----------|
| 1.0.0 | July 1, 2026 | Texas CNA Academy Team | Initial comprehensive architecture document. Includes M01-M03 implementation, design system, data structures, UI/UX patterns, and phased roadmap. |

---

## Contact & Contribution

For questions, suggestions, or contributions to this architecture:

- **Repository**: [Texas-CNA-Academy-App](https://github.com/lindalcastillo2779-web/Texas-CNA-Academy-App)
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Pull Requests**: Follow the contribution guidelines in CONTRIBUTING.md
- **Documentation**: Keep this document updated as architecture evolves

---

**End of Architecture Documentation**

*Last Updated: July 1, 2026*
*Status: ✅ Phase 1 Complete | 📋 Ready for UI Implementation*
**Document Owner**: Texas CNA Academy Development Team  
**Last Updated**: July 1, 2026  
**Next Review**: Upon Phase 1B completion
