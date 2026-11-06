import json
import re
import sys

print("[FROZEN] Translation batch scripts are preserved for historical reference. Direct execution blocked.")
sys.exit(0)

# Complete 1-to-1 Vietnamese translations for all 45 exercises in batch 1

vi_data = [
    # 0: id=1435 | Barbell Back Squat
    {
        "id": "1435",
        "stepsVi": {
            "prepare": [
                "Đặt thanh tạ đòn lên phần cơ cầu vai trên, nhấc tạ ra khỏi giá đỡ.",
                "Đứng hai chân rộng bằng vai, các ngón chân hơi xoay nhẹ ra ngoài."
            ],
            "execution": [
                "Hạ người xuống tư thế gánh tạ, giữ cột sống ở trạng thái tự nhiên.",
                "Hạ mông xuống cho đến khi đùi song song với mặt sàn hoặc sâu hơn một chút.",
                "Đạp mạnh gót chân xuống sàn để đẩy người đứng thẳng dậy về vị trí ban đầu.",
                "Lưu ý kỹ thuật: Mở rộng ngực",
                "Lưu ý kỹ thuật: Giữ thẳng lưng",
                "Lưu ý kỹ thuật: Phát lực từ gót chân"
            ],
            "breathing": [
                "Hít vào sâu khi hạ người xuống, thở ra mạnh khi đạp người đứng lên.",
                "Tránh: Đầu gối bị sụp vào trong",
                "Tránh: Cong vẹo hoặc gập lưng dưới"
            ]
        }
    },

    # 1: id=0025 | Barbell Bench Press
    {
        "id": "0025",
        "stepsVi": {
            "prepare": [
                "Nằm ngửa trên ghế phẳng sao cho tầm mắt nhìn thẳng dưới thanh tạ đòn, hai bàn chân đặt vững chắc trên mặt sàn.",
                "Nắm thanh tạ rộng hơn vai một chút và duỗi thẳng tay để nhấc tạ ra khỏi giá đỡ, giữ thanh tạ ngay phía trên ngực."
            ],
            "execution": [
                "Hạ thanh tạ đòn có kiểm soát xuống phần giữa ngực, giữ cổ tay thẳng hàng trên cẳng tay.",
                "Chạm nhẹ thanh tạ vào ngực, sau đó đẩy thanh tạ thẳng lên cho đến khi hai tay duỗi hoàn toàn.",
                "Khóa chắc khớp tay và cẩn thận đưa thanh tạ đòn trở lại giá đỡ khi hoàn thành hiệp tập.",
                "Lưu ý kỹ thuật: Đạp chặt hai chân xuống sàn",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng trục",
                "Lưu ý kỹ thuật: Chạm tạ nhẹ vào giữa ngực"
            ],
            "breathing": [
                "Hít vào khi hạ thanh tạ xuống ngực, thở ra dứt khoát khi đẩy tạ lên cao.",
                "Tránh: Để thanh tạ trượt lệch về phía cổ hoặc phía bụng",
                "Tránh: Mở rộng khuỷu tay vuông góc sang ngang bả vai"
            ]
        }
    },

    # 2: id=0028 | Barbell Clean And Press
    {
        "id": "0028",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng với hai chân rộng bằng hông đến ngang vai, đặt thanh tạ đòn ngay phía trên giữa bàn chân.",
                "Gập hông và chùng gối, hai tay nắm thanh tạ ở vị trí ngay sát mép ngoài hai chân, giữ lưng phẳng và ngực mở rộng."
            ],
            "execution": [
                "Đạp mạnh chân xuống sàn và nâng tạ lên, giữ thanh tạ lướt sát cẳng chân và đùi khi đứng lên.",
                "Phát lực bùng nổ duỗi thẳng hông, gối và cổ chân, đồng thời nhún cầu vai và nhanh chóng luồn người xuống dưới thanh tạ.",
                "Đón tạ trên phần trước của vai với hai khuỷu tay hướng ra trước, sau đó đứng thẳng người.",
                "Đẩy thanh tạ thẳng qua đầu cho đến khi hai tay khóa thẳng và tạ nằm ngay trên đỉnh vai.",
                "Hạ thanh tạ đòn trở lại phía trước vai, rồi hạ có kiểm soát xuống sàn tập.",
                "Lưu ý kỹ thuật: Giữ thanh tạ luôn sát cơ thể",
                "Lưu ý kỹ thuật: Đạp mạnh lực qua mặt sàn",
                "Lưu ý kỹ thuật: Đưa nhanh khuỷu tay ra trước khi đón tạ"
            ],
            "breathing": [
                "Hít sâu và gồng cứng cơ bụng trước khi kéo tạ từ sàn, thở ra khi đẩy tạ qua đầu và lấy lại nhịp thở trước lần lặp tiếp theo.",
                "Tránh: Bắt đầu kéo khi thanh tạ nằm quá xa phía trước bàn chân",
                "Tránh: Cong lưng dưới khi bắt đầu nhấc tạ từ mặt sàn"
            ]
        }
    },

    # 3: id=0030 | Barbell Close Grip Bench Press
    {
        "id": "0030",
        "stepsVi": {
            "prepare": [
                "Nằm ngửa trên ghế tập và nắm thanh tạ đòn với khoảng cách tay hẹp.",
                "Nhấc tạ ra khỏi giá đỡ và giữ thanh tạ ngay phía trên phần ngực dưới."
            ],
            "execution": [
                "Hạ thanh tạ xuống từ từ, giữ hai khuỷu tay khép sát vào hai bên sườn.",
                "Chạm nhẹ thanh tạ vào ngực rồi đẩy tạ trở lại vị trí ban đầu.",
                "Lặp lại động tác theo số lần quy định.",
                "Lưu ý kỹ thuật: Khép sát khuỷu tay vào thân người",
                "Lưu ý kỹ thuật: Nắm thanh tạ hẹp hơn chiều rộng vai",
                "Lưu ý kỹ thuật: Phát lực dồn vào cơ tay sau"
            ],
            "breathing": [
                "Thở ra khi đẩy tạ lên cao, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Nắm tay quá sát nhau hoặc quá rộng",
                "Tránh: Xòe khuỷu tay sang hai bên"
            ]
        }
    },

    # 4: id=0031 | Barbell Curl
    {
        "id": "0031",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng hông, hai tay cầm ngửa thanh tạ đòn ngang đùi.",
                "Kéo hai vai ra sau, gồng chặt thân người và giữ cố định hai khuỷu tay sát hai bên sườn."
            ],
            "execution": [
                "Gập khuỷu tay cuốn thanh tạ lên cho đến khi tạ đạt độ cao ngang vai.",
                "Dừng lại một nhịp ở điểm cao nhất và siết chặt cơ tay trước, không để khuỷu tay bị trượt ra trước.",
                "Hạ thanh tạ từ từ trở lại ngang đùi cho đến khi hai cánh tay duỗi thẳng hoàn toàn.",
                "Lưu ý kỹ thuật: Giữ khuỷu tay cố định sát hai bên sườn",
                "Lưu ý kỹ thuật: Phát lực co rút từ bắp tay trước",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng vững chắc"
            ],
            "breathing": [
                "Thở ra khi cuốn thanh tạ lên, hít vào sâu khi hạ tạ xuống có kiểm soát.",
                "Tránh: Vung vẩy đung đưa người để lấy đà nâng tạ",
                "Tránh: Đưa khuỷu tay trôi ra trước khi cuốn tạ lên"
            ]
        }
    },

    # 5: id=0033 | Barbell Decline Bench Press
    {
        "id": "0033",
        "stepsVi": {
            "prepare": [
                "Nằm ngửa trên ghế dốc xuống, móc chặt hai chân vào đệm cố định sao cho tầm mắt nhìn thẳng dưới thanh tạ.",
                "Nắm thanh tạ rộng hơn vai một chút và ghì chặt hai bả vai tựa sát vào mặt ghế."
            ],
            "execution": [
                "Nhấc tạ ra khỏi giá đỡ và giữ thanh tạ ngay phía trên ngực dưới với cổ tay thẳng và khớp khuỷu tay cố định.",
                "Hạ thanh tạ có kiểm soát xuống vùng ngực dưới hoặc xương ức dưới, giữ hai khuỷu tay mở một góc khoảng 45 độ so với thân người.",
                "Đẩy mạnh thanh tạ thẳng lên cho đến khi hai tay duỗi thẳng và thanh tạ trở về vị trí ngay trên ngực dưới.",
                "Lặp lại từng lần tập theo đúng quỹ đạo chuyển động ổn định và có kiểm soát.",
                "Lưu ý kỹ thuật: Ghì chặt bả vai tựa vào ghế",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng hàng trên cẳng tay",
                "Lưu ý kỹ thuật: Hạ thanh tạ trúng vào phần ngực dưới"
            ],
            "breathing": [
                "Hít vào khi hạ thanh tạ xuống ngực, thở ra khi đẩy tạ thẳng lên cao.",
                "Tránh: Thả rơi thanh tạ đập nảy trên lồng ngực",
                "Tránh: Mở bung khuỷu tay vuông góc sang hai bên"
            ]
        }
    },

    # 6: id=0038 | Barbell Drag Curl
    {
        "id": "0038",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng hông, hai tay cầm ngửa thanh tạ đòn đặt ngang đùi.",
                "Kéo nhẹ hai vai ra sau và giữ khuỷu tay hơi lùi về phía sau thân người."
            ],
            "execution": [
                "Cuốn thanh tạ lên bằng cách kéo trượt sát dọc theo mặt trước cơ thể đồng thời kéo khuỷu tay ra sau.",
                "Nâng tạ cho đến khi thanh tạ chạm vùng bụng trên hoặc ngực dưới mà không để tạ rời xa người.",
                "Hạ thanh tạ từ từ trượt sát dọc theo đường cũ cho đến khi hai tay duỗi thẳng hoàn toàn.",
                "Lưu ý kỹ thuật: Giữ thanh tạ luôn trượt sát người",
                "Lưu ý kỹ thuật: Kéo khuỷu tay sâu về phía sau",
                "Lưu ý kỹ thuật: Giữ ngực ưỡn cao và lưng thẳng"
            ],
            "breathing": [
                "Hít vào ở vị trí dưới cùng, thở ra khi kéo trượt thanh tạ lên, và hít vào sâu khi hạ tạ xuống.",
                "Tránh: Để thanh tạ văng ra xa phía trước cơ thể",
                "Tránh: Bẻ ngửa cổ tay ra sau khi nâng tạ lên"
            ]
        }
    },

    # 7: id=0041 | Barbell Front Raise
    {
        "id": "0041",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng hông, hai tay cầm úp thanh tạ đòn đặt ngang phía trước đùi.",
                "Gồng chắc cơ bụng và giữ hai khớp khuỷu tay hơi chùng nhẹ tự nhiên."
            ],
            "execution": [
                "Nâng thanh tạ đòn thẳng ra phía trước cho đến khi tạ đạt độ cao ngang bả vai.",
                "Dừng lại một nhịp ở điểm cao nhất mà không nhún bả vai lên.",
                "Hạ thanh tạ trở lại ngang đùi một cách chậm rãi có kiểm soát.",
                "Ổn định lại tư thế đứng vững chắc và tiếp tục thực hiện động tác.",
                "Lưu ý kỹ thuật: Nâng tạ lên ngang tầm vai",
                "Lưu ý kỹ thuật: Khóa chặt lồng ngực không ưỡn quá đà",
                "Lưu ý kỹ thuật: Chủ động dẫn dắt lực nâng từ bàn tay"
            ],
            "breathing": [
                "Thở ra khi nâng thanh tạ lên trước, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Ngả người ra phía sau để lấy đà nâng tạ",
                "Tránh: Dùng lực hông để đung đưa hất thanh tạ lên"
            ]
        }
    },

    # 8: id=0042 | Barbell Front Squat
    {
        "id": "0042",
        "stepsVi": {
            "prepare": [
                "Đặt thanh tạ đòn ngang xương quai xanh ở phía trước vai, nâng cao hai khuỷu tay hướng về phía trước.",
                "Đứng hai chân rộng bằng vai, mũi bàn chân hơi hướng nhẹ ra ngoài."
            ],
            "execution": [
                "Hạ người xuống tư thế gánh tạ, giữ thân người luôn dựng thẳng đứng.",
                "Hạ hông xuống cho đến khi đùi song song với mặt sàn.",
                "Đạp mạnh hai gót chân xuống sàn để đẩy người đứng thẳng dậy.",
                "Lưu ý kỹ thuật: Luôn nâng cao hai khuỷu tay",
                "Lưu ý kỹ thuật: Giữ thân trên dựng thẳng đứng",
                "Lưu ý kỹ thuật: Ghì chặt hai gót chân xuống sàn"
            ],
            "breathing": [
                "Hít vào sâu khi hạ người xuống, thở ra dứt khoát khi đứng thẳng lên.",
                "Tránh: Để hai khuỷu tay bị sà chúi xuống",
                "Tránh: Gù cong lưng trên hoặc lưng dưới"
            ]
        }
    },

    # 9: id=0047 | Barbell Incline Bench Press
    {
        "id": "0047",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế dốc lên một góc vừa phải và nằm ngửa tựa lưng, tầm mắt nhìn thẳng dưới thanh tạ, hai bàn chân đặt phẳng trên sàn.",
                "Nắm thanh tạ rộng hơn vai một chút với cổ tay thẳng, siết và hạ hai bả vai áp sát xuống mặt ghế."
            ],
            "execution": [
                "Nhấc tạ ra khỏi giá đỡ và giữ thanh tạ ngay phía trên ngực trên với hai tay duỗi thẳng.",
                "Hạ thanh tạ đòn có kiểm soát xuống phần ngực trên, giữ hai khuỷu tay hơi khép vào trong so với vai.",
                "Đẩy thanh tạ lên cao cho đến khi hai tay thẳng trở lại, giữ quỹ đạo tạ hướng về phía trên vai.",
                "Khóa chắc khớp tay và cẩn thận đưa thanh tạ trở lại giá đỡ sau lần nâng cuối cùng.",
                "Lưu ý kỹ thuật: Đạp chặt hai bàn chân xuống sàn",
                "Lưu ý kỹ thuật: Giữ lồng ngực luôn ưỡn cao",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng hàng trên khuỷu tay"
            ],
            "breathing": [
                "Hít vào khi hạ thanh tạ xuống ngực, thở ra khi đẩy tạ lên cao.",
                "Tránh: Xòe ngang hai khuỷu tay vuông góc với vai",
                "Tránh: Thả rơi thanh tạ đập nảy trên lồng ngực"
            ]
        }
    },

    # 10: id=0054 | Barbell Lunge
    {
        "id": "0054",
        "stepsVi": {
            "prepare": [
                "Đặt thanh tạ đòn ngang phần lưng trên và đứng thẳng với hai chân rộng bằng hông.",
                "Gồng chắc cơ bụng và chủ động bước dài một chân về phía trước có kiểm soát."
            ],
            "execution": [
                "Hạ thấp trọng tâm cơ thể cho đến khi cả hai gối đều gập lại và đầu gối chân sau áp sát mặt sàn.",
                "Giữ toàn bộ bàn chân trước áp phẳng xuống sàn và thân người dựng thẳng ở vị trí thấp nhất.",
                "Đạp mạnh qua bàn chân trước để đứng thẳng dậy và thu hai chân về lại vị trí ban đầu.",
                "Lặp lại tương tự với chân còn lại, đổi chân luân phiên qua từng lần tập.",
                "Lưu ý kỹ thuật: Luôn giữ thẳng lưng và ngực ưỡn",
                "Lưu ý kỹ thuật: Giữ chặt gót chân trước không bị nhấc lên",
                "Lưu ý kỹ thuật: Đầu gối chân trước hướng theo mũi chân"
            ],
            "breathing": [
                "Hít vào khi bước chân ra trước và hạ thấp người, thở ra khi đạp chân đứng thẳng dậy.",
                "Tránh: Bước bước chân quá ngắn khiến đầu gối trước lao quá xa khỏi mũi chân.",
                "Tránh: Đổ người chồm về phía trước khi hạ thấp trọng tâm."
            ]
        }
    },

    # 11: id=0072 | Barbell Prone Incline Curl
    {
        "id": "0072",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế nghiêng dốc lên và nằm sấp úp ngực vào đệm tựa, hai bàn chân đặt vững trên mặt sàn.",
                "Hai tay cầm ngửa thanh tạ đòn với khoảng cách rộng bằng vai, để hai cánh tay buông thõng tự nhiên."
            ],
            "execution": [
                "Áp chặt thân người vào đệm ghế và giữ cố định hai cánh tay trên.",
                "Gập khuỷu tay cuốn thanh tạ lên cho đến khi tạ đạt độ cao gần sát trước vai.",
                "Siết chặt cơ tay trước ở điểm cao nhất trong một nhịp mà không nhổm ngực rời khỏi ghế.",
                "Hạ thanh tạ đòn từ từ có kiểm soát cho đến khi hai tay duỗi thẳng trở lại hoàn toàn.",
                "Lưu ý kỹ thuật: Cố định chặt hai khuỷu tay",
                "Lưu ý kỹ thuật: Dùng cơ tay trước cuốn tạ, không văng đà",
                "Lưu ý kỹ thuật: Giữ ngực luôn áp sát vào đệm ghế"
            ],
            "breathing": [
                "Hít vào ở vị trí dưới cùng, thở ra khi cuốn tạ lên, và hít vào sâu khi hạ tạ xuống.",
                "Tránh: Nhấc ngực rời khỏi ghế để mượn lực nâng thanh tạ lên",
                "Tránh: Để hai khuỷu tay trượt đẩy ra trước trong lúc cuốn tạ"
            ]
        }
    },

    # 12: id=0075 | Barbell Rear Delt Raise
    {
        "id": "0075",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người, hai tay cầm úp thanh tạ đòn với khoảng cách rộng bằng vai.",
                "Hơi chùng nhẹ hai gối và gập người từ khớp hông cho đến khi thân trên gần song song với mặt sàn."
            ],
            "execution": [
                "Để thanh tạ buông thẳng tự nhiên dưới ngực với hai tay thẳng và cổ giữ ở trạng thái tự nhiên.",
                "Nâng thanh tạ sang ngang và lên cao bằng cách mở rộng hai cánh tay sang hai bên cho đến ngang tầm vai.",
                "Dừng lại một nhịp ở đỉnh động tác trong khi giữ thân người hoàn toàn bất động.",
                "Hạ thanh tạ có kiểm soát trở lại vị trí ban đầu.",
                "Lưu ý kỹ thuật: Gập từ khớp hông, không gù lưng",
                "Lưu ý kỹ thuật: Dẫn dắt chuyển động bằng khuỷu tay",
                "Lưu ý kỹ thuật: Giữ cổ thẳng hàng tự nhiên với cột sống"
            ],
            "breathing": [
                "Hít vào khi hạ tạ và ổn định tư thế gập hông, thở ra khi dang nâng thanh tạ sang hai bên.",
                "Tránh: Cong gập phần lưng dưới khi cúi người về trước",
                "Tránh: Đung đưa thân trên để giật thanh tạ lên cao"
            ]
        }
    },

    # 13: id=0082 | Barbell Reverse Wrist Curl
    {
        "id": "0082",
        "stepsVi": {
            "prepare": [
                "Ngồi trên ghế tập và hai tay nắm úp thanh tạ đòn.",
                "Đặt cẳng tay tựa lên hai đùi sao cho hai cổ tay nhô hẳn ra ngoài mép đầu gối."
            ],
            "execution": [
                "Bắt đầu ở tư thế hai cổ tay thả gập xuống dưới.",
                "Từ từ cuốn hai cổ tay lên phía trên để nâng thanh tạ đòn lên.",
                "Hạ thanh tạ từ từ có kiểm soát trở lại vị trí bắt đầu.",
                "Lưu ý kỹ thuật: Giữ cẳng tay cố định áp chặt trên đùi",
                "Lưu ý kỹ thuật: Thực hiện chuyển động chậm và có kiểm soát",
                "Lưu ý kỹ thuật: Chỉ vận động khớp cổ tay"
            ],
            "breathing": [
                "Thở ra khi cuốn cổ tay nâng thanh tạ lên, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Dùng mức tạ quá nặng",
                "Tránh: Vận lực từ khuỷu tay hoặc bả vai để nhấc tạ"
            ]
        }
    },

    # 14: id=drv-barbell-seated-behind-head-military-press | Barbell Seated Behind-The-Neck Press
    {
        "id": "drv-barbell-seated-behind-head-military-press",
        "stepsVi": {
            "prepare": [
                "Ngồi trên ghế tập có đệm tựa lưng, hai tay nắm thanh tạ đòn rộng hơn vai.",
                "Nhấc thanh tạ ra khỏi giá đỡ và giữ ổn định ở phía trên đỉnh đầu."
            ],
            "execution": [
                "Hạ thanh tạ đòn xuống phía sau đầu cho đến khi ngang tầm tai.",
                "Đẩy thanh tạ thẳng ngược lên trở lại vị trí ban đầu.",
                "Lặp lại theo số lần mong muốn và luôn siết chặt cơ bụng.",
                "Lưu ý kỹ thuật: Giữ lưng luôn dựng thẳng đứng",
                "Lưu ý kỹ thuật: Không ưỡn cong quá mức phần lưng dưới",
                "Lưu ý kỹ thuật: Hạ thanh tạ chậm rãi có kiểm soát"
            ],
            "breathing": [
                "Thở ra khi đẩy thanh tạ lên cao, hít vào khi hạ tạ xuống sau đầu.",
                "Tránh: Xòe khuỷu tay quá mức về phía sau",
                "Tránh: Ưỡn võng phần lưng dưới"
            ]
        }
    },

    # 15: id=0095 | Barbell Shrug
    {
        "id": "0095",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng hông đến ngang vai, hai tay cầm úp thanh tạ đòn đặt trước đùi.",
                "Thả thẳng hai cánh tay, gồng chặt thân người và giữ lồng ngực mở rộng."
            ],
            "execution": [
                "Nhún thẳng hai bả vai lên phía tai mà không co gập khuỷu tay hay ngả người ra sau.",
                "Dừng lại một nhịp ở điểm cao nhất và siết chặt cơ cầu vai.",
                "Hạ bả vai từ từ có kiểm soát trở về vị trí ban đầu.",
                "Lưu ý kỹ thuật: Nhún vai thẳng đứng lên trên",
                "Lưu ý kỹ thuật: Giữ hai cánh tay luôn duỗi thẳng",
                "Lưu ý kỹ thuật: Ngực luôn ưỡn cao kiêu hãnh"
            ],
            "breathing": [
                "Hít sâu trước mỗi lần tập, thở ra khi nhún vai lên cao, và hít vào khi hạ vai xuống.",
                "Tránh: Gập khuỷu tay để giật kéo thanh tạ lên.",
                "Tránh: Xoay tròn bả vai ra trước hoặc ra sau ở điểm cao nhất."
            ]
        }
    },

    # 16: id=0104 | Barbell Standing Back Wrist Curl
    {
        "id": "0104",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng hông, hai tay nắm thanh tạ đòn ở phía sau mông.",
                "Để thanh tạ tựa trên các ngón tay sao cho các đốt ngón tay hướng xuống sàn và lòng bàn tay hướng ra phía sau."
            ],
            "execution": [
                "Giữ khuỷu tay áp sát thân người và duỗi cổ tay để thanh tạ từ từ trượt xuống đầu các ngón tay.",
                "Cuốn mạnh cổ tay lên phía trên để lăn thanh tạ vào lại lòng bàn tay và nâng tạ lên cao nhất có thể.",
                "Dừng lại một nhịp ở đỉnh, sau đó hạ thanh tạ có kiểm soát trở lại vị trí ban đầu.",
                "Lưu ý kỹ thuật: Chỉ vận động khớp cổ tay",
                "Lưu ý kỹ thuật: Giữ cố định khuỷu tay ở phía sau",
                "Lưu ý kỹ thuật: Đi hết biên độ chuyển động của cổ tay"
            ],
            "breathing": [
                "Hít vào khi hạ thanh tạ xuống đầu ngón tay, thở ra khi cuốn gập cổ tay lên.",
                "Tránh: Dùng vai hoặc thân người đung đưa vung tạ",
                "Tránh: Gập khuỷu tay để nhấc thanh tạ lên"
            ]
        }
    },

    # 17: id=0116 | Barbell Straight Leg Deadlift
    {
        "id": "0116",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng hông, hai tay cầm thẳng thanh tạ đòn ở phía trước đùi.",
                "Hơi chùng nhẹ hai khớp gối tự nhiên và gồng chắc toàn bộ vùng bụng."
            ],
            "execution": [
                "Đẩy hông ra sau và hạ thanh tạ lướt sát chân trong khi giữ lưng phẳng và chân gần như thẳng.",
                "Hạ tạ xuống đến giữa cẳng chân hoặc khi cảm nhận cơ đùi sau được kéo căng tối đa mà lưng vẫn thẳng.",
                "Đẩy mạnh hông về phía trước và đứng thẳng dậy, giữ thanh tạ luôn lướt sát chân trong suốt hành trình đi lên.",
                "Kết thúc với hông duỗi thẳng hoàn toàn và hai bả vai thẳng hàng trên hông.",
                "Lưu ý kỹ thuật: Đẩy hông ra sau, không hạ thấp hông xuống",
                "Lưu ý kỹ thuật: Giữ thanh tạ luôn sát chân",
                "Lưu ý kỹ thuật: Gối chùng nhẹ, giữ lưng phẳng"
            ],
            "breathing": [
                "Hít sâu và gồng bụng trước khi gập hông cúi xuống, thở ra khi đẩy hông tới trước để đứng thẳng dậy.",
                "Tránh: Co gập đầu gối thành động tác ngồi gánh tạ khi hạ thanh tạ",
                "Tránh: Để thanh tạ trôi xa khỏi cẳng chân"
            ]
        }
    },

    # 18: id=0027 | Barbell Underhand Bent-Over Row
    {
        "id": "0027",
        "stepsVi": {
            "prepare": [
                "Đứng hai chân rộng bằng hông, đặt thanh tạ đòn trên mặt sàn.",
                "Gập người từ khớp hông, giữ lưng thẳng và nắm thanh tạ với tư thế lòng bàn tay ngửa."
            ],
            "execution": [
                "Để thanh tạ buông thẳng tự nhiên dưới bả vai với hai cánh tay duỗi.",
                "Kéo chèo thanh tạ về phía thân người, giữ hai khuỷu tay khép sát vào hai bên sườn.",
                "Hạ thanh tạ đòn từ từ có kiểm soát trở lại vị trí ban đầu.",
                "Lưu ý kỹ thuật: Giữ lưng luôn thẳng phẳng",
                "Lưu ý kỹ thuật: Dẫn dắt lực kéo bằng khuỷu tay",
                "Lưu ý kỹ thuật: Siết chặt hai bả vai lại với nhau"
            ],
            "breathing": [
                "Thở ra khi kéo chèo tạ lên, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Cong gù phần lưng dưới",
                "Tránh: Xòe khuỷu tay quá rộng sang hai bên"
            ]
        }
    },

    # 19: id=0123 | Barbell Wide-Grip Upright Row
    {
        "id": "0123",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng vai.",
                "Hai tay cầm úp thanh tạ đòn với khoảng cách rộng hơn vai."
            ],
            "execution": [
                "Để thanh tạ đòn tựa ở phía trước đùi.",
                "Nâng thanh tạ thẳng đứng lên phía ngực, mở rộng hai khuỷu tay sang hai bên.",
                "Hạ thanh tạ từ từ trở lại vị trí ban đầu.",
                "Lưu ý kỹ thuật: Dẫn dắt chuyển động bằng khuỷu tay",
                "Lưu ý kỹ thuật: Giữ thanh tạ luôn di chuyển sát thân người",
                "Lưu ý kỹ thuật: Dừng tạ lại ở ngang tầm ngực trên"
            ],
            "breathing": [
                "Thở ra khi nâng thanh tạ lên, hít vào khi hạ tạ xuống.",
                "Tránh: Nhún bả vai quá mức lên tai",
                "Tránh: Dùng đà vung thân người để nâng tạ"
            ]
        }
    },

    # 20: id=0248 | Barbell Chest-Supported Lying Row (Seal Row)
    {
        "id": "0248",
        "stepsVi": {
            "prepare": [
                "Đặt thanh tạ đòn trên sàn dưới gầm ghế phẳng và nằm sấp úp ngực áp vào đệm ghế, hai tay buông thẳng xuống.",
                "Đặt chân vững trên sàn, gồng chặt thân người và hai tay cầm úp thanh tạ với khoảng cách rộng hơn vai một chút."
            ],
            "execution": [
                "Nhấc thanh tạ nhấc rời khỏi mặt sàn, treo thẳng dưới vai và giữ cổ ở trạng thái tự nhiên.",
                "Kéo thanh tạ lên sát mặt dưới của ghế hoặc phần ngực dưới bằng cách kéo mạnh hai khuỷu tay ra sau.",
                "Dừng lại một nhịp ở điểm cao nhất và siết chặt hai bả vai lại với nhau.",
                "Hạ thanh tạ từ từ có kiểm soát cho đến khi hai tay duỗi thẳng và thanh tạ lơ lửng ngay phía trên mặt sàn.",
                "Lưu ý kỹ thuật: Giữ ngực luôn áp chặt vào đệm ghế",
                "Lưu ý kỹ thuật: Kéo hai khuỷu tay mạnh về phía sau",
                "Lưu ý kỹ thuật: Ép chặt hai bả vai vào nhau"
            ],
            "breathing": [
                "Hít vào khi hạ thanh tạ xuống, thở ra khi kéo tạ lên sát ngực.",
                "Tránh: Nhấc ngực rời khỏi ghế để giật thanh tạ lên",
                "Tránh: Nhún bả vai lên sát tai"
            ]
        }
    },

    # 21: id=0562 | Landmine 180
    {
        "id": "0562",
        "stepsVi": {
            "prepare": [
                "Đứng hướng mặt về đầu tự do của thanh tạ đòn một đầu gắn sàn với hai chân rộng bằng vai, hai tay nắm chặt đầu thanh tạ phía trước ngực.",
                "Hơi chùng nhẹ hai gối, gồng cứng cơ bụng và giữ hai tay duỗi dài tự nhiên nhưng không khóa khớp."
            ],
            "execution": [
                "Xoay đồng thời vai và hông để hạ thanh tạ đòn sang một bên hông.",
                "Đạp lực từ bàn chân và xoay người quét thanh tạ theo hình vòng cung sang phía hông đối diện.",
                "Kiểm soát thanh tạ khi đổi hướng và tiếp tục xoay luân phiên hai bên với lồng ngực luôn hướng theo thanh tạ.",
                "Duy trì chuyển động nhịp nhàng và cân bằng giữa hai bên cho đến khi hoàn thành hiệp tập.",
                "Lưu ý kỹ thuật: Xoay hông và vai cùng một nhịp",
                "Lưu ý kỹ thuật: Gồng cứng toàn bộ vùng cơ bụng",
                "Lưu ý kỹ thuật: Vung thanh tạ theo một đường vòng cung mượt mà"
            ],
            "breathing": [
                "Hít vào khi thanh tạ hạ sang một bên, thở ra khi xoay tạ quét sang phía bên kia.",
                "Tránh: Chỉ dùng tay để xoay trong khi thân người đứng bất động",
                "Tránh: Để phần lưng dưới bị ưỡn võng trong khi di chuyển tạ"
            ]
        }
    },

    # 22: id=0553 | Military Press
    {
        "id": "0553",
        "stepsVi": {
            "prepare": [
                "Đứng hai chân rộng bằng hông và giữ thanh tạ đòn ở độ cao ngang vai.",
                "Nắm thanh tạ với khoảng cách hai tay ngay mép ngoài của vai."
            ],
            "execution": [
                "Gồng chắc cơ bụng và siết cứng cơ mông.",
                "Đẩy thanh tạ thẳng qua đầu cho đến khi hai cánh tay duỗi thẳng hoàn toàn.",
                "Hạ thanh tạ từ từ trở lại ngang bả vai.",
                "Lưu ý kỹ thuật: Luôn gồng cứng vùng cơ bụng",
                "Lưu ý kỹ thuật: Đẩy tạ theo một đường thẳng đứng",
                "Lưu ý kỹ thuật: Tránh ưỡn cong phần lưng dưới"
            ],
            "breathing": [
                "Thở ra khi đẩy tạ lên cao, hít vào khi hạ tạ xuống.",
                "Tránh: Ngả thân người ra sau quá mức",
                "Tránh: Thả rơi thanh tạ đập nảy trên bả vai"
            ]
        }
    },

    # 23: id=0301 | Decline Dumbbell Bench Press
    {
        "id": "0301",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế tập dốc xuống một góc 45 độ.",
                "Cố định hai chân vào đệm giữ, nằm ngửa tựa lưng và giữ hai quả tạ đơn phía trên ngực."
            ],
            "execution": [
                "Hạ hai quả tạ đơn xuống hai bên ngực.",
                "Dừng lại một nhịp ở vị trí thấp nhất.",
                "Đẩy tạ đơn thẳng lên trở lại vị trí ban đầu.",
                "Lưu ý kỹ thuật: Kiểm soát chặt chẽ pha hạ tạ",
                "Lưu ý kỹ thuật: Không mở xòe khuỷu tay sang hai bên",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng vững chắc"
            ],
            "breathing": [
                "Hít vào khi hạ hai quả tạ đơn xuống, thở ra khi đẩy tạ lên cao.",
                "Tránh: Hạ khuỷu tay xuống quá sâu",
                "Tránh: Đẩy lệch biên độ giữa hai bên tay"
            ]
        }
    },

    # 24: id=0302 | Decline Dumbbell Fly
    {
        "id": "0302",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế dốc xuống một góc 45 độ và móc chặt hai chân vào đệm giữ.",
                "Nằm ngửa trên ghế, hai tay vươn thẳng giữ tạ phía trên ngực với khuỷu tay hơi chùng nhẹ."
            ],
            "execution": [
                "Mở rộng hai tay hạ hai quả tạ đơn theo hình vòng cung sang hai bên.",
                "Dừng lại một nhịp ở vị trí thấp nhất để kéo căng cơ ngực.",
                "Khép hai quả tạ đơn về lại vị trí ban đầu theo đường vòng cung và siết chặt cơ ngực.",
                "Lưu ý kỹ thuật: Giữ khuỷu tay luôn hơi gập nhẹ cố định",
                "Lưu ý kỹ thuật: Chuyển động theo đường vòng cung rộng mở",
                "Lưu ý kỹ thuật: Không hạ tạ quá sâu làm kéo căng khớp vai quá mức"
            ],
            "breathing": [
                "Hít vào khi mở rộng hai tay sang bên, thở ra khi khép hai quả tạ lại gần nhau.",
                "Tránh: Duỗi thẳng đơ khớp khuỷu tay",
                "Tránh: Hạ hai quả tạ đơn xuống quá sâu"
            ]
        }
    },

    # 25: id=0361 | Dumbbell Alternating Shoulder Press
    {
        "id": "0361",
        "stepsVi": {
            "prepare": [
                "Cầm hai quả tạ đơn ngang tầm vai, lòng bàn tay hướng ra phía trước.",
                "Gồng chắc cơ bụng và đẩy một quả tạ đơn lên qua đầu cho đến khi cánh tay duỗi thẳng hoàn toàn."
            ],
            "execution": [
                "Hạ tạ về ngang vai đồng thời đẩy quả tạ đơn của tay đối diện lên qua đầu.",
                "Tiếp tục đổi luân phiên từng bên tay qua mỗi lần lặp lại.",
                "Duy trì tư thế thân người thẳng đứng và tránh ưỡn cong lưng.",
                "Lưu ý kỹ thuật: Không ưỡn võng lưng",
                "Lưu ý kỹ thuật: Gồng cứng toàn bộ cơ bụng",
                "Lưu ý kỹ thuật: Giữ khuỷu tay luôn thẳng hàng dưới cổ tay"
            ],
            "breathing": [
                "Thở ra khi đẩy tạ lên, hít vào khi hạ tạ xuống.",
                "Tránh: Nghiêng người vẹo sang một bên",
                "Tránh: Đẩy cả hai tay cùng một lúc"
            ]
        }
    },

    # 26: id=2137 | Dumbbell Arnold Press
    {
        "id": "2137",
        "stepsVi": {
            "prepare": [
                "Ngồi thẳng người trên ghế tập có tựa lưng và đặt hai bàn chân vững chắc trên sàn.",
                "Cầm hai quả tạ đơn trước vai với lòng bàn tay hướng vào người và khuỷu tay gập lại."
            ],
            "execution": [
                "Gồng chắc thân người và đẩy tạ đơn lên cao đồng thời xoay lòng bàn tay hướng ra ngoài.",
                "Kết thúc ở vị trí qua đầu với hai tay duỗi thẳng và lòng bàn tay hướng về phía trước.",
                "Hạ hai quả tạ đơn có kiểm soát đồng thời xoay lòng bàn tay quay trở lại hướng vào trong.",
                "Trở về tư thế ban đầu với hai quả tạ đơn ở trước vai và tiếp tục lặp lại.",
                "Lưu ý kỹ thuật: Đẩy tạ và xoay tay một cách mượt mà đồng thời",
                "Lưu ý kỹ thuật: Khóa chặt lồng ngực không ưỡn quá đà",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng hàng phía trên khuỷu tay"
            ],
            "breathing": [
                "Hít vào ở vị trí dưới cùng, thở ra khi đẩy xoay tạ qua đầu, sau đó hít vào khi hạ tạ xuống.",
                "Tránh: Ưỡn võng lưng dưới khi đẩy hai quả tạ đơn qua đầu",
                "Tránh: Mở xòe khuỷu tay vuông góc sang ngang ở vị trí dưới cùng"
            ]
        }
    },

    # 27: id=0364 | Dumbbell Behind-the-Back Wrist Curl
    {
        "id": "0364",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với một quả tạ đơn cầm sau lưng, cánh tay duỗi thẳng và lòng bàn tay hướng ra sau.",
                "Thả lỏng nhẹ để quả tạ đơn lăn xuống một chút trên các ngón tay."
            ],
            "execution": [
                "Gập cổ tay để cuốn quả tạ đơn lên cao.",
                "Siết chặt cơ cẳng tay ở đỉnh của động tác.",
                "Từ từ hạ quả tạ xuống trở lại vị trí ban đầu.",
                "Lưu ý kỹ thuật: Chỉ vận động duy nhất khớp cổ tay",
                "Lưu ý kỹ thuật: Không đung đưa vung cánh tay",
                "Lưu ý kỹ thuật: Gập hết biên độ chuyển động của cổ tay"
            ],
            "breathing": [
                "Thở ra khi cuốn cổ tay lên, hít vào khi hạ tạ xuống.",
                "Tránh: Dùng cả cánh tay thay vì khớp cổ tay",
                "Tránh: Chuyển động thiếu biên độ không đầy đủ"
            ]
        }
    },

    # 28: id=0293 | Dumbbell Bent-Over Row
    {
        "id": "0293",
        "stepsVi": {
            "prepare": [
                "Đứng hai chân rộng bằng vai, hai tay cầm hai quả tạ đơn.",
                "Gập người từ khớp hông, giữ lưng phẳng và ưỡn ngực."
            ],
            "execution": [
                "Để hai cánh tay buông thẳng tự nhiên xuống dưới, lòng bàn tay hướng vào nhau.",
                "Kéo hai quả tạ đơn lên hai bên sườn, giữ khuỷu tay khép sát thân người.",
                "Hạ tạ từ từ có kiểm soát trở về vị trí ban đầu.",
                "Lưu ý kỹ thuật: Giữ lưng luôn phẳng thẳng",
                "Lưu ý kỹ thuật: Dẫn dắt lực kéo bằng khuỷu tay",
                "Lưu ý kỹ thuật: Gồng chắc vùng cơ bụng"
            ],
            "breathing": [
                "Thở ra khi kéo tạ lên, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Cong gù phần lưng",
                "Tránh: Giật cục người để nâng tạ"
            ]
        }
    },

    # 29: id=0294 | Dumbbell Biceps Curl
    {
        "id": "0294",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với mỗi tay cầm một quả tạ đơn buông bên sườn, lòng bàn tay hướng ra phía trước.",
                "Gồng chắc thân người và giữ cố định hai khuỷu tay sát hai bên mạn sườn."
            ],
            "execution": [
                "Cuốn cả hai quả tạ đơn lên phía vai mà không để cánh tay trên đung đưa ra trước.",
                "Dừng lại một nhịp ở điểm cao nhất và siết chặt cơ tay trước.",
                "Hạ hai quả tạ đơn xuống có kiểm soát cho đến khi hai cánh tay duỗi thẳng hoàn toàn.",
                "Lưu ý kỹ thuật: Giữ cố định khuỷu tay sát sườn",
                "Lưu ý kỹ thuật: Dùng cơ tay trước cuốn tạ, không vung người lấy đà",
                "Lưu ý kỹ thuật: Siết chặt cơ bắp ở điểm cao nhất"
            ],
            "breathing": [
                "Thở ra khi cuốn hai quả tạ đơn lên, hít vào khi hạ tạ xuống.",
                "Tránh: Vung lắc thân người để lấy đà cuốn tạ",
                "Tránh: Đưa khuỷu tay trôi ra trước khi tạ nâng lên"
            ]
        }
    },

    # 30: id=0296 | Dumbbell Close-Grip Press
    {
        "id": "0296",
        "stepsVi": {
            "prepare": [
                "Nằm ngửa trên ghế tập phẳng với mỗi tay cầm một quả tạ đơn.",
                "Giữ hai quả tạ đơn chạm sát nhau phía trên ngực, lòng bàn tay hướng vào nhau."
            ],
            "execution": [
                "Hạ hai quả tạ đơn xuống sát xương ức, giữ hai khuỷu tay khép sát thân người.",
                "Dừng lại một nhịp khi khuỷu tay gập thành một góc 90 độ.",
                "Đẩy hai quả tạ đơn thẳng lên bằng cách duỗi thẳng hai cánh tay.",
                "Lưu ý kỹ thuật: Luôn khép sát khuỷu tay vào sườn",
                "Lưu ý kỹ thuật: Giữ hai quả tạ đơn chạm sát vào nhau",
                "Lưu ý kỹ thuật: Phát lực đẩy qua lòng bàn tay"
            ],
            "breathing": [
                "Hít vào khi hạ hai quả tạ đơn xuống, thở ra khi đẩy tạ lên cao.",
                "Tránh: Mở xòe khuỷu tay sang hai bên",
                "Tránh: Để hai quả tạ đơn rời xa nhau"
            ]
        }
    },

    # 31: id=0297 | Dumbbell Concentration Curl
    {
        "id": "0297",
        "stepsVi": {
            "prepare": [
                "Ngồi trên ghế tập với hai bàn chân đặt phẳng và hai đầu gối mở rộng, một tay cầm một quả tạ đơn.",
                "Hơi rướn người về phía trước và tỳ chắc mặt sau của cánh tay trên vào mặt trong đùi cùng bên, gần sát đầu gối."
            ],
            "execution": [
                "Để cánh tay buông thẳng tự nhiên xuống dưới với lòng bàn tay ngửa lên và cổ tay thẳng.",
                "Cuốn quả tạ đơn lên phía bả vai cùng bên mà không di chuyển cánh tay trên.",
                "Siết chặt cơ tay trước ở điểm cao nhất khi cẳng tay gần như dựng thẳng đứng.",
                "Hạ quả tạ đơn từ từ cho đến khi khớp khuỷu duỗi thẳng hoàn toàn, sau đó lặp lại và đổi sang bên tay kia.",
                "Lưu ý kỹ thuật: Giữ khuỷu tay tỳ chặt cố định vào đùi",
                "Lưu ý kỹ thuật: Chỉ vận động co gập duy nhất khớp khuỷu tay",
                "Lưu ý kỹ thuật: Giữ lòng bàn tay luôn ngửa lên trên"
            ],
            "breathing": [
                "Hít vào khi hạ quả tạ đơn xuống, thở ra dứt khoát khi cuốn tạ lên.",
                "Tránh: Nhấc khuỷu tay rời khỏi đùi trong khi cuốn tạ",
                "Tránh: Đung đưa thân trên để mượn đà nâng quả tạ đơn"
            ]
        }
    },

    # 32: id=0298 | Dumbbell Cross Body Hammer Curl
    {
        "id": "0298",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với mỗi tay cầm một quả tạ đơn buông bên sườn, lòng bàn tay hướng vào trong.",
                "Gồng chắc thân người và giữ cố định hai khuỷu tay sát hai bên sườn."
            ],
            "execution": [
                "Cuốn một quả tạ đơn chéo qua thân người hướng về phía vai đối diện mà không vung đà.",
                "Dừng lại một nhịp ở ngang tầm vai với cổ tay thẳng và lòng bàn tay hướng vào trong.",
                "Hạ quả tạ đơn từ từ có kiểm soát trở lại bên sườn.",
                "Lặp lại tương tự với cánh tay còn lại, đổi bên luân phiên.",
                "Lưu ý kỹ thuật: Giữ khuỷu tay luôn khép sát người",
                "Lưu ý kỹ thuật: Cuốn chéo qua thân người, không cuốn thẳng lên",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng tự nhiên"
            ],
            "breathing": [
                "Thở ra khi cuốn tạ chéo qua thân người, hít vào khi hạ tạ xuống trở lại bên sườn.",
                "Tránh: Đung đưa thân người hoặc ngửa ra sau để nâng tạ đơn",
                "Tránh: Để khuỷu tay trượt đẩy ra xa khỏi mạn sườn"
            ]
        }
    },

    # 33: id=0300 | Dumbbell Deadlift
    {
        "id": "0300",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với hai chân rộng bằng hông đến ngang vai, hai tay cầm hai quả tạ đơn đặt phía trước đùi.",
                "Gồng chắc vùng cơ bụng, kéo hai vai ra sau và giữ hai cánh tay duỗi thẳng."
            ],
            "execution": [
                "Đẩy hông ra sau và hơi chùng nhẹ gối trong khi trượt hai quả tạ đơn sát dọc theo chân.",
                "Hạ tạ xuống ngang giữa cẳng chân hoặc ngay dưới gối trong khi luôn giữ lưng phẳng.",
                "Đạp mạnh chân xuống sàn và đẩy hông về phía trước để đứng thẳng dậy, đưa hai quả tạ về lại ngang đùi.",
                "Kết thúc ở tư thế đứng thẳng với hông và gối duỗi thẳng, sau đó lặp lại động tác gập hông.",
                "Lưu ý kỹ thuật: Chủ động đẩy hông ra sau trước tiên",
                "Lưu ý kỹ thuật: Giữ hai quả tạ đơn luôn sát chân",
                "Lưu ý kỹ thuật: Luôn mở rộng ngực kiêu hãnh"
            ],
            "breathing": [
                "Hít vào sâu khi hạ hai quả tạ đơn có kiểm soát, thở ra khi đạp mạnh chân đứng thẳng dậy.",
                "Tránh: Cong gập phần lưng dưới khi hạ tạ đơn xuống",
                "Tránh: Để hai quả tạ trôi ra quá xa phía trước chân"
            ]
        }
    },

    # 34: id=0308 | Dumbbell Fly
    {
        "id": "0308",
        "stepsVi": {
            "prepare": [
                "Nằm ngửa trên ghế tập phẳng với mỗi tay cầm một quả tạ đơn, hai bàn chân đặt vững trên sàn.",
                "Giữ hai quả tạ đơn phía trên ngực với lòng bàn tay hướng vào nhau và hơi chùng nhẹ hai khuỷu tay."
            ],
            "execution": [
                "Mở rộng hai tay hạ tạ theo hình vòng cung sang hai bên cho đến khi khuỷu tay ngang tầm ngực.",
                "Dừng lại một nhịp ở vị trí thấp nhất trong khi vẫn giữ nguyên góc cong nhẹ của khuỷu tay.",
                "Siết chặt cơ ngực và đưa hai quả tạ đơn khép lại với nhau phía trên ngực theo đúng quỹ đạo vòng cung đó.",
                "Lưu ý kỹ thuật: Tưởng tượng động tác như đang ôm một thân cây to",
                "Lưu ý kỹ thuật: Giữ khuỷu tay hơi chùng nhẹ cố định",
                "Lưu ý kỹ thuật: Mở tạ xuống chậm rãi có kiểm soát"
            ],
            "breathing": [
                "Hít vào khi mở rộng hai quả tạ sang hai bên, thở ra khi khép hai quả tạ lại phía trên ngực.",
                "Tránh: Co gập và duỗi khuỷu tay biến động tác thành bài đẩy ngực",
                "Tránh: Hạ hai quả tạ đơn xuống quá sâu dưới mức ngực"
            ]
        }
    },

    # 35: id=1277 | Dumbbell Fly On Exercise Ball
    {
        "id": "1277",
        "stepsVi": {
            "prepare": [
                "Ngồi trên bóng tập thể lực với mỗi tay cầm một quả tạ đơn đặt trên đùi.",
                "Bước chân dần về phía trước và lăn người xuống cho đến khi đầu, cổ và lưng trên tựa vững trên bóng, sau đó nâng hông lên sao cho thân người nằm ngang phẳng."
            ],
            "execution": [
                "Giữ hai quả tạ đơn phía trên ngực với lòng bàn tay hướng vào nhau và khuỷu tay hơi gập nhẹ.",
                "Mở rộng hai tay hạ tạ sang hai bên theo hình vòng cung trong khi giữ nguyên góc gập nhẹ ở khuỷu tay.",
                "Dừng lại khi hai cánh tay trên gần thẳng hàng với thân người và cơ ngực được kéo căng vừa phải.",
                "Khép hai quả tạ đơn về lại phía trên ngực theo đúng đường vòng cung và siết chặt cơ ngực ở điểm cao nhất.",
                "Lưu ý kỹ thuật: Luôn nâng cao hông giữ thân người thẳng",
                "Lưu ý kỹ thuật: Giữ khuỷu tay luôn hơi gập nhẹ",
                "Lưu ý kỹ thuật: Mở rộng sang hai bên, không hạ tạ quá sâu"
            ],
            "breathing": [
                "Hít vào khi mở hai quả tạ đơn sang hai bên, thở ra khi khép hai tạ lại phía trên ngực.",
                "Tránh: Để phần hông bị chùng võng xuống thấp hơn thân người",
                "Tránh: Gập khuỷu tay quá nhiều biến động tác ép ngực thành động tác đẩy tạ"
            ]
        }
    },

    # 36: id=0310 | Dumbbell Front Raise
    {
        "id": "0310",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng người với mỗi tay cầm một quả tạ đơn đặt trước đùi, lòng bàn tay hướng vào chân.",
                "Gồng chắc thân người và giữ khớp khuỷu tay hơi chùng nhẹ tự nhiên."
            ],
            "execution": [
                "Nâng cả hai quả tạ đơn thẳng ra phía trước cho đến khi hai bàn tay ngang tầm vai.",
                "Dừng lại một nhịp ở điểm cao nhất mà không nhún bả vai lên.",
                "Hạ hai quả tạ đơn trở lại trước đùi một cách chậm rãi có kiểm soát.",
                "Lặp lại động tác từ tư thế đứng yên thẳng người.",
                "Lưu ý kỹ thuật: Nâng tạ lên ngang tầm vai",
                "Lưu ý kỹ thuật: Khóa chặt lồng ngực không ưỡn người",
                "Lưu ý kỹ thuật: Dẫn dắt lực nâng từ bàn tay"
            ],
            "breathing": [
                "Thở ra khi nâng hai quả tạ đơn lên trước, hít vào khi hạ tạ xuống có kiểm soát.",
                "Tránh: Vung lắc hông hoặc thân người để giật hai quả tạ đơn lên.",
                "Tránh: Nâng tạ lên cao vượt quá tầm bả vai."
            ]
        }
    },

    # 37: id=1760 | Dumbbell Goblet Squat
    {
        "id": "1760",
        "stepsVi": {
            "prepare": [
                "Đứng thẳng với hai chân rộng bằng vai, hai tay cùng ôm giữ một quả tạ đơn theo chiều dọc trước ngực.",
                "Gồng chắc vùng cơ bụng và giữ hai khuỷu tay hướng xuống dưới khép sát thân người."
            ],
            "execution": [
                "Đẩy hông ra sau và hạ thấp người xuống đồng thời gập gối, hạ cho đến khi hai đùi song song với sàn hoặc sâu hơn một chút.",
                "Giữ quả tạ đơn áp sát trước ngực, bàn chân áp phẳng trên sàn và đầu gối mở hướng theo mũi chân.",
                "Đạp mạnh toàn bộ bàn chân xuống sàn để đứng thẳng dậy cho đến khi hông và gối duỗi thẳng hoàn toàn.",
                "Ổn định lại tư thế đứng và tiếp tục thực hiện lần tập tiếp theo.",
                "Lưu ý kỹ thuật: Luôn mở rộng và ưỡn cao lồng ngực",
                "Lưu ý kỹ thuật: Giữ chặt hai gót chân áp sát sàn",
                "Lưu ý kỹ thuật: Hướng đầu gối di chuyển theo mũi bàn chân"
            ],
            "breathing": [
                "Hít vào sâu khi hạ người xuống tư thế gánh tạ, thở ra dứt khoát khi đứng thẳng dậy.",
                "Tránh: Để quả tạ đơn rời xa khỏi lồng ngực",
                "Tránh: Nhấc gót chân lên khỏi sàn ở vị trí thấp nhất"
            ]
        }
    },

    # 38: id=1330 | Dumbbell Chest-Supported Hammer Row
    {
        "id": "1330",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế dốc lên một góc 30 đến 45 độ và nằm sấp úp ngực vào ghế, hai tay cầm hai quả tạ đơn.",
                "Cầm tạ đơn với hai lòng bàn tay hướng vào nhau (cầm tạ kiểu búa)."
            ],
            "execution": [
                "Kéo hai quả tạ đơn lên hướng về phía hông, giữ khuỷu tay khép sát thân người.",
                "Dừng lại một nhịp và siết chặt các nhóm cơ lưng ở điểm cao nhất.",
                "Từ từ hạ tạ xuống một cách chậm rãi có kiểm soát.",
                "Lưu ý kỹ thuật: Giữ ngực luôn áp chặt vào đệm ghế",
                "Lưu ý kỹ thuật: Khép chặt khuỷu tay sát hai bên sườn",
                "Lưu ý kỹ thuật: Không nhún bả vai lên sát tai"
            ],
            "breathing": [
                "Thở ra khi kéo tạ lên, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Nhấc ngực rời khỏi mặt đệm ghế",
                "Tránh: Dùng cơ tay trước quá nhiều để kéo thay vì dùng cơ lưng"
            ]
        }
    },

    # 39: id=0314 | Dumbbell Incline Bench Press
    {
        "id": "0314",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế dốc lên một góc 30 đến 45 độ, mỗi tay cầm một quả tạ đơn.",
                "Nằm ngửa tựa lưng vào ghế và đưa hai quả tạ đơn lên ngang ngực với lòng bàn tay hướng ra phía trước."
            ],
            "execution": [
                "Đặt vững hai bàn chân trên sàn và mở khuỷu tay hơi thấp hơn tầm bả vai.",
                "Đẩy hai quả tạ đơn thẳng lên phía trên ngực trên cho đến khi hai cánh tay duỗi thẳng.",
                "Hạ hai quả tạ đơn từ từ có kiểm soát xuống hai bên ngực trên.",
                "Tiếp tục đẩy tạ lên theo đúng quỹ đạo chuyển động ổn định.",
                "Lưu ý kỹ thuật: Giữ cổ tay thẳng hàng trên cẳng tay",
                "Lưu ý kỹ thuật: Đạp chặt hai bàn chân xuống sàn",
                "Lưu ý kỹ thuật: Hạ tạ chậm rãi có kiểm soát"
            ],
            "breathing": [
                "Hít vào khi hạ hai quả tạ đơn xuống, thở ra khi đẩy tạ lên cao.",
                "Tránh: Xòe ngang hai khuỷu tay vuông góc với thân người",
                "Tránh: Để hai quả tạ đơn trôi lệch về phía mặt"
            ]
        }
    },

    # 40: id=0322 | Dumbbell Incline Biceps Curl
    {
        "id": "0322",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế dốc lên một góc 45 đến 60 độ và ngồi tựa lưng vào ghế với mỗi tay cầm một quả tạ đơn.",
                "Thả lỏng hai cánh tay duỗi thẳng hoàn toàn ở hai bên sườn, giữ khuỷu tay sát thân người."
            ],
            "execution": [
                "Cuốn hai quả tạ đơn lên bằng cách gập khuỷu tay, giữ cố định hai cánh tay trên.",
                "Dừng lại một nhịp và siết chặt cơ tay trước ở đỉnh của động tác.",
                "Hạ hai quả tạ đơn từ từ có kiểm soát trở lại vị trí ban đầu.",
                "Lưu ý kỹ thuật: Giữ bất động hai khuỷu tay",
                "Lưu ý kỹ thuật: Để cánh tay duỗi thẳng hoàn toàn khi hạ",
                "Lưu ý kỹ thuật: Tuyệt đối không vung vẩy lấy đà nâng tạ"
            ],
            "breathing": [
                "Thở ra khi cuốn tạ lên, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Vung cánh tay để lấy đà nâng tạ",
                "Tránh: Để khuỷu tay bị trượt ra phía trước"
            ]
        }
    },

    # 41: id=0318 | Dumbbell Incline Curl
    {
        "id": "0318",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế tập dốc lên và ngồi ngả lưng vào ghế với mỗi tay cầm một quả tạ đơn.",
                "Để hai cánh tay buông thẳng tự nhiên dưới vai với hai lòng bàn tay hướng ra phía trước."
            ],
            "execution": [
                "Giữ cố định hai cánh tay trên và cuốn hai quả tạ đơn lên phía vai.",
                "Dừng lại một nhịp ở điểm cao nhất và siết chặt cơ tay trước.",
                "Hạ hai quả tạ đơn từ từ cho đến khi hai khuỷu tay duỗi thẳng trở lại hoàn toàn.",
                "Lưu ý kỹ thuật: Giữ cố định khớp khuỷu tay",
                "Lưu ý kỹ thuật: Giữ lòng bàn tay luôn hướng ra trước",
                "Lưu ý kỹ thuật: Phát lực chủ động từ cơ bắp tay trước"
            ],
            "breathing": [
                "Hít vào khi hạ hai quả tạ đơn xuống, thở ra khi cuốn tạ lên cao.",
                "Tránh: Vung đà hai quả tạ đơn để bắt đầu cuốn",
                "Tránh: Để khuỷu tay trôi đẩy ra trước khi tạ nâng lên"
            ]
        }
    },

    # 42: id=0319 | Dumbbell Incline Fly
    {
        "id": "0319",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế dốc lên và ngồi đặt hai quả tạ đơn trên hai đùi.",
                "Ngả lưng nằm vào ghế và giơ hai quả tạ đơn lên phía trên ngực trên với lòng bàn tay hướng vào nhau."
            ],
            "execution": [
                "Hơi chùng nhẹ hai khuỷu tay và khóa cố định góc gập đó.",
                "Mở rộng hai quả tạ đơn sang hai bên theo đường vòng cung cho đến khi tạ ngang tầm ngực hoặc cơ ngực cảm thấy căng nhẹ.",
                "Siết chặt cơ ngực để khép hai quả tạ đơn lại với nhau phía trên ngực trên theo đúng quỹ đạo vòng cung cũ.",
                "Dừng lại khi hai quả tạ gần chạm vào nhau rồi tiếp tục lặp lại.",
                "Lưu ý kỹ thuật: Khuỷu tay chùng nhẹ, cố định góc gập",
                "Lưu ý kỹ thuật: Mở rộng vòng cung, không hạ tạ quá sâu",
                "Lưu ý kỹ thuật: Siết chặt cơ ngực ở điểm cao nhất"
            ],
            "breathing": [
                "Hít vào khi mở hai quả tạ đơn sang hai bên, thở ra khi khép hai tạ lại phía trên ngực.",
                "Tránh: Co duỗi khuỷu tay làm biến động tác thành bài đẩy ngực",
                "Tránh: Hạ hai quả tạ đơn xuống quá sâu dưới mức ngực"
            ]
        }
    },

    # 43: id=1278 | Dumbbell Incline Fly On Exercise Ball
    {
        "id": "1278",
        "stepsVi": {
            "prepare": [
                "Cầm mỗi tay một quả tạ đơn và tựa lưng trên vào bóng tập thể lực sao cho thân người tạo một góc dốc hướng lên trên.",
                "Đặt hai bàn chân vững chắc trên sàn và nâng hai quả tạ đơn lên phía trên ngực trên với lòng bàn tay hướng vào nhau."
            ],
            "execution": [
                "Giữ khuỷu tay hơi chùng nhẹ và mở rộng hai cánh tay hạ tạ sang hai bên theo hình vòng cung.",
                "Dừng lại khi khuỷu tay gần ngang tầm ngực và bạn cảm nhận cơ ngực được kéo căng.",
                "Siết chặt cơ ngực và đưa hai quả tạ đơn nâng lên theo cùng đường vòng cung cho đến khi gặp nhau phía trên ngực.",
                "Lưu ý kỹ thuật: Giữ khuỷu tay luôn hơi chùng nhẹ",
                "Lưu ý kỹ thuật: Mở rộng tay có kiểm soát",
                "Lưu ý kỹ thuật: Phát lực khép tạ từ cơ ngực"
            ],
            "breathing": [
                "Hít vào khi mở hai quả tạ đơn sang hai bên, thở ra khi khép hai tạ lại phía trên ngực.",
                "Tránh: Duỗi thẳng khuỷu tay làm biến động tác thành bài đẩy ngực",
                "Tránh: Hạ hai quả tạ đơn xuống quá sâu dưới mức ngực"
            ]
        }
    },

    # 44: id=0320 | Dumbbell Incline Hammer Curl
    {
        "id": "0320",
        "stepsVi": {
            "prepare": [
                "Chỉnh ghế tập dốc lên và ngồi tựa lưng vào ghế với mỗi tay cầm một quả tạ đơn.",
                "Để hai cánh tay buông thẳng tự nhiên bên sườn với lòng bàn tay hướng vào nhau."
            ],
            "execution": [
                "Giữ cố định hai cánh tay trên và cuốn cả hai quả tạ đơn lên phía vai.",
                "Dừng lại khi hai cẳng tay gần như dựng thẳng đứng và siết chặt cơ bắp tay.",
                "Hạ hai quả tạ đơn từ từ cho đến khi hai khuỷu tay duỗi thẳng trở lại hoàn toàn.",
                "Lặp lại động tác mà không đung đưa thân người hay để vai bị cuộn về phía trước.",
                "Lưu ý kỹ thuật: Hai lòng bàn tay luôn hướng vào nhau",
                "Lưu ý kỹ thuật: Giữ cố định chặt hai khuỷu tay",
                "Lưu ý kỹ thuật: Chủ động dùng lực nâng tạ, không văng đà"
            ],
            "breathing": [
                "Thở ra khi cuốn hai quả tạ đơn lên, hít vào sâu khi hạ tạ xuống.",
                "Tránh: Vung đung đưa thân người để giật hai quả tạ đơn lên",
                "Tránh: Để khuỷu tay bị trượt ra phía trước trong lúc cuốn tạ"
            ]
        }
    }
]

# Write to vi_batch_1.json
out_path = '/Users/cp/code/ai/shaken/scripts/vi_batch_1.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(vi_data, f, ensure_ascii=False, indent=2)

print(f"Successfully wrote {len(vi_data)} exercises to {out_path}")
