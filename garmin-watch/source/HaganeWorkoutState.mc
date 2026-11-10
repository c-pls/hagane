import Toybox.Activity;
import Toybox.ActivityRecording;
import Toybox.Application.Storage;
import Toybox.Attention;
import Toybox.Communications;
import Toybox.FitContributor;
import Toybox.Lang;
import Toybox.Sensor;
import Toybox.Time;
import Toybox.Timer;
import Toybox.WatchUi;

class HaganeSyncConnectListener extends Communications.ConnectionListener {
    private var _state as HaganeWorkoutState;

    function initialize(state as HaganeWorkoutState) {
        ConnectionListener.initialize();
        _state = state;
    }

    function onComplete() as Void {
        // Request transmitted to phone; now awaiting onPhoneMessage callback
    }

    function onError() as Void {
        _state.onSyncRequestFailed();
    }
}

class HaganeWorkoutState {
    // Screens / States
    public static const STATE_ROUTINE_LIST     = 0;
    public static const STATE_ACTIVE_SET       = 1;
    public static const STATE_REST             = 2;
    public static const STATE_PAUSE_MENU       = 3;
    public static const STATE_SUMMARY          = 4;
    public static const STATE_DISCARD_CONFIRM  = 5;
    public static const STATE_EXERCISE_PICKER  = 6;
    public static const STATE_CLOCK_GLANCE     = 7;
    public static const STATE_RESUME_PROMPT    = 8;
    public static const STATE_EDIT_WEIGHT      = 9;

    public var screenState as Number = STATE_ROUTINE_LIST;
    public var previousWorkoutState as Number = STATE_ACTIVE_SET;
    public var exercisePickerIdx as Number = 0;

    // Synced routines array
    public var routines as Array = [];
    public var selectedRoutineIdx as Number = 0;
    // Routine id captured when a workout starts, so a phone sync that reorders or shrinks the
    // list mid-workout can never change which routine the completion report refers to.
    public var activeRoutineId as String = "";
    // Routines received from the phone while a workout was running; applied once it ends.
    public var pendingRoutines as Array? = null;
    // Step indices of sets left unfinished when the lifter jumped to another exercise (machine busy).
    // The workout returns to them once the detour exercise is finished.
    public var returnStack as Array = [];
    // Where BACK goes from the exercise picker: the pause menu, or the screen it was opened from
    public var pickerReturnState as Number = STATE_PAUSE_MENU;
    // Highest heart rate during the set just finished, and the same value kept during rest so the
    // rest screen can show how far the heart rate has recovered
    public var setPeakHr as Number = 0;
    public var editWeightValue as Float = 0.0f;
    public var restPeakHr as Number = 0;

    // Resume-after-close: saved progress offered on launch
    public var resumeRoutineName as String = "";
    public var resumeSetsDone as Number = 0;
    private var _progress as Dictionary? = null;
    public static const PROGRESS_KEY = "hagane_progress";

    // Flattened execution steps for the active routine
    public var steps as Array = [];
    public var currentStepIdx as Number = 0;

    // Timers (in seconds)
    public var setElapsedSec as Number = 0;
    public var restTargetSec as Number = 90;
    public var restElapsedSec as Number = 0;
    public var hasVibratedForRest as Boolean = false;
    public var workoutTotalSec as Number = 0;
    public var completedSetsCount as Number = 0;

    // Pause menu & completion state
    public var pauseMenuIdx as Number = 0;
    public var isWorkoutComplete as Boolean = false;
    public var discardConfirmIdx as Number = 0;

    public static const PAUSE_MENU_ITEMS = [
        "Resume",
        "Select Exercise",
        "Edit Weight",
        "Previous Set",
        "Skip Set",
        "Save Workout",
        "Discard"
    ];

    public static const COMPLETE_MENU_ITEMS = [
        "Save Workout",
        "Discard",
        "Resume Workout"
    ];

    public function getPauseMenuItems() as Array {
        if (isWorkoutComplete) {
            return COMPLETE_MENU_ITEMS;
        }
        return PAUSE_MENU_ITEMS;
    }

    // FIT Contributor Field IDs (must match resources/fitfields.xml)
    public static const FIT_FIELD_LAP_EXERCISE     = 0;
    public static const FIT_FIELD_LAP_SET          = 1;
    public static const FIT_FIELD_LAP_WEIGHT       = 2;
    public static const FIT_FIELD_LAP_REPS         = 3;
    public static const FIT_FIELD_LAP_VOLUME       = 4;
    public static const FIT_FIELD_LAP_WORK_TIME    = 5;
    public static const FIT_FIELD_LAP_REST_TIME    = 6;
    public static const FIT_FIELD_SESSION_VOLUME   = 7;
    public static const FIT_FIELD_SESSION_REPS     = 8;
    public static const FIT_FIELD_SESSION_SETS     = 9;
    public static const FIT_FIELD_SESSION_WORK_TIME = 10;
    public static const FIT_FIELD_SESSION_REST_TIME = 11;
    public static const FIT_FIELD_RECORD_WEIGHT    = 12;

    // FIT Contributor Field handles
    private var _fitLapExercise as FitContributor.Field?;
    private var _fitLapSet as FitContributor.Field?;
    private var _fitLapWeight as FitContributor.Field?;
    private var _fitLapReps as FitContributor.Field?;
    private var _fitLapVolume as FitContributor.Field?;
    private var _fitLapWorkTime as FitContributor.Field?;
    private var _fitLapRestTime as FitContributor.Field?;

    private var _fitSessionVolume as FitContributor.Field?;
    private var _fitSessionReps as FitContributor.Field?;
    private var _fitSessionSets as FitContributor.Field?;
    private var _fitSessionWorkTime as FitContributor.Field?;
    private var _fitSessionRestTime as FitContributor.Field?;

    private var _fitRecordWeight as FitContributor.Field?;

    // Running workout metrics
    public var totalWorkoutVolume as Float = 0.0f;
    public var totalWorkoutReps as Number = 0;
    public var totalWorkSec as Number = 0;
    public var totalRestSec as Number = 0;
    public var lastRestElapsedSec as Number = 0;

    // Completed sets log for Watch Summary breakdown and detail review
    public var completedLog as Array = [];
    public var summaryPageIdx as Number = 0;

    // Live Heart Rate, Calories & FIT Activity Recording Session
    public var heartRate as Number = 0;
    public var avgHeartRate as Number = 0;
    public var maxHeartRate as Number = 0;
    public var calories as Number = 0;
    public var syncStatusText as String = "Forge your steel!";
    private var _session as ActivityRecording.Session?;
    private var _timer as Timer.Timer?;

    function initialize() {
        try {
            Sensor.setEnabledSensors([Sensor.SENSOR_HEARTRATE]);
            Sensor.enableSensorEvents(method(:onSensorEvent));
        } catch (ex) {
            // Ignore on simulator if sensor unsupported
        }
    }

    function onSensorEvent(sensorInfo as Sensor.Info) as Void {
        if (sensorInfo != null && sensorInfo.heartRate != null) {
            heartRate = sensorInfo.heartRate as Number;
        }
    }

    // Safely validates and normalizes routines array from storage or phone sync
    public static function sanitizeRoutines(raw as Array) as Array {
        var clean = [] as Array;
        for (var i = 0; i < raw.size(); i += 1) {
            var r = raw[i];
            if (r != null && (r instanceof Dictionary)) {
                var rDict = r as Dictionary;
                var exArr = rDict.get("e");
                if (exArr != null && (exArr instanceof Array)) {
                    clean.add(rDict);
                }
            }
        }
        return clean;
    }

