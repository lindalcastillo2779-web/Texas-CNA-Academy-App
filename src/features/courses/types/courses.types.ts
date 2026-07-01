// Texas CNA Academy
// courses.types.ts
// Core TypeScript types for the Courses feature

export type PrometricDomainFull =
  | "Role of the Nurse Aide"
  | "Promotion of Safety"
  | "Promotion of Function and Health of Residents"
  | "Basic Nursing Care Provided by the Nurse Aide"
  | "Specialized Care Provided by the Nurse Aide";

export type PrometricDomainShort =
  | "Role"
  | "Safety"
  | "Function & Health"
  | "Basic Care"
  | "Specialized Care";

export type LessonType = "standard" | "interaction" | "review";
export type LessonStatus = "not_started" | "in_progress" | "completed";
export type ModuleStatus = "not_started" | "in_progress" | "completed";

export type ReviewAccessMode =
  | "open"
  | "soft_recommended"
  | "recommended_after_majority"
  | "recommended_after_all";

export type ReviewWeightMode = "equal" | "heavier" | "much_heavier";
export type CrossLinkMode = "minimal" | "standard" | "skill_heavy" | "review_heavy";
export type DomainDisplayMode = "full" | "compact" | "auto_by_density";

export type LessonCompletionRule =
  | "reach_end_only"
  | "end_plus_check"
  | "scenario_plus_check"
  | "review_full"
  | "review_light"
  | "review_plus_next_step";

export type QuickCheckType = "mcq" | "true_false" | "scenario_choice" | "mixed";
export type ScenarioMode = "scenario" | "visual" | "both" | "mixed";
export type ReflectionType = "encouragement" | "dignity" | "perseverance" | "service" | "comfort" | "mixed";
export type ModuleToneProfile = "foundational" | "skills_building" | "safety_focused" | "exam_focused" | "dignity_focused" | "balanced";

export interface CourseLesson {
  id: string;
  moduleId: string;
  number: number;
  title: string;
  subtitle: string;
  estimatedMinutes: number;
  type: LessonType;
  quickCheckType: QuickCheckType;
  scenarioMode: ScenarioMode;
  reflectionType: ReflectionType;
  prometricTags: PrometricDomainFull[];
  txMappingPlaceholder?: string;
}

export interface CourseModule {
  id: string;
  number: number;
  title: string;
  subtitle: string;
  learnerFriendlyTitle: string;
  texasAnchorName: string;
  summary: string;
  estimatedMinutes: number;
  lessonCount: number;
  prometricDomains: PrometricDomainFull[];
  relatedSkills: string[];
  lessons: CourseLesson[];
  reviewLessonId: string;
}

export interface LessonCompletionDefaults {
  standard: LessonCompletionRule;
  interaction: LessonCompletionRule;
}

export interface CourseModuleBehaviorConfig {
  moduleId: string;
  reviewAccessMode: ReviewAccessMode;
  reviewWeightMode: ReviewWeightMode;
  reflectionEnabled: boolean;
  reflectionPriority: "low" | "medium" | "high";
  recommendationPriority: "low" | "medium" | "high";
  resumePriority: "low" | "medium" | "high";
  crossLinkMode: CrossLinkMode;
  domainDisplayMode: DomainDisplayMode;
  lessonCompletionDefaults: LessonCompletionDefaults;
  reviewCompletionRule: LessonCompletionRule;
  moduleToneProfile: ModuleToneProfile;
}

export interface LessonBehaviorOverride {
  lessonId: string;
  completionRule?: LessonCompletionRule;
  crossLinkMode?: CrossLinkMode;
  domainDisplayMode?: DomainDisplayMode;
  reflectionType?: ReflectionType;
}

export interface CourseModuleBundle {
  module: CourseModule;
  config: CourseModuleBehaviorConfig;
  lessonOverrides?: LessonBehaviorOverride[];
}
