// module-config.ts
// Course module configuration for all 14 Texas CNA Academy modules
// Aligned with Prometric/NNAAP CNA exam curriculum

import type { CourseModule } from './types/courses.types';
import type { PrometricDomainKey } from './types/domain-labels';

export type ModuleStatus = 'available' | 'coming-soon' | 'locked';

export interface ModuleConfig {
  moduleId: string;
  moduleNumber: number;
  title: string;
  subtitle: string;
  description: string;
  estimatedMinutes: number;
  lessonCount: number;
  domains: PrometricDomainKey[];
  primaryDomain: PrometricDomainKey;
  status: ModuleStatus;
  badgeText?: string; // e.g., 'Coming Soon', 'New', 'Core'
  prerequisiteModuleIds: string[];
  prometricWeight: 'high' | 'medium' | 'low'; // Exam emphasis level
  clinicalSkillsCount: number; // Number of Prometric clinical skills in this module
  reflectionEnabled: boolean;
}

export const MODULE_CONFIGS: ModuleConfig[] = [
  {
    moduleId: 'M01',
    moduleNumber: 1,
    title: 'Role of the Nurse Aide',
    subtitle: 'Your calling as a CNA',
    description: 'Understand the scope of practice, healthcare team roles, and the professional responsibilities of a Certified Nurse Aide in Texas.',
    estimatedMinutes: 45,
    lessonCount: 6,
    domains: ['ROLE', 'LEGAL', 'COMM'],
    primaryDomain: 'ROLE',
    status: 'available',
    badgeText: 'Core',
    prerequisiteModuleIds: [],
    prometricWeight: 'high',
    clinicalSkillsCount: 0,
    reflectionEnabled: true,
  },
  {
    moduleId: 'M02',
    moduleNumber: 2,
    title: 'Legal & Ethical Behavior',
    subtitle: 'Doing right by your residents',
    description: 'Learn HIPAA, abuse reporting obligations, advance directives, professional boundaries, and ethical decision-making as a CNA.',
    estimatedMinutes: 50,
    lessonCount: 7,
    domains: ['LEGAL', 'ELDERCARE', 'COMM'],
    primaryDomain: 'LEGAL',
    status: 'available',
    badgeText: 'Core',
    prerequisiteModuleIds: ['M01'],
    prometricWeight: 'high',
    clinicalSkillsCount: 0,
    reflectionEnabled: true,
  },
  {
    moduleId: 'M03',
    moduleNumber: 3,
    title: 'Communication & Interpersonal Skills',
    subtitle: 'The language of compassionate care',
    description: 'Master verbal and nonverbal communication, active listening, documentation principles, and effective interaction with residents, families, and the care team.',
    estimatedMinutes: 55,
    lessonCount: 8,
    domains: ['COMM', 'PSYCHOSOCIAL', 'ROLE'],
    primaryDomain: 'COMM',
    status: 'available',
    badgeText: 'Core',
    prerequisiteModuleIds: ['M01'],
    prometricWeight: 'high',
    clinicalSkillsCount: 0,
    reflectionEnabled: true,
  },
  {
    moduleId: 'M04',
    moduleNumber: 4,
    title: 'Infection Control',
    subtitle: 'Your first line of defense',
    description: 'Master hand hygiene, standard precautions, PPE use, transmission-based precautions, and healthcare-associated infection prevention.',
    estimatedMinutes: 60,
    lessonCount: 8,
    domains: ['INFECT', 'SAFETY'],
    primaryDomain: 'INFECT',
    status: 'available',
    badgeText: 'Core',
    prerequisiteModuleIds: ['M01'],
    prometricWeight: 'high',
    clinicalSkillsCount: 3,
    reflectionEnabled: false,
  },
  {
    moduleId: 'M05',
    moduleNumber: 5,
    title: 'Safety & Emergency Procedures',
    subtitle: 'Keeping residents safe every shift',
    description: 'Study fall prevention strategies, safe restraint use, fire safety (RACE/PASS), disaster plans, choking response, and emergency protocols.',
    estimatedMinutes: 65,
    lessonCount: 9,
    domains: ['SAFETY', 'INFECT'],
    primaryDomain: 'SAFETY',
    status: 'available',
    badgeText: 'Core',
    prerequisiteModuleIds: ['M01', 'M04'],
    prometricWeight: 'high',
    clinicalSkillsCount: 2,
    reflectionEnabled: false,
  },
  {
    moduleId: 'M06',
    moduleNumber: 6,
    title: 'Resident Rights',
    subtitle: 'Every resident deserves dignity',
    description: 'Explore OBRA regulations, resident rights to privacy and dignity, grievance procedures, advance directives, and promoting independence.',
    estimatedMinutes: 50,
    lessonCount: 7,
    domains: ['ELDERCARE', 'LEGAL', 'PSYCHOSOCIAL'],
    primaryDomain: 'ELDERCARE',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M01', 'M02'],
    prometricWeight: 'high',
    clinicalSkillsCount: 0,
    reflectionEnabled: true,
  },
  {
    moduleId: 'M07',
    moduleNumber: 7,
    title: 'Personal Care Skills',
    subtitle: 'The heart of daily caregiving',
    description: 'Practice bathing techniques, oral hygiene, grooming, dressing assistance, skin integrity checks, and perineal care with dignity-centered approaches.',
    estimatedMinutes: 75,
    lessonCount: 10,
    domains: ['PERSONAL', 'SAFETY', 'INFECT'],
    primaryDomain: 'PERSONAL',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M04', 'M05'],
    prometricWeight: 'high',
    clinicalSkillsCount: 5,
    reflectionEnabled: false,
  },
  {
    moduleId: 'M08',
    moduleNumber: 8,
    title: 'Basic Nursing Skills',
    subtitle: 'Vital signs and clinical fundamentals',
    description: 'Learn to accurately measure temperature, pulse, respirations, blood pressure, and oxygen saturation. Includes positioning, transfer techniques, and basic wound care.',
    estimatedMinutes: 80,
    lessonCount: 11,
    domains: ['VITALS', 'SAFETY', 'SKILLS'],
    primaryDomain: 'VITALS',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M04', 'M05'],
    prometricWeight: 'high',
    clinicalSkillsCount: 6,
    reflectionEnabled: false,
  },
  {
    moduleId: 'M09',
    moduleNumber: 9,
    title: 'Nutrition & Hydration',
    subtitle: 'Fueling recovery and wellness',
    description: 'Understand therapeutic diets, feeding assistance techniques, aspiration prevention, fluid intake monitoring, and nutritional documentation.',
    estimatedMinutes: 55,
    lessonCount: 7,
    domains: ['NUTRITION', 'SAFETY', 'PERSONAL'],
    primaryDomain: 'NUTRITION',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M07'],
    prometricWeight: 'medium',
    clinicalSkillsCount: 2,
    reflectionEnabled: false,
  },
  {
    moduleId: 'M10',
    moduleNumber: 10,
    title: 'Elimination',
    subtitle: 'Promoting continence and comfort',
    description: 'Study bowel and bladder care, catheter care principles, specimen collection procedures, and dignity-preserving elimination assistance.',
    estimatedMinutes: 55,
    lessonCount: 7,
    domains: ['ELIMINATION', 'SAFETY', 'PERSONAL'],
    primaryDomain: 'ELIMINATION',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M07', 'M08'],
    prometricWeight: 'medium',
    clinicalSkillsCount: 3,
    reflectionEnabled: false,
  },
  {
    moduleId: 'M11',
    moduleNumber: 11,
    title: 'Restorative Skills',
    subtitle: 'Helping residents reach their fullest potential',
    description: 'Learn range of motion exercises, ambulation assistance, proper use of assistive devices, and restorative care philosophies that maximize resident independence.',
    estimatedMinutes: 60,
    lessonCount: 8,
    domains: ['RESTORATIVE', 'SAFETY', 'PERSONAL'],
    primaryDomain: 'RESTORATIVE',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M07', 'M08'],
    prometricWeight: 'medium',
    clinicalSkillsCount: 4,
    reflectionEnabled: false,
  },
  {
    moduleId: 'M12',
    moduleNumber: 12,
    title: 'Psychosocial Care',
    subtitle: 'Mind, heart, and spirit',
    description: 'Explore mental health awareness, dementia and Alzheimer care approaches, behavioral intervention strategies, and supporting emotional well-being.',
    estimatedMinutes: 65,
    lessonCount: 9,
    domains: ['PSYCHOSOCIAL', 'COMM', 'SPIRITUAL'],
    primaryDomain: 'PSYCHOSOCIAL',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M03', 'M06'],
    prometricWeight: 'medium',
    clinicalSkillsCount: 0,
    reflectionEnabled: true,
  },
  {
    moduleId: 'M13',
    moduleNumber: 13,
    title: 'Spiritual & Cultural Care',
    subtitle: 'Honoring the whole person',
    description: 'Learn to provide culturally humble, spiritually sensitive care including end-of-life support, religious accommodations, and cross-cultural communication.',
    estimatedMinutes: 45,
    lessonCount: 6,
    domains: ['SPIRITUAL', 'PSYCHOSOCIAL', 'COMM'],
    primaryDomain: 'SPIRITUAL',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M03', 'M12'],
    prometricWeight: 'low',
    clinicalSkillsCount: 0,
    reflectionEnabled: true,
  },
  {
    moduleId: 'M14',
    moduleNumber: 14,
    title: 'Prometric Exam Preparation',
    subtitle: 'You are ready. Let us prove it.',
    description: 'Comprehensive review of all 14 modules with practice written exam questions, clinical skills checklist, test-taking strategies, and confidence-building exercises.',
    estimatedMinutes: 120,
    lessonCount: 14,
    domains: ['ROLE', 'SAFETY', 'INFECT', 'COMM', 'VITALS', 'SKILLS'],
    primaryDomain: 'SKILLS',
    status: 'coming-soon',
    badgeText: 'Coming Soon',
    prerequisiteModuleIds: ['M01','M02','M03','M04','M05','M06','M07','M08','M09','M10','M11','M12','M13'],
    prometricWeight: 'high',
    clinicalSkillsCount: 10,
    reflectionEnabled: true,
  },
];

export function getModuleConfig(moduleId: string): ModuleConfig | undefined {
  return MODULE_CONFIGS.find((m) => m.moduleId === moduleId);
}

export function getAvailableModules(): ModuleConfig[] {
  return MODULE_CONFIGS.filter((m) => m.status === 'available');
}

export function getComingSoonModules(): ModuleConfig[] {
  return MODULE_CONFIGS.filter((m) => m.status === 'coming-soon');
}

export function isModuleUnlocked(
  moduleId: string,
  completedModuleIds: string[]
): boolean {
  const config = getModuleConfig(moduleId);
  if (!config) return false;
  return config.prerequisiteModuleIds.every((prereq) =>
    completedModuleIds.includes(prereq)
  );
}
