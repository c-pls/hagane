import React, { useMemo, useRef, useState } from 'react';
import { ActiveTab, Exercise, Language, Routine, ScreenRoute } from './types/gym';
import {
  translateEquipment,
  translateMuscle,
  UI_TEXT,
} from './i18n/translations';
import {
  getAllExercises,
  loadComments,
  loadCustomExercises,
  loadLanguage,
  loadRoutines,
  saveComments,
  saveCustomExercises,
  saveLanguage,
  saveRoutines,
  ShakenBackupPayload,
} from './services/storage';
import { RoutineList } from './components/RoutineList';
import { RoutineDetail } from './components/RoutineDetail';
import { ExerciseWiki } from './components/ExerciseWiki';
import { ExerciseDetail } from './components/ExerciseDetail';
import { BackupSync } from './components/BackupSync';

const UsaFlagIcon: React.FC = () => (
  <svg
    viewBox="0 0 28 20"
    className="w-5 h-3.5 rounded-[3px] shadow-2xs shrink-0"
    aria-hidden="true"
  >
    <rect width="28" height="20" fill="#B22234" />
    <path
      d="M0 3.07h28M0 6.15h28M0 9.23h28M0 12.3h28M0 15.38h28M0 18.46h28"
      stroke="#FFF"
      strokeWidth="1.54"
    />
    <rect width="12" height="10.77" fill="#3C3B6E" />
    <g fill="#FFF">
      <circle cx="2.4" cy="2.2" r="0.8" />
      <circle cx="6" cy="2.2" r="0.8" />
      <circle cx="9.6" cy="2.2" r="0.8" />
      <circle cx="4.2" cy="4.2" r="0.8" />
      <circle cx="7.8" cy="4.2" r="0.8" />
      <circle cx="2.4" cy="6.2" r="0.8" />
      <circle cx="6" cy="6.2" r="0.8" />
      <circle cx="9.6" cy="6.2" r="0.8" />
      <circle cx="4.2" cy="8.2" r="0.8" />
      <circle cx="7.8" cy="8.2" r="0.8" />
    </g>
  </svg>
);

