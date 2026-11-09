#!/usr/bin/env python3
"""
NOTE: This script is [FROZEN] and was originally used for initial bootstrapping and asset fetching.
The canonical source of truth for the Hagane 197 offline curated exercises
(including all bilingual Vietnamese translations, verified anatomy mappings,
and video associations) is `scripts/curated_vi_snapshot.json`.
To restore or verify the exercises database, run `python3 scripts/restore_exercises.py`.

Recorded Divergences from Raw Upstream Database:
1. Bilingual Vietnamese Translations: The raw upstream source contains only English text.
   All Vietnamese names (nameVi), step-by-step translations (stepsVi: prepare, execution,
   breathing), and localized gym cues are curated exclusively in `scripts/curated_vi_snapshot.json`.
2. Curated Custom Entries & 4 ID Schemes: Hagane features 197 total curated exercises across 4 ID schemes:
   175 numeric IDs (min 0025, max 3012; 165 selected by the equipment filter, 7 curated bodyweight staples,
   and 3 curated-only numeric entries: 0380, 0576, 0587), 13 `drv-*` entries (all present in upstream free-exercise-db),
   1 legacy `new-dumbbell-sumo-squat` entry (present in upstream), and 8 custom `famous-*` entries with bundled
   offline videos (which do not exist in upstream). The upstream filter selects 179 exercises in total
   (165 numeric + 13 `drv-*` + 1 `new-*`).
3. Strict Bodyweight Selection: Raw database contains hundreds of bodyweight movements, whereas
   Hagane curates top staple exercises with high-fidelity offline video demonstrations. Specifically,
   7 curated bodyweight staples (0284, 0474, 0705, 0796, 0826, 0851, 1764) extend beyond the simple
   name-matching filter.
4. Anatomy Mapping & Categories:
   - Adductors are mapped to category 'Glutes' with slug 'adductors'.
   - 'core' is mapped to 'Abs' / slug 'abs' to ensure 1:1 parity with the SVG anatomical map.
   - 'serratus anterior' is mapped to 'Serratus Anterior' / slug 'serratus' under category 'Core' (corresponding to the dedicated serratus anterior ribcage paths in anatomyPaths.ts).
   - 'ankle stabilizers' and 'ankles' are mapped to 'Tibialis' / slug 'tibialis' under category 'Calves'.
   - Barbell back and front squats curate Quads and Glutes as primary, with Adductors and Lower Back as secondary.
   - Refiled exercises: Deadlifts (conventional refiled under Hamstrings), Battling Ropes (Cardio), Wrist Curls (Forearms), Clean and Press (Shoulders), 0598 Seated Hip Adduction (Glutes-first), 1328 Lying Rear Delt Row (Shoulders / primary Delts / secondary Upper Back, Biceps).
   - Curated Multi-Primary Form:
     * 0296 Close-Grip Press (Dumbbell): curated Chest / ['Chest', 'Triceps'] vs upstream Triceps.
     * 0116 Barbell RDL and 1757 Single-Leg RDL: curated multi-primary ['Hamstrings', 'Glutes'] vs upstream single ['Hamstrings'].
     * 0300 Dumbbell Deadlift, 0432 Dumbbell RDL, drv-kettlebell-deadlift: curated Hamstrings / ['Hamstrings', 'Glutes', 'Lower Back'] vs upstream Glutes.
     * 0028 Clean and Press: curated Shoulders / ['Shoulders', 'Quads', 'Glutes', 'Traps'] vs upstream Quads.
     * 0752 Smith Deadlift: curated Hamstrings / ['Hamstrings', 'Glutes', 'Lower Back'] vs upstream Back / erectors.
     * 1328 Lying Rear Delt Row: curated category Shoulders / primary ['Delts'] (slug 'deltoids') / secondaries ['Upper Back', 'Biceps'] (slugs ['upper-back', 'biceps']) vs upstream Back / ['Upper Back'].
   - Curated Granularity vs Upstream Specificity & Secondary Muscle Curations:
     Upstream muscle strings distinguish 'anterior deltoids' and 'rear deltoids' / 'posterior deltoids',
     whereas Hagane curates generalized 'Delts' for secondaries in 24 exercises (e.g. 0301, 0027, 0208; while 0296 retains specific 'Front Delts').
     Similarly, 'upper pectorals' is curated as 'Chest' in 0553 and 1299, and 0705 Side Plank curates secondaries
     ['Abs', 'Glutes'] rather than upstream quadratus lumborum/shoulders.
     Additional 14 curated secondary-muscle adjustments:
     * 0082, 0364: curated ['Biceps'] vs upstream []
     * 1393: curated ['Tibialis'] vs upstream []
     * 0300: curated ['Forearms'] vs upstream ['Hamstrings', 'Lower Back']
     * 0397: curated ['Biceps'] vs upstream ['Forearms']
     * 0028: curated ['Hamstrings', 'Lower Back', 'Triceps', 'Forearms'] vs upstream ['Hamstrings', 'Glutes', 'Shoulders', 'Triceps']
     * 1452: curated ['Obliques'] vs upstream ['Obliques', 'Hip Flexors']
     * 0128: curated ['Delts', 'Forearms', 'Abs'] vs upstream ['Forearms', 'Abs']
     * 2612: curated ['Calves', 'Quads', 'Shoulders'] vs upstream ['Calves', 'Quads', 'Hamstrings', 'Glutes']
     * 0284: curated ['Tibialis'] vs upstream ['Hamstrings', 'Glutes']
     * 0796: curated ['Lats', 'Shoulders', 'Obliques'] vs upstream ['Lats', 'Chest', 'Delts']
     * 0826: curated ['Hip Flexors', 'Obliques'] vs upstream ['Hip Flexors']
     * 0851: curated ['Abs', 'Calves'] vs upstream ['Glutes', 'Hamstrings', 'Calves']
     * 1764: curated ['Hip Flexors', 'Obliques', 'Forearms'] vs upstream ['Hip Flexors', 'Lower Back']
     * Equipment for 0128 (Battling Ropes) and 2612 (Jump Rope) is normalized to 'Cardio' (upstream has raw string 'rope').
     * Fallback for any unmapped muscle string logs a warning and maps to ('Full Body', 'cardio', 'Cardio').
   - Anatomically Corrected & Tailored Descriptions:
     * 0082 Reverse Wrist Curl: curated "A wrist extension exercise performed with a pronated grip to target the forearm extensors." (corrects upstream anatomically erroneous "flexion").
     * drv-triceps-dips Parallel Bar Dips: curated "A compound bodyweight exercise performed on parallel dip bars targeting the triceps with an upright torso and elbows tucked" (tailored compound triceps cues).
5. In-flight Video Verification: Failed video downloads do not create phantom exercise entries;
   only exercises whose video files exist on disk in `public/videos/` are retained.
6. Steps Formatting: Raw dataset has single-string steps; Hagane structures them into tripartite
   prepare, execution, and breathing lists with specific technique & avoidance cues. The fetch script
   merges the curated bilingual nameVi and stepsVi fields directly from scripts/curated_vi_snapshot.json
   to build all 15 required keys.
7. Breathing Guidance: Specific rhythmic breathing cues are authored per movement pattern; when upstream
   omits breathing instructions, a standardized rhythmic breathing template is used as fallback.
8. Standardized Gym Display Names: Names follow concise gym-native conventions (e.g. "Chest-Supported Row (Dumbbell)").
"""

