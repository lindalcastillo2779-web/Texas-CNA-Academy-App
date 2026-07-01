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

// Re-export default resolver
export { default as CoursesResolver } from './courses.resolver';
