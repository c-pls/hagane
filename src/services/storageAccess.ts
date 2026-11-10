import { Capacitor, registerPlugin } from '@capacitor/core';

export interface StorageAccessStatus {
  /** True on Android 11+ where public Documents needs "All files access". */
  needsAllFilesAccess: boolean;
  granted: boolean;
}

interface StorageAccessPluginInterface {
  getStatus(): Promise<StorageAccessStatus>;
  openSettings(): Promise<void>;
}

const StorageAccessNative = registerPlugin<StorageAccessPluginInterface>('StorageAccess');

export async function getAllFilesAccessStatus(): Promise<StorageAccessStatus> {
  if (Capacitor.getPlatform() !== 'android') {
    return { needsAllFilesAccess: false, granted: true };
  }
  try {
    return await StorageAccessNative.getStatus();
  } catch (err) {
    console.warn('[Hagane] Could not read All files access status:', err);
    return { needsAllFilesAccess: false, granted: false };
  }
}

export async function openAllFilesAccessSettings(): Promise<void> {
  await StorageAccessNative.openSettings();
}