import concurrent.futures
import json
import re
import struct
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = ROOT / "public" / "videos"
DATA_DIR = ROOT / "src" / "data"

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

# Friendly gym display name overrides aligned with current curated data
DISPLAY_NAME_OVERRIDES = {
    "0327": "Chest-Supported Row (Dumbbell)",
    "1330": "Chest-Supported Hammer Row (Dumbbell)",
    "1349": "Reverse T-Bar Row (Machine)",
    "drv-lever-t-bar-row": "Chest-Supported T-Bar Row (Machine)",
    "0248": "Seal Row - Lying Row (Barbell)",
    "0061": "Skullcrusher (EZ-Bar)",
    "drv-lever-pec-deck-fly": "Pec Deck Fly (Machine)",
    "0585": "Leg Extension (Machine)",
    "0586": "Lying Leg Curl (Machine)",
    "0599": "Seated Leg Curl (Machine)",
    "0582": "Kneeling Leg Curl (Machine)",
    "0581": "High Row (Machine)",
    "0584": "Lateral Raise (Machine)",
    "0592": "Preacher Curl (Machine)",
    "0602": "Rear Delt Reverse Fly - Pec Deck (Machine)",
    "1299": "Incline Chest Press (Machine)",
    "0577": "Chest Press (Machine)",
    "0597": "Seated Hip Abduction (Machine)",
    "0598": "Seated Hip Adduction (Machine)",
    "0594": "Seated Calf Raise (Machine)",
    "0605": "Standing Calf Raise (Machine)",
    "1451": "Seated Triceps Dip (Machine)",
    "0607": "Triceps Extension (Machine)",
    "0743": "Hack Squat (Machine)",
    "0740": "45° Wide Leg Press (Machine)",
    "2611": "Horizontal Leg Press (Machine)",
    "drv-close-feet-leg-press": "Close-Stance Leg Press (Machine)",
}

