import { Exercise, Language, Routine, RoutineExerciseItem, WorkoutSet } from '../types/gym';
import bundledExercises from '../data/exercises.json';

const ROUTINES_KEY = 'hagane_routines_v1';
const COMMENTS_KEY = 'hagane_comments_v1';
const CUSTOM_EXERCISES_KEY = 'hagane_custom_exercises_v1';
const LANG_KEY = 'hagane_lang_v1';

/**
 * Legacy exercise IDs that were merged into canonical exercises to eliminate duplicate videos.
 */
const LEGACY_EXERCISE_ID_MAP: Record<string, string> = {
  '0339': '0343', // Dumbbell Lying Femoral -> Dumbbell Lying Leg Curl
  '1731': '0296', // Dumbbell Hex/Crush Press -> Dumbbell Close-Grip / Hex Press
};

let storageCorruptionLocked = false;
let customCorruptionLocked = false;

export function isStorageCorruptionLocked(): boolean {
  return storageCorruptionLocked;
}

export function isCustomCorruptionLocked(): boolean {
  return customCorruptionLocked;
}

export function clearStorageCorruptionLock(deleteBackup = false): void {
  storageCorruptionLocked = false;
  if (deleteBackup) {
    try {
      localStorage.removeItem(ROUTINES_KEY + '_corrupt_bak');
    } catch {
      // ignore
    }
  }
}

export function clearCustomCorruptionLock(deleteBackup = false): void {
  customCorruptionLocked = false;
  if (deleteBackup) {
    try {
      localStorage.removeItem(CUSTOM_EXERCISES_KEY + '_corrupt_bak');
    } catch {
      // ignore
    }
  }
}

export function getCorruptBackupRaw(): string | null {
  try {
    return localStorage.getItem(ROUTINES_KEY + '_corrupt_bak');
  } catch {
    return null;
  }
}

export function getCorruptCustomBackupRaw(): string | null {
  try {
    return localStorage.getItem(CUSTOM_EXERCISES_KEY + '_corrupt_bak');
  } catch {
    return null;
  }
}

export function deduplicateRoutineExercises(
  exercises: RoutineExerciseItem[]
): RoutineExerciseItem[] {
  return sanitizeRoutineExercises(exercises);
}

export function sanitizeRoutineExercises(
  exercises: RoutineExerciseItem[]
): RoutineExerciseItem[] {
  // Defensive validation: filter out completely invalid items
  const validItems = exercises.filter((item) => {
    return (
      item &&
      typeof item.exerciseId === 'string' &&
      item.exerciseId.trim() !== '' &&
      Array.isArray(item.sets)
    );
  });

  // Deduplicate by exerciseId: keep first occurrence, merge sets from duplicates
  const seenMap = new Map<string, RoutineExerciseItem>();
  const dedupedItems: RoutineExerciseItem[] = [];

  for (const item of validItems) {
    const existing = seenMap.get(item.exerciseId);
    if (!existing) {
      const copy = { ...item, sets: [...item.sets] };
      seenMap.set(item.exerciseId, copy);
      dedupedItems.push(copy);
    } else {
      // Merge sets from duplicate exercise item so user's recorded sets are not lost
      if (Array.isArray(item.sets) && item.sets.length > 0) {
        existing.sets.push(...item.sets);
      }
    }
  }

  // Clean up any orphaned superset groups with fewer than 2 exercises within the same section
  const supersetCounts: Record<string, number> = {};
  dedupedItems.forEach((item) => {
    if (item.supersetId) {
      const sectionKey = `${item.isWarmup ? 'W' : 'M'}:${item.supersetId}`;
      supersetCounts[sectionKey] = (supersetCounts[sectionKey] || 0) + 1;
    }
  });

  return dedupedItems.map((item) => {
    if (item.supersetId) {
      const sectionKey = `${item.isWarmup ? 'W' : 'M'}:${item.supersetId}`;
      if ((supersetCounts[sectionKey] || 0) < 2) {
        const copy = { ...item };
        delete copy.supersetId;
        return copy;
      }
    }
    return item;
  });
}

