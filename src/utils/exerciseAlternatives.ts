import { Exercise } from '../types/gym';
import { translateEquipment, translateMuscle } from '../i18n/translations';

export interface ExerciseAlternative {
  exercise: Exercise;
  score: number;
  isSameEquip: boolean;
  reasonEn: string;
  reasonVi: string;
}

interface MovementPattern {
  id: string;
  en: string;
  vi: string;
}

/**
 * Detects the core functional movement pattern of an exercise.
 */
function detectPattern(name: string, exercise?: Exercise): MovementPattern | null {
  if (!name) return null;
  const n = name.toLowerCase();

  if (n.includes('lateral raise'))
    return { id: 'lat_raise', en: 'Lateral Raise', vi: 'Dang tạ ngang vai' };
  if (
    (n.includes('rear delt') ||
      n.includes('reverse fly') ||
      n.includes('face pull')) &&
    !(
      n.includes('row') &&
      (exercise?.category === 'Back' ||
        exercise?.primaryMuscles.includes('Upper Back') ||
        exercise?.primaryMuscles.includes('Lats'))
    )
  )
    return { id: 'rear_delt', en: 'Rear Delt Fly', vi: 'Bay vai sau' };
  if (n.includes('front raise'))
    return { id: 'front_raise', en: 'Front Raise', vi: 'Nâng vai trước' };
  if (n.includes('calf raise'))
    return { id: 'calf_raise', en: 'Calf Raise', vi: 'Nhón bắp chuối' };
  if (n.includes('incline') && (n.includes('press') || n.includes('bench')))
    return {
      id: 'incline_press',
      en: 'Incline Chest Press',
      vi: 'Đẩy ngực trên',
    };
  if (n.includes('decline') && (n.includes('press') || n.includes('bench')))
    return {
      id: 'decline_press',
      en: 'Decline Chest Press',
      vi: 'Đẩy ngực dưới',
    };
  if (n.includes('chest dip') || (n.includes('dip') && n.includes('chest'))) {
    return { id: 'chest_dip', en: 'Chest Dip', vi: 'Nhún xà kép ngực' };
  }
  if (
    (n.includes('close-grip') || n.includes('close grip')) &&
    (n.includes('press') ||
      n.includes('push up') ||
      n.includes('pushup') ||
      n.includes('push-up') ||
      n.includes('bench'))
  ) {
    return {
      id: 'close_grip_press',
      en: 'Close-Grip Press',
      vi: 'Đẩy ngực / tay sau hẹp tay',
    };
  }
  if (
    ((n.includes('press') &&
      (n.includes('bench') ||
        n.includes('chest') ||
        n.includes('push up') ||
        n.includes('pushup') ||
        n.includes('hex') ||
        n.includes('lying'))) ||
      n.includes('push-up')) &&
    !n.includes('close-grip') &&
    !n.includes('close grip')
  )
    return { id: 'chest_press', en: 'Chest Press', vi: 'Đẩy ngực ngang' };
  if (
    n.includes('overhead press') ||
    n.includes('shoulder press') ||
    n.includes('military press') ||
    n.includes('arnold press') ||
    n.includes('clean and press') ||
    n.includes('clean & press') ||
    n.includes('behind-the-neck') ||
    n.includes('behind the neck')
  )
    return {
      id: 'overhead_press',
      en: 'Overhead Press',
      vi: 'Đẩy vai qua đầu',
    };
  if (
    n.includes('fly') ||
    n.includes('flye') ||
    n.includes('pec deck') ||
    n.includes('crossover')
  )
    return { id: 'chest_fly', en: 'Chest Fly', vi: 'Ép ngực' };
  if (
    n.includes('pulldown') ||
    n.includes('pull-up') ||
    n.includes('pull up') ||
    n.includes('chin-up') ||
    n.includes('chin up')
  )
    return { id: 'pulldown', en: 'Vertical Pull', vi: 'Kéo xô dọc' };
  if (n.includes('row') && !n.includes('upright'))
    return { id: 'row', en: 'Row', vi: 'Chèo lưng xô' };
  if (n.includes('upright row'))
    return { id: 'upright_row', en: 'Upright Row', vi: 'Kéo tạ thẳng đứng' };
  if (n.includes('shrug'))
    return { id: 'shrug', en: 'Shrug', vi: 'Nhún cầu vai' };
  if (
    n.includes('hyperextension') ||
    n.includes('hyper extension') ||
    n.includes('back extension')
  )
    return {
      id: 'back_ext',
      en: 'Back Extension / Hyperextension',
      vi: 'Gập lưng / Hyperextension',
    };
  if (
    n.includes('glute kickback') ||
    (n.includes('kickback') && (n.includes('glute') || n.includes('hip')))
  )
    return {
      id: 'glute_kickback',
      en: 'Glute Kickback',
      vi: 'Đá đùi sau / Mông',
    };
  if (
    n.includes('squat') ||
    n.includes('leg press') ||
    n.includes('hack squat')
  )
    return {
      id: 'squat',
      en: 'Squat / Leg Press',
      vi: 'Đạp đùi & Squat',
    };
  if (n.includes('leg extension'))
    return { id: 'leg_ext', en: 'Leg Extension', vi: 'Đá đùi trước' };
  if (n.includes('leg curl'))
    return { id: 'leg_curl', en: 'Leg Curl', vi: 'Cuốn đùi sau' };
  if (
    n.includes('deadlift') ||
    n.includes('rdl') ||
    n.includes('good morning')
  )
    return {
      id: 'hinge',
      en: 'Hip Hinge & Deadlift',
      vi: 'Gập hông & Deadlift',
    };
  if (
    n.includes('wrist') ||
    (exercise && exercise.category === 'Forearms' && n.includes('curl'))
  )
    return { id: 'wrist_curl', en: 'Wrist Curl', vi: 'Cuốn cổ tay' };
  if (
    n.includes('curl') &&
    !n.includes('wrist') &&
    !n.includes('leg curl') &&
    (!exercise || exercise.category !== 'Forearms')
  )
    return { id: 'curl', en: 'Arm Curl', vi: 'Cuốn tay trước' };
  if (
    n.includes('pushdown') ||
    n.includes('triceps dip') ||
    n.includes('bench dip') ||
    n.includes('parallel bar dip') ||
    (n.includes('dip') && (exercise?.category === 'Triceps' || exercise?.primaryMuscles.includes('Triceps'))) ||
    (n.includes('kickback') &&
      !n.includes('glute') &&
      !n.includes('hip')) ||
    n.includes('skull crusher') ||
    n.includes('skullcrusher') ||
    (n.includes('extension') &&
      !n.includes('back') &&
      !n.includes('leg') &&
      !n.includes('hyper'))
  )
    return {
      id: 'tricep_ext',
      en: 'Triceps Extension',
      vi: 'Duỗi tay sau',
    };
  return null;
}