# Mapping from raw dataset muscle names to (Display Name, SVG Anatomy Slug, Category Filter)
MUSCLE_MAP = {
    "quads": ("Quads", "quadriceps", "Quads"),
    "quadriceps": ("Quads", "quadriceps", "Quads"),
    "quadriceps femoris": ("Quads", "quadriceps", "Quads"),
    "glutes": ("Glutes", "gluteal", "Glutes"),
    "gluteus maximus": ("Glutes", "gluteal", "Glutes"),
    "gluteus medius": ("Glutes", "gluteal", "Glutes"),
    "gluteus minimus": ("Glutes", "gluteal", "Glutes"),
    "abductors": ("Glutes", "gluteal", "Glutes"),
    "hamstrings": ("Hamstrings", "hamstring", "Hamstrings"),
    "adductors": ("Adductors", "adductors", "Glutes"),
    "adductor group": ("Adductors", "adductors", "Glutes"),
    "hip adductors": ("Adductors", "adductors", "Glutes"),
    "adductor muscles": ("Adductors", "adductors", "Glutes"),
    "calves": ("Calves", "calves", "Calves"),
    "gastrocnemius": ("Calves", "calves", "Calves"),
    "soleus": ("Calves", "calves", "Calves"),
    "tibialis anterior": ("Tibialis", "tibialis", "Calves"),
    "pectorals": ("Chest", "chest", "Chest"),
    "pectoralis major": ("Chest", "chest", "Chest"),
    "pectoralis major, clavicular head": ("Chest", "chest", "Chest"),
    "chest": ("Chest", "chest", "Chest"),
    "upper chest": ("Upper Chest", "chest", "Chest"),
    "upper pectorals": ("Upper Chest", "chest", "Chest"),
    "lower chest": ("Lower Chest", "chest", "Chest"),
    "serratus anterior": ("Serratus Anterior", "serratus", "Core"),
    "lats": ("Lats", "upper-back", "Back"),
    "latissimus dorsi": ("Lats", "upper-back", "Back"),
    "upper back": ("Upper Back", "upper-back", "Back"),
    "rhomboids": ("Upper Back", "upper-back", "Back"),
    "rhomboids, trapezius, latissimus dorsi": ("Upper Back", "upper-back", "Back"),
    "middle back": ("Upper Back", "upper-back", "Back"),
    "teres major": ("Upper Back", "upper-back", "Back"),
    "traps": ("Traps", "trapezius", "Back"),
    "trapezius": ("Traps", "trapezius", "Back"),
    "upper trapezius": ("Traps", "trapezius", "Back"),
    "middle trapezius": ("Traps", "trapezius", "Back"),
    "lower trapezius": ("Traps", "trapezius", "Back"),
    "levator scapulae": ("Traps", "trapezius", "Back"),
    "lower back": ("Lower Back", "lower-back", "Back"),
    "erector spinae": ("Lower Back", "lower-back", "Back"),
    "erectors": ("Lower Back", "lower-back", "Back"),
    "quadratus lumborum": ("Lower Back", "lower-back", "Back"),
    "spine": ("Lower Back", "lower-back", "Back"),
    "delts": ("Delts", "deltoids", "Shoulders"),
    "deltoids": ("Delts", "deltoids", "Shoulders"),
    "deltoideus": ("Delts", "deltoids", "Shoulders"),
    "deltoid": ("Delts", "deltoids", "Shoulders"),
    "shoulders": ("Shoulders", "deltoids", "Shoulders"),
    "anterior deltoid": ("Front Delts", "deltoids", "Shoulders"),
    "anterior deltoids": ("Front Delts", "deltoids", "Shoulders"),
    "deltoid anterior": ("Front Delts", "deltoids", "Shoulders"),
    "front delts": ("Front Delts", "deltoids", "Shoulders"),
    "lateral deltoid": ("Delts", "deltoids", "Shoulders"),
    "posterior deltoid": ("Rear Delts", "deltoids", "Shoulders"),
    "posterior deltoids": ("Rear Delts", "deltoids", "Shoulders"),
    "rear delts": ("Rear Delts", "deltoids", "Shoulders"),
    "rear deltoids": ("Rear Delts", "deltoids", "Shoulders"),
    "rotator cuff": ("Shoulders", "deltoids", "Shoulders"),
    "biceps": ("Biceps", "biceps", "Biceps"),
    "biceps brachii": ("Biceps", "biceps", "Biceps"),
    "brachialis": ("Biceps", "biceps", "Biceps"),
    "triceps": ("Triceps", "triceps", "Triceps"),
    "triceps brachii": ("Triceps", "triceps", "Triceps"),
    "forearms": ("Forearms", "forearm", "Forearms"),
    "brachioradialis": ("Forearms", "forearm", "Forearms"),
    "wrist flexors": ("Forearms", "forearm", "Forearms"),
    "wrist extensors": ("Forearms", "forearm", "Forearms"),
    "forearm flexors": ("Forearms", "forearm", "Forearms"),
    "forearm extensors": ("Forearms", "forearm", "Forearms"),
    "abs": ("Abs", "abs", "Core"),
    "abdominals": ("Abs", "abs", "Core"),
    "rectus abdominis": ("Abs", "abs", "Core"),
    "core": ("Abs", "abs", "Core"),
    "core stabilizers": ("Abs", "abs", "Core"),
    "transverse abdominis": ("Abs", "abs", "Core"),
    "obliques": ("Obliques", "obliques", "Core"),
    "external obliques": ("Obliques", "obliques", "Core"),
    "obliquus externus abdominis": ("Obliques", "obliques", "Core"),
    "hip flexors": ("Hip Flexors", "hip-flexors", "Core"),
    "iliopsoas": ("Hip Flexors", "hip-flexors", "Core"),
    "ankle stabilizers": ("Tibialis", "tibialis", "Calves"),
    "ankles": ("Tibialis", "tibialis", "Calves"),
    "cardiovascular system": ("Cardio", "cardio", "Cardio"),
    "anconeus": ("Triceps", "triceps", "Triceps"),
    "flexor carpi radialis": ("Forearms", "forearm", "Forearms"),
    "flexor carpi ulnaris": ("Forearms", "forearm", "Forearms"),
    "achilles tendon": ("Calves", "calves", "Calves"),
    "full body": ("Full Body", "cardio", "Cardio"),
    "groin": ("Adductors", "adductors", "Glutes"),
    "hip abductors": ("Glutes", "gluteal", "Glutes"),
    "infraspinatus": ("Shoulders", "deltoids", "Shoulders"),
    "intercostals": ("Abs", "abs", "Core"),
    "lower abdominals": ("Abs", "abs", "Core"),
    "lower abs": ("Abs", "abs", "Core"),
    "neck flexors": ("Neck", "neck", "Back"),
    "peroneals": ("Calves", "calves", "Calves"),
    "piriformis": ("Glutes", "gluteal", "Glutes"),
    "rectus femoris": ("Quads", "quadriceps", "Quads"),
    "rhoboids": ("Upper Back", "upper-back", "Back"),
    "scalenes": ("Neck", "neck", "Back"),
    "spinal erectors": ("Lower Back", "lower-back", "Back"),
    "sternocleidomastoid": ("Neck", "neck", "Back"),
    "tensor fasciae latae": ("Glutes", "gluteal", "Glutes"),
    "thoracic spine": ("Upper Back", "upper-back", "Back"),
    "tibialis posterior": ("Tibialis", "tibialis", "Calves"),
    "varies by machine": ("Full Body", "cardio", "Cardio"),
    "varies by machine (legs, glutes, arms)": ("Full Body", "cardio", "Cardio"),
    "varies by movement": ("Full Body", "cardio", "Cardio"),
    "vastus medialis": ("Quads", "quadriceps", "Quads"),
}

