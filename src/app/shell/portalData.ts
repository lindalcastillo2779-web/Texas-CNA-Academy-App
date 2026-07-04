export type PortalProfile = {
  name?: string;
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  role?: string;
  facility?: string;
};

export type PortalSessionUser = PortalProfile & {
  id: number;
  dashboardPath: string;
};

export type CourseModuleProgress = {
  moduleId: string;
  completedLessonIds: string[];
  totalLessons: number;
  completedLessons: number;
  percentComplete: number;
  lastAccessedAt: string | null;
  status: 'completed' | 'in-progress' | 'not-started';
};

export type CourseProgressSnapshot = {
  completedModuleIds: string[];
  moduleProgress: Record<string, CourseModuleProgress>;
};

export type StudyPlanTask = {
  title: string;
  detail: string;
  status: string;
  view: 'courses' | 'review' | 'skills' | 'more';
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
  courseProgress: CourseProgressSnapshot;
  studyPlan: StudyPlanTask[];
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

export type StudentPortalPayload = {
  generatedAt: string;
  profile: PortalProfile;
  student: StudentPortalRecord;
};

export class PortalApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers ?? {});
  headers.set('Accept', 'application/json');
  if (init?.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(path, {
    credentials: 'include',
    ...init,
    headers,
  });

  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      throw new PortalApiError(`Invalid API response from ${path}.`, response.status);
    }
  }

  if (!response.ok) {
    const errorMessage =
      typeof data === 'object' && data !== null && 'error' in data && typeof data.error === 'string'
        ? data.error
        : response.statusText;
    throw new PortalApiError(errorMessage, response.status);
  }

  return data as T;
}

export function getPortalDisplayName(profile: PortalProfile | null | undefined): string {
  const fullName = profile?.name?.trim() || [profile?.firstName, profile?.lastName].filter(Boolean).join(' ').trim();
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

export async function loadPortalSession(): Promise<{ authenticated: true; user: PortalSessionUser }> {
  return fetchApi<{ authenticated: true; user: PortalSessionUser }>('/api/auth/session');
}

export async function signOutPortalSession(): Promise<void> {
  await fetchApi<{ ok: boolean }>('/api/auth/logout', { method: 'POST' });
}

export async function loadStudentPortalRecord(): Promise<StudentPortalPayload> {
  return fetchApi<StudentPortalPayload>('/api/portal/student');
}

export async function syncCourseProgress(moduleId: string, completedLessons: number): Promise<CourseProgressSnapshot> {
  const payload = await fetchApi<{ ok: boolean; courseProgress: CourseProgressSnapshot }>('/api/portal/course-progress', {
    method: 'POST',
    body: JSON.stringify({ moduleId, completedLessons }),
  });
  return payload.courseProgress;
}

export async function loadStaffPortalSnapshot(): Promise<StaffPortalSnapshot> {
  return fetchApi<StaffPortalSnapshot>('/api/portal/staff');
}

export async function loadAdminPortalSnapshot(): Promise<AdminPortalSnapshot> {
  return fetchApi<AdminPortalSnapshot>('/api/portal/admin');
}