    // -------------------------------------------------------------------------
    // Progress persistence: lets a workout be resumed if the app is closed or killed mid-session
    // -------------------------------------------------------------------------
    function saveProgress() as Void {
        if (activeRoutineId.length() == 0 || steps.size() == 0) {
            return;
        }
        var done = [] as Array;
        var skipped = [] as Array;
        for (var i = 0; i < steps.size(); i += 1) {
            var stp = steps[i] as Dictionary;
            if (stp.get("completed") == true) {
                done.add(i);
            } else if (stp.get("skipped") == true) {
                skipped.add(i);
            }
        }
        var log = [] as Array;
        for (var j = 0; j < completedLog.size(); j += 1) {
            var e = completedLog[j] as Dictionary;
            log.add([e.get("stepIdx"), e.get("weight"), e.get("reps"), e.get("workSec"), e.get("restSec")]);
        }
        try {
            Storage.setValue(PROGRESS_KEY, {
                "rid"  => activeRoutineId,
                "t"    => Time.now().value(),
                "cur"  => currentStepIdx,
                "done" => done,
                "skip" => skipped,
                "log"  => log,
                "tot"  => workoutTotalSec,
                "work" => totalWorkSec,
                "rest" => totalRestSec
            });
        } catch (ex) {
            // Storage unavailable: resuming simply will not be offered
        }
    }

    function clearProgress() as Void {
        try {
            Storage.deleteValue(PROGRESS_KEY);
        } catch (ex) {}
    }

    private function findRoutineIndexById(rid as String) as Number {
        for (var i = 0; i < routines.size(); i += 1) {
            var r = routines[i] as Dictionary;
            var idObj = r.get("id");
            if ((idObj instanceof String) && (idObj as String).equals(rid)) {
                return i;
            }
        }
        return -1;
    }

    // Called on launch: offers to resume if a recent unfinished workout was saved
    function checkForSavedWorkout() as Void {
        try {
            var saved = Storage.getValue(PROGRESS_KEY);
            if (saved == null || !(saved instanceof Dictionary)) {
                return;
            }
            var d = saved as Dictionary;
            var ridObj = d.get("rid");
            var tObj = d.get("t");
            var doneObj = d.get("done");
            if (!(ridObj instanceof String) || !(tObj instanceof Number) || !(doneObj instanceof Array)) {
                clearProgress();
                return;
            }
            var ageSec = Time.now().value() - (tObj as Number);
            var idx = findRoutineIndexById(ridObj as String);
            var doneCount = (doneObj as Array).size();
            if (ageSec < 0 || ageSec > 6 * 3600 || idx < 0 || doneCount == 0) {
                clearProgress();
                return;
            }
            var nmObj = (routines[idx] as Dictionary).get("n");
            resumeRoutineName = (nmObj instanceof String) ? (nmObj as String) : "Workout";
            resumeSetsDone = doneCount;
            _progress = d;
            screenState = STATE_RESUME_PROMPT;
        } catch (ex) {
            clearProgress();
        }
    }

    function discardSavedWorkout() as Void {
        _progress = null;
        clearProgress();
        screenState = STATE_ROUTINE_LIST;
        WatchUi.requestUpdate();
    }

    // START on the resume prompt: rebuild the workout where it left off and start a new FIT session
    function resumeSavedWorkout() as Void {
        var saved = _progress;
        _progress = null;
        if (saved == null) {
            discardSavedWorkout();
            return;
        }
        var prog = saved as Dictionary;
        try {
            var ridObj = prog.get("rid");
            var idx = (ridObj instanceof String) ? findRoutineIndexById(ridObj as String) : -1;
            if (idx < 0) {
                discardSavedWorkout();
                return;
            }
            selectedRoutineIdx = idx;
            var routine = routines[idx] as Dictionary;
            steps = buildStepsForRoutine(routine);
            if (steps.size() == 0) {
                discardSavedWorkout();
                return;
            }

            currentStepIdx = 0;
            setElapsedSec = 0;
            restElapsedSec = 0;
            hasVibratedForRest = false;
            workoutTotalSec = 0;
            completedSetsCount = 0;
            totalWorkoutVolume = 0.0f;
            totalWorkoutReps = 0;
            totalWorkSec = 0;
            totalRestSec = 0;
            lastRestElapsedSec = 0;
            completedLog = [];
            summaryPageIdx = 0;
            avgHeartRate = 0;
            maxHeartRate = 0;
            calories = 0;
            isWorkoutComplete = false;
            discardConfirmIdx = 0;
            returnStack = [];
            setPeakHr = 0;
            restPeakHr = 0;
            activeRoutineId = ridObj as String;

            // Completed / skipped flags
            var doneObj = prog.get("done");
            if (doneObj instanceof Array) {
                var da = doneObj as Array;
                for (var k = 0; k < da.size(); k += 1) {
                    var di = da[k];
                    if ((di instanceof Number) && (di as Number) >= 0 && (di as Number) < steps.size()) {
                        (steps[di as Number] as Dictionary).put("completed", true);
                    }
                }
            }
            var skipObj = prog.get("skip");
            if (skipObj instanceof Array) {
                var sa = skipObj as Array;
                for (var q = 0; q < sa.size(); q += 1) {
                    var si = sa[q];
                    if ((si instanceof Number) && (si as Number) >= 0 && (si as Number) < steps.size()) {
                        (steps[si as Number] as Dictionary).put("skipped", true);
                    }
                }
            }

            // Rebuild the per-set log and totals for the summary pages
            var logObj = prog.get("log");
            if (logObj instanceof Array) {
                var la = logObj as Array;
                for (var m = 0; m < la.size(); m += 1) {
                    var row = la[m];
                    if (!(row instanceof Array)) {
                        continue;
                    }
                    var ra = row as Array;
                    if (ra.size() < 5 || !(ra[0] instanceof Number) || !(ra[2] instanceof Number)) {
                        continue;
                    }
                    var sIdx = ra[0] as Number;
                    if (sIdx < 0 || sIdx >= steps.size()) {
                        continue;
                    }
                    var stp = steps[sIdx] as Dictionary;
                    var wF = parseWeightToFloat(ra[1]);
                    var rp = ra[2] as Number;
                    var vol = wF * rp.toFloat();
                    completedLog.add({
                        "name"     => stp.get("name"),
                        "label"    => stp.get("label"),
                        "setNum"   => stp.get("setNum"),
                        "setTotal" => stp.get("setTotal"),
                        "weight"   => wF,
                        "reps"     => rp,
                        "vol"      => vol,
                        "workSec"  => ((ra[3] instanceof Number) ? (ra[3] as Number) : 0),
                        "restSec"  => ((ra[4] instanceof Number) ? (ra[4] as Number) : 0),
                        "stepIdx"  => sIdx
                    });
                    completedSetsCount += 1;
                    totalWorkoutVolume += vol;
                    totalWorkoutReps += rp;
                }
            }

            var totObj = prog.get("tot");
            if (totObj instanceof Number) { workoutTotalSec = totObj as Number; }
            var workObj = prog.get("work");
            if (workObj instanceof Number) { totalWorkSec = workObj as Number; }
            var restObj = prog.get("rest");
            if (restObj instanceof Number) { totalRestSec = restObj as Number; }

            // Continue from the saved position, or the first unfinished set after it
            var start = -1;
            var curObj = prog.get("cur");
            var cur = (curObj instanceof Number) ? (curObj as Number) : 0;
            for (var a = cur; a < steps.size() && start < 0; a += 1) {
                if (a >= 0) {
                    var sa1 = steps[a] as Dictionary;
                    if (sa1.get("completed") != true && sa1.get("skipped") != true) {
                        start = a;
                    }
                }
            }
            for (var b = 0; b < steps.size() && b < cur && start < 0; b += 1) {
                var sb1 = steps[b] as Dictionary;
                if (sb1.get("completed") != true && sb1.get("skipped") != true) {
                    start = b;
                }
            }
            if (start < 0) {
                // Everything was already finished: the earlier session was saved when the app closed
                discardSavedWorkout();
                return;
            }
            currentStepIdx = start;

            // New FIT recording for the rest of the workout
            var nmObj = routine.get("n");
            var routineName = (nmObj instanceof String) ? (nmObj as String) : "Hagane";
            try {
                if (Toybox has :ActivityRecording) {
                    _session = ActivityRecording.createSession({
                        :name => routineName,
                        :sport => Activity.SPORT_TRAINING,
                        :subSport => Activity.SUB_SPORT_STRENGTH_TRAINING
                    });
                    initFitContributorFields();
                    _session.start();
                }
            } catch (ex) {
                _session = null;
            }
            updateSessionFitFields();

            screenState = STATE_ACTIVE_SET;
            vibrateShort();
            startTimer();
            WatchUi.requestUpdate();
        } catch (ex) {
            discardSavedWorkout();
        }
    }

