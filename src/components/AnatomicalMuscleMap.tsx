import React from 'react';
import {
  AnatomyBodyPart,
  BODY_BACK,
  BODY_FRONT,
  MALE_OUTLINE_BACK,
  MALE_OUTLINE_FRONT,
} from '../data/anatomyPaths';
import { Exercise, Language } from '../types/gym';
import { translateMuscle, UI_TEXT } from '../i18n/translations';

interface AnatomicalMuscleMapProps {
  exercise: Exercise;
  lang: Language;
}

const BLACK_EXTREMITIES = new Set([
  'head',
  'hair',
  'hands',
  'feet',
  'knees',
]);

export const AnatomicalMuscleMap: React.FC<AnatomicalMuscleMapProps> = ({
  exercise,
  lang,
}) => {
  const t = UI_TEXT[lang];
  const primarySet = new Set(exercise.primarySlugs || []);
  const secondarySet = new Set(exercise.secondarySlugs || []);

  const getFillColor = (slug: string): string => {
    if (BLACK_EXTREMITIES.has(slug)) return '#000000';
    if (primarySet.has(slug)) return '#eb4d3d';
    if (secondarySet.has(slug)) return '#ff786e';
    return '#8c8c8c';
  };

  const renderBodySide = (
    parts: AnatomyBodyPart[],
    outlineD: string,
    viewBox: string,
    label: string
  ) => (
    <svg
      viewBox={viewBox}
      aria-label={label}
      className="w-full h-auto max-h-[340px] select-none"
    >
      <path
        d={outlineD}
        fill="#000000"
        stroke="#000000"
        strokeWidth={10}
        strokeLinejoin="round"
      />
      {parts.map((part) => {
        const fill = getFillColor(part.slug);
        const allPaths = [
          ...(part.path.common || []),
          ...(part.path.left || []),
          ...(part.path.right || []),
        ];
        return (
          <g key={`${label}-${part.slug}`}>
            {allPaths.map((d, idx) => (
              <path key={idx} d={d} fill={fill} />
            ))}
          </g>
        );
      })}
    </svg>
  );

  return (
    <div className="space-y-3">
      {/* Front & Back Anatomical Figures Card */}
      <div className="bg-white rounded-[24px] p-5 shadow-xs">
        <div className="grid grid-cols-2 gap-2 items-center justify-items-center">
          {renderBodySide(
            BODY_FRONT,
            MALE_OUTLINE_FRONT,
            '0 50 724 1350',
            'Front muscle diagram'
          )}
          {renderBodySide(
            BODY_BACK,
            MALE_OUTLINE_BACK,
            '724 50 724 1350',
            'Back muscle diagram'
          )}
        </div>
      </div>

      {/* Section Title */}
      <h3 className="text-lg font-bold text-slate-900 px-1 pt-1">
        {t.musclesWorkedTitle}
      </h3>

      {/* Two-Column Primary & Secondary Breakdown Card */}
      <div className="bg-white rounded-[24px] p-5 shadow-xs grid grid-cols-2 gap-6">
        <div>
          <span className="text-sm font-medium text-slate-400 block mb-2">
            {t.primaryLabel}
          </span>
          <ul className="space-y-1.5 text-base font-medium text-slate-800">
            {exercise.primaryMuscles.map((muscle) => (
              <li key={muscle}>{translateMuscle(muscle, lang)}</li>
            ))}
          </ul>
        </div>

        <div>
          <span className="text-sm font-medium text-slate-400 block mb-2">
            {t.secondaryLabel}
          </span>
          <ul className="space-y-1.5 text-base font-medium text-slate-800">
            {exercise.secondaryMuscles.length > 0 ? (
              exercise.secondaryMuscles.map((muscle) => (
                <li key={muscle}>{translateMuscle(muscle, lang)}</li>
              ))
            ) : (
              <li className="text-slate-400">—</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};
