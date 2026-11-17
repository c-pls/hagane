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
        if (action.equals("Extra Set")) { return "+1 Set"; }
        return action;
    }

    // The menu calls draw() on the icon, so it must be a Drawable, not a raw BitmapResource:
    // on the FR255 a BitmapResource crashes with "Symbol Not Found".
    function iconFor(action as String) as WatchUi.Drawable? {
        try {
            if (action.equals("Resume") || action.equals("Resume Workout")) {
                return new HaganeMenuIcon(Rez.Drawables.IconResume);
            } else if (action.equals("Select Exercise")) {
                return new HaganeMenuIcon(Rez.Drawables.IconExercise);
            } else if (action.equals("Edit Weight")) {
                return new HaganeMenuIcon(Rez.Drawables.IconWeight);
            } else if (action.equals("Previous Set")) {
                return new HaganeMenuIcon(Rez.Drawables.IconUndo);
            } else if (action.equals("Skip Set")) {
                return new HaganeMenuIcon(Rez.Drawables.IconSkip);
            } else if (action.equals("Save Workout")) {
                return new HaganeMenuIcon(Rez.Drawables.IconSave);
            } else if (action.equals("Discard")) {
                return new HaganeMenuIcon(Rez.Drawables.IconDiscard);
            } else if (action.equals("Extra Set")) {
                return new HaganeMenuIcon(Rez.Drawables.IconExtraSet);
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
        // Left-aligned items put the icon beside the label (centred ones stack it above)
        var opts = { :alignment => WatchUi.MenuItem.MENU_ITEM_LABEL_ALIGN_LEFT };
        for (var i = 0; i < items.size(); i += 1) {
            var action = items[i] as String;
            var icon = iconFor(action);
            if (icon != null) {
                menu.addItem(new WatchUi.IconMenuItem(pauseLabel(action), null, action, icon, opts));
            } else {
                menu.addItem(new WatchUi.MenuItem(pauseLabel(action), null, action, opts));
            }
        }
        if (state.pauseMenuIdx >= 0 && state.pauseMenuIdx < items.size()) {
            menu.setFocus(state.pauseMenuIdx);
        }
        WatchUi.pushView(menu, new HaganePauseMenuDelegate(state), WatchUi.SLIDE_IMMEDIATE);
    }

    // Routine preview before starting: Start, then every exercise with its sets (e.g. "3x10 · 40kg")
    function showRoutinePreview(state as HaganeWorkoutState) as Void {
        if (state.selectedRoutineIdx < 0 || state.selectedRoutineIdx >= state.routines.size()) {
            return;
        }
        var routine = state.routines[state.selectedRoutineIdx] as Dictionary;
        var steps = state.buildStepsForRoutine(routine);
        if (steps.size() == 0) {
            state.syncStatusText = "Empty";
            WatchUi.requestUpdate();
            return;
        }
        var nm = routine.get("n");
        var menu = new WatchUi.Menu2({ :title => (nm instanceof String) ? (nm as String) : "Workout" });
        var opts = { :alignment => WatchUi.MenuItem.MENU_ITEM_LABEL_ALIGN_LEFT };
        menu.addItem(new WatchUi.IconMenuItem("Start", null, "start", new HaganeMenuIcon(Rez.Drawables.IconResume), opts));

        // One row per exercise, in workout order (steps are already interleaved for supersets)
        var keys = [] as Array;
        var groups = {} as Dictionary;
        for (var i = 0; i < steps.size(); i += 1) {
            var stp = steps[i] as Dictionary;
            var key = (stp.get("label") as String) + "_" + (stp.get("name") as String);
            if (!groups.hasKey(key)) {
                keys.add(key);
                groups.put(key, [] as Array);
            }
            (groups.get(key) as Array).add(stp);
        }
        for (var k = 0; k < keys.size(); k += 1) {
            var sets = groups.get(keys[k]) as Array;
            var first = sets[0] as Dictionary;
            var label = first.get("label") as String;
            var title = first.get("name") as String;
            // Superset members (3A / 3B) keep their label so the pairing is visible
            var last = label.substring(label.length() - 1, label.length());
            if (last.equals("A") || last.equals("B") || last.equals("C") || last.equals("D")) {
                title = label + " " + title;
            }
            menu.addItem(new WatchUi.MenuItem(title, setsSummary(sets), keys[k], opts));
        }
        WatchUi.pushView(menu, new HaganePreviewDelegate(state, routine.get("id")), WatchUi.SLIDE_IMMEDIATE);
    }

    // "3x10 · 40kg", "3 sets · 40-50kg", "+1 warm-up" left out to keep it short
    function setsSummary(sets as Array) as String {
        var count = 0;
        var reps = -1;
        var sameReps = true;
        var minW = -1.0f;
        var maxW = -1.0f;
        for (var i = 0; i < sets.size(); i += 1) {
            var s = sets[i] as Dictionary;
            if (s.get("isWarmupSet") == true) {
                continue;
            }
            count += 1;
            var r = s.get("reps") as Number;
            if (reps < 0) {
                reps = r;
            } else if (r != reps) {
                sameReps = false;
            }
            var w = HaganeWorkoutState.parseWeightToFloat(s.get("weight"));
            if (minW < 0.0f || w < minW) { minW = w; }
            if (w > maxW) { maxW = w; }
        }
        if (count == 0) {
            // Only warm-up sets: count those instead
            count = sets.size();
            reps = (sets[0] as Dictionary).get("reps") as Number;
            minW = HaganeWorkoutState.parseWeightToFloat((sets[0] as Dictionary).get("weight"));
            maxW = minW;
        }
        var text = sameReps ? (count + "x" + reps) : (count + " sets");
        if (maxW > 0.0f) {
            text += " · " + kg(minW);
            if (maxW > minW) {
                text += "-" + kg(maxW);
            }
            text += "kg";
        }
        return text;
    }

    function kg(w as Float) as String {
        var n = w.toNumber();
        if ((w - n.toFloat()).abs() < 0.05f) {
            return n.toString();
        }
        return w.format("%.1f");
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

// Menu icon that centres its bitmap in the slot the menu gives it, so it lines up with the
// label (a plain WatchUi.Bitmap draws from the top-left corner and sits too high).
class HaganeMenuIcon extends WatchUi.Drawable {
    private var _rezId as ResourceId;

    function initialize(rezId as ResourceId) {
        Drawable.initialize({});
        _rezId = rezId;
    }

    function draw(dc as Graphics.Dc) as Void {
        var bmp = WatchUi.loadResource(_rezId) as WatchUi.BitmapResource;
        dc.drawBitmap((dc.getWidth() - bmp.getWidth()) / 2, (dc.getHeight() - bmp.getHeight()) / 2, bmp);
    }
}

class HaganePreviewDelegate extends WatchUi.Menu2InputDelegate {
    private var _state as HaganeWorkoutState;
    private var _routineId as Object?;

    function initialize(state as HaganeWorkoutState, routineId as Object?) {
        Menu2InputDelegate.initialize();
        _state = state;
        _routineId = routineId;
    }

    function onSelect(item as WatchUi.MenuItem) as Void {
        if (!"start".equals(item.getId())) {
            return; // exercise rows are only for looking
        }
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        // A phone sync while the preview was open may have reordered the list: start this routine
        for (var i = 0; i < _state.routines.size(); i += 1) {
            var rid = (_state.routines[i] as Dictionary).get("id");
            if (rid != null && rid.equals(_routineId)) {
                _state.selectedRoutineIdx = i;
                break;
            }
        }
        _state.startSelectedRoutine();
    }

    function onBack() as Void {
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
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