CARDIO_SKIP_IDS = {
    "drv-cardio-exercises-machine",
    "drv-cardio-exercises-machines",
    "2141",  # Elliptical
    "2138",  # Stationary Bike
    "drv-treadmill-running",
    "drv-walk-wave-machine",
}


def map_muscle(raw_name: str):
    key = raw_name.strip().lower()
    if key in MUSCLE_MAP:
        return MUSCLE_MAP[key]
    print(f"⚠️ Unmapped muscle string: '{raw_name}', falling back to ('Full Body', 'cardio', 'Cardio')")
    return ("Full Body", "cardio", "Cardio")


def normalize_equipment(eq: str) -> str:
    e = eq.strip().lower()
    if "cardio" in e or "jump rope" in e or "battling rope" in e or e == "rope":
        return "Cardio"
    if "barbell" in e and "ez" not in e:
        return "Barbell"
    if "ez" in e:
        return "EZ-Bar"
    if "dumbbell" in e:
        return "Dumbbell"
    if "cable" in e or "rope" in e:
        return "Cable"
    if "machine" in e or "sled" in e or "leverage" in e or "smith" in e:
        return "Machine"
    if "kettlebell" in e:
        return "Kettlebell"
    return "Bodyweight"


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def select_all_gym_exercises(all_exercises):
    target_equipments = {
        "barbell",
        "dumbbell",
        "leverage machine",
        "sled machine",
        "smith machine",
        "cable",
        "rope",
        "ez barbell",
        "kettlebell",
    }

    bodyweight_staples = [
        "pull-up",
        "chin-up",
        "dip",
        "push-up",
        "hanging leg raise",
        "inverted row",
    ]

    selected = []
    for ex in all_exercises:
        if ex["id"] in CARDIO_SKIP_IDS:
            continue
        if not (isinstance(ex.get("videos"), dict) and ex["videos"].get("male", "").endswith(".mp4")):
            continue

        eq_l = ex.get("equipment", "").lower()
        name_l = ex.get("name", "").lower()

        if eq_l in target_equipments:
            selected.append(ex)
        elif eq_l in {"body weight", "weighted"} and any(kw in name_l for kw in bodyweight_staples):
            selected.append(ex)

    eq_rank = {
        "barbell": 0,
        "dumbbell": 1,
        "leverage machine": 2,
        "sled machine": 2,
        "smith machine": 3,
        "cable": 4,
        "rope": 4,
        "ez barbell": 5,
        "kettlebell": 6,
        "weighted": 7,
        "body weight": 8,
    }

    selected.sort(key=lambda x: (eq_rank.get(x.get("equipment", "").lower(), 9), x.get("name", "").lower()))
    return selected


