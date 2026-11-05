import { Filesystem, Directory, Encoding } from '@capacitor/filesystem';
import { Capacitor } from '@capacitor/core';
import { Routine, Exercise } from '../types/gym';

const BACKUP_DIR = 'Shaken';
const BACKUP_FILE = 'shaken_backup.json';

export interface ShakenDeviceBackup {
  version: number;
  timestamp: number;
  routines: Routine[];
  comments?: Record<string, string>;
  customExercises?: Exercise[];
}

/**
 * Automatically persist routines to the physical device's public Documents directory.
 * This storage is NOT deleted when the app is uninstalled on Android, allowing
 * seamless restoration even after a complete app uninstall/reinstall.
 */
export async function autoSaveToDevice(
  routines: Routine[],
  comments: Record<string, string> = {},
  customExercises: Exercise[] = []
): Promise<boolean> {
  if (!Capacitor.isNativePlatform()) {
    return false;
  }

  try {
    const payload: ShakenDeviceBackup = {
      version: 1,
      timestamp: Date.now(),
      routines,
      comments,
      customExercises,
    };

    const data = JSON.stringify(payload, null, 2);

    // Ensure the Shaken folder exists in Documents
    try {
      await Filesystem.mkdir({
        path: BACKUP_DIR,
        directory: Directory.Documents,
        recursive: true,
      });
    } catch {
      // directory likely already exists
    }

    // Write file to /Documents/Shaken/shaken_backup.json
    await Filesystem.writeFile({
      path: `${BACKUP_DIR}/${BACKUP_FILE}`,
      data,
      directory: Directory.Documents,
      encoding: Encoding.UTF8,
    });

    return true;
  } catch (err) {
    console.warn('[Shaken] Error saving backup to device Documents:', err);
    return false;
  }
}

/**
 * Check and restore routines from the device's public Documents folder.
 * Called on startup when local state is empty or when the user taps "Restore from Device".
 */
export async function autoLoadFromDevice(): Promise<ShakenDeviceBackup | null> {
  if (!Capacitor.isNativePlatform()) {
    return null;
  }

  try {
    const result = await Filesystem.readFile({
      path: `${BACKUP_DIR}/${BACKUP_FILE}`,
      directory: Directory.Documents,
      encoding: Encoding.UTF8,
    });

    if (result && typeof result.data === 'string') {
      const parsed = JSON.parse(result.data) as ShakenDeviceBackup;
      if (parsed && Array.isArray(parsed.routines) && parsed.routines.length > 0) {
        return parsed;
      }
    }
    return null;
  } catch {
    // Backup file does not exist yet on this device
    return null;
  }
}