function groupContiguousSupersets(
  sectionExercises: RoutineExerciseItem[]
): RoutineExerciseItem[] {
  const counts: Record<string, number> = {};
  for (const item of sectionExercises) {
    if (item.supersetId) {
      counts[item.supersetId] = (counts[item.supersetId] || 0) + 1;
    }
  }

  const result: RoutineExerciseItem[] = [];
  const placedGroupIds = new Set<string>();

  for (const item of sectionExercises) {
    const sId = item.supersetId;
    if (!sId) {
      result.push(item);
      continue;
    }

    if ((counts[sId] || 0) < 2) {
      const copy = { ...item };
      delete copy.supersetId;
      result.push(copy);
      continue;
    }

    if (placedGroupIds.has(sId)) {
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

/**
 * Defensive validator and normalizer for any Routine array loaded from localStorage or device backup.
 * Prevents malformed objects, null entries, or non-array fields from crashing the app at boot.
 */
export function sanitizeRoutines(
  rawRoutines: unknown,
  legacyComments: Record<string, string> = {}
): Routine[] {
  if (!Array.isArray(rawRoutines)) return [];

  const sanitized: Routine[] = [];
  const seenRoutineIds = new Set<string>();

  for (let i = 0; i < rawRoutines.length; i++) {
    const r = rawRoutines[i];
    if (!r || typeof r !== 'object') continue;
    const obj = r as Record<string, unknown>;

    let id =
      typeof obj.id === 'string' && obj.id.trim()
        ? obj.id.trim()
        : `routine-${Date.now()}-${i}`;
    if (seenRoutineIds.has(id)) {
      id = `${id}-${i + 1}`;
    }
    seenRoutineIds.add(id);
    const name =
      typeof obj.name === 'string' && obj.name.trim()
        ? obj.name.trim()
        : `Workout #${i + 1}`;
    const tag = typeof obj.tag === 'string' ? obj.tag.trim() : '';

    const rawExercises = Array.isArray(obj.exercises) ? obj.exercises : [];
    const validExercises: RoutineExerciseItem[] = [];

    for (const rawEx of rawExercises) {
      if (!rawEx || typeof rawEx !== 'object') continue;
      const exObj = rawEx as Record<string, unknown>;
      if (typeof exObj.exerciseId !== 'string' || !exObj.exerciseId.trim()) {
        continue;
      }

      const rawId = exObj.exerciseId.trim();
      const canonicalId = LEGACY_EXERCISE_ID_MAP[rawId] || rawId;
      const isWarmup = Boolean(exObj.isWarmup);

      const rawSets = Array.isArray(exObj.sets) ? exObj.sets : [];
      const validSets: WorkoutSet[] = [];
      for (const rawSet of rawSets) {
        if (!rawSet || typeof rawSet !== 'object') continue;
        const sObj = rawSet as Record<string, unknown>;
        const weightNum = Number(sObj.weight);
        const repsNum = Number(sObj.reps);
        const setType =
          sObj.type === 'warmup' || sObj.type === 'drop'
            ? sObj.type
            : isWarmup
              ? 'warmup'
              : 'normal';

        validSets.push({
          weight:
            Number.isFinite(weightNum) && weightNum >= 0
              ? Math.min(1000, Math.round(weightNum * 10) / 10)
              : 0,
          reps:
            Number.isFinite(repsNum) && repsNum >= 1
              ? Math.min(500, Math.round(repsNum))
              : isWarmup
                ? 15
                : 10,
          type: setType,
        });
      }

      if (validSets.length === 0) {
        validSets.push({
          weight: 0,
          reps: isWarmup ? 15 : 10,
          type: isWarmup ? 'warmup' : 'normal',
        });
      }

      const restNum = Number(exObj.restSeconds);
      const restSeconds =
        Number.isFinite(restNum) && restNum > 0
          ? Math.max(15, Math.min(900, Math.round(restNum)))
          : undefined;

      const supersetId =
        typeof exObj.supersetId === 'string' && exObj.supersetId.trim()
          ? exObj.supersetId.trim()
          : undefined;

      const note =
        typeof exObj.note === 'string'
          ? exObj.note
          : legacyComments[canonicalId] || legacyComments[rawId] || '';

      validExercises.push({
        exerciseId: canonicalId,
        isWarmup,
        supersetId,
        restSeconds,
        note,
        sets: validSets,
      });
    }

    sanitized.push({
      id,
      name,
      tag,
      exercises: sortRoutineExercisesBySection(
        deduplicateRoutineExercises(validExercises)
      ),
    });
  }

  return sanitized;
}

export function sanitizeCustomExercises(rawCustom: unknown): Exercise[] {
  if (!Array.isArray(rawCustom)) return [];
  const valid: Exercise[] = [];

  for (const item of rawCustom) {
    if (!item || typeof item !== 'object') continue;
    const obj = item as Record<string, unknown>;

    // Strict validation: reject malformed custom exercises without required fields
    if (
      typeof obj.id !== 'string' ||
      !obj.id.trim() ||
      typeof obj.name !== 'string' ||
      !obj.name.trim() ||
      typeof obj.category !== 'string' ||
      !obj.category.trim() ||
      typeof obj.equipment !== 'string' ||
      !obj.equipment.trim()
    ) {
      console.warn('[Hagane] Dropping malformed custom exercise:', obj.id || 'unknown');
      continue;
    }

    const toStrArr = (val: unknown, fallback: string[] = []): string[] =>
      Array.isArray(val)
        ? val.filter((v): v is string => typeof v === 'string' && v.trim().length > 0)
        : fallback;

    let primaryMuscles = toStrArr(obj.primaryMuscles);
    if (primaryMuscles.length === 0 && typeof obj.category === 'string' && obj.category.trim()) {
      primaryMuscles = [obj.category.trim()];
    }
    if (primaryMuscles.length === 0) {
      console.warn('[Hagane] Dropping custom exercise with empty primaryMuscles:', obj.id);
      continue;
    }

    const stepsRaw =
      obj.steps && typeof obj.steps === 'object'
        ? (obj.steps as Record<string, unknown>)
        : {};
    const stepsViRaw =
      obj.stepsVi && typeof obj.stepsVi === 'object'
        ? (obj.stepsVi as Record<string, unknown>)
        : stepsRaw;

    const steps = {
      prepare: toStrArr(stepsRaw.prepare),
      execution: toStrArr(stepsRaw.execution),
      breathing: toStrArr(stepsRaw.breathing),
    };

    const stepsVi = {
      prepare: toStrArr(stepsViRaw.prepare, steps.prepare),
      execution: toStrArr(stepsViRaw.execution, steps.execution),
      breathing: toStrArr(stepsViRaw.breathing, steps.breathing),
    };

    valid.push({
      id: obj.id.trim(),
      slug: typeof obj.slug === 'string' && obj.slug.trim() ? obj.slug.trim() : obj.id.trim(),
      name: obj.name.trim(),
      nameVi: typeof obj.nameVi === 'string' && obj.nameVi.trim() ? obj.nameVi.trim() : obj.name.trim(),
      aliases: toStrArr(obj.aliases),
      category: obj.category.trim(),
      equipment: obj.equipment.trim(),
      videoUrl: typeof obj.videoUrl === 'string' ? obj.videoUrl.trim() : '',
      primaryMuscles,
      secondaryMuscles: toStrArr(obj.secondaryMuscles),
      primarySlugs: toStrArr(obj.primarySlugs),
      secondarySlugs: toStrArr(obj.secondarySlugs),
      shortDescription:
        typeof obj.shortDescription === 'string' && obj.shortDescription.trim()
          ? obj.shortDescription.trim()
          : `Custom exercise: ${obj.name.trim()}`,
      steps,
      stepsVi,
    });
  }

  return valid;
}

export function loadLanguage(): Language {
  try {
    const saved = localStorage.getItem(LANG_KEY);
    return saved === 'vi' ? 'vi' : 'en';
  } catch {
    return 'en';
  }
}

export function saveLanguage(lang: Language): boolean {
  try {
    localStorage.setItem(LANG_KEY, lang);
    return true;
  } catch (err) {
    console.error('[Hagane] Failed to save language:', err);
    return false;
  }
}

const DEFAULT_ROUTINES: Routine[] = [];

export const LAST_SAVED_AT_KEY = 'hagane_last_saved_at';

export function loadRoutines(): Routine[] {
  let raw: string | null = null;
  try {
    raw = localStorage.getItem(ROUTINES_KEY);
    if (raw === null) return DEFAULT_ROUTINES;

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      throw new Error('Stored routines payload is not an array');
    }

    // Migrate legacy comments in an isolated block so comments parse never fails routines load
    let legacyComments: Record<string, string> = {};
    try {
      const legacyRaw = localStorage.getItem(COMMENTS_KEY);
      if (legacyRaw) {
        const parsedComments = JSON.parse(legacyRaw);
        if (parsedComments && typeof parsedComments === 'object') {
          legacyComments = parsedComments as Record<string, string>;
        }
      }
    } catch {
      legacyComments = {};
    }

    return sanitizeRoutines(parsed, legacyComments);
  } catch (err) {
    console.error('[Hagane] Error parsing stored routines from localStorage:', err);
    try {
      if (raw) {
        localStorage.setItem(ROUTINES_KEY + '_corrupt_bak', raw);
        storageCorruptionLocked = true;
      }
    } catch {
      // ignore
    }
    return DEFAULT_ROUTINES;
  }
}

export function saveRoutines(routines: Routine[]): boolean {
  if (storageCorruptionLocked) {
    console.warn(
      '[Hagane] Blocked saveRoutines while corrupt storage quarantine awaits user decision.'
    );
    return false;
  }
  try {
    localStorage.setItem(ROUTINES_KEY, JSON.stringify(routines));
    localStorage.setItem(LAST_SAVED_AT_KEY, String(Date.now()));
    return true;
  } catch (err) {
    console.error('[Hagane] Failed to save routines to localStorage:', err);
    return false;
  }
}

export function loadCustomExercises(): Exercise[] {
  let raw: string | null = null;
  try {
    raw = localStorage.getItem(CUSTOM_EXERCISES_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      throw new Error('Stored custom exercises payload is not an array');
    }
    return sanitizeCustomExercises(parsed);
  } catch (err) {
    console.error('[Hagane] Error parsing custom exercises from localStorage:', err);
    try {
      if (raw) {
        localStorage.setItem(CUSTOM_EXERCISES_KEY + '_corrupt_bak', raw);
        customCorruptionLocked = true;
      }
    } catch {
      // ignore
    }
    return [];
  }
}

export function saveCustomExercises(custom: Exercise[]): boolean {
  if (customCorruptionLocked) {
    console.warn(
      '[Hagane] Blocked saveCustomExercises while corrupt custom exercises quarantine awaits decision.'
    );
    return false;
  }
  try {
    localStorage.setItem(CUSTOM_EXERCISES_KEY, JSON.stringify(custom));
    return true;
  } catch (err) {
    console.error('[Hagane] Failed to save custom exercises to localStorage:', err);
    return false;
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

  // Explicit isolation check (always 90s standard rest, never 150s)
  const isIsolation =
    n.includes('curl') ||
    n.includes('wrist') ||
    n.includes('extension') ||
    n.includes('raise') ||
    n.includes('shrug') ||
    n.includes('fly') ||
    n.includes('flye') ||
    n.includes('scarecrow') ||
    n.includes('face pull') ||
    n.includes('cuộn') ||
    n.includes('cổ tay') ||
    n.includes('banh ngực') ||
    n.includes('đá đùi');

  if (isIsolation) return 90;

  // True compound exercises (heavy multi-joint movements)
  const isCompound =
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
    /(?:^|\s)row(?:s|\b)/.test(n) ||
    /(?:^|\s)dip(?:s|\b)/.test(n) ||
    n.includes('gánh tạ') ||
    n.includes('kéo tạ') ||
    n.includes('đẩy ngực') ||
    n.includes('đẩy vai') ||
    n.includes('kéo xô') ||
    n.includes('hít xà') ||
    n.includes('xà kép') ||
    n.includes('đạp đùi') ||
    (eq === 'barbell' && (n.includes('press') || n.includes('clean') || n.includes('snatch')));

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
