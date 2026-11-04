#!/usr/bin/env python3
"""
Populates 100% pure Vietnamese names (nameVi) and step-by-step coaching
instructions (stepsVi) with no English mixed in for all 179 exercises in
src/data/exercises.json.
"""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "src" / "data" / "exercises.json"

EXACT_VI_NAMES = {
    "1435": "Gánh tạ đòn sau vai",
    "0025": "Đẩy ngực ghế phẳng với tạ đòn",
    "0028": "Cử đẩy tạ đòn qua đầu",
    "0030": "Đẩy ngực hẹp tay với tạ đòn",
    "0031": "Cuốn tạ đòn tập tay trước",
    "0033": "Đẩy ngực dưới ghế dốc với tạ đòn",
    "0038": "Kéo trượt tạ đòn dọc thân tập tay trước",
    "0041": "Nâng tạ đòn ra trước tập vai trước",
    "0042": "Gánh tạ đòn trước ngực",
    "0047": "Đẩy ngực trên ghế dốc với tạ đòn",
    "0054": "Chùng chân bước tới với tạ đòn",
    "0072": "Nằm sấp ghế dốc cuốn tạ đòn tập tay trước",
    "0075": "Gập người kéo tạ đòn tập vai sau",
    "0082": "Cuốn cổ tay ngược với tạ đòn",
    "drv-barbell-seated-behind-head-military-press": "Ngồi đẩy vai sau cổ với tạ đòn",
    "0095": "Nhún cầu vai với tạ đòn",
    "0104": "Đứng cuốn cổ tay sau lưng với tạ đòn",
    "0116": "Kéo tạ đòn thẳng chân tập đùi sau",
    "0027": "Gập người chèo tạ đòn ngửa tay",
    "0123": "Kéo tạ đòn thẳng đứng tay rộng tập vai",
    "0248": "Nằm sấp trên ghế chèo tạ đòn tựa ngực",
    "0562": "Xoay tạ đòn một đầu tập cơ liên sườn",
    "0553": "Đứng đẩy vai với tạ đòn",
    "0301": "Đẩy ngực dưới ghế dốc với tạ đơn",
    "0302": "Ép ngực trên ghế dốc xuống với tạ đơn",
    "0361": "Đẩy vai luân phiên từng tay với tạ đơn",
    "2137": "Đẩy vai xoay cổ tay với tạ đơn",
    "0364": "Đứng cuốn cổ tay sau lưng với tạ đơn",
    "0293": "Gập người chèo tạ đơn tập lưng",
    "0294": "Đứng cuốn tạ đơn tập tay trước",
    "0296": "Nằm đẩy ngực hẹp tay với tạ đơn",
    "0297": "Ngồi cuốn tạ đơn tỳ đùi tập tay trước",
    "0298": "Cuốn tạ đơn búa ngang ngực",
    "0300": "Kéo tạ đơn từ sàn tập mông và đùi",
    "0308": "Nằm ghế phẳng ép ngực với tạ đơn",
    "1277": "Nằm trên bóng tập ép ngực với tạ đơn",
    "0310": "Nâng tạ đơn ra trước tập vai trước",
    "1760": "Gánh tạ đơn ôm trước ngực",
    "1330": "Chèo tạ đơn tựa ngực cầm dọc trên ghế dốc",
    "0314": "Đẩy ngực trên ghế dốc với tạ đơn",
    "0322": "Ngồi ghế dốc cuốn tạ đơn tập tay trước",
    "0318": "Ngồi ngả lưng cuốn tạ đơn tập tay trước",
    "0319": "Nằm ghế dốc lên ép ngực với tạ đơn",
    "1278": "Tựa bóng tập dốc lên ép ngực với tạ đơn",
    "0320": "Ngồi ghế dốc cuốn tạ đơn kiểu búa",
    "0321": "Đẩy ngực trên ghế dốc cầm tạ dọc",
    "0326": "Nằm sấp ghế dốc dang tạ đơn tập vai sau",
    "0327": "Chèo tạ đơn tựa ngực trên ghế dốc",
    "0329": "Nằm sấp ghế dốc nhún cầu vai với tạ đơn",
    "0330": "Nằm ghế dốc duỗi tạ đơn tập tay sau",
    "0332": "Dang tạ đơn chữ thập tập vai",
    "0333": "Gập người đá tạ đơn ra sau tập tay sau",
    "0334": "Đứng dang tạ đơn sang ngang tập vai giữa",
    "0336": "Chùng chân bước tới với tạ đơn",
    "1729": "Nằm duỗi tạ đơn luân phiên tập tay sau",
    "0340": "Nằm ghế phẳng đẩy ngực cầm tạ dọc",
    "0343": "Nằm sấp kẹp tạ đơn gập chân tập đùi sau",
    "1328": "Nằm sấp trên ghế chèo tạ đơn tập vai sau",
    "0351": "Nằm ghế phẳng duỗi tạ đơn tập tay sau",
    "0355": "Đứng dang một tay tạ đơn tập vai giữa",
    "1672": "Cuốn tạ đơn một tay xoay cổ tay trên bệ tỳ",
    "0306": "Duỗi tạ đơn một tay qua đầu tập tay sau",
    "0369": "Tỳ cẳng tay trên ghế cuốn cổ tay với tạ đơn",
    "1329": "Gập người chèo tạ đơn xoay cổ tay",
    "1673": "Tỳ tay trên bóng tập cuốn tạ đơn",
    "0373": "Duỗi tạ đơn tập tay sau cầm úp tay",
    "0374": "Nằm sấp ghế dốc cuốn tạ đơn tập tay trước",
    "0377": "Gập người chèo tạ đơn mở khuỷu tay tập vai sau",
    "1379": "Ngồi đặt tạ đơn lên gối nhón bắp chân",
    "0392": "Ngồi nâng tạ đơn ra trước tập vai trước",
    "0394": "Ngồi gập người đá tạ đơn ra sau tập tay sau",
    "0396": "Ngồi dang tạ đơn sang ngang tập vai giữa",
    "0397": "Ngồi cuốn cổ tay cầm tạ dọc",
    "0402": "Ngồi cuốn tạ đơn trên bệ tỳ tay trước",
    "2188": "Ngồi duỗi tạ đơn hai tay qua đầu tập tay sau",
    "0406": "Đứng nhún cầu vai với tạ đơn",
    "0407": "Đứng nghiêng lườn với tạ đơn tập liên sườn",
    "0409": "Đứng một chân nhón bắp chân với tạ đơn",
    "0411": "Gánh tạ một chân với tạ đơn",
    "0413": "Gánh tạ hai chân với tạ đơn",
    "0417": "Đứng nhón bắp chân với tạ đơn",
    "0432": "Kéo tạ đơn thẳng chân tập đùi sau",
    "new-dumbbell-sumo-squat": "Gánh tạ đơn chân rộng tập đùi trong và mông",
    "0437": "Kéo tạ đơn thẳng đứng tập vai và cầu vai",
    "0285": "Ngồi cuốn tạ đơn luân phiên từng tay",
    "0289": "Ngồi đẩy vai với tạ đơn",
    "1757": "Đứng kéo một tạ đơn thẳng chân tập đùi sau",
    "0777": "Xoay tạ đơn hai bên hông tập cơ bụng",
    "0350": "Nằm ngửa cuốn tạ đơn tập tay trước",
    "0489": "Gập lưng dưới trên ghế dốc 45 độ",
    "drv-close-feet-leg-press": "Đạp đùi trên máy chân đặt hẹp",
    "0573": "Gập duỗi lưng dưới trên máy tập",
    "0581": "Kéo xô góc cao trên máy lắp tạ",
    "2611": "Đạp đùi phương ngang trên máy",
    "1299": "Đẩy ngực trên máy dốc lên tay cầm dọc",
    "0582": "Quỳ gập chân một bên trên máy tập đùi sau",
    "0584": "Ngồi dang vai sang ngang trên máy",
    "0585": "Ngồi đá đùi trước trên máy",
    "0577": "Đẩy ngực trên máy tập",
    "0586": "Nằm sấp gập chân trên máy tập đùi sau",
    "0592": "Ngồi cuốn tay trước trên máy có bệ tỳ",
    "0593": "Nằm sấp nâng hai chân ngược trên máy tập mông",
    "1349": "Chèo tạ máy tựa ngực tay đòn",
    "0594": "Ngồi nhón bắp chân trên máy",
    "1452": "Ngồi gập bụng trên máy tập",
    "1451": "Ngồi nhấn tay sau trên máy",
    "0597": "Ngồi ép mở đùi ngoài và mông trên máy",
    "0598": "Ngồi ép khép đùi trong trên máy",
    "0599": "Ngồi gập chân trên máy tập đùi sau",
    "0602": "Ngồi ép ngực ngược trên máy tập vai sau",
    "0604": "Đứng nhún cầu vai trên máy",
    "0605": "Đứng nhón bắp chân trên máy",
    "2286": "Đứng đạp chân ra sau trên máy tập mông",
    "drv-lever-standing-rear-kick": "Đứng đá chân ra sau trên máy tập mông",
    "drv-lever-t-bar-row": "Chèo tạ đòn chữ T tựa ngực trên máy",
    "0607": "Ngồi duỗi tay sau trên máy",
    "drv-lever-pec-deck-fly": "Ngồi ép ngực trên máy",
    "0673": "Ngồi kéo xô ngửa tay trên máy",
    "0738": "Đạp nhón bắp chân trên máy nghiêng 45 độ",
    "0740": "Đạp đùi chân rộng trên máy nghiêng 45 độ",
    "0743": "Gánh đùi tựa lưng trên máy trượt",
    "0750": "Gánh tạ chân đưa trước trên khung máy trượt",
    "1393": "Đứng nhón bắp chân trên khung máy trượt",
    "0752": "Kéo tạ từ sàn trên khung máy trượt",
    "0748": "Nằm đạp đùi thẳng đứng trên khung máy trượt",
    "0765": "Ngồi đẩy vai trên khung máy trượt",
    "0128": "Quật dây thừng thể lực",
    "0974": "Kéo cáp xô tay cầm hẹp",
    "0154": "Đứng kéo cáp chéo ngược tập vai sau",
    "0175": "Quỳ kéo cáp gập bụng",
    "0178": "Đứng kéo cáp sang ngang tập vai giữa",
    "0186": "Nằm ghế phẳng duỗi cáp tập tay sau",
    "0190": "Đứng cuốn cáp một tay tập tay trước",
    "0162": "Đứng kéo cáp một tay ra trước tập vai trước",
    "2616": "Kéo cáp xô một tay",
    "0192": "Đứng kéo cáp một tay sang ngang tập vai giữa",
    "0861": "Ngồi kéo cáp lưng một tay kết hợp xoay người",
    "0198": "Kéo cáp thẳng xuống tập cơ xô",
    "0203": "Kéo cáp dây thừng về phía mặt tập vai sau",
    "0194": "Đứng quay lưng duỗi cáp dây thừng qua đầu tập tay sau",
    "0200": "Đứng nhấn cáp dây thừng tập tay sau",
    "0213": "Ngồi kéo cáp lưng góc cao tay cầm chữ V",
    "0226": "Đứng kéo cáp gập bụng",
    "1269": "Đứng ép ngực với dây cáp",
    "0229": "Đứng cuốn cáp hướng vào trong tập tay trước",
    "0230": "Đứng kéo cáp chéo từ dưới lên tập cơ liên sườn",
    "0231": "Đứng nhấn cáp một tay tập tay sau",
    "0238": "Đứng kéo cáp thẳng tay tập cơ xô",
    "1723": "Đứng nhấn cáp thanh thẳng tập tay sau",
    "0862": "Đứng xoay người với dây cáp tập liên sườn",
    "0620": "Nằm ghế phẳng ép ngực với dây cáp",
    "2612": "Nhảy dây",
    "0207": "Ngồi kéo cáp xô ngửa bàn tay",
    "0208": "Ngồi kéo cáp lưng thấp tay cầm chữ V",
    "0218": "Ngồi kéo cáp lưng thấp tay cầm rộng",
    "drv-cable-bar-lateral-pulldown-wide-shoulder-grip": "Ngồi kéo cáp xô tay cầm rộng",
    "2407": "Đứng cuốn thanh đòn cong tập tay trước",
    "0061": "Nằm ghế phẳng duỗi thanh đòn cong tập tay sau",
    "0445": "Nằm sấp ghế dốc đẩy thanh đòn cong qua đầu",
    "drv-kettlebell-deadlift": "Kéo tạ ấm từ sàn tập đùi và mông",
    "drv-bench-dips": "Chống đẩy tay sau trên ghế băng",
    "0570": "Kéo xà đơn hỗ trợ chân trên ghế",
    "drv-chest-dips": "Nhún xà kép nghiêng người tập ngực dưới",
    "0253": "Kéo xà đơn hai lòng bàn tay hướng vào nhau",
    "2987": "Kéo xà đơn ngửa tay cầm hẹp",
    "0259": "Hít đất hẹp tay tập tay sau và ngực trong",
    "drv-commando-pull-up": "Kéo xà đơn dọc thanh xà",
    "1274": "Hít đất biên độ sâu",
    "0493": "Hít đất tay chống cao trên ghế",
    "0499": "Nằm ngửa kéo lưng giữa hai ghế",
    "0498": "Nằm ngửa kéo lưng với dây treo",
    "1429": "Kéo xà đơn tay rộng tập xô",
    "drv-chin-ups-pull-ups": "Kéo xà đơn cơ bản",
    "drv-push-ups": "Hít đất cơ bản",
    "0672": "Giãn cơ vai và ngực trên ghế băng",
    "2327": "Kéo xà đơn ngửa lòng bàn tay",
    "3012": "Nhún bả vai trên xà kép",
    "0651": "Kéo xà đơn tay rộng bằng vai",
    "drv-triceps-dips": "Nhún xà kép thân thẳng tập tay sau",
}