    function loadFromStorage() as Void {
        try {
            var saved = Storage.getValue("hagane_routines");
            if (saved != null && (saved instanceof Array)) {
                routines = sanitizeRoutines(saved as Array);
            } else {
                routines = [];
            }
        } catch (ex) {
            routines = [];
        }
        if (selectedRoutineIdx >= routines.size()) {
            selectedRoutineIdx = 0;
        }
    }

    function setRoutines(newRoutines as Array) as Void {
        // Preserve currently selected routine ID across syncs/reorders if possible
        var prevSelectedId = null as String?;
        if (selectedRoutineIdx >= 0 && selectedRoutineIdx < routines.size()) {
            var prevR = routines[selectedRoutineIdx] as Dictionary;
            if (prevR.get("id") instanceof String) {
                prevSelectedId = prevR.get("id") as String;
            }
        }

        routines = sanitizeRoutines(newRoutines);

        if (prevSelectedId != null) {
            for (var i = 0; i < routines.size(); i += 1) {
                var r = routines[i] as Dictionary;
                var rid = r.get("id");
                if (rid != null && (rid instanceof String) && (rid as String).equals(prevSelectedId)) {
                    selectedRoutineIdx = i;
                    return;
                }
            }
        }
        if (selectedRoutineIdx >= routines.size()) {
            selectedRoutineIdx = 0;
        }
    }

    // True while a workout is in progress (any screen between starting a routine and the summary).
    public function isWorkoutActive() as Boolean {
        return screenState != STATE_ROUTINE_LIST && screenState != STATE_SUMMARY && screenState != STATE_RESUME_PROMPT;
    }

    function onSyncReceived(newRoutines as Array) as Void {
        if (isWorkoutActive()) {
            // Never swap routines under a running workout; apply them when it ends.
            pendingRoutines = newRoutines;
            return;
        }
        setRoutines(newRoutines);
        syncStatusText = "Forge your steel!";
        WatchUi.requestUpdate();
    }

    function applyPendingRoutines() as Void {
        if (pendingRoutines != null) {
            var queued = pendingRoutines as Array;
            pendingRoutines = null;
            setRoutines(queued);
            syncStatusText = "Forge your steel!";
        }
    }

    function onSyncRequestFailed() as Void {
        syncStatusText = "Connect Phone & Retry";
        WatchUi.requestUpdate();
    }

    // Watch-initiated pull request: asks the phone / Garmin Connect to send the latest routines
    function requestSyncFromPhone(silent as Boolean) as Void {
        if (!silent) {
            syncStatusText = "Syncing with Phone...";
            vibrateShort();
            WatchUi.requestUpdate();
        }
        try {
            Communications.transmit(
                { "cmd" => "SYNC_ROUTINES" },
                null,
                new HaganeSyncConnectListener(self)
            );
        } catch (ex) {
            if (!silent) {
                syncStatusText = "Bluetooth Offline";
                WatchUi.requestUpdate();
            }
        }
    }

    function startTimer() as Void {
        if (_timer == null) {
            _timer = new Timer.Timer();
            _timer.start(method(:onTick), 1000, true);
        }
    }

    function stopTimer() as Void {
        if (_timer != null) {
            _timer.stop();
            _timer = null;
        }
    }

    function ensureTimerIfActive() as Void {
        if (screenState == STATE_ACTIVE_SET || screenState == STATE_REST || screenState == STATE_CLOCK_GLANCE) {
            startTimer();
        }
    }

    // Best-effort cleanup if the watch OS terminates the app mid-workout
    function cleanupOnAppStop() as Void {
        stopTimer();
        if (_session != null) {
            try {
                if (_session.isRecording()) {
                    _session.stop();
                }
                if (completedSetsCount > 0) {
                    _session.save();
                } else {
                    _session.discard();
                }
            } catch (ex) {}
            _session = null;
        }
        clearFitFieldReferences();
    }

    public static function parseWeightToFloat(val as Object?) as Float {
        if (val == null) {
            return 0.0f;
        }
        if (val instanceof Number) {
            return (val as Number).toFloat();
        }
        if (val instanceof Float || val instanceof Double) {
            return (val as Float or Double).toFloat();
        }
        return 0.0f;
    }

    public static function truncateString(str as String?, maxLen as Number) as String {
        if (str == null) {
            return "";
        }
        if (str.length() <= maxLen) {
            return str;
        }
        return str.substring(0, maxLen);
    }

    private function clearFitFieldReferences() as Void {
        _fitLapExercise = null;
        _fitLapSet = null;
        _fitLapWeight = null;
        _fitLapReps = null;
        _fitLapVolume = null;
        _fitLapWorkTime = null;
        _fitLapRestTime = null;
        _fitSessionVolume = null;
        _fitSessionReps = null;
        _fitSessionSets = null;
        _fitSessionWorkTime = null;
        _fitSessionRestTime = null;
        _fitRecordWeight = null;
    }

    private function initFitContributorFields() as Void {
        if (_session == null) {
            return;
        }
        if (!(_session has :createField)) {
            return;
        }

        try {
            _fitLapExercise = _session.createField(
                "exercise",
                FIT_FIELD_LAP_EXERCISE,
                FitContributor.DATA_TYPE_STRING,
                { :mesgType => FitContributor.MESG_TYPE_LAP, :count => 32, :units => "" }
            );
        } catch (ex) { _fitLapExercise = null; }

        try {
            _fitLapSet = _session.createField(
                "set",
                FIT_FIELD_LAP_SET,
                FitContributor.DATA_TYPE_STRING,
                { :mesgType => FitContributor.MESG_TYPE_LAP, :count => 16, :units => "" }
            );
        } catch (ex) { _fitLapSet = null; }

        try {
            _fitLapWeight = _session.createField(
                "weight",
                FIT_FIELD_LAP_WEIGHT,
                FitContributor.DATA_TYPE_FLOAT,
                { :mesgType => FitContributor.MESG_TYPE_LAP, :units => "kg" }
            );
        } catch (ex) { _fitLapWeight = null; }

        try {
            _fitLapReps = _session.createField(
                "reps",
                FIT_FIELD_LAP_REPS,
                FitContributor.DATA_TYPE_UINT16,
                { :mesgType => FitContributor.MESG_TYPE_LAP, :units => "reps" }
            );
        } catch (ex) { _fitLapReps = null; }

        try {
            _fitLapVolume = _session.createField(
                "volume",
                FIT_FIELD_LAP_VOLUME,
                FitContributor.DATA_TYPE_FLOAT,
                { :mesgType => FitContributor.MESG_TYPE_LAP, :units => "kg" }
            );
        } catch (ex) { _fitLapVolume = null; }

        try {
            _fitLapWorkTime = _session.createField(
                "work_time",
                FIT_FIELD_LAP_WORK_TIME,
                FitContributor.DATA_TYPE_UINT16,
                { :mesgType => FitContributor.MESG_TYPE_LAP, :units => "s" }
            );
        } catch (ex) { _fitLapWorkTime = null; }

        try {
            _fitLapRestTime = _session.createField(
                "rest_time",
                FIT_FIELD_LAP_REST_TIME,
                FitContributor.DATA_TYPE_UINT16,
                { :mesgType => FitContributor.MESG_TYPE_LAP, :units => "s" }
            );
        } catch (ex) { _fitLapRestTime = null; }

        try {
            _fitSessionVolume = _session.createField(
                "total_volume",
                FIT_FIELD_SESSION_VOLUME,
                FitContributor.DATA_TYPE_FLOAT,
                { :mesgType => FitContributor.MESG_TYPE_SESSION, :units => "kg" }
            );
        } catch (ex) { _fitSessionVolume = null; }

        try {
            _fitSessionReps = _session.createField(
                "total_reps",
                FIT_FIELD_SESSION_REPS,
                FitContributor.DATA_TYPE_UINT16,
                { :mesgType => FitContributor.MESG_TYPE_SESSION, :units => "reps" }
            );
        } catch (ex) { _fitSessionReps = null; }

        try {
            _fitSessionSets = _session.createField(
                "total_sets",
                FIT_FIELD_SESSION_SETS,
                FitContributor.DATA_TYPE_UINT16,
                { :mesgType => FitContributor.MESG_TYPE_SESSION, :units => "sets" }
            );
        } catch (ex) { _fitSessionSets = null; }

        try {
            _fitSessionWorkTime = _session.createField(
                "total_work_time",
                FIT_FIELD_SESSION_WORK_TIME,
                FitContributor.DATA_TYPE_UINT16,
                { :mesgType => FitContributor.MESG_TYPE_SESSION, :units => "s" }
            );
        } catch (ex) { _fitSessionWorkTime = null; }

        try {
            _fitSessionRestTime = _session.createField(
                "total_rest_time",
                FIT_FIELD_SESSION_REST_TIME,
                FitContributor.DATA_TYPE_UINT16,
                { :mesgType => FitContributor.MESG_TYPE_SESSION, :units => "s" }
            );
        } catch (ex) { _fitSessionRestTime = null; }

        try {
            _fitRecordWeight = _session.createField(
                "active_weight",
                FIT_FIELD_RECORD_WEIGHT,
                FitContributor.DATA_TYPE_FLOAT,
                { :mesgType => FitContributor.MESG_TYPE_RECORD, :units => "kg" }
            );
        } catch (ex) { _fitRecordWeight = null; }
    }

