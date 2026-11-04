import { Capacitor } from '@capacitor/core';
import { Haptics, ImpactStyle } from '@capacitor/haptics';
import { StatusBar, Style } from '@capacitor/status-bar';

/**
 * Triggers a light tactile feedback tick (e.g. for + / - weight/reps, buttons).
 */
export const triggerHapticLight = async () => {
  try {
    if (Capacitor.isNativePlatform()) {
      await Haptics.impact({ style: ImpactStyle.Light });
    } else if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
      navigator.vibrate(10);
    }
  } catch {
    // Ignore errors on unsupported platforms
  }
};

/**
 * Triggers a medium tactile feedback pulse (e.g. for drag & drop reordering, card actions).
 */
export const triggerHapticMedium = async () => {
  try {
    if (Capacitor.isNativePlatform()) {
      await Haptics.impact({ style: ImpactStyle.Medium });
    } else if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
      navigator.vibrate(25);
    }
  } catch {
    // Ignore errors on unsupported platforms
  }
};

/**
 * Triggers a subtle selection click (e.g. tab switch, language switcher).
 */
export const triggerHapticSelection = async () => {
  try {
    if (Capacitor.isNativePlatform()) {
      await Haptics.selectionStart();
      await Haptics.selectionChanged();
    } else if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
      navigator.vibrate(8);
    }
  } catch {
    // Ignore errors on unsupported platforms
  }
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
