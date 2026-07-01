// domain-labels.ts
// Standardized Prometric domain short-labels for Texas CNA Academy
// Aligned with NNAAP / Prometric CNA exam domains

export type PrometricDomainKey =
  | 'ROLE'
  | 'SAFETY'
  | 'INFECT'
  | 'COMM'
  | 'ELDERCARE'
  | 'PERSONAL'
  | 'NUTRITION'
  | 'ELIMINATION'
  | 'RESTORATIVE'
  | 'PSYCHOSOCIAL'
  | 'SPIRITUAL'
  | 'LEGAL'
  | 'VITALS'
  | 'SKILLS';

export interface DomainLabel {
  key: PrometricDomainKey;
  shortLabel: string;
  fullLabel: string;
  description: string;
  color: string; // Tailwind color token for UI badge
  icon: string;  // Icon identifier (e.g., heroicons name)
}

export const DOMAIN_LABELS: Record<PrometricDomainKey, DomainLabel> = {
  ROLE: {
    key: 'ROLE',
    shortLabel: 'Role & Scope',
    fullLabel: 'Role and Responsibilities of the Nurse Aide',
    description: 'Understanding the CNA role, scope of practice, and working within the healthcare team.',
    color: 'blue',
    icon: 'user-circle',
  },
  SAFETY: {
    key: 'SAFETY',
    shortLabel: 'Safety',
    fullLabel: 'Safety and Emergency Procedures',
    description: 'Fall prevention, restraints, fire safety, disaster preparedness, and emergency response.',
    color: 'red',
    icon: 'shield-check',
  },
  INFECT: {
    key: 'INFECT',
    shortLabel: 'Infection Control',
    fullLabel: 'Infection Control',
    description: 'Standard precautions, hand hygiene, PPE, isolation, and preventing HAIs.',
    color: 'green',
    icon: 'beaker',
  },
  COMM: {
    key: 'COMM',
    shortLabel: 'Communication',
    fullLabel: 'Communication and Interpersonal Skills',
    description: 'Verbal and nonverbal communication, active listening, and documentation.',
    color: 'purple',
    icon: 'chat-bubble-left-right',
  },
  ELDERCARE: {
    key: 'ELDERCARE',
    shortLabel: 'Resident Rights',
    fullLabel: 'Resident Rights and Promotion of Independence',
    description: 'OBRA regulations, privacy, dignity, choice, and resident advocacy.',
    color: 'orange',
    icon: 'heart',
  },
  PERSONAL: {
    key: 'PERSONAL',
    shortLabel: 'Personal Care',
    fullLabel: 'Personal Care Skills',
    description: 'Bathing, grooming, oral care, dressing, and skin integrity.',
    color: 'pink',
    icon: 'sparkles',
  },
  NUTRITION: {
    key: 'NUTRITION',
    shortLabel: 'Nutrition',
    fullLabel: 'Nutrition and Hydration',
    description: 'Feeding assistance, fluid intake, special diets, and aspiration prevention.',
    color: 'yellow',
    icon: 'cake',
  },
  ELIMINATION: {
    key: 'ELIMINATION',
    shortLabel: 'Elimination',
    fullLabel: 'Elimination',
    description: 'Bowel and bladder care, catheter care, and specimen collection.',
    color: 'teal',
    icon: 'arrow-path',
  },
  RESTORATIVE: {
    key: 'RESTORATIVE',
    shortLabel: 'Restorative',
    fullLabel: 'Restorative Skills',
    description: 'Range of motion, assistive devices, ambulation, and rehabilitation support.',
    color: 'cyan',
    icon: 'arrow-trending-up',
  },
  PSYCHOSOCIAL: {
    key: 'PSYCHOSOCIAL',
    shortLabel: 'Psychosocial',
    fullLabel: 'Psychosocial Care Skills',
    description: 'Mental health, behavioral support, dementia care, and emotional well-being.',
    color: 'violet',
    icon: 'face-smile',
  },
  SPIRITUAL: {
    key: 'SPIRITUAL',
    shortLabel: 'Spiritual Care',
    fullLabel: 'Spiritual and Cultural Considerations',
    description: 'Respecting religious practices, cultural humility, and end-of-life spiritual support.',
    color: 'indigo',
    icon: 'star',
  },
  LEGAL: {
    key: 'LEGAL',
    shortLabel: 'Legal & Ethics',
    fullLabel: 'Legal and Ethical Behavior',
    description: 'Abuse reporting, HIPAA, advance directives, and professional boundaries.',
    color: 'gray',
    icon: 'scale',
  },
  VITALS: {
    key: 'VITALS',
    shortLabel: 'Vital Signs',
    fullLabel: 'Basic Nursing Skills - Vital Signs',
    description: 'Temperature, pulse, respiration, blood pressure, and oxygen saturation.',
    color: 'rose',
    icon: 'heart-pulse',
  },
  SKILLS: {
    key: 'SKILLS',
    shortLabel: 'Clinical Skills',
    fullLabel: 'Clinical Skills Lab',
    description: 'Hands-on procedural skills evaluated in the Prometric clinical skills exam.',
    color: 'lime',
    icon: 'clipboard-document-check',
  },
};

export const DOMAIN_KEYS = Object.keys(DOMAIN_LABELS) as PrometricDomainKey[];

export function getDomainLabel(key: PrometricDomainKey): DomainLabel {
  return DOMAIN_LABELS[key];
}

export function getDomainShortLabel(key: PrometricDomainKey): string {
  return DOMAIN_LABELS[key].shortLabel;
}
