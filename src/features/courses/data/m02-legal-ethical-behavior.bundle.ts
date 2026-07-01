// m02-legal-ethical-behavior.bundle.ts
// Module 2 Content Bundle: Legal & Ethical Behavior
// Texas CNA Academy - Prometric Aligned

import type { CourseModuleBundle } from '../types/courses.types';

export const M02_BUNDLE: CourseModuleBundle = {
  module: {
    moduleId: 'M02',
    title: 'Legal & Ethical Behavior',
    description: 'Learn HIPAA, abuse reporting obligations, advance directives, professional boundaries, and ethical decision-making as a CNA.',
    moduleNumber: 2,
    estimatedMinutes: 50,
    lessonIds: ['M02-L01', 'M02-L02', 'M02-L03', 'M02-L04', 'M02-L05', 'M02-L06', 'M02-L07'],
    domains: ['LEGAL', 'ELDERCARE', 'COMM'],
    primaryDomain: 'LEGAL',
    status: 'available',
    prerequisiteModuleIds: ['M01'],
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
      lessonId: 'M02-L01',
      moduleId: 'M02',
      lessonNumber: 1,
      title: 'HIPAA and Confidentiality',
      subtitle: 'Privacy is sacred',
      type: 'standard',
      estimatedMinutes: 8,
      content: {
        body: [
          {
            type: 'heading',
            text: 'What is HIPAA?',
          },
          {
            type: 'paragraph',
            text: 'The Health Insurance Portability and Accountability Act (HIPAA) protects patient health information (PHI) from unauthorized access, use, or disclosure. As a CNA, you are a HIPAA-covered entity and MUST protect resident privacy at all times.',
          },
          {
            type: 'callout',
            variant: 'warning',
            text: 'HIPAA violations can result in fines, job termination, and even criminal prosecution. If you are unsure, ask your nurse before sharing any resident information.',
          },
          {
            type: 'heading',
            text: 'What is Protected Health Information (PHI)?',
          },
          {
            type: 'list',
            items: [
              'Resident name, address, date of birth',
              'Medical diagnosis, medications, treatment plans',
              'Insurance and financial information',
              'Social Security Number',
              'Anything that could identify a resident (photos, room number, identifying characteristics)',
            ],
          },
          {
            type: 'callout',
            variant: 'tip',
            text: 'Never discuss resident information in hallways, elevators, the cafeteria, or on social media. Even if you do not use names, identifying details can violate HIPAA.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['LEGAL'],
    },
    {
      lessonId: 'M02-L02',
      moduleId: 'M02',
      lessonNumber: 2,
      title: 'Abuse, Neglect, and Reporting Obligations',
      subtitle: 'You are a mandated reporter',
      type: 'standard',
      estimatedMinutes: 9,
      content: {
        body: [
          {
            type: 'heading',
            text: 'Types of Abuse and Neglect',
          },
          {
            type: 'table',
            headers: ['Type', 'Definition', 'Examples'],
            rows: [
              ['Physical Abuse', 'Inflicting physical pain or injury', 'Hitting, slapping, rough handling, restraint misuse'],
              ['Emotional/Psychological Abuse', 'Causing emotional pain or distress', 'Yelling, humiliating, threatening, isolating'],
              ['Sexual Abuse', 'Non-consensual sexual contact', 'Unwanted touching, sexual comments, exposure'],
              ['Financial Abuse', 'Misuse of resident funds or property', 'Stealing, forging signatures, coercion'],
              ['Neglect', 'Failure to provide needed care', 'Withholding food, hygiene, medication, or assistance'],
            ],
          },
          {
            type: 'callout',
            variant: 'warning',
            text: 'CNAs in Texas are mandated reporters. You MUST report suspected abuse or neglect immediately to your supervisor, administrator, or the Texas Department of Family and Protective Services (DFPS). Failure to report is a crime.',
          },
          {
            type: 'heading',
            text: 'How to Report Abuse',
          },
          {
            type: 'steps',
            items: [
              { step: 1, title: 'Report to your charge nurse immediately', description: 'Never delay reporting. Time matters.' },
              { step: 2, title: 'Document what you observed', description: 'Be objective. Use facts, not opinions (e.g., "Bruise on left arm" not "probably abuse").' },
              { step: 3, title: 'Call Texas DFPS hotline if needed', description: '1-800-252-5400 (available 24/7)' },
              { step: 4, title: 'Follow your facility protocol', description: 'Do not confront the suspected abuser. Let administrators investigate.' },
            ],
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['LEGAL', 'ELDERCARE'],
    },
    {
      lessonId: 'M02-L03',
      moduleId: 'M02',
      lessonNumber: 3,
      title: 'Advance Directives',
      subtitle: 'Respecting end-of-life wishes',
      type: 'standard',
      estimatedMinutes: 7,
      content: {
        body: [
          {
            type: 'heading',
            text: 'What Are Advance Directives?',
          },
          {
            type: 'paragraph',
            text: 'Advance directives are legal documents that allow a person to specify their medical treatment preferences in advance, especially for end-of-life care.',
          },
          {
            type: 'list',
            items: [
              'Living Will - Specifies what treatments a person wants or does not want if unable to communicate',
              'Durable Power of Attorney for Healthcare - Designates someone to make healthcare decisions on their behalf',
              'Do Not Resuscitate (DNR) Order - Directs healthcare providers NOT to perform CPR if the heart or breathing stops',
            ],
          },
          {
            type: 'callout',
            variant: 'faith',
            text: 'Honoring a resident's wishes at the end of life is one of the most sacred responsibilities you will carry. You are present for their final chapter — handle it with reverence.',
          },
          {
            type: 'heading',
            text: 'CNA Role with Advance Directives',
          },
          {
            type: 'paragraph',
            text: 'CNAs do NOT make decisions about advance directives, but you must know if a resident has them and honor their wishes. If a resident with a DNR stops breathing, do NOT perform CPR — immediately notify the nurse.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['LEGAL', 'ELDERCARE'],
    },
    {
      lessonId: 'M02-L04',
      moduleId: 'M02',
      lessonNumber: 4,
      title: 'Professional Boundaries',
      subtitle: 'Keeping the relationship therapeutic',
      type: 'standard',
      estimatedMinutes: 7,
      content: {
        body: [
          {
            type: 'heading',
            text: 'What Are Professional Boundaries?',
          },
          {
            type: 'paragraph',
            text: 'Professional boundaries are the limits that maintain a safe, therapeutic relationship between CNAs and residents. Crossing boundaries can harm residents and jeopardize your license.',
          },
          {
            type: 'heading',
            text: 'Boundary Violations to Avoid',
          },
          {
            type: 'list',
            items: [
              'Accepting money, gifts, or loans from residents or families',
              'Sharing personal problems or asking residents for advice',
              'Engaging in romantic or sexual relationships with residents',
              'Providing care outside of work hours without facility approval',
              'Adding residents to personal social media accounts',
              'Using resident property (phone, TV, personal items) without permission',
            ],
          },
          {
            type: 'callout',
            variant: 'tip',
            text: 'If a resident or family member offers you a gift, politely decline or report it to your supervisor. Most facilities have a no-gift policy to protect staff and residents.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['LEGAL', 'COMM'],
    },
    {
      lessonId: 'M02-L05',
      moduleId: 'M02',
      lessonNumber: 5,
      title: 'Ethical Decision Making',
      subtitle: 'Doing right when no one is watching',
      type: 'standard',
      estimatedMinutes: 7,
      content: {
        body: [
          {
            type: 'heading',
            text: 'Core Ethical Principles for CNAs',
          },
          {
            type: 'table',
            headers: ['Principle', 'Meaning', 'CNA Application'],
            rows: [
              ['Autonomy', 'Respecting resident choices', 'Let residents choose their clothes, food, schedule (within safety limits)'],
              ['Beneficence', 'Acting in the resident's best interest', 'Provide care that promotes well-being, comfort, and dignity'],
              ['Nonmaleficence', 'Do no harm', 'Never take shortcuts that could injure or neglect a resident'],
              ['Justice', 'Treating everyone fairly', 'Give equal care regardless of resident behavior, background, or diagnosis'],
              ['Fidelity', 'Being faithful to commitments', 'Follow through on promises; show up on time; do your best work'],
            ],
          },
          {
            type: 'callout',
            variant: 'encouragement',
            text: 'Ethics is who you are when no one is looking. The right choice is not always the easiest choice, but it is always worth it.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['LEGAL', 'ELDERCARE'],
    },
    {
      lessonId: 'M02-L06',
      moduleId: 'M02',
      lessonNumber: 6,
      title: 'Liability and Legal Protections',
      subtitle: 'Understanding your responsibilities and rights',
      type: 'standard',
      estimatedMinutes: 7,
      content: {
        body: [
          {
            type: 'heading',
            text: 'What is Liability?',
          },
          {
            type: 'paragraph',
            text: 'Liability means legal responsibility. As a CNA, you are personally and professionally responsible for your actions. Even though you work under nurse supervision, you can be held liable for harm caused by negligence, malpractice, or unsafe practice.',
          },
          {
            type: 'heading',
            text: 'How to Protect Yourself Legally',
          },
          {
            type: 'list',
            items: [
              'Work within your scope of practice — never perform tasks you were not trained for',
              'Follow facility policies and procedures at all times',
              'Document accurately, objectively, and on time',
              'Report unsafe conditions or staffing shortages immediately',
              'Ask for clarification if instructions are unclear',
              'Consider purchasing professional liability insurance (malpractice coverage)',
            ],
          },
          {
            type: 'callout',
            variant: 'warning',
            text: 'If you make a mistake, report it immediately. Attempting to cover up an error can result in legal consequences far worse than the original mistake.',
          },
        ],
      },
      completionRule: { mode: 'scroll-and-time', minimumSeconds: 30 },
      domains: ['LEGAL'],
    },
    {
      lessonId: 'M02-L07',
      moduleId: 'M02',
      lessonNumber: 7,
      title: 'Module 2 Review',
      subtitle: 'Reinforce what you have learned',
      type: 'review',
      estimatedMinutes: 8,
      content: {
        body: [
          {
            type: 'heading',
            text: 'Key Takeaways: Legal & Ethical Behavior',
          },
          {
            type: 'summary-list',
            items: [
              'HIPAA protects resident privacy; never discuss PHI in public or on social media.',
              'CNAs are mandated reporters; you MUST report suspected abuse or neglect.',
              'Advance directives (Living Will, DNR) must be honored by all care team members.',
              'Maintain professional boundaries; do not accept gifts or engage in dual relationships.',
              'Ethical practice is based on autonomy, beneficence, nonmaleficence, justice, and fidelity.',
              'You are personally liable for your actions; document accurately and work within your scope.',
            ],
          },
          {
            type: 'reflection-prompt',
            prompt: 'Think of a time when you faced an ethical dilemma. How did you decide what was right? What values guided your decision?',
          },
        ],
      },
      completionRule: { mode: 'explicit-complete', minimumSeconds: 0 },
      domains: ['LEGAL'],
    },
  ],
};

export default M02_BUNDLE;
