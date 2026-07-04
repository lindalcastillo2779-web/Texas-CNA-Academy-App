import React, { useEffect, useMemo, useState } from 'react';
import { goToPortalSignup, printHtmlReport } from './portalActions';
import { formatRelativeDate, loadAdminPortalSnapshot, type AdminPortalSnapshot } from './portalData';

type AdminView = 'overview' | 'users' | 'courses' | 'community' | 'compliance' | 'reports';

type AdminNavItem = {
  key: AdminView;
  label: string;
  icon: string;
};

const NAV_ITEMS: AdminNavItem[] = [
  { key: 'overview', label: 'Overview', icon: '📊' },
  { key: 'users', label: 'Users', icon: '👤' },
  { key: 'courses', label: 'Courses', icon: '📘' },
  { key: 'community', label: 'Community', icon: '🤝' },
  { key: 'compliance', label: 'Compliance', icon: '✅' },
  { key: 'reports', label: 'Reports', icon: '📄' },
];

const OVERVIEW_METRICS = [
  { label: 'Total students', value: '142', detail: 'Across the active Texas CNA Academy pipeline.' },
  { label: 'Active instructors', value: '8', detail: 'Teaching cohorts this month.' },
  { label: 'Active courses', value: '6', detail: 'Live programs and renewal tracks.' },
  { label: 'Pass rate', value: '89%', detail: 'Cohorts remain above target readiness.' },
  { label: 'Pending reviews', value: '7', detail: 'Items need admin follow-up today.' },
];

const RECENT_ACTIVITY = [
  { title: 'New student enrolled: Sarah Johnson', detail: '5 minutes ago', tone: 'is-success' },
  { title: 'CEU deadline reminder sent to 12 students', detail: '1 hour ago', tone: 'is-warning' },
  { title: 'Module 4: Infection Control published', detail: '3 hours ago', tone: 'is-muted' },
];

const USERS = [
  { name: 'Maria Gonzalez', role: 'Student', email: 'm.gonzalez@email.com', status: 'Active' },
  { name: 'Prof. T. Baker', role: 'Instructor', email: 't.baker@txcna.edu', status: 'Active' },
  { name: 'Abilene Skills Lab', role: 'Facility', email: 'ops@abileneskillslab.com', status: 'Pending' },
];

const COURSES = [
  { title: 'CNA Certification Program', detail: '75 hours · 4 modules', status: 'Active', meta: '24 enrolled' },
  { title: 'CNA Renewal - CEU Track', detail: '12 credits · Online', status: 'Active', meta: '38 enrolled' },
  { title: 'Advanced Patient Care', detail: '20 hours · 2 modules', status: 'Draft', meta: '0 enrolled' },
];

const COMPLIANCE = [
  { label: 'Students compliant', value: '127', tone: 'is-success' },
  { label: 'Renewals pending', value: '9', tone: 'is-warning' },
  { label: 'CEU overdue', value: '6', tone: 'is-danger' },
];

const REPORTS = [
  { title: 'Monthly enrollment report', copy: 'June 2026 enrollment data and trend summary.', cta: 'Generate PDF' },
  { title: 'State compliance report', copy: 'Texas Board of Nursing compliance summary.', cta: 'Generate PDF' },
];

const COMMUNITY_HEALTH = [
  { label: 'Mentor profiles', value: '34', tone: 'is-success' },
  { label: 'Posts awaiting moderation', value: '5', tone: 'is-warning' },
  { label: 'Facility opportunities live', value: '12', tone: 'is-muted' },
];

const COMMUNITY_REVIEW_QUEUE = [
  { title: 'Review new mentor offer', detail: 'Verify experience summary and posting quality before approval.', tone: 'is-warning' },
  { title: 'Approve facility hiring event', detail: 'Confirm details for next week’s workforce event post.', tone: 'is-success' },
  { title: 'Archive outdated practice partner request', detail: 'Post is over 30 days old and no longer active.', tone: 'is-muted' },
];

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

