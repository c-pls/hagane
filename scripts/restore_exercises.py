#!/usr/bin/env python3
"""
Hagane — Exercise Wiki & Vietnamese Translation Restore Script.
Restores and verifies curated bilingual data in src/data/exercises.json
using scripts/curated_vi_snapshot.json as the canonical source.
"""

import json
import os
import re
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SNAPSHOT_PATH = os.path.join(SCRIPT_DIR, "curated_vi_snapshot.json")
EXERCISES_PATH = os.path.join(PROJECT_ROOT, "src", "data", "exercises.json")
BAK_PATH = os.path.join(PROJECT_ROOT, "src", "data", "exercises.json.bak")
VIDEOS_DIR = os.path.join(PROJECT_ROOT, "public", "videos")

FAMOUS_VIDEO_MAP = {
    "famous-bb-hip-thrust": "/videos/barbell-hip-thrust.mp4",
    "famous-db-one-arm-row": "/videos/dumbbell-one-arm-row.mp4",
    "famous-bb-sumo-deadlift": "/videos/barbell-sumo-deadlift.mp4",
    "famous-db-flat-bench-press": "/videos/dumbbell-bench-press-flat.mp4",
    "famous-bb-bulgarian-split-squat": "/videos/barbell-bulgarian-split-squat.mp4",
    "famous-bb-conventional-deadlift": "/videos/barbell-conventional-deadlift.mp4",
    "famous-db-bulgarian-split-squat": "/videos/dumbbell-bulgarian-split-squat.mp4",
    "famous-bb-overhand-bent-over-row": "/videos/barbell-overhand-bent-over-row.mp4",
}

EXERCISE_SCHEMA_KEYS = [
    "id",
    "slug",
    "name",
    "nameVi",
    "aliases",
    "category",
    "equipment",
    "videoUrl",
    "primaryMuscles",
    "secondaryMuscles",
    "primarySlugs",
    "secondarySlugs",
    "shortDescription",
    "steps",
    "stepsVi",
]

EXPECTED_MUSCLE_SLUG_MAP = {
    "Abs": "abs",
    "Adductors": "adductors",
    "Biceps": "biceps",
    "Calves": "calves",
    "Cardio": "cardio",
    "Chest": "chest",
    "Delts": "deltoids",
    "Forearms": "forearm",
    "Front Delts": "deltoids",
    "Glutes": "gluteal",
    "Hamstrings": "hamstring",
    "Hip Flexors": "hip-flexors",
    "Lats": "upper-back",
    "Lower Back": "lower-back",
    "Obliques": "obliques",
    "Quads": "quadriceps",
    "Rear Delts": "deltoids",
    "Serratus Anterior": "serratus",
    "Shoulders": "deltoids",
    "Tibialis": "tibialis",
    "Traps": "trapezius",
    "Triceps": "triceps",
    "Upper Back": "upper-back",
    "Upper Chest": "chest",
}

VALID_ANATOMY_SLUGS = {
    "abs",
    "adductors",
    "ankles",
    "biceps",
    "calves",
    "cardio",
    "chest",
    "deltoids",
    "feet",
    "forearm",
    "gluteal",
    "hair",
    "hamstring",
    "hands",
    "head",
    "hip-flexors",
    "knees",
    "lower-back",
    "neck",
    "obliques",
    "quadriceps",
    "serratus",
    "tibialis",
    "trapezius",
    "triceps",
    "upper-back",
}


