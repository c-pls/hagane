import { Filesystem, Directory, Encoding } from '@capacitor/filesystem';
import { Capacitor } from '@capacitor/core';
import { Routine } from '../types/gym';
import { sanitizeRoutines } from './storage';

const BACKUP_DIR = 'Hagane';
const BACKUP_FILE = 'hagane_backup.json';

export interface HaganeDeviceBackup {
  version: number;
  timestamp: number;
  routines: Routine[];
  isCorrupted?: boolean;
}

export interface DeviceBackupStatus {
  hasError: boolean;
  isInternalOnly?: boolean;
}

export interface AutoSaveResult {
  success: boolean;
  isReinstallSafe: boolean;
}

type DeviceBackupErrorHandler = (status: DeviceBackupStatus) => void;
let backupErrorHandler: DeviceBackupErrorHandler | null = null;

export function setDeviceBackupErrorHandler(handler: DeviceBackupErrorHandler | null): void {
  backupErrorHandler = handler;
}

/**
 * Non-intrusive check: checks if public storage permission is granted WITHOUT showing system dialogs.
 */
export async function checkStoragePermissions(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return true;
  try {
    const status = await Filesystem.checkPermissions();
    return status.publicStorage === 'granted';
  } catch (err) {
    console.warn('[Hagane] Storage permission check error:', err);
    return false;
  }
}

/**
 * User-initiated request: prompts the system permission dialog when the user clicks 'Grant Permission'.
 */
export async function requestStoragePermissions(): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) return true;
  try {
    const status = await Filesystem.checkPermissions();
    if (status.publicStorage === 'granted') {
      return true;
    }
    const request = await Filesystem.requestPermissions();
    return request.publicStorage === 'granted';
  } catch (err) {
    console.warn('[Hagane] Storage permission request error:', err);
    return false;
  }
}

/**
 * Backward-compatibility alias for startup/manual permission request.
 */
export const ensureStoragePermissions = requestStoragePermissions;

/**
 * Automatically persist routines to the physical device's public Documents directory.
 * When Documents storage is accessible, the backup survives app uninstall/reinstall.
 * Also persists an internal copy to Directory.Data as a safety fallback.
 */