function OverviewScreen({
  onNavigate,
  overviewMetrics,
  recentActivity,
}: {
  onNavigate: (view: AdminView) => void;
  overviewMetrics: typeof OVERVIEW_METRICS;
  recentActivity: typeof RECENT_ACTIVITY;
}) {
  return (
    <div className="screen-stack">
      <section className="hero-card">
        <div className="eyebrow">Admin portal</div>
        <div className="hero-grid">
          <div>
            <h1>Oversee the entire program in one place.</h1>
            <p className="hero-copy">
              Track operations, course readiness, compliance health, and reporting from the same unified portal experience.
            </p>
            <div className="hero-actions">
              <button className="btn btn-primary" type="button" onClick={() => onNavigate('users')}>
                Manage users
              </button>
              <button className="btn btn-secondary" type="button" onClick={() => onNavigate('reports')}>
                Open reports
              </button>
            </div>
          </div>

          <aside className="section-card emphasis-card">
            <span className="metric-label">Today&apos;s priority</span>
            <strong className="metric-value">7 reviews pending</strong>
            <p className="metric-copy">Resolve enrollment approvals and CEU exceptions before the next reporting cycle.</p>
            <div className="focus-banner">
              <strong>Most urgent queue</strong>
              <span>CEU compliance checks for six overdue accounts.</span>
            </div>
          </aside>
        </div>
      </section>

      <section className="module-grid">
        {overviewMetrics.map((metric) => (
          <article key={metric.label} className="metric-card">
            <span className="metric-label">{metric.label}</span>
            <strong className="metric-value">{metric.value}</strong>
            <p className="metric-copy">{metric.detail}</p>
          </article>
        ))}
      </section>

      <section className="section-card">
        <SectionHeader eyebrow="Activity" title="Recent platform activity" copy="Keep a quick pulse on enrollment, reminders, and content releases." />
        <div className="timeline-list">
          {recentActivity.map((item) => (
            <article key={item.title} className="timeline-item">
              <div className={`timeline-dot ${item.tone}`} />
              <div className="timeline-copy">
                <strong>{item.title}</strong>
                <p>{item.detail}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function UsersScreen({ users }: { users: typeof USERS }) {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Users" title="Manage people and organizations" copy="See who is active and where follow-up is needed." />
        <div className="section-actions">
          <button className="btn btn-primary" type="button" onClick={() => goToPortalSignup('student')}>
            Add user
          </button>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Email</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.email}>
                  <td>{user.name}</td>
                  <td>{user.role}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`status-pill ${user.status === 'Active' ? 'is-success' : 'is-warning'}`}>{user.status}</span>
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

function CoursesScreen({ courses }: { courses: typeof COURSES }) {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Courses" title="Program lineup" copy="Keep active offerings and draft work visible without leaving the portal." />
      </section>

      <section className="card-grid">
        {courses.map((course) => (
          <article key={course.title} className="section-card compact-card">
            <div className="badge-row">
              <span className={`badge ${course.status === 'Active' ? 'badge-success' : 'badge-warning'}`}>{course.status}</span>
              <span className="badge badge-muted">{course.meta}</span>
            </div>
            <h3 className="module-title">{course.title}</h3>
            <p className="module-copy">{course.detail}</p>
          </article>
        ))}
      </section>
    </div>
  );
}

function ComplianceScreen({ compliance }: { compliance: typeof COMPLIANCE }) {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Compliance" title="State readiness snapshot" copy="Watch the counts that matter most for renewals and CEU follow-up." />
      </section>

      <section className="metric-grid">
        {compliance.map((item) => (
          <article key={item.label} className={`metric-card metric-card-${item.tone}`}>
            <span className="metric-label">{item.label}</span>
            <strong className="metric-value">{item.value}</strong>
          </article>
        ))}
      </section>
    </div>
  );
}

function CommunityScreen({
  communityHealth,
  communityReviewQueue,
}: {
  communityHealth: typeof COMMUNITY_HEALTH;
  communityReviewQueue: typeof COMMUNITY_REVIEW_QUEUE;
}) {
  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Community hub" title="Moderate the mentor and workforce network" copy="Keep mentoring, study support, and facility opportunities trusted and useful." />
      </section>

      <section className="metric-grid">
        {communityHealth.map((item) => (
          <article key={item.label} className={`metric-card metric-card-${item.tone}`}>
            <span className="metric-label">{item.label}</span>
            <strong className="metric-value">{item.value}</strong>
          </article>
        ))}
      </section>

      <section className="section-card">
        <SectionHeader eyebrow="Moderation" title="Community review queue" copy="Prioritize safety, freshness, and value before posts stay visible." />
        <div className="timeline-list">
          {communityReviewQueue.map((item) => (
            <article key={item.title} className="timeline-item">
              <div className={`timeline-dot ${item.tone}`} />
              <div className="timeline-copy">
                <strong>{item.title}</strong>
                <p>{item.detail}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function ReportsScreen({
  overviewMetrics,
  recentActivity,
  compliance,
  communityHealth,
}: {
  overviewMetrics: typeof OVERVIEW_METRICS;
  recentActivity: typeof RECENT_ACTIVITY;
  compliance: typeof COMPLIANCE;
  communityHealth: typeof COMMUNITY_HEALTH;
}) {
  const handleReport = (reportTitle: string) => {
    if (reportTitle === 'Monthly enrollment report') {
      printHtmlReport(reportTitle, [
        {
          heading: 'Enrollment snapshot',
          rows: overviewMetrics.map((metric) => `${metric.label}: ${metric.value} — ${metric.detail}`),
        },
        {
          heading: 'Recent activity',
          rows: recentActivity.map((item) => `${item.title} (${item.detail})`),
        },
      ]);
      return;
    }

    printHtmlReport(reportTitle, [
      {
        heading: 'Compliance snapshot',
        rows: compliance.map((item) => `${item.label}: ${item.value}`),
      },
      {
        heading: 'Community health',
        rows: communityHealth.map((item) => `${item.label}: ${item.value}`),
      },
    ]);
  };

  return (
    <div className="screen-stack">
      <section className="section-card">
        <SectionHeader eyebrow="Reports" title="Generate and share summaries" copy="Keep recurring exports close to the rest of the admin workflow." />
      </section>

      <section className="card-grid">
        {REPORTS.map((report) => (
          <article key={report.title} className="section-card compact-card">
            <h3 className="module-title">{report.title}</h3>
            <p className="module-copy">{report.copy}</p>
            <div className="section-actions">
              <button className="btn btn-secondary" type="button" onClick={() => handleReport(report.title)}>
                {report.cta}
              </button>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

function renderView(
  view: AdminView,
  onNavigate: (view: AdminView) => void,
  snapshot: {
    overviewMetrics: typeof OVERVIEW_METRICS;
    recentActivity: typeof RECENT_ACTIVITY;
    users: typeof USERS;
    courses: typeof COURSES;
    compliance: typeof COMPLIANCE;
    communityHealth: typeof COMMUNITY_HEALTH;
    communityReviewQueue: typeof COMMUNITY_REVIEW_QUEUE;
  }
) {
  switch (view) {
    case 'overview':
      return (
        <OverviewScreen
          onNavigate={onNavigate}
          overviewMetrics={snapshot.overviewMetrics}
          recentActivity={snapshot.recentActivity}
        />
      );
    case 'users':
      return <UsersScreen users={snapshot.users} />;
    case 'courses':
      return <CoursesScreen courses={snapshot.courses} />;
    case 'community':
      return (
        <CommunityScreen
          communityHealth={snapshot.communityHealth}
          communityReviewQueue={snapshot.communityReviewQueue}
        />
      );
    case 'compliance':
      return <ComplianceScreen compliance={snapshot.compliance} />;
    case 'reports':
      return (
        <ReportsScreen
          overviewMetrics={snapshot.overviewMetrics}
          recentActivity={snapshot.recentActivity}
          compliance={snapshot.compliance}
          communityHealth={snapshot.communityHealth}
        />
      );
    default:
      return null;
  }
}

export function AdminAppShell() {
  const [currentView, setCurrentView] = useState<AdminView>('overview');
  const [portalSnapshot, setPortalSnapshot] = useState<AdminPortalSnapshot | null>(null);

  const overviewMetrics = portalSnapshot?.overviewMetrics ?? OVERVIEW_METRICS;
  const recentActivity = portalSnapshot?.recentActivity.map((item) => ({
    ...item,
    detail: formatRelativeDate(item.detail),
  })) ?? RECENT_ACTIVITY;
  const users = portalSnapshot?.users ?? USERS;
  const courses = portalSnapshot?.courses ?? COURSES;
  const compliance = portalSnapshot?.compliance ?? COMPLIANCE;
  const communityHealth = portalSnapshot?.communityHealth ?? COMMUNITY_HEALTH;
  const communityReviewQueue = portalSnapshot?.communityReviewQueue.map((item) => ({
    ...item,
    detail: formatRelativeDate(item.detail),
  })) ?? COMMUNITY_REVIEW_QUEUE;

  useEffect(() => {
    const syncFromHash = () => {
      const rawHash = window.location.hash.replace('#', '');
      if (NAV_ITEMS.some((item) => item.key === rawHash)) {
        setCurrentView(rawHash as AdminView);
      }
    };

    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => window.removeEventListener('hashchange', syncFromHash);
  }, []);

  useEffect(() => {
    let isMounted = true;

    loadAdminPortalSnapshot()
      .then((snapshot) => {
        if (isMounted) {
          setPortalSnapshot(snapshot);
        }
      })
      .catch(() => {
        if (isMounted) {
          setPortalSnapshot(null);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const navigate = (view: AdminView) => {
    setCurrentView(view);
    window.history.replaceState(null, '', `#${view}`);
  };

  const currentTitle = useMemo(() => {
    switch (currentView) {
      case 'overview':
        return 'Program overview';
      case 'users':
        return 'User management';
      case 'courses':
        return 'Course oversight';
      case 'community':
        return 'Community moderation';
      case 'compliance':
        return 'Compliance tracker';
      case 'reports':
        return 'Reporting center';
      default:
        return 'Admin portal';
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
          <p className="topbar-subtitle">A unified admin portal for operations, compliance, user management, and reporting.</p>
        </div>
        <div className="topbar-actions">
          <span className="status-chip">{overviewMetrics[4]?.value ?? '0'} reviews pending</span>
          <button
            className="profile-chip"
            type="button"
            aria-label="Admin profile"
            onClick={() => goToPortalSignup('admin')}
          >
            Admin
          </button>
        </div>
      </header>

      <main id="main-content" className="main-content">
        {renderView(currentView, navigate, {
          overviewMetrics,
          recentActivity,
          users,
          courses,
          compliance,
          communityHealth,
          communityReviewQueue,
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
