import React, { useMemo, useState } from 'react';
import { Exercise, Language } from '../types/gym';
import {
  translateEquipment,
  translateMuscle,
  UI_TEXT,
} from '../i18n/translations';

interface ExercisePickerModalProps {
  isOpen: boolean;
  lang: Language;
  exercises: Exercise[];
  onClose: () => void;
  onSelectExercise: (exerciseId: string) => void;
}

const MUSCLE_FILTERS = [
  'All',
  'Quads',
  'Glutes',
  'Hamstrings',
  'Chest',
  'Back',
  'Shoulders',
  'Biceps',
  'Triceps',
  'Forearms',
  'Core',
  'Calves',
];

export const ExercisePickerModal: React.FC<ExercisePickerModalProps> = ({
  isOpen,
  lang,
  exercises,
  onClose,
  onSelectExercise,
}) => {
  const t = UI_TEXT[lang];
  const [search, setSearch] = useState('');
  const [muscleFilter, setMuscleFilter] = useState('All');

  const filtered = useMemo(() => {
    const normalize = (s: string) =>
      s.toLowerCase().replace(/[-_/(),.]+/g, ' ').replace(/\s+/g, ' ').trim();
    const tokens = normalize(search).split(' ').filter(Boolean);

    return exercises.filter((ex) => {
      const searchableBlob = normalize(
        [
          ex.name,
          ex.nameVi || '',
          ex.equipment,
          ex.category,
          ...ex.primaryMuscles,
          ...ex.secondaryMuscles,
          ...ex.aliases,
        ].join(' ')
      );
      const matchSearch =
        tokens.length === 0 ||
        tokens.every((tok) => searchableBlob.includes(tok));

      const matchMuscle =
        muscleFilter === 'All' ||
        ex.category === muscleFilter ||
        ex.primaryMuscles.some((m) =>
          m.toLowerCase().includes(muscleFilter.toLowerCase())
        );

      return matchSearch && matchMuscle;
    });
  }, [exercises, search, muscleFilter]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-white text-slate-900 rounded-[28px] max-w-lg w-full p-5 shadow-2xl space-y-4 max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="font-bold text-base text-slate-900">
              {t.addExerciseModalTitle}
            </h3>
            <p className="text-xs text-slate-400">
              {filtered.length} {t.exercisesAvailable}
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-sm flex items-center justify-center cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* Search Input */}
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t.searchExercisePlaceholder}
          className="w-full rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        {/* Muscle Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {MUSCLE_FILTERS.map((m) => (
            <button
              key={m}
              onClick={() => setMuscleFilter(m)}
              className={`px-3 py-1 rounded-full text-xs font-semibold shrink-0 transition cursor-pointer ${
                muscleFilter === m
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {translateMuscle(m, lang)}
            </button>
          ))}
        </div>

        {/* Exercise List */}
        <div className="space-y-2 overflow-y-auto pr-1 flex-1">
          {filtered.map((ex) => (
            <div
              key={ex.id}
              className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 hover:bg-slate-100/80 transition gap-3"
            >
              <div className="min-w-0">
                <div className="font-bold text-sm text-slate-900 truncate">
                  {lang === 'vi' && ex.nameVi ? ex.nameVi : ex.name}
                </div>
                <div className="text-xs text-slate-500 mt-0.5">
                  <span className="text-red-600 font-semibold">
                    {ex.primaryMuscles
                      .map((m) => translateMuscle(m, lang))
                      .join(', ')}
                  </span>{' '}
                  • {translateEquipment(ex.equipment, lang)}
                </div>
              </div>
              <button
                onClick={() => onSelectExercise(ex.id)}
                className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shrink-0 cursor-pointer transition"
              >
                {t.addBtn}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
