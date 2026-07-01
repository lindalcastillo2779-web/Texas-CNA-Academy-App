// courses.resolver.ts
// Resolver functions for Courses feature
// Handles learner state, module readiness, and adaptive behavior

import type {
  CourseModule,
  CourseLesson,
  LearnerState,
  ModuleProgress,
  LessonProgress,
} from './types/courses.types';
import { MODULE_CONFIGS, getModuleConfig, isModuleUnlocked } from './module-config';
import { M01_BUNDLE } from './data/m01-role-of-nurse-aide.bundle';
import { M02_BUNDLE } from './data/m02-legal-ethical-behavior.bundle';
import { M03_BUNDLE } from './data/m03-communication-interpersonal.bundle';

// Registry of all available module bundles
const MODULE_BUNDLE_REGISTRY: Record<string, any> = {
  M01: M01_BUNDLE,
  M02: M02_BUNDLE,
  M03: M03_BUNDLE,
  // M04-M14 will be added as content bundles are created
};

/**
 * Get all modules with learner progress and readiness state
 */
export function getModulesWithProgress(
  learnerState: LearnerState
): (CourseModule & { progress: ModuleProgress; isUnlocked: boolean })[] {
  const completedModuleIds = learnerState.completedModuleIds || [];

  return MODULE_CONFIGS.map((config) => {
    const bundle = MODULE_BUNDLE_REGISTRY[config.moduleId];
    const module = bundle ? bundle.module : null;

    const progress = learnerState.moduleProgress?.[config.moduleId] || {
      moduleId: config.moduleId,
      completedLessonIds: [],
      totalLessons: config.lessonCount,
      completedLessons: 0,
      percentComplete: 0,
      lastAccessedAt: null,
      status: 'not-started',
    };

    const isUnlocked = isModuleUnlocked(config.moduleId, completedModuleIds);

    return {
      ...module,
      moduleId: config.moduleId,
      moduleNumber: config.moduleNumber,
      title: config.title,
      description: config.description,
      estimatedMinutes: config.estimatedMinutes,
      lessonIds: module?.lessonIds || [],
      domains: config.domains,
      primaryDomain: config.primaryDomain,
      status: config.status,
      prerequisiteModuleIds: config.prerequisiteModuleIds,
      reflectionEnabled: config.reflectionEnabled,
      progress,
      isUnlocked,
    };
  });
}

/**
 * Get a specific module bundle with all lessons
 */
export function getModuleBundle(moduleId: string): any | null {
  return MODULE_BUNDLE_REGISTRY[moduleId] || null;
}

/**
 * Get a specific lesson from a module
 */
export function getLesson(moduleId: string, lessonId: string): CourseLesson | null {
  const bundle = MODULE_BUNDLE_REGISTRY[moduleId];
  if (!bundle) return null;

  return bundle.lessons.find((lesson: CourseLesson) => lesson.lessonId === lessonId) || null;
}

/**
 * Get lessons for a module with progress
 */
export function getLessonsWithProgress(
  moduleId: string,
  learnerState: LearnerState
): (CourseLesson & { progress: LessonProgress })[] {
  const bundle = MODULE_BUNDLE_REGISTRY[moduleId];
  if (!bundle) return [];

  const moduleProgress = learnerState.moduleProgress?.[moduleId];

  return bundle.lessons.map((lesson: CourseLesson) => {
    const progress: LessonProgress = {
      lessonId: lesson.lessonId,
      moduleId: lesson.moduleId,
      isComplete: moduleProgress?.completedLessonIds.includes(lesson.lessonId) || false,
      timeSpentSeconds: 0,
      lastAccessedAt: null,
    };

    return { ...lesson, progress };
  });
}

/**
 * Calculate if a lesson is complete based on completion rules
 */
export function isLessonComplete(
  lesson: CourseLesson,
  timeSpentSeconds: number,
  scrolledToBottom: boolean,
  explicitComplete: boolean
): boolean {
  const rule = lesson.completionRule;

  if (rule.mode === 'explicit-complete') {
    return explicitComplete;
  }

  if (rule.mode === 'scroll-and-time') {
    return scrolledToBottom && timeSpentSeconds >= rule.minimumSeconds;
  }

  if (rule.mode === 'interaction') {
    return explicitComplete; // Requires explicit interaction (quiz, exercise, etc.)
  }

  return false;
}

/**
 * Mark a lesson as complete and update learner state
 */
export function completeLessonAndUpdateState(
  learnerState: LearnerState,
  moduleId: string,
  lessonId: string
): LearnerState {
  const moduleProgress = learnerState.moduleProgress?.[moduleId] || {
    moduleId,
    completedLessonIds: [],
    totalLessons: 0,
    completedLessons: 0,
    percentComplete: 0,
    lastAccessedAt: null,
    status: 'not-started',
  };

  if (moduleProgress.completedLessonIds.includes(lessonId)) {
    return learnerState; // Already complete
  }

  const updatedCompletedLessonIds = [...moduleProgress.completedLessonIds, lessonId];
  const config = getModuleConfig(moduleId);
  const totalLessons = config?.lessonCount || 0;
  const completedLessons = updatedCompletedLessonIds.length;
  const percentComplete = totalLessons > 0 ? (completedLessons / totalLessons) * 100 : 0;

  const updatedModuleProgress: ModuleProgress = {
    ...moduleProgress,
    completedLessonIds: updatedCompletedLessonIds,
    totalLessons,
    completedLessons,
    percentComplete,
    lastAccessedAt: new Date().toISOString(),
    status: percentComplete === 100 ? 'completed' : 'in-progress',
  };

  const updatedCompletedModuleIds =
    percentComplete === 100 && !learnerState.completedModuleIds.includes(moduleId)
      ? [...learnerState.completedModuleIds, moduleId]
      : learnerState.completedModuleIds;

  return {
    ...learnerState,
    moduleProgress: {
      ...learnerState.moduleProgress,
      [moduleId]: updatedModuleProgress,
    },
    completedModuleIds: updatedCompletedModuleIds,
  };
}

/**
 * Get next recommended lesson based on learner progress
 */
export function getNextLesson(learnerState: LearnerState): {
  moduleId: string;
  lessonId: string;
} | null {
  const modulesWithProgress = getModulesWithProgress(learnerState);

  // Find first incomplete lesson in first incomplete unlocked module
  for (const module of modulesWithProgress) {
    if (!module.isUnlocked) continue;
    if (module.progress.status === 'completed') continue;

    const lessons = getLessonsWithProgress(module.moduleId, learnerState);
    const nextLesson = lessons.find((lesson) => !lesson.progress.isComplete);

    if (nextLesson) {
      return {
        moduleId: module.moduleId,
        lessonId: nextLesson.lessonId,
      };
    }
  }

  return null; // All unlocked modules complete
}

/**
 * Get current learner confidence level for a module
 */
export function getModuleConfidenceLevel(
  moduleId: string,
  learnerState: LearnerState
): 'low' | 'medium' | 'high' | null {
  const moduleProgress = learnerState.moduleProgress?.[moduleId];
  if (!moduleProgress) return null;

  const { percentComplete } = moduleProgress;

  if (percentComplete < 50) return 'low';
  if (percentComplete < 90) return 'medium';
  return 'high';
}

export default {
  getModulesWithProgress,
  getModuleBundle,
  getLesson,
  getLessonsWithProgress,
  isLessonComplete,
  completeLessonAndUpdateState,
  getNextLesson,
  getModuleConfidenceLevel,
};
