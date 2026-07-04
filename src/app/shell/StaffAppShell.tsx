import React, { useEffect, useMemo, useState } from 'react';

type StaffView = 'students' | 'schedule' | 'grades' | 'community' | 'resources';

type StaffNavItem = {
  key: StaffView;
  label: string;
  icon: string;
};

const NAV_ITEMS: StaffNavItem[] = [
  { key: 'students', label: 'Students', icon: '👥' },
  { key: 'schedule', label: 'Schedule', icon: '🗓' },
  { key: 'grades', label: 'Grades', icon: '📘' },
  { key: 'community', label: 'Community', icon: '🤝' },
  { key: 'resources', label: 'Resources', icon: '📄' },
];

const STUDENT_METRICS = [
  { label: 'Total students', value: '24', detail: 'Across current active cohorts.' },
  { label: 'Passing rate', value: '87%', detail: 'Most learners are staying on pace.' },
  { label: 'Average progress', value: '71%', detail: 'Coaching focus is Module 4 readiness.' },
];

const STUDENT_ROSTER = [
  { name: 'Maria Gonzalez', progress: 92, lastActive: 'Today', status: 'On track' },
  { name: 'James Carter', progress: 45, lastActive: '3 days ago', status: 'Needs attention' },
  { name: 'Tanya Williams', progress: 78, lastActive: 'Yesterday', status: 'On track' },
];

const WEEKLY_SCHEDULE = [
  { day: 'MON', title: 'CNA Lecture - Module 3', detail: '9:00 AM - 11:00 AM · Room 201', status: 'Upcoming' },
  { day: 'WED', title: 'Skills Lab - Vital Signs', detail: '1:00 PM - 3:00 PM · Skills Lab A', status: 'Confirmed' },
  { day: 'FRI', title: 'Quiz Review + Office Hours', detail: '10:00 AM - 12:00 PM · Online', status: 'Open' },
];

const GRADE_BOOK = [
  { name: 'Maria Gonzalez', exam1: '96%', exam2: '88%', average: '92%' },
  { name: 'James Carter', exam1: '70%', exam2: '62%', average: '66%' },
  { name: 'Tanya Williams', exam1: '84%', exam2: '80%', average: '82%' },
];

const RESOURCE_CARDS = [
  {
    title: 'CNA Instructor Handbook',
    copy: 'Official Texas CNA instructor guidelines and standards.',
    cta: 'Download handbook',
  },
  {
    title: 'Lesson Plan Templates',
    copy: 'Reusable templates for lecture flow, labs, and skill checkoffs.',
    cta: 'Download templates',
  },
  {
    title: 'Learner Outreach Scripts',
    copy: 'Ready-to-send nudges for missing work, low readiness, and exam prep.',
    cta: 'Open scripts',
  },
  {
    title: 'Clinical Skills Prep',
    copy: 'Quick reminders for high-risk misses before lab assessments.',
    cta: 'Review checklist',
  },
];

const COMMUNITY_QUEUE = [
  { title: '3 students requested mentors', detail: 'Most requests focus on infection control and transfer safety.', status: 'Action needed' },
  { title: 'Saturday practice lab is filling', detail: 'Eight learners want a guided clinical skills rehearsal block.', status: 'Open' },
  { title: 'Facility partner asked for job-ready referrals', detail: 'Two entry-level openings are available after next month’s cohort checkoff.', status: 'Partnership' },
];

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

