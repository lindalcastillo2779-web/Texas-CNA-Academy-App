// m01-role-of-nurse-aide.bundle.ts
// Module 1 Content Bundle: Role of the Nurse Aide
// Texas CNA Academy - Prometric Aligned

import type { CourseModuleBundle } from '../types/courses.types';

export const M01_BUNDLE: CourseModuleBundle = {
  module: {
    moduleId: 'M01',
    title: 'Role of the Nurse Aide',
    description: 'Understand the scope of practice, healthcare team roles, and the professional responsibilities of a Certified Nurse Aide in Texas.',
    moduleNumber: 1,
    estimatedMinutes: 45,
    lessonIds: ['M01-L01', 'M01-L02', 'M01-L03', 'M01-L04', 'M01-L05', 'M01-L06'],
    domains: ['ROLE', 'LEGAL', 'COMM'],
    primaryDomain: 'ROLE',
    status: 'available',
    prerequisiteModuleIds: [],
    reflectionEnabled: true,
    reviewAccessMode: 'always',
    reviewWeightMode: 'equal',
    crossLinkMode: 'suggest',
    domainDisplayMode: 'badge',
    lessonCompletionDefaults: {
      standard: { mode: 'scroll-and-time', minimumSeconds: 30 },
      interaction: { mode: 'explicit-complete', minimumSeconds: 0 },
    },
    reviewCompletionRule: { mode: 'scroll-and-time', minimumSeconds: 20 },
    moduleToneProfile: {
      warmth: 'high',
      faithAware: true,
      motivationalStyle: 'encouraging',
      microcopyTone: 'warm-professional',
    },
  },
  lessons: [
    {
      lessonId: 'M01-L01',
      moduleId: 'M01',
      lessonNumber: 1,
      title: 'What is a CNA?',
      subtitle: 'Your role, your purpose, your calling',
      type: 'standard',
      estimatedMinutes: 8,
      content: {
        body: [
          {
            type: 'heading',
            text: 'Defining the Certified Nurse Aide',
          },
          {
            type: 'paragraph',
            text: 'A Certified Nurse Aide (CNA) is a licensed healthcare professional who provides direct patient care under the supervision of a Registered Nurse (RN) or Licensed Vocational/Practical Nurse (LVN/LPN). In Texas, CNAs must pass the Nurse Aide Competency Evaluation Program (NACEP) administered through Prometric.',
          },
          {
            type: 'callout',
            variant: 'encouragement',
            text: 'You are more than a job title. CNAs are often the primary human connection a resident experiences each day. Your presence matters deeply.',
          },
          {
            type: 'heading',
            text: 'The CNA Scope of Practice in Texas',
          },
          {
            type: 'list',
            items: [
              'Assist with activities of daily living (ADLs): bathing, dressing, grooming, eating, and mobility',
              'Measure and record vital signs (temperature, pulse, respiration, blood pressure)',
              'Assist with ambulation and positioning',
              'Report observations to the supervising nurse',
              'Maintain a safe, clean environment for residents',
              'Document care provided accurately and on time',
            ],
          },
          {
            type: 'callout',
            variant: 'warning',
            text: 'CNAs do NOT administer medications, perform wound care, or carry out tasks reserved for licensed nurses unless specifically trained and authorized.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['ROLE'],
    },
    {
      lessonId: 'M01-L02',
      moduleId: 'M01',
      lessonNumber: 2,
      title: 'The Healthcare Team',
      subtitle: 'You are not alone - you are part of something bigger',
      type: 'standard',
      estimatedMinutes: 7,
      content: {
        body: [
          {
            type: 'heading',
            text: 'Members of the Interdisciplinary Care Team',
          },
          {
            type: 'paragraph',
            text: 'Healthcare is a team effort. Understanding who does what helps you communicate effectively and keep residents safe.',
          },
          {
            type: 'table',
            headers: ['Team Member', 'Primary Role', 'CNA Interaction'],
            rows: [
              ['Registered Nurse (RN)', 'Assess, plan, and supervise care', 'Report observations; receive assignments'],
              ['LVN/LPN', 'Implement nursing care plans', 'Report changes; follow care plans'],
              ['Physician/NP/PA', 'Diagnose and prescribe', 'Indirect; report urgent changes to nurse'],
              ['Physical Therapist (PT)', 'Restore mobility and function', 'Assist with PT exercises as instructed'],
              ['Occupational Therapist (OT)', 'Restore daily living skills', 'Support OT goals in ADL assistance'],
              ['Social Worker', 'Psychosocial and discharge planning', 'Alert to resident emotional concerns'],
              ['Dietitian', 'Nutritional assessment and planning', 'Follow diet orders; monitor intake'],
              ['Chaplain/Spiritual Care', 'Spiritual and emotional support', 'Notify if resident requests spiritual care'],
            ],
          },
          {
            type: 'callout',
            variant: 'tip',
            text: 'When in doubt, report. CNAs are the eyes and ears of the care team. Your observations are clinical data.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['ROLE', 'COMM'],
    },
    {
      lessonId: 'M01-L03',
      moduleId: 'M01',
      lessonNumber: 3,
      title: 'CNA Certification in Texas',
      subtitle: 'Understanding NACEP and the Prometric exam',
      type: 'standard',
      estimatedMinutes: 7,
      content: {
        body: [
          {
            type: 'heading',
            text: 'The Texas CNA Certification Pathway',
          },
          {
            type: 'paragraph',
            text: 'To become a certified CNA in Texas, you must complete an approved nurse aide training program and pass the Nurse Aide Competency Evaluation Program (NACEP) through Prometric.',
          },
          {
            type: 'steps',
            items: [
              { step: 1, title: 'Complete an approved training program', description: 'Minimum 100 hours: 60 classroom + 40 clinical hours (Texas requirement)' },
              { step: 2, title: 'Apply for the Prometric exam', description: 'Submit application through your training program or directly via Prometric Texas' },
              { step: 3, title: 'Pass the written knowledge test', description: '60 questions, 90-minute time limit, minimum passing score required' },
              { step: 4, title: 'Pass the clinical skills test', description: 'Demonstrate 5 randomly selected skills before a Prometric evaluator' },
              { step: 5, title: 'Receive your CNA certification', description: 'Your name is added to the Texas Nurse Aide Registry (NAR)' },
            ],
          },
          {
            type: 'callout',
            variant: 'encouragement',
            text: 'You have prepared for this. Every lesson in this course brings you one step closer to your certification and your calling.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['ROLE', 'LEGAL'],
    },
    {
      lessonId: 'M01-L04',
      moduleId: 'M01',
      lessonNumber: 4,
      title: 'Professional Behavior & Work Ethics',
      subtitle: 'The foundation of trustworthy care',
      type: 'standard',
      estimatedMinutes: 7,
      content: {
        body: [
          {
            type: 'heading',
            text: 'What Professional Behavior Looks Like',
          },
          {
            type: 'list',
            items: [
              'Arrive on time and prepared for every shift',
              'Dress according to facility dress code and maintain good hygiene',
              'Treat every resident with dignity, respect, and compassion',
              'Follow the chain of command when reporting concerns',
              'Maintain confidentiality at all times (HIPAA)',
              'Accept constructive feedback and apply it immediately',
              'Never use personal devices or social media to discuss residents',
              'Stay within your scope of practice - always',
            ],
          },
          {
            type: 'callout',
            variant: 'faith',
            text: 'Service with excellence is a form of honor. How you treat the most vulnerable among us reflects the values you carry into every room.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['ROLE', 'LEGAL'],
    },
    {
      lessonId: 'M01-L05',
      moduleId: 'M01',
      lessonNumber: 5,
      title: 'Delegation & Supervision',
      subtitle: 'Working smart within the chain of command',
      type: 'standard',
      estimatedMinutes: 8,
      content: {
        body: [
          {
            type: 'heading',
            text: 'Understanding Delegation',
          },
          {
            type: 'paragraph',
            text: 'Delegation is the process by which a licensed nurse assigns a task to a CNA. The nurse retains accountability while the CNA is responsible for performing the task correctly.',
          },
          {
            type: 'heading',
            text: 'The Five Rights of Delegation',
          },
          {
            type: 'list',
            items: [
              'Right Task - Is this task appropriate to delegate to a CNA?',
              'Right Circumstance - Is the resident stable enough for this delegation?',
              'Right Person - Does this CNA have the training and competency?',
              'Right Direction - Were clear instructions given?',
              'Right Supervision - Will the nurse monitor and evaluate the outcome?',
            ],
          },
          {
            type: 'callout',
            variant: 'warning',
            text: 'If you are unsure about a delegated task, ask before you act. It is never wrong to seek clarification to protect your resident.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['ROLE', 'COMM'],
    },
    {
      lessonId: 'M01-L06',
      moduleId: 'M01',
      lessonNumber: 6,
      title: 'Module 1 Review',
      subtitle: 'Reinforce what you have learned',
      type: 'review',
      estimatedMinutes: 8,
      content: {
        body: [
          {
            type: 'heading',
            text: 'Key Takeaways: Role of the Nurse Aide',
          },
          {
            type: 'summary-list',
            items: [
              'CNAs provide direct care under RN/LVN supervision within a defined scope of practice.',
              'Texas CNA certification requires passing the Prometric NACEP written and clinical skills exams.',
              'Professional behavior, ethics, and confidentiality are non-negotiable.',
              'Delegation follows the Five Rights and the nurse retains accountability.',
              'You are an essential, valued member of the interdisciplinary care team.',
            ],
          },
          {
            type: 'reflection-prompt',
            prompt: 'Think about a healthcare worker who inspired you. What qualities did they demonstrate that you want to carry into your own practice as a CNA?',
          },
        ],
      },
      completionRule: { mode: 'explicit-complete', minimumSeconds: 0 },
      domains: ['ROLE'],
    },
  ],
};

export default M01_BUNDLE;
