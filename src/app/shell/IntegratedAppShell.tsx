import React, { useMemo, useState } from 'react';

type AppView = 'home' | 'courses' | 'clinical-skills' | 'flashcards' | 'more';

type NavItem = {
  key: AppView;
  label: string;
  icon: string;
};

const NAV_ITEMS: NavItem[] = [
  { key: 'home', label: 'Home', icon: '⌂' },
  { key: 'courses', label: 'Courses', icon: '▣' },
  { key: 'clinical-skills', label: 'Clinical Skills', icon: '✚' },
  { key: 'flashcards', label: 'Flashcards', icon: '◫' },
  { key: 'more', label: 'More', icon: '⋯' },
];

function HomeScreen() {
  return (
    <div className="screen-stack">
      <section className="hero-card">
        <div className="eyebrow">Texas CNA Academy</div>
        <h1>Study next with confidence.</h1>
        <p className="hero-copy">
          Track coursework, clinical preparation, flashcard review, and renewal support in one place.
        </p>
        <div className="button-row">
          <button className="btn btn-primary">Continue learning</button>
          <button className="btn btn-secondary">View progress</button>
        </div>
      </section>

      <section className="kpi-grid">
        <article className="panel-card">
          <span className="kpi-label">Study next</span>
          <strong className="kpi-value">Module 1 Review</strong>
          <p className="kpi-copy">Resume your current learning path and keep momentum.</p>
        </article>

        <article className="panel-card">
          <span className="kpi-label">Renewal due</span>
          <strong className="kpi-value">Not due yet</strong>
          <p className="kpi-copy">Verify final renewal timing with Texas HHSC, TULIP, and Prometric.</p>
        </article>

        <article className="panel-card">
          <span className="kpi-label">Weak area</span>
          <strong className="kpi-value">Infection control</strong>
          <p className="kpi-copy">Focus review and safety steps are ready when you need them.</p>
        </article>
      </section>
    </div>
  );
}

function CoursesScreen() {
  return (
    <div className="screen-stack">
      <section className="section-header">
        <div>
          <div className="eyebrow">Courses</div>
          <h2>Texas curriculum modules</h2>
        </div>
        <button className="btn btn-secondary">Browse all</button>
      </section>

      <article className="course-card">
        <div className="course-meta-row">
          <span className="tag">Module 1</span>
          <span className="tag">Core training</span>
        </div>
        <h3>Role of the Nurse Aide</h3>
        <p>
          Learn the responsibilities, work standards, communication basics, and expectations that shape safe CNA practice in Texas settings.
        </p>
        <div className="progress-row">
          <span>Progress: 42%</span>
          <span>6 lessons</span>
          <span>25 min left</span>
        </div>
        <div className="button-row">
          <button className="btn btn-primary">Continue module</button>
          <button className="btn btn-secondary">View details</button>
        </div>
      </article>
    </div>
  );
}

function ClinicalSkillsScreen() {
  return (
    <div className="screen-stack">
      <section className="section-header">
        <div>
          <div className="eyebrow">Clinical Skills</div>
          <h2>Step-by-step skills training</h2>
        </div>
      </section>

      <article className="panel-card">
        <h3>Handwashing</h3>
        <p>Review each step in sequence, why it matters, and the most common exam-day misses.</p>
        <div className="button-row">
          <button className="btn btn-primary">Start skill</button>
          <button className="btn btn-secondary">Why it matters</button>
        </div>
      </article>
    </div>
  );
}

function FlashcardsScreen() {
  return (
    <div className="screen-stack">
      <section className="section-header">
        <div>
          <div className="eyebrow">Flashcards</div>
          <h2>Quick review and exam recall</h2>
        </div>
      </section>

      <article className="panel-card">
        <h3>Safety and infection control</h3>
        <p>Review key terms, steps, and test-style prompts with short rationale support.</p>
        <div className="button-row">
          <button className="btn btn-primary">Open deck</button>
          <button className="btn btn-secondary">Shuffle review</button>
        </div>
      </article>
    </div>
  );
}

function MoreScreen() {
  return (
    <div className="screen-stack">
      <section className="section-header">
        <div>
          <div className="eyebrow">More</div>
          <h2>More tools and support</h2>
        </div>
      </section>

      <div className="more-grid">
        {[
          'Skills Lab',
          'Study Buddy',
          'Verified Resources',
          'Accessibility',
          'About',
          'Settings',
        ].map((item) => (
          <article key={item} className="panel-card compact-card">
            <h3>{item}</h3>
            <p>Open this area.</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function renderView(view: AppView) {
  switch (view) {
    case 'home':
      return <HomeScreen />;
    case 'courses':
      return <CoursesScreen />;
    case 'clinical-skills':
      return <ClinicalSkillsScreen />;
    case 'flashcards':
      return <FlashcardsScreen />;
    case 'more':
      return <MoreScreen />;
    default:
      return <HomeScreen />;
  }
}

export function IntegratedAppShell() {
  const [currentView, setCurrentView] = useState<AppView>('home');

  const currentTitle = useMemo(() => {
    switch (currentView) {
      case 'home':
        return 'Student Home';
      case 'courses':
        return 'Courses';
      case 'clinical-skills':
        return 'Clinical Skills';
      case 'flashcards':
        return 'Flashcards';
      case 'more':
        return 'More';
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
        <div>
          <div className="brand-kicker">Texas CNA Academy</div>
          <div className="topbar-title">{currentTitle}</div>
        </div>
        <button className="profile-chip" type="button">
          Student
        </button>
      </header>

      <main id="main-content" className="main-content">
        {renderView(currentView)}
      </main>

      <nav className="bottom-nav" aria-label="Primary">
        {NAV_ITEMS.map((item) => {
          const isActive = item.key === currentView;

          return (
            <button
              key={item.key}
              type="button"
              className={`bottom-nav-item ${isActive ? 'is-active' : ''}`}
              onClick={() => setCurrentView(item.key)}
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
