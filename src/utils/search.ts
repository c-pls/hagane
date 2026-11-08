import { Exercise, Language } from '../types/gym';

export function normalizeSearchString(s: string): string {
  return s
    .toLowerCase()
    .replace(/đ/g, 'd')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // remove Vietnamese diacritics for flexible search
    .replace(/[-_/(),.]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

const searchBlobCache = new WeakMap<
  Exercise,
  { blob: string; rawBlob: string }
>();

function getExerciseSearchBlobs(ex: Exercise): {
  blob: string;
  rawBlob: string;
} {
  let cached = searchBlobCache.get(ex);
  if (!cached) {
    const rawBlob = [
      ex.name,
      ex.nameVi || '',
      ex.equipment,
      ex.category,
      ...ex.primaryMuscles,
      ...ex.secondaryMuscles,
      ...ex.aliases,
    ]
      .join(' ')
      .toLowerCase();

    cached = {
      rawBlob,
      blob: normalizeSearchString(rawBlob),
    };
    searchBlobCache.set(ex, cached);
  }
  return cached;
}

export function searchAndRankExercises(
  exercises: Exercise[],
  query: string,
  muscleFilter: string = 'All',
  equipmentFilter: string = 'All',
  lang: Language = 'en'
): Exercise[] {
  const normalizedQuery = normalizeSearchString(query);
  const tokens = normalizedQuery.split(' ').filter(Boolean);

  // 1. Filter
  const matches = exercises.filter((ex) => {
    // Muscle filter
    if (muscleFilter !== 'All') {
      const filterLower = muscleFilter.toLowerCase();
      const matchCat = ex.category.toLowerCase() === filterLower;
      const matchMuscle = ex.primaryMuscles.some((m) => {
        const mLower = m.toLowerCase();
        if (filterLower === 'back') {
          return (
            mLower === 'back' ||
            mLower === 'upper back' ||
            mLower === 'lower back' ||
            mLower === 'lats' ||
            mLower === 'traps'
          );
        }
        if (filterLower === 'shoulders') {
          return (
            mLower === 'shoulders' ||
            mLower === 'delts' ||
            mLower === 'front delts' ||
            mLower === 'rear delts'
          );
        }
        if (filterLower === 'core') {
          return (
            mLower === 'core' ||
            mLower === 'abs' ||
            mLower === 'obliques' ||
            mLower === 'hip flexors'
          );
        }
        return mLower === filterLower;
      });

      // Specific muscle pills match exercises working that muscle as primary or secondary.
      // Group umbrella pills ('shoulders', 'back', 'core') avoid broad multi-muscle secondary
      // expansion to prevent pulling in unrelated compound movements (e.g. chest presses into shoulders).
      const matchSecondary =
        filterLower !== 'shoulders' &&
        filterLower !== 'back' &&
        filterLower !== 'core' &&
        ex.secondaryMuscles.some((m) => m.toLowerCase() === filterLower);

      if (!matchCat && !matchMuscle && !matchSecondary) return false;
    }

    // Equipment filter
    if (equipmentFilter !== 'All') {
      if (ex.equipment.toLowerCase() !== equipmentFilter.toLowerCase()) {
        return false;
      }
    }

    if (tokens.length === 0) return true;

    // Searchable text blobs (cached per exercise to prevent reallocations)
    const { blob, rawBlob } = getExerciseSearchBlobs(ex);

    return (
      tokens.every((tok) => blob.includes(tok)) ||
      tokens.every((tok) => rawBlob.includes(tok))
    );
  });

  if (tokens.length === 0) {
    return matches;
  }

  // 2. Score and Rank
  const scored = matches.map((ex) => {
    const nameNorm = normalizeSearchString(ex.name);
    const nameViNorm = normalizeSearchString(ex.nameVi || '');
    const activeNameNorm = lang === 'vi' && nameViNorm ? nameViNorm : nameNorm;

    let score = 0;

    // Exact full name match
    if (nameNorm === normalizedQuery || nameViNorm === normalizedQuery) {
      score += 10000;
    }

    // Name starts with the query
    if (
      nameNorm.startsWith(normalizedQuery) ||
      nameViNorm.startsWith(normalizedQuery)
    ) {
      score += 6000;
    }

    // Name contains the full query string as a substring
    if (
      nameNorm.includes(normalizedQuery) ||
      nameViNorm.includes(normalizedQuery)
    ) {
      score += 3500;
    }

    // Every token appears in the name
    const allTokensInEnName = tokens.every((tok) => nameNorm.includes(tok));
    const allTokensInViName = tokens.every((tok) => nameViNorm.includes(tok));
    if (allTokensInEnName || allTokensInViName) {
      score += 2000;
    }

    // Individual token positions in name (earlier words get bonus)
    tokens.forEach((tok) => {
      if (nameNorm.includes(tok) || nameViNorm.includes(tok)) {
        score += 500;
        const words = activeNameNorm.split(' ');
        if (words[0] === tok) score += 300;
      }
    });

    // Primary muscles or category match
    const categoryNorm = normalizeSearchString(ex.category);
    const primaryMusclesNorm = ex.primaryMuscles.map(normalizeSearchString);
    tokens.forEach((tok) => {
      if (
        categoryNorm.includes(tok) ||
        primaryMusclesNorm.some((m) => m.includes(tok))
      ) {
        score += 300;
      }
    });

    // Equipment match
    const eqNorm = normalizeSearchString(ex.equipment);
    tokens.forEach((tok) => {
      if (eqNorm.includes(tok)) {
        score += 150;
      }
    });

    // Alias matches
    const aliasesNorm = ex.aliases.map(normalizeSearchString);
    tokens.forEach((tok) => {
      if (aliasesNorm.some((a) => a.includes(tok))) {
        score += 50;
      }
    });

    return { ex, score };
  });

  // Sort descending by score
  scored.sort((a, b) => b.score - a.score);

  return scored.map((item) => item.ex);
}