def is_valid_mp4(path: Path) -> bool:
    """Validate that path exists, has sufficient size (>=50KB), and is a complete, non-truncated MP4 container.

    Walks all top-level boxes (ftyp, moov, mdat, etc.) and asserts:
    1. Every box has valid length >= 8.
    2. No box exceeds physical file bounds (detects any truncation, even if >=50KB).
    3. Mandatory boxes (ftyp, moov, and mdat) are all present.
    4. Total walked box length matches physical file size exactly (offset == size).
    """
    if not path.is_file():
        return False
    try:
        size = path.stat().st_size
        if size < 50000:
            return False
        with open(path, "rb") as f:
            offset = 0
            has_ftyp = False
            has_moov = False
            has_mdat = False
            while offset < size:
                f.seek(offset)
                hdr = f.read(8)
                if len(hdr) < 8:
                    return False
                box_size, box_type = struct.unpack(">I4s", hdr)
                if box_size == 1:
                    hdr64 = f.read(8)
                    if len(hdr64) < 8:
                        return False
                    box_size = struct.unpack(">Q", hdr64)[0]
                elif box_size == 0:
                    box_size = size - offset

                if box_size < 8:
                    return False
                if offset + box_size > size:
                    # File is truncated
                    return False

                if box_type == b"ftyp":
                    has_ftyp = True
                elif box_type == b"moov":
                    has_moov = True
                elif box_type == b"mdat":
                    has_mdat = True

                offset += box_size

            return has_ftyp and has_moov and has_mdat and offset == size
    except Exception:
        return False


