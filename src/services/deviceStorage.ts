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

type DeviceBackupErrorHandler = (hasError: boolean) => void;
let backupErrorHandler: DeviceBackupErrorHandler | null = null;

export function setDeviceBackupErrorHandler(handler: DeviceBackupErrorHandler | null): void {
  backupErrorHandler = handler;
}

/**
 * Check and request public storage permissions if not already granted on native device.
 */
export async function ensureStoragePermissions(): Promise<boolean> {
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
 * Automatically persist routines to the physical device's public Documents directory.
 * This storage is NOT deleted when the app is uninstalled on Android, allowing
 * seamless restoration even after a complete app uninstall/reinstall.
 */
export async function autoSaveToDevice(routines: Routine[]): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) {
    return false;
  }

  const payload: HaganeDeviceBackup = {
    version: 1,
    timestamp: Date.now(),
    routines,
  };

  const data = JSON.stringify(payload, null, 2);

  // 1. Primary: Persist to public Documents (survives app reinstallation)
  try {
    const hasPermission = await ensureStoragePermissions();
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

      return true;
    }
  } catch (err) {
    console.warn('[Hagane] Error saving backup to device Documents:', err);
  }

  // 2. Secondary fallback: Persist to internal app data storage (requires zero permissions)
  try {
    await Filesystem.writeFile({
      path: BACKUP_FILE,
      data,
      directory: Directory.Data,
      encoding: Encoding.UTF8,
    });
    console.info('[Hagane] Backup saved to internal app data fallback.');
    return true;
  } catch (fallbackErr) {
    console.warn('[Hagane] Fallback write to internal app data failed:', fallbackErr);
  }

  return false;
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
      const ok = await autoSaveToDevice(toSave.routines);
      if (!ok) {
        console.error('[Hagane] Device backup failed to write to physical storage.');
        if (backupErrorHandler) backupErrorHandler(true);
      } else {
        if (backupErrorHandler) backupErrorHandler(false);
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
  autoSaveToDevice(toSave.routines).then((ok) => {
    if (!ok) {
      console.error('[Hagane] Flush device backup failed on app background.');
      if (backupErrorHandler) backupErrorHandler(true);
    } else {
      if (backupErrorHandler) backupErrorHandler(false);
    }
  }).finally(() => {
    isWriting = false;
    if (pendingSaveArgs) {
      flushPendingDeviceSave();
    }
  });
}

/**
 * Check and restore routines from the device's public Documents folder.
 * Validates and normalizes all routines via `sanitizeRoutines`.
 */
export async function autoLoadFromDevice(): Promise<HaganeDeviceBackup | null> {
  if (!Capacitor.isNativePlatform()) {
    return null;
  }

  try {
    let rawData: string | null = null;

    // 1. Check public Documents folder first
    try {
      const result = await Filesystem.readFile({
        path: `${BACKUP_DIR}/${BACKUP_FILE}`,
        directory: Directory.Documents,
        encoding: Encoding.UTF8,
      });
      if (result && typeof result.data === 'string') {
        rawData = result.data;
      }
    } catch {
      // 2. Check internal Directory.Data fallback
      try {
        const fallbackResult = await Filesystem.readFile({
          path: BACKUP_FILE,
          directory: Directory.Data,
          encoding: Encoding.UTF8,
        });
        if (fallbackResult && typeof fallbackResult.data === 'string') {
          rawData = fallbackResult.data;
        }
      } catch {
        // no backup file exists in either directory
      }
    }

    if (rawData) {
      try {
        const parsed = JSON.parse(rawData) as Record<string, unknown>;
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

          return {
            version: Number(parsed.version) || 1,
            timestamp: Number.isFinite(ts) && ts > 0 ? ts : 0,
            routines: sanitizedRoutines,
          };
        }
      } catch (parseErr) {
        console.error('[Hagane] Backup file exists on device but is corrupted or malformed:', parseErr);
        // Quarantine corrupt backup to a single deterministic file to avoid unbounded file accumulation
        try {
          await Filesystem.writeFile({
            path: `${BACKUP_DIR}/hagane_backup_corrupt.json`,
            data: rawData,
            directory: Directory.Documents,
            encoding: Encoding.UTF8,
          });
        } catch {
          // ignore
        }
        return {
          version: 1,
          timestamp: 0,
          routines: [],
          isCorrupted: true,
        };
      }
    }
    return null;
  } catch {
    // Backup file does not exist yet on this device
    return null;
  }
}
