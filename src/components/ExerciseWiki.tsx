import React, { useMemo } from 'react';
import { Exercise, Language } from '../types/gym';
import {
  translateEquipment,
  translateMuscle,
  UI_TEXT,
} from '../i18n/translations';
import { searchAndRankExercises } from '../utils/search';

import {
  EQUIPMENT_CHOICES,
  MUSCLE_FILTER_CHOICES,
} from '../data/exerciseConstants';

interface ExerciseWikiProps {
  exercises: Exercise[];
  lang: Language;
  onSelectExercise: (exerciseId: string) => void;
  search: string;
  onSearchChange: (search: string) => void;
  muscleFilter: string;
  onMuscleFilterChange: (muscle: string) => void;
  equipmentFilter: string;
  onEquipmentFilterChange: (eq: string) => void;
}

const MUSCLE_CATEGORIES = [
  'All',
  ...MUSCLE_FILTER_CHOICES,
];

const EQUIPMENT_CATEGORIES = ['All', ...EQUIPMENT_CHOICES];

export const ExerciseWiki: React.FC<ExerciseWikiProps> = ({
  exercises,
  lang,
  onSelectExercise,
  search,
  onSearchChange,
  muscleFilter,
  onMuscleFilterChange,
  equipmentFilter,
  onEquipmentFilterChange,
}) => {
  const t = UI_TEXT[lang];

  const filtered = useMemo(() => {
    return searchAndRankExercises(
      exercises,
      search,
      muscleFilter,
      equipmentFilter,
      lang
    );
  }, [exercises, search, muscleFilter, equipmentFilter, lang]);

  return (
    <div className="space-y-4">
      {/* Search & Filter Card (Clean — no redundant header banner) */}
      <div className="bg-white rounded-[24px] p-4 shadow-xs space-y-3">
        {/* Search Input with 1-click Clear Button & No Cache */}
        <div className="relative">
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            onFocus={(e) => e.target.select()}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck={false}
            name="wiki-search-clean"
            aria-label={t.searchExercisePlaceholder}
            placeholder={t.searchExercisePlaceholder}
            className="w-full rounded-2xl bg-slate-100 pl-4 pr-10 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {search ? (
            <button
              type="button"
              onClick={() => {
                onSearchChange('');
              }}
              className="absolute right-1 top-1/2 -translate-y-1/2 w-11 h-11 min-w-[44px] min-h-[44px] rounded-full text-slate-500 hover:text-slate-700 hover:bg-slate-200/80 font-bold text-xs flex items-center justify-center cursor-pointer transition"
              title={lang === 'vi' ? 'Xóa tìm kiếm' : 'Clear search'}
              aria-label={lang === 'vi' ? 'Xóa tìm kiếm' : 'Clear search'}
            >
              ✕
            </button>
          ) : null}
        </div>

        {/* Active search or filter reset bar */}
        {(search || muscleFilter !== 'All' || equipmentFilter !== 'All') && (
          <div className="flex items-center justify-between px-1 pt-0.5">
            <span className="text-xs text-blue-600 font-medium truncate">
              {search && <span>"{search}" </span>}
              {muscleFilter !== 'All' && (
                <span>• {translateMuscle(muscleFilter, lang)} </span>
              )}
              {equipmentFilter !== 'All' && (
                <span>• {translateEquipment(equipmentFilter, lang)} </span>
              )}
            </span>
            <button
              type="button"
              onClick={() => {
                onSearchChange('');
                onMuscleFilterChange('All');
                onEquipmentFilterChange('All');
              }}
              className="text-xs font-semibold text-slate-500 hover:text-red-600 transition cursor-pointer underline shrink-0 ml-2 min-h-[44px] inline-flex items-center"
            >
              {lang === 'vi' ? 'Đặt lại bộ lọc' : 'Clear all'}
            </button>
          </div>
        )}

        {/* Muscle Filter Pills */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {MUSCLE_CATEGORIES.map((m) => (
              <button
                key={m}
                onClick={() => onMuscleFilterChange(m)}
                className={`px-3.5 py-1.5 min-h-[44px] flex items-center justify-center rounded-full text-xs font-semibold shrink-0 transition cursor-pointer ${
                  muscleFilter === m
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {translateMuscle(m, lang)}
              </button>
            ))}
          </div>

          {/* Equipment Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {EQUIPMENT_CATEGORIES.map((eq) => (
              <button
                key={eq}
                onClick={() => onEquipmentFilterChange(eq)}
                className={`px-3 py-1 min-h-[44px] flex items-center justify-center rounded-full text-xs font-medium shrink-0 transition cursor-pointer ${
                  equipmentFilter === eq
                    ? 'bg-slate-800 text-white shadow-xs'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-200 border border-slate-200/70'
                }`}
              >
                {translateEquipment(eq, lang)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Exercise Cards Grid (Clean Wiki — no routine comment pins) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filtered.map((ex) => {
          const displayName =
            lang === 'vi' && ex.nameVi ? ex.nameVi : ex.name;
          return (
            <div
              key={ex.id}
              role="button"
              tabIndex={0}
              onClick={() => onSelectExercise(ex.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelectExercise(ex.id);
                }
              }}
              className="bg-white rounded-[22px] p-4 shadow-xs hover:shadow-md cursor-pointer transition flex items-center justify-between gap-3"
            >
              <div className="min-w-0 space-y-1">
                <div>
                  <h3 className="font-bold text-sm text-slate-900 truncate">
                    {displayName}
                  </h3>
                </div>
                <p className="text-xs text-slate-400">
                  {t.primaryLabel}:{' '}
                  <span className="text-slate-700 font-semibold">
                    {ex.primaryMuscles
                      .map((m) => translateMuscle(m, lang))
                      .join(', ')}
                  </span>
                </p>
              </div>

              <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-700 font-serif italic font-bold text-sm flex items-center justify-center shrink-0">
                i
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="col-span-full p-8 text-center space-y-3 bg-white rounded-[24px]">
            <p className="text-sm font-semibold text-slate-700">
              {lang === 'vi'
                ? 'Không tìm thấy bài tập nào phù hợp'
                : 'No exercises found matching your search'}
            </p>
            <button
              type="button"
              onClick={() => {
                onSearchChange('');
                onMuscleFilterChange('All');
                onEquipmentFilterChange('All');
              }}
              className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition cursor-pointer"
            >
              {lang === 'vi' ? 'Đặt lại bộ lọc' : 'Clear search & filters'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
