#!/usr/bin/env python3
"""
Polishes all exercise names, aliases, categories, and adds the 4 missing
staple exercises (Dumbbell Lying Leg Curl, Captain's Chair Leg Raise,
Side Plank, Dumbbell Close-Grip Hex Press) with 1080p male videos from R2.
Ensures pure Vietnamese translations with NO English in parentheses.
"""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "src" / "data" / "exercises.json"
VIDEOS_DIR = ROOT / "public" / "videos"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

NEW_EXERCISES_DATA = [
    {
        "id": "0339",
        "slug": "dumbbell-lying-leg-curl",
        "name": "Dumbbell Lying Leg Curl (Hamstring Curl)",
        "nameVi": "Nằm sấp cuốn tạ đơn tập đùi sau",
        "aliases": [
            "dumbbell leg curl",
            "dumbbell lying leg curl",
            "dumbbell hamstring curl",
            "lying femoral curl",
            "leg curl with dumbbell",
            "dumbbell hamstring curl lying"
        ],
        "category": "Hamstrings",
        "equipment": "Dumbbell",
        "videoUrl": "/videos/dumbbell-lying-femoral-0339.mp4",
        "r2_slug": "dumbbell-lying-femoral",
        "primaryMuscles": ["Hamstrings"],
        "secondaryMuscles": ["Glutes", "Calves"],
        "primarySlugs": ["hamstring"],
        "secondarySlugs": ["gluteal", "calves"],
        "shortDescription": "Classic prone dumbbell leg curl targeting the hamstrings.",
        "steps": {
            "prepare": [
                "Lie face down on a flat gym bench with your knees at the edge and a dumbbell standing upright at the foot of the bench.",
                "Secure the handle of the dumbbell between the arches of your feet, keeping your legs fully extended."
            ],
            "execution": [
                "Curl your legs upward by bending at the knees until your lower legs are near vertical.",
                "Squeeze your hamstrings firmly at the top of the movement.",
                "Slowly lower the dumbbell back down under full control until your legs are nearly straight.",
                "Form cue: Keep your hips pressed firmly into the bench",
                "Form cue: Squeeze feet together to secure the dumbbell"
            ],
            "breathing": [
                "Exhale as you curl the dumbbell toward your glutes, and inhale as you lower it back down.",
                "Avoid: Lifting your hips off the bench during the curl",
                "Avoid: Letting the dumbbell drop quickly"
            ]
        },
        "stepsVi": {
            "prepare": [
                "Nằm sấp trên ghế tập phẳng với hai đầu gối ở mép ghế và kẹp tạ đơn thẳng đứng giữa hai lòng bàn chân.",
                "Giữ chặt thân tạ giữa hai bàn chân, hai chân duỗi thẳng về phía sau."
            ],
            "execution": [
                "Gập đầu gối cuốn cẳng chân lên trên cho đến khi cẳng chân vuông góc với đùi.",
                "Gồng siết cơ đùi sau thật chặt ở vị trí cao nhất.",
                "Từ từ hạ tạ xuống có kiểm soát cho đến khi hai chân gần như duỗi thẳng hoàn toàn.",
                "Lưu ý kỹ thuật: Giữ chặt xương chậu áp sát mặt ghế",
                "Lưu ý kỹ thuật: Kẹp chặt hai bàn chân để tạ không bị trượt"
            ],
            "breathing": [
                "Thở ra khi cuốn tạ lên về phía mông, hít vào khi hạ tạ từ từ xuống.",
                "Tránh: Nhấc hông lên khỏi mặt ghế khi cuốn tạ",
                "Tránh: Thả tạ rơi tự do quá nhanh"
            ]
        }
    },
    {
        "id": "0826",
        "slug": "captains-chair-leg-raise",
        "name": "Captain's Chair Leg Raise (Vertical Leg Raise)",
        "nameVi": "Tựa khuỷu tay nâng chân tập cơ bụng dưới",
        "aliases": [
            "captain chair",
            "captains chair leg raise",
            "vertical leg raise",
            "parallel bar leg raise",
            "hanging leg raise alternative",
            "captain's chair",
            "tower leg raise"
        ],
        "category": "Core",
        "equipment": "Bodyweight",
        "videoUrl": "/videos/vertical-leg-raise-on-parallel-bars-0826.mp4",
        "r2_slug": "vertical-leg-raise-on-parallel-bars",
        "primaryMuscles": ["Abs"],
        "secondaryMuscles": ["Hip Flexors", "Obliques"],
        "primarySlugs": ["abs"],
        "secondarySlugs": ["adductors", "obliques"],
        "shortDescription": "Staple lower-abs exercise performed on the captain's chair tower.",
        "steps": {
            "prepare": [
                "Step into the captain's chair tower and rest your forearms on the padded armrests, gripping the handles firmly.",
                "Press your lower back flat against the back pad and let your legs hang straight down."
            ],
            "execution": [
                "Engage your abs and raise your legs or knees up in front of you until your thighs are parallel to the floor or higher.",
                "Curl your pelvis slightly upward at the top to fully contract the lower abdominals.",
                "Slowly lower your legs back to the starting hanging position without swinging.",
                "Form cue: Drive with your abs rather than swinging with hip momentum",
                "Form cue: Keep your shoulders depressed away from your ears"
            ],
            "breathing": [
                "Exhale as you lift your legs upward, and inhale as you lower them back under control.",
                "Avoid: Swinging your torso back and forth to generate momentum",
                "Avoid: Shrugging your shoulders up toward your neck"
            ]
        },
        "stepsVi": {
            "prepare": [
                "Bước vào khung tập nâng bụng chuyên dụng, đặt hai cẳng tay lên đệm lót và nắm chặt tay cầm.",
                "Tựa chắc toàn bộ lưng vào đệm lưng phía sau, để hai chân buông thẳng tự nhiên."
            ],
            "execution": [
                "Gồng chặt cơ bụng và nâng thẳng hai chân hoặc co gối lên phía trước cho đến khi đùi song song với sàn.",
                "Hơi cuộn nhẹ xương chậu lên trên ở điểm cao nhất để tác động tối đa vào nhóm cơ bụng dưới.",
                "Từ từ hạ chân về vị trí ban đầu có kiểm soát mà không để người bị đung đưa.",
                "Lưu ý kỹ thuật: Dùng lực cơ bụng để nâng chân thay vì lấy đà văng người",
                "Lưu ý kỹ thuật: Ghì vai xuống thấp, không rụt cổ vào vai"
            ],
            "breathing": [
                "Thở ra khi nâng hai chân lên cao, hít vào khi từ từ hạ chân xuống.",
                "Tránh: Lấy đà đung đưa người qua lại để nâng chân",
                "Tránh: Rụt vai lên sát tai trong suốt bài tập"
            ]
        }
    },
    {
        "id": "0705",
        "slug": "side-plank",
        "name": "Side Plank (Side Bridge)",
        "nameVi": "Nằm nghiêng chống cùi chỏ giữ thân người",
        "aliases": [
            "side plank",
            "side bridge",
            "oblique plank",
            "side core plank",
            "side bridge hold"
        ],
        "category": "Core",
        "equipment": "Bodyweight",
        "videoUrl": "/videos/side-bridge-side-plank-0705.mp4",
        "r2_slug": "side-bridge-side-plank",
        "primaryMuscles": ["Obliques"],
        "secondaryMuscles": ["Abs", "Glutes"],
        "primarySlugs": ["obliques"],
        "secondarySlugs": ["abs", "gluteal"],
        "shortDescription": "Isometric core exercise targeting the obliques and lateral stabilizers.",
        "steps": {
            "prepare": [
                "Lie on your side on an exercise mat with your legs extended straight and your feet stacked.",
                "Place your lower elbow directly beneath your shoulder with your forearm flat on the ground pointing forward."
            ],
            "execution": [
                "Engage your obliques and lift your hips off the floor until your body forms a straight line from head to ankles.",
                "Hold this rigid straight position for the prescribed duration while keeping your neck neutral.",
                "Slowly lower your hips back to the mat with control before repeating on the opposite side.",
                "Form cue: Keep hips high and do not let them sag toward the floor",
                "Form cue: Keep your chest open and shoulders square"
            ],
            "breathing": [
                "Breathe smoothly and rhythmically throughout the hold without holding your breath.",
                "Avoid: Letting your hips drop toward the floor",
                "Avoid: Rolling your top shoulder forward"
            ]
        },
        "stepsVi": {
            "prepare": [
                "Nằm nghiêng một bên trên thảm tập với hai chân duỗi thẳng và xếp chồng lên nhau.",
                "Đặt cùi chỏ tay dưới ngay dưới khớp vai, cẳng tay áp sát sàn và hướng về phía trước."
            ],
            "execution": [
                "Gồng chặt cơ liên sườn và nâng hông lên khỏi mặt sàn cho đến khi thân người tạo thành một đường thẳng.",
                "Giữ vững tư thế thẳng người này trong khoảng thời gian quy định, giữ cổ thẳng tự nhiên.",
                "Từ từ hạ hông tiếp đất có kiểm soát rồi đổi sang thực hiện cho bên còn lại.",
                "Lưu ý kỹ thuật: Giữ hông luôn được đẩy lên cao, không để võng hông xuống sàn",
                "Lưu ý kỹ thuật: Mở rộng lồng ngực và giữ hai vai thẳng hàng"
            ],
            "breathing": [
                "Duy trì nhịp hít thở đều đặn và sâu trong suốt thời gian giữ tư thế, không nín thở.",
                "Tránh: Để hông bị chùng võng chạm sàn",
                "Tránh: Đổ vai trên về phía trước làm lệch cột sống"
            ]
        }
    },
    {
        "id": "1731",
        "slug": "dumbbell-close-grip-press",
        "name": "Dumbbell Close-Grip Press (Hex Press / Crush Press)",
        "nameVi": "Nằm ghế ép hai tạ đơn đẩy ngực và tay sau",
        "aliases": [
            "hex press",
            "crush press",
            "dumbbell hex press",
            "close grip dumbbell press",
            "squeeze press",
            "dumbbell crush press"
        ],
        "category": "Chest",
        "equipment": "Dumbbell",
        "videoUrl": "/videos/dumbbell-close-grip-press-1731.mp4",
        "r2_slug": "dumbbell-close-grip-press",
        "primaryMuscles": ["Chest", "Triceps"],
        "secondaryMuscles": ["Front Delts"],
        "primarySlugs": ["chest", "triceps"],
        "secondarySlugs": ["deltoids"],
        "shortDescription": "Flat bench close dumbbell press with weights pressed together for inner chest and triceps tension.",
        "steps": {
            "prepare": [
                "Lie flat on a gym bench holding a pair of dumbbells pressed tightly together over your sternum with neutral palms.",
                "Plant your feet firmly on the floor and pull your shoulder blades together into the bench."
            ],
            "execution": [
                "While continuously squeezing the dumbbells together, slowly lower them to touch the middle of your chest.",
                "Pause for a brief second on your chest while maintaining inward squeezing pressure.",
                "Press the dumbbells back up to full arm extension, focusing on inner chest and tricep contraction.",
                "Form cue: Constantly press the dumbbells inward against each other",
                "Form cue: Keep your elbows tucked at roughly 45 degrees"
            ],
            "breathing": [
                "Inhale as you lower the dumbbells to your chest, exhale forcefully as you press them up to lockout.",
                "Avoid: Letting the dumbbells separate during the rep",
                "Avoid: Flaring elbows straight out to the sides"
            ]
        },
        "stepsVi": {
            "prepare": [
                "Nằm ngửa trên ghế tập phẳng, hai tay cầm tạ đơn ép chặt vào nhau ngay phía trên ngực với lòng bàn tay hướng vào nhau.",
                "Đặt hai bàn chân vững chắc trên sàn và ép chặt hai bả vai vào mặt ghế."
            ],
            "execution": [
                "Duy trì lực ép hai quả tạ vào nhau liên tục, từ từ hạ tạ xuống chạm nhẹ vào giữa ngực.",
                "Dừng lại một giây ở vị trí thấp nhất trên ngực trong khi vẫn duy trì áp lực ép chặt tạ.",
                "Đẩy hai quả tạ thẳng lên trên cho đến khi hai tay duỗi thẳng, tập trung siết chặt cơ ngực và tay sau.",
                "Lưu ý kỹ thuật: Luôn ép chặt hai quả tạ vào nhau trong suốt toàn bộ chuyển động",
                "Lưu ý kỹ thuật: Giữ khuỷu tay chếch một góc khoảng 45 độ so với thân người"
            ],
            "breathing": [
                "Hít vào khi từ từ hạ tạ xuống ngực, thở mạnh ra khi đẩy tạ lên vị trí cao nhất.",
                "Tránh: Để hai quả tạ tách rời nhau trong lúc đẩy",
                "Tránh: Mở rộng khuỷu tay sang hai bên quá mức gây áp lực lên vai"
            ]
        }
    }
]

