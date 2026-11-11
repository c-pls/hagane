import Toybox.Graphics;
import Toybox.Lang;
import Toybox.System;
import Toybox.Timer;
import Toybox.WatchUi;

// Menus and dialogs built from Garmin's own UI components, so they look and behave
// like the built-in activity apps (same fonts, list style, scrolling and "Discard?" dialog).
module HaganeNativeUi {

    var laterTimer as Timer.Timer? = null;

    function pauseLabel(action as String) as String {
        if (action.equals("Resume Workout")) { return "Resume"; }
        if (action.equals("Save Workout")) { return "Save"; }
        if (action.equals("Previous Set")) { return "Undo Set"; }
        if (action.equals("Select Exercise")) { return "Exercise"; }
        if (action.equals("Edit Weight")) { return "Weight"; }
        return action;
    }

    function iconFor(action as String) as WatchUi.BitmapResource? {
        try {
            if (action.equals("Resume") || action.equals("Resume Workout")) {
                return WatchUi.loadResource(Rez.Drawables.IconResume) as WatchUi.BitmapResource;
            } else if (action.equals("Select Exercise")) {
                return WatchUi.loadResource(Rez.Drawables.IconExercise) as WatchUi.BitmapResource;
            } else if (action.equals("Edit Weight")) {
                return WatchUi.loadResource(Rez.Drawables.IconWeight) as WatchUi.BitmapResource;
            } else if (action.equals("Previous Set")) {
                return WatchUi.loadResource(Rez.Drawables.IconUndo) as WatchUi.BitmapResource;
            } else if (action.equals("Skip Set")) {
                return WatchUi.loadResource(Rez.Drawables.IconSkip) as WatchUi.BitmapResource;
            } else if (action.equals("Save Workout")) {
                return WatchUi.loadResource(Rez.Drawables.IconSave) as WatchUi.BitmapResource;
            } else if (action.equals("Discard")) {
                return WatchUi.loadResource(Rez.Drawables.IconDiscard) as WatchUi.BitmapResource;
            }
        } catch (ex) {}
        return null;
    }

    // Pause / workout-complete menu. Title shows the time of day.
    function showPauseMenu(state as HaganeWorkoutState) as Void {
        var clock = System.getClockTime();
        var title = clock.hour.format("%02d") + ":" + clock.min.format("%02d");
        var menu = new WatchUi.Menu2({ :title => title });
        var items = state.getPauseMenuItems();
        for (var i = 0; i < items.size(); i += 1) {
            var action = items[i] as String;
            var icon = iconFor(action);
            if (icon != null) {
                menu.addItem(new WatchUi.IconMenuItem(pauseLabel(action), null, action, icon, null));
            } else {
                menu.addItem(new WatchUi.MenuItem(pauseLabel(action), null, action, null));
            }
        }
        if (state.pauseMenuIdx >= 0 && state.pauseMenuIdx < items.size()) {
            menu.setFocus(state.pauseMenuIdx);
        }
        WatchUi.pushView(menu, new HaganePauseMenuDelegate(state), WatchUi.SLIDE_IMMEDIATE);
    }

    // Exercise list: name plus how many sets are done
    function showExercisePicker(state as HaganeWorkoutState) as Void {
        var menu = new WatchUi.Menu2({ :title => "Exercise" });
        var list = state.getActiveExerciseList();
        for (var i = 0; i < list.size(); i += 1) {
            var ex = list[i] as Dictionary;
            var cSets = ex.get("completedSets") as Number;
            var tSets = ex.get("totalSets") as Number;
            var status = cSets + "/" + tSets + " sets";
            if (ex.get("isDone") == true) {
                status = (cSets == 0) ? "Skipped" : ("Done " + cSets + "/" + tSets);
            }
            menu.addItem(new WatchUi.MenuItem(ex.get("name") as String, status, i, null));
        }
        if (state.exercisePickerIdx >= 0 && state.exercisePickerIdx < list.size()) {
            menu.setFocus(state.exercisePickerIdx);
        }
        WatchUi.pushView(menu, new HaganePickerDelegate(state), WatchUi.SLIDE_IMMEDIATE);
    }

    // Garmin's own "Discard?" dialog, shown on top of the pause menu
    function showDiscardConfirm(state as HaganeWorkoutState) as Void {
        WatchUi.pushView(new WatchUi.Confirmation("Discard?"), new HaganeDiscardDelegate(state), WatchUi.SLIDE_IMMEDIATE);
    }

    // Run a callback shortly after the current input event (a dialog closes itself after it answers)
    function runLater(cb as Method() as Void) as Void {
        if (laterTimer != null) {
            laterTimer.stop();
        }
        laterTimer = new Timer.Timer();
        laterTimer.start(cb, 60, false);
    }
}

class HaganePauseMenuDelegate extends WatchUi.Menu2InputDelegate {
    private var _state as HaganeWorkoutState;

    function initialize(state as HaganeWorkoutState) {
        Menu2InputDelegate.initialize();
        _state = state;
    }

    function onSelect(item as WatchUi.MenuItem) as Void {
        var action = item.getId() as String;
        if (action.equals("Discard")) {
            // The dialog sits on top of this menu: answering "no" simply returns here
            HaganeNativeUi.showDiscardConfirm(_state);
            return;
        }
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        _state.runPauseAction(action);
    }

    function onBack() as Void {
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        _state.onPauseMenuBack();
    }
}

class HaganePickerDelegate extends WatchUi.Menu2InputDelegate {
    private var _state as HaganeWorkoutState;

    function initialize(state as HaganeWorkoutState) {
        Menu2InputDelegate.initialize();
        _state = state;
    }

    function onSelect(item as WatchUi.MenuItem) as Void {
        var idx = item.getId() as Number;
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        _state.exercisePickerIdx = idx;
        _state.jumpToExercise(idx);
    }

    function onBack() as Void {
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        _state.onPickerBack();
    }
}

class HaganeDiscardDelegate extends WatchUi.ConfirmationDelegate {
    private var _state as HaganeWorkoutState;

    function initialize(state as HaganeWorkoutState) {
        ConfirmationDelegate.initialize();
        _state = state;
    }

    function onResponse(response as WatchUi.Confirm) as Boolean {
        if (response == WatchUi.CONFIRM_YES) {
            // The dialog closes itself after this returns; then close the pause menu and discard
            HaganeNativeUi.runLater(method(:finishDiscard));
        }
        return true;
    }

    function finishDiscard() as Void {
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        _state.discardWorkout();
    }
}