def build_vi_steps(ex: dict) -> dict:
    nl = ex["name"].lower()
    eq = ex["equipment"]

    eq_vi = {
        "Barbell": "tạ đòn",
        "Dumbbell": "tạ đơn",
        "Cable": "dây cáp",
        "Machine": "máy tập",
        "EZ-Bar": "thanh đòn cong",
        "Kettlebell": "tạ ấm",
        "Bodyweight": "trọng lượng cơ thể",
    }.get(eq, "dụng cụ tập")

    # 1. CHEST-SUPPORTED ROW VARIATIONS
    if "chest-supported" in nl or "t-bar row" in nl or "seal row" in nl:
        return {
            "prepare": [
                "Nằm sấp hoặc áp sát lồng ngực vào đệm tựa ngực của ghế hoặc máy, hai chân đặt vững trên sàn hoặc bàn đạp.",
                f"Hai tay vươn thẳng nắm {eq_vi}, thả lỏng bả vai ở vị trí bắt đầu để kéo giãn cơ lưng trên và cơ xô.",
            ],
            "execution": [
                "Giữ ngực luôn áp sát đệm tựa (không nhấc ngực lấy đà), phát lực khép hai bả vai và kéo khuỷu tay mạnh về phía sau.",
                "Kéo tạ lên hết biên độ và giữ siết chặt cơ lưng giữa cùng cơ xô trong 1 giây ở đỉnh.",
                "Từ từ hạ tạ xuống có kiểm soát về vị trí duỗi thẳng tay ban đầu.",
                "Lưu ý kỹ thuật: Nhờ có đệm đỡ ngực, lưng dưới được cố định an toàn—hãy tập trung tối đa vào co rút cơ lưng.",
            ],
            "breathing": [
                "Thở ra khi kéo tạ lên, hít vào sâu khi duỗi tay hạ tạ.",
                "Tránh: Nhổm ngực rời khỏi đệm ghế hoặc nhún cầu vai lên tai.",
            ],
        }

    # 2. LEG EXTENSION / LEG CURL / HIP ABDUCTION / ADDUCTION / LEG PRESS / HACK SQUAT
    if "leg extension" in nl:
        return {
            "prepare": [
                "Ngồi vào máy đá đùi, chỉnh đệm lưng sao cho kheo gối vừa khít mép ghế và đệm cổ chân nằm ngay trên mu bàn chân.",
                "Hai tay nắm chặt tay cầm hai bên ghế để cố định phần hông và mông không bị nhấc lên.",
            ],
            "execution": [
                "Phát lực từ cơ đùi trước đá thẳng hai chân lên cho đến khi gối duỗi hoàn toàn.",
                "Siết cứng cơ đùi trước ở điểm cao nhất trong 1 giây.",
                "Từ từ hạ chân xuống có kiểm soát về vị trí ban đầu mà không để bánh tạ chạm mạnh xuống.",
            ],
            "breathing": [
                "Thở ra khi đá chân lên, hít vào khi hạ chân xuống.",
                "Tránh: Đá giật cục theo quán tính hoặc nhấc mông khỏi ghế.",
            ],
        }

    if "leg curl" in nl:
        return {
            "prepare": [
                f"Vào tư thế chuẩn bị với {eq_vi}, căn chỉnh khớp gối thẳng hàng và cố định đệm đỡ ngay phía trên gót chân.",
                "Giữ phần hông và đùi áp sát cố định vào đệm ghế.",
            ],
            "execution": [
                "Gập đầu gối để cuốn tạ hết biên độ bằng lực co của cơ đùi sau.",
                "Giữ và siết chặt cơ đùi sau ở điểm co rút tối đa trong 1 giây.",
                "Hạ tạ từ từ và có kiểm soát về vị trí duỗi chân ban đầu.",
            ],
            "breathing": [
                "Thở ra khi cuốn chân, hít vào khi duỗi chân trả tạ.",
                "Tránh: Nhấc hông lên khỏi mặt đệm hoặc thả tạ rơi tự do.",
            ],
        }

    if "leg press" in nl or "hack squat" in nl:
        return {
            "prepare": [
                "Tựa sát toàn bộ lưng dưới và mông vào đệm lưng của máy, đặt hai bàn chân lên bàn đạp rộng bằng vai.",
                "Mở chốt an toàn của máy và giữ hai đầu gối thẳng hướng với mũi chân.",
            ],
            "execution": [
                "Từ từ gập gối hạ tạ xuống có kiểm soát cho đến khi đùi và cẳng chân tạo góc khoảng 90 độ mà mông không bị cuộn rời khỏi đệm.",
                "Đạp mạnh qua gót chân và giữa bàn chân để đẩy bàn đạp lên, dừng lại ngay trước khi khóa cứng khớp gối.",
                "Lưu ý kỹ thuật: Luôn ép chặt lưng dưới vào đệm ghế và giữ gối mở theo hướng mũi chân.",
            ],
            "breathing": [
                "Hít sâu khi hạ tạ xuống, thở ra mạnh khi đạp tạ lên.",
                "Tránh: Khóa thẳng cứng khớp gối ở đỉnh hoặc để hai gối chụm vào nhau.",
            ],
        }

    if "abduction" in nl or "adduction" in nl:
        is_abd = "abduction" in nl
        return {
            "prepare": [
                "Ngồi thẳng lưng trên máy, đặt hai đùi vào đệm đỡ và nắm tay cầm hai bên.",
                "Cố định vùng chậu và cột sống lưng.",
            ],
            "execution": [
                "Phát lực đẩy hai đùi mở rộng ra ngoài hết biên độ và siết cơ mông trong 1 giây."
                if is_abd
                else "Phát lực từ cơ đùi trong ép hai đùi khép lại vào nhau và giữ siết 1 giây.",
                "Từ từ kiểm soát tạ trở về vị trí bắt đầu mà không để bánh tạ va vào nhau.",
            ],
            "breathing": [
                "Thở ra khi phát lực đẩy hoặc ép, hít vào khi trả tạ chậm rãi.",
                "Tránh: Dùng đà giật mạnh hoặc nhấc lưng rời khỏi ghế.",
            ],
        }

    # 3. HYPEREXTENSION / BACK EXTENSION
    if "hyperextension" in nl or "back extension" in nl:
        return {
            "prepare": [
                "Đặt hông lên đệm đỡ của ghế tập lưng dưới, cố định cổ chân vào đệm giữ.",
                "Giữ cột sống lưng hoàn toàn thẳng tự nhiên, hai tay khoanh trước ngực.",
            ],
            "execution": [
                "Từ từ gập tại khớp hông để hạ thân trên xuống trong khi vẫn giữ lưng thẳng cho đến khi cảm nhận đùi sau căng.",
                "Siết chặt cơ mông và cơ lưng dưới để nâng thân người lên cho đến khi thân trên thẳng hàng với chân.",
            ],
            "breathing": [
                "Hít vào khi hạ thân người xuống, thở ra khi nâng người lên.",
                "Tránh: Ưỡn cong ngược cột sống lưng dưới quá mức ở đỉnh chuyển động.",
            ],
        }

    # 4. PULL-UP / CHIN-UP / DIP / PUSH-UP
    if "pull-up" in nl or "chin-up" in nl:
        return {
            "prepare": [
                "Hai tay nắm chặt thanh xà đơn, treo người thẳng tay và hạ bả vai xuống.",
                "Gồng chặt cơ bụng và giữ thân người ổn định, không đung đưa.",
            ],
            "execution": [
                "Phát lực từ cơ xô và cơ tay kéo ngực trên lên về phía thanh xà bằng cách ép mạnh khuỷu tay xuống dưới.",
                "Kéo lên cho đến khi cằm vượt qua thanh xà, sau đó từ từ hạ người xuống có kiểm soát về tư thế duỗi thẳng tay.",
            ],
            "breathing": [
                "Thở ra khi kéo người lên, hít vào khi hạ người xuống.",
                "Tránh: Đạp giật chân lấy đà hoặc không hạ hết biên độ tay.",
            ],
        }

    if "dip" in nl or "push-up" in nl:
        return {
            "prepare": [
                "Đặt hai tay vững chắc trên thanh xà kép, ghế băng hoặc mặt sàn, hạ bả vai xuống và gồng chặt cơ bụng.",
                "Giữ trục thân người, cột sống và cổ thẳng hàng.",
            ],
            "execution": [
                "Từ từ gập khuỷu tay để hạ thân người xuống có kiểm soát cho đến khi cánh tay trên song song với mặt sàn.",
                "Phát lực qua lòng bàn tay đẩy mạnh thân người lên về vị trí duỗi thẳng tay ban đầu.",
            ],
            "breathing": [
                "Hít vào khi hạ người xuống, thở ra khi đẩy người lên.",
                "Tránh: Nhún vai lên tai hoặc để lưng dưới bị võng xuống.",
            ],
        }

    # 5. SQUAT VARIATIONS
    if "front squat" in nl:
        return {
            "prepare": [
                "Đặt thanh đòn lên giá đỡ ngang tầm xương đòn, bước vào dưới thanh đòn và đặt tạ lên phần cơ vai trước.",
                "Nâng cao khuỷu tay song song với sàn, nhấc tạ ra khỏi giá và đứng hai chân rộng bằng vai, mũi chân hơi mở 15–30 độ.",
            ],
            "execution": [
                "Gồng chặt bụng, giữ lưng thẳng đứng và từ từ hạ hông xuống đồng thời mở gối theo hướng mũi chân.",
                "Hạ sâu cho đến khi đùi song song hoặc thấp hơn mặt sàn, luôn giữ khuỷu tay hướng cao.",
                "Đạp mạnh qua gót chân và giữa bàn chân để đứng thẳng dậy.",
            ],
            "breathing": [
                "Hít sâu vào bụng và gồng cơ trung tâm trước khi hạ người, thở ra mạnh khi đạp lên.",
                "Tránh: Để khuỷu tay bị sụp xuống hoặc cong lưng dưới.",
            ],
        }

    if "squat" in nl:
        return {
            "prepare": [
                f"Chuẩn bị tư thế vững chắc với {eq_vi}, hai chân mở rộng bằng vai và mũi chân xoay nhẹ ra ngoài 15–30 độ.",
                "Mắt nhìn thẳng, ngực mở cao và gồng cứng cơ bụng.",
            ],
            "execution": [
                "Đẩy hông ra sau và gập đầu gối cùng lúc, giữ đầu gối mở theo đúng hướng mũi chân.",
                "Hạ thân người xuống có kiểm soát cho đến khi đùi song song hoặc thấp hơn mặt sàn.",
                "Đạp mạnh qua lòng bàn chân và gót chân để đứng thẳng dậy về vị trí ban đầu.",
                "Lưu ý kỹ thuật: Giữ ngực mở, lưng thẳng, không để đầu gối chụm vào trong.",
            ],
            "breathing": [
                "Hít sâu vào bụng và gồng cơ trung tâm trước khi hạ người, thở ra khi đẩy lên qua điểm nặng nhất.",
                "Tránh: Chụm đầu gối vào trong hoặc cong tròn lưng dưới.",
            ],
        }

    # 6. LUNGE VARIATIONS
    if "lunge" in nl:
        return {
            "prepare": [
                f"Giữ {eq_vi} ổn định, đứng thẳng hai chân rộng bằng hông.",
                "Gồng chặt cơ bụng và bước một chân dài về phía trước có kiểm soát.",
            ],
            "execution": [
                "Hạ thấp trọng tâm thẳng xuống cho đến khi cả hai gối tạo góc khoảng 90 độ, gối sau gần chạm sàn.",
                "Giữ thân trên thẳng đứng, toàn bộ bàn chân trước bám chắc trên mặt sàn.",
                "Đạp mạnh qua gót chân trước để trở về vị trí đứng thẳng.",
            ],
            "breathing": [
                "Hít vào khi bước lên và hạ trọng tâm, thở ra khi đạp chân đứng dậy.",
                "Tránh: Bước quá ngắn làm nhón gót chân trước hoặc mất thăng bằng.",
            ],
        }

    # 7. DEADLIFT
    if "deadlift" in nl:
        return {
            "prepare": [
                f"Đứng thẳng, hai chân mở rộng bằng hông, hai tay nắm {eq_vi} đặt sát phía trước đùi.",
                "Hơi trùng nhẹ đầu gối khoảng 15 độ, ép bả vai và gồng chặt cơ bụng.",
            ],
            "execution": [
                "Thực hiện chuyển động gập hông bằng cách đẩy mông thẳng ra phía sau, giữ tạ trượt sát dọc theo đùi và ống quyển.",
                "Giữ cột sống lưng hoàn toàn thẳng tự nhiên, hạ tạ xuống đến khi cảm nhận cơ đùi sau căng tối đa.",
                "Đẩy mạnh hông về phía trước và siết chặt cơ mông để đứng thẳng dậy.",
            ],
            "breathing": [
                "Hít sâu và gồng cứng bụng trước khi gập người xuống, thở ra khi đẩy hông đứng thẳng lên.",
                "Tránh: Cong lưng dưới hoặc để tạ rời xa khỏi thân người.",
            ],
        }

    # 8. BENCH PRESS / CHEST PRESS
    if "press" in nl and ("bench" in nl or "chest" in nl or "incline" in nl or "decline" in nl or "lying" in nl or "close-grip" in nl or "close grip" in nl):
        return {
            "prepare": [
                "Nằm hoặc tựa lưng vững chãi trên ghế tập, hai bàn chân đặt bám chặt xuống mặt sàn.",
                f"Ép chặt hai bả vai xuống mặt ghế, hai tay nắm {eq_vi} với cổ tay thẳng.",
            ],
            "execution": [
                "Đưa tạ về vị trí bắt đầu với hai tay duỗi thẳng.",
                "Từ từ hạ tạ về phía ngực dưới sự kiểm soát, giữ khuỷu tay khép góc khoảng 45–60 độ so với thân người.",
                "Phát lực từ cơ ngực và tay sau đẩy mạnh tạ thẳng ra về vị trí ban đầu.",
            ],
            "breathing": [
                "Hít sâu khi hạ tạ về ngực, thở ra mạnh khi đẩy tạ ra.",
                "Tránh: Xòe khuỷu tay ngang 90 độ gây áp lực khớp vai hoặc nhấc mông khỏi ghế.",
            ],
        }

    # 9. FLY / PEC DECK / REVERSE FLY
    if "fly" in nl or "pec deck" in nl:
        if "reverse" in nl or "rear" in nl:
            return {
                "prepare": [
                    f"Ngồi hoặc đứng vững với {eq_vi}, giữ lưng thẳng và hơi gập nhẹ khuỷu tay ở góc cố định.",
                    "Hạ thấp cầu vai để cô lập hoàn toàn vào phần cơ vai sau.",
                ],
                "execution": [
                    "Mở rộng hai cánh tay sang hai bên về phía sau theo hình vòng cung cho đến khi ngang vai.",
                    "Siết nhẹ cơ vai sau và lưng trên ở điểm cuối trong 1 giây.",
                    "Từ từ kiểm soát tạ trở lại vị trí ban đầu.",
                ],
                "breathing": [
                    "Thở ra khi mở tay sang ngang, hít vào khi thu tay về.",
                    "Tránh: Vung người lấy đà hoặc gồng co rút cơ cầu vai.",
                ],
            }
        return {
            "prepare": [
                f"Vào tư thế chuẩn bị với {eq_vi}, ép chặt hai bả vai ra sau để mở rộng lồng ngực.",
                "Giữ hai tay hơi cong nhẹ ở khuỷu tay suốt bài tập.",
            ],
            "execution": [
                "Từ từ mở rộng hai cánh tay sang hai bên cho đến khi cơ ngực được kéo giãn tối đa.",
                "Phát lực từ cơ ngực để ép hai tay khép lại phía trước ngực và giữ siết cơ ngực 1 giây.",
                "Kiểm soát tạ chậm rãi trong lượt mở tay tiếp theo.",
            ],
            "breathing": [
                "Hít sâu khi mở rộng tay, thở ra khi ép ngực khép tay lại.",
                "Tránh: Duỗi thẳng khóa cứng khuỷu tay hoặc dùng lực vai đẩy tạ.",
            ],
        }

    # 10. LAT PULLDOWN
    if "pulldown" in nl:
        return {
            "prepare": [
                "Điều chỉnh đệm giữ đùi sao cho chân được cố định chắc chắn trên ghế.",
                "Nắm thanh kéo với độ rộng phù hợp, ngồi thẳng lưng và mở cao lồng ngực.",
            ],
            "execution": [
                "Hơi ngả nhẹ thân người ra sau khoảng 10–15 độ, hạ bả vai xuống.",
                "Kéo thanh cầm xuống phía ngực trên bằng cách dẫn lực từ hai khuỷu tay ép xuống và ra sau.",
                "Siết chặt cơ xô ở điểm dưới cùng, sau đó từ từ thả lên có kiểm soát cho đến khi cơ xô giãn hết cỡ.",
            ],
            "breathing": [
                "Thở ra khi kéo xuống ngực, hít vào khi kiểm soát tạ đi lên.",
                "Tránh: Ngả người giật tạ bằng lưng dưới hoặc nhún vai.",
            ],
        }

    # 11. UPRIGHT ROW & GENERAL ROWS
    if "upright row" in nl:
        return {
            "prepare": [
                f"Đứng thẳng, hai tay nắm {eq_vi} đặt trước đùi, chân rộng bằng vai.",
                "Giữ lưng thẳng, gồng nhẹ cơ bụng.",
            ],
            "execution": [
                "Kéo tạ thẳng lên dọc sát thân người bằng cách nâng hai khuỷu tay lên cao và sang ngang.",
                "Dừng lại khi khuỷu tay ngang tầm vai, sau đó hạ tạ từ từ về vị trí ban đầu.",
            ],
            "breathing": [
                "Thở ra khi kéo tạ lên, hít vào khi hạ tạ xuống.",
                "Tránh: Kéo quá cao vượt quá khớp vai hoặc dùng lưng giật tạ.",
            ],
        }

    if "row" in nl:
        return {
            "prepare": [
                f"Vào tư thế chuẩn bị vững chắc với {eq_vi}, giữ cột sống lưng hoàn toàn thẳng và ngực mở.",
                "Duỗi thẳng tay cầm tạ ở vị trí bắt đầu, cảm nhận bả vai được kéo giãn tự nhiên.",
            ],
            "execution": [
                "Khởi động lực kéo bằng cách khép bả vai và kéo khuỷu tay mạnh về phía sau sát thân người.",
                "Kéo tạ về phía thân người và siết chặt cơ lưng trong 1 giây.",
                "Hạ tạ từ từ theo đúng quỹ đạo về vị trí duỗi thẳng tay mà không làm cong lưng.",
            ],
            "breathing": [
                "Thở ra khi kéo tạ vào thân người, hít vào khi duỗi tay hạ tạ.",
                "Tránh: Cong lưng dưới hoặc nhún cầu vai lên tai khi kéo.",
            ],
        }

    # 12. SHOULDER PRESS / LATERAL RAISE
    if "press" in nl:
        return {
            "prepare": [
                f"Đưa {eq_vi} lên ngang tầm vai, giữ cổ tay thẳng trực tiếp phía trên khuỷu tay.",
                "Gồng chặt cơ bụng hoặc tựa chắc lưng vào ghế để giữ cột sống ổn định.",
            ],
            "execution": [
                "Đẩy mạnh tạ thẳng qua đầu cho đến khi hai cánh tay duỗi thẳng tự nhiên.",
                "Từ từ hạ tạ xuống có kiểm soát về ngang cằm và vai.",
            ],
            "breathing": [
                "Hít vào khi hạ tạ về vai, thở ra mạnh khi đẩy tạ qua đầu.",
                "Tránh: Ưỡn võng lưng dưới quá mức khi đẩy tạ.",
            ],
        }

    if "raise" in nl or "iron cross" in nl:
        return {
            "prepare": [
                f"Đứng hoặc ngồi thẳng lưng, tay cầm {eq_vi} với khuỷu tay hơi cong nhẹ 10–15 độ.",
                "Hạ thấp bả vai để hạn chế cơ cầu vai tham gia quá nhiều.",
            ],
            "execution": [
                "Nâng cánh tay lên đến tầm ngang vai theo đúng hướng mục tiêu của bài tập.",
                "Giữ ở đỉnh chuyển động trong nửa giây rồi hạ tạ xuống chậm rãi dưới sự kiểm soát.",
            ],
            "breathing": [
                "Thở ra khi nâng tạ lên ngang vai, hít vào khi hạ tạ xuống.",
                "Tránh: Đung đưa thân người lấy đà hoặc nhún cầu vai.",
            ],
        }

    # 13. SHRUG
    if "shrug" in nl:
        return {
            "prepare": [
                f"Giữ {eq_vi} với hai tay duỗi thẳng tự nhiên, đứng hoặc tựa lưng vững chãi.",
                "Mắt nhìn thẳng, thả lỏng khớp khuỷu tay.",
            ],
            "execution": [
                "Nhún thẳng hai vai lên cao hết mức về phía tai để co rút tối đa cơ cầu vai.",
                "Giữ và siết chặt ở điểm cao nhất trong 1–2 giây rồi hạ xuống từ từ.",
            ],
            "breathing": [
                "Thở ra khi nhún vai lên cao, hít vào khi hạ vai xuống.",
                "Tránh: Xoay tròn khớp vai hoặc gập khuỷu tay để kéo tạ.",
            ],
        }

    # 14. WRIST CURL / BICEPS CURL / TRICEPS / CALF / CORE
    if "wrist curl" in nl:
        return {
            "prepare": [
                f"Cầm {eq_vi}, cố định cẳng tay trên đùi hoặc mặt ghế, chỉ để phần cổ tay chuyển động.",
                "Giữ thân người ổn định, tập trung hoàn toàn vào nhóm cơ cẳng tay.",
            ],
            "execution": [
                "Từ từ hạ cổ tay xuống hết biên độ để kéo giãn cơ cẳng tay.",
                "Cuộn mạnh cổ tay lên cao hết cỡ và siết chặt cơ cẳng tay trong 1 giây.",
            ],
            "breathing": [
                "Thở ra khi cuộn cổ tay lên, hít vào khi hạ cổ tay xuống.",
                "Tránh: Nhấc cả cẳng tay hoặc dùng lực bắp tay.",
            ],
        }

    if "curl" in nl:
        return {
            "prepare": [
                f"Cầm {eq_vi} với tư thế chuẩn, cố định hai khuỷu tay bên sườn hoặc trên bệ đỡ tay.",
                "Giữ ngực mở, vai hạ thấp và thân người hoàn toàn ổn định.",
            ],
            "execution": [
                "Phát lực từ cơ bắp tay trước để cuốn tạ lên cao mà không di chuyển khuỷu tay.",
                "Siết chặt cơ tay trước ở đỉnh chuyển động trong 1 giây rồi từ từ hạ tạ xuống có kiểm soát.",
            ],
            "breathing": [
                "Thở ra khi cuốn tạ lên, hít vào khi hạ tạ xuống chậm rãi.",
                "Tránh: Đung đưa lưng lấy đà hoặc nhấc khuỷu tay lên theo tạ.",
            ],
        }

    if "tricep" in nl or "extension" in nl or "pushdown" in nl or "skullcrusher" in nl or "kickback" in nl:
        return {
            "prepare": [
                f"Cầm {eq_vi} chắc chắn, cố định vị trí hai khuỷu tay hướng thẳng và khép gọn.",
                "Gồng chặt cơ bụng để giữ thân người ổn định.",
            ],
            "execution": [
                "Chỉ cử động khớp khuỷu tay, phát lực từ cơ tay sau để duỗi thẳng hoàn toàn cánh tay.",
                "Siết mạnh cơ tay sau ở điểm duỗi thẳng trong 1 giây rồi từ từ gập khuỷu tay trả tạ có kiểm soát.",
            ],
            "breathing": [
                "Thở ra khi duỗi thẳng tay phát lực, hít vào khi gập khuỷu tay hồi tạ.",
                "Tránh: Xòe rộng khuỷu tay hoặc dùng sức nặng cơ thể đè tạ.",
            ],
        }

    if "calf" in nl:
        return {
            "prepare": [
                f"Vào vị trí với {eq_vi}, đặt phần ức bàn chân lên bục hoặc bàn đạp vững chắc.",
                "Giữ cột sống thẳng và khớp cổ chân linh hoạt.",
            ],
            "execution": [
                "Hạ thấp gót chân xuống hết biên độ để kéo giãn tối đa cơ bắp chân.",
                "Nhón mạnh lên cao hết cỡ trên phần ức bàn chân và giữ siết cơ bắp chân trong 1–2 giây ở đỉnh.",
            ],
            "breathing": [
                "Thở ra khi nhón gót lên cao, hít vào khi hạ gót chân xuống.",
                "Tránh: Nhún nhanh theo quán tính mà không giữ ở đỉnh và đáy.",
            ],
        }

    return {
        "prepare": [
            f"Vào tư thế chuẩn bị với {eq_vi}, cố định phần hông và gồng chặt nhóm cơ bụng.",
            "Giữ nhịp thở đều và tập trung cảm nhận nhóm cơ mục tiêu.",
        ],
        "execution": [
            "Thực hiện chuyển động có kiểm soát với biên độ đầy đủ bằng lực co rút của nhóm cơ chính.",
            "Giữ và siết chặt cơ ở điểm co rút tối đa trong 1 giây trước khi trở về vị trí bắt đầu.",
        ],
        "breathing": [
            "Thở ra khi phát lực co cơ, hít vào khi trở về vị trí ban đầu.",
            "Tránh: Dùng quán tính giật cục hoặc làm mất tư thế chuẩn của cột sống.",
        ],
    }


def main():
    exercises = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for ex in exercises:
        ex_id = str(ex["id"])
        ex["nameVi"] = EXACT_VI_NAMES.get(ex_id, ex["name"])
        ex["stepsVi"] = build_vi_steps(ex)

    DATA_PATH.write_text(json.dumps(exercises, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {len(exercises)} exercises with pure Vietnamese names and instructions.")


if __name__ == "__main__":
    main()
