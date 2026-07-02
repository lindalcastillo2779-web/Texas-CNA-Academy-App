// index.ts
// Main export file for Courses feature
// Texas CNA Academy - Prometric Aligned

// Types
export * from './types/courses.types';
export * from './types/domain-labels';

// Configuration
export * from './module-config';

// Resolver functions
export * from './courses.resolver';

// Data bundles
export { M01_BUNDLE } from './data/m01-role-of-nurse-aide.bundle';
export { M02_BUNDLE } from './data/m02-legal-ethical-behavior.bundle';
export { M03_BUNDLE } from './data/m03-communication-interpersonal.bundle';
export { M04_BUNDLE } from './data/m04-infection-control.bundle';
export { M05_BUNDLE } from './data/m05-safety-emergency.bundle';
export { M06_BUNDLE } from './data/m06-resident-rights.bundle';
export { M07_BUNDLE } from './data/m07-personal-care.bundle';
export { M08_BUNDLE } from './data/m08-basic-nursing-skills.bundle';
export { M09_BUNDLE } from './data/m09-nutrition-hydration.bundle';
export { M10_BUNDLE } from './data/m10-elimination.bundle';
export { M11_BUNDLE } from './data/m11-restorative-skills.bundle';
export { M12_BUNDLE } from './data/m12-psychosocial-care.bundle';
export { M13_BUNDLE } from './data/m13-spiritual-cultural-care.bundle';
export { M14_BUNDLE } from './data/m14-prometric-exam-prep.bundle';

// Re-export default resolver
export { default as CoursesResolver } from './courses.resolver';
