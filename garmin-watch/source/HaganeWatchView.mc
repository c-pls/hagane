import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.Timer;
import Toybox.WatchUi;

class HaganeWatchView extends WatchUi.View {
    private var _state as HaganeWorkoutState;

    // Scrolling ("marquee") for exercise names that are wider than the screen.
    // One scrolling line per screen; it pauses at the start and the end, then starts over.
    private var _marqueeTimer as Timer.Timer?;
    private var _marqueeText as String = "";
    private var _marqueeOffset as Number = 0;
    private var _marqueeMax as Number = 0;
    private var _marqueePause as Number = 0;
    private var _marqueeAtEnd as Boolean = false;
    private var _marqueeUsed as Boolean = false;
    private static const MARQUEE_STEP_PX = 6;
    private static const MARQUEE_TICK_MS = 150;
    private static const MARQUEE_PAUSE_TICKS = 10;

    function initialize(state as HaganeWorkoutState) {
        View.initialize();
        _state = state;
    }

    function onShow() as Void {
        // Ensure timer resumes if app regained focus mid-workout
        _state.ensureTimerIfActive();
    }

    function onHide() as Void {
        stopMarquee();
    }

    function onUpdate(dc as Graphics.Dc) as Void {
        // Clear screen to crisp white for maximum MIP legibility in light mode
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_WHITE);
        dc.clear();
        _marqueeUsed = false;
        drawScreen(dc);
        // Run the scroll timer only while a name on screen is too long to fit
        if (_marqueeUsed) {
            if (_marqueeTimer == null) {
                _marqueeTimer = new Timer.Timer();
                _marqueeTimer.start(method(:onMarqueeTick), MARQUEE_TICK_MS, true);
            }
        } else {
            stopMarquee();
        }
    }

    private function stopMarquee() as Void {
        if (_marqueeTimer != null) {
            _marqueeTimer.stop();
            _marqueeTimer = null;
        }
    }

    function onMarqueeTick() as Void {
        if (_marqueePause > 0) {
            _marqueePause -= 1;
            if (_marqueePause == 0 && _marqueeAtEnd) {
                // Paused at the end: jump back to the start (and pause there again)
                _marqueeAtEnd = false;
                _marqueeOffset = 0;
                _marqueePause = MARQUEE_PAUSE_TICKS;
                WatchUi.requestUpdate();
            }
            return;
        }
        _marqueeOffset += MARQUEE_STEP_PX;
        if (_marqueeOffset >= _marqueeMax) {
            _marqueeOffset = _marqueeMax;
            _marqueeAtEnd = true;
            _marqueePause = MARQUEE_PAUSE_TICKS;
        }
        WatchUi.requestUpdate();
    }

    // Draws text centred at (cx, y). If it is wider than maxW it scrolls right-to-left inside a
    // maxW-wide window so the whole name can be read.
    private function drawFitText(dc as Graphics.Dc, cx as Number, y as Number, font as Graphics.FontDefinition, text as String, maxW as Number) as Void {
        var tw = dc.getTextWidthInPixels(text, font);
        if (tw <= maxW || _marqueeUsed) {
            if (tw > maxW) {
                // A second long line on the same screen: cut it instead of scrolling two lines
                var t = text;
                while (t.length() > 2 && dc.getTextWidthInPixels(t + ".", font) > maxW) {
                    t = t.substring(0, t.length() - 1);
                }
                dc.drawText(cx, y, font, t + ".", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
                return;
            }
            dc.drawText(cx, y, font, text, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
            return;
        }
        _marqueeUsed = true;
        if (!text.equals(_marqueeText)) {
            _marqueeText = text;
            _marqueeOffset = 0;
            _marqueeAtEnd = false;
            _marqueePause = MARQUEE_PAUSE_TICKS;
        }
        _marqueeMax = tw - maxW;
        if (_marqueeOffset > _marqueeMax) {
            _marqueeOffset = _marqueeMax;
        }
        var fh = dc.getFontHeight(font);
        var left = cx - (maxW / 2);
        dc.setClip(left, y - (fh / 2), maxW, fh);
        dc.drawText(left - _marqueeOffset, y, font, text, Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER);
        dc.clearClip();
    }

    private function drawScreen(dc as Graphics.Dc) as Void {

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
        } else if (st == HaganeWorkoutState.STATE_RESUME_PROMPT) {
            drawResumePrompt(dc);
        } else if (st == HaganeWorkoutState.STATE_EDIT_WEIGHT) {
            drawEditWeight(dc);
        }
    }

    // Weight editor opened from the pause menu (UP/DOWN = +/- 2.5 kg, START = apply)
    private function drawEditWeight(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var cx = w / 2;
        var name = "";
        if (_state.currentStepIdx >= 0 && _state.currentStepIdx < _state.steps.size()) {
            name = (_state.steps[_state.currentStepIdx] as Dictionary).get("name") as String;
        }
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 30, Graphics.FONT_SMALL, "WEIGHT", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        drawFitText(dc, cx, 66, Graphics.FONT_SMALL, name, 196);
        dc.setColor(Graphics.COLOR_ORANGE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 134, Graphics.FONT_NUMBER_HOT, formatWeight(_state.editWeightValue), Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 204, Graphics.FONT_MEDIUM, "kg", Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    // -------------------------------------------------------------------------
    // RESUME PROMPT (shown on launch when an unfinished workout was saved)
    // -------------------------------------------------------------------------
    private function drawResumePrompt(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var cx = w / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 40, Graphics.FONT_SMALL, "RESUME?", cj);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        drawFitText(dc, cx, 84, Graphics.FONT_MEDIUM, _state.resumeRoutineName, 200);

        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 122, Graphics.FONT_SMALL, _state.resumeSetsDone + " sets done", cj);

        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 164, Graphics.FONT_SMALL, "START: Resume", cj);
        dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 198, Graphics.FONT_SMALL, "BACK: Discard", cj);
    }

    // -------------------------------------------------------------------------
    // 1. ROUTINE LIST SCREEN
    // -------------------------------------------------------------------------
    private function drawRoutineList(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var cx = w / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        // Header: latest status (Syncing..., Saved, No phone...) or the app name
        var status = _state.syncStatusText;
        dc.setColor(status.length() > 0 ? Graphics.COLOR_DK_GREEN : Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 34, Graphics.FONT_SMALL, status.length() > 0 ? truncateText(status, 11) : "HAGANE", cj);

        var routines = _state.routines;
        if (routines.size() == 0) {
            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 92, Graphics.FONT_MEDIUM, "No routines", cj);
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 138, Graphics.FONT_SMALL, "Sync via phone", cj);
            dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 186, Graphics.FONT_SMALL, "START: Sync", cj);
            return;
        }

        var sel = _state.selectedRoutineIdx;
        var total = routines.size();

        // Previous routine (above)
        if (sel > 0 && (routines[sel - 1] instanceof Dictionary)) {
            var prev = routines[sel - 1] as Dictionary;
            var prevNmObj = prev.get("n");
            var prevName = (prevNmObj instanceof String) ? (prevNmObj as String) : "Workout";
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 66, Graphics.FONT_SMALL, truncateText(prevName, 15), cj);
        }

        var curr = routines[sel] as Dictionary;
        var currNmObj  = curr.get("n");
        var currName   = (currNmObj instanceof String) ? (currNmObj as String) : "Workout";
        var exListObj  = curr.get("e");
        var exCount    = (exListObj instanceof Array) ? (exListObj as Array).size() : 0;

        // Selected routine card
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_LT_GRAY);
        dc.fillRoundedRectangle(14, 84, w - 28, 92, 14);
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawRoundedRectangle(14, 84, w - 28, 92, 14);

        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 101, Graphics.FONT_SMALL, (sel + 1) + "/" + total + "  " + exCount + " ex", cj);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        drawFitText(dc, cx, 142, Graphics.FONT_MEDIUM, currName, w - 48);

        // Next routine (below)
        if (sel + 1 < total && (routines[sel + 1] instanceof Dictionary)) {
            var next = routines[sel + 1] as Dictionary;
            var nextNmObj = next.get("n");
            var nextName = (nextNmObj instanceof String) ? (nextNmObj as String) : "Workout";
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 200, Graphics.FONT_SMALL, truncateText(nextName, 14), cj);
        }
    }

    // -------------------------------------------------------------------------
    // 2. ACTIVE SET SCREEN
    // -------------------------------------------------------------------------
    private function drawActiveSet(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var cx = w / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

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

        // Header: set counter. Orange = warm-up, purple = superset (letter shown)
        var topColor = Graphics.COLOR_DK_BLUE;
        var topText = "SET " + setNum + "/" + setTotal;
        if (isWarmup || isWarmupSet) {
            topColor = Graphics.COLOR_ORANGE;
            topText = "WARM " + setNum + "/" + setTotal;
        } else if (label.length() >= 2) {
            var lastCh = label.substring(label.length() - 1, label.length());
            if (lastCh.toNumber() == null) {
                topColor = Graphics.COLOR_PURPLE;
                topText = label + "  " + setNum + "/" + setTotal;
            }
        }
        dc.setColor(topColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 30, Graphics.FONT_SMALL, topText, cj);

        // Exercise name: one big line; long names scroll so they can be read in full
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        drawFitText(dc, cx, 66, Graphics.FONT_MEDIUM, name, 200);
        var nameBottom = 86;

        // Weight x reps on one line, as large as fits. Changed values turn orange.
        var weightChanged = (HaganeWorkoutState.parseWeightToFloat(weight) != HaganeWorkoutState.parseWeightToFloat(step.get("plannedWeight")));
        var repsChanged = (reps != step.get("plannedReps"));
        var mainStr = formatWeight(weight) + "kg x " + reps + " reps";
        var mainFont = Graphics.FONT_LARGE;
        if (dc.getTextWidthInPixels(mainStr, mainFont) > w - 24) {
            mainFont = Graphics.FONT_MEDIUM;
        }
        if (dc.getTextWidthInPixels(mainStr, mainFont) > w - 24) {
            mainFont = Graphics.FONT_SMALL;
        }
        var mainY = nameBottom + 24;
        dc.setColor((weightChanged || repsChanged) ? Graphics.COLOR_ORANGE : Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, mainY, mainFont, mainStr, cj);

        // Time of this set right below
        var timerTop = mainY + (dc.getFontHeight(mainFont) / 2) + 2;
        var timerRoom = 206 - timerTop;
        var timerFont = Graphics.FONT_NUMBER_MEDIUM;
        if (dc.getFontHeight(timerFont) > timerRoom) {
            timerFont = Graphics.FONT_NUMBER_MILD;
        }
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, timerTop + (timerRoom / 2), timerFont, formatMmSs(_state.setElapsedSec), cj);

        // Live heart rate, labelled
        var hrStr = _state.heartRate > 0 ? _state.heartRate.toString() : "--";
        dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 228, Graphics.FONT_SMALL, "HR " + hrStr, cj);
    }

    // -------------------------------------------------------------------------
    // 3. REST TIMER SCREEN (Countdown -> Vibrate at 00:00 -> Overtime +00:01)
    // -------------------------------------------------------------------------
    private function drawRestTimer(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;
        var cy = h / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        var target = _state.restTargetSec;
        var elapsed = _state.restElapsedSec;
        var isZeroRest = (target <= 0);
        var isOvertime = (!isZeroRest && elapsed >= target);

        // Circular progress ring around the bezel
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
            dc.setColor(Graphics.COLOR_ORANGE, Graphics.COLOR_TRANSPARENT);
            dc.drawCircle(cx, cy, cx - 6);
        }
        dc.setPenWidth(1);

        // The set that comes next
        var setNum = 0;
        var setTot = 0;
        if (_state.currentStepIdx < _state.steps.size()) {
            var ns = _state.steps[_state.currentStepIdx] as Dictionary;
            setNum = ns.get("setNum") as Number;
            setTot = ns.get("setTotal") as Number;
        }
        var setStr = (setTot > 0) ? ("  " + setNum + "/" + setTot) : "";

        // Header
        if (isZeroRest) {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 32, Graphics.FONT_SMALL, "GET READY", cj);
        } else if (!isOvertime) {
            dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 32, Graphics.FONT_SMALL, "REST" + setStr, cj);
        } else {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 32, Graphics.FONT_SMALL, "GO!" + setStr, cj);
        }

        // Big timer
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
        dc.drawText(cx, 88, Graphics.FONT_NUMBER_HOT, timerStr, cj);

        // Heart rate with the drop from the set's peak
        var hrStr = _state.heartRate > 0 ? _state.heartRate.toString() : "--";
        var recStr = "";
        if (_state.heartRate > 0 && _state.restPeakHr > _state.heartRate) {
            recStr = "  -" + (_state.restPeakHr - _state.heartRate);
        }
        dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 142, Graphics.FONT_SMALL, "HR " + hrStr + recStr, cj);

        // What comes next: exercise, then weight x reps
        if (_state.currentStepIdx < _state.steps.size()) {
            var nextStep = _state.steps[_state.currentStepIdx] as Dictionary;
            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
            drawFitText(dc, cx, 176, Graphics.FONT_SMALL, nextStep.get("name") as String, 210);
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 208, Graphics.FONT_MEDIUM, formatWeight(nextStep.get("weight")) + "kg x " + (nextStep.get("reps") as Number), cj);
        }
    }

    // -------------------------------------------------------------------------
    // 4. PAUSE / OPTIONS MENU (running-style: time of day + icon list)
    // -------------------------------------------------------------------------
    private function drawPauseMenu(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;

        // Dark screen like the native running pause page
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();

        // Red ring marks the paused state
        dc.setColor(Graphics.COLOR_RED, Graphics.COLOR_TRANSPARENT);
        dc.setPenWidth(3);
        dc.drawCircle(cx, h / 2, (w / 2) - 7);
        dc.setPenWidth(1);

        // Current time of day is the only information shown
        var clock = System.getClockTime();
        var timeStr = Lang.format("$1$:$2$", [clock.hour.format("%02d"), clock.min.format("%02d")]);
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 50, Graphics.FONT_NUMBER_MEDIUM, timeStr, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);

        var items = _state.getPauseMenuItems();
        var count = items.size();
        var sel = _state.pauseMenuIdx;

        // Selected item sits in the middle row, its neighbours above and below (wraps around)
        var midY = 154;
        var rowH = 56;
        var barX = w * 13 / 100;
        var iconX = w * 22 / 100;
        var textX = w * 32 / 100;
        var radius = cx - 8;

        for (var r = -1; r <= 1; r += 1) {
            var i = ((sel + r) % count + count) % count;
            var itemText = items[i] as String;
            var isSelected = (r == 0);
            var cy = midY + (r * rowH);

            var color = isSelected ? Graphics.COLOR_WHITE : Graphics.COLOR_LT_GRAY;
            if (itemText.equals("Discard")) {
                color = isSelected ? Graphics.COLOR_RED : Graphics.COLOR_DK_RED;
            }
            dc.setColor(color, Graphics.COLOR_TRANSPARENT);

            if (isSelected) {
                dc.setPenWidth(4);
                dc.drawLine(barX, cy - (rowH / 2) + 6, barX, cy + (rowH / 2) - 6);
                dc.setPenWidth(1);
            }

            drawPauseIcon(dc, itemText, iconX, cy);

            // Largest font whose text still fits inside the round screen on this row
            var label = pauseLabel(itemText);
            var dy = (cy - (h / 2)).abs();
            var rightEdge = cx + Math.sqrt((radius * radius) - (dy * dy)).toNumber() - 6;
            var fnt = Graphics.FONT_LARGE;
            if (textX + dc.getTextWidthInPixels(label, fnt) > rightEdge) {
                fnt = Graphics.FONT_MEDIUM;
            }
            if (textX + dc.getTextWidthInPixels(label, fnt) > rightEdge) {
                fnt = Graphics.FONT_SMALL;
            }
            dc.drawText(textX, cy, fnt, label, Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER);
        }
        dc.setPenWidth(1);
    }

    // Short label shown for each pause menu action (the action strings themselves stay unchanged)
    private function pauseLabel(item as String) as String {
        if (item.equals("Resume Workout")) {
            return "Resume";
        }
        if (item.equals("Save Workout")) {
            return "Save";
        }
        if (item.equals("Previous Set")) {
            return "Undo Set";
        }
        if (item.equals("Select Exercise")) {
            return "Exercise";
        }
        if (item.equals("Edit Weight")) {
            return "Weight";
        }
        return item;
    }

    // 22px glyphs drawn with plain primitives, in the colour currently set on the dc
    private function drawPauseIcon(dc as Graphics.Dc, item as String, x as Number, cy as Number) as Void {
        var s = 26;
        var half = s / 2;
        var left = x - half;
        dc.setPenWidth(1);

        if (item.equals("Resume") || item.equals("Resume Workout")) {
            fillTriangleRight(dc, left + 3, cy, s - 4, half);
        } else if (item.equals("Select Exercise")) {
            dc.fillRectangle(left, cy - 8, s, 3);
            dc.fillRectangle(left, cy - 1, s, 3);
            dc.fillRectangle(left, cy + 6, s, 3);
        } else if (item.equals("Edit Weight")) {
            dc.fillRectangle(left, cy - 2, s, 4);
            dc.fillRectangle(x - 2, cy - half, 4, s);
        } else if (item.equals("Skip Set")) {
            fillTriangleRight(dc, left, cy, s - 6, half);
            dc.fillRectangle(left + s - 4, cy - half, 4, s);
        } else if (item.equals("Previous Set")) {
            dc.fillRectangle(left, cy - half, 4, s);
            fillTriangleLeft(dc, left + 6, cy, s - 6, half);
        } else if (item.equals("Save Workout")) {
            // download arrow: stem, head and tray
            dc.fillRectangle(x - 2, cy - half, 4, half - 1);
            fillTriangleDown(dc, x, cy - 2, 8, 9);
            dc.fillRectangle(left, cy + half - 3, s, 3);
        } else if (item.equals("Discard")) {
            dc.setPenWidth(3);
            dc.drawLine(left + 2, cy - 8, left + s - 2, cy + 8);
            dc.drawLine(left + 2, cy + 8, left + s - 2, cy - 8);
            dc.setPenWidth(1);
        } else {
            dc.fillCircle(x, cy, 5);
        }
    }

    // Triangle pointing right: flat edge at x, apex at x + wd
    private function fillTriangleRight(dc as Graphics.Dc, x as Number, cy as Number, wd as Number, hh as Number) as Void {
        for (var i = 0; i < wd; i += 1) {
            var e = hh * (wd - i) / wd;
            dc.drawLine(x + i, cy - e, x + i, cy + e);
        }
    }

    // Triangle pointing left: apex at x, flat edge at x + wd
    private function fillTriangleLeft(dc as Graphics.Dc, x as Number, cy as Number, wd as Number, hh as Number) as Void {
        for (var i = 0; i < wd; i += 1) {
            var e = hh * i / wd;
            dc.drawLine(x + i, cy - e, x + i, cy + e);
        }
    }

    // Triangle pointing down: flat edge at top y, apex at y + ht
    private function fillTriangleDown(dc as Graphics.Dc, cx as Number, y as Number, hw as Number, ht as Number) as Void {
        for (var j = 0; j < ht; j += 1) {
            var e = hw * (ht - j) / ht;
            dc.drawLine(cx - e, y + j, cx + e, y + j);
        }
    }

    // -------------------------------------------------------------------------
    // 5. DISCARD CONFIRMATION SCREEN
    // -------------------------------------------------------------------------
    private function drawDiscardConfirm(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var cx = w / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 44, Graphics.FONT_MEDIUM, "DISCARD?", cj);

        var sel = _state.discardConfirmIdx;

        // Button 0: keep the workout
        if (sel == 0) {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_DK_BLUE);
            dc.fillRoundedRectangle(24, 80, w - 48, 56, 14);
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        } else {
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_DK_GRAY);
            dc.drawRoundedRectangle(24, 80, w - 48, 56, 14);
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        }
        dc.drawText(cx, 108, Graphics.FONT_MEDIUM, "Keep", cj);

        // Button 1: discard
        if (sel == 1) {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_DK_RED);
            dc.fillRoundedRectangle(24, 148, w - 48, 56, 14);
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        } else {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_DK_RED);
            dc.drawRoundedRectangle(24, 148, w - 48, 56, 14);
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
        }
        dc.drawText(cx, 176, Graphics.FONT_MEDIUM, "Discard", cj);
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
        var cx = w / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 30, Graphics.FONT_SMALL, "SAVED", cj);

        // Total time
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 76, Graphics.FONT_NUMBER_MEDIUM, formatMmSs(_state.workoutTotalSec), cj);

        // Volume
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 122, Graphics.FONT_MEDIUM, formatVolume(_state.totalWorkoutVolume) + " kg", cj);

        // Sets and reps
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 156, Graphics.FONT_SMALL, _state.completedSetsCount + " sets  " + _state.totalWorkoutReps + " reps", cj);

        // Heart rate and calories
        var hrVal = _state.avgHeartRate > 0 ? _state.avgHeartRate : _state.heartRate;
        var statStr = "";
        if (hrVal > 0) {
            statStr = hrVal + " bpm";
        }
        if (_state.calories > 0) {
            statStr = (statStr.length() > 0) ? (statStr + "  " + _state.calories + " kcal") : (_state.calories + " kcal");
        }
        if (statStr.length() > 0) {
            dc.setColor(Graphics.COLOR_DK_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 186, Graphics.FONT_SMALL, statStr, cj);
        }

        // Footer
        var exGroups = _state.getExerciseSummaries();
        dc.setColor(Graphics.COLOR_DK_GREEN, Graphics.COLOR_TRANSPARENT);
        if (exGroups.size() > 0) {
            dc.drawText(cx, 220, Graphics.FONT_SMALL, "DOWN: more", cj);
        } else {
            dc.drawText(cx, 220, Graphics.FONT_SMALL, "START: done", cj);
        }
    }

    private function drawSummaryExercisePage(dc as Graphics.Dc, exIdxZeroBased as Number) as Void {
        var w = dc.getWidth();
        var cx = w / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        var exGroups = _state.getExerciseSummaries();
        if (exIdxZeroBased < 0 || exIdxZeroBased >= exGroups.size()) {
            return;
        }

        var grp = exGroups[exIdxZeroBased] as Dictionary;
        var exName = grp.get("name") as String;
        var sets = grp.get("sets") as Array;
        var totalVol = grp.get("totalVol") as Float;

        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 28, Graphics.FONT_SMALL, (exIdxZeroBased + 1) + "/" + exGroups.size(), cj);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
        drawFitText(dc, cx, 60, Graphics.FONT_SMALL, exName, 190);

        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 90, Graphics.FONT_SMALL, sets.size() + " sets  " + formatVolume(totalVol) + " kg", cj);

        // One row per set (the last row becomes "+N more" when there are too many)
        var numSets = sets.size();
        var maxRows = 4;
        var shown = (numSets > maxRows) ? (maxRows - 1) : numSets;
        for (var s = 0; s < shown; s += 1) {
            var setItem = sets[s] as Dictionary;
            var sNum = setItem.get("setNum") as Number;
            var wKg = formatWeight(setItem.get("weight"));
            var reps = setItem.get("reps") as Number;
            var rowY = 122 + (s * 30);
            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, rowY, Graphics.FONT_SMALL, sNum + "  " + wKg + "kg x " + reps, cj);
        }
        if (numSets > maxRows) {
            dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 122 + (shown * 30), Graphics.FONT_SMALL, "+" + (numSets - shown) + " more", cj);
        }
    }

    // -------------------------------------------------------------------------
    // 7. EXERCISE PICKER SCREEN (Jump to any exercise mid-workout)
    // -------------------------------------------------------------------------
    private function drawExercisePicker(dc as Graphics.Dc) as Void {
        var w = dc.getWidth();
        var cx = w / 2;
        var cj = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 28, Graphics.FONT_SMALL, "EXERCISE", cj);

        var exList = _state.getActiveExerciseList();
        var total = exList.size();
        if (total == 0) {
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 130, Graphics.FONT_SMALL, "No exercises", cj);
            return;
        }

        var sel = _state.exercisePickerIdx;
        if (sel < 0) { sel = 0; }
        if (sel >= total) { sel = total - 1; }

        // Previous exercise (above)
        if (sel > 0) {
            var pex = exList[sel - 1] as Dictionary;
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 72, Graphics.FONT_SMALL, truncateText(pex.get("name") as String, 14), cj);
        }

        // Selected exercise card
        var ex = exList[sel] as Dictionary;
        var cSets = ex.get("completedSets") as Number;
        var tSets = ex.get("totalSets") as Number;
        var isDone = (ex.get("isDone") == true);
        var statusStr = cSets + "/" + tSets + " sets";
        var statusColor = Graphics.COLOR_LT_GRAY;
        if (isDone) {
            if (cSets == 0) {
                statusStr = "Skipped";
                statusColor = Graphics.COLOR_ORANGE;
            } else {
                statusStr = "Done " + cSets + "/" + tSets;
                statusColor = Graphics.COLOR_GREEN;
            }
        }
        dc.setColor(Graphics.COLOR_DK_BLUE, Graphics.COLOR_DK_BLUE);
        dc.fillRoundedRectangle(12, 92, w - 24, 76, 14);
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        drawFitText(dc, cx, 118, Graphics.FONT_MEDIUM, ex.get("name") as String, w - 44);
        dc.setColor(statusColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, 150, Graphics.FONT_SMALL, statusStr, cj);

        // Next exercise (below)
        if (sel + 1 < total) {
            var nex = exList[sel + 1] as Dictionary;
            dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
            dc.drawText(cx, 196, Graphics.FONT_SMALL, truncateText(nex.get("name") as String, 14), cj);
        }
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

}
