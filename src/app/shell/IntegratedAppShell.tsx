import React, { useEffect, useMemo, useState } from 'react';
import {
  getDomainLabel,
  getModulesWithProgress,
  getNextLesson,
} from '../../features/courses';
import { goToPortalSignup } from './portalActions';
import {
  getPortalDisplayName,
  loadStudentPortalRecord,
  type PortalProfile,
  type StudentPortalRecord,
} from './portalData';

type AppView = 'home' | 'courses' | 'skills' | 'review' | 'community' | 'more';

type NavItem = {
  key: AppView;
  label: string;
  icon: string;
};

type TaskItem = {
  title: string;
  detail: string;
  status: string;
  view: AppView;
};

type LearnerModuleProgress = {
  moduleId: string;
  completedLessonIds: string[];
  totalLessons: number;
  completedLessons: number;
  percentComplete: number;
  lastAccessedAt: string;
  status: 'completed' | 'in-progress' | 'not-started';
};

type DemoLearnerState = {
  completedModuleIds: string[];
  moduleProgress: Record<string, LearnerModuleProgress>;
};

type DashboardModule = {
  moduleId: string;
  moduleNumber: number;
  title: string;
  description: string;
  estimatedMinutes: number;
  clinicalSkillsCount: number;
  primaryDomain: string;
  status: string;
  isUnlocked: boolean;
  progress: LearnerModuleProgress;
};

const NAV_ITEMS: NavItem[] = [
  { key: 'home', label: 'Home', icon: '⌂' },
  { key: 'courses', label: 'Courses', icon: '▣' },
  { key: 'skills', label: 'Skills', icon: '✚' },
  { key: 'review', label: 'Review', icon: '◫' },
  { key: 'community', label: 'Community', icon: '🤝' },
  { key: 'more', label: 'More', icon: '⋯' },
];

const DEMO_LEARNER_STATE: DemoLearnerState = {
  completedModuleIds: ['M01', 'M02'],
  moduleProgress: {
    M01: {
      moduleId: 'M01',
      completedLessonIds: ['M01-L01', 'M01-L02', 'M01-L03', 'M01-L04', 'M01-L05', 'M01-L06'],
      totalLessons: 6,
      completedLessons: 6,
      percentComplete: 100,
      lastAccessedAt: '2026-06-28T08:30:00Z',
      status: 'completed',
    },
    M02: {
      moduleId: 'M02',
      completedLessonIds: ['M02-L01', 'M02-L02', 'M02-L03', 'M02-L04', 'M02-L05', 'M02-L06', 'M02-L07'],
      totalLessons: 7,
      completedLessons: 7,
      percentComplete: 100,
      lastAccessedAt: '2026-06-29T14:15:00Z',
      status: 'completed',
    },
    M03: {
      moduleId: 'M03',
      completedLessonIds: ['M03-L01', 'M03-L02', 'M03-L03', 'M03-L04'],
      totalLessons: 8,
      completedLessons: 4,
      percentComplete: 50,
      lastAccessedAt: '2026-07-02T18:00:00Z',
      status: 'in-progress',
    },
    M04: {
      moduleId: 'M04',
      completedLessonIds: ['M04-L01', 'M04-L02'],
      totalLessons: 8,
      completedLessons: 2,
      percentComplete: 25,
      lastAccessedAt: '2026-07-01T09:45:00Z',
      status: 'in-progress',
    },
  },
};

const TODAY_TASKS: TaskItem[] = [
  {
    title: 'Resume communication module',
    detail: 'Finish the next lesson and keep your study streak active.',
    status: '15 min',
    view: 'courses',
  },
  {
    title: 'Review infection control misses',
    detail: 'Target the weakest domain before your next quiz.',
    status: '8 cards due',
    view: 'review',
  },
  {
    title: 'Practice one clinical skill',
    detail: 'Run a handwashing or transfer readiness check today.',
    status: '1 skill focus',
    view: 'skills',
  },
];

