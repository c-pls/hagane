import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class HaganeWatchDelegate extends WatchUi.BehaviorDelegate {
    private var _state as HaganeWorkoutState;
    private var _lastSelectTickMs as Number = 0;

    function initialize(state as HaganeWorkoutState) {
        BehaviorDelegate.initialize();
        _state = state;
    }

    // Physical START / ENTER button (top-right button on Forerunner 255 Music)
    function onSelect() as Boolean {
        // 500ms debounce guard to prevent accidental double-presses from skipping a set
        var nowMs = System.getTimer();
        if (_lastSelectTickMs > 0 && (nowMs - _lastSelectTickMs).abs() < 500) {
            return true;
        }
        _lastSelectTickMs = nowMs;

        var st = _state.screenState;
        if (st == HaganeWorkoutState.STATE_ROUTINE_LIST) {
            if (_state.routines.size() == 0) {
                // No routines yet -> request sync from phone via Garmin Connect
                _state.requestSyncFromPhone(false);
                return true;
            }
            return _state.startSelectedRoutine();
        } else if (st == HaganeWorkoutState.STATE_ACTIVE_SET) {
            _state.completeCurrentSet();
            return true;
        } else if (st == HaganeWorkoutState.STATE_REST) {
            // Works both BEFORE 00:00 (early set start) and AFTER 00:00 (overtime)
            _state.startNextSetFromRest();
            return true;
        } else if (st == HaganeWorkoutState.STATE_PAUSE_MENU) {
            _state.executePauseMenuAction();
            return true;
        } else if (st == HaganeWorkoutState.STATE_DISCARD_CONFIRM) {
            if (_state.discardConfirmIdx == 0) {
                // Cancel discard -> return back to pause menu
                _state.screenState = HaganeWorkoutState.STATE_PAUSE_MENU;
                WatchUi.requestUpdate();
            } else {
                // Confirm discard -> delete FIT recording and return to routine list
                _state.discardWorkout();
            }
            return true;
        } else if (st == HaganeWorkoutState.STATE_SUMMARY) {
            _state.screenState = HaganeWorkoutState.STATE_ROUTINE_LIST;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_EXERCISE_PICKER) {
            _state.jumpToExercise(_state.exercisePickerIdx);
            return true;
        } else if (st == HaganeWorkoutState.STATE_CLOCK_GLANCE) {
            // In Clock Glance, pressing START completes the set just like in Active Set
            _state.completeCurrentSet();
            return true;
        } else if (st == HaganeWorkoutState.STATE_RESUME_PROMPT) {
            _state.resumeSavedWorkout();
            return true;
        } else if (st == HaganeWorkoutState.STATE_EDIT_WEIGHT) {
            _state.confirmEditWeight();
            return true;
        }
        return false;
    }

    // Physical BACK / LAP button (bottom-right button on Forerunner 255 Music)
    function onBack() as Boolean {
        var st = _state.screenState;
        if (st == HaganeWorkoutState.STATE_ROUTINE_LIST) {
            // Allow normal exit back to watch face / Activities list
            return false;
        } else if (st == HaganeWorkoutState.STATE_ACTIVE_SET || st == HaganeWorkoutState.STATE_REST) {
            _state.openPauseMenu();
            return true;
        } else if (st == HaganeWorkoutState.STATE_CLOCK_GLANCE) {
            // Return back to active set
            _state.screenState = HaganeWorkoutState.STATE_ACTIVE_SET;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_EDIT_WEIGHT) {
            _state.screenState = HaganeWorkoutState.STATE_PAUSE_MENU;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_EXERCISE_PICKER) {
            if (_state.pickerReturnState != HaganeWorkoutState.STATE_PAUSE_MENU) {
                // Opened directly from a set / rest screen: go straight back to it
                _state.screenState = _state.pickerReturnState;
                _state.pickerReturnState = HaganeWorkoutState.STATE_PAUSE_MENU;
                WatchUi.requestUpdate();
                return true;
            }
            // Return back to pause menu; if all steps are completed, preserve isWorkoutComplete
            if (_state.areAllStepsCompleted()) {
                _state.isWorkoutComplete = true;
            }
            _state.screenState = HaganeWorkoutState.STATE_PAUSE_MENU;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_PAUSE_MENU) {
            if (_state.isWorkoutComplete || _state.areAllStepsCompleted()) {
                // On complete screen, BACK should not resume straight to a completed set.
                // Open the exercise picker so the lifter can pick an exercise to do extra sets for.
                _state.openExercisePicker();
                return true;
            }
            _state.resumeFromPauseMenu();
            return true;
        } else if (st == HaganeWorkoutState.STATE_DISCARD_CONFIRM) {
            // Cancel discard and return to pause menu
            _state.screenState = HaganeWorkoutState.STATE_PAUSE_MENU;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_SUMMARY) {
            _state.screenState = HaganeWorkoutState.STATE_ROUTINE_LIST;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_RESUME_PROMPT) {
            _state.discardSavedWorkout();
            return true;
        }
        return false;
    }

    // Physical UP button (middle-left button on Forerunner 255 Music)
    function onPreviousPage() as Boolean {
        var st = _state.screenState;
        if (st == HaganeWorkoutState.STATE_ROUTINE_LIST) {
            if (_state.routines.size() > 0) {
                _state.selectedRoutineIdx = (_state.selectedRoutineIdx - 1 + _state.routines.size()) % _state.routines.size();
                WatchUi.requestUpdate();
            }
            return true;
        } else if (st == HaganeWorkoutState.STATE_ACTIVE_SET) {
            // UP = one more rep than planned
            _state.adjustReps(1);
            return true;
        } else if (st == HaganeWorkoutState.STATE_CLOCK_GLANCE) {
            // Return back to active set
            _state.screenState = HaganeWorkoutState.STATE_ACTIVE_SET;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_EDIT_WEIGHT) {
            _state.adjustEditWeight(2.5f);
            return true;
        } else if (st == HaganeWorkoutState.STATE_EXERCISE_PICKER) {
            var count = _state.getActiveExerciseList().size();
            if (count > 0) {
                _state.exercisePickerIdx = (_state.exercisePickerIdx - 1 + count) % count;
                WatchUi.requestUpdate();
            }
            return true;
        } else if (st == HaganeWorkoutState.STATE_REST) {
            // Add +15 seconds to current rest timer
            _state.adjustRestTarget(15);
            return true;
        } else if (st == HaganeWorkoutState.STATE_PAUSE_MENU) {
            var count = _state.getPauseMenuItems().size();
            _state.pauseMenuIdx = (_state.pauseMenuIdx - 1 + count) % count;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_DISCARD_CONFIRM) {
            _state.discardConfirmIdx = (_state.discardConfirmIdx == 0) ? 1 : 0;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_SUMMARY) {
            var exGroups = _state.getExerciseSummaries();
            var maxPages = 1 + exGroups.size();
            _state.summaryPageIdx = (_state.summaryPageIdx - 1 + maxPages) % maxPages;
            WatchUi.requestUpdate();
            return true;
        }
        return false;
    }

    // Physical DOWN button (bottom-left button on Forerunner 255 Music)
    function onNextPage() as Boolean {
        var st = _state.screenState;
        if (st == HaganeWorkoutState.STATE_ROUTINE_LIST) {
            if (_state.routines.size() > 0) {
                _state.selectedRoutineIdx = (_state.selectedRoutineIdx + 1) % _state.routines.size();
                WatchUi.requestUpdate();
            }
            return true;
        } else if (st == HaganeWorkoutState.STATE_ACTIVE_SET) {
            // DOWN = one rep fewer than planned
            _state.adjustReps(-1);
            return true;
        } else if (st == HaganeWorkoutState.STATE_CLOCK_GLANCE) {
            // Return back to active set
            _state.screenState = HaganeWorkoutState.STATE_ACTIVE_SET;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_EDIT_WEIGHT) {
            _state.adjustEditWeight(-2.5f);
            return true;
        } else if (st == HaganeWorkoutState.STATE_EXERCISE_PICKER) {
            var count = _state.getActiveExerciseList().size();
            if (count > 0) {
                _state.exercisePickerIdx = (_state.exercisePickerIdx + 1) % count;
                WatchUi.requestUpdate();
            }
            return true;
        } else if (st == HaganeWorkoutState.STATE_REST) {
            // Subtract 15 seconds from current rest timer
            _state.adjustRestTarget(-15);
            return true;
        } else if (st == HaganeWorkoutState.STATE_PAUSE_MENU) {
            var count = _state.getPauseMenuItems().size();
            _state.pauseMenuIdx = (_state.pauseMenuIdx + 1) % count;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_DISCARD_CONFIRM) {
            _state.discardConfirmIdx = (_state.discardConfirmIdx == 0) ? 1 : 0;
            WatchUi.requestUpdate();
            return true;
        } else if (st == HaganeWorkoutState.STATE_SUMMARY) {
            var exGroups = _state.getExerciseSummaries();
            var maxPages = 1 + exGroups.size();
            _state.summaryPageIdx = (_state.summaryPageIdx + 1) % maxPages;
            WatchUi.requestUpdate();
            return true;
        }
        return false;
    }

    // Long-press UP (Menu) -> on Routine List triggers Sync from Phone; during a set or rest opens the exercise picker
    function onMenu() as Boolean {
        var st = _state.screenState;
        if (st == HaganeWorkoutState.STATE_ROUTINE_LIST) {
            _state.requestSyncFromPhone(false);
            return true;
        } else if (st == HaganeWorkoutState.STATE_ACTIVE_SET || st == HaganeWorkoutState.STATE_REST) {
            _state.openExercisePickerDirect();
            return true;
        }
        return false;
    }
}
