import React, { useState } from 'react';
import { Exercise, Language, Routine } from '../types/gym';
import { translateRoutineText, UI_TEXT } from '../i18n/translations';

interface RoutineListProps {
  routines: Routine[];
  lang: Language;
  exercisesMap: Record<string, Exercise>;
  onOpenRoutine: (routineId: string) => void;
  onCreateRoutine: (name: string, tag: string) => void;
  onDeleteRoutine: (routineId: string) => void;
}

export const RoutineList: React.FC<RoutineListProps> = ({
  routines,
  lang,
  exercisesMap,
  onOpenRoutine,
  onCreateRoutine,
  onDeleteRoutine,
}) => {
  const t = UI_TEXT[lang];
  const [showNewModal, setShowNewModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [newTag, setNewTag] = useState('Custom Routine');

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = newName.trim() || `Workout #${routines.length + 1}`;
    onCreateRoutine(trimmed, newTag.trim() || 'Custom Routine');
    setNewName('');
    setShowNewModal(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-1">
        <div>
          <h2 className="font-bold text-lg text-slate-900">{t.myRoutines}</h2>
          <p className="text-xs text-slate-500">{t.selectOrCreateRoutine}</p>
        </div>

        <button
          onClick={() => setShowNewModal(true)}
          className="px-4 py-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition cursor-pointer"
        >
          {t.newRoutineBtn}
        </button>
      </div>

      {/* Create Routine Inline Card */}
      {showNewModal && (
        <form
          onSubmit={handleCreate}
          className="bg-white rounded-[24px] p-5 shadow-xs space-y-3 border border-blue-100"
        >
          <h3 className="font-bold text-sm text-slate-900">
            {t.createNewRoutineTitle}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder={t.routineNamePlaceholder}
              autoFocus
              className="rounded-xl bg-slate-100 px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder={t.routineTagPlaceholder}
              className="rounded-xl bg-slate-100 px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowNewModal(false)}
              className="px-4 py-2 rounded-xl bg-slate-100 text-slate-600 text-xs font-bold cursor-pointer"
            >
              {t.cancel}
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold cursor-pointer"
            >
              {t.createAndOpen}
            </button>
          </div>
        </form>
      )}

      {/* Routines Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {routines.map((routine) => (
          <div
            key={routine.id}
            onClick={() => onOpenRoutine(routine.id)}
            className="bg-white rounded-[24px] p-5 shadow-xs hover:shadow-md cursor-pointer transition space-y-3 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-xs font-semibold text-blue-600">
                    {translateRoutineText(routine.tag, lang)}
                  </span>
                  <h3 className="font-bold text-base text-slate-900 mt-0.5">
                    {translateRoutineText(routine.name, lang)}
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    const routineName = translateRoutineText(routine.name, lang);
                    const confirmMsg =
                      lang === 'vi'
                        ? `Bạn có chắc chắn muốn xóa buổi tập "${routineName}"?`
                        : `Are you sure you want to delete routine "${routineName}"?`;
                    if (!window.confirm(confirmMsg)) return;
                    onDeleteRoutine(routine.id);
                  }}
                  className="w-7 h-7 rounded-full text-slate-400 hover:bg-red-50 hover:text-red-600 text-xs font-bold flex items-center justify-center transition cursor-pointer"
                  title={lang === 'vi' ? 'Xóa buổi tập' : 'Delete routine'}
                >
                  ✕
                </button>
              </div>

              <div className="pt-3 mt-3 border-t border-slate-100 space-y-1.5 text-xs text-slate-600">
                {routine.exercises.length === 0 ? (
                  <p className="text-slate-400 italic">{t.noExercisesYet}</p>
                ) : (
                  routine.exercises.map((item, idx) => {
                    const ex = exercisesMap[item.exerciseId];
                    const firstSet = item.sets[0] || { weight: 0, reps: 0 };
                    const displayName =
                      ex && lang === 'vi' && ex.nameVi
                        ? ex.nameVi
                        : ex
                          ? ex.name
                          : item.exerciseId;
                    return (
                      <div key={idx} className="space-y-0.5">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-slate-800 truncate pr-2">
                            {displayName}
                          </span>
                          <span className="text-slate-400 font-medium shrink-0">
                            {item.sets.length} {t.setsLabel} • {firstSet.weight}kg
                            × {firstSet.reps}
                          </span>
                        </div>
                        {item.note && (
                          <p className="text-[11px] text-blue-600 truncate">
                            📌 {item.note}
                          </p>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