const GOALS = [
  { title: 'Pass the written exam in 30 days', progress: 78, note: 'You are on pace this week.' },
  { title: 'Finish 3 modules this month', progress: 67, note: 'One more module completes the goal.' },
  { title: 'Keep CEU records organized', progress: 50, note: 'Upload the next certificate after completion.' },
];

const REVIEW_DECKS = [
  { title: 'Infection control', due: '8 cards due today', mastery: 62, action: 'Spaced repetition priority' },
  { title: 'Safety and emergency', due: '5 cards due tomorrow', mastery: 74, action: 'Adaptive quiz recommended' },
  { title: 'Resident rights', due: 'Mastered this week', mastery: 91, action: 'Light refresh only' },
];

const SKILL_TRACKER = [
  { title: 'Handwashing', readiness: 92, notes: 'Strong sequencing. Keep wet-hand timing consistent.' },
  { title: 'Transfer: bed to wheelchair', readiness: 71, notes: 'Focus on lock brakes and clear cueing.' },
  { title: 'Vital signs and documentation', readiness: 64, notes: 'Recheck normal ranges before testing.' },
];

const TOOL_CARDS = [
  { title: 'Exam Prep', status: 'Live now', copy: 'Use adaptive quizzes by domain and subtopic.' },
  { title: 'Community Hub', status: 'Available', copy: 'Match with mentors, practice partners, study groups, and local workforce opportunities.' },
  { title: 'CEU Tracker', status: 'Live now', copy: 'Track annual credits and upload proof faster.' },
  { title: 'Renewal Check', status: 'Live now', copy: 'See readiness, deadlines, and missing steps.' },
  { title: 'Buddy', status: 'Next up', copy: 'Turn chat into study plans, explanations, reminders, and community nudges.' },
  { title: 'Document Vault', status: 'Recommended', copy: 'Store certificates, completion records, and forms.' },
  { title: 'Instructor + Admin Portals', status: 'Live now', copy: 'Shared role-specific dashboards now use the same unified portal foundation.' },
];

const COMMUNITY_MATCHES = [
  {
    name: 'Angela R.',
    role: 'CNA Mentor',
    focus: 'Transfer safety, infection control, test-day confidence',
    availability: 'Virtual evenings',
  },
  {
    name: 'Prof. Baker',
    role: 'Instructor',
    focus: 'Study planning, remediation, module check-ins',
    availability: 'Wednesday office hours',
  },
];

const COMMUNITY_POSTS = [
  {
    title: 'Weekly infection control study circle',
    meta: 'Houston + virtual · 8 learners waiting',
    detail: 'Join focused review blocks for PPE, isolation, and common quiz misses.',
    status: 'Study group',
  },
  {
    title: 'Prometric skills practice partner search',
    meta: 'San Antonio · transfer + vital signs',
    detail: 'Pair with someone to rehearse high-risk clinical skill sequences before lab day.',
    status: 'Practice partner',
  },
  {
    title: 'Facility shadow day + hiring event',
    meta: 'Fort Worth · entry-level opportunity',
    detail: 'Meet local facility leaders and learn what they want from new CNA candidates.',
    status: 'Opportunity',
  },
];

function formatLessonLabel(lessonId: string): string {
  const match = lessonId.match(/^[A-Z0-9]+-L(\d+)$/);
  if (!match) {
    return lessonId;
  }

  return `Lesson ${match[1]}`;
}

