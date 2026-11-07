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

function groupContiguousSupersets(
  sectionExercises: RoutineExerciseItem[]
): RoutineExerciseItem[] {
  // Count how many exercises belong to each supersetId in this section
  const counts: Record<string, number> = {};
  for (const item of sectionExercises) {
    if (item.supersetId) {
      counts[item.supersetId] = (counts[item.supersetId] || 0) + 1;
    }
  }

  // Group exercises sharing a valid supersetId (>= 2 members) together as a single contiguous block
  const result: RoutineExerciseItem[] = [];
  const placedGroupIds = new Set<string>();

  for (const item of sectionExercises) {
    const sId = item.supersetId;
    if (!sId) {
      result.push(item);
      continue;
    }

    if ((counts[sId] || 0) < 2) {
      // Orphan single exercise -> strip supersetId
      const copy = { ...item };
      delete copy.supersetId;
      result.push(copy);
      continue;
    }

    if (placedGroupIds.has(sId)) {
      // Already placed as part of its superset block
      continue;
    }

    placedGroupIds.add(sId);
    for (const member of sectionExercises) {
      if (member.supersetId === sId) {
        result.push(member);
      }
    }
  }

  return result;
}

export function sortRoutineExercisesBySection(
  exercises: RoutineExerciseItem[]
): RoutineExerciseItem[] {
  const warmups = groupContiguousSupersets(
    exercises.filter((e) => Boolean(e.isWarmup))
  );
  const mains = groupContiguousSupersets(
    exercises.filter((e) => !e.isWarmup)
  );
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

const DEFAULT_ROUTINES: Routine[] = [];

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

export const REST_TIME_PRESETS = [45, 60, 90, 120, 150, 180, 240] as const;

export function getDefaultRestSeconds(
  exercise: Exercise | undefined,
  isWarmup?: boolean
): number {
  if (isWarmup) return 60;
  if (!exercise) return 90;

  const n = `${exercise.name} ${exercise.nameVi || ''}`.toLowerCase();
  const eq = (exercise.equipment || '').toLowerCase();
  const isCompound =
    eq === 'barbell' ||
    n.includes('squat') ||
    n.includes('deadlift') ||
    n.includes('rdl') ||
    n.includes('leg press') ||
    n.includes('bench press') ||
    n.includes('overhead press') ||
    n.includes('shoulder press') ||
    n.includes('pull-up') ||
    n.includes('pull up') ||
    n.includes('chin-up') ||
    n.includes('row') ||
    n.includes('dip') ||
    n.includes('gánh tạ') ||
    n.includes('kéo tạ') ||
    n.includes('đẩy ngực') ||
    n.includes('đẩy vai') ||
    n.includes('kéo xô') ||
    n.includes('hít xà') ||
    n.includes('xà kép') ||
    n.includes('đạp đùi');

  return isCompound ? 150 : 90;
}

export function formatRestTime(seconds: number): string {
  const safe = Math.max(0, Math.round(seconds));
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

export function getAllExercises(customExercises: Exercise[]): Exercise[] {
  return [...customExercises, ...(bundledExercises as Exercise[])];
}


