package com.hagane.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.Settings;
import android.util.Log;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Android 11+ no longer honours WRITE_EXTERNAL_STORAGE, so the only way to keep the routines
 * backup in the public Documents folder (where it survives uninstall) is "All files access".
 * This plugin reports that state and opens the system settings page where the user grants it.
 */
@CapacitorPlugin(name = "StorageAccess")
public class StorageAccessPlugin extends Plugin {

    private static final String TAG = "HaganeStorageAccess";

    @PluginMethod
    public void getStatus(PluginCall call) {
        boolean needsAllFilesAccess = Build.VERSION.SDK_INT >= Build.VERSION_CODES.R;
        JSObject res = new JSObject();
        res.put("needsAllFilesAccess", needsAllFilesAccess);
        res.put("granted", needsAllFilesAccess && Environment.isExternalStorageManager());
        call.resolve(res);
    }

    @PluginMethod
    public void openSettings(PluginCall call) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R || getActivity() == null) {
            call.resolve();
            return;
        }
        try {
            // Opens this app's own "All files access" toggle directly.
            Intent intent = new Intent(
                Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION,
                Uri.parse("package:" + getContext().getPackageName())
            );
            getActivity().startActivity(intent);
            call.resolve();
        } catch (Exception first) {
            Log.w(TAG, "App-specific settings page unavailable: " + first.getMessage());
            try {
                // Fallback: the general "All files access" list.
                getActivity().startActivity(new Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION));
                call.resolve();
            } catch (Exception second) {
                call.reject("Could not open the All files access settings.");
            }
        }
    }
}
