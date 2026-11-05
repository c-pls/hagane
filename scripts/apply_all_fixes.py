#!/usr/bin/env python3
"""
Applies user requested improvements:
1. Replaces mismatched videos with authentic 1080p MP4 videos:
   - Bulgarian Split Squat (Dumbbell) -> /videos/dumbbell-bulgarian-split-squat.mp4
   - Bulgarian Split Squat (Barbell)  -> /videos/barbell-bulgarian-split-squat.mp4
   - Deadlift - Conventional (Barbell) -> /videos/barbell-conventional-deadlift.mp4
   - Sumo Deadlift (Barbell)          -> /videos/barbell-sumo-deadlift.mp4
   - Hip Thrust (Barbell)             -> /videos/barbell-hip-thrust.mp4
   - Bent-Over Row - Overhand (Barbell) -> /videos/barbell-overhand-bent-over-row.mp4
   - One-Arm Row (Dumbbell)           -> /videos/dumbbell-one-arm-row.mp4
2. Enforces pure Metric units (cm, meters, kg) across instructions & descriptions:
   - "about two feet" -> "about 50–60 cm" (EN) / "khoảng 50–60 cm" (VI)
   - "a few inches"   -> "a few centimeters (5–10 cm)" (EN) / "khoảng 5–10 cm" (VI)
3. Formats all exercise names naturally as `Movement (Equipment)`:
   - e.g. Bulgarian Split Squat (Dumbbell), Back Squat (Barbell), Bench Press (Barbell), etc.
   - Preserves previous names in `aliases` so existing searches and routines remain 100% compatible.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "src" / "data" / "exercises.json"

VIDEO_UPDATES = {
    "famous-db-bulgarian-split-squat": "/videos/dumbbell-bulgarian-split-squat.mp4",
    "famous-bb-bulgarian-split-squat": "/videos/barbell-bulgarian-split-squat.mp4",
    "famous-bb-conventional-deadlift": "/videos/barbell-conventional-deadlift.mp4",
    "famous-bb-sumo-deadlift": "/videos/barbell-sumo-deadlift.mp4",
    "famous-bb-hip-thrust": "/videos/barbell-hip-thrust.mp4",
    "famous-bb-overhand-bent-over-row": "/videos/barbell-overhand-bent-over-row.mp4",
    "famous-db-one-arm-row": "/videos/dumbbell-one-arm-row.mp4",
}

CURATED_NAMES = {
    # Bulgarian split squats
    "famous-db-bulgarian-split-squat": "Bulgarian Split Squat (Dumbbell)",
    "famous-bb-bulgarian-split-squat": "Bulgarian Split Squat (Barbell)",
    
    # Squats & Legs
    "1435": "Back Squat (Barbell)",
    "0042": "Front Squat (Barbell)",
    "1760": "Goblet Squat (Dumbbell)",
    "0413": "Squat (Dumbbell)",
    "new-dumbbell-sumo-squat": "Sumo Squat (Dumbbell)",
    "0743": "Hack Squat (Machine)",
    "0740": "45° Wide Leg Press (Machine)",
    "2611": "Horizontal Leg Press (Machine)",
    "drv-close-feet-leg-press": "Close-Stance Leg Press (Machine)",
    "0750": "Chair Squat (Smith Machine)",
    "0748": "Leg Press (Smith Machine)",
    "famous-weighted-sissy-squat": "Sissy Squat (Bodyweight)",
    "0585": "Leg Extension (Machine)",
    "0586": "Lying Leg Curl (Machine)",
    "0599": "Seated Leg Curl (Machine)",
    "0582": "Kneeling Leg Curl (Machine)",
    "0054": "Lunge (Barbell)",
    "0336": "Lunge (Dumbbell)",
    "0409": "Single-Leg Calf Raise (Dumbbell)",
    "0411": "Single-Leg Squat (Dumbbell)",
    "0417": "Standing Calf Raise (Dumbbell)",
    "1379": "Seated Calf Raise (Dumbbell)",
    "0605": "Standing Calf Raise (Machine)",
    "0594": "Seated Calf Raise (Machine)",
    "0738": "Leg Press Calf Raise (Machine)",
    "1393": "Calf Raise (Smith Machine)",
    "famous-donkey-calf-raise": "Donkey Calf Raise (Bodyweight)",
    "0339": "Lying Leg Curl - Hamstrings (Dumbbell)",
    
    # Deadlifts
    "famous-bb-conventional-deadlift": "Deadlift - Conventional (Barbell)",
    "famous-bb-sumo-deadlift": "Sumo Deadlift (Barbell)",
    "0116": "Romanian Deadlift - RDL (Barbell)",
    "0432": "Romanian Deadlift - RDL (Dumbbell)",
    "1757": "Single-Leg Romanian Deadlift (Dumbbell)",
    "0300": "Deadlift (Dumbbell)",
    "0752": "Deadlift (Smith Machine)",
    "drv-kettlebell-deadlift": "Deadlift (Kettlebell)",
    
    # Hip thrusts & glutes
    "famous-bb-hip-thrust": "Hip Thrust (Barbell)",
    "2286": "Standing Glute Kickback (Machine)",
    "drv-lever-standing-rear-kick": "Standing Rear Kick (Machine)",
    "0597": "Seated Hip Abduction (Machine)",
    "0598": "Seated Hip Adduction (Machine)",
    
    # Bench Press & Chest
    "0025": "Bench Press (Barbell)",
    "0047": "Incline Bench Press (Barbell)",
    "0033": "Decline Bench Press (Barbell)",
    "0030": "Close-Grip Bench Press (Barbell)",
    "famous-db-flat-bench-press": "Flat Bench Press (Dumbbell)",
    "0314": "Incline Bench Press (Dumbbell)",
    "0301": "Decline Bench Press (Dumbbell)",
    "0296": "Close-Grip Press (Dumbbell)",
    "1731": "Hex Press - Crush Press (Dumbbell)",
    "0577": "Chest Press (Machine)",
    "0576": "Seated Chest Press (Machine)",
    "1299": "Incline Chest Press (Machine)",
    "drv-lever-pec-deck-fly": "Pec Deck Fly (Machine)",
    "0308": "Chest Fly (Dumbbell)",
    "0319": "Incline Fly (Dumbbell)",
    "0302": "Decline Fly (Dumbbell)",
    "1277": "Fly on Exercise Ball (Dumbbell)",
    "1278": "Incline Fly on Exercise Ball (Dumbbell)",
    "0148": "Cable Crossover Fly (Cable)",
    "0620": "Flat Bench Fly (Cable)",
    "1269": "Standing Fly (Cable)",
    
    # Rows & Back
    "famous-bb-overhand-bent-over-row": "Bent-Over Row - Overhand (Barbell)",
    "0027": "Bent-Over Row - Yates Underhand (Barbell)",
    "0293": "Bent-Over Row (Dumbbell)",
    "famous-db-one-arm-row": "One-Arm Row (Dumbbell)",
    "0327": "Chest-Supported Row (Dumbbell)",
    "1330": "Chest-Supported Hammer Row (Dumbbell)",
    "drv-lever-t-bar-row": "Chest-Supported T-Bar Row (Machine)",
    "1349": "Reverse T-Bar Row (Machine)",
    "0581": "High Row (Machine)",
    "0208": "Seated Cable Row - V-Grip (Cable)",
    "0218": "Seated Cable Row - Wide Grip (Cable)",
    "0248": "Seal Row - Lying Row (Barbell)",
    "0377": "Rear Delt Row (Dumbbell)",
    "0213": "Seated High Row (Cable)",
    "0861": "One-Arm Twisting Seated Row (Cable)",
    
    # Pull-Ups & Lat Pulldowns
    "0254": "Pull-Up (Bodyweight)",
    "0253": "Chin-Up (Bodyweight)",
    "0652": "Wide-Grip Pull-Up (Bodyweight)",
    "0653": "Close-Grip Pull-Up (Bodyweight)",
    "0651": "Shoulder-Width Pull-Up (Bodyweight)",
    "1429": "Pull-Up - Wide Grip (Bodyweight)",
    "2327": "Reverse Grip Pull-Up (Bodyweight)",
    "drv-chin-ups-pull-ups": "Pull-Up / Chin-Up (Bodyweight)",
    "drv-commando-pull-up": "Commando Pull-Up (Bodyweight)",
    "0570": "Bench Pull-Up (Bodyweight)",
    "2987": "Close-Grip Chin-Up (Bodyweight)",
    "0974": "Lat Pulldown - Close Grip (Cable)",
    "0198": "Lat Pulldown - Wide Grip (Cable)",
    "0207": "Lat Pulldown - Reverse Grip (Cable)",
    "2616": "One-Arm Lateral Pulldown (Cable)",
    "drv-cable-bar-lateral-pulldown-wide-shoulder-grip": "Wide-Grip Lat Pulldown (Cable)",
    "0673": "Lat Pulldown - Reverse Grip (Machine)",
    "0238": "Straight-Arm Pulldown - Lat Prayer (Cable)",
    
    # Shoulders & Delts
    "0553": "Overhead Press - OHP (Barbell)",
    "drv-barbell-seated-behind-head-military-press": "Seated Behind-The-Neck Press (Barbell)",
    "0361": "Alternating Shoulder Press (Dumbbell)",
    "2137": "Arnold Press (Dumbbell)",
    "0289": "Seated Shoulder Press (Dumbbell)",
    "famous-machine-military-press": "Shoulder Press (Machine)",
    "0587": "Shoulder Press - Leverage (Machine)",
    "0765": "Seated Shoulder Press (Smith Machine)",
    "0334": "Lateral Raise (Dumbbell)",
    "0396": "Seated Lateral Raise (Dumbbell)",
    "0326": "Incline Rear Lateral Raise (Dumbbell)",
    "0178": "Lateral Raise (Cable)",
    "0192": "One-Arm Lateral Raise (Cable)",
    "0584": "Lateral Raise (Machine)",
    "famous-db-rear-lateral-raise": "Rear Delt Fly (Dumbbell)",
    "0380": "Rear Delt Fly - Bent-Over (Dumbbell)",
    "0602": "Rear Delt Reverse Fly - Pec Deck (Machine)",
    "0154": "Crossover Reverse Fly (Cable)",
    "0203": "Face Pull (Cable)",
    "famous-cable-front-raise": "Front Raise (Cable)",
    "0162": "One-Arm Front Raise (Cable)",
    "0041": "Front Raise (Barbell)",
    "0310": "Front Raise (Dumbbell)",
    "0392": "Seated Front Raise (Dumbbell)",
    "0075": "Rear Delt Raise (Barbell)",
    "0123": "Wide-Grip Upright Row (Barbell)",
    "0437": "Upright Row (Dumbbell)",
    "0095": "Shrug (Barbell)",
    "0406": "Shrug (Dumbbell)",
    "0329": "Incline Shrug (Dumbbell)",
    "0604": "Trap Shrug (Machine)",
    
    # Arms - Biceps
    "0031": "Bicep Curl (Barbell)",
    "0038": "Drag Curl (Barbell)",
    "0072": "Spider Curl (Barbell)",
    "0294": "Bicep Curl (Dumbbell)",
    "famous-db-standing-alternating-curl": "Alternating Bicep Curl (Dumbbell)",
    "0285": "Seated Alternating Bicep Curl (Dumbbell)",
    "0318": "Incline Bicep Curl (Dumbbell)",
    "0322": "Incline Bicep Curl - Supinated (Dumbbell)",
    "0320": "Incline Hammer Curl (Dumbbell)",
    "0321": "Incline Hammer Press (Dumbbell)",
    "0298": "Cross Body Hammer Curl (Dumbbell)",
    "0297": "Concentration Curl (Dumbbell)",
    "0402": "Preacher Curl (Dumbbell)",
    "0350": "Supine Bicep Curl (Dumbbell)",
    "0592": "Preacher Curl (Machine)",
    "0060": "Preacher Curl (EZ-Bar)",
    "0059": "Bicep Curl (EZ-Bar)",
    "2407": "Biceps Curl (EZ-Bar)",
    "0169": "High Cable Bicep Curl (Cable)",
    "0190": "One-Arm Bicep Curl (Cable)",
    "0229": "Standing Inner Bicep Curl (Cable)",
    
    # Arms - Triceps
    "0061": "Skullcrusher (EZ-Bar)",
    "0186": "Lying Triceps Extension (Cable)",
    "0205": "Triceps Pushdown - V-Bar (Cable)",
    "0241": "Triceps Pushdown - Rope (Cable)",
    "1723": "Triceps Pushdown (Cable)",
    "0194": "Rope Overhead Triceps Extension (Cable)",
    "0231": "Standing One-Arm Triceps Extension (Cable)",
    "0607": "Triceps Extension (Machine)",
    "0330": "Incline Triceps Extension (Dumbbell)",
    "2188": "Seated Triceps Extension (Dumbbell)",
    "1729": "Lying Alternate Extension (Dumbbell)",
    "0333": "Triceps Kickback (Dumbbell)",
    "0394": "Seated Triceps Kickback (Dumbbell)",
    "1451": "Seated Triceps Dip (Machine)",
    "drv-bench-dips": "Bench Dips (Bodyweight)",
    "0250": "Bench Dips (Bodyweight)",
    "drv-chest-dips": "Chest Dips (Bodyweight)",
    "drv-triceps-dips": "Triceps Dips (Bodyweight)",
    
    # Forearms & Wrists
    "0082": "Reverse Wrist Curl (Barbell)",
    "0104": "Standing Back Wrist Curl (Barbell)",
    "0364": "Behind-the-Back Wrist Curl (Dumbbell)",
    "0397": "Seated Neutral Wrist Curl (Dumbbell)",
    
    # Abs, Core & Lower Back
    "famous-hanging-leg-raise": "Hanging Leg Raise (Bodyweight)",
    "0474": "Hanging Straight Leg Raise (Bodyweight)",
    "1764": "Hanging Knee & Hip Raise (Bodyweight)",
    "0826": "Captain's Chair Leg Raise (Bodyweight)",
    "famous-ab-wheel-rollout": "Ab Wheel Rollout (Bodyweight)",
    "1452": "Seated Crunch (Machine)",
    "0156": "Cable Crunch (Cable)",
    "0175": "Kneeling Rope Crunch (Cable)",
    "0226": "Standing Crunch (Cable)",
    "0862": "Woodchopper (Cable)",
    "0407": "Side Bend (Dumbbell)",
    "0705": "Side Plank (Bodyweight)",
    "0777": "Spell Caster (Dumbbell)",
    "0562": "Landmine 180 (Barbell)",
    "0489": "45° Hyperextension (Machine)",
    "0573": "Back Extension (Machine)",
    "0593": "Reverse Hyperextension (Machine)",
    
    # Push-Ups & Bodyweight
    "drv-push-ups": "Push-Up (Bodyweight)",
    "0259": "Close-Grip Push-Up (Bodyweight)",
    "1274": "Deep Push-Up (Bodyweight)",
    "0493": "Incline Push-Up (Bodyweight)",
    "0499": "Inverted Row Between Chairs (Bodyweight)",
    "0498": "Inverted Row With Straps (Bodyweight)",
    "drv-ring-high-row": "Ring High Row (Bodyweight)",
    "3012": "Scapula Dips (Bodyweight)",
    "0672": "Reverse Dip Stretch (Bodyweight)",
    "0028": "Clean and Press (Barbell)",
    "0332": "Iron Cross (Dumbbell)",
    "0128": "Battling Ropes (Ropes)",
    "2612": "Jump Rope (Cardio)",
    "0230": "Standing Lift (Cable)",
}

def clean_auto_name(name: str, eq: str) -> str:
    cleaned = name
    for prefix in ["Barbell ", "Dumbbell ", "Cable ", "Machine ", "EZ-Bar ", "EZ Bar ", "Kettlebell ", "Bodyweight "]:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break
    cleaned = re.sub(r"\b(Barbell|Dumbbell|Cable|Machine|EZ-Bar|Kettlebell)\b", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.replace("( )", "").replace("()", "").strip()
    cleaned = re.sub(rf"\s*\({eq}\)\s*$", "", cleaned).strip()
    return f"{cleaned} ({eq})"

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        exercises = json.load(f)

    print(f"Loaded {len(exercises)} exercises.")

    for ex in exercises:
        eid = ex["id"]
        old_name = ex["name"]
        eq = ex.get("equipment", "Bodyweight")

        # 1. Update video URL if in VIDEO_UPDATES
        if eid in VIDEO_UPDATES:
            ex["videoUrl"] = VIDEO_UPDATES[eid]
            print(f"Updated videoUrl for [{eid}] -> {ex['videoUrl']}")

        # 2. Format name as Movement (Equipment)
        if eid in CURATED_NAMES:
            new_name = CURATED_NAMES[eid]
        else:
            new_name = clean_auto_name(old_name, eq)

        ex["name"] = new_name

        # Ensure old name is preserved in aliases
        aliases = ex.get("aliases", [])
        if old_name not in aliases and old_name != new_name:
            aliases.insert(0, old_name)
        # Also ensure plain movement name without equipment is in aliases
        base_name = re.sub(r"\s*\([^)]*\)", "", new_name).strip()
        if base_name and base_name not in aliases:
            aliases.append(base_name)
        ex["aliases"] = aliases

        # 3. Unit corrections (Feet/Inches -> Metric cm)
        if eid == "famous-db-bulgarian-split-squat":
            ex["nameVi"] = "Bulgarian Split Squat (Tạ đơn)"
            if isinstance(ex.get("steps"), dict):
                prep = ex["steps"].get("prepare", [])
                if prep and "two feet" in prep[0]:
                    prep[0] = prep[0].replace("Stand about two feet in front of a flat bench", "Stand about 50–60 cm in front of a flat bench")
            if isinstance(ex.get("stepsVi"), dict):
                prep_vi = ex["stepsVi"].get("prepare", [])
                if prep_vi:
                    prep_vi[0] = "Đứng cách ghế tập khoảng 50–60 cm, mỗi tay cầm một quả tạ đơn duỗi xuôi bên người, rồi đặt mu bàn chân sau lên mặt đệm ghế phía sau."

        if eid == "famous-bb-bulgarian-split-squat":
            ex["nameVi"] = "Bulgarian Split Squat (Tạ đòn)"

        if eid == "3012":
            if isinstance(ex.get("steps"), list):
                ex["steps"] = [s.replace("a few inches", "a few centimeters (5–10 cm)") for s in ex["steps"]]
            elif isinstance(ex.get("steps"), dict):
                for k, v in ex["steps"].items():
                    if isinstance(v, list):
                        ex["steps"][k] = [s.replace("a few inches", "a few centimeters (5–10 cm)") for s in v]
            if isinstance(ex.get("stepsVi"), list):
                ex["stepsVi"] = [s.replace("vài inch", "khoảng 5–10 cm") for s in ex["stepsVi"]]
            elif isinstance(ex.get("stepsVi"), dict):
                for k, v in ex["stepsVi"].items():
                    if isinstance(v, list):
                        ex["stepsVi"][k] = [s.replace("vài inch", "khoảng 5–10 cm") for s in v]

    # Write back
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)

    print("Successfully updated src/data/exercises.json!")

if __name__ == "__main__":
    main()