function StudentsScreen({ onNavigate }: { onNavigate: (view: StaffView) => void }) {
  return (
    <div className="screen-stack">
      <section className="hero-card">
        <div className="eyebrow">Instructor portal</div>
        <div className="hero-grid">
          <div>
            <h1>Support every learner from one place.</h1>
            <p className="hero-copy">
              Track cohort progress, jump into grading, and keep the next teaching priorities in one unified workflow.
            </p>
            <div className="hero-actions">
              <button className="btn btn-primary" type="button" onClick={() => onNavigate('grades')}>
                Open grade book
              </button>
              <button className="btn btn-secondary" type="button" onClick={() => onNavigate('resources')}>
                View resources
              </button>
            </div>
          </div>

          <aside className="section-card emphasis-card">
            <span className="metric-label">Teaching focus</span>
            <strong className="metric-value">Module 4 intervention</strong>
            <p className="metric-copy">Two learners need extra infection control coaching before the next quiz block.</p>
            <ProgressBar value={71} tone="navy" />
            <div className="progress-meta">
              <span>Average learner progress</span>
              <span>71%</span>
            </div>
          </aside>
        </div>
      </section>

      <section className="metric-grid">
        {STUDENT_METRICS.map((metric) => (
          <article key={metric.label} className="metric-card">
            <span className="metric-label">{metric.label}</span>
            <strong className="metric-value">{metric.value}</strong>
            <p className="metric-copy">{metric.detail}</p>
          </article>
        ))}
      </section>

      <section className="section-card">
        <SectionHeader eyebrow="Roster" title="Student progress snapshot" copy="See who is thriving and who needs direct follow-up." />
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Progress</th>
                <th>Last active</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {STUDENT_ROSTER.map((student) => (
                <tr key={student.name}>
                  <td>{student.name}</td>
                  <td>
                    <div className="table-progress">
                      <ProgressBar value={student.progress} tone={student.progress >= 75 ? 'success' : 'accent'} />
                      <span>{student.progress}%</span>
                    </div>
                  </td>
                  <td>{student.lastActive}</td>
                  <td>
                    <span className={`status-pill ${student.status === 'On track' ? 'is-success' : 'is-warning'}`}>
                      {student.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function ScheduleScreen() {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Schedule" title="This week at a glance" copy="Keep labs, lectures, and review time aligned with student needs." />
        <div className="timeline-list">
          {WEEKLY_SCHEDULE.map((event) => (
            <article key={`${event.day}-${event.title}`} className="timeline-item">
              <div className="timeline-day">{event.day}</div>
              <div className="timeline-copy">
                <strong>{event.title}</strong>
                <p>{event.detail}</p>
              </div>
              <span className={`status-pill ${event.status === 'Confirmed' ? 'is-success' : 'is-muted'}`}>{event.status}</span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function GradesScreen() {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Grade book" title="Recent exam performance" copy="Prioritize remediation where scores and progress both dip." />
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Exam 1</th>
                <th>Exam 2</th>
                <th>Average</th>
              </tr>
            </thead>
            <tbody>
              {GRADE_BOOK.map((student) => (
                <tr key={student.name}>
                  <td>{student.name}</td>
                  <td>{student.exam1}</td>
                  <td>{student.exam2}</td>
                  <td><strong>{student.average}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function ResourcesScreen() {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Resources" title="Instructor tools and downloads" copy="Keep teaching materials and communication aids within the same portal." />
      </section>

      <section className="card-grid">
        {RESOURCE_CARDS.map((resource) => (
          <article key={resource.title} className="section-card compact-card">
            <span className="metric-label">Ready to use</span>
            <h3 className="module-title">{resource.title}</h3>
            <p className="module-copy">{resource.copy}</p>
            <div className="section-actions">
              <button className="btn btn-secondary" type="button">{resource.cta}</button>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

function CommunityScreen() {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Community hub" title="Mentor, practice, and workforce coordination" copy="Help learners move from weak domains into real support and real opportunities." />
      </section>

      <section className="timeline-list">
        {COMMUNITY_QUEUE.map((item) => (
          <article key={item.title} className="timeline-item">
            <div className="timeline-day">NOW</div>
            <div className="timeline-copy">
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
            </div>
            <span className="status-pill is-warning">{item.status}</span>
          </article>
        ))}
      </section>

      <section className="panel-grid">
        <article className="section-card">
          <SectionHeader eyebrow="Best use" title="What instructors can do here" />
          <ul className="info-list">
            <li>Match struggling learners with mentor volunteers based on weak domains.</li>
            <li>Organize study groups and skills-lab practice sessions faster.</li>
            <li>Route job-ready learners toward trusted facility opportunities.</li>
          </ul>
        </article>
        <article className="section-card">
          <SectionHeader eyebrow="Outcomes" title="Signals worth watching" />
          <ul className="info-list">
            <li>Mentor requests from low-progress learners</li>
            <li>Study groups filling before high-stakes quizzes</li>
            <li>Facilities repeatedly posting entry-level opportunities</li>
          </ul>
        </article>
      </section>
    </div>
  );
}

function renderView(view: StaffView, onNavigate: (view: StaffView) => void) {
  switch (view) {
    case 'students':
      return <StudentsScreen onNavigate={onNavigate} />;
    case 'schedule':
      return <ScheduleScreen />;
    case 'grades':
      return <GradesScreen />;
    case 'community':
      return <CommunityScreen />;
    case 'resources':
      return <ResourcesScreen />;
    default:
      return null;
  }
}

export function StaffAppShell() {
  const [currentView, setCurrentView] = useState<StaffView>('students');

  useEffect(() => {
    const syncFromHash = () => {
      const rawHash = window.location.hash.replace('#', '');
      if (NAV_ITEMS.some((item) => item.key === rawHash)) {
        setCurrentView(rawHash as StaffView);
      }
    };

    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => window.removeEventListener('hashchange', syncFromHash);
  }, []);

  const navigate = (view: StaffView) => {
    setCurrentView(view);
    window.history.replaceState(null, '', `#${view}`);
  };

  const currentTitle = useMemo(() => {
    switch (currentView) {
      case 'students':
        return 'Student overview';
      case 'schedule':
        return 'Teaching schedule';
      case 'grades':
        return 'Grade book';
      case 'community':
        return 'Community hub';
      case 'resources':
        return 'Instructor resources';
      default:
        return 'Instructor portal';
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
          <p className="topbar-subtitle">A unified instructor portal for coaching, grading, scheduling, and teaching support.</p>
        </div>
        <div className="topbar-actions">
          <span className="status-chip">24 active learners</span>
          <button className="profile-chip" type="button" aria-label="Instructor profile">
            Instructor
          </button>
        </div>
      </header>

      <main id="main-content" className="main-content">
        {renderView(currentView, navigate)}
      </main>

      <nav className="bottom-nav bottom-nav-5" aria-label="Primary">
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