    private function updateSessionFitFields() as Void {
        try {
            if (_fitSessionVolume != null) {
                _fitSessionVolume.setData(totalWorkoutVolume);
            }
            if (_fitSessionReps != null) {
                _fitSessionReps.setData(totalWorkoutReps);
            }
            if (_fitSessionSets != null) {
                _fitSessionSets.setData(completedSetsCount);
            }
            if (_fitSessionWorkTime != null) {
                _fitSessionWorkTime.setData(totalWorkSec);
            }
            if (_fitSessionRestTime != null) {
                _fitSessionRestTime.setData(totalRestSec);
            }
        } catch (ex) {}
    }

    // Returns array of exercise summary objects for multi-page review:
    // Groups by exercise label+name across all sets (including interleaved superset rounds)
    public function getExerciseSummaries() as Array {
        var groups = [] as Array;
        if (completedLog.size() == 0) {
            return groups;
        }

        var map = {} as Dictionary;
        for (var i = 0; i < completedLog.size(); i += 1) {
            var s = completedLog[i] as Dictionary;
            var exName = s.get("name") as String;
            var exLabel = s.get("label") as String;
            var setVol = s.get("vol") as Float;
            var key = exLabel + "_" + exName;

            if (!map.hasKey(key)) {
                var newGrp = {
                    "name"     => exName,
                    "label"    => exLabel,
                    "sets"     => [s] as Array,
                    "totalVol" => setVol
                };
                map.put(key, newGrp);
                groups.add(newGrp);
            } else {
                var existingGrp = map.get(key) as Dictionary;
                var sList = existingGrp.get("sets") as Array;
                sList.add(s);
                var prevVol = existingGrp.get("totalVol") as Float;
                existingGrp.put("totalVol", prevVol + setVol);
            }
        }
        return groups;
    }

    private function tickRest() as Void {
        restElapsedSec += 1;
        workoutTotalSec += 1;
        totalRestSec += 1;

        // Countdown cues so the lifter can look away from the watch: one tick at 10s left,
        // then one each for the last three seconds (the full pattern still fires at 00:00)
        if (restTargetSec >= 20 && restElapsedSec == restTargetSec - 10) {
            vibrateTick();
        } else if (restTargetSec > 3 && restElapsedSec >= restTargetSec - 3 && restElapsedSec < restTargetSec) {
            vibrateTick();
        }
        if (_fitRecordWeight != null) {
            _fitRecordWeight.setData(0.0f);
        }

        // Fire rest-complete vibration once when elapsed >= target (safe against +/-15s adjustments)
        if (!hasVibratedForRest && restTargetSec > 0 && restElapsedSec >= restTargetSec) {
            hasVibratedForRest = true;
            vibrateRestComplete();
        }
    }

    function onTick() as Void {
        var info = Activity.getActivityInfo();
        if (info != null && info.currentHeartRate != null) {
            heartRate = info.currentHeartRate as Number;
        }

        if (screenState == STATE_ACTIVE_SET || screenState == STATE_CLOCK_GLANCE) {
            setElapsedSec += 1;
            workoutTotalSec += 1;
            totalWorkSec += 1;
            if (heartRate > setPeakHr) {
                setPeakHr = heartRate;
            }
            if (_fitRecordWeight != null && currentStepIdx < steps.size()) {
                var step = steps[currentStepIdx] as Dictionary;
                _fitRecordWeight.setData(parseWeightToFloat(step.get("weight")));
            }
            WatchUi.requestUpdate();
        } else if (screenState == STATE_REST) {
            tickRest();
            WatchUi.requestUpdate();
        } else if (screenState == STATE_PAUSE_MENU) {
            // The rest countdown keeps running while the pause menu is open over the rest screen
            if (previousWorkoutState == STATE_REST && !isWorkoutComplete) {
                tickRest();
            }
            // Keep the time of day on the pause screen current
            WatchUi.requestUpdate();
        }

        // Save progress every 15s of workout time so the session can be resumed after an exit
        if (workoutTotalSec > 0 && workoutTotalSec % 15 == 0 &&
            (screenState == STATE_ACTIVE_SET || screenState == STATE_REST || screenState == STATE_CLOCK_GLANCE)) {
            saveProgress();
        }
    }