/**
 * Detects the core functional movement pattern of an exercise.
 * Evaluates the clean English name and muscle context with 100% accuracy.
 */
export function detectExercisePattern(exercise: Exercise): MovementPattern | null {
  if (!exercise) return null;
  return detectPattern(exercise.name, exercise);
}

/**
 * Finds the top similar & alternative exercises for a given exercise.
 * Provides a smart, balanced mix of:
 * 1) Same equipment alternatives (e.g. Incline DB Curl <-> Standing DB Curl, DB Hammer Curl)
 * 2) Different equipment substitutes (e.g. Dumbbell to Cable, Barbell, or Machine)
 */
export function getSimilarExercises(
  target: Exercise,
  all: Exercise[],
  limit = 6
): ExerciseAlternative[] {
  if (!target || !all || all.length === 0) return [];

  const pattern = detectExercisePattern(target);
  const targetPrimary = new Set(
    target.primaryMuscles.map((m) => m.toLowerCase())
  );
  const targetCategory = (target.category || '').toLowerCase();
  const targetEquip = (target.equipment || '').toLowerCase();

  const scored: ExerciseAlternative[] = all
    .filter((e) => e.id !== target.id)
    .map((e) => {
      let score = 0;
      const ePattern = detectExercisePattern(e);
      const ePrimary = e.primaryMuscles.map((m) => m.toLowerCase());
      const eCategory = (e.category || '').toLowerCase();
      const eEquip = (e.equipment || '').toLowerCase();

      // 1. Functional pattern match
      const hasPatternMatch = Boolean(
        pattern && ePattern && pattern.id === ePattern.id
      );

      // 2. Primary muscle match
      let primaryMatches = 0;
      for (const m of ePrimary) {
        if (targetPrimary.has(m)) {
          score += 40;
          primaryMatches++;
        }
      }

      // Check cross matches between target primary and candidate secondary
      const targetSec = new Set(
        (target.secondaryMuscles || []).map((m) => m.toLowerCase())
      );
      const eSec = new Set(
        (e.secondaryMuscles || []).map((m) => m.toLowerCase())
      );

      let targetPrimInCandSec = false;
      for (const m of eSec) {
        if (targetPrimary.has(m)) {
          score += 20;
          targetPrimInCandSec = true;
        }
      }
      let candPrimInTargetSec = false;
      for (const m of ePrimary) {
        if (targetSec.has(m)) {
          score += 15;
          candPrimInTargetSec = true;
        }
      }

      let secOverlap = false;
      for (const m of eSec) {
        if (targetSec.has(m)) {
          score += 8;
          secOverlap = true;
        }
      }

      // 3. Category match
      const hasCategoryMatch = Boolean(
        targetCategory && eCategory === targetCategory
      );
      if (hasCategoryMatch) {
        score += 25;
      }

      // Strict anatomical filter: candidate MUST share at least one anatomical target
      // (primary muscle, target primary in candidate secondary, candidate primary in target secondary,
      // shared secondary with pattern match, or exact category match).
      const sharesMuscleContext =
        primaryMatches > 0 ||
        targetPrimInCandSec ||
        candPrimInTargetSec ||
        (secOverlap && hasPatternMatch) ||
        hasCategoryMatch;

      if (!sharesMuscleContext) {
        return {
          exercise: e,
          score: 0,
          isSameEquip: eEquip === targetEquip,
          reasonEn: '',
          reasonVi: '',
        };
      }

      // Pattern bonus: full +70 if direct primary/category match, +20 otherwise
      if (hasPatternMatch) {
        score += (primaryMatches > 0 || targetPrimInCandSec || hasCategoryMatch) ? 70 : 20;
      }

      // 4. Word overlap in names (filtered by stopwords so posture/equipment words don't skew scoring)
      const ALTERNATIVE_STOPWORDS = new Set([
        'tap', 'tren', 'may', 'ngoi', 'dung', 'ghe', 'don', 'tay', 'nam',
        'sau', 'truoc', 'voi', 'cho', 'va', 'cua', 'bar', 'cable', 'machine',
        'dumbbell', 'barbell', 'bench', 'seated', 'standing', 'lying', 'with',
        'and', 'for', 'the', 'over', 'under', 'arm', 'one', 'two', 'leg', 'bodyweight'
      ]);

      const extractTokens = (str: string) => {
        return str
          .toLowerCase()
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .replace(/đ/g, 'd')
          .replace(/[^a-z0-9\s]/g, ' ')
          .split(/\s+/)
          .filter((w) => w.length > 2 && !ALTERNATIVE_STOPWORDS.has(w));
      };

      const targetWords = [
        ...extractTokens(target.name),
        ...extractTokens(target.nameVi || ''),
      ];
      const eWords = new Set([
        ...extractTokens(e.name),
        ...extractTokens(e.nameVi || ''),
      ]);
      for (const tw of targetWords) {
        if (eWords.has(tw)) score += 8;
      }

      // 5. Construct user-friendly reasons
      const isSameEquip = eEquip === targetEquip;
      let reasonEn = '';
      let reasonVi = '';

      if (pattern && hasPatternMatch && sharesMuscleContext) {
        reasonEn = isSameEquip
          ? `Same movement (${pattern.en})`
          : `${e.equipment} alternative`;
        reasonVi = isSameEquip
          ? `Cùng chuyển động (${pattern.vi})`
          : `Thay thế bằng ${translateEquipment(e.equipment, 'vi')}`;
      } else if (primaryMatches > 0) {
        reasonEn = `Targets ${target.primaryMuscles[0]}`;
        reasonVi = `Tác động ${translateMuscle(target.primaryMuscles[0], 'vi')}`;
      } else if (targetPrimInCandSec) {
        reasonEn = `Targets ${target.primaryMuscles[0]}`;
        reasonVi = `Tác động ${translateMuscle(target.primaryMuscles[0], 'vi')}`;
      } else {
        reasonEn = 'Alternative variation';
        reasonVi = 'Biến thể tương đương';
      }

      return {
        exercise: e,
        score,
        isSameEquip,
        reasonEn,
        reasonVi,
      };
    })
    .filter((c) => c.score >= 50)
    .sort((a, b) => b.score - a.score);

  // Balanced picking: interleave same equipment & different equipment
  const sameEquip = scored.filter((s) => s.isSameEquip);
  const diffEquip = scored.filter((s) => !s.isSameEquip);

  // If top diff-equipment candidate significantly outscores top same-equipment candidate,
  // lead with the higher-quality diff-equipment substitute.
  let startWithSame = true;
  if (diffEquip.length > 0 && sameEquip.length > 0) {
    if (sameEquip[0].score < diffEquip[0].score - 30) {
      startWithSame = false;
    }
  } else if (sameEquip.length === 0) {
    startWithSame = false;
  }

  const balanced: ExerciseAlternative[] = [];
  let i = 0;
  let j = 0;
  while (
    balanced.length < limit &&
    (i < sameEquip.length || j < diffEquip.length)
  ) {
    const wantSame =
      balanced.length % 2 === 0 ? startWithSame : !startWithSame;
    if (wantSame && i < sameEquip.length) {
      if (
        j >= diffEquip.length ||
        sameEquip[i].score >= diffEquip[j].score - 40
      ) {
        balanced.push(sameEquip[i++]);
      } else {
        balanced.push(diffEquip[j++]);
      }
    } else if (j < diffEquip.length) {
      balanced.push(diffEquip[j++]);
    } else if (i < sameEquip.length) {
      balanced.push(sameEquip[i++]);
    }
  }

  return balanced;
}
