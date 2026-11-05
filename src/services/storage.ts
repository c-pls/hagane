import { Exercise, Language, Routine } from '../types/gym';
import bundledExercises from '../data/exercises.json';

const ROUTINES_KEY = 'shaken_routines_v1';
const COMMENTS_KEY = 'shaken_comments_v1';
const CUSTOM_EXERCISES_KEY = 'shaken_custom_exercises_v1';
const LANG_KEY = 'shaken_lang_v1';

export function loadLanguage(): Language {
  const saved = localStorage.getItem(LANG_KEY);
  return saved === 'vi' ? 'vi' : 'en';
}

export function saveLanguage(lang: Language): void {
  localStorage.setItem(LANG_KEY, lang);
}

const DEFAULT_ROUTINES: Routine[] = [
  {
    id: 'routine-default-1',
    name: 'Leg & Compound Day',
    tag: 'Custom Routine',
    exercises: [
      {
        exerciseId: '1435', // Barbell Back Squat
        isWarmup: true,
        note: 'Light warmup to prime hip mobility & knees',
        sets: [
          { weight: 20, reps: 15, type: 'warmup' },
          { weight: 40, reps: 10, type: 'warmup' },
        ],
      },
      {
        exerciseId: '1435', // Barbell Back Squat
        isWarmup: false,
        note: 'Rack pin #11. Focus on bracing core and driving knees out.',
        sets: [
          { weight: 50, reps: 8, type: 'warmup' },
          { weight: 70, reps: 10, type: 'normal' },
          { weight: 70, reps: 10, type: 'normal' },
        ],
      },
      {
        exerciseId: '0116', // Barbell Straight Leg Deadlift
        isWarmup: false,
        sets: [
          { weight: 50, reps: 10, type: 'warmup' },
          { weight: 80, reps: 10, type: 'normal' },
          { weight: 80, reps: 10, type: 'normal' },
        ],
      },
    ],
  },
  {
    id: 'routine-default-2',
    name: 'Upper Body Push & Pull',
    tag: 'Custom Routine',
    exercises: [
      {
        exerciseId: '0025', // Barbell Bench Press
        isWarmup: false,
        sets: [
          { weight: 40, reps: 10, type: 'warmup' },
          { weight: 60, reps: 10, type: 'normal' },
          { weight: 60, reps: 10, type: 'normal' },
        ],
      },
      {
        exerciseId: '0027', // Barbell Underhand Bent-Over Row
        isWarmup: false,
        sets: [
          { weight: 30, reps: 12, type: 'warmup' },
          { weight: 50, reps: 10, type: 'normal' },
          { weight: 50, reps: 10, type: 'normal' },
        ],
      },
    ],
  },
];

export function loadRoutines(): Routine[] {
  try {
    const raw = localStorage.getItem(ROUTINES_KEY);
    if (!raw) return DEFAULT_ROUTINES;
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return DEFAULT_ROUTINES;

    // Migrate any legacy global comments into routine items if item.note is undefined
    const legacyRaw = localStorage.getItem(COMMENTS_KEY);
    const legacyComments: Record<string, string> = legacyRaw
      ? JSON.parse(legacyRaw) || {}
      : { '1435': 'Rack pin #11. Focus on bracing core and driving knees out.' };

    return parsed.map((r: Routine) => ({
      ...r,
      exercises: (r.exercises || []).map((item) => ({
        ...item,
        note:
          item.note !== undefined
            ? item.note
            : legacyComments[item.exerciseId] || '',
      })),
    }));
  } catch {
    return DEFAULT_ROUTINES;
  }
}

export function saveRoutines(routines: Routine[]): void {
  localStorage.setItem(ROUTINES_KEY, JSON.stringify(routines));
}

export function loadComments(): Record<string, string> {
  try {
    const raw = localStorage.getItem(COMMENTS_KEY);
    if (!raw) return {};
    return JSON.parse(raw) || {};
  } catch {
    return {};
  }
}

export function saveComments(comments: Record<string, string>): void {
  localStorage.setItem(COMMENTS_KEY, JSON.stringify(comments));
}

export function loadCustomExercises(): Exercise[] {
  try {
    const raw = localStorage.getItem(CUSTOM_EXERCISES_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveCustomExercises(custom: Exercise[]): void {
  localStorage.setItem(CUSTOM_EXERCISES_KEY, JSON.stringify(custom));
}

export function getAllExercises(customExercises: Exercise[]): Exercise[] {
  return [...customExercises, ...(bundledExercises as Exercise[])];
}

export interface ShakenBackupPayload {
  version: number;
  exportedAt: string;
  routines: Routine[];
  comments: Record<string, string>;
  customExercises: Exercise[];
}

export function exportBackupJSON(
  routines: Routine[],
  comments: Record<string, string>,
  customExercises: Exercise[]
): string {
  const payload: ShakenBackupPayload = {
    version: 1,
    exportedAt: new Date().toISOString(),
    routines,
    comments,
    customExercises,
  };
  return JSON.stringify(payload, null, 2);
}

export function parseBackupJSON(rawJson: string): ShakenBackupPayload {
  const parsed = JSON.parse(rawJson);
  if (!parsed || !Array.isArray(parsed.routines)) {
    throw new Error('Invalid backup format: missing routines array.');
  }
  return {
    version: parsed.version || 1,
    exportedAt: parsed.exportedAt || new Date().toISOString(),
    routines: parsed.routines,
    comments: parsed.comments || {},
    customExercises: Array.isArray(parsed.customExercises)
      ? parsed.customExercises
      : [],
  };
}