    // Build flattened step queue for a routine, interleaving superset rounds (e.g., 3A Set 1 -> 3B Set 1 -> Rest -> 3A Set 2 -> 3B Set 2)
    function buildStepsForRoutine(routine as Dictionary) as Array {
        var result = [] as Array;
        var exListObj = routine.get("e");
        if (exListObj == null || !(exListObj instanceof Array)) {
            return result;
        }
        var exList = exListObj as Array;
        if (exList.size() == 0) {
            return result;
        }

        var totalEx = exList.size();
        var i = 0;
        while (i < totalEx) {
            if (!(exList[i] instanceof Dictionary)) {
                i += 1;
                continue;
            }
            // Collect a contiguous superset chain where sn == 1 links to the next exercise
            var groupIndices = [i] as Array;
            var curr = exList[i] as Dictionary;
            while (curr.get("sn") == 1 && (i + 1) < totalEx && (exList[i + 1] instanceof Dictionary)) {
                i += 1;
                groupIndices.add(i);
                curr = exList[i] as Dictionary;
            }

            // Find max set count across exercises in this group
            var maxSets = 0;
            for (var g = 0; g < groupIndices.size(); g += 1) {
                var exDict = exList[groupIndices[g] as Number] as Dictionary;
                var sArrObj = exDict.get("s");
                if (sArrObj != null && (sArrObj instanceof Array)) {
                    var sArr = sArrObj as Array;
                    if (sArr.size() > maxSets) {
                        maxSets = sArr.size();
                    }
                }
            }

            // Interleave sets round by round
            for (var sIdx = 0; sIdx < maxSets; sIdx += 1) {
                for (var g = 0; g < groupIndices.size(); g += 1) {
                    var exIdx = groupIndices[g] as Number;
                    var exDict = exList[exIdx] as Dictionary;
                    var sArrObj = exDict.get("s");
                    if (sArrObj != null && (sArrObj instanceof Array)) {
                        var sArr = sArrObj as Array;
                        if (sIdx < sArr.size() && (sArr[sIdx] instanceof Array)) {
                            var setTuple = sArr[sIdx] as Array;
                            var weightVal = setTuple.size() > 0 ? setTuple[0] : 0;
                            var repsVal = (setTuple.size() > 1 && (setTuple[1] instanceof Number))
                                ? (setTuple[1] as Number)
                                : 10;
                            var isWarmupSet = (setTuple.size() > 2 && setTuple[2] == 1);

                            var isLastInGroup = (g == groupIndices.size() - 1);
                            var restSec = 90;
                            if (!isLastInGroup) {
                                restSec = 0; // Superset transition (e.g., 3A -> 3B has 0s rest)
                            } else if (exDict.get("r") instanceof Number) {
                                restSec = exDict.get("r") as Number;
                            }

                            var lblObj = exDict.get("l");
                            var nmObj = exDict.get("n");
                            var ntObj = exDict.get("nt");

                            var step = {
                                "exIdx"       => exIdx + 1,
                                "exTotal"     => totalEx,
                                "label"       => (lblObj instanceof String) ? (lblObj as String) : (exIdx + 1).toString(),
                                "name"        => (nmObj instanceof String) ? (nmObj as String) : "Exercise",
                                "isWarmup"    => (exDict.get("w") == 1),
                                "setNum"      => sIdx + 1,
                                "setTotal"    => sArr.size(),
                                "weight"      => weightVal,
                                "reps"        => repsVal,
                                "plannedWeight" => weightVal,
                                "plannedReps" => repsVal,
                                "isWarmupSet" => isWarmupSet,
                                "restSeconds" => restSec,
                                "note"        => (ntObj instanceof String) ? (ntObj as String) : "",
                                "completed"   => false,
                                "skipped"     => false
                            };
                            result.add(step);
                        }
                    }
                }
            }
            i += 1;
        }
        return result;
    }

    // Returns array of unique exercises in the active routine with their set status
    function getActiveExerciseList() as Array {
        var list = [] as Array;
        var seen = {} as Dictionary;
        for (var i = 0; i < steps.size(); i += 1) {
            var step = steps[i] as Dictionary;
            var name = step.get("name") as String;
            var label = step.get("label") as String;
            var key = label + "_" + name;
            var isCompleted = (step.get("completed") == true);
            var isSkipped = (step.get("skipped") == true);

            if (!seen.hasKey(key)) {
                var item = {
                    "label"         => label,
                    "name"          => name,
                    "firstStepIdx"  => i,
                    "totalSets"     => 0,
                    "completedSets" => 0,
                    "handledSets"   => 0,
                    "isDone"        => false
                };
                seen.put(key, item);
                list.add(item);
            }

            var entry = seen.get(key) as Dictionary;
            entry.put("totalSets", (entry.get("totalSets") as Number) + 1);
            if (isCompleted) {
                entry.put("completedSets", (entry.get("completedSets") as Number) + 1);
                entry.put("handledSets", (entry.get("handledSets") as Number) + 1);
            } else if (isSkipped) {
                entry.put("handledSets", (entry.get("handledSets") as Number) + 1);
            }
        }

        for (var j = 0; j < list.size(); j += 1) {
            var e = list[j] as Dictionary;
            var hSets = e.get("handledSets") as Number;
            var tSets = e.get("totalSets") as Number;
            e.put("isDone", (hSets >= tSets));
        }

        return list;
    }

    // "3A"/"3B" -> "3", "W1A" -> "W1", "2" -> "2": steps of one exercise or superset share a group
    private function groupKeyOf(label as String) as String {
        var n = label.length();
        if (n >= 2) {
            var last = label.substring(n - 1, n);
            var prev = label.substring(n - 2, n - 1);
            var digits = "0123456789";
            if (digits.find(prev) != null && digits.find(last) == null) {
                return label.substring(0, n - 1);
            }
        }
        return label;
    }

    private function groupOfStep(stepIdx as Number) as String {
        var lbl = (steps[stepIdx] as Dictionary).get("label");
        return (lbl instanceof String) ? groupKeyOf(lbl as String) : "";
    }

    // Called when jumping to another exercise: remember the set we were about to do so the
    // workout can come back to it after the detour (e.g. leg press taken -> leg extension first).
    private function rememberReturnPoint(targetIdx as Number) as Void {
        if (currentStepIdx < 0 || currentStepIdx >= steps.size() || targetIdx < 0 || targetIdx >= steps.size()) {
            return;
        }
        var cur = steps[currentStepIdx] as Dictionary;
        if (cur.get("completed") == true || cur.get("skipped") == true) {
            return;
        }
        if (groupOfStep(currentStepIdx).equals(groupOfStep(targetIdx))) {
            return;
        }
        for (var i = 0; i < returnStack.size(); i += 1) {
            if ((returnStack[i] as Number) == currentStepIdx) {
                return;
            }
        }
        returnStack.add(currentStepIdx);
        if (returnStack.size() > 4) {
            returnStack = returnStack.slice(1, returnStack.size());
        }
    }

    // After finishing a set: if we are about to leave the exercise/superset we detoured into,
    // return the step to go back to; otherwise -1 (keep the normal order).
    private function popReturnPoint(doneIdx as Number, nextIdx as Number) as Number {
        if (returnStack.size() == 0 || doneIdx < 0 || doneIdx >= steps.size()) {
            return -1;
        }
        var doneGroup = groupOfStep(doneIdx);
        if (nextIdx >= 0 && nextIdx < steps.size() && groupOfStep(nextIdx).equals(doneGroup)) {
            return -1;
        }
        while (returnStack.size() > 0) {
            var idx = returnStack[returnStack.size() - 1] as Number;
            returnStack = returnStack.slice(0, returnStack.size() - 1);
            if (idx >= 0 && idx < steps.size()) {
                var stp = steps[idx] as Dictionary;
                if (stp.get("completed") != true && stp.get("skipped") != true &&
                    !groupOfStep(idx).equals(doneGroup)) {
                    return idx;
                }
            }
        }
        return -1;
    }

    // Hold UP during a set or rest: open the exercise picker right away, without pausing the recording
    function openExercisePickerDirect() as Void {
        var origin = screenState;
        previousWorkoutState = origin;
        openExercisePicker();
        pickerReturnState = origin;
    }

    function jumpToExercise(targetExIdx as Number) as Void {
        var exList = getActiveExerciseList();
        if (targetExIdx < 0 || targetExIdx >= exList.size()) {
            return;
        }
        var target = exList[targetExIdx] as Dictionary;
        var targetLabel = target.get("label") as String;
        var targetName = target.get("name") as String;

        // Find the first uncompleted step for this exercise
        var foundIdx = -1;
        for (var i = 0; i < steps.size(); i += 1) {
            var step = steps[i] as Dictionary;
            if ((step.get("label") as String).equals(targetLabel) &&
                (step.get("name") as String).equals(targetName)) {
                if (step.get("completed") != true && step.get("skipped") != true) {
                    foundIdx = i;
                    break;
                }
            }
        }
        var isRedo = false;
        if (foundIdx < 0) {
            foundIdx = target.get("firstStepIdx") as Number;
            // Lifter jumped to an already-completed/skipped exercise to redo it -> uncomplete it cleanly
            uncompleteStep(foundIdx);
            isRedo = true;
        }

        if (_session != null && !_session.isRecording()) {
            try {
                _session.start();
            } catch (ex) {}
        }
        startTimer();

        // Only clear rest elapsed if redoing a completed step or jumping to a different step.
        // If exiting from a rest in progress (and not redoing), capture the rest elapsed for the upcoming set.
        if (!isRedo && previousWorkoutState == STATE_REST) {
            lastRestElapsedSec = restElapsedSec;
            setElapsedSec = 0;
        } else if (isRedo || foundIdx != currentStepIdx) {
            lastRestElapsedSec = 0;
            setElapsedSec = 0;
        }

        rememberReturnPoint(foundIdx);
        currentStepIdx = foundIdx;
        restElapsedSec = 0;
        screenState = STATE_ACTIVE_SET;
        vibrateShort();
        WatchUi.requestUpdate();
    }