const VietnamFlagIcon: React.FC = () => (
  <svg
    viewBox="0 0 28 20"
    className="w-5 h-3.5 rounded-[3px] shadow-2xs shrink-0"
    aria-hidden="true"
  >
    <rect width="28" height="20" fill="#DA251D" />
    <polygon
      points="14,4 15.35,8.15 19.7,8.15 16.18,10.7 17.52,14.85 14,12.3 10.48,14.85 11.82,10.7 8.3,8.15 12.65,8.15"
      fill="#FFFF00"
    />
  </svg>
);

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>(() => loadLanguage());
  const [routines, setRoutines] = useState<Routine[]>(() => loadRoutines());
  const [comments, setComments] = useState<Record<string, string>>(() =>
    loadComments()
  );
  const [customExercises, setCustomExercises] = useState<Exercise[]>(() =>
    loadCustomExercises()
  );

  const [activeTab, setActiveTab] = useState<ActiveTab>('routines');
  const [route, setRoute] = useState<ScreenRoute>(() => {
    const initial = loadRoutines();
    return initial.length > 0
      ? { name: 'routineDetail', routineId: initial[0].id }
      : { name: 'routineList' };
  });

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const toastTimeoutRef = useRef<number | null>(null);

  const t = UI_TEXT[lang];

  const handleToggleLanguage = (nextLang: Language) => {
    setLang(nextLang);
    saveLanguage(nextLang);
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    if (toastTimeoutRef.current) {
      window.clearTimeout(toastTimeoutRef.current);
    }
    toastTimeoutRef.current = window.setTimeout(() => {
      setToastMessage(null);
    }, 1800);
  };

  const allExercises = useMemo(
    () => getAllExercises(customExercises),
    [customExercises]
  );

  const exercisesMap = useMemo(() => {
    const map: Record<string, Exercise> = {};
    for (const ex of allExercises) {
      map[ex.id] = ex;
    }
    return map;
  }, [allExercises]);

  const handleSwitchTab = (tab: ActiveTab) => {
    setActiveTab(tab);
    if (tab === 'routines') {
      setRoute({ name: 'routineList' });
    } else if (tab === 'wiki') {
      setRoute({ name: 'wikiList' });
    } else {
      setRoute({ name: 'backup' });
    }
  };

  const handleUpdateRoutine = (updated: Routine) => {
    const next = routines.map((r) => (r.id === updated.id ? updated : r));
    setRoutines(next);
    saveRoutines(next);
  };

  const handleCreateRoutine = (name: string, tag: string) => {
    const newRoutine: Routine = {
      id: `routine-${Date.now()}`,
      name,
      tag,
      exercises: [],
    };
    const next = [...routines, newRoutine];
    setRoutines(next);
    saveRoutines(next);
    setRoute({ name: 'routineDetail', routineId: newRoutine.id });
  };

  const handleDeleteRoutine = (routineId: string) => {
    const next = routines.filter((r) => r.id !== routineId);
    setRoutines(next);
    saveRoutines(next);
    showToast(t.toastDeletedRoutine);
  };

  const handleSaveRoutineExerciseComment = (
    routineId: string | undefined,
    routineExIndex: number | undefined,
    commentText: string
  ) => {
    if (!routineId || routineExIndex === undefined) return;
    const targetRoutine = routines.find((r) => r.id === routineId);
    if (!targetRoutine) return;
    const nextExercises = targetRoutine.exercises.map((item, idx) =>
      idx === routineExIndex ? { ...item, note: commentText.trim() } : item
    );
    handleUpdateRoutine({ ...targetRoutine, exercises: nextExercises });
    showToast(t.toastSavedNote);
  };

  const handleAddCustomExercise = (newExercise: Exercise) => {
    const next = [newExercise, ...customExercises];
    setCustomExercises(next);
    saveCustomExercises(next);
  };

  const handleAddExerciseToRoutine = (
    routineId: string,
    exerciseId: string
  ) => {
    const targetRoutine = routines.find((r) => r.id === routineId);
    if (!targetRoutine) return;
    const updated: Routine = {
      ...targetRoutine,
      exercises: [
        ...targetRoutine.exercises,
        {
          exerciseId,
          note: '',
          sets: [
            { weight: 60, reps: 10 },
            { weight: 60, reps: 10 },
            { weight: 60, reps: 10 },
          ],
        },
      ],
    };
    handleUpdateRoutine(updated);
    const ex = exercisesMap[exerciseId];
    const exName = ex && lang === 'vi' && ex.nameVi ? ex.nameVi : ex?.name;
    showToast(`+ ${exName} → ${targetRoutine.name}`);
  };

  const handleRestoreBackup = (payload: ShakenBackupPayload) => {
    setRoutines(payload.routines);
    saveRoutines(payload.routines);
    setComments(payload.comments);
    saveComments(payload.comments);
    setCustomExercises(payload.customExercises);
    saveCustomExercises(payload.customExercises);
  };

  // Header Left (Clean — no subtitle under Shaken)
  const renderHeaderLeft = () => {
    if (route.name === 'exerciseInfo') {
      const ex = exercisesMap[route.exerciseId];
      const displayName =
        ex && lang === 'vi' && ex.nameVi ? ex.nameVi : ex?.name;
      return (
        <div className="flex items-center gap-2.5 min-w-0">
          <button
            onClick={() => setRoute(route.returnTo)}
            className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition cursor-pointer shrink-0"
          >
            {t.back}
          </button>
          <div className="min-w-0">
            <h1 className="font-bold text-base text-slate-900 leading-tight truncate">
              {displayName || 'Exercise'}
            </h1>
            {ex && (
              <p className="text-xs text-slate-400 font-medium truncate">
                {translateEquipment(ex.equipment, lang)} •{' '}
                {translateMuscle(ex.category, lang)}
              </p>
            )}
          </div>
        </div>
      );
    }

    if (route.name === 'routineDetail') {
      return (
        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setRoute({ name: 'routineList' })}
            className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition cursor-pointer"
          >
            {t.routinesBack}
          </button>
          <h1 className="font-bold text-base text-slate-900 leading-tight">
            Shaken
          </h1>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-xl bg-blue-600 text-white font-black text-sm flex items-center justify-center shadow-xs">
          S
        </div>
        <h1 className="font-bold text-base text-slate-900 leading-tight">
          Shaken
        </h1>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#f2f4f7] text-slate-900 flex flex-col pb-20">
      {/* Top Sticky App Bar */}
      <header className="bg-white/95 backdrop-blur-xs border-b border-slate-200/70 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-2">
          {renderHeaderLeft()}

          <div className="flex items-center gap-2 shrink-0">
            {toastMessage && (
              <span className="px-3 py-1 rounded-full bg-emerald-600 text-white text-xs font-bold">
                {toastMessage}
              </span>
            )}

            {/* Flag Icon + Language Select Dropdown (USA / Vietnam) */}
            <div className="relative flex items-center bg-slate-100 hover:bg-slate-200/70 rounded-xl pl-2.5 pr-2 py-1.5 transition border border-slate-200/70">
              {lang === 'en' ? <UsaFlagIcon /> : <VietnamFlagIcon />}
              <select
                aria-label="Select Language"
                value={lang}
                onChange={(e) =>
                  handleToggleLanguage(e.target.value as Language)
                }
                className="appearance-none bg-transparent pl-2 pr-4 text-xs font-bold text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value="en">🇺🇸 English</option>
                <option value="vi">🇻🇳 Tiếng Việt</option>
              </select>
              <svg
                className="w-3.5 h-3.5 text-slate-500 pointer-events-none absolute right-2"
                fill="none"
                stroke="currentColor"
                strokeWidth={2.2}
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="max-w-5xl w-full mx-auto px-4 py-5 flex-1">
        {route.name === 'routineList' && (
          <RoutineList
            routines={routines}
            lang={lang}
            exercisesMap={exercisesMap}
            onOpenRoutine={(routineId) =>
              setRoute({ name: 'routineDetail', routineId })
            }
            onCreateRoutine={handleCreateRoutine}
            onDeleteRoutine={handleDeleteRoutine}
          />
        )}

        {route.name === 'routineDetail' && (
          <RoutineDetail
            routine={
              routines.find((r) => r.id === route.routineId) ||
              routines[0] || {
                id: 'empty',
                name: 'Routine',
                tag: 'Custom',
                exercises: [],
              }
            }
            lang={lang}
            exercisesMap={exercisesMap}
            allExercises={allExercises}
            onUpdateRoutine={handleUpdateRoutine}
            onOpenExerciseInfo={(exerciseId, routineExIndex) => {
              const activeRoutine =
                routines.find((r) => r.id === route.routineId) || routines[0];
              setRoute({
                name: 'exerciseInfo',
                exerciseId,
                routineId: activeRoutine?.id,
                routineExIndex,
                returnTo: route,
              });
            }}
          />
        )}

        {route.name === 'wikiList' && (
          <ExerciseWiki
            exercises={allExercises}
            lang={lang}
            onSelectExercise={(exerciseId) =>
              setRoute({
                name: 'exerciseInfo',
                exerciseId,
                returnTo: { name: 'wikiList' },
              })
            }
            onAddCustomExercise={handleAddCustomExercise}
          />
        )}

        {route.name === 'exerciseInfo' && exercisesMap[route.exerciseId] && (
          <ExerciseDetail
            exercise={exercisesMap[route.exerciseId]}
            lang={lang}
            showComment={
              Boolean(route.routineId) && route.routineExIndex !== undefined
            }
            comment={
              route.routineId && route.routineExIndex !== undefined
                ? routines.find((r) => r.id === route.routineId)?.exercises[
                    route.routineExIndex
                  ]?.note || ''
                : ''
            }
            onSaveComment={(commentText) =>
              handleSaveRoutineExerciseComment(
                route.routineId,
                route.routineExIndex,
                commentText
              )
            }
            routines={routines}
            onAddExerciseToRoutine={handleAddExerciseToRoutine}
          />
        )}

        {route.name === 'backup' && (
          <BackupSync
            routines={routines}
            lang={lang}
            comments={comments}
            customExercises={customExercises}
            onRestoreBackup={handleRestoreBackup}
            onShowToast={showToast}
          />
        )}
      </main>

      {/* Bottom Sticky Navigation Bar */}
      <nav className="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-xs border-t border-slate-200/80 z-30">
        <div className="max-w-lg mx-auto px-4 py-2 grid grid-cols-3 gap-2">
          <button
            onClick={() => handleSwitchTab('routines')}
            className={`flex flex-col items-center justify-center py-1.5 rounded-2xl text-xs transition cursor-pointer ${
              activeTab === 'routines'
                ? 'text-blue-600 bg-blue-50 font-bold'
                : 'text-slate-500 hover:bg-slate-100 font-semibold'
            }`}
          >
            <svg
              className="w-5 h-5 mb-0.5"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <span>{t.tabWorkouts}</span>
          </button>

          <button
            onClick={() => handleSwitchTab('wiki')}
            className={`flex flex-col items-center justify-center py-1.5 rounded-2xl text-xs transition cursor-pointer ${
              activeTab === 'wiki'
                ? 'text-blue-600 bg-blue-50 font-bold'
                : 'text-slate-500 hover:bg-slate-100 font-semibold'
            }`}
          >
            <svg
              className="w-5 h-5 mb-0.5"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <span>{t.tabWiki}</span>
          </button>

          <button
            onClick={() => handleSwitchTab('backup')}
            className={`flex flex-col items-center justify-center py-1.5 rounded-2xl text-xs transition cursor-pointer ${
              activeTab === 'backup'
                ? 'text-blue-600 bg-blue-50 font-bold'
                : 'text-slate-500 hover:bg-slate-100 font-semibold'
            }`}
          >
            <svg
              className="w-5 h-5 mb-0.5"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
              />
            </svg>
            <span>{t.tabBackup}</span>
          </button>
        </div>
      </nav>
    </div>
  );
};
export default App;
