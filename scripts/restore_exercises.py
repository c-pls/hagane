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


def derive_safe_slug(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return cleaned or "exercise"


def derive_video_url(ex_id: str, slug: str) -> str:
    if ex_id in FAMOUS_VIDEO_MAP:
        return FAMOUS_VIDEO_MAP[ex_id]
    candidate_named = f"/videos/{slug}-{ex_id}.mp4"
    if os.path.isfile(os.path.join(VIDEOS_DIR, f"{slug}-{ex_id}.mp4")):
        return candidate_named
    # Scan VIDEOS_DIR for any file matching *-[ex_id].mp4 or [ex_id].mp4
    if os.path.isdir(VIDEOS_DIR):
        for fname in os.listdir(VIDEOS_DIR):
            if fname.endswith(f"-{ex_id}.mp4") or fname == f"{ex_id}.mp4":
                return f"/videos/{fname}"
    if os.path.isfile(os.path.join(VIDEOS_DIR, f"{slug}.mp4")):
        return f"/videos/{slug}.mp4"
    return candidate_named


def restore():
    if not os.path.isfile(SNAPSHOT_PATH):
        print(f"❌ Error: Snapshot file not found at {SNAPSHOT_PATH}")
        sys.exit(1)

    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    if not isinstance(snapshot, dict) or len(snapshot) == 0:
        print("❌ Error: Invalid snapshot format (expected non-empty dict).")
        sys.exit(1)

    print(f"📦 Loaded {len(snapshot)} curated exercises from snapshot.")

    existing_exercises = []
    if os.path.isfile(EXERCISES_PATH):
        try:
            with open(EXERCISES_PATH, "r", encoding="utf-8") as f:
                existing_exercises = json.load(f)
        except Exception:
            existing_exercises = []

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
    all_ids = sorted(list(snapshot_ids | existing_ids), key=lambda x: (len(x), x))

    for ex_id in all_ids:
        if ex_id not in snapshot:
            # Preserve non-snapshot existing exercise exactly
            preserved = existing_map[ex_id]
            merged_list.append(preserved)
            continue

        snap_data = snapshot[ex_id]
        base = existing_map.get(ex_id, {})
        name = snap_data.get("name") or base.get("name") or ex_id
        slug = snap_data.get("slug") or base.get("slug") or derive_safe_slug(name)
        video_url = snap_data.get("videoUrl") or base.get("videoUrl") or derive_video_url(ex_id, slug)

        short_desc = snap_data.get("shortDescription") or base.get("shortDescription")
        if not short_desc:
            raise ValueError(
                f"[{ex_id}] Missing shortDescription in both snapshot and existing data! "
                f"Refusing to invent fake description."
            )

        name_vi = snap_data.get("nameVi") or base.get("nameVi")
        if not name_vi:
            raise ValueError(f"[{ex_id}] Missing nameVi in both snapshot and existing data!")

        steps_en = snap_data.get("steps") or base.get("steps")
        if not steps_en or not isinstance(steps_en, dict) or not steps_en.get("prepare"):
            raise ValueError(f"[{ex_id}] Missing or malformed steps (English)!")

        steps_vi = snap_data.get("stepsVi") or base.get("stepsVi")
        if not steps_vi or not isinstance(steps_vi, dict) or not steps_vi.get("prepare"):
            raise ValueError(f"[{ex_id}] Missing or malformed stepsVi (Vietnamese)!")

        primary_muscles = snap_data.get("primaryMuscles") or base.get("primaryMuscles") or []
        primary_slugs = snap_data.get("primarySlugs") or base.get("primarySlugs") or []
        secondary_muscles = snap_data.get("secondaryMuscles") or base.get("secondaryMuscles") or []
        secondary_slugs = snap_data.get("secondarySlugs") or base.get("secondarySlugs") or []

        # Length equality checks
        if len(primary_muscles) != len(primary_slugs):
            raise ValueError(f"[{ex_id}] Primary muscles ({len(primary_muscles)}) and slugs ({len(primary_slugs)}) mismatch!")
        if len(secondary_muscles) != len(secondary_slugs):
            raise ValueError(f"[{ex_id}] Secondary muscles ({len(secondary_muscles)}) and slugs ({len(secondary_slugs)}) mismatch!")

        merged = {
            "id": ex_id,
            "slug": slug,
            "name": name,
            "nameVi": name_vi,
            "aliases": snap_data.get("aliases") or base.get("aliases") or [],
            "category": snap_data.get("category") or base.get("category") or "Other",
            "equipment": snap_data.get("equipment") or base.get("equipment") or "Bodyweight",
            "videoUrl": video_url,
            "primaryMuscles": primary_muscles,
            "secondaryMuscles": secondary_muscles,
            "primarySlugs": primary_slugs,
            "secondarySlugs": secondary_slugs,
            "shortDescription": short_desc,
            "steps": steps_en,
            "stepsVi": steps_vi,
        }
        merged_list.append(merged)

    # Sort deterministically
    merged_list.sort(key=lambda x: (len(x["id"]), x["id"]))

    # Backup existing file
    if os.path.isfile(EXERCISES_PATH):
        shutil.copyfile(EXERCISES_PATH, BAK_PATH)
        print(f"💾 Backed up existing exercises to {BAK_PATH}")

    os.makedirs(os.path.dirname(EXERCISES_PATH), exist_ok=True)
    with open(EXERCISES_PATH, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Post-write verification
    with open(EXERCISES_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    if len(verified) != len(merged_list):
        raise ValueError("Verification failed: row count mismatch after write!")
    for row in verified:
        if len(row["primaryMuscles"]) != len(row["primarySlugs"]):
            raise ValueError(f"Verification failed: {row['id']} primary length mismatch!")
        if len(row["secondaryMuscles"]) != len(row["secondarySlugs"]):
            raise ValueError(f"Verification failed: {row['id']} secondary length mismatch!")
        if os.path.isdir(VIDEOS_DIR):
            v_rel = row["videoUrl"].lstrip("/").replace("videos/", "")
            v_path = os.path.join(VIDEOS_DIR, v_rel)
            if not os.path.isfile(v_path):
                print(f"⚠️ Notice: Video file not found on disk for {row['id']}: {v_path}")

    print(f"✅ Successfully restored and verified {len(verified)} exercises in {EXERCISES_PATH}!")


if __name__ == "__main__":
    restore()
