# Hagane — notes for Claude

Context carried over from earlier Claude sessions. Read this first.

## What the project is
Offline-first gym tracker.
- **Phone app**: React + Vite + Tailwind (`src/`), wrapped with Capacitor 8 for Android (`android/`).
  The phone app is only for **organising routines/exercises** and syncing them to the watch.
  It must **not** store workout sessions/history (owner's decision).
- **Watch app**: Monkey C, Garmin Connect IQ, Forerunner 255 / 255 Music (`garmin-watch/`).
  Runs the workout and saves it as a FIT activity to **Garmin Connect**. History lives only there.
- **Android ↔ watch bridge**: custom Capacitor plugin `GarminSyncPlugin.java` (Connect IQ Mobile SDK).
- Repo: `github.com/c-pls/hagane`. Work directly on `main`, no feature branches.

## Commands
- `npm run typecheck`, `npm test` (typecheck + `scripts/restore_exercises.py --check`)
- `npm run build:garmin` → `garmin-watch/build.sh` → `garmin-watch/dist/Hagane.prg` and `Hagane.iq`
  (needs the Connect IQ SDK + fr255/fr255m device profiles from SDK Manager).
- **Always build the watch app after changing `garmin-watch/source/*.mc` and fix compile errors.**
  Recent watch changes were written without a compiler — expect some errors on first build.

## Release / CI
- `.github/workflows/build-apk.yml`: every push to `main` builds a signed APK and creates a GitHub
  release tagged `v1.<run_number>`. App version = `1.<run_number>` (`versionCode` = run number + 9).
- No hardcoded app versions anywhere (removed from package.json, lockfile, Garmin manifest).
- Secrets needed: `ANDROID_KEYSTORE_BASE64`, `RELEASE_KEYSTORE_PASSWORD`, `RELEASE_KEY_PASSWORD`,
  `RELEASE_KEY_ALIAS`. Local release signing can use `android/keystore.properties` (git-ignored).

## Android storage
- Backup to Documents needs "All files access" on Android 11+ (`MANAGE_EXTERNAL_STORAGE`).
  `StorageAccessPlugin.java` opens the settings page; the banner button is "Allow".
  Distributed via GitHub APK (Google Play would restrict this permission).

## Watch app — owner's preferences (important)
- **Text as large as possible** while still fitting the round 260×260 screen. Owner hates small text.
- **Low text**: no hint lines, nothing redundant on screen.
- **Look like Garmin's built-in apps.** Use native components where they exist
  (`WatchUi.Menu2`, `IconMenuItem`, `Confirmation`). Custom-drawn screens only where Garmin has no
  component (set, rest/GET READY, edit weight, summary, routine list, resume prompt).
- Moving to a new set is **always manual** (START). After the last set of an exercise there is
  no rest: a **GET READY** wait screen instead. Same after switching exercise, skip, undo, resume.
- Long names **scroll right-to-left** (marquee in `HaganeWatchView.drawFitText`), not truncated.

## Watch app — behaviour
- Files: `HaganeWorkoutState.mc` (state machine, FIT recording, sync, progress),
  `HaganeWatchView.mc` (custom screens), `HaganeWatchDelegate.mc` (buttons on custom screens),
  `HaganeNativeUi.mc` (native pause menu, exercise list, Discard? dialog + their delegates),
  `HaganeWatchApp.mc` (lifecycle, phone messages).
- Buttons: START = finish set / start next set; BACK = pause menu; UP/DOWN on set screen = reps ±1
  (changed values turn orange); UP/DOWN on rest = ±15 s; hold UP during set/rest = switch exercise
  (returns to the exercise you left afterwards — `returnStack`); hold UP on list = sync.
- Pause menu: Resume, Exercise, Weight (±2.5 kg, applies to remaining sets of that exercise),
  Undo Set (reopens the last logged set), Skip Set (skips the upcoming set, also from rest),
  Save, Discard. Rest countdown keeps running while the menu is open over the rest screen.
- Set screen: `SET n/m` header, exercise name, `32kg x 10 reps`, set timer, `HR 70`.
- Rest screen: `REST n/m` / `GO! n/m` / `GET READY`, big timer, HR and drop from set peak,
  next exercise, `weight x reps`. Vibration at 10 s left, each of last 3 s, pattern at 0, then one buzz every 15 s of overtime.
- Resume after app exit: progress saved to Storage every 15 s; on launch offers resume (≤ 6 h).
  The first part is saved as its own activity. Edited reps/weights of not-yet-done sets reset.
- Routines from the phone mid-workout are queued and applied after the workout.

- `IconMenuItem` icons must be `WatchUi.Bitmap` drawables, not `loadResource` BitmapResources
  (the latter crash the FR255 with "Symbol Not Found" when the menu draws).

## Known Garmin limitations (don't re-investigate)
- The "Lap 1 …" pop-up/voice after each set is from the watch firmware on `addLap()`; a CIQ app
  can't rename or hide it. Owner chose to keep per-set laps.
- Garmin Connect's native strength "Exercises/Sets" table can't be filled by CIQ apps (no FIT `set`
  messages). Per-set data is in lap developer fields; totals show in the "Connect IQ" stats block.
  Owner accepted: detailed per-exercise review is on the watch summary only.
- Vector fonts (Garmin's bold condensed look) would need minApiLevel ≥ 4 — not done; minApiLevel is 3.2.0.

## Docs
- `garmin-watch/USER_GUIDE.md` — user guide; keep it in sync with behaviour changes.
- `garmin-watch/store/STORE_DESCRIPTION.txt`, `STORE_WHATS_NEW.txt` — Connect IQ store text
  (plain text, one short paragraph per feature; the store collapses single line breaks).

## Open items
- Build and test the latest watch changes on the device (native menus, marquee, review fixes).
