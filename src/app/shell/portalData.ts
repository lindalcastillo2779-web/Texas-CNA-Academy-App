export type PortalProfile = {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  role?: string;
  facility?: string;
};

export type StudentPortalRecord = {
  id: number;
  name: string;
  email: string;
  role: string;
  statusChip: string;
  access: {
    allowed: boolean;
    subscribed: boolean;
    trial_active: boolean;
    days_left: number;
    trial_ends_on: string | null;
  };
  ceu: {
    earnedHours: number;
    requiredHours: number;
    remainingHours: number;
    recentRecords: Array<{
      completed_on: string;
      course_name: string;
      provider: string;
      hours: number;
      certificate: string;
    }>;
  };
  quiz: {
    readinessScore: number;
    totalAttempts: number;
    totalQuestions: number;
    weakestDomainKey: string;
    strongestDomainKey: string;
    statsByDomain: Array<{
      domain: string;
      avgPct: number;
      bestPct: number;
      attempts: number;
    }>;
    recentAttempts: Array<{
      domain: string | null;
      pct: number;
      takenAt: string;
    }>;
  };
  community: {
    recommendedActions: string[];
    mentorMatches: Array<{
      name: string;
      role: string;
      interest_areas?: string;
      availability?: string;
      city?: string;
    }>;
    recommendedPosts: Array<{
      title: string;
      description: string;
      location?: string;
      post_type: string;
    }>;
  };
};

export type StaffPortalSnapshot = {
  generatedAt: string;
  studentMetrics: Array<{ label: string; value: string; detail: string }>;
  studentRoster: Array<{
    name: string;
    email: string;
    progress: number;
    lastActiveAt: string | null;
    status: string;
  }>;
  facilitySchedule: Array<{
    day: string;
    title: string;
    detail: string;
    status: string;
  }>;
  gradeBook: Array<{
    name: string;
    exam1: string;
    exam2: string;
    average: string;
  }>;
  communityQueue: Array<{
    title: string;
    detail: string;
    status: string;
  }>;
};

export type AdminPortalSnapshot = {
  generatedAt: string;
  overviewMetrics: Array<{ label: string; value: string; detail: string }>;
  recentActivity: Array<{ title: string; detail: string; tone: string }>;
  users: Array<{ name: string; role: string; email: string; status: string }>;
  courses: Array<{ title: string; detail: string; status: string; meta: string }>;
  compliance: Array<{ label: string; value: string; tone: string }>;
  communityHealth: Array<{ label: string; value: string; tone: string }>;
  communityReviewQueue: Array<{ title: string; detail: string; tone: string }>;
};

type StudentDashboardSnapshot = {
  generatedAt: string;
  students: StudentPortalRecord[];
};

function safeJsonParse<T>(value: string | null): T | null {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

async function fetchSnapshot<T>(path: string): Promise<T | null> {
  const response = await fetch(path, { headers: { Accept: 'application/json' } });
  if (!response.ok) {
    return null;
  }

  return (await response.json()) as T;
}

export function readPortalProfile(): PortalProfile | null {
  return safeJsonParse<PortalProfile>(window.localStorage.getItem('texas-cna-academy.portal-profile'));
}

export function getPortalDisplayName(profile: PortalProfile | null): string {
  const fullName = [profile?.firstName, profile?.lastName].filter(Boolean).join(' ').trim();
  return fullName || 'Portal user';
}

export function formatRelativeDate(value: string | null | undefined): string {
  if (!value) {
    return 'No recent activity';
  }

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return value;
  }

  const now = new Date();
  const diffMs = now.getTime() - timestamp.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays <= 0) {
    return 'Today';
  }
  if (diffDays === 1) {
    return 'Yesterday';
  }
  if (diffDays < 7) {
    return `${diffDays} days ago`;
  }

  return timestamp.toLocaleDateString();
}

export async function loadStudentPortalRecord(): Promise<{
  generatedAt: string | null;
  profile: PortalProfile | null;
  student: StudentPortalRecord | null;
}> {
  const profile = readPortalProfile();
  const snapshot = await fetchSnapshot<StudentDashboardSnapshot>('/portal-data/student-dashboard.json');
  const requestedEmail = profile?.email?.trim().toLowerCase();
  const student =
    snapshot?.students.find((candidate) => candidate.email.trim().toLowerCase() === requestedEmail) ??
    snapshot?.students[0] ??
    null;

  return {
    generatedAt: snapshot?.generatedAt ?? null,
    profile,
    student,
  };
}

export async function loadStaffPortalSnapshot(): Promise<StaffPortalSnapshot | null> {
  return fetchSnapshot<StaffPortalSnapshot>('/portal-data/staff-dashboard.json');
}

export async function loadAdminPortalSnapshot(): Promise<AdminPortalSnapshot | null> {
  return fetchSnapshot<AdminPortalSnapshot>('/portal-data/admin-dashboard.json');
}
