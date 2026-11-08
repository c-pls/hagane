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
function detectPattern(name: string): MovementPattern | null {
  const n = name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');

  if (n.includes('lateral raise') || n.includes('dang vai') || n.includes('bay vai'))
    return { id: 'lat_raise', en: 'Lateral Raise', vi: 'Dang tạ ngang vai' };
  if (
    n.includes('rear delt') ||
    n.includes('reverse fly') ||
    n.includes('face pull') ||
    n.includes('vai sau')
  )
    return { id: 'rear_delt', en: 'Rear Delt Fly', vi: 'Bay vai sau' };
  if (n.includes('front raise') || n.includes('nang vai truoc'))
    return { id: 'front_raise', en: 'Front Raise', vi: 'Nâng vai trước' };
  if (n.includes('calf raise') || n.includes('nhon bap') || n.includes('bap chuoi'))
    return { id: 'calf_raise', en: 'Calf Raise', vi: 'Nhón bắp chuối' };
  if (
    (n.includes('incline') && (n.includes('press') || n.includes('bench'))) ||
    n.includes('nguc tren')
  )
    return {
      id: 'incline_press',
      en: 'Incline Chest Press',
      vi: 'Đẩy ngực trên',
    };
  if (
    (n.includes('decline') && (n.includes('press') || n.includes('bench'))) ||
    n.includes('nguc duoi')
  )
    return {
      id: 'decline_press',
      en: 'Decline Chest Press',
      vi: 'Đẩy ngực dưới',
    };
  if (
    (n.includes('press') &&
      (n.includes('bench') ||
        n.includes('chest') ||
        n.includes('push up') ||
        n.includes('pushup'))) ||
    n.includes('day nguc') ||
    n.includes('chong day')
  )
    return { id: 'chest_press', en: 'Chest Press', vi: 'Đẩy ngực ngang' };
  if (
    n.includes('overhead press') ||
    n.includes('shoulder press') ||
    n.includes('military press') ||
    n.includes('arnold press') ||
    n.includes('day vai')
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
    n.includes('crossover') ||
    n.includes('ep nguc')
  )
    return { id: 'chest_fly', en: 'Chest Fly', vi: 'Ép ngực' };
  if (
    n.includes('pulldown') ||
    n.includes('pull-up') ||
    n.includes('pull up') ||
    n.includes('chin-up') ||
    n.includes('chin up') ||
    n.includes('keo xo') ||
    n.includes('hit xa')
  )
    return { id: 'pulldown', en: 'Vertical Pull', vi: 'Kéo xô dọc' };
  if (
    (n.includes('row') && !n.includes('upright')) ||
    n.includes('cheo thuyen') ||
    n.includes('keo ngang')
  )
    return { id: 'row', en: 'Row', vi: 'Chèo lưng xô' };
  if (n.includes('upright row') || n.includes('cheo thang dung'))
    return { id: 'upright_row', en: 'Upright Row', vi: 'Kéo tạ thẳng đứng' };
  if (n.includes('shrug') || n.includes('nhun cau vai') || n.includes('cau vai'))
    return { id: 'shrug', en: 'Shrug', vi: 'Nhún cầu vai' };
  if (
    n.includes('hyperextension') ||
    n.includes('hyper extension') ||
    n.includes('back extension') ||
    n.includes('gap lung')
  )
    return {
      id: 'back_ext',
      en: 'Back Extension / Hyperextension',
      vi: 'Gập lưng / Hyperextension',
    };
  if (
    n.includes('glute kickback') ||
    (n.includes('kickback') &&
      (n.includes('glute') || n.includes('hip') || n.includes('mong')))
  )
    return {
      id: 'glute_kickback',
      en: 'Glute Kickback',
      vi: 'Đá đùi sau / Mông',
    };
  if (
    n.includes('squat') ||
    n.includes('leg press') ||
    n.includes('hack squat') ||
    n.includes('ganh dui') ||
    n.includes('ngoi xo')
  )
    return {
      id: 'squat',
      en: 'Squat / Leg Press',
      vi: 'Đạp đùi & Squat',
    };
  if (n.includes('leg extension') || n.includes('da dui'))
    return { id: 'leg_ext', en: 'Leg Extension', vi: 'Đá đùi trước' };
  if (n.includes('leg curl') || n.includes('cuon chan') || n.includes('dui sau'))
    return { id: 'leg_curl', en: 'Leg Curl', vi: 'Cuốn đùi sau' };
  if (
    n.includes('deadlift') ||
    n.includes('rdl') ||
    n.includes('good morning') ||
    n.includes('keo ta')
  )
    return {
      id: 'hinge',
      en: 'Hip Hinge & Deadlift',
      vi: 'Gập hông & Deadlift',
    };
  if (n.includes('curl') || n.includes('cuon tay'))
    return { id: 'curl', en: 'Arm Curl', vi: 'Cuốn tay trước' };
  if (
    n.includes('pushdown') ||
    (n.includes('kickback') &&
      !n.includes('glute') &&
      !n.includes('hip') &&
      !n.includes('mong')) ||
    n.includes('skull crusher') ||
    n.includes('skullcrusher') ||
    (n.includes('extension') &&
      !n.includes('back') &&
      !n.includes('leg') &&
      !n.includes('hyper')) ||
    n.includes('tay sau')
  )
    return {
      id: 'tricep_ext',
      en: 'Triceps Extension',
      vi: 'Duỗi tay sau',
    };
  return null;
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

  const targetFullName = `${target.name} ${target.nameVi || ''}`;
  const pattern = detectPattern(targetFullName);
  const targetPrimary = new Set(
    target.primaryMuscles.map((m) => m.toLowerCase())
  );
  const targetCategory = (target.category || '').toLowerCase();
  const targetEquip = (target.equipment || '').toLowerCase();

  const scored: ExerciseAlternative[] = all
    .filter((e) => e.id !== target.id)
    .map((e) => {
      let score = 0;
      const eFullName = `${e.name} ${e.nameVi || ''}`;
      const ePattern = detectPattern(eFullName);
      const ePrimary = e.primaryMuscles.map((m) => m.toLowerCase());
      const eCategory = (e.category || '').toLowerCase();
      const eEquip = (e.equipment || '').toLowerCase();

      // 1. Functional pattern match
      const hasPatternMatch =
        pattern && ePattern && pattern.id === ePattern.id;
      if (hasPatternMatch) {
        score += 70;
      }

      // 2. Primary muscle match
      let primaryMatches = 0;
      for (const m of ePrimary) {
        if (targetPrimary.has(m)) {
          score += 40;
          primaryMatches++;
        }
      }

      // 3. Category match
      if (targetCategory && eCategory === targetCategory) {
        score += 25;
      }

      // 4. Word overlap in names (supporting both English and Vietnamese diacritics)
      const extractTokens = (str: string) => {
        return str
          .toLowerCase()
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .replace(/đ/g, 'd')
          .replace(/[^a-z0-9\s]/g, ' ')
          .split(/\s+/)
          .filter((w) => w.length > 2);
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

      if (hasPatternMatch) {
        reasonEn = isSameEquip
          ? `Same movement (${pattern.en})`
          : `${e.equipment} alternative`;
        reasonVi = isSameEquip
          ? `Cùng chuyển động (${pattern.vi})`
          : `Thay thế bằng ${translateEquipment(e.equipment, 'vi')}`;
      } else if (primaryMatches > 0) {
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

  const balanced: ExerciseAlternative[] = [];
  let i = 0;
  let j = 0;
  while (
    balanced.length < limit &&
    (i < sameEquip.length || j < diffEquip.length)
  ) {
    if (
      i < sameEquip.length &&
      (balanced.length % 2 === 0 || j >= diffEquip.length)
    ) {
      balanced.push(sameEquip[i++]);
    } else if (j < diffEquip.length) {
      balanced.push(diffEquip[j++]);
    } else if (i < sameEquip.length) {
      balanced.push(sameEquip[i++]);
    }
  }

  return balanced;
}
