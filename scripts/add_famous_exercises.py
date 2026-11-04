#!/usr/bin/env python3
"""
1. Updates display names & Vietnamese names for existing RDL and Face Pull exercises
   so searching "Romanian Deadlift", "RDL", or "Face Pull" matches immediately in the title.
2. Downloads newly discovered 1080p 30-FPS male MP4 videos from the R2 bucket
   (Dumbbell Flat Bench Press, Machine Military Press, Dumbbell Rear Lateral Raise,
   Cable Front Raise, Standing Alternating Dumbbell Curl, Machine Seated Chest Press,
   Hanging Leg Raises, Ab Wheel Rollout, Weighted Sissy Squat, Donkey Calf Raise).
3. Adds dedicated exercise entries for the most famous gym movements:
   - Dumbbell Bulgarian Split Squat
   - Barbell Bulgarian Split Squat
   - Barbell Conventional Deadlift
   - Barbell Sumo Deadlift
   - Barbell Hip Thrust
   - Dumbbell Hip Thrust
   - Barbell Overhand Bent-Over Row (Pendlay / Standard)
   - One-Arm Dumbbell Row (Bench-Supported)
   plus all newly downloaded R2 video exercises, each with 1-to-1 aligned English (`steps`)
   and pure Vietnamese (`stepsVi`, `nameVi`) coaching instructions.
"""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = ROOT / "public" / "videos"
DATA_PATH = ROOT / "src" / "data" / "exercises.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
R2_BASE = "https://pub-585d42eb1aa64a67aedf483ec328d3fe.r2.dev/exercise-videos/male/"