    function startSelectedRoutine() as Boolean {
        if (routines.size() == 0 || selectedRoutineIdx >= routines.size()) {
            return false;
        }
        var routine = routines[selectedRoutineIdx] as Dictionary;
        steps = buildStepsForRoutine(routine);
        if (steps.size() == 0) {
            syncStatusText = "Routine is Empty";
            WatchUi.requestUpdate();
            return false;
        }
        var startIdObj = routine.get("id");
        activeRoutineId = (startIdObj instanceof String) ? (startIdObj as String) : "";
        returnStack = [];
        setPeakHr = 0;
        restPeakHr = 0;

        currentStepIdx = 0;
        setElapsedSec = 0;
        restElapsedSec = 0;
        hasVibratedForRest = false;
        workoutTotalSec = 0;
        completedSetsCount = 0;
        totalWorkoutVolume = 0.0f;
        totalWorkoutReps = 0;
        totalWorkSec = 0;
        totalRestSec = 0;
        lastRestElapsedSec = 0;
        completedLog = [];
        summaryPageIdx = 0;
        avgHeartRate = 0;
        maxHeartRate = 0;
        calories = 0;
        isWorkoutComplete = false;
        discardConfirmIdx = 0;
        // Wait on the GET READY screen (no countdown) until the lifter presses START for set 1
        previousWorkoutState = STATE_REST;
        restTargetSec = 0;
        hasVibratedForRest = true;
        screenState = STATE_REST;

        // Start Garmin FIT Strength Training Recording Session
        var nmObj = routine.get("n");
        var routineName = (nmObj instanceof String) ? (nmObj as String) : "Hagane";
        try {
            if (Toybox has :ActivityRecording) {
                _session = ActivityRecording.createSession({
                    :name => routineName,
                    :sport => Activity.SPORT_TRAINING,
                    :subSport => Activity.SUB_SPORT_STRENGTH_TRAINING
                });
                initFitContributorFields();
                _session.start();
            }
        } catch (ex) {
            _session = null;
        }

        vibrateShort();
        startTimer();
        WatchUi.requestUpdate();
        return true;
    }

    // Called when user presses START while performing an active set
    function completeCurrentSet() as Void {
        if (currentStepIdx >= steps.size()) {
            onWorkoutComplete();
            return;
        }

        var step = steps[currentStepIdx] as Dictionary;

        // Guard against re-completing an already completed or skipped step:
        // If the step was previously marked completed, retract its prior totals before re-logging
        if (step.get("completed") == true || step.get("skipped") == true) {
            uncompleteStep(currentStepIdx);
        }

        var exName = (step.get("name") instanceof String) ? (step.get("name") as String) : "Exercise";
        var exLabel = (step.get("label") instanceof String) ? (step.get("label") as String) : "";
        var setNum = (step.get("setNum") instanceof Number) ? (step.get("setNum") as Number) : 1;
        var setTotal = (step.get("setTotal") instanceof Number) ? (step.get("setTotal") as Number) : 1;
        var repsVal = (step.get("reps") instanceof Number) ? (step.get("reps") as Number) : 0;
        var isWarmup = (step.get("isWarmup") == true);
        var isWarmupSet = (step.get("isWarmupSet") == true);
        var weightFloat = parseWeightToFloat(step.get("weight"));
        var setVol = weightFloat * repsVal.toFloat();
        var workSec = setElapsedSec;
        var restSecTaken = lastRestElapsedSec;
        lastRestElapsedSec = 0;

        // Build set label e.g. "1/3", "3A • 2/3", or "Warmup 1"
        var setLabelStr = "";
        if (isWarmup || isWarmupSet) {
            setLabelStr = "Warmup " + setNum;
        } else if (exLabel.length() >= 2) {
            setLabelStr = exLabel + " • " + setNum + "/" + setTotal;
        } else {
            setLabelStr = setNum + "/" + setTotal;
        }

        // 1. Populate FIT Lap Developer Fields
        try {
            if (_fitLapExercise != null) {
                _fitLapExercise.setData(truncateString(exName, 31));
            }
            if (_fitLapSet != null) {
                _fitLapSet.setData(truncateString(setLabelStr, 15));
            }
            if (_fitLapWeight != null) {
                _fitLapWeight.setData(weightFloat);
            }
            if (_fitLapReps != null) {
                _fitLapReps.setData(repsVal);
            }
            if (_fitLapVolume != null) {
                _fitLapVolume.setData(setVol);
            }
            if (_fitLapWorkTime != null) {
                _fitLapWorkTime.setData(workSec);
            }
            if (_fitLapRestTime != null) {
                _fitLapRestTime.setData(restSecTaken);
            }
        } catch (ex) {}

        // 2. Accumulate totals
        completedSetsCount += 1;
        totalWorkoutVolume += setVol;
        totalWorkoutReps += repsVal;

        // 3. Update Session summary FIT fields
        updateSessionFitFields();

        // 4. Record to completedLog for Watch Summary pages
        completedLog.add({
            "name"     => exName,
            "label"    => exLabel,
            "setNum"   => setNum,
            "setTotal" => setTotal,
            "weight"   => weightFloat,
            "reps"     => repsVal,
            "vol"      => setVol,
            "workSec"  => workSec,
            "restSec"  => restSecTaken,
            "stepIdx"  => currentStepIdx
        });

        // 5. Mark current step as completed
        if (currentStepIdx < steps.size()) {
            var currStep = steps[currentStepIdx] as Dictionary;
            currStep.put("completed", true);
            currStep.put("skipped", false);
        }

        // 6. Commit lap to FIT file for each completed set
        if (_session != null && _session.isRecording()) {
            try {
                _session.addLap();
            } catch (ex) {}
        }

        // 7. Find next uncompleted step (prefer forward, then wrap around for skipped exercises)
        var nextIdx = -1;
        for (var i = currentStepIdx + 1; i < steps.size(); i += 1) {
            var stp = steps[i] as Dictionary;
            if (stp.get("completed") != true && stp.get("skipped") != true) {
                nextIdx = i;
                break;
            }
        }
        if (nextIdx < 0) {
            for (var j = 0; j < currentStepIdx; j += 1) {
                var stp = steps[j] as Dictionary;
                if (stp.get("completed") != true && stp.get("skipped") != true) {
                    nextIdx = j;
                    break;
                }
            }
        }

        // Detour finished? Go back to the exercise that was left unfinished.
        var returnIdx = popReturnPoint(currentStepIdx, nextIdx);
        if (returnIdx >= 0) {
            nextIdx = returnIdx;
        }

        // If all steps in the entire workout are completed, prompt Save / Discard!
        if (nextIdx < 0) {
            onWorkoutComplete();
            return;
        }

        var doneStepIdx = currentStepIdx;
        currentStepIdx = nextIdx;
        setElapsedSec = 0;

        restPeakHr = setPeakHr;
        setPeakHr = 0;

        // ALWAYS enter rest/prep state! Moving to next set is ALWAYS manual!
        var restSec = step.get("restSeconds") as Number;
        // Moving on to another exercise: no rest, just a wait screen until START
        // (supersets keep their own rest settings)
        if (!groupOfStep(doneStepIdx).equals(groupOfStep(nextIdx))) {
            restSec = 0;
        }
        vibrateShort();
        restTargetSec = (restSec != null && restSec > 0) ? restSec : 0;
        restElapsedSec = 0;
        hasVibratedForRest = false;
        screenState = STATE_REST;
        saveProgress();
        WatchUi.requestUpdate();
    }

