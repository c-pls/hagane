import React, { useState, useEffect } from 'react';
import {
  Exercise,
  Language,
  Routine,
  RoutineExerciseItem,
  WorkoutSet,
} from '../types/gym';
import {
  translateEquipment,
  translateMuscle,
  translateRoutineText,
  UI_TEXT,
} from '../i18n/translations';
import { triggerHapticLight, triggerHapticMedium } from '../services/native';

interface SetNumberInputProps {
  value: number;
  onChange: (value: number) => void;
  isDecimal?: boolean;
  className?: string;
  min?: number;
}

/**
 * Mobile-friendly numeric input for weights and reps.
 * - Allows clearing the field completely without forcing an unwanted '0'.
 * - Auto-selects existing text on tap so typing immediately replaces the number.
 * - Opens the phone's native numeric keypad with decimal dot support.
 */
const SetNumberInput: React.FC<SetNumberInputProps> = ({
  value,
  onChange,
  isDecimal = false,
  className = '',
  min = 0,
}) => {
  const [draft, setDraft] = useState<string>(value.toString());
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (!isFocused) {
      setDraft(value.toString());
    }
  }, [value, isFocused]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;

    // Filter characters: allow digits and optional single decimal point
    if (isDecimal) {
      if (!/^\d*\.?\d*$/.test(raw)) return;
    } else {
      if (!/^\d*$/.test(raw)) return;
    }

    setDraft(raw);

    // If it's a non-empty, non-dot number, update parent immediately
    if (raw !== '' && raw !== '.') {
      const parsed = parseFloat(raw);
      if (!Number.isNaN(parsed)) {
        onChange(Math.max(min, parsed));
      }
    }
  };

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true);
    const target = e.target;
    // Auto-select entire number on tap so typing immediately overwrites old number
    // Timeout defeats Android WebView touch-release caret placement
    setTimeout(() => {
      try {
        target.select();
      } catch {
        // ignore
      }
    }, 25);
  };

  const handleBlur = () => {
    setIsFocused(false);
    if (draft === '' || draft === '.') {
      onChange(min);
      setDraft(min.toString());
    } else {
      const parsed = parseFloat(draft);
      const safe = Number.isNaN(parsed) ? min : Math.max(min, parsed);
      onChange(safe);
      setDraft(safe.toString());
    }
  };

  return (
    <input
      type="text"
      inputMode={isDecimal ? 'decimal' : 'numeric'}
      autoComplete="off"
      autoCorrect="off"
      autoCapitalize="off"
      spellCheck={false}
      value={isFocused ? draft : value.toString()}
      onChange={handleChange}
      onFocus={handleFocus}
      onBlur={handleBlur}
      className={className}
    />
  );
};

interface RoutineDetailProps {
  routine: Routine;
  lang: Language;
  exercisesMap: Record<string, Exercise>;
  allExercises: Exercise[];
  initialEditMode?: boolean;
  onUpdateRoutine: (updated: Routine) => void;
  onOpenExerciseInfo: (exerciseId: string, routineExIndex: number) => void;
  onOpenPicker: (params: {
    asWarmup: boolean;
    replacingExIdx: number | null;
    fromEditMode?: boolean;
  }) => void;
}