export async function autoSaveToDevice(routines: Routine[]): Promise<AutoSaveResult> {
  if (!Capacitor.isNativePlatform()) {
    return { success: false, isReinstallSafe: false };
  }

  const payload: HaganeDeviceBackup = {
    version: 1,
    timestamp: Date.now(),
    routines,
  };

  const data = JSON.stringify(payload, null, 2);

  // 1. Primary: Persist to public Documents (survives app reinstallation)
  // Uses checkStoragePermissions() ONLY - never pops up a system dialog during typing!
  let savedToPublic = false;
  try {
    const hasPermission = await checkStoragePermissions();
    if (hasPermission) {
      try {
        await Filesystem.mkdir({
          path: BACKUP_DIR,
          directory: Directory.Documents,
          recursive: true,
        });
      } catch {
        // directory likely already exists
      }

      await Filesystem.writeFile({
        path: `${BACKUP_DIR}/${BACKUP_FILE}`,
        data,
        directory: Directory.Documents,
        encoding: Encoding.UTF8,
      });

      savedToPublic = true;
    }
  } catch (err) {
    console.warn('[Hagane] Error saving backup to device Documents:', err);
  }

  // 2. Also persist to internal app data storage as cache / fallback
  let savedToInternal = false;
  try {
    await Filesystem.writeFile({
      path: BACKUP_FILE,
      data,
      directory: Directory.Data,
      encoding: Encoding.UTF8,
    });
    savedToInternal = true;
  } catch (fallbackErr) {
    console.warn('[Hagane] Fallback write to internal app data failed:', fallbackErr);
  }

  if (savedToPublic) {
    return { success: true, isReinstallSafe: true };
  }

  if (savedToInternal) {
    // Saved ONLY to internal storage! Not reinstall safe!
    console.warn('[Hagane] Backup saved to internal app data only (will NOT survive reinstall).');
    return { success: true, isReinstallSafe: false };
  }

  return { success: false, isReinstallSafe: false };
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;
let pendingSaveArgs: {
  routines: Routine[];
} | null = null;
let isWriting = false;

/**
 * Debounced and serialized auto-save to prevent concurrent disk writes
 * during rapid typing in weight/rep fields.
 */
export function debouncedAutoSaveToDevice(
  routines: Routine[],
  delayMs = 500
): void {
  if (!Capacitor.isNativePlatform()) return;

  pendingSaveArgs = { routines };
  if (debounceTimer) clearTimeout(debounceTimer);

  debounceTimer = setTimeout(async () => {
    debounceTimer = null;
    if (isWriting) {
      if (pendingSaveArgs) {
        debouncedAutoSaveToDevice(pendingSaveArgs.routines, 150);
      }
      return;
    }
    if (!pendingSaveArgs) return;
    const toSave = pendingSaveArgs;
    pendingSaveArgs = null;
    isWriting = true;
    try {
      const res = await autoSaveToDevice(toSave.routines);
      if (!res.success) {
        console.error('[Hagane] Device backup failed to write to physical storage.');
        if (backupErrorHandler) backupErrorHandler({ hasError: true, isInternalOnly: false });
      } else if (!res.isReinstallSafe) {
        // Fallback write succeeded, but it is NOT reinstall-safe!
        if (backupErrorHandler) backupErrorHandler({ hasError: true, isInternalOnly: true });
      } else {
        if (backupErrorHandler) backupErrorHandler({ hasError: false });
      }
    } finally {
      isWriting = false;
    }
  }, delayMs);
}

/**
 * Immediately flushes any pending debounced device backup when the app enters background.
 */
export function flushPendingDeviceSave(): void {
  if (!Capacitor.isNativePlatform() || !pendingSaveArgs) return;
  if (debounceTimer) {
    clearTimeout(debounceTimer);
    debounceTimer = null;
  }
  if (isWriting) {
    // Write in flight: do not discard args! Schedule immediate retry
    setTimeout(() => {
      flushPendingDeviceSave();
    }, 60);
    return;
  }
  const toSave = pendingSaveArgs;
  pendingSaveArgs = null;
  isWriting = true;
  autoSaveToDevice(toSave.routines).then((res) => {
    if (!res.success) {
      console.error('[Hagane] Flush device backup failed on app background.');
      if (backupErrorHandler) backupErrorHandler({ hasError: true, isInternalOnly: false });
    } else if (!res.isReinstallSafe) {
      if (backupErrorHandler) backupErrorHandler({ hasError: true, isInternalOnly: true });
    } else {
      if (backupErrorHandler) backupErrorHandler({ hasError: false });
    }
  }).finally(() => {
    isWriting = false;
    if (pendingSaveArgs) {
      flushPendingDeviceSave();
    }
  });
}

/**
 * Check and restore routines from device storage.
 * Reads both public Documents and internal Data storage, compares timestamps,
 * and recovers the newest valid backup. Corrupted files in one location do not
 * shadow valid backups in the other.
 */
export async function autoLoadFromDevice(): Promise<HaganeDeviceBackup | null> {
  if (!Capacitor.isNativePlatform()) {
    return null;
  }

  let docBackup: HaganeDeviceBackup | null = null;
  let dataBackup: HaganeDeviceBackup | null = null;
  let docCorrupted = false;
  let dataCorrupted = false;

  // 1. Check public Documents folder
  try {
    const result = await Filesystem.readFile({
      path: `${BACKUP_DIR}/${BACKUP_FILE}`,
      directory: Directory.Documents,
      encoding: Encoding.UTF8,
    });
    if (result && typeof result.data === 'string') {
      try {
        const parsed = JSON.parse(result.data) as Record<string, unknown>;
        if (parsed && Array.isArray(parsed.routines)) {
          const legacyComments =
            parsed.comments && typeof parsed.comments === 'object'
              ? (parsed.comments as Record<string, string>)
              : {};
          const sanitizedRoutines = sanitizeRoutines(
            parsed.routines,
            legacyComments
          );
          const ts = Number(parsed.timestamp);

          docBackup = {
            version: Number(parsed.version) || 1,
            timestamp: Number.isFinite(ts) && ts > 0 ? ts : 0,
            routines: sanitizedRoutines,
          };
        } else {
          docCorrupted = true;
        }
      } catch (parseErr) {
        console.error('[Hagane] Corrupt backup in Documents:', parseErr);
        docCorrupted = true;
        try {
          await Filesystem.writeFile({
            path: `${BACKUP_DIR}/hagane_backup_corrupt.json`,
            data: result.data,
            directory: Directory.Documents,
            encoding: Encoding.UTF8,
          });
        } catch {
          // ignore
        }
      }
    }
  } catch {
    // Documents backup does not exist or permission denied
  }

  // 2. Check internal Directory.Data fallback
  try {
    const fallbackResult = await Filesystem.readFile({
      path: BACKUP_FILE,
      directory: Directory.Data,
      encoding: Encoding.UTF8,
    });
    if (fallbackResult && typeof fallbackResult.data === 'string') {
      try {
        const parsed = JSON.parse(fallbackResult.data) as Record<string, unknown>;
        if (parsed && Array.isArray(parsed.routines)) {
          const legacyComments =
            parsed.comments && typeof parsed.comments === 'object'
              ? (parsed.comments as Record<string, string>)
              : {};
          const sanitizedRoutines = sanitizeRoutines(
            parsed.routines,
            legacyComments
          );
          const ts = Number(parsed.timestamp);

          dataBackup = {
            version: Number(parsed.version) || 1,
            timestamp: Number.isFinite(ts) && ts > 0 ? ts : 0,
            routines: sanitizedRoutines,
          };
        } else {
          dataCorrupted = true;
        }
      } catch (parseErr) {
        console.error('[Hagane] Corrupt backup in Data:', parseErr);
        dataCorrupted = true;
        // Quarantine to Data directory specifically
        try {
          await Filesystem.writeFile({
            path: 'hagane_backup_corrupt.json',
            data: fallbackResult.data,
            directory: Directory.Data,
            encoding: Encoding.UTF8,
          });
        } catch {
          // ignore
        }
      }
    }
  } catch {
    // no internal backup file exists
  }

  // 3. Compare and return the newest valid backup
  if (docBackup && dataBackup) {
    if (dataBackup.timestamp > docBackup.timestamp) {
      console.info('[Hagane] Internal Data backup is newer than Documents backup. Using Data backup.');
      // Auto-sync newer backup into Documents if permissions permit
      checkStoragePermissions().then((granted) => {
        if (granted && dataBackup) {
          autoSaveToDevice(dataBackup.routines).catch(() => {});
        }
      });
      return dataBackup;
    }
    return docBackup;
  }

  if (docBackup) {
    return docBackup;
  }

  if (dataBackup) {
    console.info('[Hagane] Loaded backup from internal Data fallback.');
    return dataBackup;
  }

  // If both failed to parse and at least one was corrupt, report corrupted
  if (docCorrupted || dataCorrupted) {
    return {
      version: 1,
      timestamp: 0,
      routines: [],
      isCorrupted: true,
    };
  }

  return null;
}