    // Called when user presses START during Rest Timer (either early before 00:00, or during +00:xx overtime)
    function startNextSetFromRest() as Void {
        vibrateShort();
        lastRestElapsedSec = restElapsedSec;
        setElapsedSec = 0;
        screenState = STATE_ACTIVE_SET;
        WatchUi.requestUpdate();
    }

    // Adjust rest timer target on the fly with UP (+15s) or DOWN (-15s)
    function adjustRestTarget(deltaSec as Number) as Void {
        if (restTargetSec <= 0) {
            // In 0s "GET READY" / equipment setup mode, ignore timer adjustments
            return;
        }
        restTargetSec += deltaSec;
        if (restTargetSec < 15) {
            restTargetSec = 15;
        } else if (restTargetSec > 600) {
            restTargetSec = 600;
        }
        // If user lowered target at or below current elapsed time and hasn't vibrated yet, trigger immediately
        if (!hasVibratedForRest && restElapsedSec >= restTargetSec) {
            hasVibratedForRest = true;
            vibrateRestComplete();
        }
        WatchUi.requestUpdate();
    }

    function onWorkoutComplete() as Void {
        isWorkoutComplete = true;
        pauseMenuIdx = 0; // "Save Workout" is pre-selected
        screenState = STATE_PAUSE_MENU;
        stopTimer();
        if (_session != null && _session.isRecording()) {
            try {
                _session.stop();
            } catch (ex) {}
        }
        vibrateWorkoutComplete();
        WatchUi.requestUpdate();
    }

    function openPauseMenu() as Void {
        previousWorkoutState = screenState;
        isWorkoutComplete = false;
        pauseMenuIdx = 0; // "Resume" is pre-selected
        screenState = STATE_PAUSE_MENU;
        // Pause the FIT recording while a set is paused; during rest the clock keeps running
        if (previousWorkoutState != STATE_REST && _session != null && _session.isRecording()) {
            try {
                _session.stop();
            } catch (ex) {}
        }
        WatchUi.requestUpdate();
    }

    function openDiscardConfirm() as Void {
        discardConfirmIdx = 0; // 0 = Cancel (safe default), 1 = Discard Workout
        screenState = STATE_DISCARD_CONFIRM;
        WatchUi.requestUpdate();
    }

    function areAllStepsCompleted() as Boolean {
        if (steps.size() == 0) {
            return false;
        }
        for (var i = 0; i < steps.size(); i += 1) {
            var stp = steps[i] as Dictionary;
            if (stp.get("completed") != true && stp.get("skipped") != true) {
                return false;
            }
        }
        return true;
    }

    function resumeFromPauseMenu() as Void {
        if (isWorkoutComplete || areAllStepsCompleted()) {
            openExercisePicker();
            return;
        }

        // If current step is already completed or skipped, advance to next uncompleted step or open picker
        if (currentStepIdx < steps.size()) {
            var currStep = steps[currentStepIdx] as Dictionary;
            if (currStep.get("completed") == true || currStep.get("skipped") == true) {
                var nextIdx = -1;
                for (var i = 0; i < steps.size(); i += 1) {
                    var stp = steps[i] as Dictionary;
                    if (stp.get("completed") != true && stp.get("skipped") != true) {
                        nextIdx = i;
                        break;
                    }
                }
                if (nextIdx >= 0) {
                    currentStepIdx = nextIdx;
                } else {
                    openExercisePicker();
                    return;
                }
            }
        }

        if (_session != null && !_session.isRecording()) {
            try {
                _session.start();
            } catch (ex) {}
        }
        startTimer();
        screenState = previousWorkoutState;
        WatchUi.requestUpdate();
    }

    function openExercisePicker() as Void {
        pickerReturnState = STATE_PAUSE_MENU;
        var exList = getActiveExerciseList();
        exercisePickerIdx = 0;
        if (currentStepIdx < steps.size()) {
            var currStep = steps[currentStepIdx] as Dictionary;
            var currLabel = currStep.get("label") as String;
            var currName = currStep.get("name") as String;
            for (var i = 0; i < exList.size(); i += 1) {
                var item = exList[i] as Dictionary;
                if ((item.get("label") as String).equals(currLabel) &&
                    (item.get("name") as String).equals(currName)) {
                    exercisePickerIdx = i;
                    break;
                }
            }
        }
        screenState = STATE_EXERCISE_PICKER;
        WatchUi.requestUpdate();
    }

    function skipCurrentSet() as Void {
        if (_session != null && !_session.isRecording()) {
            try {
                _session.start();
            } catch (ex) {}
        }
        startTimer();
        if (previousWorkoutState == STATE_REST) {
            lastRestElapsedSec = restElapsedSec;
            setElapsedSec = 0;
            screenState = STATE_ACTIVE_SET;
        } else {
            if (currentStepIdx < steps.size()) {
                var currStep = steps[currentStepIdx] as Dictionary;
                currStep.put("skipped", true);
                currStep.put("completed", false);
            }
            var nextIdx = -1;
            for (var i = currentStepIdx + 1; i < steps.size(); i += 1) {
                var stp = steps[i] as Dictionary;
                if (stp.get("completed") != true && stp.get("skipped") != true) {
                    nextIdx = i;
                    break;
                }
            }
            if (nextIdx < 0) {
                for (var j = 0; j < currentStepIdx; j += 1) {
                    var stp = steps[j] as Dictionary;
                    if (stp.get("completed") != true && stp.get("skipped") != true) {
                        nextIdx = j;
                        break;
                    }
                }
            }
            if (nextIdx < 0) {
                onWorkoutComplete();
                return;
            }
            currentStepIdx = nextIdx;
            setElapsedSec = 0;
            lastRestElapsedSec = 0;
            screenState = STATE_ACTIVE_SET;
        }
        WatchUi.requestUpdate();
    }

    // Reverts completion of a step and deducts volume/reps/log entry to prevent double-counting
    function uncompleteStep(stepIdx as Number) as Void {
        if (stepIdx < 0 || stepIdx >= steps.size()) {
            return;
        }
        var step = steps[stepIdx] as Dictionary;
        var wasCompleted = (step.get("completed") == true);
        var wasSkipped = (step.get("skipped") == true);

        if (!wasCompleted && !wasSkipped) {
            return;
        }

        step.put("completed", false);
        step.put("skipped", false);

        if (wasSkipped && !wasCompleted) {
            // Skipped step has no log entry and never incremented counts; nothing to remove!
            return;
        }

        // Find and remove the matching entry from completedLog (searching backwards strictly by stepIdx)
        var removed = false;
        for (var i = completedLog.size() - 1; i >= 0; i -= 1) {
            var entry = completedLog[i] as Dictionary;
            if (entry.hasKey("stepIdx") && entry.get("stepIdx") == stepIdx) {
                var vol = entry.get("vol") as Float;
                var reps = entry.get("reps") as Number;
                totalWorkoutVolume -= vol;
                if (totalWorkoutVolume < 0.0f) {
                    totalWorkoutVolume = 0.0f;
                }
                totalWorkoutReps -= reps;
                if (totalWorkoutReps < 0) {
                    totalWorkoutReps = 0;
                }
                completedLog.remove(entry);
                removed = true;
                break;
            }
        }

        // Only decrement completedSetsCount if a log entry was actually removed!
        if (removed && completedSetsCount > 0) {
            completedSetsCount -= 1;
        }

        updateSessionFitFields();
    }