def download_r2(slug_name: str, dest_filename: str) -> str:
    dest = VIDEOS_DIR / dest_filename
    if not (dest.exists() and dest.stat().st_size > 10000):
        url = f"{R2_BASE}{slug_name}.mp4"
        print(f"Downloading {url} -> {dest_filename} ...")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as resp:
            dest.write_bytes(resp.read())
    return f"/videos/{dest_filename}"


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        exercises = json.load(f)

    # 1. Rename existing RDL, Face Pull, and Split/Single-Leg exercises so their famous names are front and center
    rename_map = {
        "0116": {
            "name": "Barbell Romanian Deadlift (RDL)",
            "nameVi": "Kéo tạ đòn chân thẳng kiểu Rumani",
            "aliases": [
                "romanian deadlift",
                "barbell romanian deadlift",
                "RDL",
                "barbell RDL",
                "stiff leg deadlift",
                "straight leg deadlift",
                "SLDL",
            ],
        },
        "0432": {
            "name": "Dumbbell Romanian Deadlift (RDL)",
            "nameVi": "Kéo tạ đơn chân thẳng kiểu Rumani",
            "aliases": [
                "dumbbell romanian deadlift",
                "DB RDL",
                "romanian deadlift",
                "RDL",
                "dumbbell stiff leg deadlift",
                "SLDL",
            ],
        },
        "1757": {
            "name": "Single-Dumbbell Romanian Deadlift (RDL)",
            "nameVi": "Kéo một tạ đơn chân thẳng kiểu Rumani",
            "aliases": [
                "single leg romanian deadlift",
                "single dumbbell RDL",
                "romanian deadlift",
                "one dumbbell RDL",
            ],
        },
        "0203": {
            "name": "Cable Face Pull (Rope Rear Delt Row)",
            "nameVi": "Kéo cáp dây thừng về phía mặt tập vai sau",
            "aliases": [
                "face pull",
                "cable face pull",
                "rope face pull",
                "rear delt cable row",
            ],
        },
    }

    for ex in exercises:
        if ex["id"] in rename_map:
            upd = rename_map[ex["id"]]
            ex["name"] = upd["name"]
            ex["nameVi"] = upd["nameVi"]
            ex["aliases"] = list(set(ex.get("aliases", []) + upd["aliases"]))

    # 2. Download newly discovered 1080p 30-FPS male videos from R2
    r2_downloads = {
        "db-flat-bench-press": ("dumbbell-bench-press", "dumbbell-bench-press-flat.mp4"),
        "machine-military-press": ("lever-military-press", "lever-military-press-0587.mp4"),
        "db-rear-delt-fly": ("dumbbell-rear-lateral-raise", "dumbbell-rear-lateral-raise-0380.mp4"),
        "cable-front-raise": ("cable-front-raise", "cable-front-raise-0162.mp4"),
        "db-standing-alt-curl": ("dumbbell-alternate-biceps-curl", "dumbbell-alternate-biceps-curl.mp4"),
        "machine-seated-chest-press": ("lever-chest-press", "lever-chest-press-0576.mp4"),
        "0474": ("hanging-straight-leg-raise", "hanging-straight-leg-raise-0474.mp4"),
        "1764": ("hanging-leg-hip-raise", "hanging-leg-hip-raise-1764.mp4"),
        "0325": ("incline-leg-hip-raise", "incline-leg-hip-raise-0325.mp4"),
        "0796": ("stretching-standing-wheel-rollout", "standing-wheel-rollout-0796.mp4"),
        "0851": ("weighted-sissy-squat", "weighted-sissy-squat-0851.mp4"),
        "0284": ("donkey-calf-raise", "donkey-calf-raise-0284.mp4"),
        "0668": ("rear-decline-bridge", "rear-decline-bridge-0668.mp4"),
    }

    video_paths = {}
    for key, (r2_slug, fname) in r2_downloads.items():
        video_paths[key] = download_r2(r2_slug, fname)

    # 3. Famous exercises to add (if not already present)
    new_exercises = [
        {
            "id": "famous-db-bulgarian-split-squat",
            "slug": "dumbbell-bulgarian-split-squat",
            "name": "Dumbbell Bulgarian Split Squat",
            "nameVi": "Gánh tạ đơn một chân kê ghế sau",
            "aliases": [
                "bulgarian split squat",
                "rear foot elevated split squat",
                "RFESS",
                "dumbbell split squat",
                "single leg split squat",
            ],
            "category": "Quads",
            "equipment": "Dumbbell",
            "videoUrl": "/videos/dumbbell-lunge-0336.mp4",
            "primaryMuscles": ["Quads", "Glutes"],
            "secondaryMuscles": ["Hamstrings", "Adductors", "Calves"],
            "primarySlugs": ["quadriceps", "gluteal"],
            "secondarySlugs": ["hamstring", "adductors", "calves"],
            "shortDescription": "Single-leg squat with the rear foot elevated on a bench and dumbbells held at the sides to heavily target the quads and glutes.",
            "steps": {
                "prepare": [
                    "Stand about two feet in front of a flat bench holding a dumbbell in each hand at your sides, and place the top of your rear foot onto the bench behind you.",
                    "Square your hips forward, brace your core, and plant your front foot flat on the floor.",
                ],
                "execution": [
                    "Lower your hips down and slightly back by bending your front knee until your rear knee nearly touches the floor.",
                    "Keep a slight forward torso lean for glute emphasis or an upright torso for quad emphasis, ensuring your front knee tracks over your toes.",
                    "Drive firmly through your entire front foot to return to the top starting position without locking out harshly.",
                    "Form cue: Front foot flat on floor",
                    "Form cue: Knee tracks in line with toes",
                    "Form cue: Drive through the front leg",
                ],
                "breathing": [
                    "Inhale as you lower under control into the split squat, and exhale as you drive back up to the top.",
                    "Avoid: Pushing off excessively with the back foot on the bench",
                    "Avoid: Letting the front knee cave inward at the bottom",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đứng cách ghế phẳng khoảng hai bước bàn chân, hai tay cầm tạ đơn thả dọc hai bên sườn và đặt mu bàn chân sau lên mặt đệm ghế phía sau.",
                    "Giữ khung hông hướng thẳng về phía trước, gồng chặt cơ bụng và đặt bàn chân trước bám phẳng hoàn toàn xuống mặt sàn.",
                ],
                "execution": [
                    "Hạ thấp hông xuống và hơi đẩy nhẹ ra sau bằng cách gập đầu gối chân trước cho đến khi đầu gối chân sau gần chạm sàn.",
                    "Hơi đổ nhẹ thân người về trước để tập trung vào cơ mông hoặc giữ lưng thẳng đứng để tập trung vào cơ đùi trước, đảm bảo đầu gối chân trước mở theo đúng hướng mũi chân.",
                    "Đạp mạnh qua toàn bộ lòng bàn chân trước để đẩy người đứng lên vị trí bắt đầu mà không khóa cứng khớp gối.",
                    "Lưu ý kỹ thuật: Giữ bàn chân trước bám chặt trên sàn",
                    "Lưu ý kỹ thuật: Đầu gối mở theo đúng hướng mũi chân",
                    "Lưu ý kỹ thuật: Phát lực chính từ chân trụ phía trước",
                ],
                "breathing": [
                    "Hít vào khi hạ người xuống có kiểm soát, và thở ra khi đạp chân trước đẩy người đứng lên.",
                    "Tránh: Dùng chân kê trên ghế phía sau để đạp lấy đà quá nhiều",
                    "Tránh: Để đầu gối chân trước bị chụm sụp vào trong ở vị trí thấp nhất",
                ],
            },
        },
        {
            "id": "famous-bb-bulgarian-split-squat",
            "slug": "barbell-bulgarian-split-squat",
            "name": "Barbell Bulgarian Split Squat",
            "nameVi": "Gánh tạ đòn một chân kê ghế sau",
            "aliases": [
                "barbell bulgarian split squat",
                "bulgarian split squat",
                "barbell rear foot elevated split squat",
                "barbell split squat",
            ],
            "category": "Quads",
            "equipment": "Barbell",
            "videoUrl": "/videos/barbell-lunge-0054.mp4",
            "primaryMuscles": ["Quads", "Glutes"],
            "secondaryMuscles": ["Hamstrings", "Adductors", "Lower Back"],
            "primarySlugs": ["quadriceps", "gluteal"],
            "secondarySlugs": ["hamstring", "adductors", "lower-back"],
            "shortDescription": "Rear-foot-elevated split squat performed with a barbell across the upper back for high-load unilateral leg development.",
            "steps": {
                "prepare": [
                    "Unrack the barbell across your upper traps, step forward in front of a bench, and rest the laces of your rear foot on the bench pad.",
                    "Brace your core tightly, keep your chest proud, and balance your weight over your front mid-foot.",
                ],
                "execution": [
                    "Bend your front knee and hip to descend smoothly until your front thigh is parallel to the floor.",
                    "Pause briefly at the bottom while keeping your spine neutral and your front knee aligned with your foot.",
                    "Drive up forcefully through your front heel and mid-foot to return to standing.",
                    "Form cue: Brace torso tightly under the bar",
                    "Form cue: Keep hips squared forward",
                    "Form cue: Control the descent",
                ],
                "breathing": [
                    "Take a deep breath and brace before descending, then exhale as you drive up through the sticking point.",
                    "Avoid: Twisting the hips or leaning sideways",
                    "Avoid: Bouncing off the bottom of the rep",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Nhấc thanh tạ đòn đặt vững trên cơ cầu vai trên, bước ra phía trước ghế tập và đặt mu bàn chân sau lên mặt đệm ghế.",
                    "Gồng chặt cơ bụng, giữ ngực mở cao và dồn trọng tâm cân bằng trên lòng bàn chân trước.",
                ],
                "execution": [
                    "Gập khớp gối và khớp hông chân trước để hạ người xuống mượt mà cho đến khi đùi trước song song với mặt sàn.",
                    "Dừng một nhịp ngắn ở điểm thấp nhất trong khi vẫn giữ cột sống thẳng tự nhiên và đầu gối thẳng hàng với mũi chân.",
                    "Đạp mạnh qua gót chân và giữa bàn chân trước để đẩy người trở lại tư thế đứng thẳng.",
                    "Lưu ý kỹ thuật: Gồng cứng thân người dưới thanh tạ",
                    "Lưu ý kỹ thuật: Giữ hai bên hông cân bằng hướng thẳng về trước",
                    "Lưu ý kỹ thuật: Hạ người xuống có kiểm soát",
                ],
                "breathing": [
                    "Hít sâu và gồng bụng trước khi hạ người xuống, sau đó thở ra khi đạp mạnh vượt qua điểm nặng nhất.",
                    "Tránh: Xoay lệch hông hoặc nghiêng vẹo thân người sang bên",
                    "Tránh: Nhún bật lấy đà ở điểm thấp nhất của động tác",
                ],
            },
        },
        {
            "id": "famous-bb-conventional-deadlift",
            "slug": "barbell-conventional-deadlift",
            "name": "Barbell Deadlift (Conventional)",
            "nameVi": "Kéo tạ đòn từ sàn truyền thống",
            "aliases": [
                "deadlift",
                "barbell deadlift",
                "conventional deadlift",
                "floor deadlift",
            ],
            "category": "Back",
            "equipment": "Barbell",
            "videoUrl": "/videos/barbell-straight-leg-deadlift-0116.mp4",
            "primaryMuscles": ["Hamstrings", "Glutes", "Lower Back"],
            "secondaryMuscles": ["Quads", "Lats", "Traps", "Forearms"],
            "primarySlugs": ["hamstring", "gluteal", "lower-back"],
            "secondarySlugs": ["quadriceps", "upper-back", "trapezius", "forearm"],
            "shortDescription": "Fundamental full-body compound pull lifting a loaded barbell from the floor to a standing lockout.",
            "steps": {
                "prepare": [
                    "Stand with your feet hip-width apart with the barbell positioned directly over your mid-foot (about 2–3 cm from your shins).",
                    "Hinge at the hips and bend your knees until your shins touch the bar, grip the bar just outside your legs, pull your chest up, and flatten your back.",
                ],
                "execution": [
                    "Take the slack out of the bar, engage your lats (imagine squeezing oranges in your armpits), and push the floor away with your legs.",
                    "Keep the barbell dragging close along your shins and thighs as your hips and shoulders rise at the same rate.",
                    "Drive your hips forward to stand tall at lockout with glutes squeezed, then hinge at the hips to lower the bar back to the floor under control.",
                    "Form cue: Keep bar against shins and thighs",
                    "Form cue: Push the floor away with your feet",
                    "Form cue: Lock out with glutes, do not hyperextend lower back",
                ],
                "breathing": [
                    "Take a big 360-degree breath into your belly and brace hard before lifting from the floor; exhale at the top or after resetting on the floor.",
                    "Avoid: Letting the lower back round as the bar leaves the floor",
                    "Avoid: Letting the bar drift forward away from your shins",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đứng hai chân rộng bằng hông với thanh tạ đòn nằm ngay phía trên giữa bàn chân (cách ống quyển khoảng 2–3 cm).",
                    "Gập hông và hạ gối cho đến khi ống quyển chạm nhẹ vào thanh tạ, hai tay nắm tạ ngay sát mép ngoài hai chân, mở ngực cao và giữ lưng phẳng.",
                ],
                "execution": [
                    "Kéo căng nhẹ để khử độ rơ của thanh tạ, khóa chặt cơ xô (tưởng tượng như đang kẹp chặt vật dưới nách), và đạp mạnh hai chân xuống mặt sàn.",
                    "Giữ thanh tạ luôn trượt sát dọc theo ống quyển và đùi trong khi hông và vai nâng lên cùng một tốc độ.",
                    "Đẩy hông về phía trước để đứng thẳng khóa khớp cùng cơ mông siết chặt, sau đó đẩy hông ra sau để hạ tạ có kiểm soát trở lại mặt sàn.",
                    "Lưu ý kỹ thuật: Luôn giữ thanh tạ sát ống quyển và đùi",
                    "Lưu ý kỹ thuật: Dùng lực chân đạp mạnh mặt sàn ra xa",
                    "Lưu ý kỹ thuật: Khóa khớp bằng cơ mông, không ưỡn võng lưng dưới",
                ],
                "breathing": [
                    "Hít một hơi thật sâu vào bụng và gồng cứng toàn bộ cơ trung tâm trước khi nhấc tạ khỏi sàn; thở ra ở đỉnh hoặc sau khi đặt tạ xuống sàn.",
                    "Tránh: Để lưng dưới bị cong gù khi thanh tạ rời khỏi mặt sàn",
                    "Tránh: Để thanh tạ trôi ra xa phía trước ống quyển",
                ],
            },
        },
        {
            "id": "famous-bb-sumo-deadlift",
            "slug": "barbell-sumo-deadlift",
            "name": "Barbell Sumo Deadlift",
            "nameVi": "Kéo tạ đòn từ sàn chân rộng",
            "aliases": [
                "sumo deadlift",
                "barbell sumo deadlift",
                "wide stance deadlift",
            ],
            "category": "Glutes",
            "equipment": "Barbell",
            "videoUrl": "/videos/dumbbell-sumo-squat-new-dumbbell-sumo-squat.mp4",
            "primaryMuscles": ["Glutes", "Adductors", "Hamstrings"],
            "secondaryMuscles": ["Quads", "Lower Back", "Traps", "Forearms"],
            "primarySlugs": ["gluteal", "adductors", "hamstring"],
            "secondarySlugs": ["quadriceps", "lower-back", "trapezius", "forearm"],
            "shortDescription": "Wide-stance barbell deadlift with hands gripping inside the knees to emphasize the glutes, adductors, and quads while reducing lower-back shear.",
            "steps": {
                "prepare": [
                    "Take a wide stance with your toes pointed out at roughly 45 degrees and the barbell directly over your mid-foot.",
                    "Push your knees out in line with your toes, drop your hips, and grip the bar with your arms straight down inside your legs.",
                ],
                "execution": [
                    "Pull your chest tall, wedge your hips close to the bar, and spread the floor apart with your feet to initiate the pull.",
                    "Keep your torso upright and the bar sliding close up your shins and thighs.",
                    "Lock out your hips and knees simultaneously at the top, then control the bar back down to the floor.",
                    "Form cue: Open knees wide in line with toes",
                    "Form cue: Wedge hips in close to the bar",
                    "Form cue: Spread the floor with your feet",
                ],
                "breathing": [
                    "Inhale deeply and brace your core before pulling from the floor, exhaling at lockout.",
                    "Avoid: Letting the knees cave inward off the floor",
                    "Avoid: Shooting the hips up first and turning it into a stiff-leg pull",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đứng chân mở rộng với hai mũi chân xoay ra ngoài góc khoảng 45 độ và thanh tạ đòn nằm ngay phía trên giữa bàn chân.",
                    "Mở rộng hai đầu gối theo đúng hướng mũi chân, hạ hông xuống và nắm thanh tạ với hai tay thả thẳng bên trong hai chân.",
                ],
                "execution": [
                    "Mở cao lồng ngực, ép sát hông vào gần thanh tạ và dùng hai bàn chân đạp tách mặt sàn sang hai bên để bắt đầu kéo tạ.",
                    "Giữ thân người thẳng và kéo thanh tạ trượt sát dọc theo ống quyển và đùi.",
                    "Khóa thẳng khớp hông và khớp gối cùng lúc ở vị trí cao nhất, sau đó hạ thanh tạ có kiểm soát trở lại sàn.",
                    "Lưu ý kỹ thuật: Mở rộng hai gối theo đúng hướng mũi chân",
                    "Lưu ý kỹ thuật: Ép hông vào sát thanh tạ trước khi kéo",
                    "Lưu ý kỹ thuật: Đạp tách mặt sàn sang hai bên bằng hai bàn chân",
                ],
                "breathing": [
                    "Hít sâu và gồng cứng cơ bụng trước khi nhấc tạ khỏi sàn, thở ra khi đã đứng thẳng khóa khớp.",
                    "Tránh: Để hai đầu gối bị chụm vào trong khi tạ rời sàn",
                    "Tránh: Nhổm mông lên quá sớm làm mất thế lưng thẳng",
                ],
            },
        },
        {
            "id": "famous-bb-hip-thrust",
            "slug": "barbell-hip-thrust",
            "name": "Barbell Hip Thrust",
            "nameVi": "Tựa ghế đẩy hông với tạ đòn",
            "aliases": [
                "hip thrust",
                "barbell hip thrust",
                "glute bridge on bench",
                "barbell glute thrust",
            ],
            "category": "Glutes",
            "equipment": "Barbell",
            "videoUrl": video_paths["0668"],
            "primaryMuscles": ["Glutes"],
            "secondaryMuscles": ["Hamstrings", "Adductors", "Core"],
            "primarySlugs": ["gluteal"],
            "secondarySlugs": ["hamstring", "adductors", "abs"],
            "shortDescription": "Premier glute-building exercise performed with upper back braced against a bench and a padded barbell resting across the hips.",
            "steps": {
                "prepare": [
                    "Sit on the floor with your upper back (just below your shoulder blades) resting against the edge of a sturdy bench and roll a padded barbell over your hips.",
                    "Bend your knees and plant your feet flat on the floor hip-width apart so that your shins are vertical at the top of the movement.",
                ],
                "execution": [
                    "Brace your abs, tuck your chin slightly, and drive through your heels to lift your hips until your body forms a flat tabletop from shoulders to knees.",
                    "Squeeze your glutes hard for a 1-second pause at full hip extension while keeping your ribs down.",
                    "Lower your hips back down under control without resting the weight completely between reps.",
                    "Form cue: Vertical shins at the top",
                    "Form cue: Chin tucked and ribs down",
                    "Form cue: Full glute squeeze at lockout",
                ],
                "breathing": [
                    "Inhale as you lower your hips toward the floor, and exhale forcefully as you drive your hips up and squeeze your glutes.",
                    "Avoid: Hyperextending the lower back instead of extending the hips",
                    "Avoid: Placing feet too close or too far away from the bench",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Ngồi trên sàn với phần lưng trên (ngay dưới xương bả vai) tựa vào mép ghế tập chắc chắn và lăn thanh tạ đòn có bọc đệm êm đặt ngang qua hông.",
                    "Co đầu gối và đặt hai bàn chân bám phẳng trên sàn rộng bằng hông sao cho khi đẩy hông lên cao nhất thì hai ống quyển thẳng đứng vuông góc với sàn.",
                ],
                "execution": [
                    "Gồng chặt cơ bụng, hơi thu nhẹ cằm và đạp lực qua hai gót chân để đẩy hông lên cao cho đến khi thân người từ vai đến đầu gối tạo thành một mặt phẳng ngang.",
                    "Siết cứng cơ mông và giữ 1 giây ở đỉnh động tác trong khi vẫn giữ khung sườn khép chặt.",
                    "Từ từ hạ hông xuống có kiểm soát trước khi thực hiện lần lặp tiếp theo.",
                    "Lưu ý kỹ thuật: Cẳng chân vuông góc với mặt sàn ở đỉnh động tác",
                    "Lưu ý kỹ thuật: Thu nhẹ cằm và giữ khung sườn ổn định",
                    "Lưu ý kỹ thuật: Siết chặt tối đa cơ mông ở điểm cao nhất",
                ],
                "breathing": [
                    "Hít vào khi hạ hông xuống gần sàn, và thở ra mạnh khi đẩy hông lên cao siết chặt cơ mông.",
                    "Tránh: Ưỡn võng lưng dưới thay vì đẩy bằng cơ mông",
                    "Tránh: Đặt hai bàn chân quá gần hoặc quá xa ghế tựa",
                ],
            },
        },
        {
            "id": "famous-db-flat-bench-press",
            "slug": "dumbbell-bench-press",
            "name": "Dumbbell Bench Press (Flat)",
            "nameVi": "Nằm ghế phẳng đẩy ngực với tạ đơn",
            "aliases": [
                "dumbbell bench press",
                "flat dumbbell press",
                "DB bench press",
                "dumbbell chest press",
            ],
            "category": "Chest",
            "equipment": "Dumbbell",
            "videoUrl": video_paths["db-flat-bench-press"],
            "primaryMuscles": ["Chest"],
            "secondaryMuscles": ["Front Delts", "Triceps"],
            "primarySlugs": ["chest"],
            "secondarySlugs": ["deltoids", "triceps"],
            "shortDescription": "Classic flat-bench pressing exercise using dumbbells for a deep pectoral stretch and natural shoulder path.",
            "steps": {
                "prepare": [
                    "Sit on a flat bench with a dumbbell resting on each thigh, then lie back while kicking the weights up to chest level.",
                    "Plant your feet firmly on the floor, retract your shoulder blades into the bench, and hold the dumbbells with palms facing forward.",
                ],
                "execution": [
                    "Lower the dumbbells slowly to the sides of your mid-chest with your elbows tucked at roughly a 45-degree angle.",
                    "Feel a controlled stretch across your chest at the bottom with your forearms vertical.",
                    "Press the dumbbells up in a slight arc over your chest until your arms are extended.",
                    "Form cue: Retract shoulder blades into bench",
                    "Form cue: Keep elbows at 45-degree angle",
                    "Form cue: Full stretch at chest level",
                ],
                "breathing": [
                    "Inhale as you lower the dumbbells toward your chest, and exhale as you press them back up.",
                    "Avoid: Flaring elbows straight out to 90 degrees",
                    "Avoid: Clanging the dumbbells together hard at the top",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Ngồi trên ghế phẳng với mỗi bên đùi đặt một quả tạ đơn, sau đó ngả lưng nằm xuống đồng thời hất nhẹ đùi đưa tạ lên ngang ngực.",
                    "Đặt hai bàn chân bám chặt xuống mặt sàn, ép chặt hai xương bả vai xuống mặt ghế và cầm tạ đơn với lòng bàn tay hướng về phía trước.",
                ],
                "execution": [
                    "Hạ chậm hai quả tạ đơn xuống hai bên cạnh ngực giữa với khuỷu tay khép góc khoảng 45 độ so với thân người.",
                    "Cảm nhận độ căng mở của cơ ngực ở điểm thấp nhất trong khi cẳng tay giữ thẳng đứng.",
                    "Đẩy mạnh hai quả tạ lên theo đường vòng cung nhẹ về phía trên ngực cho đến khi hai tay duỗi thẳng.",
                    "Lưu ý kỹ thuật: Ép chặt hai bả vai xuống mặt ghế",
                    "Lưu ý kỹ thuật: Giữ khuỷu tay mở góc 45 độ an toàn cho khớp vai",
                    "Lưu ý kỹ thuật: Hạ tạ đủ sâu ngang tầm ngực",
                ],
                "breathing": [
                    "Hít vào khi hạ tạ đơn xuống hai bên ngực, và thở ra khi đẩy tạ lên cao.",
                    "Tránh: Xòe ngang hai khuỷu tay vuông góc 90 độ gây áp lực lên khớp vai",
                    "Tránh: Đập mạnh hai quả tạ vào nhau ở điểm cao nhất",
                ],
            },
        },
        {
            "id": "famous-bb-overhand-bent-over-row",
            "slug": "barbell-bent-over-row-overhand",
            "name": "Barbell Bent-Over Row (Overhand / Pendlay)",
            "nameVi": "Gập người chèo tạ đòn úp tay",
            "aliases": [
                "barbell row",
                "bent over row",
                "overhand barbell row",
                "pendlay row",
                "BB row",
            ],
            "category": "Back",
            "equipment": "Barbell",
            "videoUrl": "/videos/barbell-underhand-bent-over-row-0027.mp4",
            "primaryMuscles": ["Upper Back", "Lats"],
            "secondaryMuscles": ["Rear Delts", "Biceps", "Lower Back"],
            "primarySlugs": ["upper-back"],
            "secondarySlugs": ["deltoids", "biceps", "lower-back"],
            "shortDescription": "Staple compound back builder rowing a barbell with an overhand grip into the lower chest or upper abdomen.",
            "steps": {
                "prepare": [
                    "Stand with feet hip-width apart and grip the barbell slightly wider than shoulder width with an overhand (pronated) grip.",
                    "Hinge forward at the hips until your torso is between 45 degrees and parallel to the floor, keeping your spine flat and knees slightly bent.",
                ],
                "execution": [
                    "Brace your core and drive your elbows back to row the barbell into your upper abdomen or lower sternum.",
                    "Squeeze your shoulder blades firmly together at the top of the rep.",
                    "Lower the barbell under control until your arms are fully extended while maintaining your hip hinge angle.",
                    "Form cue: Keep back flat and torso angle fixed",
                    "Form cue: Drive with the elbows, not the wrists",
                    "Form cue: Squeeze shoulder blades at the top",
                ],
                "breathing": [
                    "Exhale as you row the barbell toward your torso, and inhale as you lower it under control.",
                    "Avoid: Standing upright and jerking the weight with momentum",
                    "Avoid: Rounding the lower back during the set",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đứng hai chân rộng bằng hông và nắm thanh tạ đòn rộng hơn vai một chút bằng tay cầm úp (lòng bàn tay hướng về phía người).",
                    "Gập người về trước từ khớp hông cho đến khi thân người nghiêng khoảng 45 độ hoặc gần song song với sàn, giữ cột sống thẳng và đầu gối hơi chùng nhẹ.",
                ],
                "execution": [
                    "Gồng chặt cơ bụng và kéo mạnh hai khuỷu tay ra sau để đưa thanh tạ đòn chạm vào phần bụng trên hoặc chấn thủy.",
                    "Siết chặt hai xương bả vai lại với nhau ở điểm cao nhất của động tác.",
                    "Từ từ hạ thanh tạ xuống có kiểm soát cho đến khi hai tay duỗi thẳng hoàn toàn mà vẫn giữ nguyên góc gập thân người.",
                    "Lưu ý kỹ thuật: Giữ lưng phẳng và cố định góc gập người",
                    "Lưu ý kỹ thuật: Phát lực kéo từ khuỷu tay chứ không gập cổ tay",
                    "Lưu ý kỹ thuật: Khép chặt hai bả vai ở đỉnh động tác",
                ],
                "breathing": [
                    "Thở ra khi kéo thanh tạ đòn về sát thân người, và hít vào khi hạ tạ xuống có kiểm soát.",
                    "Tránh: Nhổm đứng dậy giật tạ bằng quán tính",
                    "Tránh: Để lưng dưới bị cong gù trong suốt hiệp tập",
                ],
            },
        },
        {
            "id": "famous-db-one-arm-row",
            "slug": "one-arm-dumbbell-row",
            "name": "One-Arm Dumbbell Row (Single-Arm Row)",
            "nameVi": "Chèo tạ đơn một tay tựa ghế tập xô",
            "aliases": [
                "one arm dumbbell row",
                "single arm dumbbell row",
                "dumbbell row",
                "kroc row",
                "bench supported one arm row",
            ],
            "category": "Back",
            "equipment": "Dumbbell",
            "videoUrl": "/videos/dumbbell-bent-over-row-0293.mp4",
            "primaryMuscles": ["Lats", "Upper Back"],
            "secondaryMuscles": ["Rear Delts", "Biceps", "Forearms"],
            "primarySlugs": ["upper-back"],
            "secondarySlugs": ["deltoids", "biceps", "forearm"],
            "shortDescription": "Unilateral back exercise bracing one hand on a bench while rowing a dumbbell in an arc toward the hip.",
            "steps": {
                "prepare": [
                    "Place your non-working hand and knee (or plant both feet in a staggered stance with one hand braced) on a flat bench.",
                    "Flatten your back parallel to the floor and hold a dumbbell in your working hand with your arm fully extended.",
                ],
                "execution": [
                    "Pull the dumbbell back in a smooth arc toward your hip pocket by driving your elbow past your torso.",
                    "Pause briefly at the top and squeeze your lat without twisting your spine.",
                    "Lower the dumbbell slowly back down into a full lat stretch at the bottom.",
                    "Form cue: Row toward the hip pocket in an arc",
                    "Form cue: Keep shoulders squared to the floor",
                    "Form cue: Full stretch at the bottom",
                ],
                "breathing": [
                    "Exhale as you drive your elbow back to row the dumbbell up, and inhale as you lower it down.",
                    "Avoid: Shrugging the shoulder up toward your ear",
                    "Avoid: Jerking and rotating the torso excessively to heave the weight",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đặt tay và đầu gối bên không tập lên mặt ghế phẳng (hoặc đứng chân trước chân sau và chống một tay vững chắc lên ghế).",
                    "Giữ lưng phẳng gần như song song với mặt sàn và cầm tạ đơn ở tay tập với cánh tay duỗi thẳng tự nhiên.",
                ],
                "execution": [
                    "Kéo quả tạ đơn về phía sau theo đường vòng cung hướng về phía hông bằng cách đưa khuỷu tay vượt qua thân người.",
                    "Dừng một nhịp ngắn ở điểm cao nhất và siết chặt cơ xô mà không vặn xoắn cột sống.",
                    "Hạ quả tạ đơn chậm rãi xuống vị trí bắt đầu để kéo giãn tối đa cơ xô ở điểm dưới cùng.",
                    "Lưu ý kỹ thuật: Kéo tạ theo đường vòng cung về phía túi quần (hông)",
                    "Lưu ý kỹ thuật: Giữ hai vai cân bằng song song với mặt sàn",
                    "Lưu ý kỹ thuật: Thả giãn hết biên độ cơ xô ở điểm thấp nhất",
                ],
                "breathing": [
                    "Thở ra khi kéo khuỷu tay ra sau đưa tạ lên, và hít vào khi hạ tạ xuống có kiểm soát.",
                    "Tránh: Nhún rụt vai lên sát tai khi kéo",
                    "Tránh: Vặn xoắn thân người quá mức để giật tạ",
                ],
            },
        },
        {
            "id": "0587",
            "slug": "machine-shoulder-press",
            "name": "Machine Shoulder Press (Leverage Military Press)",
            "nameVi": "Ngồi đẩy vai trên máy tập",
            "aliases": [
                "machine shoulder press",
                "lever military press",
                "seated machine overhead press",
                "shoulder press machine",
            ],
            "category": "Shoulders",
            "equipment": "Machine",
            "videoUrl": video_paths["machine-military-press"],
            "primaryMuscles": ["Delts", "Front Delts"],
            "secondaryMuscles": ["Triceps", "Upper Chest"],
            "primarySlugs": ["deltoids"],
            "secondarySlugs": ["triceps", "chest"],
            "shortDescription": "Seated overhead shoulder press on a leverage or selectorized machine for stable deltoid hypertrophy.",
            "steps": {
                "prepare": [
                    "Adjust the seat height so the machine handles start at roughly shoulder or ear level.",
                    "Sit tall with your back pressed firmly against the pad, plant your feet flat, and grip the handles.",
                ],
                "execution": [
                    "Press the handles smoothly overhead until your arms are extended without locking your elbows harshly.",
                    "Pause briefly at the top while keeping your shoulders down away from your ears.",
                    "Lower the handles slowly back to shoulder height under full control.",
                    "Form cue: Keep back glued to the backrest",
                    "Form cue: Wrists stacked under handles",
                    "Form cue: Controlled negative to ear level",
                ],
                "breathing": [
                    "Exhale as you press the handles overhead, and inhale as you lower them back to shoulder level.",
                    "Avoid: Arching the lower back off the pad",
                    "Avoid: Letting the weight stack slam between reps",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Điều chỉnh độ cao yên ghế sao cho tay cầm của máy ở ngang tầm vai hoặc ngang tai khi bắt đầu.",
                    "Ngồi thẳng lưng áp sát vào đệm tựa, đặt hai bàn chân vững chắc trên sàn và nắm chặt hai tay cầm.",
                ],
                "execution": [
                    "Đẩy mượt mà hai tay cầm thẳng lên qua đầu cho đến khi hai cánh tay duỗi thẳng tự nhiên mà không khóa cứng khớp khuỷu tay.",
                    "Dừng một nhịp ngắn ở điểm cao nhất trong khi vẫn giữ cầu vai hạ thấp cách xa tai.",
                    "Từ từ hạ tay cầm trở lại ngang tầm vai với sự kiểm soát hoàn toàn.",
                    "Lưu ý kỹ thuật: Luôn giữ lưng áp sát đệm tựa ghế",
                    "Lưu ý kỹ thuật: Giữ cổ tay thẳng ngay dưới tay cầm",
                    "Lưu ý kỹ thuật: Hạ tạ chậm có kiểm soát về ngang tai",
                ],
                "breathing": [
                    "Thở ra khi đẩy tay cầm lên qua đầu, và hít vào khi hạ tay cầm trở lại ngang tầm vai.",
                    "Tránh: Ưỡn võng lưng dưới tách rời khỏi đệm tựa",
                    "Tránh: Thả rơi tạ làm va đập các bánh tạ giữa các lần lặp",
                ],
            },
        },
        {
            "id": "0380",
            "slug": "dumbbell-rear-delt-fly",
            "name": "Dumbbell Rear Delt Fly (Bent-Over Reverse Fly)",
            "nameVi": "Gập người dang tạ đơn tập vai sau",
            "aliases": [
                "rear delt fly",
                "dumbbell rear lateral raise",
                "bent over lateral raise",
                "reverse dumbbell fly",
            ],
            "category": "Shoulders",
            "equipment": "Dumbbell",
            "videoUrl": video_paths["db-rear-delt-fly"],
            "primaryMuscles": ["Rear Delts"],
            "secondaryMuscles": ["Upper Back", "Traps"],
            "primarySlugs": ["deltoids"],
            "secondarySlugs": ["upper-back", "trapezius"],
            "shortDescription": "Bent-over dumbbell reverse fly isolating the posterior deltoids and upper back.",
            "steps": {
                "prepare": [
                    "Stand with feet hip-width apart holding a dumbbell in each hand, and hinge forward at the hips until your torso is nearly parallel to the floor.",
                    "Let the dumbbells hang beneath your chest with palms facing each other and a slight bend in your elbows.",
                ],
                "execution": [
                    "Sweep the dumbbells out and up in a wide arc until your upper arms are in line with your back.",
                    "Pause briefly at the top to feel the contraction in the back of your shoulders.",
                    "Lower the dumbbells slowly along the same arc back to the starting position.",
                    "Form cue: Lead with the backs of your wrists and elbows",
                    "Form cue: Keep torso angle stationary",
                    "Form cue: Avoid pinching traps excessively",
                ],
                "breathing": [
                    "Exhale as you raise the dumbbells out to the sides, and inhale as you lower them under control.",
                    "Avoid: Swinging the torso upright to throw the weights up",
                    "Avoid: Bending the elbows and turning the movement into a row",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đứng hai chân rộng bằng hông, mỗi tay cầm một quả tạ đơn và gập người về trước từ khớp hông cho đến khi thân người gần song song với mặt sàn.",
                    "Để hai quả tạ thả dọc dưới ngực với hai lòng bàn tay hướng vào nhau và khuỷu tay hơi cong nhẹ cố định.",
                ],
                "execution": [
                    "Dang rộng hai quả tạ đơn sang hai bên và nâng lên theo đường vòng cung cho đến khi bắp tay ngang với mặt phẳng lưng.",
                    "Dừng một nhịp ngắn ở điểm cao nhất để cảm nhận cơ vai sau co thắt.",
                    "Chậm rãi hạ hai quả tạ theo đúng quỹ đạo cũ trở về vị trí bắt đầu.",
                    "Lưu ý kỹ thuật: Dẫn hướng chuyển động bằng mu cổ tay và khuỷu tay",
                    "Lưu ý kỹ thuật: Giữ nguyên góc gập thân người cố định",
                    "Lưu ý kỹ thuật: Tránh nhún co cơ cầu vai quá nhiều",
                ],
                "breathing": [
                    "Thở ra khi dang tạ đơn sang hai bên, và hít vào khi hạ tạ xuống có kiểm soát.",
                    "Tránh: Đung đưa nhổm thân người lên để vung tạ",
                    "Tránh: Gập khuỷu tay quá nhiều biến động tác thành bài chèo tạ",
                ],
            },
        },
        {
            "id": "0576",
            "slug": "machine-seated-chest-press",
            "name": "Machine Seated Chest Press",
            "nameVi": "Ngồi đẩy ngực trên máy tập",
            "aliases": [
                "seated chest press machine",
                "lever chest press",
                "machine bench press",
            ],
            "category": "Chest",
            "equipment": "Machine",
            "videoUrl": video_paths["machine-seated-chest-press"],
            "primaryMuscles": ["Chest"],
            "secondaryMuscles": ["Front Delts", "Triceps"],
            "primarySlugs": ["chest"],
            "secondarySlugs": ["deltoids", "triceps"],
            "shortDescription": "Seated horizontal chest press machine providing stable, guided resistance for the pectorals.",
            "steps": {
                "prepare": [
                    "Adjust the seat height so the handles align with your mid-to-lower chest.",
                    "Sit back with your shoulder blades retracted against the pad and grip the handles firmly.",
                ],
                "execution": [
                    "Press the handles forward until your arms are extended in front of your chest.",
                    "Squeeze your chest briefly at full extension while keeping your shoulders pinned back.",
                    "Return the handles slowly until you feel a comfortable stretch across your chest.",
                    "Form cue: Keep shoulder blades pinned to pad",
                    "Form cue: Elbows slightly below shoulder height",
                    "Form cue: Smooth controlled eccentric",
                ],
                "breathing": [
                    "Exhale as you press the handles forward, and inhale as you return them toward your chest.",
                    "Avoid: Letting your shoulders roll forward at the end of the press",
                    "Avoid: Bouncing the weight stack at the bottom",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Điều chỉnh độ cao yên ghế sao cho hai tay cầm nằm ngang tầm ngực giữa hoặc ngực dưới.",
                    "Ngồi tựa lưng với hai xương bả vai ép chặt vào đệm ghế và nắm chắc tay cầm.",
                ],
                "execution": [
                    "Đẩy hai tay cầm về phía trước cho đến khi hai cánh tay duỗi thẳng trước ngực.",
                    "Siết chặt cơ ngực một nhịp ở điểm duỗi tay trong khi vẫn giữ hai vai ghìm sát đệm lưng.",
                    "Từ từ thu tay cầm trở lại cho đến khi cảm nhận cơ ngực được kéo giãn thoải mái.",
                    "Lưu ý kỹ thuật: Luôn ghìm chặt hai bả vai vào đệm tựa",
                    "Lưu ý kỹ thuật: Giữ khuỷu tay thấp hơn vai một chút",
                    "Lưu ý kỹ thuật: Kiểm soát nhịp trả tạ chậm rãi",
                ],
                "breathing": [
                    "Thở ra khi đẩy tay cầm về phía trước, và hít vào khi thu tay cầm về gần ngực.",
                    "Tránh: Để hai vai bị nhô cuộn về phía trước khi duỗi tay",
                    "Tránh: Thả tạ rơi tự do làm nảy các bánh tạ",
                ],
            },
        },
        {
            "id": "0474",
            "slug": "hanging-straight-leg-raise",
            "name": "Hanging Straight Leg Raise",
            "nameVi": "Treo người trên xà nâng thẳng hai chân tập bụng",
            "aliases": [
                "hanging leg raise",
                "toes to bar",
                "hanging abs raise",
            ],
            "category": "Core",
            "equipment": "Bodyweight",
            "videoUrl": video_paths["0474"],
            "primaryMuscles": ["Abs", "Hip Flexors"],
            "secondaryMuscles": ["Obliques", "Forearms"],
            "primarySlugs": ["abs", "adductors"],
            "secondarySlugs": ["obliques", "forearm"],
            "shortDescription": "Advanced hanging core exercise lifting straight legs while curling the pelvis upward.",
            "steps": {
                "prepare": [
                    "Hang from an overhead pull-up bar with a shoulder-width overhand grip and engage your shoulders lightly.",
                    "Keep your legs straight and together with your pelvis slightly tucked.",
                ],
                "execution": [
                    "Curl your pelvis upward and raise your straight legs in front of you until they are at least parallel to the floor.",
                    "Pause briefly at the top while contracting your lower abs.",
                    "Lower your legs slowly under control without swinging your body.",
                    "Form cue: Curl the pelvis up, don't just lift from the hips",
                    "Form cue: Control the descent to prevent swinging",
                    "Form cue: Keep shoulders active on the bar",
                ],
                "breathing": [
                    "Exhale as you raise your legs up, and inhale as you lower them back to a dead hang.",
                    "Avoid: Using momentum and swinging back and forth",
                    "Avoid: Bending the knees excessively unless performing knee raises",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Treo người trên thanh xà đơn với hai tay nắm rộng bằng vai và kích hoạt nhẹ cơ vai để giữ ổn định.",
                    "Duỗi thẳng hai chân khép sát cạnh nhau và hơi cuộn nhẹ khung chậu.",
                ],
                "execution": [
                    "Cuộn khung chậu hướng lên và nâng hai chân thẳng ra phía trước cho đến khi ít nhất song song với mặt sàn.",
                    "Dừng một nhịp ngắn ở điểm cao nhất đồng thời siết chặt cơ bụng dưới.",
                    "Từ từ hạ hai chân xuống có kiểm soát mà không để cơ thể đung đưa.",
                    "Lưu ý kỹ thuật: Cuộn khung chậu lên để vào cơ bụng thay vì chỉ gập hông",
                    "Lưu ý kỹ thuật: Hạ chân chậm để chống đung đưa người",
                    "Lưu ý kỹ thuật: Giữ vai chắc chắn khi treo trên xà",
                ],
                "breathing": [
                    "Thở ra khi nâng hai chân lên cao, và hít vào khi hạ chân trở lại vị trí treo thẳng.",
                    "Tránh: Đung đưa lấy đà qua lại khi thực hiện động tác",
                    "Tránh: Co gập đầu gối quá nhiều khi đang tập biến thể thẳng chân",
                ],
            },
        },
        {
            "id": "1764",
            "slug": "hanging-knee-hip-raise",
            "name": "Hanging Knee & Hip Raise",
            "nameVi": "Treo người trên xà co gối nâng hông tập bụng",
            "aliases": [
                "hanging knee raise",
                "captain's chair knee raise",
                "hanging leg hip raise",
            ],
            "category": "Core",
            "equipment": "Bodyweight",
            "videoUrl": video_paths["1764"],
            "primaryMuscles": ["Abs"],
            "secondaryMuscles": ["Hip Flexors", "Obliques", "Forearms"],
            "primarySlugs": ["abs"],
            "secondarySlugs": ["adductors", "obliques", "forearm"],
            "shortDescription": "Hanging abdominal raise tucking the knees toward the chest with a posterior pelvic tilt.",
            "steps": {
                "prepare": [
                    "Grip a pull-up bar with a firm overhand grip and hang with your body steady.",
                    "Brace your core and slightly bend your knees.",
                ],
                "execution": [
                    "Draw your knees up toward your chest while curling your tailbone forward and up.",
                    "Squeeze your abs hard at the top of the movement for a brief pause.",
                    "Lower your legs slowly back to the starting hang position without swinging.",
                    "Form cue: Tuck tailbone up at the top",
                    "Form cue: Keep torso still",
                    "Form cue: Slow controlled lowering phase",
                ],
                "breathing": [
                    "Exhale forcefully as you curl your knees up toward your chest, and inhale on the way down.",
                    "Avoid: Swinging the torso to generate momentum",
                    "Avoid: Stopping at 90 degrees without curling the pelvis",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Nắm chắc thanh xà đơn bằng tay cầm úp và treo thẳng cơ thể ở trạng thái ổn định.",
                    "Gồng cơ bụng và hơi co nhẹ hai đầu gối.",
                ],
                "execution": [
                    "Kéo hai đầu gối lên cao về phía ngực đồng thời cuộn xương cụt hướng lên trên.",
                    "Siết chặt cơ bụng và giữ một nhịp ngắn ở đỉnh động tác.",
                    "Từ từ hạ hai chân trở lại tư thế treo ban đầu mà không đung đưa người.",
                    "Lưu ý kỹ thuật: Cuộn xương cụt lên ở đỉnh động tác để ăn vào cơ bụng",
                    "Lưu ý kỹ thuật: Giữ thân người ổn định không lắc lư",
                    "Lưu ý kỹ thuật: Hạ chân xuống chậm rãi có kiểm soát",
                ],
                "breathing": [
                    "Thở ra mạnh khi cuộn đầu gối lên sát ngực, và hít vào khi hạ chân xuống.",
                    "Tránh: Đung đưa thân người để lấy đà",
                    "Tránh: Chỉ nâng đùi đến 90 độ mà không cuộn khung chậu",
                ],
            },
        },
        {
            "id": "0796",
            "slug": "ab-wheel-rollout",
            "name": "Ab Wheel Rollout",
            "nameVi": "Quỳ lăn bánh xe tập cơ bụng",
            "aliases": [
                "ab rollout",
                "ab wheel",
                "standing wheel rollout",
                "kneeling ab wheel rollout",
            ],
            "category": "Core",
            "equipment": "Bodyweight",
            "videoUrl": video_paths["0796"],
            "primaryMuscles": ["Abs", "Core"],
            "secondaryMuscles": ["Lats", "Shoulders", "Obliques"],
            "primarySlugs": ["abs"],
            "secondarySlugs": ["upper-back", "deltoids", "obliques"],
            "shortDescription": "High-tension anti-extension core exercise rolling an ab wheel forward while maintaining a braced spine.",
            "steps": {
                "prepare": [
                    "Kneel (or stand) on the floor holding the ab wheel handles directly beneath your shoulders with arms straight.",
                    "Tuck your pelvis slightly (posterior pelvic tilt) and brace your abs and glutes tightly.",
                ],
                "execution": [
                    "Roll the wheel forward slowly while keeping your core locked and preventing your lower back from sagging.",
                    "Extend as far forward as you can maintain a flat or slightly rounded lower back.",
                    "Pull through your abs and lats to roll the wheel back under your shoulders.",
                    "Form cue: Keep ribs down and pelvis tucked",
                    "Form cue: Brace glutes and abs together",
                    "Form cue: Only roll as far as your lower back stays supported",
                ],
                "breathing": [
                    "Inhale and brace as you roll forward, and exhale as you pull the wheel back to the start.",
                    "Avoid: Letting the lower back arch or sag toward the floor",
                    "Avoid: Sitting your hips backward toward your heels before pulling with your abs",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Quỳ gối (hoặc đứng) trên sàn, hai tay nắm tay cầm bánh xe tập bụng đặt ngay dưới vai với hai cánh tay duỗi thẳng.",
                    "Hơi cuộn nhẹ khung chậu vào trong và gồng cứng cả cơ bụng lẫn cơ mông.",
                ],
                "execution": [
                    "Từ từ đẩy bánh xe lăn về phía trước trong khi vẫn khóa chặt cơ bụng và giữ cho lưng dưới không bị võng xuống.",
                    "Vươn người ra xa nhất trong khả năng vẫn giữ được lưng phẳng hoặc hơi cuộn nhẹ.",
                    "Phát lực từ cơ bụng và cơ xô để kéo bánh xe lăn ngược trở về ngay dưới vai.",
                    "Lưu ý kỹ thuật: Khép khung sườn và cuộn nhẹ khung chậu",
                    "Lưu ý kỹ thuật: Gồng chặt cơ mông và cơ bụng cùng lúc",
                    "Lưu ý kỹ thuật: Chỉ lăn xa trong tầm kiểm soát của lưng dưới",
                ],
                "breathing": [
                    "Hít sâu và gồng bụng khi lăn bánh xe ra trước, và thở ra khi kéo bánh xe thu về.",
                    "Tránh: Để lưng dưới bị võng sụp xuống về phía mặt sàn",
                    "Tránh: Đẩy lùi mông ngồi về phía gót chân thay vì dùng cơ bụng kéo về",
                ],
            },
        },
        {
            "id": "0851",
            "slug": "weighted-sissy-squat",
            "name": "Sissy Squat (Weighted / Bodyweight)",
            "nameVi": "Quỳ ngả người gánh đùi trước",
            "aliases": [
                "sissy squat",
                "weighted sissy squat",
                "quad isolation squat",
            ],
            "category": "Quads",
            "equipment": "Bodyweight",
            "videoUrl": video_paths["0851"],
            "primaryMuscles": ["Quads"],
            "secondaryMuscles": ["Core", "Calves"],
            "primarySlugs": ["quadriceps"],
            "secondarySlugs": ["abs", "calves"],
            "shortDescription": "Extreme knee-flexion quad isolation squat leaning the torso and hips back as the knees travel forward.",
            "steps": {
                "prepare": [
                    "Stand tall holding a sturdy support with one hand and optionally a weight plate against your chest.",
                    "Rise slightly onto the balls of your feet and brace your abs and glutes so your hips and torso form a straight line.",
                ],
                "execution": [
                    "Push your knees forward and lean your entire body backward as one straight plank from knees to shoulders.",
                    "Lower until you feel a deep stretch in your quadriceps while keeping your hips fully extended.",
                    "Extend your knees to drive yourself back up to the starting position.",
                    "Form cue: Keep hips locked in line with torso and thighs",
                    "Form cue: Push knees forward under control",
                    "Form cue: Use a support hand for balance",
                ],
                "breathing": [
                    "Inhale as you lean back and bend your knees, and exhale as you drive back up.",
                    "Avoid: Bending at the hips and sitting backward at the bottom",
                    "Avoid: Dropping into the bottom position without control",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đứng thẳng, một tay vịn vào điểm tựa chắc chắn và tay kia có thể ôm thêm bánh tạ trước ngực.",
                    "Nhón nhẹ lên phần mũi bàn chân, đồng thời gồng chặt cơ bụng và cơ mông sao cho từ đầu gối qua hông đến vai tạo thành một đường thẳng.",
                ],
                "execution": [
                    "Đẩy hai đầu gối về phía trước và ngả toàn bộ thân người ra sau như một tấm ván thẳng từ đầu gối đến vai.",
                    "Hạ thấp xuống cho đến khi cảm nhận cơ đùi trước căng giãn mạnh mà vẫn giữ khớp hông duỗi thẳng.",
                    "Duỗi khớp gối để đẩy cơ thể nâng lên trở lại vị trí bắt đầu.",
                    "Lưu ý kỹ thuật: Giữ khớp hông thẳng hàng với thân người và đùi",
                    "Lưu ý kỹ thuật: Đẩy đầu gối ra trước có kiểm soát",
                    "Lưu ý kỹ thuật: Vịn tay vào điểm tựa để giữ thăng bằng",
                ],
                "breathing": [
                    "Hít vào khi ngả người ra sau hạ thấp gối, và thở ra khi đạp duỗi gối nâng người lên.",
                    "Tránh: Gập khớp hông đẩy mông ra sau ở điểm thấp nhất",
                    "Tránh: Hạ người đột ngột không kiểm soát gây áp lực lên khớp gối",
                ],
            },
        },
        {
            "id": "0284",
            "slug": "donkey-calf-raise",
            "name": "Donkey Calf Raise",
            "nameVi": "Gập người nhón bắp chân",
            "aliases": [
                "donkey calf raise",
                "bent over calf raise",
            ],
            "category": "Calves",
            "equipment": "Bodyweight",
            "videoUrl": video_paths["0284"],
            "primaryMuscles": ["Calves"],
            "secondaryMuscles": [],
            "primarySlugs": ["calves"],
            "secondarySlugs": [],
            "shortDescription": "Hinged-hip calf raise placing the gastrocnemius under a deep stretch at the bottom of every rep.",
            "steps": {
                "prepare": [
                    "Stand with the balls of your feet on an elevated block or step and hinge forward at the hips to place your hands or forearms on a support.",
                    "Keep your knees straight (with a micro-bend) and your back flat.",
                ],
                "execution": [
                    "Lower your heels as far below the block as possible until you feel a deep stretch in your calves.",
                    "Drive up onto the balls of your feet as high as you can and pause for 1 second at peak contraction.",
                    "Lower slowly back into the full stretch position.",
                    "Form cue: Full pause at top and bottom",
                    "Form cue: Keep hips hinged at 90 degrees",
                    "Form cue: Drive straight through big toe",
                ],
                "breathing": [
                    "Inhale as your heels lower into the stretch, and exhale as you press up onto your toes.",
                    "Avoid: Bouncing quickly out of the bottom stretch",
                    "Avoid: Bending and straightening the knees to assist the lift",
                ],
            },
            "stepsVi": {
                "prepare": [
                    "Đứng đặt phần ức bàn chân lên bục kê cao và gập người về trước từ khớp hông, hai tay hoặc cẳng tay tỳ lên điểm tựa phía trước.",
                    "Giữ hai chân thẳng (khớp gối hơi mở nhẹ tự nhiên) và lưng phẳng.",
                ],
                "execution": [
                    "Hạ hai gót chân xuống thấp nhất có thể bên dưới mặt bục cho đến khi cảm nhận cơ bắp chân căng giãn sâu.",
                    "Nhón mạnh lên phần ức bàn chân cao hết mức có thể và giữ 1 giây ở đỉnh co cơ.",
                    "Từ từ hạ chậm gót chân trở lại vị trí kéo giãn hoàn toàn.",
                    "Lưu ý kỹ thuật: Dừng 1 giây ở cả điểm cao nhất và điểm thấp nhất",
                    "Lưu ý kỹ thuật: Giữ góc gập hông cố định khoảng 90 độ",
                    "Lưu ý kỹ thuật: Đạp lực thẳng qua phần ức ngón chân cái",
                ],
                "breathing": [
                    "Hít vào khi hạ gót chân xuống kéo giãn, và thở ra khi nhón cao mũi chân lên.",
                    "Tránh: Nhún nảy nhanh ở điểm dưới cùng làm mất tác dụng vào cơ bắp chân",
                    "Tránh: Nhún gập đầu gối để ăn gian lấy đà",
                ],
            },
        },
    ]

    existing_ids = {ex["id"] for ex in exercises}
    added_count = 0
    for new_ex in new_exercises:
        if new_ex["id"] not in existing_ids:
            exercises.append(new_ex)
            existing_ids.add(new_ex["id"])
            added_count += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)

    print(f"Done! Renamed 4 RDL/Face Pull exercises and added {added_count} new famous exercises. Total exercises: {len(exercises)}")


if __name__ == "__main__":
    main()