def derive_safe_slug(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return cleaned or "exercise"


def derive_video_url(ex_id: str, slug: str) -> str:
    if not os.path.isdir(VIDEOS_DIR):
        raise FileNotFoundError(f"Videos directory not found at {VIDEOS_DIR}")
    if ex_id in FAMOUS_VIDEO_MAP:
        return FAMOUS_VIDEO_MAP[ex_id]
    candidate_named = f"/videos/{slug}-{ex_id}.mp4"
    if os.path.isfile(os.path.join(VIDEOS_DIR, f"{slug}-{ex_id}.mp4")):
        return candidate_named
    # Scan VIDEOS_DIR deterministically for any file matching *-[ex_id].mp4 or [ex_id].mp4
    for fname in sorted(os.listdir(VIDEOS_DIR)):
        if fname.endswith(f"-{ex_id}.mp4") or fname == f"{ex_id}.mp4":
            return f"/videos/{fname}"
    if os.path.isfile(os.path.join(VIDEOS_DIR, f"{slug}.mp4")):
        return f"/videos/{slug}.mp4"
    raise FileNotFoundError(
        f"[{ex_id}] Cannot derive valid video URL: no matching video file found in {VIDEOS_DIR}"
    )


def validate_exercise_structure(row: dict, location: str = ""):
    ex_id = row.get("id", "unknown")
    # Schema whitelist
    extra_keys = set(row.keys()) - set(EXERCISE_SCHEMA_KEYS)
    if extra_keys:
        raise ValueError(
            f"{location}[{ex_id}] Unexpected extra keys in exercise data: {sorted(extra_keys)}"
        )
    missing_keys = set(EXERCISE_SCHEMA_KEYS) - set(row.keys())
    if missing_keys:
        raise ValueError(
            f"{location}[{ex_id}] Missing required schema keys: {sorted(missing_keys)}"
        )

    # Core non-empty string fields
    for field in ("name", "nameVi", "category", "equipment", "shortDescription", "videoUrl"):
        val = row.get(field)
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{location}[{ex_id}] Field '{field}' must be a non-empty string!")

    # Muscles and aliases non-empty validation
    primary_muscles = row.get("primaryMuscles")
    primary_slugs = row.get("primarySlugs")
    if not isinstance(primary_muscles, list) or len(primary_muscles) == 0:
        raise ValueError(f"{location}[{ex_id}] primaryMuscles must be a non-empty list!")
    for pm in primary_muscles:
        if not isinstance(pm, str) or not pm.strip():
            raise ValueError(f"{location}[{ex_id}] primaryMuscles entries must be non-empty strings!")
    if not isinstance(primary_slugs, list) or len(primary_slugs) == 0:
        raise ValueError(f"{location}[{ex_id}] primarySlugs must be a non-empty list!")
    for ps in primary_slugs:
        if not isinstance(ps, str) or not ps.strip():
            raise ValueError(f"{location}[{ex_id}] primarySlugs entries must be non-empty strings!")

    secondary_muscles = row.get("secondaryMuscles")
    secondary_slugs = row.get("secondarySlugs")
    if not isinstance(secondary_muscles, list) or len(secondary_muscles) == 0:
        raise ValueError(f"{location}[{ex_id}] secondaryMuscles must be a non-empty list!")
    for sm in secondary_muscles:
        if not isinstance(sm, str) or not sm.strip():
            raise ValueError(f"{location}[{ex_id}] secondaryMuscles entries must be non-empty strings!")
    if not isinstance(secondary_slugs, list) or len(secondary_slugs) == 0:
        raise ValueError(f"{location}[{ex_id}] secondarySlugs must be a non-empty list!")
    for ss in secondary_slugs:
        if not isinstance(ss, str) or not ss.strip():
            raise ValueError(f"{location}[{ex_id}] secondarySlugs entries must be non-empty strings!")

    aliases = row.get("aliases")
    if not isinstance(aliases, list) or len(aliases) == 0:
        raise ValueError(f"{location}[{ex_id}] aliases must be a non-empty list!")
    for a in aliases:
        if not isinstance(a, str) or not a.strip():
            raise ValueError(f"{location}[{ex_id}] aliases entries must be non-empty strings!")

    # Steps validation: prepare, execution, breathing must be non-empty lists in both EN and VI
    for step_field, lang in [("steps", "English"), ("stepsVi", "Vietnamese")]:
        step_dict = row.get(step_field)
        if not isinstance(step_dict, dict):
            raise ValueError(f"{location}[{ex_id}] {step_field} ({lang}) must be an object")
        for subkey in ("prepare", "execution", "breathing"):
            items = step_dict.get(subkey)
            if not isinstance(items, list) or len(items) == 0:
                raise ValueError(
                    f"{location}[{ex_id}] {step_field}.{subkey} ({lang}) must be a non-empty list of steps"
                )
            for s_idx, item in enumerate(items):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(
                        f"{location}[{ex_id}] {step_field}.{subkey}[{s_idx}] ({lang}) must be a non-empty string"
                    )

    # Muscle-Slug pairing validation
    for m_field, s_field in [("primaryMuscles", "primarySlugs"), ("secondaryMuscles", "secondarySlugs")]:
        muscles = row.get(m_field, [])
        slugs = row.get(s_field, [])
        if len(muscles) != len(slugs):
            raise ValueError(
                f"{location}[{ex_id}] {m_field} ({len(muscles)}) and {s_field} ({len(slugs)}) length mismatch!"
            )
        for m, s in zip(muscles, slugs):
            if s not in VALID_ANATOMY_SLUGS:
                raise ValueError(f"{location}[{ex_id}] Unknown anatomy slug '{s}' for muscle '{m}'")
            expected_slug = EXPECTED_MUSCLE_SLUG_MAP.get(m)
            if expected_slug and s != expected_slug:
                raise ValueError(
                    f"{location}[{ex_id}] Muscle '{m}' mapped to slug '{s}', expected '{expected_slug}'"
                )

    # Video file verification on disk
    if not os.path.isdir(VIDEOS_DIR):
        raise FileNotFoundError(f"Videos directory not found at {VIDEOS_DIR}")
    v_url = row.get("videoUrl", "")
    if not v_url.startswith("/videos/"):
        raise ValueError(f"{location}[{ex_id}] Invalid videoUrl format: {v_url}")
    v_filename = v_url.replace("/videos/", "")
    v_path = os.path.join(VIDEOS_DIR, v_filename)
    if not os.path.isfile(v_path):
        raise FileNotFoundError(f"{location}[{ex_id}] Video file not found on disk: {v_path}")


def restore(check_only: bool = False):
    if not os.path.isfile(SNAPSHOT_PATH):
        print(f"❌ Error: Snapshot file not found at {SNAPSHOT_PATH}")
        sys.exit(1)

    def detect_duplicate_keys(pairs):
        res = {}
        for k, v in pairs:
            if k in res:
                raise ValueError(f"Duplicate key detected in {SNAPSHOT_PATH}: '{k}'")
            res[k] = v
        return res

    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snapshot = json.load(f, object_pairs_hook=detect_duplicate_keys)

    if not isinstance(snapshot, dict) or len(snapshot) == 0:
        print("❌ Error: Invalid snapshot format (expected non-empty dict).")
        sys.exit(1)

    print(f"📦 Loaded {len(snapshot)} curated exercises from snapshot.")

    # Validate all snapshot entries against extra schema keys upfront
    for snap_id, snap_entry in snapshot.items():
        if not isinstance(snap_entry, dict):
            raise ValueError(f"Snapshot entry '{snap_id}' is not a dict!")
        extra_keys = set(snap_entry.keys()) - set(EXERCISE_SCHEMA_KEYS)
        if extra_keys:
            raise ValueError(
                f"[{snap_id}] Snapshot contains unexpected extra schema keys: {sorted(extra_keys)}"
            )

    existing_exercises = []
    if os.path.isfile(EXERCISES_PATH):
        with open(EXERCISES_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if not isinstance(loaded, list):
            raise ValueError(
                f"Expected JSON list in {EXERCISES_PATH}, got {type(loaded).__name__}. Refusing to proceed."
            )
        existing_exercises = loaded

    # Check for duplicate IDs in existing file
    existing_ids_list = [ex.get("id") for ex in existing_exercises if isinstance(ex, dict) and "id" in ex]
    if len(existing_ids_list) != len(set(existing_ids_list)):
        dupes = [x for x in existing_ids_list if existing_ids_list.count(x) > 1]
        raise ValueError(f"Duplicate exercise IDs detected in {EXERCISES_PATH}: {sorted(set(dupes))}")

    for idx, ex in enumerate(existing_exercises):
        if not isinstance(ex, dict) or "id" not in ex:
            raise ValueError(f"Existing exercises entry at index {idx} is invalid (missing 'id')")

    existing_map = {ex["id"]: ex for ex in existing_exercises if "id" in ex}
    existing_ids = set(existing_map.keys())
    snapshot_ids = set(snapshot.keys())

    # ID-based coverage guard: refuse silent data drops if existing IDs are missing from snapshot
    missing_from_snapshot = existing_ids - snapshot_ids
    if missing_from_snapshot:
        print(
            f"⚠️ Warning: {len(missing_from_snapshot)} exercises in {EXERCISES_PATH} are missing from snapshot:\n"
            f"   {sorted(missing_from_snapshot)}\n"
            f"   These exercises will be preserved to prevent accidental data loss!"
        )

    merged_list = []
    sort_key = lambda x: (0, int(x)) if x.isdigit() else (1, x)
    all_ids = sorted(list(snapshot_ids | existing_ids), key=sort_key)

    for ex_id in all_ids:
        if ex_id not in snapshot:
            # Preserve non-snapshot existing exercise exactly
            preserved = existing_map[ex_id]
            validate_exercise_structure(preserved, location="Preserved ")
            merged_list.append(preserved)
            continue

        snap_data = snapshot[ex_id]
        base = existing_map.get(ex_id, {})

        if "name" in snap_data:
            name = snap_data["name"]
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"[{ex_id}] Snapshot has missing or empty 'name'!")
        else:
            name = base.get("name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"[{ex_id}] Missing or empty 'name' in exercise data!")

        slug = snap_data.get("slug") or base.get("slug") or derive_safe_slug(name)

        if "nameVi" in snap_data:
            name_vi = snap_data["nameVi"]
            if not isinstance(name_vi, str) or not name_vi.strip():
                raise ValueError(f"[{ex_id}] Snapshot has missing or empty 'nameVi'!")
        else:
            name_vi = base.get("nameVi")
            if not isinstance(name_vi, str) or not name_vi.strip():
                raise ValueError(f"[{ex_id}] Missing or empty 'nameVi' in exercise data!")

        if "category" in snap_data:
            category = snap_data["category"]
            if not isinstance(category, str) or not category.strip():
                raise ValueError(f"[{ex_id}] Snapshot has missing or empty 'category'!")
        else:
            category = base.get("category")
            if not isinstance(category, str) or not category.strip():
                raise ValueError(f"[{ex_id}] Missing or empty 'category' in exercise data!")

        if "equipment" in snap_data:
            equipment = snap_data["equipment"]
            if not isinstance(equipment, str) or not equipment.strip():
                raise ValueError(f"[{ex_id}] Snapshot has missing or empty 'equipment'!")
        else:
            equipment = base.get("equipment")
            if not isinstance(equipment, str) or not equipment.strip():
                raise ValueError(f"[{ex_id}] Missing or empty 'equipment' in exercise data!")

        # Video URL resolution: verify snapshot video exists on disk, otherwise derive
        snap_v = snap_data.get("videoUrl")
        if snap_v and os.path.isfile(os.path.join(VIDEOS_DIR, snap_v.lstrip("/").replace("videos/", ""))):
            video_url = snap_v
        else:
            video_url = derive_video_url(ex_id, slug)

        if "shortDescription" in snap_data:
            short_desc = snap_data["shortDescription"]
            if not isinstance(short_desc, str) or not short_desc.strip():
                raise ValueError(f"[{ex_id}] Snapshot has missing or empty 'shortDescription'!")
        else:
            short_desc = base.get("shortDescription")
            if not isinstance(short_desc, str) or not short_desc.strip():
                raise ValueError(
                    f"[{ex_id}] Missing shortDescription in both snapshot and existing data! "
                    f"Refusing to invent fake description."
                )

        steps_en = snap_data["steps"] if "steps" in snap_data else base.get("steps")
        steps_vi = snap_data["stepsVi"] if "stepsVi" in snap_data else base.get("stepsVi")

        # Explicit list fallback: do not treat [] as falsy to fall back to base
        primary_muscles = snap_data["primaryMuscles"] if "primaryMuscles" in snap_data else base.get("primaryMuscles", [])
        secondary_muscles = snap_data["secondaryMuscles"] if "secondaryMuscles" in snap_data else base.get("secondaryMuscles", [])
        primary_slugs = snap_data["primarySlugs"] if "primarySlugs" in snap_data else base.get("primarySlugs", [])
        secondary_slugs = snap_data["secondarySlugs"] if "secondarySlugs" in snap_data else base.get("secondarySlugs", [])
        aliases = snap_data["aliases"] if "aliases" in snap_data else base.get("aliases", [])

        merged = {
            "id": ex_id,
            "slug": slug,
            "name": name,
            "nameVi": name_vi,
            "aliases": aliases,
            "category": category,
            "equipment": equipment,
            "videoUrl": video_url,
            "primaryMuscles": primary_muscles,
            "secondaryMuscles": secondary_muscles,
            "primarySlugs": primary_slugs,
            "secondarySlugs": secondary_slugs,
            "shortDescription": short_desc,
            "steps": steps_en,
            "stepsVi": steps_vi,
        }

        # Validate structure before appending
        validate_exercise_structure(merged, location="Snapshot ")
        merged_list.append(merged)

    # Sort deterministically: numeric IDs first (0025-3012), then named IDs alphabetically (drv-*, famous-*, new-*)
    merged_list.sort(key=lambda x: (0, int(x["id"])) if x["id"].isdigit() else (1, x["id"]))

    if check_only:
        # Read-only verification used by `npm test`: never touches exercises.json or the .bak.
        if not os.path.isfile(EXERCISES_PATH):
            print(f"❌ {EXERCISES_PATH} is missing.")
            sys.exit(1)
        with open(EXERCISES_PATH, "r", encoding="utf-8") as f:
            current = json.load(f)
        if current != merged_list:
            current_ids = {row.get("id") for row in current}
            expected_ids = {row["id"] for row in merged_list}
            print(
                "❌ exercises.json differs from what the snapshot would produce "
                f"(only in file: {sorted(current_ids - expected_ids)[:10]}, "
                f"only in snapshot: {sorted(expected_ids - current_ids)[:10]}). "
                "Run `python3 scripts/restore_exercises.py` to regenerate it."
            )
            sys.exit(1)
        print(f"✅ exercises.json matches the snapshot ({len(current)} exercises); nothing written.")
        return

    # Backup existing file to .bak
    if os.path.isfile(EXERCISES_PATH):
        shutil.copyfile(EXERCISES_PATH, BAK_PATH)
        print(f"💾 Backed up existing exercises to {BAK_PATH}")

    os.makedirs(os.path.dirname(EXERCISES_PATH), exist_ok=True)
    # Write to a temp file and rename so an interrupted run cannot truncate exercises.json.
    tmp_path = EXERCISES_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp_path, EXERCISES_PATH)

    # Post-write verification
    with open(EXERCISES_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    if len(verified) != len(merged_list):
        raise ValueError(
            f"Verification failed: row count mismatch after write ({len(verified)} vs {len(merged_list)})!"
        )
    for idx, row in enumerate(verified):
        validate_exercise_structure(row, location="Post-write ")
        expected_row = merged_list[idx]
        if row != expected_row:
            diff_fields = [k for k in EXERCISE_SCHEMA_KEYS if row.get(k) != expected_row.get(k)]
            raise ValueError(
                f"Post-write mismatch at index {idx} (ID: {row.get('id')} vs expected {expected_row.get('id')}): "
                f"mismatched fields {diff_fields}"
            )

    print(f"✅ Successfully restored and verified {len(verified)} exercises in {EXERCISES_PATH}!")


if __name__ == "__main__":
    restore(check_only="--check" in sys.argv)
