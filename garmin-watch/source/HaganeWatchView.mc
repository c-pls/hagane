import Toybox.Graphics;
import Toybox.Lang;
import Toybox.WatchUi;

class HaganeWatchView extends WatchUi.View {
    private var _state as HaganeWorkoutState;

    function initialize(state as HaganeWorkoutState) {
        View.initialize();
        _state = state;
    }

    function onShow() as Void {
        // Ensure timer resumes if app regained focus mid-workout
        _state.ensureTimerIfActive();
    }

    function onUpdate(dc as Graphics.Dc) as Void {
        // Clear screen to crisp white for maximum MIP legibility in light mode
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_WHITE);
        dc.clear();

        var st = _state.screenState;
        if (st == HaganeWorkoutState.STATE_ROUTINE_LIST) {
            drawRoutineList(dc);
        } else if (st == HaganeWorkoutState.STATE_ACTIVE_SET) {
            drawActiveSet(dc);
        } else if (st == HaganeWorkoutState.STATE_REST) {
            drawRestTimer(dc);
        } else if (st == HaganeWorkoutState.STATE_PAUSE_MENU) {
            drawPauseMenu(dc);
        } else if (st == HaganeWorkoutState.STATE_DISCARD_CONFIRM) {
            drawDiscardConfirm(dc);
        } else if (st == HaganeWorkoutState.STATE_SUMMARY) {
            drawSummary(dc);
        } else if (st == HaganeWorkoutState.STATE_EXERCISE_PICKER) {
            drawExercisePicker(dc);
        } else if (st == HaganeWorkoutState.STATE_CLOCK_GLANCE) {
            drawClockGlance(dc);
        }
    }

    // -------------------------------------------------------------------------
    // 1. ROUTINE LIST SCREEN
    // -------------------------------------------------------------------------
    private function drawRoutineList(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        // Top Header
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 16, Graphics.FONT_XTINY, "HAGANE", Graphics.TEXT_JUSTIFY_CENTER);

        var routines = _state.routines;
        if (routines.size() == 0) {
            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 78, Graphics.FONT_SMALL, "No Routines Yet", Graphics.TEXT_JUSTIFY_CENTER);

            if (_state.syncStatusText.length() > 0 && !_state.syncStatusText.equals("Forge your steel!")) {
                dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, 114, Graphics.FONT_XTINY, _state.syncStatusText, Graphics.TEXT_JUSTIFY_CENTER);
            } else {
                dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, 114, Graphics.FONT_XTINY, "Sync via Garmin Connect", Graphics.TEXT_JUSTIFY_CENTER);
            }

            dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 152, Graphics.FONT_XTINY, "Press START to Sync", Graphics.TEXT_JUSTIFY_CENTER);
            return;
        }

        var sel = _state.selectedRoutineIdx;
        var total = routines.size();

        // Previous item preview (above center)
        if (sel > 0 && (routines[sel - 1] instanceof Dictionary)) {
            var prev = routines[sel - 1] as Dictionary;
            var prevNmObj = prev.get("n");
            var prevName = (prevNmObj instanceof String) ? (prevNmObj as String) : "Workout";
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 54, Graphics.FONT_XTINY, truncateText(prevName, 22), Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            var bannerText = (_state.syncStatusText.length() > 0) ? _state.syncStatusText : "Forge your steel!";
            dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 54, Graphics.FONT_XTINY, bannerText, Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Selected item card in center
        var curr = routines[sel] as Dictionary;
        var currNmObj  = curr.get("n");
        var currTagObj = curr.get("t");
        var currName   = (currNmObj instanceof String) ? (currNmObj as String) : "Workout";
        var currTag    = (currTagObj instanceof String) ? (currTagObj as String) : "GYM";
        var exListObj  = curr.get("e");
        var exCount    = (exListObj instanceof Array) ? (exListObj as Array).size() : 0;

        // Highlight box
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_LT_GRAY);
        dc.fillRoundedRectangle(20, 84, w - 40, 82, 12);
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawRoundedRectangle(20, 84, w - 40, 82, 12);

        // Tag & Index
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        var badgeStr = "[" + currTag.toUpper() + "]  " + (sel + 1) + "/" + total;
        dc.drawText(cx, 90, Graphics.FONT_XTINY, badgeStr, Graphics.TEXT_JUSTIFY_CENTER);

        // Routine Name
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 112, Graphics.FONT_SMALL, truncateText(currName, 15), Graphics.TEXT_JUSTIFY_CENTER);

        // Exercise Count
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 140, Graphics.FONT_XTINY, exCount + " Exercises", Graphics.TEXT_JUSTIFY_CENTER);

        // Next item preview (below center)
        if (sel + 1 < total && (routines[sel + 1] instanceof Dictionary)) {
            var next = routines[sel + 1] as Dictionary;
            var nextNmObj = next.get("n");
            var nextName = (nextNmObj instanceof String) ? (nextNmObj as String) : "Workout";
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 176, Graphics.FONT_XTINY, truncateText(nextName, 22), Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 176, Graphics.FONT_XTINY, "Hold UP: Sync Routines", Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Bottom prompt anchored relative to screen height
        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, h - 42, Graphics.FONT_XTINY, "START to Begin", Graphics.TEXT_JUSTIFY_CENTER);
    }

    // -------------------------------------------------------------------------
    // 2. ACTIVE SET SCREEN
    // -------------------------------------------------------------------------
    private function drawActiveSet(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        if (_state.currentStepIdx >= _state.steps.size()) {
            return;
        }
        var step = _state.steps[_state.currentStepIdx] as Dictionary;
        var label       = step.get("label") as String;
        var name        = step.get("name") as String;
        var isWarmup    = step.get("isWarmup") as Boolean;
        var setNum      = step.get("setNum") as Number;
        var setTotal    = step.get("setTotal") as Number;
        var weight      = step.get("weight");
        var reps        = step.get("reps") as Number;
        var isWarmupSet = step.get("isWarmupSet") as Boolean;
        var note        = step.get("note") as String;

        var topColor = Graphics.COLOR_DK_BLUE;
        var topText = "EX " + label + "  •  SET " + setNum + "/" + setTotal;
        if (isWarmup || isWarmupSet) {
            topColor = Graphics.COLOR_ORANGE;
            topText = "WARM " + label + " • SET " + setNum + "/" + setTotal;
        } else if (label.length() >= 2) {
            var lastCh = label.substring(label.length() - 1, label.length());
            if (!lastCh.equals("0") && !lastCh.equals("1") && !lastCh.equals("2") &&
                !lastCh.equals("3") && !lastCh.equals("4") && !lastCh.equals("5") &&
                !lastCh.equals("6") && !lastCh.equals("7") && !lastCh.equals("8") &&
                !lastCh.equals("9")) {
                topColor = Graphics.COLOR_PURPLE;
                topText = "SUPER " + label + " • SET " + setNum + "/" + setTotal;
            }
        }

        dc.setColor(topColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 20, Graphics.FONT_XTINY, topText, Graphics.TEXT_JUSTIFY_CENTER);

        // Exercise Name (split into up to 2 lines if long)
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        var lines = splitTwoLines(name, 16);
        if (lines.size() == 1) {
            dc.drawText(cx, 54, Graphics.FONT_SMALL, lines[0] as String, Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.drawText(cx, 43, Graphics.FONT_SMALL, lines[0] as String, Graphics.TEXT_JUSTIFY_CENTER);
            dc.drawText(cx, 69, Graphics.FONT_SMALL, lines[1] as String, Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Divider line
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(34, 102, w - 34, 102);

        // Target Weight x Reps
        var weightStr = formatWeight(weight);
        var targetStr = weightStr + " kg  x  " + reps;
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 110, Graphics.FONT_MEDIUM, targetStr, Graphics.TEXT_JUSTIFY_CENTER);

        // Optional Exercise Note (if present) or Next Exercise hint
        if (note != null && note.length() > 0) {
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 152, Graphics.FONT_XTINY, truncateText(note, 24), Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            var restSec = step.get("restSeconds") as Number;
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            if (restSec <= 0 && (_state.currentStepIdx + 1) < _state.steps.size()) {
                var nextStep = _state.steps[_state.currentStepIdx + 1] as Dictionary;
                var nextLbl = nextStep.get("label") as String;
                var nextNm = nextStep.get("name") as String;
                dc.drawText(cx, 152, Graphics.FONT_XTINY, "Next -> " + nextLbl + " " + truncateText(nextNm, 14), Graphics.TEXT_JUSTIFY_CENTER);
            } else {
                dc.drawText(cx, 152, Graphics.FONT_XTINY, "Rest after set: " + formatMmSs(restSec), Graphics.TEXT_JUSTIFY_CENTER);
            }
        }

        // Bottom Bar: Live HR + Active Set Elapsed Time
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(44, 184, w - 44, 184);

        var hrStr = _state.heartRate > 0 ? (_state.heartRate.toString() + " bpm") : "-- bpm";
        var durStr = formatMmSs(_state.setElapsedSec);

        dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx - 42, 192, Graphics.FONT_XTINY, "HR " + hrStr, Graphics.TEXT_JUSTIFY_CENTER);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx + 46, 192, Graphics.FONT_XTINY, durStr, Graphics.TEXT_JUSTIFY_CENTER);

        // Action Prompt at bottom
        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, h - 40, Graphics.FONT_XTINY, "START: Done Set", Graphics.TEXT_JUSTIFY_CENTER);
    }

    // -------------------------------------------------------------------------
    // 3. REST TIMER SCREEN (Countdown -> Vibrate at 00:00 -> Overtime +00:01)
    // -------------------------------------------------------------------------
    private function drawRestTimer(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;
        var cy = h / 2;

        var target = _state.restTargetSec;
        var elapsed = _state.restElapsedSec;
        var isZeroRest = (target <= 0);
        var isOvertime = (!isZeroRest && elapsed >= target);

        // Draw 360-degree circular progress gauge around the 260x260 bezel
        dc.setPenWidth(8);
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawCircle(cx, cy, cx - 6);

        if (isZeroRest) {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawCircle(cx, cy, cx - 6);
        } else if (!isOvertime && target > 0) {
            var remainingRatio = (target - elapsed).toFloat() / target.toFloat();
            var sweepDeg = (remainingRatio * 360.0).toNumber();
            if (sweepDeg >= 360) {
                dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
                dc.drawCircle(cx, cy, cx - 6);
            } else if (sweepDeg > 0) {
                dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
                var startDeg = 90;
                var endDeg = 90 - sweepDeg;
                if (endDeg < 0) {
                    endDeg += 360;
                }
                dc.drawArc(cx, cy, cx - 6, Graphics.ARC_CLOCKWISE, startDeg, endDeg);
            }
        } else {
            // Overtime ring in bright Amber/Orange
            dc.setColor(Graphics.COLOR_ORANGE, Graphics.COLOR_TRANSPARENT);
            dc.drawCircle(cx, cy, cx - 6);
        }
        dc.setPenWidth(1);

        // Header
        if (isZeroRest) {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 22, Graphics.FONT_XTINY, "GET READY", Graphics.TEXT_JUSTIFY_CENTER);
        } else if (!isOvertime) {
            dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 22, Graphics.FONT_XTINY, "REST TIMER", Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 22, Graphics.FONT_XTINY, "REST COMPLETE!", Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Center Timer / Setup display
        var timerStr = "";
        if (isZeroRest) {
            timerStr = formatMmSs(elapsed);
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        } else if (!isOvertime) {
            timerStr = formatMmSs(target - elapsed);
            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        } else {
            timerStr = "+" + formatMmSs(elapsed - target);
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        }
        dc.drawText(cx, 50, Graphics.FONT_NUMBER_HOT, timerStr, Graphics.TEXT_JUSTIFY_CENTER);

        // UP/DOWN +/-15s & HR sub-row
        var hrStr = _state.heartRate > 0 ? (_state.heartRate.toString() + " bpm") : "-- bpm";
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        if (isZeroRest) {
            dc.drawText(cx, 126, Graphics.FONT_XTINY, "HR " + hrStr, Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.drawText(cx, 126, Graphics.FONT_XTINY, "UP/DN +/-15s  •  HR " + hrStr, Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Divider
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(36, 150, w - 36, 150);

        // NEXT SET PREVIEW
        if (_state.currentStepIdx < _state.steps.size()) {
            var nextStep = _state.steps[_state.currentStepIdx] as Dictionary;
            var nextLabel  = nextStep.get("label") as String;
            var nextName   = nextStep.get("name") as String;
            var nextSetNum = nextStep.get("setNum") as Number;
            var nextSetTot = nextStep.get("setTotal") as Number;
            var nextWeight = formatWeight(nextStep.get("weight"));
            var nextReps   = nextStep.get("reps") as Number;

            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 156, Graphics.FONT_XTINY, "NEXT: [" + nextLabel + "] SET " + nextSetNum + "/" + nextSetTot, Graphics.TEXT_JUSTIFY_CENTER);

            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 176, Graphics.FONT_XTINY, truncateText(nextName, 21), Graphics.TEXT_JUSTIFY_CENTER);

            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 196, Graphics.FONT_XTINY, nextWeight + " kg x " + nextReps, Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Bottom prompt
        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, h - 40, Graphics.FONT_XTINY, "START: Begin Set", Graphics.TEXT_JUSTIFY_CENTER);
    }

    // -------------------------------------------------------------------------
    // 4. PAUSE / OPTIONS MENU (Save, Discard, Resume, etc.)
    // -------------------------------------------------------------------------
    private function drawPauseMenu(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        var isComplete = _state.isWorkoutComplete;

        // Top Status Header
        if (isComplete) {
            dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 18, Graphics.FONT_XTINY, "WORKOUT COMPLETE!", Graphics.TEXT_JUSTIFY_CENTER);

            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
            var durStr = formatMmSs(_state.workoutTotalSec);
            dc.drawText(cx, 34, Graphics.FONT_XTINY, _state.completedSetsCount + " Sets  •  " + durStr, Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 18, Graphics.FONT_XTINY, "WORKOUT PAUSED", Graphics.TEXT_JUSTIFY_CENTER);

            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            var durStr = formatMmSs(_state.workoutTotalSec);
            dc.drawText(cx, 34, Graphics.FONT_XTINY, durStr + "  •  " + _state.completedSetsCount + " Sets", Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Thin divider
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(44, 50, w - 44, 50);

        var items = _state.getPauseMenuItems();
        var sel = _state.pauseMenuIdx;
        var count = items.size();

        // Calculate card layout based on item count
        var itemH = isComplete ? 34 : 22;
        var startY = isComplete ? 64 : 54;
        var spacingY = isComplete ? 40 : 25;

        for (var i = 0; i < count; i += 1) {
            var y = startY + (i * spacingY);
            var itemText = items[i] as String;
            var isSelected = (i == sel);

            if (isSelected) {
                var bgColor = Graphics.COLOR_DK_BLUE;
                if (itemText.equals("Resume") || itemText.equals("Resume Workout")) {
                    bgColor = Graphics.COLOR_DK_GREEN;
                } else if (itemText.equals("Save Workout")) {
                    bgColor = Graphics.COLOR_DK_GREEN;
                } else if (itemText.equals("Discard")) {
                    bgColor = Graphics.COLOR_DK_RED;
                } else if (itemText.equals("Select Exercise")) {
                    bgColor = Graphics.COLOR_DK_BLUE;
                } else {
                    bgColor = Graphics.COLOR_DK_GRAY;
                }

                dc.setColor(bgColor, bgColor);
                dc.fillRoundedRectangle(26, y - 2, w - 52, itemH, 8);
                dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, y + (itemH / 2) - 10, Graphics.FONT_XTINY, itemText, Graphics.TEXT_JUSTIFY_CENTER);
            } else {
                var textColor = Graphics.COLOR_DK_GRAY;
                if (itemText.equals("Save Workout")) {
                    textColor = Graphics.COLOR_DK_GREEN;
                } else if (itemText.equals("Discard")) {
                    textColor = Graphics.COLOR_DK_RED;
                } else if (itemText.equals("Select Exercise")) {
                    textColor = Graphics.COLOR_DK_BLUE;
                }
                dc.setColor(textColor, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, y + (itemH / 2) - 10, Graphics.FONT_XTINY, itemText, Graphics.TEXT_JUSTIFY_CENTER);
            }
        }

        // Bottom guide
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        if (isComplete) {
            dc.drawText(cx, h - 34, Graphics.FONT_XTINY, "START: Select", Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.drawText(cx, h - 40, Graphics.FONT_XTINY, "START: Select", Graphics.TEXT_JUSTIFY_CENTER);
            dc.drawText(cx, h - 24, Graphics.FONT_XTINY, "BACK: Resume", Graphics.TEXT_JUSTIFY_CENTER);
        }
    }

    // -------------------------------------------------------------------------
    // 5. DISCARD CONFIRMATION SCREEN
    // -------------------------------------------------------------------------
    private function drawDiscardConfirm(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 22, Graphics.FONT_XTINY, "DISCARD WORKOUT?", Graphics.TEXT_JUSTIFY_CENTER);

        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 48, Graphics.FONT_XTINY, "All session data", Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(cx, 66, Graphics.FONT_XTINY, "will be deleted.", Graphics.TEXT_JUSTIFY_CENTER);

        var sel = _state.discardConfirmIdx;

        // Button 0: Cancel / Keep (y = 98)
        if (sel == 0) {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_DK_BLUE);
            dc.fillRoundedRectangle(28, 98, w - 56, 34, 10);
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 106, Graphics.FONT_XTINY, "Cancel (Keep)", Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_LT_GRAY);
            dc.drawRoundedRectangle(28, 98, w - 56, 34, 10);
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 106, Graphics.FONT_XTINY, "Cancel (Keep)", Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Button 1: Discard Workout (y = 142)
        if (sel == 1) {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_DK_RED);
            dc.fillRoundedRectangle(28, 142, w - 56, 34, 10);
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 150, Graphics.FONT_XTINY, "Discard Workout", Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_DK_RED);
            dc.drawRoundedRectangle(28, 142, w - 56, 34, 10);
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 150, Graphics.FONT_XTINY, "Discard Workout", Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Prompt
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, h - 36, Graphics.FONT_XTINY, "START to Confirm", Graphics.TEXT_JUSTIFY_CENTER);
    }

    // -------------------------------------------------------------------------
    // 6. WORKOUT SUMMARY SCREEN (Saved to Garmin Connect)
    // -------------------------------------------------------------------------
    private function drawSummary(dc as Graphics.Dc) as Void {
        if (_state.summaryPageIdx == 0) {
            drawSummaryOverview(dc);
        } else {
            drawSummaryExercisePage(dc, _state.summaryPageIdx - 1);
        }
    }

    private function drawSummaryOverview(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 16, Graphics.FONT_XTINY, "WORKOUT SAVED!", Graphics.TEXT_JUSTIFY_CENTER);

        // Routine Name
        if (_state.selectedRoutineIdx < _state.routines.size()) {
            var r = _state.routines[_state.selectedRoutineIdx] as Dictionary;
            var rName = (r.get("n") instanceof String) ? (r.get("n") as String) : "Workout";
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 34, Graphics.FONT_XTINY, truncateText(rName, 18), Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Center card with stats
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_LT_GRAY);
        dc.fillRoundedRectangle(20, 52, w - 40, 114, 12);
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawRoundedRectangle(20, 52, w - 40, 114, 12);

        // Total Time
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 56, Graphics.FONT_MEDIUM, formatMmSs(_state.workoutTotalSec), Graphics.TEXT_JUSTIFY_CENTER);

        // Total Volume
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 90, Graphics.FONT_XTINY, "Volume: " + formatVolume(_state.totalWorkoutVolume) + " kg", Graphics.TEXT_JUSTIFY_CENTER);

        // Sets count & Reps
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 110, Graphics.FONT_XTINY, _state.completedSetsCount + " Sets  •  " + _state.totalWorkoutReps + " Reps", Graphics.TEXT_JUSTIFY_CENTER);

        // HR & Calories subrow
        var hrVal = _state.avgHeartRate > 0 ? _state.avgHeartRate : _state.heartRate;
        var hrStr = hrVal > 0 ? ("Avg HR " + hrVal + " bpm") : "";
        var calStr = _state.calories > 0 ? (_state.calories + " kcal") : "";
        var statStr = hrStr;
        if (hrStr.length() > 0 && calStr.length() > 0) {
            statStr = hrStr + "  •  " + calStr;
        } else if (calStr.length() > 0) {
            statStr = calStr;
        }

        if (statStr.length() > 0) {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 132, Graphics.FONT_XTINY, statStr, Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Work / Rest breakdown
        var workM = _state.totalWorkSec / 60;
        var restM = _state.totalRestSec / 60;
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 174, Graphics.FONT_XTINY, "Work " + workM + "m  •  Rest " + restM + "m", Graphics.TEXT_JUSTIFY_CENTER);

        // Footer navigation prompt
        var exGroups = _state.getExerciseSummaries();
        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        if (exGroups.size() > 0) {
            dc.drawText(cx, h - 38, Graphics.FONT_XTINY, "DOWN: Details (" + exGroups.size() + " Ex)", Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            dc.drawText(cx, h - 38, Graphics.FONT_XTINY, "START: Finish", Graphics.TEXT_JUSTIFY_CENTER);
        }
    }

    private function drawSummaryExercisePage(dc as Graphics.Dc, exIdxZeroBased as Number) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        var exGroups = _state.getExerciseSummaries();
        if (exIdxZeroBased < 0 || exIdxZeroBased >= exGroups.size()) {
            return;
        }

        var grp = exGroups[exIdxZeroBased] as Dictionary;
        var exName = grp.get("name") as String;
        var sets = grp.get("sets") as Array;
        var totalVol = grp.get("totalVol") as Float;

        // Top line 1: Badge [3/6] EXERCISE
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        var pageHeader = "[" + (exIdxZeroBased + 1) + "/" + exGroups.size() + "] EXERCISE";
        dc.drawText(cx, 16, Graphics.FONT_XTINY, pageHeader, Graphics.TEXT_JUSTIFY_CENTER);

        // Top line 2: Full Exercise Name
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 32, Graphics.FONT_XTINY, truncateText(exName, 22), Graphics.TEXT_JUSTIFY_CENTER);

        // Top line 3: Sets count & Exercise Volume
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        var volStr = sets.size() + " " + (sets.size() == 1 ? "Set" : "Sets") + "  •  Vol: " + formatVolume(totalVol) + " kg";
        dc.drawText(cx, 48, Graphics.FONT_XTINY, volStr, Graphics.TEXT_JUSTIFY_CENTER);

        // Thin divider
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(36, 64, w - 36, 64);

        // Dynamic Sets container: clean rows with alternating pills (no huge empty gray space!)
        var numSets = sets.size();
        var maxShow = numSets > 5 ? 5 : numSets;
        var startY = 70;
        var rowH = 22;

        for (var s = 0; s < maxShow; s += 1) {
            var setItem = sets[s] as Dictionary;
            var sNum = setItem.get("setNum") as Number;
            var wKg = formatWeight(setItem.get("weight"));
            var reps = setItem.get("reps") as Number;
            var workSec = setItem.get("workSec") as Number;

            var rowY = startY + (s * rowH);

            if (s % 2 == 0) {
                dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_LT_GRAY);
                dc.fillRoundedRectangle(22, rowY - 2, w - 44, 20, 6);
            }

            var lineStr = "Set " + sNum + ": " + wKg + "kg x " + reps + " (" + formatMmSs(workSec) + ")";
            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, rowY, Graphics.FONT_XTINY, lineStr, Graphics.TEXT_JUSTIFY_CENTER);
        }

        if (numSets > 5) {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, startY + (maxShow * rowH) + 2, Graphics.FONT_XTINY, "+" + (numSets - 5) + " more sets", Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Footer prompt
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, h - 38, Graphics.FONT_XTINY, "UP/DN: Page  •  START: Exit", Graphics.TEXT_JUSTIFY_CENTER);
    }

    // -------------------------------------------------------------------------
    // 7. EXERCISE PICKER SCREEN (Jump to any exercise mid-workout)
    // -------------------------------------------------------------------------
    private function drawExercisePicker(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 16, Graphics.FONT_XTINY, "SELECT EXERCISE", Graphics.TEXT_JUSTIFY_CENTER);

        var exList = _state.getActiveExerciseList();
        var total = exList.size();
        if (total == 0) {
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 110, Graphics.FONT_XTINY, "No Exercises", Graphics.TEXT_JUSTIFY_CENTER);
            return;
        }

        var sel = _state.exercisePickerIdx;
        if (sel < 0) { sel = 0; }
        if (sel >= total) { sel = total - 1; }

        var windowSize = 3;
        var startIdx = sel - 1;
        if (startIdx < 0) {
            startIdx = 0;
        } else if (startIdx + windowSize > total) {
            startIdx = total - windowSize;
            if (startIdx < 0) { startIdx = 0; }
        }

        var startY = 46;
        var itemH = 46;
        var spacingY = 52;

        for (var i = 0; i < windowSize && (startIdx + i) < total; i += 1) {
            var idx = startIdx + i;
            var ex = exList[idx] as Dictionary;
            var label = ex.get("label") as String;
            var name = ex.get("name") as String;
            var cSets = ex.get("completedSets") as Number;
            var tSets = ex.get("totalSets") as Number;
            var isDone = (ex.get("isDone") == true);
            var isSelected = (idx == sel);

            var y = startY + (i * spacingY);

            var skipStr = (tSets == 1) ? "Skipped (1 Set)" : ("Skipped (" + tSets + " Sets)");
            var statusStr = isDone ? (cSets == 0 ? skipStr : ("Done (" + cSets + "/" + tSets + " Sets)")) : (cSets + "/" + tSets + " Sets");

            if (isSelected) {
                dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_DK_BLUE);
                dc.fillRoundedRectangle(20, y, w - 40, itemH, 10);

                dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, y + 4, Graphics.FONT_XTINY, "[" + label + "] " + truncateText(name, 17), Graphics.TEXT_JUSTIFY_CENTER);

                dc.setColor(isDone ? (cSets == 0 ? Graphics.COLOR_ORANGE : Graphics.COLOR_GREEN) : Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, y + 24, Graphics.FONT_XTINY, statusStr, Graphics.TEXT_JUSTIFY_CENTER);
            } else {
                dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_LT_GRAY);
                dc.drawRoundedRectangle(20, y, w - 40, itemH, 10);

                dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, y + 4, Graphics.FONT_XTINY, "[" + label + "] " + truncateText(name, 17), Graphics.TEXT_JUSTIFY_CENTER);

                dc.setColor(isDone ? (cSets == 0 ? Graphics.COLOR_ORANGE : Graphics.COLOR_DK_GREEN) : Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
                dc.drawText(cx, y + 24, Graphics.FONT_XTINY, statusStr, Graphics.TEXT_JUSTIFY_CENTER);
            }
        }

        // Bottom guide
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, h - 36, Graphics.FONT_XTINY, "UP/DN: Scroll  •  START: Pick", Graphics.TEXT_JUSTIFY_CENTER);
    }

    // -------------------------------------------------------------------------
    // 8. CLOCK & SESSION GLANCE SCREEN (Press UP/DOWN in Active Set)
    // -------------------------------------------------------------------------
    private function drawClockGlance(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        // Top Header
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 16, Graphics.FONT_XTINY, "CURRENT TIME", Graphics.TEXT_JUSTIFY_CENTER);

        // Huge Time of Day in Center
        var clock = System.getClockTime();
        var timeStr = Lang.format("$1$:$2$", [clock.hour.format("%02d"), clock.min.format("%02d")]);
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 38, Graphics.FONT_NUMBER_HOT, timeStr, Graphics.TEXT_JUSTIFY_CENTER);

        // Seconds indicator
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 114, Graphics.FONT_XTINY, ":" + clock.sec.format("%02d") + " sec", Graphics.TEXT_JUSTIFY_CENTER);

        // Divider
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(36, 134, w - 36, 134);

        // Active Session Context
        var hrStr = _state.heartRate > 0 ? (_state.heartRate.toString() + " bpm") : "-- bpm";
        var totalDurStr = formatMmSs(_state.workoutTotalSec);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 142, Graphics.FONT_XTINY, "Workout Total: " + totalDurStr, Graphics.TEXT_JUSTIFY_CENTER);

        dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 162, Graphics.FONT_XTINY, "HR " + hrStr + "  •  " + _state.completedSetsCount + " Sets", Graphics.TEXT_JUSTIFY_CENTER);

        if (_state.currentStepIdx < _state.steps.size()) {
            var step = _state.steps[_state.currentStepIdx] as Dictionary;
            var lbl = step.get("label") as String;
            var nm = step.get("name") as String;
            var sNum = step.get("setNum") as Number;
            var sTot = step.get("setTotal") as Number;
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 182, Graphics.FONT_XTINY, "[" + lbl + "] " + truncateText(nm, 14) + " (" + sNum + "/" + sTot + ")", Graphics.TEXT_JUSTIFY_CENTER);
        }

        // Bottom guide
        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, h - 36, Graphics.FONT_XTINY, "UP/DN: Back  •  START: Done", Graphics.TEXT_JUSTIFY_CENTER);
    }

    // -------------------------------------------------------------------------
    // Formatting Helpers
    // -------------------------------------------------------------------------
    private function formatMmSs(totalSeconds as Number) as String {
        if (totalSeconds < 0) {
            totalSeconds = 0;
        }
        var mins = totalSeconds / 60;
        var secs = totalSeconds % 60;
        return mins.format("%02d") + ":" + secs.format("%02d");
    }

    private function formatVolume(val as Float) as String {
        var i = val.toNumber();
        if ((val - i.toFloat()).abs() < 0.05f) {
            return i.toString();
        }
        return val.format("%.1f");
    }

    private function formatWeight(val as Object?) as String {
        if (val == null) {
            return "0";
        }
        if (val instanceof Number) {
            return (val as Number).toString();
        }
        if (val instanceof Float || val instanceof Double) {
            // Convert safely via Numeric.toFloat() without throwing InvalidValueException on Double
            var f = (val as Float or Double).toFloat();
            var i = f.toNumber();
            if ((f - i.toFloat()).abs() < 0.05f) {
                return i.toString();
            }
            return f.format("%.1f");
        }
        return val.toString();
    }

    private function truncateText(str as String, maxLen as Number) as String {
        if (str.length() <= maxLen) {
            return str;
        }
        return str.substring(0, maxLen - 1) + ".";
    }

    private function splitTwoLines(str as String, maxLineLen as Number) as Array {
        if (str.length() <= maxLineLen) {
            return [str];
        }
        var splitIdx = -1;
        for (var i = 0; i < maxLineLen && i < str.length(); i += 1) {
            if (str.substring(i, i + 1).equals(" ")) {
                splitIdx = i;
            }
        }
        if (splitIdx <= 0) {
            var line1 = str.substring(0, maxLineLen);
            var line2 = truncateText(str.substring(maxLineLen, str.length()), maxLineLen);
            return [line1, line2];
        }
        var first = str.substring(0, splitIdx);
        var rest = str.substring(splitIdx + 1, str.length());
        return [first, truncateText(rest, maxLineLen)];
    }
}