export const RoutineDetail: React.FC<RoutineDetailProps> = ({
  routine,
  lang,
  exercisesMap,
  initialEditMode = false,
  onUpdateRoutine,
  onOpenExerciseInfo,
  onOpenPicker,
}) => {
  const t = UI_TEXT[lang];
  const [isEditMode, setIsEditMode] = useState(initialEditMode);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState(routine.name);
  const [editingNoteIdx, setEditingNoteIdx] = useState<number | null>(null);
  const [noteDraft, setNoteDraft] = useState('');

  useEffect(() => {
    if (initialEditMode !== undefined) {
      setIsEditMode(initialEditMode);
    }
  }, [initialEditMode]);

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

  const handleToggleSetType = (exIndex: number, setIndex: number) => {
    if (!isEditMode) return;
    triggerHapticLight();
    const nextExercises = routine.exercises.map((item, idx) => {
      if (idx !== exIndex) return item;
      const nextSets: WorkoutSet[] = item.sets.map((s, sIdx) => {
        if (sIdx !== setIndex) return s;
        const nextType: 'normal' | 'warmup' =
          s.type === 'warmup' ? 'normal' : 'warmup';
        return { ...s, type: nextType };
      });
      return { ...item, sets: nextSets };
    });
    onUpdateRoutine({ ...routine, exercises: nextExercises });
  };

  const handleToggleExerciseWarmup = (exIndex: number) => {
    triggerHapticLight();
    const nextExercises = routine.exercises.map((item, idx) =>
      idx === exIndex ? { ...item, isWarmup: !item.isWarmup } : item
    );
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
      let nextType: 'normal' | 'warmup' | 'drop' = 'normal';
      if (item.isWarmup) {
        nextType = 'warmup';
      } else if (item.sets.length > 0) {
        const last = item.sets[item.sets.length - 1];
        if (last.type === 'warmup' && item.sets.length === 1) {
          nextType = 'normal';
        } else {
          nextType = last.type || 'normal';
        }
      }

      const lastSet =
        item.sets.length > 0
          ? {
              weight: item.sets[item.sets.length - 1].weight,
              reps: item.sets[item.sets.length - 1].reps,
              type: nextType,
            }
          : {
              weight: item.isWarmup ? 20 : 60,
              reps: item.isWarmup ? 15 : 10,
              type: item.isWarmup ? ('warmup' as const) : ('normal' as const),
            };
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

  const warmupIndices = routine.exercises
    .map((item, idx) => (item.isWarmup ? idx : -1))
    .filter((idx) => idx !== -1);

  const mainIndices = routine.exercises
    .map((item, idx) => (!item.isWarmup ? idx : -1))
    .filter((idx) => idx !== -1);

  const renderExerciseCard = (item: RoutineExerciseItem, exIdx: number) => {
    const ex = exercisesMap[item.exerciseId];
    if (!ex) return null;
    const note = item.note || '';
    const displayName = lang === 'vi' && ex.nameVi ? ex.nameVi : ex.name;
    const isBeingDragged = draggedIdx === exIdx;
    const isDragTarget =
      dragOverIdx === exIdx && draggedIdx !== null && draggedIdx !== exIdx;
    const isWarmupEx = Boolean(item.isWarmup);

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
          isWarmupEx ? 'border-l-4 border-l-amber-500' : ''
        } ${isBeingDragged ? 'opacity-50 scale-[0.98]' : ''} ${
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
              <div className="flex items-center gap-1.5 flex-wrap">
                <button
                  type="button"
                  onClick={() => onOpenExerciseInfo(ex.id, exIdx)}
                  className="text-left hover:text-blue-600 transition cursor-pointer"
                >
                  <h3 className="font-bold text-base text-slate-900 leading-snug">
                    {displayName}
                  </h3>
                </button>
                {isWarmupEx && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wide bg-amber-100 text-amber-800 border border-amber-200">
                    🔥 {t.warmupBadge}
                  </span>
                )}
              </div>
              <span className="text-xs text-slate-400 font-medium block mt-0.5">
                {ex.primaryMuscles
                  .map((m) => translateMuscle(m, lang))
                  .join(', ')}{' '}
                • {translateEquipment(ex.equipment, lang)}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
            {isEditMode && (
              <>
                {/* Toggle between Warm-up & Main */}
                <button
                  type="button"
                  onClick={() => handleToggleExerciseWarmup(exIdx)}
                  className={`px-2.5 py-1 rounded-full text-xs font-semibold transition cursor-pointer ${
                    isWarmupEx
                      ? 'bg-blue-50 text-blue-700 hover:bg-blue-100'
                      : 'bg-amber-50 text-amber-800 hover:bg-amber-100'
                  }`}
                  title={isWarmupEx ? t.moveToMain : t.moveToWarmup}
                >
                  {isWarmupEx ? t.moveToMain : t.moveToWarmup}
                </button>

                {/* Change / Swap Exercise Button */}
                <button
                  type="button"
                  onClick={() => {
                    triggerHapticLight();
                    onOpenPicker({
                      asWarmup: isWarmupEx,
                      replacingExIdx: exIdx,
                      fromEditMode: isEditMode,
                    });
                  }}
                  className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-blue-50 text-slate-600 hover:text-blue-600 text-xs font-semibold transition cursor-pointer"
                >
                  {t.changeExerciseBtn}
                </button>

                {/* Remove Exercise Button */}
                <button
                  type="button"
                  onClick={() => handleRemoveExercise(exIdx)}
                  className="w-7 h-7 rounded-full text-slate-400 hover:bg-red-50 hover:text-red-600 text-xs font-bold flex items-center justify-center cursor-pointer"
                >
                  ✕
                </button>
              </>
            )}

            {/* THE (i) ICON BUTTON */}
            <button
              type="button"
              onClick={() => onOpenExerciseInfo(ex.id, exIdx)}
              className="w-8 h-8 rounded-full bg-slate-100 hover:bg-blue-600 text-slate-700 hover:text-white font-serif italic font-bold text-sm flex items-center justify-center transition cursor-pointer"
            >
              i
            </button>
          </div>
        </div>

        {/* Set Rows */}
        <div className="divide-y divide-slate-100">
          {item.sets.map((set, setIdx) => {
            const isWarmupSet = set.type === 'warmup';
            const workingSetNum =
              item.sets
                .slice(0, setIdx)
                .filter((s) => s.type !== 'warmup').length + 1;
            const setBadgeLabel = isWarmupSet ? t.warmupSetTag : workingSetNum;

            return (
              <div
                key={setIdx}
                className="grid grid-cols-12 items-center py-2.5"
              >
                {/* Set Badge */}
                <div className="col-span-2 flex items-center">
                  {isEditMode ? (
                    <button
                      type="button"
                      onClick={() => handleToggleSetType(exIdx, setIdx)}
                      title={
                        isWarmupSet
                          ? `${t.warmupBadge} (Click to toggle working set)`
                          : `Working Set (Click to toggle warmup set)`
                      }
                      className={`w-7 h-7 rounded-full font-bold text-xs flex items-center justify-center transition cursor-pointer shadow-xs ${
                        isWarmupSet
                          ? 'bg-amber-500 hover:bg-amber-600 text-white ring-2 ring-amber-300'
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      }`}
                    >
                      {setBadgeLabel}
                    </button>
                  ) : (
                    <span
                      className={`w-6 h-6 rounded-full font-bold text-xs flex items-center justify-center ${
                        isWarmupSet
                          ? 'bg-amber-100 text-amber-800 border border-amber-300 font-extrabold'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {setBadgeLabel}
                    </span>
                  )}
                </div>

                {/* Weight (kg) */}
                {isEditMode ? (
                  <div className="col-span-5 flex items-center justify-center gap-1.5">
                    <button
                      type="button"
                      onClick={() =>
                        handleSetChange(
                          exIdx,
                          setIdx,
                          'weight',
                          Number((set.weight - 2.5).toFixed(1))
                        )
                      }
                      className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer shrink-0"
                    >
                      −
                    </button>
                    <div className="flex items-baseline gap-1">
                      <SetNumberInput
                        value={set.weight}
                        isDecimal
                        onChange={(newWeight) =>
                          handleSetChange(exIdx, setIdx, 'weight', newWeight)
                        }
                        className="w-14 text-center font-bold text-sm text-slate-900 bg-slate-100 hover:bg-slate-200/80 focus:bg-white px-1.5 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg transition"
                      />
                      <span className="text-xs text-slate-500 font-medium">
                        kg
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() =>
                        handleSetChange(
                          exIdx,
                          setIdx,
                          'weight',
                          Number((set.weight + 2.5).toFixed(1))
                        )
                      }
                      className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer shrink-0"
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
                      type="button"
                      onClick={() =>
                        handleSetChange(
                          exIdx,
                          setIdx,
                          'reps',
                          Math.max(1, set.reps - 1)
                        )
                      }
                      className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer shrink-0"
                    >
                      −
                    </button>
                    <div className="flex items-baseline gap-1">
                      <SetNumberInput
                        value={set.reps}
                        min={1}
                        onChange={(newReps) =>
                          handleSetChange(exIdx, setIdx, 'reps', newReps)
                        }
                        className="w-12 text-center font-bold text-sm text-slate-900 bg-slate-100 hover:bg-slate-200/80 focus:bg-white px-1.5 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg transition"
                      />
                      <span className="text-xs text-slate-500 font-medium">
                        {t.repsLabel}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() =>
                        handleSetChange(exIdx, setIdx, 'reps', set.reps + 1)
                      }
                      className="w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs cursor-pointer shrink-0"
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
            );
          })}
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
              type="button"
              onClick={() => handleSaveExerciseNote(exIdx, noteDraft)}
              className="px-3 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-bold cursor-pointer"
            >
              {t.saveNoteBtn}
            </button>
          </div>
        )}

        {/* Card Footer */}
        {isEditMode ? (
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
            <button
              type="button"
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
                  type="button"
                  onClick={() => handleRemoveLastSet(exIdx)}
                  className="px-2.5 py-1 rounded-xl text-xs font-semibold text-slate-500 bg-slate-100 hover:bg-slate-200 transition cursor-pointer"
                >
                  {t.minusSet}
                </button>
              )}
              <button
                type="button"
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
              <p className="text-xs text-blue-600 font-medium">📌 {note}</p>
            </div>
          )
        )}
      </div>
    );
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
                type="button"
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

        {/* Right Controls */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          <button
            type="button"
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
          <div className="flex items-center justify-center gap-3">
            <button
              type="button"
              onClick={() => {
                triggerHapticLight();
                onOpenPicker({
                  asWarmup: true,
                  replacingExIdx: null,
                  fromEditMode: isEditMode,
                });
              }}
              className="px-4 py-2.5 rounded-full bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold transition cursor-pointer shadow-xs"
            >
              {t.addWarmupExerciseBtn}
            </button>
            <button
              type="button"
              onClick={() => {
                triggerHapticLight();
                onOpenPicker({
                  asWarmup: false,
                  replacingExIdx: null,
                  fromEditMode: isEditMode,
                });
              }}
              className="px-5 py-2.5 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition cursor-pointer"
            >
              {t.addFirstExerciseBtn}
            </button>
          </div>
        </div>
      )}

      {/* Routine Sections */}
      {routine.exercises.length > 0 && (
        <div className="space-y-6">
          {/* 1. Warm-up Exercises Section */}
          {warmupIndices.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                  <h3 className="font-bold text-sm text-slate-900 tracking-wide uppercase">
                    {t.warmupSectionTitle}
                  </h3>
                  <span className="text-xs text-amber-800 font-semibold bg-amber-100/80 px-2 py-0.5 rounded-full border border-amber-200">
                    {warmupIndices.length}
                  </span>
                </div>
                <span className="text-xs text-slate-400 font-medium hidden sm:inline">
                  {t.warmupSectionSubtitle}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
                {warmupIndices.map((idx) =>
                  renderExerciseCard(routine.exercises[idx], idx)
                )}
              </div>
              {isEditMode && (
                <button
                  type="button"
                  onClick={() => {
                    triggerHapticLight();
                    onOpenPicker({
                      asWarmup: true,
                      replacingExIdx: null,
                      fromEditMode: isEditMode,
                    });
                  }}
                  className="w-full py-2.5 px-4 rounded-xl border border-dashed border-amber-300 bg-amber-50/50 hover:bg-amber-100/60 text-amber-800 text-xs font-bold flex items-center justify-center gap-1.5 transition cursor-pointer"
                >
                  <span>🔥</span>
                  <span>{t.addWarmupExerciseBtn}</span>
                </button>
              )}
            </div>
          )}

          {/* Quick Add Warmup button when in Edit Mode and no warmup exercises yet */}
          {isEditMode && warmupIndices.length === 0 && (
            <button
              type="button"
              onClick={() => {
                triggerHapticLight();
                onOpenPicker({
                  asWarmup: true,
                  replacingExIdx: null,
                  fromEditMode: isEditMode,
                });
              }}
              className="w-full py-3 px-4 rounded-[20px] border-2 border-dashed border-amber-300/80 bg-amber-50/40 hover:bg-amber-50/80 text-amber-800 text-xs font-bold flex items-center justify-center gap-2 transition cursor-pointer"
            >
              <span>🔥</span>
              <span>{t.addWarmupExerciseBtn}</span>
              <span className="text-[11px] font-normal text-amber-700/80 hidden sm:inline">
                ({t.warmupSectionSubtitle})
              </span>
            </button>
          )}

          {/* 2. Main Workout Section */}
          {mainIndices.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                  <h3 className="font-bold text-sm text-slate-900 tracking-wide uppercase">
                    {t.mainSectionTitle}
                  </h3>
                  <span className="text-xs text-blue-800 font-semibold bg-blue-100/80 px-2 py-0.5 rounded-full border border-blue-200">
                    {mainIndices.length}
                  </span>
                </div>
                <span className="text-xs text-slate-400 font-medium hidden sm:inline">
                  {t.mainSectionSubtitle}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
                {mainIndices.map((idx) =>
                  renderExerciseCard(routine.exercises[idx], idx)
                )}
              </div>
            </div>
          )}

          {/* 3. Bottom Actions: Add Exercise & Add Warm-up moved to the end of the routine */}
          <div className="pt-3 pb-8 space-y-2.5">
            <button
              type="button"
              onClick={() => {
                triggerHapticLight();
                onOpenPicker({
                  asWarmup: false,
                  replacingExIdx: null,
                  fromEditMode: isEditMode,
                });
              }}
              className="w-full py-3.5 px-5 rounded-2xl bg-blue-600 hover:bg-blue-700 active:scale-[0.99] text-white font-bold text-sm flex items-center justify-center gap-2 shadow-sm transition cursor-pointer"
            >
              <span className="text-lg leading-none font-bold">+</span>
              <span>{t.addExerciseBtn}</span>
            </button>

            <button
              type="button"
              onClick={() => {
                triggerHapticLight();
                onOpenPicker({
                  asWarmup: true,
                  replacingExIdx: null,
                  fromEditMode: isEditMode,
                });
              }}
              className="w-full py-2.5 px-4 rounded-xl bg-amber-50 hover:bg-amber-100 active:scale-[0.99] text-amber-800 border border-amber-200 text-xs font-bold flex items-center justify-center gap-1.5 transition cursor-pointer"
            >
              <span>🔥</span>
              <span>{t.addWarmupExerciseBtn}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
