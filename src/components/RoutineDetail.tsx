import React, { useState } from 'react';
import { Exercise, Language, Routine } from '../types/gym';
import {
  translateEquipment,
  translateMuscle,
  translateRoutineText,
  UI_TEXT,
} from '../i18n/translations';
import { ExercisePickerModal } from './ExercisePickerModal';
import { triggerHapticLight, triggerHapticMedium } from '../services/native';

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
  const [isEditMode, setIsEditMode] = useState(false);
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const [replacingExIdx, setReplacingExIdx] = useState<number | null>(null);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState(routine.name);
  const [editingNoteIdx, setEditingNoteIdx] = useState<number | null>(null);
  const [noteDraft, setNoteDraft] = useState('');

  // Drag-and-drop state (supports both desktop drag & mobile touch)
  const [draggedIdx, setDraggedIdx] = useState<number | null>(null);
  const [dragOverIdx, setDragOverIdx] = useState<number | null>(null);

  const handleSetChange = (
    exIndex: number,
    setIndex: number,
    field: 'weight' | 'reps',
    value: number
  ) => {
    triggerHapticLight();
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
    triggerHapticLight();
    const nextExercises = routine.exercises.map((item, idx) =>
      idx === exIndex ? { ...item, note: text.trim() } : item
    );
    onUpdateRoutine({ ...routine, exercises: nextExercises });
    setEditingNoteIdx(null);
  };

  const handleAddSet = (exIndex: number) => {
    triggerHapticLight();
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
    triggerHapticLight();
    const nextExercises = routine.exercises.map((item, idx) => {
      if (idx !== exIndex || item.sets.length <= 1) return item;
      return { ...item, sets: item.sets.slice(0, -1) };
    });
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleRemoveExercise = (exIndex: number) => {
    triggerHapticLight();
    const nextExercises = routine.exercises.filter((_, idx) => idx !== exIndex);
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleReorderExercises = (fromIdx: number, toIdx: number) => {
    if (fromIdx === toIdx || fromIdx < 0 || toIdx < 0) return;
    triggerHapticMedium();
    const nextExercises = [...routine.exercises];
    const [moved] = nextExercises.splice(fromIdx, 1);
    nextExercises.splice(toIdx, 0, moved);
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleSelectFromPicker = (exerciseId: string) => {
    if (replacingExIdx !== null) {
      // Replace/Change exercise in-place while keeping its sets & note
      const nextExercises = routine.exercises.map((item, idx) =>
        idx === replacingExIdx ? { ...item, exerciseId } : item
      );
      onUpdateRoutine({ ...routine, exercises: nextExercises });
      setReplacingExIdx(null);
      setIsPickerOpen(false);
      return;
    }

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

  // Touch drag support for mobile / Samsung Galaxy
  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isEditMode || draggedIdx === null) return;
    const touch = e.touches[0];
    if (!touch) return;
    const el = document.elementFromPoint(touch.clientX, touch.clientY);
    const cardEl = el?.closest('[data-routine-card-idx]');
    if (cardEl) {
      const overIdx = Number(cardEl.getAttribute('data-routine-card-idx'));
      if (!Number.isNaN(overIdx) && overIdx !== dragOverIdx) {
        setDragOverIdx(overIdx);
      }
    }
  };

  const handleTouchEnd = () => {
    if (
      draggedIdx !== null &&
      dragOverIdx !== null &&
      draggedIdx !== dragOverIdx
    ) {
      handleReorderExercises(draggedIdx, dragOverIdx);
    }
    setDraggedIdx(null);
    setDragOverIdx(null);
  };

  return (
    <div className="space-y-4">
      {/* Routine Sub-header Bar */}
      <div className="bg-white rounded-[24px] p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          {isEditMode && isEditingTitle ? (
            <input
              type="text"
              value={titleDraft}
              autoFocus
              onChange={(e) => setTitleDraft(e.target.value)}
              onBlur={saveTitle}
              onKeyDown={(e) => e.key === 'Enter' && saveTitle()}
              className="rounded-xl bg-slate-100 px-3 py-1 font-bold text-base text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          ) : isEditMode ? (
            <div>
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
              {routine.exercises.length > 1 && (
                <p className="text-xs text-blue-600 font-medium mt-0.5">
                  {t.dragHint}
                </p>
              )}
            </div>
          ) : (
            <h2 className="font-bold text-lg text-slate-900">
              {translateRoutineText(routine.name, lang)}
            </h2>
          )}
        </div>

        {/* Right Controls: Read-Only Mode shows "Edit", Edit Mode shows "+ Add Exercise" + "Done" */}
        <div className="flex items-center gap-2">
          {isEditMode && (
            <button
              onClick={() => {
                setReplacingExIdx(null);
                setIsPickerOpen(true);
              }}
              className="px-3.5 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition cursor-pointer"
            >
              {t.addExerciseBtn}
            </button>
          )}

          <button
            onClick={() => {
              triggerHapticLight();
              setIsEditMode(!isEditMode);
              setIsEditingTitle(false);
              setEditingNoteIdx(null);
            }}
            className={`px-4 py-2 rounded-full text-xs font-bold transition shadow-xs cursor-pointer ${
              isEditMode
                ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isEditMode ? t.doneEditingBtn : t.editRoutineBtn}
          </button>
        </div>
      </div>

      {/* Empty State */}
      {routine.exercises.length === 0 && (
        <div className="bg-white rounded-[24px] p-8 text-center shadow-xs space-y-3">
          <p className="text-sm text-slate-500">{t.emptyRoutineText}</p>
          <button
            onClick={() => {
              setIsEditMode(true);
              setReplacingExIdx(null);
              setIsPickerOpen(true);
            }}
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
          const isBeingDragged = draggedIdx === exIdx;
          const isDragTarget =
            dragOverIdx === exIdx && draggedIdx !== null && draggedIdx !== exIdx;

          return (
            <div
              key={`${ex.id}-${exIdx}`}
              data-routine-card-idx={exIdx}
              draggable={isEditMode && editingNoteIdx === null}
              onDragStart={(e) => {
                if (!isEditMode) return;
                setDraggedIdx(exIdx);
                e.dataTransfer.effectAllowed = 'move';
              }}
              onDragOver={(e) => {
                if (!isEditMode || draggedIdx === null) return;
                e.preventDefault();
                if (dragOverIdx !== exIdx) {
                  setDragOverIdx(exIdx);
                }
              }}
              onDrop={(e) => {
                e.preventDefault();
                if (draggedIdx !== null && draggedIdx !== exIdx) {
                  handleReorderExercises(draggedIdx, exIdx);
                }
                setDraggedIdx(null);
                setDragOverIdx(null);
              }}
              onDragEnd={() => {
                setDraggedIdx(null);
                setDragOverIdx(null);
              }}
              className={`bg-white rounded-[24px] p-4 shadow-xs space-y-3 transition ${
                isBeingDragged ? 'opacity-50 scale-[0.98]' : ''
              } ${
                isDragTarget ? 'ring-2 ring-blue-500 bg-blue-50/20' : ''
              }`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between border-b border-slate-100 pb-2.5 gap-2">
                <div className="flex items-start gap-2 min-w-0">
                  {/* Drag Handle in Edit Mode */}
                  {isEditMode && (
                    <div
                      onTouchStart={() => {
                        triggerHapticLight();
                        setDraggedIdx(exIdx);
                      }}
                      onTouchMove={handleTouchMove}
                      onTouchEnd={handleTouchEnd}
                      title={t.dragHint}
                      className="mt-0.5 px-1.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500 cursor-grab active:cursor-grabbing select-none touch-none shrink-0 font-bold text-xs leading-none"
                    >
                      ⋮⋮
                    </div>
                  )}

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
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  {isEditMode && (
                    <>
                      {/* Change / Swap Exercise Button */}
                      <button
                        onClick={() => {
                          setReplacingExIdx(exIdx);
                          setIsPickerOpen(true);
                        }}
                        className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-blue-50 text-slate-600 hover:text-blue-600 text-xs font-semibold transition cursor-pointer"
                      >
                        {t.changeExerciseBtn}
                      </button>

                      {/* Remove Exercise Button */}
                      <button
                        onClick={() => handleRemoveExercise(exIdx)}
                        className="w-7 h-7 rounded-full text-slate-400 hover:bg-red-50 hover:text-red-600 text-xs font-bold flex items-center justify-center cursor-pointer"
                      >
                        ✕
                      </button>
                    </>
                  )}

                  {/* THE (i) ICON BUTTON */}
                  <button
                    onClick={() => onOpenExerciseInfo(ex.id, exIdx)}
                    className="w-8 h-8 rounded-full bg-slate-100 hover:bg-blue-600 text-slate-700 hover:text-white font-serif italic font-bold text-sm flex items-center justify-center transition cursor-pointer"
                  >
                    i
                  </button>
                </div>
              </div>

              {/* Set Rows: Read-Only Mode vs Edit Mode */}
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
                    {isEditMode ? (
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
                            className="w-11 text-right font-bold text-sm text-slate-900 bg-slate-50 px-1 py-0.5 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded"
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
                    ) : (
                      <div className="col-span-5 flex items-baseline justify-center gap-1">
                        <span className="font-bold text-sm text-slate-900">
                          {set.weight}
                        </span>
                        <span className="text-xs text-slate-500 font-medium">
                          kg
                        </span>
                      </div>
                    )}

                    {/* Reps */}
                    {isEditMode ? (
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
                            className="w-9 text-right font-bold text-sm text-slate-900 bg-slate-50 px-1 py-0.5 focus:outline-none focus:ring-1 focus:ring-blue-500 rounded"
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
                    ) : (
                      <div className="col-span-5 flex items-baseline justify-end gap-1 pr-1">
                        <span className="font-bold text-sm text-slate-900">
                          {set.reps}
                        </span>
                        <span className="text-xs text-slate-500 font-medium">
                          {t.repsLabel}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Inline Routine Note Editor (only in Edit Mode) */}
              {isEditMode && editingNoteIdx === exIdx && (
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

              {/* Card Footer: In Read-Only Mode, only show if there is a pinned note */}
              {isEditMode ? (
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    onClick={() => {
                      setNoteDraft(note);
                      setEditingNoteIdx(
                        editingNoteIdx === exIdx ? null : exIdx
                      );
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
              ) : (
                note && (
                  <div className="pt-2 border-t border-slate-100">
                    <p className="text-xs text-blue-600 font-medium">
                      📌 {note}
                    </p>
                  </div>
                )
              )}
            </div>
          );
        })}
      </div>

      {/* Add / Swap Exercise Picker Modal */}
      <ExercisePickerModal
        isOpen={isPickerOpen}
        lang={lang}
        exercises={allExercises}
        onClose={() => {
          setIsPickerOpen(false);
          setReplacingExIdx(null);
        }}
        onSelectExercise={handleSelectFromPicker}
      />
    </div>
  );
};
