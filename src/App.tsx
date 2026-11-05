import React, { useEffect, useMemo, useRef, useState } from 'react';
import { App as CapApp } from '@capacitor/app';
import { Capacitor } from '@capacitor/core';
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
import {
  initNativeStatusBar,
  triggerHapticLight,
  triggerHapticSelection,
} from './services/native';

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
  const [wikiNavKey, setWikiNavKey] = useState<number>(0);
  const [route, setRoute] = useState<ScreenRoute>(() => {
    const initial = loadRoutines();
    return initial.length > 0
      ? { name: 'routineDetail', routineId: initial[0].id }
      : { name: 'routineList' };
  });

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const toastTimeoutRef = useRef<number | null>(null);
  const lastBackPressRef = useRef<number>(0);

  const t = UI_TEXT[lang];

  // Initialize Native Android / iOS Status Bar
  useEffect(() => {
    initNativeStatusBar();
  }, []);

  // When navigating to the wiki, always begin at the beginning (top) of the page
  useEffect(() => {
    if (route.name === 'wikiList') {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
      const raf = requestAnimationFrame(() => {
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      });
      return () => cancelAnimationFrame(raf);
    }
  }, [route]);

  // Native Android Hardware / Gesture Edge-Swipe Back Button Listener
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    let backListener: { remove: () => void } | null = null;
    CapApp.addListener('backButton', () => {
      if (route.name === 'exerciseInfo') {
        const target = route.returnTo;
        setRoute(target);
        triggerHapticLight();
        if (target.name === 'wikiList') {
          setWikiNavKey((k) => k + 1);
          window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
          document.documentElement.scrollTop = 0;
          document.body.scrollTop = 0;
        }
      } else if (route.name === 'routineDetail') {
        setRoute({ name: 'routineList' });
        setActiveTab('routines');
        triggerHapticLight();
      } else {
        const now = Date.now();
        if (now - lastBackPressRef.current < 2000) {
          CapApp.exitApp();
        } else {
          lastBackPressRef.current = now;
          showToast(
            lang === 'vi'
              ? 'Nhấn quay lại lần nữa để thoát'
              : 'Press back again to exit'
          );
          triggerHapticLight();
        }
      }
    }).then((handle) => {
      backListener = handle;
    });

    return () => {
      if (backListener) backListener.remove();
    };
  }, [route, lang]);

  // In-App Edge Swipe-to-Go-Back Gesture
  const canGoBack =
    route.name === 'exerciseInfo' || route.name === 'routineDetail';

  const handleNavigateBack = () => {
    if (route.name === 'exerciseInfo') {
      const target = route.returnTo;
      setRoute(target);
      triggerHapticLight();
      if (target.name === 'wikiList') {
        setWikiNavKey((k) => k + 1);
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
      }
    } else if (route.name === 'routineDetail') {
      setRoute({ name: 'routineList' });
      setActiveTab('routines');
      triggerHapticLight();
    }
  };

  const touchStartRef = useRef<{ x: number; y: number; time: number } | null>(
    null
  );
  const [swipeProgress, setSwipeProgress] = useState<number | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (!canGoBack) return;
    const touch = e.touches[0];
    if (touch && touch.clientX <= 48) {
      touchStartRef.current = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now(),
      };
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!touchStartRef.current || !canGoBack) return;
    const touch = e.touches[0];
    if (!touch) return;
    const dx = touch.clientX - touchStartRef.current.x;
    const dy = Math.abs(touch.clientY - touchStartRef.current.y);

    if (dy > 45 && dx < 35) {
      touchStartRef.current = null;
      setSwipeProgress(null);
      return;
    }
    if (dx > 0) {
      setSwipeProgress(Math.min(100, Math.round((dx / 120) * 100)));
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!touchStartRef.current || !canGoBack) {
      setSwipeProgress(null);
      return;
    }
    const touch = e.changedTouches[0];
    if (!touch) {
      touchStartRef.current = null;
      setSwipeProgress(null);
      return;
    }
    const dx = touch.clientX - touchStartRef.current.x;
    const dy = Math.abs(touch.clientY - touchStartRef.current.y);
    const dt = Date.now() - touchStartRef.current.time;

    touchStartRef.current = null;
    setSwipeProgress(null);

    if ((dx > 75 || (dx > 40 && dt < 280)) && dy < 60) {
      handleNavigateBack();
    }
  };

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
      setWikiNavKey((k) => k + 1);
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
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
            { weight: 40, reps: 10, type: 'warmup' },
            { weight: 60, reps: 10, type: 'normal' },
            { weight: 60, reps: 10, type: 'normal' },
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
            onClick={handleNavigateBack}
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
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="min-h-screen bg-[#f2f4f7] text-slate-900 flex flex-col pb-20"
    >
      {/* Edge Swipe Back Visual Chevron Indicator */}
      {swipeProgress !== null && swipeProgress > 15 && (
        <div
          style={{
            transform: `translateY(-50%) translateX(${Math.min(
              swipeProgress * 0.35,
              35
            )}px)`,
            opacity: Math.min(1, swipeProgress / 40),
          }}
          className="fixed left-2 top-1/2 z-50 bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center shadow-lg transition-transform pointer-events-none"
        >
          <svg
            className="w-5 h-5 -translate-x-0.5"
            fill="none"
            stroke="currentColor"
            strokeWidth={2.5}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </div>
      )}

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

            {/* 1-Click Flag + EN / VI Language Switcher (No dropdown) */}
            <div
              className="flex items-center bg-slate-100 p-0.5 rounded-full border border-slate-200/80 select-none shadow-2xs"
              role="group"
              aria-label="Language selection"
            >
              <button
                type="button"
                onClick={() => {
                  triggerHapticSelection();
                  handleToggleLanguage('en');
                }}
                aria-pressed={lang === 'en'}
                className={`px-2.5 py-1 rounded-full text-xs font-bold transition flex items-center gap-1 cursor-pointer ${
                  lang === 'en'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-400 hover:text-slate-700'
                }`}
              >
                <span className="text-xs leading-none">🇺🇸</span>
                <span>EN</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  triggerHapticSelection();
                  handleToggleLanguage('vi');
                }}
                aria-pressed={lang === 'vi'}
                className={`px-2.5 py-1 rounded-full text-xs font-bold transition flex items-center gap-1 cursor-pointer ${
                  lang === 'vi'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-400 hover:text-slate-700'
                }`}
              >
                <span className="text-xs leading-none">🇻🇳</span>
                <span>VI</span>
              </button>
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
            key={wikiNavKey}
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

      {/* Bottom Sticky Navigation Bar (Clean 2-Tab: Workouts & Wiki) */}
      <nav className="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-xs border-t border-slate-200/80 z-30">
        <div className="max-w-md mx-auto px-6 py-2 grid grid-cols-2 gap-4">
          <button
            onClick={() => {
              triggerHapticSelection();
              handleSwitchTab('routines');
            }}
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
            onClick={() => {
              triggerHapticSelection();
              handleSwitchTab('wiki');
            }}
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
        </div>
      </nav>
    </div>
  );
};
export default App;