    function goToPreviousSet() as Void {
        if (_session != null && !_session.isRecording()) {
            try {
                _session.start();
            } catch (ex) {}
        }
        startTimer();
        if (currentStepIdx > 0) {
            currentStepIdx -= 1;
            uncompleteStep(currentStepIdx);
        } else if (currentStepIdx == 0) {
            uncompleteStep(0);
        }
        setElapsedSec = 0;
        lastRestElapsedSec = 0;
        screenState = STATE_ACTIVE_SET;
        WatchUi.requestUpdate();
    }

    // UP / DOWN on the set screen: log what was really lifted (reps +/- 1)
    function adjustReps(delta as Number) as Void {
        if (currentStepIdx < 0 || currentStepIdx >= steps.size()) {
            return;
        }
        var step = steps[currentStepIdx] as Dictionary;
        var cur = (step.get("reps") instanceof Number) ? (step.get("reps") as Number) : 0;
        var next = cur + delta;
        if (next < 0) { next = 0; }
        if (next > 99) { next = 99; }
        step.put("reps", next);
        WatchUi.requestUpdate();
    }

    function openEditWeight() as Void {
        if (currentStepIdx < 0 || currentStepIdx >= steps.size() || isWorkoutComplete) {
            return;
        }
        var step = steps[currentStepIdx] as Dictionary;
        editWeightValue = parseWeightToFloat(step.get("weight"));
        screenState = STATE_EDIT_WEIGHT;
        WatchUi.requestUpdate();
    }

    function adjustEditWeight(delta as Float) as Void {
        var next = editWeightValue + delta;
        if (next < 0.0f) { next = 0.0f; }
        if (next > 500.0f) { next = 500.0f; }
        editWeightValue = next;
        WatchUi.requestUpdate();
    }

    // Apply the new weight to this set and the remaining sets of the same exercise
    function confirmEditWeight() as Void {
        if (currentStepIdx >= 0 && currentStepIdx < steps.size()) {
            var cur = steps[currentStepIdx] as Dictionary;
            var nm = cur.get("name");
            var lb = cur.get("label");
            var wu = (cur.get("isWarmupSet") == true);
            for (var i = currentStepIdx; i < steps.size(); i += 1) {
                var stp = steps[i] as Dictionary;
                if (stp.get("completed") == true || stp.get("skipped") == true) {
                    continue;
                }
                var sameEx = (stp.get("name") as String).equals(nm as String) &&
                             (stp.get("label") as String).equals(lb as String) &&
                             ((stp.get("isWarmupSet") == true) == wu);
                if (i == currentStepIdx || sameEx) {
                    stp.put("weight", editWeightValue);
                }
            }
        }
        resumeFromPauseMenu();
    }

    function executePauseMenuAction() as Void {
        var items = getPauseMenuItems();
        if (pauseMenuIdx < 0 || pauseMenuIdx >= items.size()) {
            return;
        }
        var action = items[pauseMenuIdx] as String;

        if (action.equals("Resume") || action.equals("Resume Workout")) {
            if (isWorkoutComplete) {
                isWorkoutComplete = false;
                // If entire workout was marked complete and lifter resumes, open the Exercise Picker
                // so they can choose which exercise to do extra sets for
                openExercisePicker();
                return;
            }
            resumeFromPauseMenu();
            return;
        } else if (action.equals("Select Exercise")) {
            openExercisePicker();
            return;
        } else if (action.equals("Edit Weight")) {
            openEditWeight();
            return;
        } else if (action.equals("Skip Set")) {
            skipCurrentSet();
            return;
        } else if (action.equals("Previous Set")) {
            goToPreviousSet();
            return;
        } else if (action.equals("Save Workout")) {
            finishAndSaveWorkout();
            return;
        } else if (action.equals("Discard")) {
            openDiscardConfirm();
            return;
        }
    }

    function finishAndSaveWorkout() as Void {
        stopTimer();
        clearProgress();
        // Capture telemetry before saving FIT session
        try {
            var info = Activity.getActivityInfo();
            if (info != null) {
                if (info.averageHeartRate != null) {
                    avgHeartRate = info.averageHeartRate as Number;
                } else if (heartRate > 0) {
                    avgHeartRate = heartRate;
                }
                if (info.maxHeartRate != null) {
                    maxHeartRate = info.maxHeartRate as Number;
                }
                if (info.calories != null) {
                    calories = info.calories as Number;
                }
            }
        } catch (ex) {}

        // Ensure session developer fields have final totals
        updateSessionFitFields();

        if (_session != null) {
            try {
                if (_session.isRecording()) {
                    _session.stop();
                }
                _session.save();
            } catch (ex) {}
            _session = null;
        }
        clearFitFieldReferences();

        // Transmit workout completion log to companion phone app if connected
        try {
            Communications.transmit(
                {
                    "cmd"      => "WORKOUT_COMPLETED",
                    "routine"  => activeRoutineId,
                    "totalSec" => workoutTotalSec,
                    "volume"   => totalWorkoutVolume,
                    "reps"     => totalWorkoutReps,
                    "sets"     => completedSetsCount,
                    "workSec"  => totalWorkSec,
                    "restSec"  => totalRestSec
                },
                null,
                new HaganeSyncConnectListener(self)
            );
        } catch (ex) {}

        vibrateWorkoutSaved();
        syncStatusText = "Workout Saved!";
        screenState = STATE_SUMMARY;
        summaryPageIdx = 0;
        applyPendingRoutines();
        syncStatusText = "Workout Saved!";
        WatchUi.requestUpdate();
    }

    function discardWorkout() as Void {
        stopTimer();
        clearProgress();
        if (_session != null) {
            try {
                if (_session.isRecording()) {
                    _session.stop();
                }
                _session.discard();
            } catch (ex) {}
            _session = null;
        }
        clearFitFieldReferences();
        vibrateShort();
        screenState = STATE_ROUTINE_LIST;
        applyPendingRoutines();
        syncStatusText = "Workout Discarded";
        WatchUi.requestUpdate();
    }

    function vibrateTick() as Void {
        if (Attention has :vibrate) {
            try {
                Attention.vibrate([new Attention.VibeProfile(60, 90)]);
            } catch (ex) {}
        }
    }

    function vibrateShort() as Void {
        if (Attention has :vibrate) {
            try {
                Attention.vibrate([new Attention.VibeProfile(75, 160)]);
            } catch (ex) {}
        }
    }

    function vibrateRestComplete() as Void {
        if (Attention has :vibrate) {
            try {
                var pulses = [
                    new Attention.VibeProfile(100, 350),
                    new Attention.VibeProfile(0, 150),
                    new Attention.VibeProfile(100, 350),
                    new Attention.VibeProfile(0, 150),
                    new Attention.VibeProfile(100, 600)
                ];
                Attention.vibrate(pulses);
            } catch (ex) {}
        }
        if (Attention has :playTone) {
            try {
                Attention.playTone(Attention.TONE_TIME_ALERT);
            } catch (ex) {}
        }
    }

    function vibrateWorkoutSaved() as Void {
        if (Attention has :vibrate) {
            try {
                var pulses = [
                    new Attention.VibeProfile(90, 180),
                    new Attention.VibeProfile(0, 100),
                    new Attention.VibeProfile(100, 450)
                ];
                Attention.vibrate(pulses);
            } catch (ex) {}
        }
        if (Attention has :playTone) {
            try {
                Attention.playTone(Attention.TONE_SUCCESS);
            } catch (ex) {}
        }
    }

    function vibrateWorkoutComplete() as Void {
        if (Attention has :vibrate) {
            try {
                var pulses = [
                    new Attention.VibeProfile(100, 200),
                    new Attention.VibeProfile(0, 100),
                    new Attention.VibeProfile(100, 200),
                    new Attention.VibeProfile(0, 100),
                    new Attention.VibeProfile(100, 500)
                ];
                Attention.vibrate(pulses);
            } catch (ex) {}
        }
        if (Attention has :playTone) {
            try {
                Attention.playTone(Attention.TONE_TIME_ALERT);
            } catch (ex) {}
        }
    }
}