function ProgressBar({ value, tone = 'accent' }: { value: number; tone?: 'accent' | 'success' | 'navy' }) {
  return (
    <div className="progress-meter" aria-hidden="true">
      <span className={`progress-meter-bar tone-${tone}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  );
}

function SectionHeader({
  eyebrow,
  title,
  copy,
}: {
  eyebrow: string;
  title: string;
  copy?: string;
}) {
  return (
    <div className="section-header">
      <div>
        <div className="section-kicker">{eyebrow}</div>
        <h2 className="section-title">{title}</h2>
        {copy ? <p className="section-copy">{copy}</p> : null}
      </div>
    </div>
  );
}

function HomeScreen({
  onNavigate,
  courseworkCompletion,
  completedModules,
  nextLessonSummary,
  ceuRemainingSummary,
  weakestDomainKey,
  examReadiness,
  ceuCompletion,
}: {
  onNavigate: (view: AppView) => void;
  courseworkCompletion: number;
  completedModules: number;
  nextLessonSummary: string;
  ceuRemainingSummary: string;
  weakestDomainKey: string;
  examReadiness: number;
  ceuCompletion: number;
}) {
  const weakestDomain = getDomainLabel(weakestDomainKey as Parameters<typeof getDomainLabel>[0]);

  return (
    <div className="screen-stack">
      <section className="hero-card">
        <div className="eyebrow">Student portal</div>
        <div className="hero-grid">
          <div>
            <h1>Your CNA command center.</h1>
            <p className="hero-copy">
              See what to study next, which skill needs attention, and whether you are on track for testing and renewal.
            </p>
            <div className="hero-actions">
              <button className="btn btn-primary" type="button" onClick={() => onNavigate('courses')}>
                Continue learning
              </button>
              <button className="btn btn-secondary" type="button" onClick={() => onNavigate('review')}>
                Review weak area
              </button>
            </div>
          </div>

          <aside className="section-card emphasis-card">
            <span className="metric-label">Study next</span>
            <strong className="metric-value">{nextLessonSummary}</strong>
            <p className="metric-copy">Finish this lesson to stay on pace for your 30-day exam goal.</p>
            <ProgressBar value={courseworkCompletion} />
            <div className="progress-meta">
              <span>{courseworkCompletion}% coursework complete</span>
              <span>{completedModules} modules finished</span>
            </div>
          </aside>
        </div>
      </section>

      <section className="metric-grid">
        <article className="metric-card">
          <span className="metric-label">Weakest domain</span>
          <strong className="metric-value">{weakestDomain.shortLabel}</strong>
          <p className="metric-copy">{weakestDomain.description}</p>
        </article>
        <article className="metric-card">
          <span className="metric-label">Exam readiness</span>
          <strong className="metric-value">{Math.round(examReadiness)}%</strong>
          <p className="metric-copy">Strong pace overall. Keep drilling infection control and transfer safety.</p>
        </article>
        <article className="metric-card">
          <span className="metric-label">CEU remaining</span>
          <strong className="metric-value">{ceuRemainingSummary}</strong>
          <p className="metric-copy">Stay ahead on CEU uploads and renewal proof collection.</p>
        </article>
      </section>

      <section className="panel-grid">
        <article className="section-card">
          <SectionHeader eyebrow="Today" title="Priority tasks" copy="One clear plan for the next study session." />
          <div className="task-list">
            {TODAY_TASKS.map((task) => (
              <button key={task.title} type="button" className="task-item" onClick={() => onNavigate(task.view)}>
                <div className="task-copy">
                  <span className="task-kicker">{task.status}</span>
                  <strong className="task-title">{task.title}</strong>
                  <span className="task-meta">{task.detail}</span>
                </div>
                <span className="task-action">Open</span>
              </button>
            ))}
          </div>
        </article>

        <article className="section-card">
          <SectionHeader eyebrow="Snapshot" title="Readiness overview" copy="Focus on the signals that matter most this week." />
          <div className="insight-stack">
            <div>
              <div className="progress-meta"><span>Coursework</span><span>{courseworkCompletion}%</span></div>
              <ProgressBar value={courseworkCompletion} tone="navy" />
            </div>
            <div>
              <div className="progress-meta"><span>Exam readiness</span><span>{Math.round(examReadiness)}%</span></div>
              <ProgressBar value={examReadiness} tone={examReadiness >= 70 ? 'success' : 'accent'} />
            </div>
            <div>
              <div className="progress-meta"><span>CEU progress</span><span>{Math.round(ceuCompletion)}%</span></div>
              <ProgressBar value={ceuCompletion} />
            </div>
          </div>
        </article>
      </section>

      <section className="section-card">
        <SectionHeader eyebrow="Goals" title="Momentum this month" copy="Goals, reminders, and progress should live in the same place." />
        <div className="goal-grid">
          {GOALS.map((goal) => (
            <article key={goal.title} className="goal-card">
              <strong>{goal.title}</strong>
              <p>{goal.note}</p>
              <div className="progress-meta"><span>Progress</span><span>{goal.progress}%</span></div>
              <ProgressBar value={goal.progress} />
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function CoursesScreen({
  modules,
  nextLessonSummary,
}: {
  modules: DashboardModule[];
  nextLessonSummary: string;
}) {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader
          eyebrow="Courses"
          title="Personalized learning path"
          copy="The portal now uses real course metadata so the dashboard and module list stay aligned."
        />
        <div className="focus-banner">
          <span className="badge badge-accent">Recommended next step</span>
          <strong>{nextLessonSummary}</strong>
        </div>
      </section>

      <section className="module-grid" aria-label="Course modules">
        {modules.map((module) => (
          <article key={module.moduleId} className="module-card">
            <div className="badge-row">
              <span className="badge badge-muted">Module {module.moduleNumber}</span>
              <span className={`badge ${module.isUnlocked ? 'badge-success' : 'badge-warning'}`}>
                {module.isUnlocked ? 'Unlocked' : 'Locked'}
              </span>
            </div>
            <h3 className="module-title">{module.title}</h3>
            <p className="module-copy">{module.description}</p>
            <div className="progress-meta">
              <span>{module.progress.completedLessons}/{module.progress.totalLessons} lessons</span>
              <span>{Math.round(module.progress.percentComplete)}%</span>
            </div>
            <ProgressBar value={module.progress.percentComplete} tone={module.progress.percentComplete >= 75 ? 'success' : 'accent'} />
            <div className="module-footer">
              <span>{module.estimatedMinutes} min</span>
              <span>{module.clinicalSkillsCount} skills</span>
              <span>{module.primaryDomain}</span>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

function SkillsScreen() {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader
          eyebrow="Clinical skills"
          title="Skills mastery tracker"
          copy="Track readiness, common misses, and the next coaching focus for each high-value skill."
        />
      </section>

      <section className="card-grid">
        {SKILL_TRACKER.map((skill) => (
          <article key={skill.title} className="section-card">
            <span className="metric-label">Pass-readiness</span>
            <h3 className="module-title">{skill.title}</h3>
            <p className="module-copy">{skill.notes}</p>
            <div className="progress-meta"><span>Confidence</span><span>{skill.readiness}%</span></div>
            <ProgressBar value={skill.readiness} tone={skill.readiness >= 80 ? 'success' : 'accent'} />
          </article>
        ))}
      </section>

      <section className="panel-grid">
        <article className="section-card">
          <SectionHeader eyebrow="Exam day" title="Common misses to prevent" />
          <ul className="info-list">
            <li>Lock wheelchair brakes before any transfer movement.</li>
            <li>Keep resident communication clear before touching equipment.</li>
            <li>Document readings immediately after taking vital signs.</li>
          </ul>
        </article>
        <article className="section-card">
          <SectionHeader eyebrow="Coaching" title="What to practice next" />
          <ul className="info-list">
            <li>Run one timed transfer simulation this afternoon.</li>
            <li>Repeat handwashing sequence with wet-hand timing.</li>
            <li>Review normal blood pressure ranges before the next quiz.</li>
          </ul>
        </article>
      </section>
    </div>
  );
}

function ReviewScreen({ reviewDecks }: { reviewDecks: typeof REVIEW_DECKS }) {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader
          eyebrow="Review center"
          title="Adaptive study + spaced repetition"
          copy="The review experience should prioritize weak areas, due flashcards, and just-in-time exam drills."
        />
      </section>

      <section className="card-grid">
        {reviewDecks.map((deck) => (
          <article key={deck.title} className="section-card">
            <span className="metric-label">{deck.due}</span>
            <h3 className="module-title">{deck.title}</h3>
            <p className="module-copy">{deck.action}</p>
            <div className="progress-meta"><span>Mastery</span><span>{deck.mastery}%</span></div>
            <ProgressBar value={deck.mastery} tone={deck.mastery >= 85 ? 'success' : 'accent'} />
          </article>
        ))}
      </section>

      <section className="panel-grid">
        <article className="section-card">
          <SectionHeader eyebrow="Smart review" title="What excellent feels like" />
          <ul className="info-list">
            <li>Auto-schedule cards based on mistakes and recall confidence.</li>
            <li>Serve more quiz items from low-mastery domains.</li>
            <li>Recommend the next lesson when a pattern of misses appears.</li>
          </ul>
        </article>
        <article className="section-card">
          <SectionHeader eyebrow="This week" title="Recommended review cadence" />
          <ul className="info-list">
            <li>Mon/Wed/Fri: infection control flashcards</li>
            <li>Tue/Thu: mixed safety quiz blocks</li>
            <li>Weekend: one clinical skill simulation + debrief</li>
          </ul>
        </article>
      </section>
    </div>
  );
}

function CommunityScreen({
  weakestDomainKey,
  communityMatches,
  communityPosts,
  recommendedActions,
}: {
  weakestDomainKey: string;
  communityMatches: typeof COMMUNITY_MATCHES;
  communityPosts: typeof COMMUNITY_POSTS;
  recommendedActions: string[];
}) {
  const weakestDomain = getDomainLabel(weakestDomainKey as Parameters<typeof getDomainLabel>[0]);

  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader
          eyebrow="Community hub"
          title="Find mentors, practice partners, and pathways into work"
          copy="Turn your next weak area into a connection plan with people and opportunities around you."
        />
        <div className="focus-banner">
          <span className="badge badge-accent">Best next match</span>
          <strong>Ask for help in {weakestDomain.shortLabel}</strong>
        </div>
      </section>

      <section className="card-grid">
        {communityMatches.map((match) => (
          <article key={match.name} className="section-card">
            <span className="metric-label">{match.role}</span>
            <h3 className="module-title">{match.name}</h3>
            <p className="module-copy">{match.focus}</p>
            <div className="focus-banner">
              <strong>Availability</strong>
              <span>{match.availability}</span>
            </div>
          </article>
        ))}
      </section>

      <section className="panel-grid">
        <article className="section-card">
          <SectionHeader eyebrow="Recommended" title="Community actions this week" />
          <ul className="info-list">
            {(recommendedActions.length ? recommendedActions : [
              `Post a mentor request tied to your weakest domain: ${weakestDomain.shortLabel}.`,
              'Join one study group before your next quiz attempt.',
              'Save one local opportunity so your exam plan also builds career momentum.',
            ]).map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ul>
        </article>
        <article className="section-card">
          <SectionHeader eyebrow="Board highlights" title="What people are posting now" />
          <div className="timeline-list">
            {communityPosts.map((post) => (
              <article key={post.title} className="timeline-item">
                <div className="timeline-dot is-success" />
                <div className="timeline-copy">
                  <strong>{post.title}</strong>
                  <p>{post.detail}</p>
                </div>
                <span className="status-pill is-muted">{post.status}</span>
              </article>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}

function MoreScreen() {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader
          eyebrow="Platform roadmap"
          title="More tools in one unified experience"
          copy="These are the product areas that should feel connected instead of split across separate pages and prototypes."
        />
      </section>

      <section className="card-grid">
        {TOOL_CARDS.map((tool) => (
          <article key={tool.title} className="section-card compact-card">
            <div className="badge-row">
              <span className="badge badge-muted">{tool.status}</span>
            </div>
            <h3 className="module-title">{tool.title}</h3>
            <p className="module-copy">{tool.copy}</p>
          </article>
        ))}
      </section>
    </div>
  );
}

function renderView(view: AppView, args: {
  onNavigate: (view: AppView) => void;
  courseworkCompletion: number;
  completedModules: number;
  nextLessonSummary: string;
  ceuRemainingSummary: string;
  weakestDomainKey: string;
  modules: DashboardModule[];
  examReadiness: number;
  ceuCompletion: number;
  reviewDecks: typeof REVIEW_DECKS;
  communityMatches: typeof COMMUNITY_MATCHES;
  communityPosts: typeof COMMUNITY_POSTS;
  communityActions: string[];
}) {
  switch (view) {
    case 'home':
      return (
        <HomeScreen
          onNavigate={args.onNavigate}
          courseworkCompletion={args.courseworkCompletion}
          completedModules={args.completedModules}
          nextLessonSummary={args.nextLessonSummary}
          ceuRemainingSummary={args.ceuRemainingSummary}
          weakestDomainKey={args.weakestDomainKey}
          examReadiness={args.examReadiness}
          ceuCompletion={args.ceuCompletion}
        />
      );
    case 'courses':
      return <CoursesScreen modules={args.modules} nextLessonSummary={args.nextLessonSummary} />;
    case 'skills':
      return <SkillsScreen />;
    case 'review':
      return <ReviewScreen reviewDecks={args.reviewDecks} />;
    case 'community':
      return (
        <CommunityScreen
          weakestDomainKey={args.weakestDomainKey}
          communityMatches={args.communityMatches}
          communityPosts={args.communityPosts}
          recommendedActions={args.communityActions}
        />
      );
    case 'more':
      return <MoreScreen />;
    default:
      return null;
  }
}

export function IntegratedAppShell() {
  const [currentView, setCurrentView] = useState<AppView>('home');
  const [portalProfile, setPortalProfile] = useState<PortalProfile | null>(null);
  const [portalStudent, setPortalStudent] = useState<StudentPortalRecord | null>(null);
  const learnerState = DEMO_LEARNER_STATE as unknown as Parameters<typeof getModulesWithProgress>[0];

  const modulesWithProgress = useMemo(
    () => getModulesWithProgress(learnerState).filter((module) => module.status === 'available') as DashboardModule[],
    [learnerState]
  );

  const weakestDomainKey = useMemo(() => {
    const weakestModule = [...modulesWithProgress]
      .filter((module) => module.progress.totalLessons > 0)
      .sort((left, right) => left.progress.percentComplete - right.progress.percentComplete)[0];

    return weakestModule?.primaryDomain ?? 'INFECT';
  }, [modulesWithProgress]);

  const nextLessonSummary = useMemo(() => {
    const nextLesson = getNextLesson(learnerState);
    if (!nextLesson) {
      return 'Prometric Exam Preparation';
    }

    const module = modulesWithProgress.find((item) => item.moduleId === nextLesson.moduleId);
    const lessonLabel = formatLessonLabel(nextLesson.lessonId);

    return `${module?.title ?? nextLesson.moduleId} · ${lessonLabel}`;
  }, [learnerState, modulesWithProgress]);

  const courseworkCompletion = useMemo(() => {
    const totals = modulesWithProgress.reduce(
      (acc, module) => {
        acc.complete += module.progress.completedLessons;
        acc.total += module.progress.totalLessons;
        return acc;
      },
      { complete: 0, total: 0 }
    );

    return totals.total ? Math.round((totals.complete / totals.total) * 100) : 0;
  }, [modulesWithProgress]);

  const completedModules = useMemo(
    () => modulesWithProgress.filter((module) => module.progress.status === 'completed').length,
    [modulesWithProgress]
  );

  const examReadiness = portalStudent?.quiz.readinessScore ?? 78;
  const ceuCompletion = portalStudent
    ? Math.round((portalStudent.ceu.earnedHours / Math.max(1, portalStudent.ceu.requiredHours)) * 100)
    : 50;
  const ceuRemainingSummary = portalStudent ? `${portalStudent.ceu.remainingHours.toFixed(1)} hrs` : '12.0 hrs';

  const reviewDecks = useMemo(() => {
    if (!portalStudent?.quiz.statsByDomain.length) {
      return REVIEW_DECKS;
    }

    return [...portalStudent.quiz.statsByDomain]
      .sort((left, right) => left.avgPct - right.avgPct)
      .slice(0, 3)
      .map((stat) => ({
        title: stat.domain,
        due: `${stat.attempts} quiz attempt${stat.attempts === 1 ? '' : 's'} logged`,
        mastery: Math.round(stat.avgPct),
        action: stat.bestPct >= 85 ? 'Keep this domain warm with light review.' : 'Prioritize this domain in your next review block.',
      }));
  }, [portalStudent]);

  const communityMatches = useMemo(() => {
    if (!portalStudent?.community.mentorMatches.length) {
      return COMMUNITY_MATCHES;
    }

    return portalStudent.community.mentorMatches.slice(0, 4).map((match) => ({
      name: match.name,
      role: match.role.toUpperCase(),
      focus: match.interest_areas || 'Mentoring, exam prep, and learner support',
      availability: match.availability || match.city || 'Availability not listed',
    }));
  }, [portalStudent]);

  const communityPosts = useMemo(() => {
    if (!portalStudent?.community.recommendedPosts.length) {
      return COMMUNITY_POSTS;
    }

    return portalStudent.community.recommendedPosts.slice(0, 4).map((post) => ({
      title: post.title,
      meta: `${post.location || 'Texas CNA Academy'} · ${post.post_type.replaceAll('_', ' ')}`,
      detail: post.description,
      status: post.post_type.replaceAll('_', ' '),
    }));
  }, [portalStudent]);

  const communityActions = portalStudent?.community.recommendedActions ?? [];

  useEffect(() => {
    const syncFromHash = () => {
      const rawHash = window.location.hash.replace('#', '');
      if (NAV_ITEMS.some((item) => item.key === rawHash)) {
        setCurrentView(rawHash as AppView);
      }
    };

    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => window.removeEventListener('hashchange', syncFromHash);
  }, []);

  useEffect(() => {
    let isMounted = true;

    loadStudentPortalRecord()
      .then((result) => {
        if (!isMounted) {
          return;
        }
        setPortalProfile(result.profile);
        setPortalStudent(result.student);
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }
        setPortalProfile(null);
        setPortalStudent(null);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const navigate = (view: AppView) => {
    setCurrentView(view);
    window.history.replaceState(null, '', `#${view}`);
  };

  const currentTitle = useMemo(() => {
    switch (currentView) {
      case 'home':
        return 'Today dashboard';
      case 'courses':
        return 'Learning path';
      case 'skills':
        return 'Skills mastery';
      case 'review':
        return 'Review center';
      case 'community':
        return 'Community hub';
      case 'more':
        return 'More tools';
      default:
        return 'Texas CNA Academy';
    }
  }, [currentView]);

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <header className="topbar">
        <div className="topbar-copy">
          <div className="brand-kicker">Texas CNA Academy</div>
          <div className="topbar-title">{currentTitle}</div>
          <p className="topbar-subtitle">A unified student portal for courses, readiness, skills, and renewal support.</p>
        </div>
        <div className="topbar-actions">
          <span className="status-chip">{portalStudent?.statusChip ?? '30-day plan active'}</span>
          <button
            className="profile-chip"
            type="button"
            aria-label="Student profile"
            onClick={() => goToPortalSignup('student')}
          >
            {portalStudent?.name ?? getPortalDisplayName(portalProfile)}
          </button>
        </div>
      </header>

      <main id="main-content" className="main-content">
        {renderView(currentView, {
          onNavigate: navigate,
          courseworkCompletion,
          completedModules,
          nextLessonSummary,
          ceuRemainingSummary,
          weakestDomainKey,
          modules: modulesWithProgress,
          examReadiness,
          ceuCompletion,
          reviewDecks,
          communityMatches,
          communityPosts,
          communityActions,
        })}
      </main>

      <nav className="bottom-nav bottom-nav-6" aria-label="Primary">
        {NAV_ITEMS.map((item) => {
          const isActive = item.key === currentView;

          return (
            <button
              key={item.key}
              type="button"
              className={`bottom-nav-item ${isActive ? 'is-active' : ''}`}
              onClick={() => navigate(item.key)}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="bottom-nav-icon" aria-hidden="true">
                {item.icon}
              </span>
              <span className="bottom-nav-label">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