# Rename / Polish map for existing exercises
POLISH_MAP = {
    "0553": {
        "name": "Barbell Overhead Press (OHP / Military Press)",
        "nameVi": "Đẩy tạ đòn qua đầu",
        "category": "Shoulders",
        "equipment": "Barbell",
        "primaryMuscles": ["Delts"],
        "aliases": [
            "overhead press", "OHP", "barbell overhead press", "barbell military press",
            "military press", "strict press", "barbell shoulder press", "standing barbell press", "standing OHP"
        ]
    },
    "0072": {
        "name": "Barbell Spider Curl (Prone Incline Curl)",
        "nameVi": "Nằm sấp ghế dốc cuốn tạ đòn tập tay trước",
        "aliases": [
            "spider curl", "barbell spider curl", "prone incline curl",
            "incline prone barbell curl", "chest supported bicep curl", "barbell prone incline curl"
        ]
    },
    "0374": {
        "name": "Dumbbell Spider Curl (Prone Incline Curl)",
        "nameVi": "Nằm sấp ghế dốc cuốn tạ đơn tập tay trước",
        "aliases": [
            "dumbbell spider curl", "spider curl", "incline prone dumbbell curl",
            "chest supported dumbbell curl", "prone incline curl", "dumbbell prone incline curl"
        ]
    },
    "0027": {
        "name": "Barbell Reverse-Grip Bent-Over Row (Yates Row)",
        "nameVi": "Gập người chèo tạ đòn ngửa tay kiểu Yates",
        "aliases": [
            "yates row", "reverse grip barbell row", "underhand barbell row",
            "dorian yates row", "underhand bent over row", "barbell row", "barbell underhand bent over row"
        ]
    },
    "0351": {
        "name": "Dumbbell Skullcrusher (Lying Triceps Extension)",
        "nameVi": "Nằm ghế duỗi tạ đơn qua đầu tập tay sau",
        "aliases": [
            "dumbbell skullcrusher", "skullcrusher", "DB skull crusher",
            "dumbbell lying triceps extension", "lying dumbbell tricep extension"
        ]
    },
    "0186": {
        "name": "Cable Skullcrusher (Lying Triceps Extension)",
        "nameVi": "Nằm ghế kéo cáp duỗi tay sau",
        "aliases": [
            "cable skullcrusher", "skullcrusher", "cable lying triceps extension",
            "lying cable tricep extension"
        ]
    },
    "0333": {
        "name": "Dumbbell Triceps Kickback",
        "nameVi": "Gập người duỗi tạ đơn ra sau tập tay sau",
        "aliases": [
            "tricep kickback", "triceps kickback", "dumbbell tricep kickback",
            "dumbbell kickback", "DB kickback", "rear triceps kickback"
        ]
    },
    "0394": {
        "name": "Seated Dumbbell Triceps Kickback",
        "nameVi": "Ngồi duỗi tạ đơn ra sau tập tay sau",
        "aliases": [
            "seated tricep kickback", "seated dumbbell triceps kickback",
            "seated kickback", "dumbbell seated kickback"
        ]
    },
    "0738": {
        "name": "Leg Press Calf Raise (45° Sled)",
        "nameVi": "Nhón bắp chân trên máy đạp đùi 45 độ",
        "aliases": [
            "leg press calf raise", "calf press on leg press", "45 degree calf raise",
            "sled calf press", "machine calf raise", "sled 45 degree calf press"
        ]
    },
    "0573": {
        "name": "Machine Back Extension (Hyperextension Machine)",
        "nameVi": "Ngồi gập duỗi lưng trên máy tập",
        "aliases": [
            "machine back extension", "back extension machine", "hyperextension machine",
            "seated back extension machine", "lower back machine", "lever back extension"
        ]
    },
    "0593": {
        "name": "Machine Reverse Hyperextension (Reverse Hyper)",
        "nameVi": "Nằm nâng chân tập lưng dưới trên máy tập",
        "aliases": [
            "reverse hyper", "reverse hyperextension", "reverse hyper machine",
            "machine reverse hyper", "glute hyperextension", "lever reverse hyperextension"
        ]
    },
    "1452": {
        "name": "Machine Seated Crunch (Ab Crunch Machine)",
        "nameVi": "Ngồi gập bụng trên máy tập",
        "aliases": [
            "ab machine", "ab crunch machine", "machine seated crunch",
            "machine ab crunch", "seated crunch machine", "lever seated crunch"
        ]
    },
    "0604": {
        "name": "Machine Trap Shrug (Plate-Loaded)",
        "nameVi": "Nhún cơ cầu vai trên máy tập",
        "aliases": [
            "machine shrug", "plate loaded shrug", "trap shrug machine",
            "shoulder shrug machine", "lever shrug"
        ]
    },
    "2286": {
        "name": "Machine Standing Glute Kickback",
        "nameVi": "Đứng đá chân ra sau tập mông trên máy tập",
        "aliases": [
            "glute kickback machine", "machine standing hip extension",
            "butt blaster machine", "standing glute kickback", "lever standing hip extension"
        ]
    },
    "drv-lever-standing-rear-kick": {
        "name": "Machine Standing Glute Kickback (Rear Kick)",
        "nameVi": "Đứng đạp chân ra sau tập mông trên máy tập",
        "aliases": [
            "machine rear kick", "standing glute kickback machine", "glute kick machine",
            "lever standing rear kick"
        ]
    },
    "0489": {
        "name": "45° Hyperextension (Back Extension)",
        "nameVi": "Gập người duỗi lưng trên ghế dốc 45 độ",
        "aliases": [
            "hyperextension", "back extension", "roman chair", "45 degree hyperextension",
            "back extension bench"
        ]
    },
    "0198": {
        "name": "Cable Lat Pulldown (Wide-Grip)",
        "nameVi": "Ngồi kéo cáp thẳng tay xô rộng",
        "aliases": [
            "lat pulldown", "cable lat pulldown", "wide grip lat pulldown",
            "lat pull down", "cable pulldown"
        ]
    },
    "0238": {
        "name": "Cable Straight-Arm Pulldown (Lat Prayer)",
        "nameVi": "Đứng kéo cáp thẳng tay tập xô",
        "aliases": [
            "lat prayer", "straight arm pulldown", "cable straight arm pulldown",
            "cable pullover", "stiff arm pulldown"
        ]
    },
    "0175": {
        "name": "Cable Kneeling Crunch (Rope Crunch / Cable Abs)",
        "nameVi": "Quỳ kéo cáp gập bụng tập cơ bụng 6 múi",
        "aliases": [
            "cable crunch", "rope crunch", "kneeling cable crunch",
            "cable abs", "kneeling rope crunch", "cable kneeling crunch"
        ]
    },
    "0862": {
        "name": "Cable Woodchopper (Diagonal Twist / Cable Chop)",
        "nameVi": "Kéo cáp chéo người tập cơ bụng liên sườn",
        "aliases": [
            "woodchopper", "cable woodchopper", "cable chop", "cable twist",
            "standing cable rotation", "oblique cable twist", "cable twist up down"
        ]
    },
    "drv-lever-pec-deck-fly": {
        "name": "Machine Pec Deck Fly (Chest Fly Machine)",
        "nameVi": "Ngồi ép ngực trên máy tập",
        "aliases": [
            "pec deck", "chest fly machine", "pec deck fly", "machine chest fly",
            "butterfly machine", "lever pec deck fly"
        ]
    },
    "0602": {
        "name": "Reverse Pec Deck Fly (Machine Rear Delt)",
        "nameVi": "Ngồi ép vai sau trên máy tập",
        "aliases": [
            "reverse pec deck", "rear delt fly machine", "machine rear delt fly",
            "reverse fly machine", "pec deck reverse fly"
        ]
    },
    "0752": {
        "category": "Back",
        "primaryMuscles": ["Hamstrings", "Glutes", "Lower Back"],
        "aliases": [
            "smith machine deadlift", "smith deadlift", "deadlift on smith machine"
        ]
    },
    "0397": {
        "category": "Forearms",
        "primaryMuscles": ["Forearms"],
        "aliases": [
            "wrist curl", "neutral wrist curl", "dumbbell wrist curl", "forearm curl"
        ]
    }
}