def download_video(task):
    ex_id, url, dest_path = task
    if is_valid_mp4(dest_path):
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
            if len(data) >= 50000 and b"ftyp" in data[:128]:
                dest_path.write_bytes(data)
                if is_valid_mp4(dest_path):
                    return True
                dest_path.unlink(missing_ok=True)
        return False
    except Exception as exc:
        print(f"Failed downloading {ex_id} ({url}): {exc}")
        if dest_path.is_file():
            dest_path.unlink(missing_ok=True)
        return False


def main():
    out_json = DATA_DIR / "exercises.json"
    if out_json.exists():
        print(f"[FROZEN] {out_json} already exists with curated bilingual content. Overwrite blocked to protect hand-curated translations.")
        return
    print("Fetching exercise dataset...")
    raw_url = "https://raw.githubusercontent.com/harshvishu/free-exercise-db-with-videos/main/data/exercises.json"
    all_exercises = fetch_json(raw_url)

    selected = select_all_gym_exercises(all_exercises)
    print(f"Selected {len(selected)} total Barbell, Dumbbell, Machine, Cable, EZ-Bar, Kettlebell & Staple exercises.")

    download_tasks = []
    formatted_exercises = []

    curated_map = {}
    snap_path = ROOT / "scripts" / "curated_vi_snapshot.json"
    if snap_path.is_file():
        try:
            snap_data = json.loads(snap_path.read_text(encoding="utf-8"))
            if isinstance(snap_data, dict):
                curated_map = snap_data
            elif isinstance(snap_data, list):
                curated_map = {row["id"]: row for row in snap_data}
            print(f"Loaded {len(curated_map)} bilingual exercises from snapshot.")
        except Exception as e:
            print(f"⚠️ Could not load snapshot for bilingual fields: {e}")

    for ex in selected:
        ex_id = str(ex["id"])
        raw_name = ex["name"]
        display_name = DISPLAY_NAME_OVERRIDES.get(ex_id, raw_name)

        safe_slug = re.sub(r"[^a-z0-9-]+", "-", raw_name.lower()).strip("-")
        video_filename = f"{safe_slug}-{ex_id}.mp4"
        video_dest = VIDEOS_DIR / video_filename
        male_url = ex["videos"]["male"]

        download_tasks.append((ex_id, male_url, video_dest))

        p_disp, p_slug, category = map_muscle(ex.get("target") or ex.get("muscleGroup") or "Core")
        primary_muscles = [p_disp]
        primary_slugs = [p_slug]

        secondary_muscles = []
        secondary_slugs = []
        for sm in ex.get("secondaryMuscles", []):
            s_disp, s_slug, _ = map_muscle(sm)
            if (
                s_disp not in primary_muscles
                and s_disp not in secondary_muscles
                and s_slug not in primary_slugs
                and s_slug not in secondary_slugs
            ):
                secondary_muscles.append(s_disp)
                secondary_slugs.append(s_slug)

        name_l = display_name.lower()
        if "squat" in name_l and "sumo" not in name_l:
            category = "Quads"
            if "Quads" not in primary_muscles:
                if "Glutes" in primary_muscles:
                    primary_muscles.remove("Glutes")
                    if "gluteal" in primary_slugs:
                        primary_slugs.remove("gluteal")
                    if "Glutes" not in secondary_muscles:
                        secondary_muscles.insert(0, "Glutes")
                        secondary_slugs.insert(0, "gluteal")
                if "Quads" in secondary_muscles:
                    secondary_muscles.remove("Quads")
                if "quadriceps" in secondary_slugs:
                    secondary_slugs.remove("quadriceps")
                primary_muscles.insert(0, "Quads")
                primary_slugs.insert(0, "quadriceps")

        if "squat" in name_l and "barbell" in name_l:
            if "Glutes" in secondary_muscles:
                secondary_muscles.remove("Glutes")
            if "gluteal" in secondary_slugs:
                secondary_slugs.remove("gluteal")
            if "Glutes" not in primary_muscles:
                primary_muscles.append("Glutes")
            if "gluteal" not in primary_slugs:
                primary_slugs.append("gluteal")
            for extra_m, extra_s in [("Adductors", "adductors"), ("Lower Back", "lower-back")]:
                if extra_m not in secondary_muscles and extra_m not in primary_muscles:
                    secondary_muscles.append(extra_m)
                if extra_s not in secondary_slugs and extra_s not in primary_slugs:
                    secondary_slugs.append(extra_s)

        # Deduplicate: ensure no muscle or slug in primary appears in secondary
        cleaned_secondaries = [
            (m, s) for m, s in zip(secondary_muscles, secondary_slugs)
            if m not in primary_muscles and s not in primary_slugs
        ]
        secondary_muscles = [m for m, s in cleaned_secondaries]
        secondary_slugs = [s for m, s in cleaned_secondaries]

        raw_steps = ex.get("steps") or []
        form_cues = ex.get("formCues") or []
        mistakes = ex.get("commonMistakes") or []
        breathing_str = ex.get("breathing") or "Inhale on the eccentric (lowering) phase, exhale on the concentric (lifting) phase."

        if len(raw_steps) > 2:
            prepare_steps = raw_steps[:2]
            execution_steps = raw_steps[2:]
        elif len(raw_steps) == 2:
            prepare_steps = [raw_steps[0]]
            execution_steps = [raw_steps[1]]
        elif len(raw_steps) == 1:
            prepare_steps = raw_steps
            execution_steps = [ex.get("instructions", "")] if ex.get("instructions") else []
        else:
            prepare_steps = [ex.get("instructions", "")] if ex.get("instructions") else []
            execution_steps = []
        if form_cues:
            execution_steps = list(execution_steps) + [f"Form cue: {c}" for c in form_cues[:3]]

        breathing_steps = [breathing_str]
        if mistakes:
            breathing_steps.extend([f"Avoid: {m}" for m in mistakes[:2]])

        aliases = list(ex.get("aliases", []))
        if raw_name != display_name and raw_name not in aliases:
            aliases.append(raw_name)

        assert len(primary_muscles) == len(primary_slugs), f"Primary mismatch in {ex_id}"
        assert len(secondary_muscles) == len(secondary_slugs), f"Secondary mismatch in {ex_id}"

        curated_entry = curated_map.get(ex_id, {})
        name_vi = curated_entry.get("nameVi", "")
        steps_vi = curated_entry.get("stepsVi", {
            "prepare": [],
            "execution": [],
            "breathing": [],
        })

        # Explicit refiles & anatomical corrections
        if ex_id == "1328":
            category = "Shoulders"
            primary_muscles = ["Delts"]
            primary_slugs = ["deltoids"]
            secondary_muscles = ["Upper Back", "Biceps"]
            secondary_slugs = ["upper-back", "biceps"]

        short_desc = ex.get("shortDescription", "")
        if ex_id == "0082":
            short_desc = "A wrist extension exercise performed with a pronated grip to target the forearm extensors."
        elif ex_id == "drv-triceps-dips":
            short_desc = "A compound bodyweight exercise performed on parallel dip bars targeting the triceps with an upright torso and elbows tucked."

        # Merge any overrides from curated snapshot
        if "category" in curated_entry:
            category = curated_entry["category"]
        if "primaryMuscles" in curated_entry:
            primary_muscles = list(curated_entry["primaryMuscles"])
        if "primarySlugs" in curated_entry:
            primary_slugs = list(curated_entry["primarySlugs"])
        if "secondaryMuscles" in curated_entry:
            secondary_muscles = list(curated_entry["secondaryMuscles"])
        if "secondarySlugs" in curated_entry:
            secondary_slugs = list(curated_entry["secondarySlugs"])
        if "shortDescription" in curated_entry:
            short_desc = curated_entry["shortDescription"]
        if "name" in curated_entry:
            display_name = curated_entry["name"]
        if "aliases" in curated_entry:
            aliases = list(curated_entry["aliases"])
        if "equipment" in curated_entry:
            equipment_val = curated_entry["equipment"]
        else:
            equipment_val = normalize_equipment(ex.get("equipment", "Bodyweight"))
        if "steps" in curated_entry:
            cur_steps = curated_entry["steps"]
            prepare_steps = list(cur_steps.get("prepare", prepare_steps))
            execution_steps = list(cur_steps.get("execution", execution_steps))
            breathing_steps = list(cur_steps.get("breathing", breathing_steps))

        formatted_exercises.append({
            "id": ex_id,
            "slug": safe_slug,
            "name": display_name,
            "nameVi": name_vi,
            "aliases": aliases,
            "category": category,
            "equipment": equipment_val,
            "videoUrl": f"/videos/{video_filename}",
            "primaryMuscles": primary_muscles,
            "secondaryMuscles": secondary_muscles,
            "primarySlugs": primary_slugs,
            "secondarySlugs": secondary_slugs,
            "shortDescription": short_desc,
            "steps": {
                "prepare": prepare_steps,
                "execution": execution_steps,
                "breathing": breathing_steps,
            },
            "stepsVi": steps_vi,
        })

    print(f"Downloading {len(download_tasks)} male 1080p 30fps MP4 videos concurrently...")
    ok_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for ok in pool.map(download_video, download_tasks):
            if ok:
                ok_count += 1
    print(f"Downloaded {ok_count}/{len(download_tasks)} videos into public/videos/")

    # Merge any curated exercises from snapshot not in the upstream selection (7 bodyweight staples, 3 curated numerics, 8 famous-*)
    selected_ids = {row["id"] for row in formatted_exercises}
    for cid, crow in curated_map.items():
        if cid not in selected_ids:
            formatted_exercises.append(crow)

    verified_exercises = []
    for row in formatted_exercises:
        v_rel = row["videoUrl"].lstrip("/").replace("videos/", "")
        v_path = VIDEOS_DIR / v_rel
        if is_valid_mp4(v_path):
            verified_exercises.append(row)
        else:
            print(f"⚠️ Omitting exercise {row['id']} ({row['name']}): video {v_rel} missing or invalid on disk")

    verified_exercises.sort(key=lambda x: (0, int(x["id"])) if x["id"].isdigit() else (1, x["id"]))

    out_json = DATA_DIR / "exercises.json"
    out_json.write_text(json.dumps(verified_exercises, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(verified_exercises)} verified exercises to src/data/exercises.json")


if __name__ == "__main__":
    main()
