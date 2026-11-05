import { Capacitor } from '@capacitor/core';
import { StatusBar, Style } from '@capacitor/status-bar';

/**
 * Triggers a light tactile feedback tick (e.g. for + / - weight/reps, buttons).
 * Disabled per user preference (silent/no vibration).
 */
export const triggerHapticLight = async () => {
  // Haptic vibration disabled
};

/**
 * Triggers a medium tactile feedback pulse (e.g. for drag & drop reordering, card actions).
 * Disabled per user preference (silent/no vibration).
 */
export const triggerHapticMedium = async () => {
  // Haptic vibration disabled
};

/**
 * Triggers a subtle selection click (e.g. tab switch, language switcher).
 * Disabled per user preference (silent/no vibration).
 */
export const triggerHapticSelection = async () => {
  // Haptic vibration disabled
};

/**
 * Configures the native mobile status bar to match Shaken's light theme.
 */
export const initNativeStatusBar = async () => {
  if (!Capacitor.isNativePlatform()) return;
  try {
    await StatusBar.setStyle({ style: Style.Light });
    await StatusBar.setBackgroundColor({ color: '#FFFFFF' });
    await StatusBar.setOverlaysWebView({ overlay: false });
  } catch (err) {
    console.debug('StatusBar configuration not supported', err);
  }
};