def download_file(url: str, dest: Path):
    if dest.exists() and dest.stat().st_size > 10000:
        return
    print(f"Downloading {url} -> {dest.name} ...")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        dest.write_bytes(resp.read())


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        exercises = json.load(f)

    # 1. Download videos for new exercises and add them
    base_r2 = "https://pub-585d42eb1aa64a67aedf483ec328d3fe.r2.dev/exercise-videos/male/"
    existing_ids = {ex["id"] for ex in exercises}

    for item in NEW_EXERCISES_DATA:
        dest_filename = Path(item["videoUrl"]).name
        dest_path = VIDEOS_DIR / dest_filename
        r2_url = f"{base_r2}{item['r2_slug']}.mp4"
        download_file(r2_url, dest_path)

        # Build clean exercise object
        ex_obj = {k: v for k, v in item.items() if k != "r2_slug"}
        if item["id"] in existing_ids:
            exercises = [ex_obj if ex["id"] == item["id"] else ex for ex in exercises]
        else:
            exercises.append(ex_obj)
            existing_ids.add(item["id"])

    # 2. Polish existing exercises
    for ex in exercises:
        eid = ex["id"]
        if eid in POLISH_MAP:
            updates = POLISH_MAP[eid]
            for k, v in updates.items():
                ex[k] = v

    # Write back clean JSON
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)

    print(f"Successfully polished exercises database. Total exercises now: {len(exercises)}")


if __name__ == "__main__":
    main()
