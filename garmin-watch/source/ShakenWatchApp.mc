import Toybox.Application;
import Toybox.Application.Storage;
import Toybox.Attention;
import Toybox.Communications;
import Toybox.Lang;
import Toybox.WatchUi;

class ShakenWatchApp extends Application.AppBase {
    private var _state as ShakenWorkoutState?;
    private var _phoneCallback as Communications.PhoneAppMessageCallback?;

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
        _state = new ShakenWorkoutState();
        _state.loadFromStorage();

        // Register listener for incoming workouts sent by the phone companion bridge
        _phoneCallback = method(:onPhoneMessage);
        Communications.registerForPhoneAppMessages(_phoneCallback);

        // Automatically request latest routines from the phone via Garmin Connect on launch
        _state.requestSyncFromPhone(true);
    }

    function onStop(state as Dictionary?) as Void {
        if (_state != null) {
            _state.cleanupOnAppStop();
        }
    }

    function onPhoneMessage(msg as Communications.PhoneAppMessage) as Void {
        var data = msg.data;
        if (data == null || !(data instanceof Dictionary)) {
            return;
        }
        var dict = data as Dictionary;

        // Check schema version (accept v == 1 or missing v)
        var ver = dict.get("v");
        if (ver != null && (ver instanceof Number) && (ver as Number) != 1) {
            if (_state != null) {
                _state.syncStatusText = "Incompatible App v" + ver.toString();
                WatchUi.requestUpdate();
            }
            return;
        }

        var routinesObj = dict.get("routines");
        if (routinesObj == null || !(routinesObj instanceof Array)) {
            return;
        }

        var sanitized = ShakenWorkoutState.sanitizeRoutines(routinesObj as Array);
        try {
            Storage.setValue("shaken_routines", sanitized);
        } catch (ex) {
            // Storage quota exceeded or write error; still keep in RAM for this session
        }

        if (_state != null) {
            _state.onSyncReceived(sanitized);
        }
        if (Attention has :vibrate) {
            try {
                var vibe = [new Attention.VibeProfile(80, 220)];
                Attention.vibrate(vibe);
            } catch (ex) {}
        }
        WatchUi.requestUpdate();
    }

    function getInitialView() as [Views] or [Views, InputDelegates] {
        if (_state == null) {
            _state = new ShakenWorkoutState();
            _state.loadFromStorage();
        }
        var view = new ShakenWatchView(_state);
        var delegate = new ShakenWatchDelegate(_state);
        return [view, delegate];
    }
}

function getApp() as ShakenWatchApp {
    return Application.getApp() as ShakenWatchApp;
}
