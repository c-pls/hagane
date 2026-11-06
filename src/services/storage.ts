import { Exercise, Language, Routine, RoutineExerciseItem } from '../types/gym';
import bundledExercises from '../data/exercises.json';

const ROUTINES_KEY = 'shaken_routines_v1';
const COMMENTS_KEY = 'shaken_comments_v1';
const CUSTOM_EXERCISES_KEY = 'shaken_custom_exercises_v1';
const LANG_KEY = 'shaken_lang_v1';

export function deduplicateRoutineExercises(
  exercises: RoutineExerciseItem[]
): RoutineExerciseItem[] {
  const seen = new Set<string>();
  const deduplicated = exercises.filter((item) => {
    if (seen.has(item.exerciseId)) return false;
    seen.add(item.exerciseId);
    return true;
  });

  // Clean up any orphaned superset groups with fewer than 2 exercises
  const supersetCounts: Record<string, number> = {};
  deduplicated.forEach((item) => {
    if (item.supersetId) {
      supersetCounts[item.supersetId] =
        (supersetCounts[item.supersetId] || 0) + 1;
    }
  });

  return deduplicated.map((item) => {
    if (item.supersetId && (supersetCounts[item.supersetId] || 0) < 2) {
      const copy = { ...item };
      delete copy.supersetId;
      return copy;
    }
    return item;
  });
}

export function sortRoutineExercisesBySection(
  exercises: RoutineExerciseItem[]
): RoutineExerciseItem[] {
  const warmups = exercises.filter((e) => Boolean(e.isWarmup));
  const mains = exercises.filter((e) => !e.isWarmup);
  return [...warmups, ...mains];
}

export function loadLanguage(): Language {
  const saved = localStorage.getItem(LANG_KEY);
  return saved === 'vi' ? 'vi' : 'en';
}

export function saveLanguage(lang: Language): void {
  try {
    localStorage.setItem(LANG_KEY, lang);
  } catch (err) {
    console.error('[Shaken] Failed to save language:', err);
  }
}

const DEFAULT_ROUTINES: Routine[] = [
  {
    id: 'routine-default-1',
    name: 'Leg & Compound Day',
    tag: 'Custom Routine',
    exercises: [
      {
        exerciseId: '0585', // Machine Leg Extension
        isWarmup: true,
        note: 'Light warmup to prime quads & knee joints',
        sets: [
          { weight: 20, reps: 15, type: 'warmup' },
          { weight: 30, reps: 12, type: 'warmup' },
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

export const LAST_SAVED_AT_KEY = 'shaken_last_saved_at';

export function loadRoutines(): Routine[] {
  let parsed: any;
  try {
    const raw = localStorage.getItem(ROUTINES_KEY);
    // Return defaults only on true first launch (key does not exist)
    if (raw === null) return DEFAULT_ROUTINES;
    parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return DEFAULT_ROUTINES;
  } catch (err) {
    console.error('[Shaken] Error parsing stored routines from localStorage:', err);
    try {
      const raw = localStorage.getItem(ROUTINES_KEY);
      if (raw) {
        localStorage.setItem(ROUTINES_KEY + '_corrupt_bak', raw);
      }
    } catch {}
    return DEFAULT_ROUTINES;
  }

  // Migrate legacy comments in an isolated block so comments parse never fails routines load
  let legacyComments: Record<string, string> = {};
  try {
    const legacyRaw = localStorage.getItem(COMMENTS_KEY);
    if (legacyRaw) {
      legacyComments = JSON.parse(legacyRaw) || {};
    }
  } catch {
    legacyComments = {};
  }

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
}

export function saveRoutines(routines: Routine[]): boolean {
  try {
    localStorage.setItem(ROUTINES_KEY, JSON.stringify(routines));
    localStorage.setItem(LAST_SAVED_AT_KEY, String(Date.now()));
    return true;
  } catch (err) {
    console.error('[Shaken] Failed to save routines to localStorage:', err);
    return false;
  }
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
  try {
    localStorage.setItem(COMMENTS_KEY, JSON.stringify(comments));
  } catch (err) {
    console.error('[Shaken] Failed to save comments to localStorage:', err);
  }
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
  try {
    localStorage.setItem(CUSTOM_EXERCISES_KEY, JSON.stringify(custom));
  } catch (err) {
    console.error('[Shaken] Failed to save custom exercises to localStorage:', err);
  }
}

export function getAllExercises(customExercises: Exercise[]): Exercise[] {
  return [...customExercises, ...(bundledExercises as Exercise[])];
}


