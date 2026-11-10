# ⌚ Hagane — Garmin Forerunner 255 Music (46mm) App

Custom English-only **Monkey C** strength-training watch app (`type="watch-app"`) designed specifically for the **Garmin Forerunner 255 Music (`260 × 260 px` MIP screen, 5 physical buttons)** and paired directly with the **Hagane Android App**.

---

## ✨ Key Features

- **Appears in Activities List**: Press **START** on your Forerunner 255 Music -> scroll to **Hagane** right alongside *Run*, *Jump Rope*, and *Bike*.
- **Watch-Initiated Sync (Phone App in Background or Open)**:
  - The Hagane Android app passively caches your latest routines and listens for sync requests whenever the app is running or open in the background.
  - Whenever you open **Hagane** on your watch (or **hold `UP`** on the watch's routine list), the watch asks your paired phone to transmit the cached routines and saves them offline on your wrist. If the phone app has been force-closed or killed by Android battery optimization, simply launch Hagane on your phone once to reconnect the BLE listener.
- **Strictly English-Only UI**: All watch screens and synced exercise/routine payloads use clean English/ASCII text for crisp rendering on the Forerunner 255 Music MIP display.
- **Per-Exercise Custom Rest Timer + Overtime**:
  - Each exercise has its own rest time (e.g., `2:30` for heavy compounds, `1:30` for isolation, `1:00` for warm-ups).
  - **Superset Aware**: Finishing Set 1 of `3A` steps immediately to `3B` (`0s` rest), and triggers the rest timer only after `3B`.
  - **Early Set Start**: Press **START** at any time during the rest countdown to jump into the next set early.
  - **Rest Complete Vibration + Overtime (`+00:01`)**: When the countdown reaches `00:00`, the watch fires a strong multi-pulse wrist vibration and counts up overtime (`+00:01`, `+00:02`...) in yellow/orange until you press **START** to begin your next set.
  - **Live `±15s` Adjustment**: Press **UP** (`+15s`) or **DOWN** (`-15s`) during rest to adjust the timer on the fly.
- **Log what you really lifted**: on the set screen **UP/DOWN** change the reps by ±1 (changed numbers turn orange). Different weight? Pause menu → **Edit Weight** (±2.5 kg, applies to the remaining sets of that exercise). The logged values go to the FIT file and Garmin Connect.
- **Switch Exercise Mid-Workout**: Machine busy? **Hold `UP`** during a set or rest to pick another exercise. When you finish it, Hagane takes you back to the exercise you left (supersets stay together).
- **Rest Cues**: One buzz at 10s left, one per second for the last 3s, and the full pattern at `00:00`. The rest screen also shows how far your heart rate has dropped from the set's peak.
- **Resume After Exit**: If the app is closed or killed mid-workout, the next launch offers **START: Resume** / **BACK: Discard**. Progress is kept on the watch only and expires after 6 hours.
- **Native `.FIT` Strength Activity Recording**: Records live wrist Heart Rate, total elapsed time, and set laps into Garmin Connect.

---

## 🎮 Forerunner 255 Music Button Map

| Physical Button | Routine List | Active Set | Rest Timer | Pause Menu |
| :--- | :--- | :--- | :--- | :--- |
| **START** *(Top-Right)* | Start selected routine *(or Sync if empty)* | **Finish Set** -> Start Rest (or next Superset exercise) | **Begin Next Set** (early or after `00:00`) | Select menu action |
| **BACK** *(Bottom-Right)* | Exit app | Open **Pause Menu** | Open **Pause Menu** | Resume workout |
| **UP** *(Middle-Left)* | Previous routine *(Hold: Sync from Phone)* | **+1 rep** *(Hold: Switch exercise)* | **`+15s`** rest time *(Hold: Switch exercise)* | Move cursor up |
| **DOWN** *(Bottom-Left)* | Next routine | **-1 rep** | **`-15s`** rest time | Move cursor down |

---

## 🚀 How to Build & Install (Both Methods Supported!)

Both methods share the exact same App UUID (`a3f5c8d2-7b1e-4f9a-8c2d-5e6f7a8b9c0d`), so background sync via Garmin Connect works identically with either method.

### Prerequisites (One-Time Setup on macOS/Windows/Linux)
1. Install the official **[Garmin Connect IQ SDK Manager](https://developer.garmin.com/connect-iq/sdk/)**.
2. Open the SDK Manager -> download the latest **Connect IQ SDK** and in the **Devices** tab download **Forerunner 255 Music** (`fr255m`) and **Forerunner 255** (`fr255`).
3. Run the build script:
   ```bash
   cd garmin-watch
   chmod +x build.sh
   ./build.sh
   ```
   This generates a persistent signing key (`garmin-watch/developer_key.der` — back this file up so future updates share the same signing identity) and builds:
   - `garmin-watch/dist/Hagane.prg` (for Method 1: USB Sideload)
   - `garmin-watch/dist/Hagane.iq` (for Method 2: Private Beta Wireless Install)

---

### Method 1: Instant USB Sideload (`Hagane.prg`)
1. Plug your **Forerunner 255 Music** into your computer using the Garmin USB cable.
2. Copy `garmin-watch/dist/Hagane.prg` into the **`GARMIN/APPS/`** folder on the watch drive.
   *(Note for macOS: Because the watch is an MTP music device, use free **[OpenMTP](https://openmtp.ganeshrvel.com/)** or **Android File Transfer** to drag `Hagane.prg` into `GARMIN/APPS/`).*
3. Unplug the watch -> press **START** -> **Hagane** is immediately in your Activities list!

---

### Method 2: Wireless Private Beta Store Install (`Hagane.iq`)
1. Go to **[apps.garmin.com](https://apps.garmin.com/)** -> Sign in with your Garmin account -> **Upload App**.
2. Upload `garmin-watch/dist/Hagane.iq`.
3. Check the **"Beta App"** checkbox -> Submit.
4. It is approved **instantly (0-minute wait, private to your account only)**. Open the **Connect IQ Store** app on your phone and tap **Install** to beam it to your watch over Bluetooth!
