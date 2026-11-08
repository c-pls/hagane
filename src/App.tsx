import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { App as CapApp } from '@capacitor/app';
import { Capacitor } from '@capacitor/core';
import {
  ActiveTab,
  Exercise,
  Language,
  Routine,
  RoutineExerciseItem,
  ScreenRoute,
  WorkoutSet,
} from './types/gym';
import {
  translateMuscle,
  translateRoutineText,
  UI_TEXT,
} from './i18n/translations';
import {
  clearStorageCorruptionLock,
  deduplicateRoutineExercises,
  getAllExercises,
  getCorruptBackupRaw,
  getDefaultRestSeconds,
  isStorageCorruptionLocked,
  loadLanguage,
  loadRoutines,
  sanitizeRoutines,
  saveLanguage,
  saveRoutines,
  LAST_SAVED_AT_KEY,
  sortRoutineExercisesBySection,
} from './services/storage';
import { CategoryTagPicker, RoutineList } from './components/RoutineList';
import { RoutineDetail } from './components/RoutineDetail';
import { ExercisePickerView } from './components/ExercisePickerView';
import { ExerciseWiki } from './components/ExerciseWiki';
import { ExerciseDetail } from './components/ExerciseDetail';
import {
  initNativeStatusBar,
} from './services/native';
import {
  autoLoadFromDevice,
  debouncedAutoSaveToDevice,
  flushPendingDeviceSave,
  setDeviceBackupErrorHandler,
  HaganeDeviceBackup,
} from './services/deviceStorage';
import {
  debouncedUpdateGarminWatchCache,
  flushGarminWatchCache,
  setGarminSyncStatusHandler,
} from './services/garminSync';

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>(() => loadLanguage());
  const [routines, setRoutines] = useState<Routine[]>(() =>
    loadRoutines().map((r) => ({
      ...r,
      exercises: sortRoutineExercisesBySection(
        deduplicateRoutineExercises(r.exercises)
      ),
    }))
  );
  const routinesRef = useRef(routines);
  useEffect(() => {
    routinesRef.current = routines;
  }, [routines]);

  const [isCorruptLocked, setIsCorruptLocked] = useState<boolean>(() =>
    isStorageCorruptionLocked()
  );
  const [showCorruptModal, setShowCorruptModal] = useState<boolean>(false);
  const [pendingBackupRestore, setPendingBackupRestore] =
    useState<HaganeDeviceBackup | null>(null);

  const [activeTab, setActiveTab] = useState<ActiveTab>('routines');
  const [wikiSearch, setWikiSearch] = useState<string>('');
  const [wikiMuscleFilter, setWikiMuscleFilter] = useState<string>('All');
  const [wikiEquipmentFilter, setWikiEquipmentFilter] = useState<string>('All');
  const wikiScrollPosRef = useRef<number>(0);
  const [route, setRoute] = useState<ScreenRoute>({ name: 'routineList' });
  const [deviceBackupError, setDeviceBackupError] = useState(false);
  const [routineVersion, setRoutineVersion] = useState(0);
  const isRestoringRef = useRef(false);
  const hasDiscardedDraftRef = useRef(false);

  useEffect(() => {
    setDeviceBackupErrorHandler((hasError) => {
      setDeviceBackupError(hasError);
    });
    return () => setDeviceBackupErrorHandler(null);
  }, []);

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const toastTimeoutRef = useRef<number | null>(null);
  const toastQueueRef = useRef<{ msg: string; durationMs: number }[]>([]);
  const isToastActiveRef = useRef(false);
  const activeToastMsgRef = useRef<string | null>(null);
  const lastBackPressRef = useRef<number>(0);
  const routineScrollPosRef = useRef<number>(0);
  const routineListScrollPosRef = useRef<number>(0);
  const scrollTimersRef = useRef<number[]>([]);

  const clearScrollTimers = () => {
    scrollTimersRef.current.forEach((id) => clearTimeout(id));
    scrollTimersRef.current = [];
  };

  const restoreScrollPosition = (targetY = 0) => {
    clearScrollTimers();
    const applyScroll = () => {
      window.scrollTo({ top: targetY, left: 0, behavior: 'instant' });
      document.documentElement.scrollTop = targetY;
      document.body.scrollTop = targetY;
    };
    applyScroll();
    requestAnimationFrame(applyScroll);
    const t1 = window.setTimeout(applyScroll, 30);
    const t2 = window.setTimeout(applyScroll, 80);
    scrollTimersRef.current.push(t1, t2);
  };

  const restoreRoutineScroll = (savedY?: number) =>
    restoreScrollPosition(savedY ?? routineScrollPosRef.current ?? 0);

  const restoreRoutineListScroll = (savedY?: number) =>
    restoreScrollPosition(savedY ?? routineListScrollPosRef.current ?? 0);

  const restoreWikiScroll = (savedY?: number) =>
    restoreScrollPosition(savedY ?? wikiScrollPosRef.current ?? 0);

  const restorePickerScroll = (savedY?: number) =>
    restoreScrollPosition(savedY ?? 0);

  // Routine Edit Mode & Title/Category editing
  const [isRoutineEditMode, setIsRoutineEditMode] = useState<boolean>(false);
  const [isEditingRoutineTitle, setIsEditingRoutineTitle] =
    useState<boolean>(false);
  const [routineTitleDraft, setRoutineTitleDraft] = useState<string>('');
  const [routineTagDraft, setRoutineTagDraft] = useState<string>('');

  useEffect(() => {
    if (route.name === 'routineDetail') {
      if (route.initialEditMode !== undefined) {
        setIsRoutineEditMode(route.initialEditMode);
      }
    } else if (route.name === 'routineList' || route.name === 'wikiList') {
      setIsRoutineEditMode(false);
      setIsEditingRoutineTitle(false);
    } else {
      setIsEditingRoutineTitle(false);
    }
  }, [route]);

  const handleSaveRoutineTitle = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (route.name !== 'routineDetail') return;
    const currentRoutines = routinesRef.current || routines;
    const routine = currentRoutines.find((r) => r.id === route.routineId);
    if (!routine) return;
    const trimmedName = routineTitleDraft.trim() || routine.name;
    const trimmedTag = routineTagDraft.trim();
    handleUpdateRoutineMeta(routine.id, trimmedName, trimmedTag);
    setIsEditingRoutineTitle(false);
  };

  const t = UI_TEXT[lang];

  // Initialize Native Android / iOS Status Bar
  useEffect(() => {
    initNativeStatusBar();
  }, []);

  // Auto-restore routines from device Documents storage if freshly installed or reinstalled
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    autoLoadFromDevice()
      .then((backup) => {
        if (backup && backup.isCorrupted) {
          showToast(
            lang === 'vi'
              ? '⚠️ Tệp sao lưu thiết bị bị lỗi định dạng và đã được cách ly an toàn.'
              : '⚠️ Device backup file is corrupted and has been quarantined.'
          );
          return;
        }

        if (backup && Array.isArray(backup.routines)) {
          const localTimestamp = Number(
            localStorage.getItem(LAST_SAVED_AT_KEY) || '0'
          );
          const backupTimestamp = backup.timestamp || 0;

          if (
            routinesRef.current.length === 0 &&
            localTimestamp === 0 &&
            backup.routines.length > 0 &&
            !isStorageCorruptionLocked()
          ) {
            // True fresh install / reinstall with empty local state -> auto-restore immediately
            isRestoringRef.current = true;
            const sanitized = sanitizeRoutines(backup.routines);
            setRoutines(sanitized);
            setRoutineVersion((v) => v + 1);
            const ok = saveRoutines(sanitized);
            const currentLang = loadLanguage();
            if (ok) {
              showToast(
                currentLang === 'vi'
                  ? 'Đã tự động khôi phục giáo án từ bộ nhớ máy'
                  : 'Auto-restored routines from device storage'
              );
            } else {
              showToast(
                currentLang === 'vi'
                  ? 'Lỗi: Không thể lưu giáo án đã khôi phục'
                  : 'Error: Failed to save restored routines'
              );
            }
          } else if (
            backup.routines.length > 0 &&
            (isStorageCorruptionLocked() ||
              (backupTimestamp > 0 && backupTimestamp > localTimestamp))
          ) {
            // Existing local data or corrupt state -> ask user for confirmation before overwriting
            setPendingBackupRestore(backup);
          }
        }
      })
      .catch((err) => {
        console.warn('[Hagane] Device backup check failed:', err);
      });
  }, []);

  // Immediately flush any pending debounced Garmin watch cache or device backup on app pause / background
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        flushGarminWatchCache();
        flushPendingDeviceSave();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('pagehide', handleVisibilityChange);

    let appStateHandle: { remove: () => void } | null = null;
    let isMounted = true;
    if (Capacitor.isNativePlatform()) {
      CapApp.addListener('appStateChange', ({ isActive }) => {
        if (!isActive) {
          flushGarminWatchCache();
          flushPendingDeviceSave();
        }
      }).then((h) => {
        if (!isMounted) h.remove();
        else appStateHandle = h;
      });
    }

    return () => {
      isMounted = false;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('pagehide', handleVisibilityChange);
      if (appStateHandle) appStateHandle.remove();
    };
  }, []);

  // Disable text copying on Mobile only (PC can freely select and copy for debugging)
  useEffect(() => {
    const isMobile =
      Capacitor.isNativePlatform() ||
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      );

    if (isMobile) {
      document.documentElement.classList.add('is-mobile');
      document.body.classList.add('is-mobile');
      if (Capacitor.isNativePlatform()) {
        document.documentElement.classList.add('is-native');
        document.body.classList.add('is-native');
      }

      const handleCopy = (e: ClipboardEvent) => {
        e.preventDefault();
      };

      document.addEventListener('copy', handleCopy);

      return () => {
        document.documentElement.classList.remove('is-mobile');
        document.body.classList.remove('is-mobile');
        document.documentElement.classList.remove('is-native');
        document.body.classList.remove('is-native');
        document.removeEventListener('copy', handleCopy);
      };
    } else {
      document.documentElement.classList.add('is-pc');
      document.body.classList.add('is-pc');

      return () => {
        document.documentElement.classList.remove('is-pc');
        document.body.classList.remove('is-pc');
      };
    }
  }, []);

  // When opening an exercise detail, always begin at the beginning (top) of the page
  useEffect(() => {
    if (route.name === 'exerciseInfo') {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
      const raf = requestAnimationFrame(() => {
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
      });
      return () => cancelAnimationFrame(raf);
    }
  }, [route]);

  // In-App Edge Swipe-to-Go-Back & Back Navigation
  const canGoBack =
    route.name === 'exerciseInfo' ||
    route.name === 'routineDetail' ||
    route.name === 'exercisePicker';

  const lastBackNavigationTimeRef = useRef<number>(0);

  const handleNavigateBack = () => {
    const now = Date.now();
    // Guard against Android hardware/gesture back + web touch event double-firing within 350ms (M6)
    if (now - lastBackNavigationTimeRef.current < 350) {
      return;
    }
    lastBackNavigationTimeRef.current = now;

    if (route.name === 'exerciseInfo') {
      const target = route.returnTo;
      setRoute(target);
      if (target.name === 'routineDetail') {
        const savedY = 'savedScrollY' in target && typeof target.savedScrollY === 'number' ? target.savedScrollY : undefined;
        restoreRoutineScroll(savedY);
      } else if (target.name === 'wikiList') {
        const savedY = 'savedScrollY' in target && typeof target.savedScrollY === 'number' ? target.savedScrollY : undefined;
        restoreWikiScroll(savedY);
      } else if (target.name === 'exercisePicker') {
        const savedY = 'savedScrollY' in target && typeof target.savedScrollY === 'number' ? target.savedScrollY : undefined;
        restorePickerScroll(savedY);
      } else {
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
      }
    } else if (route.name === 'exercisePicker') {
      setRoute({
        name: 'routineDetail',
        routineId: route.routineId,
        initialEditMode: route.fromEditMode ?? false,
      });
      restoreRoutineScroll();
    } else if (route.name === 'routineDetail') {
      setRoute({ name: 'routineList' });
      setActiveTab('routines');
      restoreRoutineListScroll();
    }
  };

  const backHandlerRef = useRef<() => void>(() => {});
  backHandlerRef.current = () => {
    if (canGoBack) {
      handleNavigateBack();
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
      }
    }
  };

  // Native Android Hardware / Gesture Edge-Swipe Back Button Listener (Single registered listener)
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    let handle: { remove: () => void } | null = null;
    let isMounted = true;

    CapApp.addListener('backButton', () => {
      backHandlerRef.current();
    }).then((listenerHandle) => {
      if (!isMounted) {
        listenerHandle.remove();
      } else {
        handle = listenerHandle;
      }
    });

    return () => {
      isMounted = false;
      if (handle) {
        handle.remove();
      }
    };
  }, []);

  const touchStartRef = useRef<{ x: number; y: number; time: number } | null>(
    null
  );
  const [swipeProgress, setSwipeProgress] = useState<number | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    const isAnyModalOpen = Boolean(
      showCorruptModal ||
      pendingBackupRestore ||
      document.querySelector('[role="dialog"]')
    );
    if (!canGoBack || document.body.dataset.dragging === 'true' || isAnyModalOpen) return;
    const target = e.target as HTMLElement | null;
    if (target?.closest('.overflow-x-auto, pre')) return;

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
    if (
      !touchStartRef.current ||
      !canGoBack ||
      document.body.dataset.dragging === 'true'
    ) {
      return;
    }
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
    if (
      !touchStartRef.current ||
      !canGoBack ||
      document.body.dataset.dragging === 'true'
    ) {
      touchStartRef.current = null;
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

  const processToastQueue = () => {
    if (toastQueueRef.current.length === 0) {
      isToastActiveRef.current = false;
      activeToastMsgRef.current = null;
      setToastMessage(null);
      return;
    }
    const next = toastQueueRef.current.shift()!;
    isToastActiveRef.current = true;
    activeToastMsgRef.current = next.msg;
    setToastMessage(next.msg);
    toastTimeoutRef.current = window.setTimeout(() => {
      processToastQueue();
    }, next.durationMs);
  };

  const showToast = (msg: string, durationMs = 1800) => {
    if (!isToastActiveRef.current) {
      isToastActiveRef.current = true;
      activeToastMsgRef.current = msg;
      setToastMessage(msg);
      if (toastTimeoutRef.current) {
        window.clearTimeout(toastTimeoutRef.current);
      }
      toastTimeoutRef.current = window.setTimeout(() => {
        processToastQueue();
      }, durationMs);
    } else {
      if (
        msg !== activeToastMsgRef.current &&
        !toastQueueRef.current.some((item) => item.msg === msg)
      ) {
        if (toastQueueRef.current.length < 5) {
          toastQueueRef.current.push({ msg, durationMs });
        }
      }
    }
  };

  useEffect(() => {
    if (isRestoringRef.current && hasDiscardedDraftRef.current) {
      showToast(
        lang === 'vi'
          ? '⚠️ Bản nháp ghi chú chưa lưu đã bị hủy do khôi phục sao lưu'
          : '⚠️ Unsaved note draft was discarded due to backup restore',
        2200
      );
    }
    isRestoringRef.current = false;
    hasDiscardedDraftRef.current = false;
  }, [routineVersion, lang]);

  const allExercises = useMemo(() => getAllExercises(), []);

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
      restoreRoutineListScroll();
    } else if (tab === 'wiki') {
      setRoute({ name: 'wikiList' });
      restoreWikiScroll();
    }
  };

  const persistRoutines = (
    next: Routine[],
    delayMs = 500
  ) => {
    routinesRef.current = next;
    setRoutines(next);
    const savedOk = saveRoutines(next);
    if (!savedOk) {
      if (isStorageCorruptionLocked()) {
        showToast(
          lang === 'vi'
            ? '⚠️ Chưa lưu vào bộ nhớ! Dữ liệu đang bị khóa cách ly, hãy chọn Khôi phục hoặc Bắt đầu mới.'
            : '⚠️ Not saved! Storage is quarantined. Please Restore or Start Fresh.'
        );
      } else {
        showToast(t.toastSaveError);
      }
    }
    debouncedAutoSaveToDevice(next, delayMs);
  };

  const handleUpdateRoutine = (updated: Routine) => {
    if (isRestoringRef.current) {
      console.warn('[Hagane] Dropped stale routine update during restore');
      hasDiscardedDraftRef.current = true;
      return;
    }
    const cleanedRoutine = {
      ...updated,
      exercises: sortRoutineExercisesBySection(
        deduplicateRoutineExercises(updated.exercises)
      ),
    };
    const currentRoutines = routinesRef.current || routines;
    const next = currentRoutines.map((r) =>
      r.id === cleanedRoutine.id ? cleanedRoutine : r
    );
    persistRoutines(next);
  };

  const handleCreateRoutine = (name: string, tag: string) => {
    const currentRoutines = routinesRef.current || routines;
    let trimmed = name.trim();
    if (!trimmed) {
      trimmed = lang === 'vi' ? 'Buổi tập mới' : 'New Routine';
    }
    const existingNames = new Set(
      currentRoutines.map((r) => r.name.trim().toLowerCase())
    );
    if (existingNames.has(trimmed.toLowerCase())) {
      let counter = 2;
      while (existingNames.has(`${trimmed.toLowerCase()} (${counter})`)) {
        counter += 1;
      }
      trimmed = `${trimmed} (${counter})`;
    }
    const uuid =
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const newRoutine: Routine = {
      id: `routine-${uuid}`,
      name: trimmed,
      tag,
      exercises: [],
    };
    const next = [...currentRoutines, newRoutine];
    persistRoutines(next, 100);
    setRoute({ name: 'routineDetail', routineId: newRoutine.id });
  };

  const handleDeleteRoutine = (routineId: string) => {
    const currentRoutines = routinesRef.current || routines;
    const next = currentRoutines.filter((r) => r.id !== routineId);
    persistRoutines(next, 100);
    showToast(t.toastDeletedRoutine);
  };

  const handleReorderRoutines = (fromIdx: number, toIdx: number) => {
    const currentRoutines = routinesRef.current || routines;
    if (
      fromIdx === toIdx ||
      fromIdx < 0 ||
      toIdx < 0 ||
      fromIdx >= currentRoutines.length ||
      toIdx >= currentRoutines.length
    ) {
      return;
    }
    const next = [...currentRoutines];
    const [moved] = next.splice(fromIdx, 1);
    next.splice(toIdx, 0, moved);
    persistRoutines(next, 100);
  };

  const handleUpdateRoutineMeta = (
    routineId: string,
    name: string,
    tag: string
  ) => {
    const currentRoutines = routinesRef.current || routines;
    let trimmed = name.trim();
    const otherNames = new Set(
      currentRoutines
        .filter((r) => r.id !== routineId)
        .map((r) => r.name.trim().toLowerCase())
    );
    if (otherNames.has(trimmed.toLowerCase())) {
      let counter = 2;
      while (otherNames.has(`${trimmed.toLowerCase()} (${counter})`)) {
        counter += 1;
      }
      trimmed = `${trimmed} (${counter})`;
    }
    const next = currentRoutines.map((r) =>
      r.id === routineId ? { ...r, name: trimmed, tag } : r
    );
    persistRoutines(next, 100);
  };

  const handleSaveRoutineExerciseComment = (
    routineId: string | undefined,
    routineExIndex: number | undefined,
    commentText: string,
    expectedExerciseId?: string
  ) => {
    if (isRestoringRef.current) {
      hasDiscardedDraftRef.current = true;
      return;
    }
    if (!routineId || routineExIndex === undefined) return;
    const currentRoutines = routinesRef.current || routines;
    const targetRoutine = currentRoutines.find((r) => r.id === routineId);
    if (!targetRoutine) return;
    const targetExercise = targetRoutine.exercises[routineExIndex];
    if (!targetExercise) return;
    if (expectedExerciseId && targetExercise.exerciseId !== expectedExerciseId) return;
    const trimmed = commentText.trim();
    if ((targetExercise.note || '').trim() === trimmed) return;
    const nextExercises = targetRoutine.exercises.map((item, idx) =>
      idx === routineExIndex ? { ...item, note: trimmed } : item
    );
    handleUpdateRoutine({ ...targetRoutine, exercises: nextExercises });
    showToast(t.toastSavedNote);
  };

  // Listen for Garmin sync status updates
  useEffect(() => {
    setGarminSyncStatusHandler((info) => {
      if (!info.success && info.message) {
        showToast(
          lang === 'vi'
            ? `⚠️ Đồng bộ Garmin: ${info.message}`
            : `⚠️ Garmin sync: ${info.message}`
        );
      } else if (info.isTrimmed && info.message) {
        showToast(
          lang === 'vi'
            ? `ℹ️ Giới hạn bộ nhớ Garmin: ${info.message}`
            : `ℹ️ Garmin watch memory: ${info.message}`
        );
      }
    });
    return () => {
      setGarminSyncStatusHandler(null);
    };
  }, [lang]);

  const handleClearScrollToIndex = useCallback(() => {
    setRoute((prev) =>
      prev.name === 'routineDetail' && prev.scrollToIndex !== undefined
        ? { ...prev, scrollToIndex: undefined }
        : prev
    );
  }, []);

  // Passively keep the Garmin watch payload cache up to date in the background
  // (debounced 2.5s so typing weights/reps does not spam Bluetooth or SharedPreferences).
  useEffect(() => {
    debouncedUpdateGarminWatchCache(routines, exercisesMap, 2500);
  }, [routines, exercisesMap]);

  const handleAddExerciseToRoutine = (
    routineId: string,
    exerciseId: string,
    asWarmup: boolean = false,
    replacingExIdx: number | null = null
  ): boolean => {
    const currentRoutines = routinesRef.current || routines;
    const targetRoutine = currentRoutines.find((r) => r.id === routineId);
    if (!targetRoutine) return false;

    const ex = exercisesMap[exerciseId];
    const exName = ex && lang === 'vi' && ex.nameVi ? ex.nameVi : ex?.name;

    // Strict duplication prevention: 1 exercise can only appear 1 time in the routine!
    const isAlreadyInRoutine = targetRoutine.exercises.some((item, idx) => {
      if (replacingExIdx !== null && idx === replacingExIdx) return false;
      return item.exerciseId === exerciseId;
    });

    if (isAlreadyInRoutine) {
      showToast(
        lang === 'vi'
          ? `⚠️ "${exName}" đã có trong buổi tập! Không thể thêm trùng lặp.`
          : `⚠️ "${exName}" is already in this routine! Cannot add duplicate.`
      );
      return false;
    }

    if (replacingExIdx !== null && targetRoutine.exercises[replacingExIdx]) {
      const isWarmup = Boolean(targetRoutine.exercises[replacingExIdx].isWarmup);
      const isBodyweight = (ex?.equipment || '').toLowerCase() === 'bodyweight';
      const isCardio = (ex?.category || '').toLowerCase() === 'cardio';
      const defaultWeight = isBodyweight || isCardio ? 0 : 20;
      const defaultSets: WorkoutSet[] = isWarmup
        ? [{ weight: defaultWeight, reps: 15, type: 'warmup' }]
        : [{ weight: defaultWeight, reps: 10, type: 'normal' }];
      const defaultRest = getDefaultRestSeconds(ex, isWarmup);

      const nextExercises = targetRoutine.exercises.map((item, idx) =>
        idx === replacingExIdx
          ? {
              ...item,
              exerciseId,
              isWarmup,
              restSeconds: defaultRest,
              sets: defaultSets,
              note: '', // Clear previous exercise's note explicitly
            }
          : item
      );
      handleUpdateRoutine({ ...targetRoutine, exercises: nextExercises });
      showToast(`${t.pickerTitleSwap}: ${exName}`);
      return true;
    }

    // Default to 1 single set on newly added exercises as requested (0 kg for Bodyweight/Cardio, 20 kg for barbell/etc.).
    const isBodyweight = (ex?.equipment || '').toLowerCase() === 'bodyweight';
    const isCardio = (ex?.category || '').toLowerCase() === 'cardio';
    const defaultWeight = isBodyweight || isCardio ? 0 : 20;
    const defaultSets: WorkoutSet[] = asWarmup
      ? [{ weight: defaultWeight, reps: 15, type: 'warmup' }]
      : [{ weight: defaultWeight, reps: 10, type: 'normal' }];

    const defaultRest = getDefaultRestSeconds(ex, asWarmup);

    const nextExercises: RoutineExerciseItem[] = asWarmup
      ? [
          ...targetRoutine.exercises.filter((e) => e.isWarmup),
          {
            exerciseId,
            isWarmup: true,
            restSeconds: defaultRest,
            note: '',
            sets: defaultSets,
          },
          ...targetRoutine.exercises.filter((e) => !e.isWarmup),
        ]
      : [
          ...targetRoutine.exercises,
          {
            exerciseId,
            isWarmup: false,
            restSeconds: defaultRest,
            note: '',
            sets: defaultSets,
          },
        ];

    handleUpdateRoutine({ ...targetRoutine, exercises: nextExercises });
    showToast(`+ ${exName} → ${targetRoutine.name}`);
    return true;
  };

  // Header Left (Clean — back buttons shown on PC, hidden on mobile for edge-swipe)
  const renderHeaderLeft = () => {
    if (route.name === 'exerciseInfo') {
      const ex = exercisesMap[route.exerciseId];
      const displayName =
        ex && lang === 'vi' && ex.nameVi ? ex.nameVi : ex?.name;
      const backLabel =
        route.returnTo.name === 'exercisePicker' ? t.backToPicker : t.back;
      return (
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          <button
            type="button"
            onClick={handleNavigateBack}
            className="hidden sm:inline-flex items-center px-3 py-1.5 min-h-[44px] rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition cursor-pointer shrink-0"
          >
            {backLabel}
          </button>
          <div className="min-w-0">
            <h1 className="font-bold text-base text-slate-900 leading-tight truncate">
              {displayName || 'Exercise'}
            </h1>
            {ex && (
              <p className="text-xs text-slate-400 font-medium truncate">
                {ex.primaryMuscles.map((m) => translateMuscle(m, lang)).join(', ') ||
                  translateMuscle(ex.category, lang)}
              </p>
            )}
          </div>
        </div>
      );
    }

    if (route.name === 'exercisePicker') {
      return (
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          <button
            type="button"
            onClick={handleNavigateBack}
            className="hidden sm:inline-flex items-center px-3 py-1.5 min-h-[44px] rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition cursor-pointer shrink-0"
          >
            {t.back}
          </button>
          <h1 className="font-bold text-base text-slate-900 leading-tight truncate">
            {route.replacingExIdx !== null
              ? t.pickerTitleSwap
              : route.asWarmup
                ? t.pickerTitleWarmup
                : t.pickerTitleAdd}
          </h1>
        </div>
      );
    }

    if (route.name === 'routineDetail') {
      const routine = routines.find((r) => r.id === route.routineId);
      const routineName = routine
        ? translateRoutineText(routine.name, lang)
        : 'Routine';
      return (
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          <button
            type="button"
            onClick={handleNavigateBack}
            className="hidden sm:inline-flex items-center px-3 py-1.5 min-h-[44px] rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition cursor-pointer shrink-0"
          >
            {t.routinesBack}
          </button>
          <div className="min-w-0">
            {isRoutineEditMode ? (
              <button
                type="button"
                onClick={() => {
                  if (routine) {
                    setRoutineTitleDraft(routine.name);
                    setRoutineTagDraft(routine.tag || '');
                    setIsEditingRoutineTitle(true);
                  }
                }}
                className="text-left group cursor-pointer flex items-center gap-1.5 min-h-[44px]"
              >
                <h1 className="font-bold text-base text-slate-900 group-hover:text-blue-600 transition truncate max-w-[180px] sm:max-w-[240px]">
                  {routineName}
                </h1>
                <span className="text-xs text-blue-600 font-bold shrink-0">
                  ✎
                </span>
              </button>
            ) : (
              <h1 className="font-bold text-base text-slate-900 leading-tight truncate max-w-[200px] sm:max-w-[280px]">
                {routineName}
              </h1>
            )}
            {routine?.tag && (
              <p className="text-xs text-slate-400 font-medium truncate">
                {translateRoutineText(routine.tag, lang)}
              </p>
            )}
          </div>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-xl bg-slate-900 border border-slate-700/60 flex items-center justify-center shadow-xs overflow-hidden shrink-0">
          <svg viewBox="0 0 512 512" className="w-6 h-6" fill="none">
            <rect x="144" y="226" width="224" height="60" rx="8" fill="#3B82F6" />
            <polygon points="98,124 144,78 144,434 98,388" fill="#FFFFFF" />
            <polygon points="144,78 174,108 174,404 144,434" fill="#94A3B8" />
            <polygon points="368,78 338,108 338,404 368,434" fill="#94A3B8" />
            <polygon points="414,124 368,78 368,434 414,388" fill="#FFFFFF" />
          </svg>
        </div>
        <div>
          <h1 className="font-extrabold text-base text-slate-900 tracking-tight leading-none">
            Hagane
          </h1>
          <p className="text-[10px] text-slate-400 font-medium leading-none mt-1">
            Forge your steel
          </p>
        </div>
      </div>
    );
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="min-h-screen bg-[#f2f4f7] text-slate-900 flex flex-col pb-28"
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

      {/* Top Sticky App Bar (Hidden in Exercise Picker for native full-height search) */}
      {route.name === 'exercisePicker' && toastMessage && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 pointer-events-none">
          <span
            role="status"
            aria-live="polite"
            className="px-4 py-2 rounded-full bg-slate-900/90 text-white text-xs font-bold shadow-lg backdrop-blur-xs flex items-center gap-1.5"
          >
            {toastMessage}
          </span>
        </div>
      )}
      {route.name !== 'exercisePicker' && (
        <header className="bg-white/95 backdrop-blur-xs border-b border-slate-200/70 sticky top-0 z-30 pt-safe">
          <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-2">
            {renderHeaderLeft()}

            <div className="flex items-center gap-2 shrink-0">
              {toastMessage && (
                <span
                  role="status"
                  aria-live="polite"
                  className="px-3 py-1 rounded-full bg-emerald-600 text-white text-xs font-bold"
                >
                  {toastMessage}
                </span>
              )}

              {/* Routine Edit Mode Toggle (Option A: Right in the header) */}
              {route.name === 'routineDetail' && (
                <button
                  type="button"
                  onClick={() => {
                    setIsRoutineEditMode(!isRoutineEditMode);
                    setIsEditingRoutineTitle(false);
                  }}
                  className={`px-3.5 py-2 min-h-[44px] flex items-center justify-center rounded-full text-xs font-bold transition shadow-xs cursor-pointer ${
                    isRoutineEditMode
                      ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {isRoutineEditMode ? t.doneEditingBtn : t.editRoutineBtn}
                </button>
              )}

              {/* 1-Click Flag + EN / VI Language Switcher (No dropdown) */}
              <div
                className="flex items-center bg-slate-100 p-0.5 rounded-full border border-slate-200/80 select-none shadow-2xs"
                role="group"
                aria-label={lang === 'vi' ? 'Chọn ngôn ngữ' : 'Language selection'}
              >
                <button
                  type="button"
                  onClick={() => {
                    handleToggleLanguage('en');
                  }}
                  aria-pressed={lang === 'en'}
                  className={`px-3 py-2 min-h-[44px] rounded-full text-xs font-bold transition flex items-center gap-1 cursor-pointer ${
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
                    handleToggleLanguage('vi');
                  }}
                  aria-pressed={lang === 'vi'}
                  className={`px-3 py-2 min-h-[44px] rounded-full text-xs font-bold transition flex items-center gap-1 cursor-pointer ${
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
      )}

      {/* Main Content Container */}
      <main className="max-w-5xl w-full mx-auto px-4 py-5 flex-1 space-y-4">
        {/* Corrupt LocalStorage Recovery Banner (C2) */}
        {isCorruptLocked && (
          <div className="bg-amber-50 border border-amber-300 rounded-[24px] p-4 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="space-y-1">
              <h3 className="font-bold text-sm text-amber-950">
                ⚠️ {t.corruptStorageTitle}
              </h3>
              <p className="text-xs text-amber-800 leading-relaxed">
                {t.corruptStorageDesc}
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0 flex-wrap">
              <button
                type="button"
                onClick={() => setShowCorruptModal(true)}
                className="px-3.5 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-amber-100 hover:bg-amber-200 text-amber-900 border border-amber-300 text-xs font-bold cursor-pointer"
              >
                {lang === 'vi' ? '📋 Xem dữ liệu' : '📋 View Data'}
              </button>
              {pendingBackupRestore && (
                <button
                  type="button"
                  onClick={() => {
                    isRestoringRef.current = true;
                    clearStorageCorruptionLock();
                    setIsCorruptLocked(false);
                    const sanitized = sanitizeRoutines(pendingBackupRestore.routines);
                    setRoutines(sanitized);
                    setRoutineVersion((v) => v + 1);
                    const ok = saveRoutines(sanitized);
                    if (!ok) {
                      showToast(t.toastSaveError || (lang === 'vi' ? 'Không thể lưu giáo án' : 'Failed to save routines'));
                    }
                    setPendingBackupRestore(null);
                  }}
                  className="px-3.5 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer"
                >
                  {t.restoreNowBtn}
                </button>
              )}
              <button
                type="button"
                onClick={() => {
                  const confirmFresh = window.confirm(
                    lang === 'vi'
                      ? 'Bạn có chắc chắn muốn bắt đầu mới? Dữ liệu lỗi trước đó vẫn được lưu an toàn trong bộ nhớ máy.'
                      : 'Are you sure you want to start fresh? The corrupt data is preserved in storage.'
                  );
                  if (!confirmFresh) return;
                  isRestoringRef.current = true;
                  clearStorageCorruptionLock(false);
                  setIsCorruptLocked(false);
                  setRoutineVersion((v) => v + 1);
                  const ok = saveRoutines(routines);
                  if (!ok) {
                    showToast(t.toastSaveError || (lang === 'vi' ? 'Không thể lưu giáo án' : 'Failed to save routines'));
                  }
                }}
                className="px-3.5 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-white hover:bg-amber-100 text-amber-900 border border-amber-300 text-xs font-bold cursor-pointer"
              >
                {t.startFreshBtn}
              </button>
            </div>
          </div>
        )}

        {/* Newer Device Backup Confirmation Prompt (C3) */}
        {!isCorruptLocked && pendingBackupRestore && (
          <div className="bg-blue-50 border border-blue-200 rounded-[24px] p-4 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="space-y-1">
              <h3 className="font-bold text-sm text-blue-950">
                🔄 {t.restoreBackupPromptTitle}
              </h3>
              <p className="text-xs text-blue-800 leading-relaxed">
                {t.restoreBackupPromptDesc}
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => {
                  setPendingBackupRestore(null);
                  // Touch local timestamp so we don't re-prompt on next launch unless backup changes again
                  const ok = saveRoutines(routines);
                  if (!ok) {
                    showToast(t.toastSaveError || (lang === 'vi' ? 'Không thể lưu giáo án' : 'Failed to save routines'));
                  }
                }}
                className="px-3.5 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-bold cursor-pointer"
              >
                {t.keepLocalBtn}
              </button>
              <button
                type="button"
                onClick={() => {
                  isRestoringRef.current = true;
                  const sanitized = sanitizeRoutines(pendingBackupRestore.routines);
                  setRoutines(sanitized);
                  setRoutineVersion((v) => v + 1);
                  const ok = saveRoutines(sanitized);
                  setPendingBackupRestore(null);
                  if (ok) {
                    showToast(
                      lang === 'vi'
                        ? 'Đã khôi phục giáo án từ bộ nhớ máy'
                        : 'Restored routines from device storage'
                    );
                  } else {
                    showToast(t.toastSaveError || (lang === 'vi' ? 'Không thể lưu giáo án' : 'Failed to save routines'));
                  }
                }}
                className="px-3.5 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer"
              >
                {t.restoreNowBtn}
              </button>
            </div>
          </div>
        )}

        {/* Physical Device Backup Write Failure Banner */}
        {deviceBackupError && (
          <div className="bg-amber-50 border border-amber-300 rounded-[24px] p-4 shadow-xs flex items-center justify-between gap-3">
            <div className="space-y-0.5">
              <h3 className="font-bold text-sm text-amber-950">
                ⚠️ {lang === 'vi' ? 'Không thể lưu bản sao lưu thiết bị' : 'Device Backup Write Failed'}
              </h3>
              <p className="text-xs text-amber-800 leading-relaxed">
                {lang === 'vi'
                  ? 'Ứng dụng không thể ghi tệp sao lưu vào bộ nhớ Documents của máy. Hãy kiểm tra quyền truy cập bộ nhớ.'
                  : 'Unable to write backup to device Documents storage. Please check storage permissions.'}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setDeviceBackupError(false)}
              aria-label={lang === 'vi' ? 'Đóng thông báo' : 'Dismiss'}
              className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-full flex items-center justify-center bg-amber-100 hover:bg-amber-200 text-amber-900 text-sm font-bold cursor-pointer shrink-0"
            >
              ✕
            </button>
          </div>
        )}

        {route.name === 'routineList' && (
          <RoutineList
            routines={routines}
            lang={lang}
            exercisesMap={exercisesMap}
            onOpenRoutine={(routineId) => {
              const currentScroll =
                window.scrollY ||
                document.documentElement.scrollTop ||
                document.body.scrollTop ||
                0;
              routineListScrollPosRef.current = currentScroll;
              setRoute({ name: 'routineDetail', routineId });
            }}
            onCreateRoutine={handleCreateRoutine}
            onDeleteRoutine={handleDeleteRoutine}
            onReorderRoutines={handleReorderRoutines}
            onUpdateRoutineMeta={handleUpdateRoutineMeta}
          />
        )}

        {route.name === 'routineDetail' &&
          (() => {
            const activeRoutine = routines.find(
              (r) => r.id === route.routineId
            );
            if (!activeRoutine) {
              return (
                <div className="bg-white rounded-[24px] p-8 text-center shadow-xs space-y-3 border border-slate-100">
                  <p className="font-bold text-base text-slate-900">
                    {t.routineNotFoundTitle}
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setRoute({ name: 'routineList' });
                      restoreRoutineListScroll();
                    }}
                    className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer"
                  >
                    {t.routinesBack}
                  </button>
                </div>
              );
            }
            return (
              <RoutineDetail
                key={`${activeRoutine.id}_${routineVersion}`}
                routine={activeRoutine}
                isEditMode={isRoutineEditMode}
                scrollToIndex={route.scrollToIndex}
                onClearScrollToIndex={handleClearScrollToIndex}
                lang={lang}
                exercisesMap={exercisesMap}
                onUpdateRoutine={handleUpdateRoutine}
                onOpenExerciseInfo={(exerciseId, routineExIndex) => {
                  const currentScroll =
                    window.scrollY ||
                    document.documentElement.scrollTop ||
                    document.body.scrollTop ||
                    0;
                  routineScrollPosRef.current = currentScroll;
                  setRoute({
                    name: 'exerciseInfo',
                    exerciseId,
                    routineId: activeRoutine.id,
                    routineExIndex,
                    returnTo: {
                      ...route,
                      initialEditMode: isRoutineEditMode,
                      savedScrollY: currentScroll,
                    },
                  });
                }}
                onOpenPicker={({ asWarmup, replacingExIdx }) => {
                  const currentScroll =
                    window.scrollY ||
                    document.documentElement.scrollTop ||
                    document.body.scrollTop ||
                    0;
                  routineScrollPosRef.current = currentScroll;
                  setRoute({
                    name: 'exercisePicker',
                    routineId: activeRoutine.id,
                    asWarmup,
                    replacingExIdx,
                    fromEditMode: isRoutineEditMode,
                  });
                }}
              />
            );
          })()}

        {route.name === 'exercisePicker' &&
          (() => {
            const targetRoutine = routines.find(
              (r) => r.id === route.routineId
            );
            if (!targetRoutine) {
              return (
                <div className="bg-white rounded-[24px] p-8 text-center shadow-xs space-y-3 border border-slate-100">
                  <p className="font-bold text-base text-slate-900">
                    {t.routineNotFoundTitle}
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setRoute({ name: 'routineList' });
                      restoreRoutineListScroll();
                    }}
                    className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer"
                  >
                    {t.routinesBack}
                  </button>
                </div>
              );
            }
            return (
              <ExercisePickerView
                routine={targetRoutine}
                asWarmup={route.asWarmup}
                replacingExIdx={route.replacingExIdx}
                lang={lang}
                allExercises={allExercises}
                initialSearch={route.searchQuery || ''}
                initialMuscle={route.muscleFilter || 'All'}
                initialEquipment={route.equipmentFilter || 'All'}
                initialTab={route.pickerTab}
                autoFocusSearch={route.savedScrollY === undefined}
                onBack={() => {
                  setRoute({
                    name: 'routineDetail',
                    routineId: targetRoutine.id,
                    initialEditMode: route.fromEditMode ?? false,
                  });
                  restoreRoutineScroll();
                }}
                onSelectExercise={(exerciseId) => {
                  let scrollIdx = 0;
                  if (route.replacingExIdx !== null) {
                    scrollIdx = route.replacingExIdx;
                  } else if (route.asWarmup) {
                    scrollIdx = (targetRoutine.exercises || []).filter(
                      (e) => e.isWarmup
                    ).length;
                  } else {
                    scrollIdx = (targetRoutine.exercises || []).length;
                  }

                  const success = handleAddExerciseToRoutine(
                    targetRoutine.id,
                    exerciseId,
                    route.asWarmup,
                    route.replacingExIdx
                  );
                  if (success) {
                    setRoute({
                      name: 'routineDetail',
                      routineId: targetRoutine.id,
                      initialEditMode: true,
                      scrollToIndex: scrollIdx,
                    });
                  }
                }}
                onDuplicateWarning={(exName) => {
                  showToast(
                    lang === 'vi'
                      ? `⚠️ "${exName}" đã có trong buổi tập! Không thể thêm trùng lặp.`
                      : `⚠️ "${exName}" is already in this routine! Cannot add duplicate.`
                  );
                }}
                onOpenWiki={(
                  exerciseId,
                  currentSearch,
                  currentMuscle,
                  currentEquipment,
                  currentTab
                ) => {
                  const currentScroll =
                    window.scrollY ||
                    document.documentElement.scrollTop ||
                    document.body.scrollTop ||
                    0;
                  setRoute({
                    name: 'exerciseInfo',
                    exerciseId,
                    routineId: targetRoutine.id,
                    asWarmup: route.asWarmup,
                    replacingExIdx: route.replacingExIdx,
                    returnTo: {
                      name: 'exercisePicker',
                      routineId: targetRoutine.id,
                      asWarmup: route.asWarmup,
                      replacingExIdx: route.replacingExIdx,
                      fromEditMode: route.fromEditMode,
                      searchQuery: currentSearch,
                      muscleFilter: currentMuscle,
                      equipmentFilter: currentEquipment,
                      savedScrollY: currentScroll,
                      pickerTab: currentTab,
                    },
                  });
                }}
              />
            );
          })()}

        {route.name === 'wikiList' && (
          <ExerciseWiki
            exercises={allExercises}
            lang={lang}
            search={wikiSearch}
            onSearchChange={setWikiSearch}
            muscleFilter={wikiMuscleFilter}
            onMuscleFilterChange={setWikiMuscleFilter}
            equipmentFilter={wikiEquipmentFilter}
            onEquipmentFilterChange={setWikiEquipmentFilter}
            onSelectExercise={(exerciseId) => {
              const currentScroll =
                window.scrollY ||
                document.documentElement.scrollTop ||
                document.body.scrollTop ||
                0;
              wikiScrollPosRef.current = currentScroll;
              setRoute({
                name: 'exerciseInfo',
                exerciseId,
                returnTo: { name: 'wikiList', savedScrollY: currentScroll },
              });
            }}
          />
        )}

        {route.name === 'exerciseInfo' &&
          (exercisesMap[route.exerciseId] ? (
            <ExerciseDetail
              key={`${route.exerciseId}_${route.routineId || ''}_${route.routineExIndex ?? ''}_${routineVersion}`}
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
                  commentText,
                  route.exerciseId
                )
              }
              activeRoutineId={
                route.routineExIndex === undefined ? route.routineId : undefined
              }
              asWarmup={route.asWarmup}
              replacingExIdx={route.replacingExIdx}
              allExercises={allExercises}
              onSelectExercise={(newExId) => {
                const currentRoutines = routinesRef.current || routines;
                const currentRoutine = currentRoutines.find(
                  (r) => r.id === route.routineId
                );
                const inferredWarmup =
                  route.asWarmup ??
                  (route.routineExIndex !== undefined
                    ? Boolean(
                        currentRoutine?.exercises[route.routineExIndex]
                          ?.isWarmup
                      )
                    : false);
                const inferredReplacingIdx =
                  route.replacingExIdx !== undefined
                    ? route.replacingExIdx
                    : route.routineExIndex !== undefined
                      ? route.routineExIndex
                      : null;

                setRoute({
                  name: 'exerciseInfo',
                  exerciseId: newExId,
                  routineId: route.routineId,
                  routineExIndex: undefined,
                  asWarmup: inferredWarmup,
                  replacingExIdx: inferredReplacingIdx,
                  returnTo: route,
                });
              }}
              onAddExerciseToRoutine={(
                routineId,
                exerciseId,
                asWarmup,
                replacingExIdx
              ) => {
                const currentRoutines = routinesRef.current || routines;
                const targetRoutine = currentRoutines.find((r) => r.id === routineId);
                let scrollIdx = 0;
                if (replacingExIdx !== null && replacingExIdx !== undefined) {
                  scrollIdx = replacingExIdx;
                } else if (asWarmup) {
                  scrollIdx = (targetRoutine?.exercises || []).filter(
                    (e) => e.isWarmup
                  ).length;
                } else {
                  scrollIdx = (targetRoutine?.exercises || []).length;
                }

                const success = handleAddExerciseToRoutine(
                  routineId,
                  exerciseId,
                  asWarmup,
                  replacingExIdx
                );
                if (success) {
                  setRoute({
                    name: 'routineDetail',
                    routineId,
                    initialEditMode: true,
                    scrollToIndex: scrollIdx,
                  });
                }
              }}
            />
          ) : (
            <div className="bg-white rounded-[24px] p-8 text-center shadow-xs space-y-3 border border-slate-100">
              <p className="font-bold text-base text-slate-900">
                {t.exerciseNotFoundTitle} ({route.exerciseId})
              </p>
              <button
                type="button"
                onClick={handleNavigateBack}
                className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer"
              >
                {t.back}
              </button>
            </div>
          ))}
      </main>

      {/* Edit Routine Name & Category Modal from Routine Detail Header */}
      {route.name === 'routineDetail' && isEditingRoutineTitle && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-routine-header-title"
          className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setIsEditingRoutineTitle(false)}
        >
          <form
            onSubmit={handleSaveRoutineTitle}
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-[24px] p-5 w-full max-w-sm shadow-xl space-y-3.5 border border-slate-100"
          >
            <h3 id="edit-routine-header-title" className="font-bold text-base text-slate-900">
              {t.editRoutineInfoBtn}
            </h3>
            <div className="space-y-3">
              <input
                type="text"
                value={routineTitleDraft}
                onChange={(e) => setRoutineTitleDraft(e.target.value)}
                aria-label={t.routineNamePlaceholder}
                placeholder={t.routineNamePlaceholder}
                autoFocus
                className="w-full rounded-xl bg-slate-100 px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <CategoryTagPicker
                value={routineTagDraft}
                onChange={setRoutineTagDraft}
                lang={lang}
              />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setIsEditingRoutineTitle(false)}
                className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold cursor-pointer"
              >
                {t.cancel}
              </button>
              <button
                type="submit"
                className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer"
              >
                {t.save}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Bottom Sticky Navigation Bar (Hidden when searching in Exercise Picker) */}
      {route.name !== 'exercisePicker' && (
        <nav className="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-xs border-t border-slate-200/80 z-30 pb-safe">
          <div className="max-w-md mx-auto px-6 py-2 grid grid-cols-2 gap-4">
            <button
              onClick={() => {
                handleSwitchTab('routines');
              }}
              aria-current={activeTab === 'routines' ? 'page' : undefined}
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
                handleSwitchTab('wiki');
              }}
              aria-current={activeTab === 'wiki' ? 'page' : undefined}
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
      )}

      {showCorruptModal && (() => {
        const rawRoutines = getCorruptBackupRaw();
        const combinedRaw = rawRoutines
          ? `=== QUARANTINED ROUTINES ===\n${rawRoutines}`
          : '(Empty)';

        return (
          <div
            role="dialog"
            aria-modal="true"
            className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4"
            onClick={() => setShowCorruptModal(false)}
          >
            <div
              className="bg-white rounded-[24px] p-5 w-full max-w-lg shadow-xl space-y-3.5 border border-slate-100 max-h-[85vh] flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between">
                <h3 id="corrupt-modal-title" className="font-bold text-base text-slate-900">
                  {lang === 'vi' ? 'Dữ liệu bộ nhớ lỗi (Quarantine)' : 'Corrupted Storage Data'}
                </h3>
                <button
                  type="button"
                  onClick={() => setShowCorruptModal(false)}
                  aria-label={t.cancel}
                  className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 text-sm font-bold cursor-pointer"
                >
                  ✕
                </button>
              </div>
              <p id="corrupt-modal-desc" className="text-xs text-slate-500">
                {lang === 'vi'
                  ? 'Dưới đây là chuỗi JSON thô được trích xuất từ dữ liệu bị lỗi trước đó. Bạn có thể sao chép để lưu giữ.'
                  : 'Raw JSON payload preserved from corrupted storage. You can copy it to preserve your history.'}
              </p>
              <textarea
                id="corrupt-raw-textarea"
                aria-label={lang === 'vi' ? 'Dữ liệu JSON sao lưu bị lỗi' : 'Corrupted backup JSON payload'}
                aria-labelledby="corrupt-modal-title"
                aria-describedby="corrupt-modal-desc"
                readOnly
                value={combinedRaw}
                className="w-full flex-1 min-h-[220px] rounded-xl bg-slate-50 p-3 text-[11px] font-mono text-slate-800 border border-slate-200 select-all"
              />
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(combinedRaw);
                      showToast(lang === 'vi' ? 'Đã sao chép vào bộ nhớ tạm' : 'Copied to clipboard');
                    } catch {
                      showToast(lang === 'vi' ? 'Không thể tự động sao chép, vui lòng copy thủ công' : 'Could not copy to clipboard');
                    }
                  }}
                  className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold cursor-pointer"
                >
                  {lang === 'vi' ? 'Sao chép JSON' : 'Copy JSON'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCorruptModal(false)}
                  className="px-4 py-2 min-h-[44px] inline-flex items-center justify-center rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold cursor-pointer"
                >
                  {t.cancel}
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};
export default App;
