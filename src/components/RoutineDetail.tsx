import React, { useState } from 'react';
import { Exercise, Language, Routine } from '../types/gym';
import {
  translateEquipment,
  translateMuscle,
  translateRoutineText,
  UI_TEXT,
} from '../i18n/translations';
import { ExercisePickerModal } from './ExercisePickerModal';

interface RoutineDetailProps {
  routine: Routine;
  lang: Language;
  exercisesMap: Record<string, Exercise>;
  allExercises: Exercise[];
  onUpdateRoutine: (updated: Routine) => void;
  onOpenExerciseInfo: (exerciseId: string, routineExIndex: number) => void;
}

export const RoutineDetail: React.FC<RoutineDetailProps> = ({
  routine,
  lang,
  exercisesMap,
  allExercises,
  onUpdateRoutine,
  onOpenExerciseInfo,
}) => {
  const t = UI_TEXT[lang];
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState(routine.name);
  const [editingNoteIdx, setEditingNoteIdx] = useState<number | null>(null);
  const [noteDraft, setNoteDraft] = useState('');

  const handleSetChange = (
    exIndex: number,
    setIndex: number,
    field: 'weight' | 'reps',
    value: number
  ) => {
    const nextExercises = routine.exercises.map((item, idx) => {
      if (idx !== exIndex) return item;
      const nextSets = item.sets.map((s, sIdx) =>
        sIdx === setIndex ? { ...s, [field]: Math.max(0, value) } : s
      );
      return { ...item, sets: nextSets };
    });
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleSaveExerciseNote = (exIndex: number, text: string) => {
    const nextExercises = routine.exercises.map((item, idx) =>
      idx === exIndex ? { ...item, note: text.trim() } : item
    );
    onUpdateRoutine({ ...routine, exercises: nextExercises });
    setEditingNoteIdx(null);
  };

  const handleAddSet = (exIndex: number) => {
    const nextExercises = routine.exercises.map((item, idx) => {
      if (idx !== exIndex) return item;
      const lastSet =
        item.sets.length > 0
          ? { ...item.sets[item.sets.length - 1] }
          : { weight: 60, reps: 10 };
      return { ...item, sets: [...item.sets, lastSet] };
    });
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleRemoveLastSet = (exIndex: number) => {
    const nextExercises = routine.exercises.map((item, idx) => {
      if (idx !== exIndex || item.sets.length <= 1) return item;
      return { ...item, sets: item.sets.slice(0, -1) };
    });
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleRemoveExercise = (exIndex: number) => {
    const nextExercises = routine.exercises.filter((_, idx) => idx !== exIndex);
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleMoveExercise = (exIndex: number, direction: -1 | 1) => {
    const targetIndex = exIndex + direction;
    if (targetIndex < 0 || targetIndex >= routine.exercises.length) return;
    const nextExercises = [...routine.exercises];
    const [moved] = nextExercises.splice(exIndex, 1);
    nextExercises.splice(targetIndex, 0, moved);
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleAddExercise = (exerciseId: string) => {
    const nextExercises = [
      ...routine.exercises,
      {
        exerciseId,
        note: '',
        sets: [
          { weight: 60, reps: 10 },
          { weight: 60, reps: 10 },
          { weight: 60, reps: 10 },
        ],
      },
    ];
    onUpdateRoutine({ ...routine, exercises: nextExercises });
    setIsPickerOpen(false);
  };

  const saveTitle = () => {
    const trimmed = titleDraft.trim();
    if (trimmed) {
      onUpdateRoutine({ ...routine, name: trimmed });
    } else {
      setTitleDraft(routine.name);
    }
    setIsEditingTitle(false);
  };

  return (
    <div className="space-y-4">
      {/* Routine Sub-header Bar */}
      <div className="bg-white rounded-[24px] p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {isEditingTitle ? (
            <input
              type="text"
              value={titleDraft}
              autoFocus
              onChange={(e) => setTitleDraft(e.target.value)}
              onBlur={saveTitle}
              onKeyDown={(e) => e.key === 'Enter' && saveTitle()}
              className="rounded-xl bg-slate-100 px-3 py-1 font-bold text-base text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          ) : (
            <button
              onClick={() => {
                setTitleDraft(translateRoutineText(routine.name, lang));
                setIsEditingTitle(true);
              }}
              className="text-left group cursor-pointer"
            >
              <h2 className="font-bold text-lg text-slate-900 group-hover:text-blue-600 transition flex items-center gap-1.5">
                {translateRoutineText(routine.name, lang)}
                <span className="text-xs text-slate-400 font-normal">✎</span>
              </h2>
            </button>
          )}
        </div>

        <button
          onClick={() => setIsPickerOpen(true)}
          className="px-4 py-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition shadow-xs cursor-pointer"
        >
          {t.addExerciseBtn}
        </button>
      </div>

      {/* Empty State */}
      {routine.exercises.length === 0 && (
        <div className="bg-white rounded-[24px] p-8 text-center shadow-xs space-y-3">
          <p className="text-sm text-slate-500">{t.emptyRoutineText}</p>
          <button
            onClick={() => setIsPickerOpen(true)}
            className="px-5 py-2.5 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition cursor-pointer"
          >
            {t.addFirstExerciseBtn}
          </button>
        </div>
      )}

      {/* Exercise Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
        {routine.exercises.map((item, exIdx) => {
          const ex = exercisesMap[item.exerciseId];
          if (!ex) return null;
          const note = item.note || '';
          const displayName =
            lang === 'vi' && ex.nameVi ? ex.nameVi : ex.name;

          return (
            <div
              key={`${ex.id}-${exIdx}`}
              className="bg-white rounded-[24px] p-4 shadow-xs space-y-3"
            >
              {/* Card Header: Exercise Name on left, Reorder/Delete + (i) Icon on right */}
              <div className="flex items-start justify-between border-b border-slate-100 pb-2.5 gap-2">
                <div className="min-w-0">
                  <button
                    onClick={() => onOpenExerciseInfo(ex.id, exIdx)}
                    className="text-left hover:text-blue-600 transition cursor-pointer"
                  >
                    <h3 className="font-bold text-base text-slate-900 leading-snug">
                      {displayName}
                    </h3>
                  </button>
                  <span className="text-xs text-slate-400 font-medium block mt-0.5">
                    {ex.primaryMuscles
                      .map((m) => translateMuscle(m, lang))
                      .join(', ')}{' '}
                    • {translateEquipment(ex.equipment, lang)}
                  </span>
                </div>

                <div className="flex items-center gap-1 shrink-0">
                  {routine.exercises.length > 1 && (
                    <>
                      <button
                        onClick={() => handleMoveExercise(exIdx, -1)}
                        disabled={exIdx === 0}
                        className="w-7 h-7 rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-30 text-xs font-bold flex items-center justify-center cursor-pointer"
                      >
                        ↑
                      </button>
                      <button
                        onClick={() => handleMoveExercise(exIdx, 1)}
                        disabled={exIdx === routine.exercises.length - 1}
                        className="w-7 h-7 rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-30 text-xs font-bold flex items-center justify-center cursor-pointer"
                      >
                        ↓
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => handleRemoveExercise(exIdx)}
                    className="w-7 h-7 rounded-full text-slate-400 hover:bg-red-50 hover:text-red-600 text-xs font-bold flex items-center justify-center cursor-pointer"
                  >
                    ✕
                  </button>

                  {/* THE (i) ICON BUTTON */}
                  <button
                    onClick={() => onOpenExerciseInfo(ex.id, exIdx)}
                    className="w-8 h-8 rounded-full bg-slate-100 hover:bg-blue-600 text-slate-700 hover:text-white font-serif italic font-bold text-sm flex items-center justify-center transition cursor-pointer ml-1"
                  >
                    i
                  </button>
                </div>
              </div>

              {/* Set Rows: 1 | 60kg | 10 reps */}
              <div className="divide-y divide-slate-100">
                {item.sets.map((set, setIdx) => (
                  <div
                    key={setIdx}
                    className="grid grid-cols-12 items-center py-2.5"
                  >
                    <div className="col-span-2">
                      <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center">
                        {setIdx + 1}
                      </span>
                    </div>

                    {/* Weight (kg) */}
                    <div className="col-span-5 flex items-center justify-center gap-1.5">
                      <button
                        onClick={() =>
                          handleSetChange(
                            exIdx,
                            setIdx,
                            'weight',
                            Number((set.weight - 2.5).toFixed(1))
                          )
                        }
                        className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer"
                      >
                        −
                      </button>
                      <div className="flex items-baseline gap-0.5">
                        <input
                          type="number"
                          step="0.5"
                          value={set.weight}
                          onChange={(e) =>
                            handleSetChange(
                              exIdx,
                              setIdx,
                              'weight',
                              parseFloat(e.target.value) || 0
                            )
                          }
                          className="w-11 text-right font-bold text-sm text-slate-900 bg-transparent focus:outline-none focus:bg-slate-50 rounded"
                        />
                        <span className="text-xs text-slate-500 font-medium">
                          kg
                        </span>
                      </div>
                      <button
                        onClick={() =>
                          handleSetChange(
                            exIdx,
                            setIdx,
                            'weight',
                            Number((set.weight + 2.5).toFixed(1))
                          )
                        }
                        className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer"
                      >
                        +
                      </button>
                    </div>

                    {/* Reps */}
                    <div className="col-span-5 flex items-center justify-end gap-1.5">
                      <button
                        onClick={() =>
                          handleSetChange(exIdx, setIdx, 'reps', set.reps - 1)
                        }
                        className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer"
                      >
                        −
                      </button>
                      <div className="flex items-baseline gap-1">
                        <input
                          type="number"
                          value={set.reps}
                          onChange={(e) =>
                            handleSetChange(
                              exIdx,
                              setIdx,
                              'reps',
                              parseInt(e.target.value, 10) || 0
                            )
                          }
                          className="w-8 text-right font-bold text-sm text-slate-900 bg-transparent focus:outline-none focus:bg-slate-50 rounded"
                        />
                        <span className="text-xs text-slate-500 font-medium">
                          {t.repsLabel}
                        </span>
                      </div>
                      <button
                        onClick={() =>
                          handleSetChange(exIdx, setIdx, 'reps', set.reps + 1)
                        }
                        className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer"
                      >
                        +
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Inline Routine Note Editor (when active) */}
              {editingNoteIdx === exIdx && (
                <div className="pt-2 border-t border-slate-100 flex items-center gap-2">
                  <input
                    type="text"
                    autoFocus
                    value={noteDraft}
                    onChange={(e) => setNoteDraft(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleSaveExerciseNote(exIdx, noteDraft);
                      } else if (e.key === 'Escape') {
                        setEditingNoteIdx(null);
                      }
                    }}
                    placeholder={t.commentPlaceholder}
                    className="flex-1 rounded-xl bg-slate-100 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() => handleSaveExerciseNote(exIdx, noteDraft)}
                    className="px-3 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-bold cursor-pointer"
                  >
                    {t.saveNoteBtn}
                  </button>
                </div>
              )}

              {/* Card Footer: Routine-scoped Note + Set Controls */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                <button
                  onClick={() => {
                    setNoteDraft(note);
                    setEditingNoteIdx(editingNoteIdx === exIdx ? null : exIdx);
                  }}
                  className="text-xs text-blue-600 hover:underline truncate max-w-[55%] text-left cursor-pointer font-medium"
                >
                  {note ? (
                    <span>📌 {note}</span>
                  ) : (
                    <span className="text-slate-400 font-normal">
                      {t.addNotePlaceholder}
                    </span>
                  )}
                </button>

                <div className="flex items-center gap-2 shrink-0">
                  {item.sets.length > 1 && (
                    <button
                      onClick={() => handleRemoveLastSet(exIdx)}
                      className="px-2.5 py-1 rounded-xl text-xs font-semibold text-slate-500 bg-slate-100 hover:bg-slate-200 transition cursor-pointer"
                    >
                      {t.minusSet}
                    </button>
                  )}
                  <button
                    onClick={() => handleAddSet(exIdx)}
                    className="px-3 py-1 rounded-xl text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 transition cursor-pointer"
                  >
                    {t.addSet}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Exercise Picker Modal */}
      <ExercisePickerModal
        isOpen={isPickerOpen}
        lang={lang}
        exercises={allExercises}
        onClose={() => setIsPickerOpen(false)}
        onSelectExercise={handleAddExercise}
      />
    </div>
  );
};
