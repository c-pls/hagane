import Toybox.Activity;
import Toybox.ActivityRecording;
import Toybox.Application.Storage;
import Toybox.Attention;
import Toybox.Communications;
import Toybox.FitContributor;
import Toybox.Lang;
import Toybox.Sensor;
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

    public var screenState as Number = STATE_ROUTINE_LIST;
    public var previousWorkoutState as Number = STATE_ACTIVE_SET;
    public var exercisePickerIdx as Number = 0;

    // Synced routines array
    public var routines as Array = [];
    public var selectedRoutineIdx as Number = 0;

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
        "Skip Set",
        "Previous Set",
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

    function onSyncReceived(newRoutines as Array) as Void {
        setRoutines(newRoutines);
        syncStatusText = "Forge your steel!";
        WatchUi.requestUpdate();
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

    function onTick() as Void {
        var info = Activity.getActivityInfo();
        if (info != null && info.currentHeartRate != null) {
            heartRate = info.currentHeartRate as Number;
        }

        if (screenState == STATE_ACTIVE_SET || screenState == STATE_CLOCK_GLANCE) {
            setElapsedSec += 1;
            workoutTotalSec += 1;
            totalWorkSec += 1;
            if (_fitRecordWeight != null && currentStepIdx < steps.size()) {
                var step = steps[currentStepIdx] as Dictionary;
                _fitRecordWeight.setData(parseWeightToFloat(step.get("weight")));
            }
            WatchUi.requestUpdate();
        } else if (screenState == STATE_REST) {
            restElapsedSec += 1;
            workoutTotalSec += 1;
            totalRestSec += 1;
            if (_fitRecordWeight != null) {
                _fitRecordWeight.setData(0.0f);
            }

            // Fire rest-complete vibration once when elapsed >= target (safe against +/-15s adjustments)
            if (!hasVibratedForRest && restTargetSec > 0 && restElapsedSec >= restTargetSec) {
                hasVibratedForRest = true;
                vibrateRestComplete();
            }
            WatchUi.requestUpdate();
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
                                "isWarmupSet" => isWarmupSet,
                                "restSeconds" => restSec,
                                "note"        => (ntObj instanceof String) ? (ntObj as String) : "",
                                "completed"   => false
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

            if (!seen.hasKey(key)) {
                var item = {
                    "label"         => label,
                    "name"          => name,
                    "firstStepIdx"  => i,
                    "totalSets"     => 0,
                    "completedSets" => 0,
                    "isDone"        => false
                };
                seen.put(key, item);
                list.add(item);
            }

            var entry = seen.get(key) as Dictionary;
            entry.put("totalSets", (entry.get("totalSets") as Number) + 1);
            if (isCompleted) {
                entry.put("completedSets", (entry.get("completedSets") as Number) + 1);
            }
        }

        for (var j = 0; j < list.size(); j += 1) {
            var e = list[j] as Dictionary;
            var cSets = e.get("completedSets") as Number;
            var tSets = e.get("totalSets") as Number;
            e.put("isDone", (cSets >= tSets));
        }

        return list;
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
                if (step.get("completed") != true) {
                    foundIdx = i;
                    break;
                }
            }
        }
        if (foundIdx < 0) {
            foundIdx = target.get("firstStepIdx") as Number;
            // Lifter jumped to an already-completed exercise to redo it -> uncomplete it cleanly
            uncompleteStep(foundIdx);
        }

        if (_session != null && !_session.isRecording()) {
            try {
                _session.start();
            } catch (ex) {}
        }
        startTimer();

        currentStepIdx = foundIdx;
        setElapsedSec = 0;
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
        screenState = STATE_ACTIVE_SET;

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
        }

        // 6. Commit lap to FIT file (if not the last set; on the last set, session.stop() finalizes it)
        if (_session != null && _session.isRecording()) {
            try {
                _session.addLap();
            } catch (ex) {}
        }

        // 7. Find next uncompleted step (prefer forward, then wrap around for skipped exercises)
        var nextIdx = -1;
        for (var i = currentStepIdx + 1; i < steps.size(); i += 1) {
            var stp = steps[i] as Dictionary;
            if (stp.get("completed") != true) {
                nextIdx = i;
                break;
            }
        }
        if (nextIdx < 0) {
            for (var j = 0; j < currentStepIdx; j += 1) {
                var stp = steps[j] as Dictionary;
                if (stp.get("completed") != true) {
                    nextIdx = j;
                    break;
                }
            }
        }

        // If all steps in the entire workout are completed, prompt Save / Discard!
        if (nextIdx < 0) {
            onWorkoutComplete();
            return;
        }

        currentStepIdx = nextIdx;
        setElapsedSec = 0;

        // ALWAYS enter rest/prep state! Moving to next set is ALWAYS manual!
        var restSec = step.get("restSeconds") as Number;
        vibrateShort();
        restTargetSec = (restSec != null && restSec > 0) ? restSec : 0;
        restElapsedSec = 0;
        hasVibratedForRest = false;
        screenState = STATE_REST;
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
        // Pause the underlying FIT recording session while in Pause Menu
        if (_session != null && _session.isRecording()) {
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

    function resumeFromPauseMenu() as Void {
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
            setElapsedSec = 0;
            screenState = STATE_ACTIVE_SET;
        } else {
            if (currentStepIdx < steps.size()) {
                var currStep = steps[currentStepIdx] as Dictionary;
                currStep.put("completed", true);
            }
            var nextIdx = -1;
            for (var i = currentStepIdx + 1; i < steps.size(); i += 1) {
                var stp = steps[i] as Dictionary;
                if (stp.get("completed") != true) {
                    nextIdx = i;
                    break;
                }
            }
            if (nextIdx < 0) {
                for (var j = 0; j < currentStepIdx; j += 1) {
                    var stp = steps[j] as Dictionary;
                    if (stp.get("completed") != true) {
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
        if (step.get("completed") != true) {
            return;
        }
        step.put("completed", false);
        if (completedSetsCount > 0) {
            completedSetsCount -= 1;
        }

        // Find and remove the matching entry from completedLog (searching backwards)
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

        if (!removed && completedLog.size() > 0) {
            var lastEntry = completedLog[completedLog.size() - 1] as Dictionary;
            var exName = step.get("name") as String;
            if ((lastEntry.get("name") as String).equals(exName)) {
                var vol = lastEntry.get("vol") as Float;
                var reps = lastEntry.get("reps") as Number;
                totalWorkoutVolume -= vol;
                if (totalWorkoutVolume < 0.0f) {
                    totalWorkoutVolume = 0.0f;
                }
                totalWorkoutReps -= reps;
                if (totalWorkoutReps < 0) {
                    totalWorkoutReps = 0;
                }
                completedLog.remove(lastEntry);
            }
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
        }
        setElapsedSec = 0;
        screenState = STATE_ACTIVE_SET;
        WatchUi.requestUpdate();
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
                    "routine"  => (selectedRoutineIdx < routines.size()) ? (routines[selectedRoutineIdx] as Dictionary).get("id") : "",
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
        WatchUi.requestUpdate();
    }

    function discardWorkout() as Void {
        stopTimer();
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
        syncStatusText = "Workout Discarded";
        screenState = STATE_ROUTINE_LIST;
        WatchUi.requestUpdate();
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
