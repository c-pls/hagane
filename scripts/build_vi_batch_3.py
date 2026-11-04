import json
import re

DATA = [
  # 0: drv-close-feet-leg-press
  {
    "id": "drv-close-feet-leg-press",
    "stepsVi": {
      "prepare": [
        "Ngồi vào máy đạp đùi với hai bàn chân đặt sát nhau trên bàn đạp.",
        "Điều chỉnh ghế ngồi và vị trí đặt chân sao cho thoải mái và an toàn."
      ],
      "execution": [
        "Mở chốt an toàn và nắm chắc hai tay cầm bên hông để giữ vững cơ thể.",
        "Duỗi khớp gối để đạp bàn đạp đẩy tạ lên trên.",
        "Hạ bàn đạp từ từ quay về vị trí ban đầu.",
        "Lưu ý kỹ thuật: Giữ đầu gối luôn chuyển động thẳng hàng với mũi chân",
        "Lưu ý kỹ thuật: Không khóa cứng khớp gối ở điểm cao nhất",
        "Lưu ý kỹ thuật: Hạ tạ có kiểm soát và giữ chuyển động chậm rãi"
      ],
      "breathing": [
        "Thở ra khi đạp tạ lên, hít vào khi hạ tạ xuống.",
        "Tránh: Để hai đầu gối sụp chụm vào nhau",
        "Tránh: Nhấc gót chân rời khỏi bàn đạp"
      ]
    }
  },

  # 1: 0573
  {
    "id": "0573",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh máy sao cho đệm tựa lưng áp vừa vặn vào lưng trên và hai bàn chân được cố định vững chắc trên bàn đạp.",
        "Ngồi thẳng người tựa sát vào đệm và nắm chắc hai tay cầm hoặc thanh vịn hai bên."
      ],
      "execution": [
        "Gồng chặt cơ bụng và gập thân người về phía trước có kiểm soát theo toàn bộ biên độ của máy.",
        "Dừng lại ở vị trí thấp nhất khi cảm thấy cơ lưng dưới được kéo căng thoải mái, giữ bàn chân ép chặt vào bàn đạp.",
        "Phát lực từ lưng dưới đẩy thân người ra sau ép vào đệm tựa cho đến khi trở lại tư thế ngồi thẳng.",
        "Lặp lại động tác nhịp nhàng, không dùng đà nảy hoặc giật mạnh đệm tựa.",
        "Lưu ý kỹ thuật: Gồng chặt cơ bụng trước khi bắt đầu chuyển động",
        "Lưu ý kỹ thuật: Di chuyển mượt mà theo cung đường tròn cố định của máy",
        "Lưu ý kỹ thuật: Giữ hai bàn chân luôn bám chặt trên bàn đạp"
      ],
      "breathing": [
        "Hít vào khi gập thân người ra trước, thở ra khi duỗi lưng đẩy người về tư thế thẳng đứng.",
        "Tránh: Dùng quán tính và giật nảy người từ vị trí thấp nhất",
        "Tránh: Tập với biên độ quá ngắn hoặc di chuyển vội vàng mất kiểm soát"
      ]
    }
  },

  # 2: 0581
  {
    "id": "0581",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi sao cho tay cầm ngang tầm ngực trên khi bạn ngồi xuống.",
        "Ngồi áp sát ngực vào đệm tựa và đặt hai bàn chân phẳng vững chãi trên bàn đạp."
      ],
      "execution": [
        "Nắm chặt tay cầm bằng kiểu nắm sấp bàn tay và duỗi thẳng cánh tay mà không nhấc ngực khỏi đệm.",
        "Kéo tay cầm về phía xương sườn trên bằng cách hướng cùi chỏ xuống dưới và ra sau.",
        "Khép chặt hai bả vai vào nhau ở điểm cuối của động tác kéo.",
        "Từ từ đưa tay cầm về phía trước có kiểm soát cho đến khi hai cánh tay duỗi thẳng trở lại.",
        "Lưu ý kỹ thuật: Luôn giữ ngực áp sát cố định vào đệm tựa",
        "Lưu ý kỹ thuật: Chủ động kéo cùi chỏ mạnh mẽ về phía sau",
        "Lưu ý kỹ thuật: Siết chặt hai bả vai để kích hoạt cơ lưng tối đa"
      ],
      "breathing": [
        "Thở ra khi kéo tay cầm về phía người, hít vào khi trả tay cầm về vị trí ban đầu.",
        "Tránh: Nhún hai vai lên sát tai khi kéo tạ",
        "Tránh: Ngả người rời khỏi đệm tựa ngực để lấy đà giật tạ"
      ]
    }
  },

  # 3: 2611
  {
    "id": "2611",
    "stepsVi": {
      "prepare": [
        "Ngồi vào máy đạp đùi nằm ngang và điều chỉnh khoảng cách ghế phù hợp.",
        "Đặt hai bàn chân rộng bằng vai trên bàn đạp."
      ],
      "execution": [
        "Đạp duỗi chân để đẩy bàn đạp ra xa.",
        "Không khóa cứng khớp gối ở vị trí duỗi thẳng cao nhất.",
        "Hạ bàn đạp về vị trí ban đầu một cách chậm rãi có kiểm soát.",
        "Lưu ý kỹ thuật: Luôn giữ lưng dưới áp sát vào đệm ghế",
        "Lưu ý kỹ thuật: Tuyệt đối không khóa cứng khớp gối",
        "Lưu ý kỹ thuật: Đặt toàn bộ bàn chân phẳng và phân bổ lực đều khắp bàn chân"
      ],
      "breathing": [
        "Thở ra khi đạp tạ ra xa, hít vào khi gập chân hạ tạ về.",
        "Tránh: Để hai đầu gối chụm vào trong hoặc xòe ra ngoài quá mức",
        "Tránh: Nhấc mông và hông rời khỏi đệm ghế"
      ]
    }
  },

  # 4: 1299
  {
    "id": "1299",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh chiều cao ghế ngồi sao cho tay cầm nằm ở vị trí tối ưu ngang ngực trên.",
        "Ngồi vững trên ghế và nắm chặt tay cầm dọc với cùi chỏ gập lại."
      ],
      "execution": [
        "Đẩy tay cầm lên trên và hơi hướng ra trước ở phía trên ngực.",
        "Tránh khóa cứng hoàn toàn khớp cùi chỏ ở điểm cao nhất.",
        "Hạ tay cầm xuống từ từ có kiểm soát về vị trí bắt đầu.",
        "Lưu ý kỹ thuật: Đẩy tạ hướng lên trên và chếch nhẹ về phía trước",
        "Lưu ý kỹ thuật: Giữ hai bàn chân áp phẳng vững chắc trên sàn",
        "Lưu ý kỹ thuật: Không nhún vai hoặc gồng cổ"
      ],
      "breathing": [
        "Thở ra khi đẩy tạ lên, hít vào khi hạ tạ xuống.",
        "Tránh: Bành cùi chỏ sang hai bên quá rộng gây áp lực lên vai",
        "Tránh: Khóa cứng khớp cùi chỏ khi đẩy hết tầm"
      ]
    }
  },

  # 5: 0582
  {
    "id": "0582",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh máy sao cho khớp gối thẳng hàng với trục quay của máy và phần cổ chân nằm gọn gàng dưới đệm lăn đỡ.",
        "Quỳ gối lên đệm hướng mặt về phía máy, tựa thân người vững chãi vào đệm đỡ và nắm chặt hai tay cầm."
      ],
      "execution": [
        "Bắt đầu với chân duỗi thẳng ra phía sau và giữ cố định phần hông.",
        "Gập đầu gối để cuốn gót chân lên sát cơ mông bằng cách ép mạnh vào đệm lăn.",
        "Dừng lại 1 nhịp ở điểm co rút cao nhất và siết chặt cơ đùi sau.",
        "Hạ đệm lăn xuống từ từ có kiểm soát cho đến khi chân duỗi thẳng trở lại.",
        "Lưu ý kỹ thuật: Giữ phần hông luôn áp chặt cố định vào đệm",
        "Lưu ý kỹ thuật: Gập tạ dứt khoát bằng khớp gối",
        "Lưu ý kỹ thuật: Nhả chân thật chậm và kiểm soát trên đường hạ xuống"
      ],
      "breathing": [
        "Thở ra khi cuốn gót chân lên, hít vào khi hạ chân duỗi thẳng về vị trí ban đầu.",
        "Tránh: Nhấc hông rời khỏi đệm trong quá trình cuốn chân",
        "Tránh: Vung chân lấy đà để bắt đầu mỗi nhịp tập"
      ]
    }
  },

  # 6: 0584
  {
    "id": "0584",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi sao cho tay đòn của máy thẳng hàng với khớp vai khi bạn ngồi xuống.",
        "Ngồi tựa lưng vào đệm và đặt cẳng tay hoặc bàn tay lên đệm tỳ hoặc tay cầm của máy."
      ],
      "execution": [
        "Bắt đầu với hai cánh tay thả dọc hai bên thân người và giữ cùi chỏ hơi cong nhẹ.",
        "Nâng hai tay đòn của máy sang hai bên cho đến khi cánh tay trên ngang tầm vai.",
        "Dừng lại 1 nhịp ở điểm cao nhất mà không nhún vai lên.",
        "Hạ hai tay đòn xuống có kiểm soát quay trở lại vị trí ban đầu.",
        "Lưu ý kỹ thuật: Dẫn hướng chuyển động bằng cùi chỏ",
        "Lưu ý kỹ thuật: Giữ hai vai hạ thấp, không gồng vai",
        "Lưu ý kỹ thuật: Nâng tạ lên ngang tầm vai"
      ],
      "breathing": [
        "Thở ra khi nâng tay sang hai bên, hít vào khi hạ tay xuống.",
        "Tránh: Nhún hai vai lên sát tai",
        "Tránh: Vung giật hoặc nhún nảy tạ ở vị trí thấp nhất"
      ]
    }
  },

  # 7: 0585
  {
    "id": "0585",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi và đệm tựa lưng sao cho khớp gối thẳng hàng với trục quay của máy.",
        "Ngồi tựa lưng sát vào đệm và đặt cẳng chân phía sau con lăn đệm dưới."
      ],
      "execution": [
        "Nắm chặt hai tay cầm, bắt đầu với đầu gối gập và mũi chân hướng về phía trước.",
        "Duỗi thẳng khớp gối để nâng đệm tạ lên cho đến khi hai chân gần như thẳng hoàn toàn.",
        "Dừng lại 1 nhịp trong khi vẫn giữ đùi áp chặt xuống mặt ghế.",
        "Hạ đệm tạ xuống có kiểm soát cho đến khi đầu gối gập trở lại.",
        "Lưu ý kỹ thuật: Đảm bảo khớp gối thẳng hàng với trục quay của máy",
        "Lưu ý kỹ thuật: Nâng tạ bằng lực co của cơ đùi trước",
        "Lưu ý kỹ thuật: Giữ cố định mông và hông trên mặt ghế"
      ],
      "breathing": [
        "Thở ra khi duỗi thẳng khớp gối đá tạ lên, hít vào khi hạ đệm tạ xuống.",
        "Tránh: Đặt đầu gối quá xa ra phía trước hoặc phía sau so với trục quay của máy.",
        "Tránh: Dùng quán tính vung mạnh tạ lên."
      ]
    }
  },

  # 8: 0577
  {
    "id": "0577",
    "stepsVi": {
      "prepare": [
        "Nằm ngửa trên đệm ghế của máy tập ngực.",
        "Nắm chắc hai tay cầm với cùi chỏ gập lại."
      ],
      "execution": [
        "Gồng siết cơ ngực và đẩy hai tay cầm ra phía trước và lên trên.",
        "Duỗi thẳng hoàn toàn hai cánh tay nhưng không khóa cứng khớp cùi chỏ.",
        "Từ từ hạ tay quay trở lại vị trí bắt đầu.",
        "Lưu ý kỹ thuật: Giữ hai bàn chân áp phẳng trên sàn",
        "Lưu ý kỹ thuật: Không duỗi cùi chỏ quá mức",
        "Lưu ý kỹ thuật: Đẩy lực đồng đều bằng cả hai cánh tay"
      ],
      "breathing": [
        "Thở ra khi đẩy tạ lên, hít vào khi hạ tạ xuống.",
        "Tránh: Để hai vai bị cuộn đổ về phía trước",
        "Tránh: Nhấc lưng dưới rời khỏi đệm ghế"
      ]
    }
  },

  # 9: 0586
  {
    "id": "0586",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh máy sao cho khớp gối thẳng hàng với trục quay của máy và đệm lăn tỳ vào phía sau cẳng chân ngay trên gót chân.",
        "Nằm sấp trên đệm ghế với hai chân duỗi thẳng, nắm chắc hai tay cầm hoặc mép ghế để giữ vững cơ thể."
      ],
      "execution": [
        "Áp chặt hông vào đệm ghế và hướng mũi chân thẳng ra trước để vào tư thế bắt đầu.",
        "Gập đầu gối để cuốn đệm tạ lên trên cho đến khi gót chân hướng sát về phía cơ mông.",
        "Dừng lại 1 nhịp ở điểm cao nhất trong khi vẫn giữ hông và đùi áp chặt vào đệm.",
        "Hạ đệm tạ xuống từ từ có kiểm soát cho đến khi chân duỗi thẳng trở lại.",
        "Lưu ý kỹ thuật: Luôn giữ phần hông áp chặt vào mặt đệm",
        "Lưu ý kỹ thuật: Phát lực cuốn tạ tập trung hoàn toàn vào cơ đùi sau",
        "Lưu ý kỹ thuật: Chuyển động hạ tạ thật chậm rãi và có kiểm soát"
      ],
      "breathing": [
        "Thở ra khi cuốn đệm tạ lên, hít vào khi hạ tạ xuống có kiểm soát.",
        "Tránh: Nhấc hông rời khỏi đệm ở điểm cao nhất",
        "Tránh: Dùng đà quán tính vung hất đệm tạ lên"
      ]
    }
  },

  # 10: 0592
  {
    "id": "0592",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi sao cho hõm nách tỳ sát vào mép trên của bệ đỡ tay.",
        "Ngồi xuống và đặt toàn bộ mặt sau cánh tay trên áp phẳng lên mặt bệ đỡ."
      ],
      "execution": [
        "Nắm chặt tay cầm của máy bằng kiểu nắm ngửa bàn tay và duỗi tay về vị trí xuất phát.",
        "Giữ ngực ưỡn cao và gập cùi chỏ để cuốn tay cầm về phía vai.",
        "Siết chặt cơ tay trước trong 1 nhịp ở điểm cao nhất mà không nhấc cánh tay trên khỏi bệ tỳ.",
        "Hạ tay cầm xuống có kiểm soát cho đến khi cánh tay gần như duỗi thẳng hoàn toàn.",
        "Lưu ý kỹ thuật: Giữ chặt cánh tay trên áp sát cố định vào bệ tỳ",
        "Lưu ý kỹ thuật: Chỉ chuyển động duy nhất ở khớp cùi chỏ",
        "Lưu ý kỹ thuật: Cuốn lên mượt mà và hạ xuống thật chậm rãi"
      ],
      "breathing": [
        "Thở ra khi cuốn tay cầm lên, hít vào khi hạ tạ xuống có kiểm soát.",
        "Tránh: Nhấc cánh tay trên khỏi bệ tỳ khi tạ đang nâng lên",
        "Tránh: Dùng vai hoặc đung đưa thân người để lấy đà cuốn tạ"
      ]
    }
  },

  # 11: 0593
  {
    "id": "0593",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh máy sao cho hông tựa vững trên đệm và hai chân có thể buông thõng tự do.",
        "Nằm sấp với toàn bộ thân trên tựa chắc chắn, nắm chặt hai tay cầm hoặc mép máy để giữ thăng bằng."
      ],
      "execution": [
        "Đặt chân vào đệm đỡ và để hai chân buông thõng xuống dưới có kiểm soát.",
        "Gồng chặt cơ bụng và siết cơ mông để nâng hai chân ra phía sau lên cao.",
        "Nâng chân lên cho đến khi thẳng hàng với thân người mà không làm cong ưỡn lưng dưới.",
        "Hạ hai chân từ từ quay về vị trí bắt đầu và lặp lại động tác.",
        "Lưu ý kỹ thuật: Phát lực nâng chân chủ yếu bằng cơ mông",
        "Lưu ý kỹ thuật: Giữ hông luôn áp sát vào đệm đỡ",
        "Lưu ý kỹ thuật: Kiểm soát chuyển động, không để chân đung đưa tự do"
      ],
      "breathing": [
        "Hít vào khi hạ chân xuống, thở ra khi siết cơ mông nâng chân ra sau.",
        "Tránh: Dùng đà vung chân lên cao",
        "Tránh: Ưỡn cong lưng dưới quá mức ở đỉnh chuyển động"
      ]
    }
  },

  # 12: 1349
  {
    "id": "1349",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế hoặc đệm đỡ ngực sao cho tay cầm ngang tầm ngực giữa khi vươn tay ra trước.",
        "Áp ngực vững chắc vào đệm tựa và đặt hai bàn chân phẳng trên bàn đạp."
      ],
      "execution": [
        "Nắm chặt tay cầm bằng kiểu nắm sấp bàn tay và duỗi thẳng cánh tay mà không để gù vai.",
        "Kéo tay cầm về phía ngực bằng cách kéo cùi chỏ ra sau và hơi chếch ra ngoài.",
        "Khép chặt hai bả vai vào nhau ở điểm cuối của động tác kéo.",
        "Hạ tay cầm về phía trước có kiểm soát cho đến khi hai cánh tay duỗi thẳng trở lại.",
        "Lưu ý kỹ thuật: Luôn giữ ngực áp cố định vào đệm tựa",
        "Lưu ý kỹ thuật: Chủ động dẫn hướng chuyển động bằng cùi chỏ",
        "Lưu ý kỹ thuật: Siết chặt hai bả vai lại với nhau"
      ],
      "breathing": [
        "Thở ra khi kéo tay cầm về phía ngực, hít vào khi duỗi tay hạ tạ có kiểm soát.",
        "Tránh: Nhún hai vai lên sát tai",
        "Tránh: Nhấc ngực rời khỏi đệm để lấy đà giật tay cầm"
      ]
    }
  },

  # 13: 0594
  {
    "id": "0594",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế sao cho đệm tỳ đùi áp chắc chắn lên đùi với đầu gối gập khoảng 90 độ.",
        "Đặt phần ức bàn chân lên mép bàn đạp với gót chân thả tự do ngoài rìa."
      ],
      "execution": [
        "Nắm chặt tay cầm hoặc mép ghế và nâng nhẹ gót chân để tải tạ lên cơ bắp chân.",
        "Dùng lực từ ức bàn chân nhấn xuống để nhón gót chân lên cao hết mức có thể.",
        "Dừng lại 1 nhịp ở điểm cao nhất trong khi các ngón chân vẫn bám chắc trên bàn đạp.",
        "Hạ gót chân xuống từ từ cho đến khi cảm thấy cơ bắp chân được kéo căng, sau đó lặp lại.",
        "Lưu ý kỹ thuật: Dồn lực phát động qua ngón chân cái",
        "Lưu ý kỹ thuật: Nâng gót chân thẳng đứng lên trên",
        "Lưu ý kỹ thuật: Kiểm soát chuyển động hạ gót thật chậm rãi"
      ],
      "breathing": [
        "Hít vào khi hạ gót chân xuống, thở ra khi nhấn ức bàn chân nhón gót lên cao.",
        "Tránh: Nhún nảy giật cục ở điểm thấp nhất thay vì hạ tạ có kiểm soát.",
        "Tránh: Để đầu gối nhấp nhô lên xuống trong suốt nhịp tập."
      ]
    }
  },

  # 14: 1452
  {
    "id": "1452",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi và chọn mức tạ phù hợp.",
        "Ngồi tựa lưng ra sau, móc chân cố định và nắm chặt tay cầm theo thiết kế của máy."
      ],
      "execution": [
        "Gồng cứng cơ bụng và cuộn cột sống về phía trước theo chuyển động gập bụng.",
        "Kéo ngực gập về phía đầu gối đồng thời thở ra.",
        "Kiểm soát chuyển động trả người về vị trí ban đầu và lặp lại.",
        "Lưu ý kỹ thuật: Chuyển động bằng lực cơ bụng, không dùng lực từ khớp hông",
        "Lưu ý kỹ thuật: Tuyệt đối không dùng quán tính để giật người",
        "Lưu ý kỹ thuật: Duy trì chuyển động chậm rãi và có kiểm soát"
      ],
      "breathing": [
        "Thở ra khi gập người xuống, hít vào khi mở người trở về vị trí ban đầu.",
        "Tránh: Để cơ gập hông hoạt động quá mức thay vì cơ bụng",
        "Tránh: Dùng mức tạ quá nặng làm sai tư thế"
      ]
    }
  },

  # 15: 1451
  {
    "id": "1451",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh độ cao ghế ngồi và chọn mức tạ phù hợp.",
        "Ngồi thẳng lưng và nắm chặt hai tay cầm."
      ],
      "execution": [
        "Nhấn tay cầm xuống dưới bằng cách duỗi thẳng hoàn toàn cánh tay.",
        "Dừng lại 1 nhịp ở vị trí duỗi hết tầm.",
        "Từ từ nhả tay quay trở lại vị trí ban đầu.",
        "Lưu ý kỹ thuật: Giữ hai cùi chỏ khép sát hai bên thân người",
        "Lưu ý kỹ thuật: Kiểm soát chuyển động khi nâng tay trở về",
        "Lưu ý kỹ thuật: Không khóa cứng khớp cùi chỏ"
      ],
      "breathing": [
        "Thở ra khi nhấn tay xuống, hít vào khi đưa tay trở lên.",
        "Tránh: Để cùi chỏ bành rộng sang hai bên",
        "Tránh: Sử dụng mức tạ quá nặng"
      ]
    }
  },

  # 16: 0597
  {
    "id": "0597",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế sao cho đầu gối gập khoảng 90 độ và đệm tỳ đùi áp vào mặt ngoài hai chân.",
        "Ngồi thẳng người tựa lưng vào đệm, đặt hai bàn chân lên bàn để chân và nắm chặt hai tay cầm."
      ],
      "execution": [
        "Bắt đầu với hai chân khép lại và khớp gối thẳng hàng với trục quay của máy.",
        "Phát lực đẩy hai đầu gối sang hai bên ép vào đệm cho đến khi chân mở rộng hết biên độ thoải mái.",
        "Dừng lại 1 nhịp ở điểm mở rộng nhất trong khi mông vẫn giữ cố định trên mặt ghế.",
        "Khép hai chân lại từ từ cho đến khi hai đệm gần chạm nhau, sau đó lặp lại.",
        "Lưu ý kỹ thuật: Luôn ngồi thẳng lưng",
        "Lưu ý kỹ thuật: Phát lực chủ động mở rộng từ đầu gối",
        "Lưu ý kỹ thuật: Kiểm soát chuyển động khi khép chân trở về"
      ],
      "breathing": [
        "Thở ra khi mở đầu gối sang hai bên, hít vào khi khép chân về vị trí bắt đầu.",
        "Tránh: Chồm thân người ra trước hoặc đung đưa ra sau để đẩy tạ.",
        "Tránh: Thả lỏng để hai chân bật khép mạnh vào nhau khi trở về."
      ]
    }
  },

  # 17: 0598
  {
    "id": "0598",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế và đệm sao cho đầu gối thẳng hàng với trục quay của máy.",
        "Ngồi thẳng lưng tựa vào đệm, đặt hai chân ở mặt ngoài đệm tỳ đùi và nắm chặt hai tay cầm."
      ],
      "execution": [
        "Đặt bàn chân phẳng trên bàn để chân và bắt đầu với hai chân mở rộng vừa phải.",
        "Ép hai chân vào trong bằng cách đẩy mạnh vào đệm đùi.",
        "Siết chặt cơ đùi trong trong 1 nhịp khi hai đệm chạm sát vào nhau.",
        "Nhả hai chân mở ra ngoài từ từ về vị trí bắt đầu mà không để bánh tạ va đập mạnh.",
        "Lưu ý kỹ thuật: Luôn ngồi thẳng lưng",
        "Lưu ý kỹ thuật: Kiểm soát lực ở cả hai chiều ép và nhả",
        "Lưu ý kỹ thuật: Tập trung siết chặt cơ đùi trong"
      ],
      "breathing": [
        "Thở ra khi ép hai chân khép vào nhau, hít vào khi mở chân về vị trí bắt đầu.",
        "Tránh: Chồm người ra trước hoặc nhấc lưng dưới rời khỏi đệm tựa.",
        "Tránh: Thả chân mở bung ra ngoài quá nhanh khi nhả tạ."
      ]
    }
  },

  # 18: 0599
  {
    "id": "0599",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi và đệm đỡ sao cho khớp gối thẳng hàng với trục quay của máy.",
        "Ngồi tựa lưng sát vào đệm và đặt cẳng chân dưới con lăn đệm, ngay phía trên cổ chân."
      ],
      "execution": [
        "Nắm chặt hai tay cầm và giữ đùi ép chặt xuống mặt ghế.",
        "Gập đầu gối để cuốn đệm tạ xuống dưới cho đến khi gót chân hướng về phía sàn.",
        "Dừng lại 1 nhịp và siết chặt cơ đùi sau ở điểm thấp nhất.",
        "Nhả đệm tạ nâng lên có kiểm soát cho đến khi chân gần như duỗi thẳng hoàn toàn.",
        "Lưu ý kỹ thuật: Giữ chặt phần hông và mông cố định trên ghế",
        "Lưu ý kỹ thuật: Phát lực cuốn tạ thông qua gót chân",
        "Lưu ý kỹ thuật: Chỉ chuyển động duy nhất ở khớp gối"
      ],
      "breathing": [
        "Thở ra khi cuốn đệm tạ xuống dưới, hít vào khi trả chân trở về vị trí ban đầu.",
        "Tránh: Nhấc mông khỏi mặt ghế trong quá trình cuốn tạ.",
        "Tránh: Dùng đà quán tính và vung giật đệm tạ trong suốt nhịp tập."
      ]
    }
  },

  # 19: 0602
  {
    "id": "0602",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi sao cho tay cầm ngang tầm vai khi bạn ngồi xuống.",
        "Ngồi áp ngực vào đệm tựa, bàn chân đặt phẳng trên sàn và nắm tay cầm bằng kiểu nắm sấp bàn tay."
      ],
      "execution": [
        "Bắt đầu với hai cánh tay ở phía trước ngực và giữ cùi chỏ hơi cong nhẹ.",
        "Kéo hai tay cầm mở rộng sang hai bên và ra sau theo vòng cung lớn cho đến khi cánh tay thẳng hàng với vai.",
        "Siết chặt cơ vai sau và cơ lưng trên ở điểm cuối của chuyển động.",
        "Đưa tay cầm trở về vị trí ban đầu thật chậm mà không để bánh tạ va đập vào nhau.",
        "Lưu ý kỹ thuật: Dẫn hướng chuyển động bằng cùi chỏ",
        "Lưu ý kỹ thuật: Luôn giữ ngực áp sát cố định vào đệm tựa",
        "Lưu ý kỹ thuật: Giữ cùi chỏ hơi cong nhẹ trong suốt bài tập"
      ],
      "breathing": [
        "Thở ra khi kéo tay cầm ra phía sau, hít vào khi đưa tay trở về vị trí ban đầu.",
        "Tránh: Nhún hai vai lên sát tai",
        "Tránh: Duỗi thẳng cứng cùi chỏ biến bài tập thành động tác đẩy"
      ]
    }
  },

  # 20: 0604
  {
    "id": "0604",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh máy sao cho tay cầm nằm ở hai bên hông khi vai ở trạng thái thả lỏng.",
        "Ngồi hoặc đứng tựa vào đệm và nắm chắc tay cầm bằng kiểu nắm sấp bàn tay."
      ],
      "execution": [
        "Duỗi thẳng cánh tay, ưỡn ngực cao và giữ cổ ở vị trí tự nhiên.",
        "Nhún hai vai thẳng đứng lên phía tai mà không gập cùi chỏ.",
        "Dừng lại 1 nhịp ở điểm cao nhất trong khi thân người giữ cố định.",
        "Hạ hai vai xuống từ từ có kiểm soát cho đến khi trở về vị trí ban đầu.",
        "Lưu ý kỹ thuật: Nhún vai thẳng đứng lên trên",
        "Lưu ý kỹ thuật: Giữ cánh tay luôn duỗi thẳng tự nhiên",
        "Lưu ý kỹ thuật: Luôn giữ ngực ưỡn cao"
      ],
      "breathing": [
        "Hít vào ở vị trí thấp nhất, thở ra khi nhún vai lên cao, sau đó hít vào khi hạ vai xuống.",
        "Tránh: Gập cùi chỏ biến bài tập thành động tác kéo lưng",
        "Tránh: Xoay tròn vai ra trước hoặc ra sau"
      ]
    }
  },

  # 21: 0605
  {
    "id": "0605",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh đệm tỳ vai sao cho tựa thoải mái lên vai khi bạn đứng trên bục để chân.",
        "Đặt phần ức bàn chân lên mép bục với gót chân thả tự do ngoài rìa và nắm chắc hai tay cầm."
      ],
      "execution": [
        "Duỗi thẳng chân, gồng chặt thân người và hạ gót chân xuống cho đến khi cảm thấy cơ bắp chân được kéo căng.",
        "Nhấn mạnh phần ức bàn chân để nhón gót chân lên cao hết mức có thể.",
        "Dừng lại 1 nhịp ở điểm cao nhất trong khi giữ thăng bằng vững dưới đệm vai.",
        "Hạ gót chân xuống từ từ có kiểm soát trở về vị trí kéo giãn ban đầu.",
        "Lưu ý kỹ thuật: Dồn lực phát động qua ngón chân cái",
        "Lưu ý kỹ thuật: Nâng gót chân thẳng đứng lên trên",
        "Lưu ý kỹ thuật: Khai thác trọn vẹn toàn bộ biên độ khớp cổ chân"
      ],
      "breathing": [
        "Hít vào khi hạ gót chân xuống, thở ra khi nhấn ức bàn chân nhón gót lên cao.",
        "Tránh: Nhún nảy giật cục ở vị trí thấp nhất thay vì hạ xuống có kiểm soát.",
        "Tránh: Gập chùng đầu gối rõ rệt trong suốt quá trình nâng gót."
      ]
    }
  },

  # 22: 2286
  {
    "id": "2286",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh máy tập cho phù hợp với chiều cao của bạn.",
        "Đặt một chân lên bục đứng, áp sát ngực vào đệm tựa."
      ],
      "execution": [
        "Gồng chặt cơ bụng và nắm chắc tay cầm để giữ thăng bằng.",
        "Duỗi khớp hông, dùng gót chân đạp cần đòn tạ ra phía sau.",
        "Thu chân về vị trí ban đầu và lặp lại động tác.",
        "Lưu ý kỹ thuật: Dồn lực phát động qua gót chân",
        "Lưu ý kỹ thuật: Giữ đầu gối hơi chùng nhẹ",
        "Lưu ý kỹ thuật: Không ưỡn cong lưng dưới"
      ],
      "breathing": [
        "Thở ra khi đạp duỗi hông ra sau, hít vào khi thu chân trở về.",
        "Tránh: Ưỡn cong lưng dưới quá mức",
        "Tránh: Dùng đà quán tính để vung chân"
      ]
    }
  },

  # 23: drv-lever-standing-rear-kick
  {
    "id": "drv-lever-standing-rear-kick",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh đệm tựa của máy đòn bẩy ngang tầm ngực và chọn mức tạ phù hợp.",
        "Đặt chân tập lên bàn đạp tiếp xúc của máy."
      ],
      "execution": [
        "Nắm chắc tay cầm và gồng cứng cơ bụng.",
        "Mở rộng khớp hông bằng cách đạp chân ra sau xa nhất có thể trong biên độ thoải mái.",
        "Thu chân từ từ trở về vị trí ban đầu và lặp lại động tác.",
        "Lưu ý kỹ thuật: Dẫn hướng lực đạp bằng gót chân",
        "Lưu ý kỹ thuật: Giữ cơ bụng luôn siết chặt",
        "Lưu ý kỹ thuật: Tránh ưỡn cong lưng khi đạp chân"
      ],
      "breathing": [
        "Thở ra khi đá đạp chân ra sau, hít vào khi thu chân trở về.",
        "Tránh: Dùng lưng dưới để gánh lực nâng tạ",
        "Tránh: Dùng quán tính vung chân mất kiểm soát"
      ]
    }
  },

  # 24: drv-lever-t-bar-row
  {
    "id": "drv-lever-t-bar-row",
    "stepsVi": {
      "prepare": [
        "Nằm sấp áp ngực vào đệm tựa của máy chèo tạ chữ T và nắm chắc hai tay cầm.",
        "Gồng cứng thân trên và khép nhẹ hai bả vai lại."
      ],
      "execution": [
        "Kéo hai tay cầm về phía ngực hoặc phần dưới xương sườn.",
        "Dừng lại 1 nhịp và siết chặt cơ lưng ở điểm co rút cao nhất.",
        "Hạ tạ xuống có kiểm soát để kéo giãn hoàn toàn cơ lưng.",
        "Lưu ý kỹ thuật: Khép chặt hai bả vai vào nhau",
        "Lưu ý kỹ thuật: Kéo mạnh cùi chỏ về phía sau",
        "Lưu ý kỹ thuật: Giữ ngực luôn áp sát cố định vào đệm tựa"
      ],
      "breathing": [
        "Thở ra khi kéo tạ lên, hít vào khi hạ tạ xuống.",
        "Tránh: Ưỡn cong lưng dưới để lấy đà",
        "Tránh: Không duỗi thẳng tay kéo giãn hết biên độ ở điểm hạ"
      ]
    }
  },

  # 25: 0607
  {
    "id": "0607",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi sao cho tay cầm ngang tầm mắt hoặc trán khi bạn ngồi xuống.",
        "Ngồi tựa lưng vào đệm và đặt hai bàn chân phẳng trên sàn."
      ],
      "execution": [
        "Nắm tay cầm với lòng bàn tay úp xuống và duỗi thẳng cánh tay ra phía trước.",
        "Giữ cố định cánh tay trên và gập cùi chỏ để hạ tay cầm về phía trán.",
        "Dừng lại 1 nhịp khi cùi chỏ gập sâu và tay cầm ở gần đầu.",
        "Đẩy tay cầm ra xa bằng cách duỗi thẳng cùi chỏ cho đến khi cánh tay duỗi thẳng trở lại.",
        "Lưu ý kỹ thuật: Giữ hai cùi chỏ khép gọn vào trong",
        "Lưu ý kỹ thuật: Giữ cánh tay trên cố định không đung đưa",
        "Lưu ý kỹ thuật: Chỉ chuyển động duy nhất ở khớp cùi chỏ"
      ],
      "breathing": [
        "Hít vào khi gập cùi chỏ hạ tay cầm về, thở ra khi duỗi thẳng tay đẩy tạ ra xa.",
        "Tránh: Bành hai cùi chỏ sang hai bên quá rộng.",
        "Tránh: Cuộn hai vai ra trước làm sụp lồng ngực."
      ]
    }
  },

  # 26: drv-lever-pec-deck-fly
  {
    "id": "drv-lever-pec-deck-fly",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh chiều cao ghế ngồi và ngồi áp lưng sát vào đệm tựa.",
        "Đặt hai cẳng tay lên đệm đỡ với cùi chỏ hơi cong nhẹ."
      ],
      "execution": [
        "Ép hai cánh tay lại gần nhau theo một đường vòng cung rộng.",
        "Siết chặt cơ ngực ở điểm cuối của chuyển động ép.",
        "Mở hai tay từ từ quay trở về vị trí ban đầu.",
        "Lưu ý kỹ thuật: Giữ khớp cùi chỏ luôn hơi cong nhẹ thả lỏng",
        "Lưu ý kỹ thuật: Siết cứng cơ ngực ở đỉnh co rút",
        "Lưu ý kỹ thuật: Duy trì toàn bộ lưng áp sát vào đệm tựa"
      ],
      "breathing": [
        "Thở ra khi ép hai tay vào nhau, hít vào khi mở rộng hai tay ra.",
        "Tránh: Khóa cứng khớp cùi chỏ",
        "Tránh: Ưỡn cong lưng dưới rời khỏi đệm"
      ]
    }
  },

  # 27: 0673
  {
    "id": "0673",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh đệm tỳ đùi sao cho vừa khít với đùi trên và đặt hai bàn chân phẳng trên sàn.",
        "Vươn hai tay lên nắm thanh kéo bằng kiểu nắm ngửa bàn tay với khoảng cách rộng bằng vai."
      ],
      "execution": [
        "Ngồi thẳng người, ưỡn ngực cao và hai tay duỗi thẳng hoàn toàn qua đầu.",
        "Kéo thanh cầm xuống về phía ngực trên bằng cách kéo mạnh cùi chỏ xuống dưới và ra sau.",
        "Siết chặt cơ lưng trên và cơ xô ở vị trí thấp nhất mà không ngả người ra sau quá nhiều.",
        "Từ từ thả tay để thanh kéo nâng lên cho đến khi cánh tay duỗi thẳng trong tầm kiểm soát.",
        "Lưu ý kỹ thuật: Luôn giữ ngực ưỡn cao",
        "Lưu ý kỹ thuật: Kéo mạnh cùi chỏ hướng xuống dưới",
        "Lưu ý kỹ thuật: Giữ thẳng cổ tay, không bẻ gập cổ tay"
      ],
      "breathing": [
        "Hít vào khi thanh kéo đi lên duỗi thẳng tay, thở ra khi kéo thanh cầm xuống ngực.",
        "Tránh: Ngả người ra sau quá nhiều làm biến thành động tác chèo lưng",
        "Tránh: Kéo thanh cầm ra phía sau gáy"
      ]
    }
  },

  # 28: 0738
  {
    "id": "0738",
    "stepsVi": {
      "prepare": [
        "Ngồi vào máy trượt nghiêng 45 độ và đặt ức của cả hai bàn chân lên mép dưới bàn đạp với gót chân thả tự do ngoài rìa.",
        "Đạp duỗi chân vừa đủ để đỡ bàn trượt và giữ đầu gối hơi chùng nhẹ."
      ],
      "execution": [
        "Hạ gót chân xuống bằng cách gập khớp cổ chân cho đến khi cảm thấy cơ bắp chân được kéo căng.",
        "Nhấn mạnh phần ức bàn chân để nhón gót chân lên cao hết mức có thể.",
        "Dừng lại 1 nhịp ở điểm cao nhất trong khi giữ chân luôn ổn định.",
        "Hạ gót chân xuống có kiểm soát trở về vị trí kéo căng ban đầu và lặp lại.",
        "Lưu ý kỹ thuật: Phát lực đạp qua phần ức bàn chân",
        "Lưu ý kỹ thuật: Nhón gót chân lên cao nhất có thể",
        "Lưu ý kỹ thuật: Kiểm soát quá trình hạ gót chân thật chậm rãi"
      ],
      "breathing": [
        "Hít vào khi hạ gót chân xuống, thở ra khi nhấn ức bàn chân nhón gót lên cao.",
        "Tránh: Gập và duỗi đầu gối thay vì chỉ chuyển động duy nhất ở khớp cổ chân",
        "Tránh: Đặt toàn bộ bàn chân lên bàn đạp khiến gót chân không thể hạ xuống sâu"
      ]
    }
  },

  # 29: 0740
  {
    "id": "0740",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh ghế ngồi và lắp mức tạ mong muốn.",
        "Ngồi với toàn bộ lưng và đầu áp sát đệm, đặt hai bàn chân mở rộng trên bàn đạp."
      ],
      "execution": [
        "Mở chốt an toàn và nắm chắc hai tay cầm bên hông ghế.",
        "Gập đầu gối để hạ bàn đạp xuống cho đến khi đùi tạo góc khoảng 90 độ hoặc sâu hơn một chút.",
        "Đạp mạnh qua gót chân để duỗi chân đẩy bàn đạp lên, nhưng tránh khóa cứng khớp gối.",
        "Lưu ý kỹ thuật: Phát lực đạp đẩy qua gót chân",
        "Lưu ý kỹ thuật: Giữ đầu gối luôn mở thẳng hàng với hướng mũi chân",
        "Lưu ý kỹ thuật: Tuyệt đối không khóa cứng khớp gối ở vị trí cao nhất"
      ],
      "breathing": [
        "Hít vào khi hạ bàn đạp xuống, thở ra khi đạp đẩy bàn đạp lên.",
        "Tránh: Để hai đầu gối sụp chụm vào bên trong",
        "Tránh: Cong tròn lưng dưới rời khỏi đệm ghế"
      ]
    }
  },

  # 30: 0743
  {
    "id": "0743",
    "stepsVi": {
      "prepare": [
        "Đứng vào bục máy trượt với lưng áp sát vào đệm tựa và hai vai đặt dưới đệm đòn gánh.",
        "Đặt hai bàn chân rộng bằng vai trên bàn đạp với mũi chân hơi xoay nhẹ ra ngoài, sau đó nắm chắc hai tay cầm."
      ],
      "execution": [
        "Mở chốt an toàn của khung trượt và hạ người xuống bằng cách gập gối và hông cho đến khi đùi song song với mặt sàn hoặc ở độ sâu tối đa mà bạn kiểm soát được.",
        "Giữ toàn bộ bàn chân bám chặt trên bàn đạp và đầu gối di chuyển theo hướng mũi chân.",
        "Đạp mạnh qua gót chân và giữa bàn chân để duỗi khớp gối và hông, đẩy khung trượt lên trên.",
        "Dừng lại ngay trước khi khớp gối bị khóa cứng, sau đó tiếp tục nhịp tập tiếp theo.",
        "Lưu ý kỹ thuật: Giữ toàn bộ lưng luôn áp sát vào đệm tựa",
        "Lưu ý kỹ thuật: Đầu gối luôn chuyển động theo hướng của mũi chân",
        "Lưu ý kỹ thuật: Đạp phân bổ lực đều khắp toàn bộ bàn chân"
      ],
      "breathing": [
        "Hít vào khi hạ khung trượt xuống, thở ra khi đạp đẩy khung trượt lên.",
        "Tránh: Đặt chân quá thấp khiến gót chân bị nhấc rời khỏi bàn đạp",
        "Tránh: Đầu gối bị sụp chụm vào trong suốt giai đoạn hạ người"
      ]
    }
  },

  # 31: 0750
  {
    "id": "0750",
    "stepsVi": {
      "prepare": [
        "Đặt thanh tạ đòn của khung máy trượt ngang qua phần lưng trên và đứng hai chân rộng bằng vai, đưa hai bàn chân hơi chếch ra phía trước đường trượt của thanh tạ.",
        "Mở khóa thanh tạ, gồng chặt cơ bụng, ưỡn ngực cao và mắt nhìn thẳng về phía trước."
      ],
      "execution": [
        "Đồng thời gập đầu gối và khớp hông để ngồi thẳng người xuống dưới có kiểm soát.",
        "Hạ người xuống cho đến khi đùi song song với mặt sàn hoặc thấp hơn một chút trong khi gót chân vẫn bám chặt trên sàn.",
        "Đạp mạnh qua giữa bàn chân và gót chân để đứng thẳng dậy cho đến khi gối và hông duỗi thẳng hoàn toàn.",
        "Đứng thẳng hoàn tất động tác, sau đó lặp lại cho nhịp tập tiếp theo.",
        "Lưu ý kỹ thuật: Luôn giữ ngực ưỡn cao",
        "Lưu ý kỹ thuật: Đầu gối di chuyển theo hướng của mũi chân",
        "Lưu ý kỹ thuật: Phát lực đạp đẩy qua gót chân"
      ],
      "breathing": [
        "Hít vào và gồng bụng trước khi hạ người xuống, thở ra khi đạp người đứng thẳng dậy.",
        "Tránh: Đặt chân ngay dưới thanh tạ khiến đầu gối bị đẩy nhô ra phía trước quá nhiều.",
        "Tránh: Nhấc gót chân rời khỏi sàn ở vị trí thấp nhất."
      ]
    }
  },

  # 32: 1393
  {
    "id": "1393",
    "stepsVi": {
      "prepare": [
        "Điều chỉnh độ cao của thanh tạ trên khung máy trượt ngang tầm vai.",
        "Bước vào dưới thanh tạ, đặt đòn tạ tựa lên phần cơ cầu vai trên và xoay mở khóa chốt an toàn."
      ],
      "execution": [
        "Đứng thẳng người với hai bàn chân mở rộng bằng hông hoặc bằng vai.",
        "Dùng lực từ phần ức bàn chân để nhón nâng gót chân lên cao thông qua chuyển động duỗi cổ chân.",
        "Dừng lại 1 nhịp ở đỉnh co rút, sau đó hạ gót chân xuống một cách chậm rãi có kiểm soát.",
        "Lưu ý kỹ thuật: Chỉ chuyển động duy nhất ở khớp cổ chân",
        "Lưu ý kỹ thuật: Giữ hai chân thẳng nhưng không khóa cứng khớp gối",
        "Lưu ý kỹ thuật: Kiểm soát chặt chẽ từng chuyển động"
      ],
      "breathing": [
        "Thở ra khi nhón gót chân lên, hít vào khi hạ gót chân xuống.",
        "Tránh: Nhún nảy lấy quán tính",
        "Tránh: Tập với biên độ chuyển động quá ngắn"
      ]
    }
  },

  # 33: 0752
  {
    "id": "0752",
    "stepsVi": {
      "prepare": [
        "Đặt hai bàn chân rộng bằng vai ngay bên dưới thanh đòn của khung máy trượt.",
        "Dùng hai tay nắm chặt thanh đòn ở vị trí ngay sát bên ngoài hai đầu gối."
      ],
      "execution": [
        "Đẩy hông ra sau và hạ thấp thân người xuống, luôn giữ ngực ưỡn cao.",
        "Duỗi khớp hông và đầu gối để kéo thanh đòn nâng lên theo đường ray dẫn hướng của máy.",
        "Hạ thanh đòn xuống vị trí ban đầu một cách chậm rãi có kiểm soát.",
        "Lưu ý kỹ thuật: Bản lề gập duỗi chủ yếu tại khớp hông",
        "Lưu ý kỹ thuật: Luôn giữ lưng thẳng tự nhiên",
        "Lưu ý kỹ thuật: Phát lực đạp đẩy qua gót chân"
      ],
      "breathing": [
        "Hít vào khi hạ thanh đòn xuống, thở ra khi kéo tạ nâng lên.",
        "Tránh: Cong tròn phần lưng dưới",
        "Tránh: Dùng lực cánh tay để kéo thay vì phát lực từ chân và hông"
      ]
    }
  },

  # 34: 0748
  {
    "id": "0748",
    "stepsVi": {
      "prepare": [
        "Cài đặt chốt chặn an toàn và lắp mức tạ thích hợp lên thanh đòn.",
        "Nằm ngửa bên dưới thanh đòn của khung máy trượt và đặt hai bàn chân mở rộng hơn vai lên giữa thanh đòn."
      ],
      "execution": [
        "Xoay hai bàn chân hướng lên trên để mở khóa thanh đòn tạ khỏi giá đỡ.",
        "Từ từ hạ thanh đòn xuống về phía thân người cho đến khi chân tạo góc khoảng 90 độ.",
        "Đạp thanh đòn lên trên bằng cách duỗi thẳng khớp gối và khớp hông.",
        "Lưu ý kỹ thuật: Luôn gồng chặt cơ bụng để giữ vững lưng dưới",
        "Lưu ý kỹ thuật: Đạp lực đồng đều ở cả hai bên bàn chân",
        "Lưu ý kỹ thuật: Đi trọn vẹn toàn bộ biên độ chuyển động"
      ],
      "breathing": [
        "Hít vào khi hạ thanh đòn xuống, thở ra khi đạp tạ đẩy lên.",
        "Tránh: Đặt vị trí bàn chân không chuẩn xác",
        "Tránh: Chỉ dùng lực từ mũi ngón chân để đạp tạ"
      ]
    }
  },

  # 35: 0765
  {
    "id": "0765",
    "stepsVi": {
      "prepare": [
        "Đặt ghế tập có tựa lưng dưới thanh đòn của khung máy trượt sao cho thanh đòn ngang tầm vai khi ngồi xuống.",
        "Ngồi thẳng người tựa lưng chắc chắn, đặt hai bàn chân phẳng trên sàn và nắm thanh đòn rộng hơn vai một chút với lòng bàn tay hướng ra trước."
      ],
      "execution": [
        "Xoay mở khóa thanh đòn và giữ tạ ngay phía trên ngực trên với cổ tay thẳng hàng phía trên cùi chỏ.",
        "Hạ thanh đòn theo phương thẳng đứng xuống cho đến khi ngang tầm cằm hoặc tầm vai.",
        "Đẩy thanh đòn thẳng lên trên cho đến khi hai cánh tay duỗi thẳng qua đầu.",
        "Hạ thanh đòn xuống có kiểm soát về vị trí bắt đầu và lặp lại.",
        "Kết thúc bài tập bằng cách duỗi thẳng tay ở đỉnh và xoay thanh đòn để cài lại vào móc an toàn.",
        "Lưu ý kỹ thuật: Giữ xương sườn không bị ưỡn đẩy nhô ra trước",
        "Lưu ý kỹ thuật: Đẩy tạ thẳng đứng lên trên theo ray trượt",
        "Lưu ý kỹ thuật: Giữ cổ tay luôn thẳng hàng ngay phía trên cùi chỏ"
      ],
      "breathing": [
        "Hít vào khi hạ thanh đòn xuống ngang vai, thở ra khi đẩy thanh đòn lên qua đầu.",
        "Tránh: Hạ thanh đòn xuống phía sau cổ gáy",
        "Tránh: Bành cùi chỏ ngang sang hai bên quá mức"
      ]
    }
  },

  # 36: 0128
  {
    "id": "0128",
    "stepsVi": {
      "prepare": [
        "Đứng vững chãi với hai bàn chân rộng bằng vai và hơi chùng nhẹ đầu gối.",
        "Mỗi tay cầm một đầu dây thừng với hai lòng bàn tay hướng vào nhau và cánh tay đặt trước người."
      ],
      "execution": [
        "Gồng chặt cơ bụng, nâng một tay lên đồng thời hạ tay kia xuống để bắt đầu tạo sóng dây.",
        "Tiếp tục đánh đổi tay thật nhanh và liên tục để tạo ra các đợt sóng chuyển động đều đặn dọc theo dây thừng.",
        "Duy trì tư thế chùng nhẹ gối và giữ vững thân người khi quật dây.",
        "Lưu ý kỹ thuật: Đánh tay nhanh và dứt khoát",
        "Lưu ý kỹ thuật: Luôn giữ ngực ưỡn cao",
        "Lưu ý kỹ thuật: Gồng cứng cơ bụng và cơ trung tâm"
      ],
      "breathing": [
        "Hít thở đều đặn trong suốt bài tập, thở ra theo từng nhịp dập tay và hít vào khi đổi tay liên tục.",
        "Tránh: Đứng thẳng đơ người với khớp gối bị khóa cứng",
        "Tránh: Đung đưa lắc lư toàn bộ thân người thay vì chỉ phát lực từ cánh tay"
      ]
    }
  },

  # 37: 0974
  {
    "id": "0974",
    "stepsVi": {
      "prepare": [
        "Gắn tay cầm chữ V hoặc tay cầm hẹp vào đầu dây cáp của máy kéo xô.",
        "Ngồi xuống ghế và cố định đùi chắc chắn dưới đệm tỳ."
      ],
      "execution": [
        "Nắm chặt tay cầm bằng kiểu nắm hai lòng bàn tay hướng vào nhau.",
        "Kéo tay cầm xuống chạm vào phần ngực trên, luôn giữ thân người thẳng đứng.",
        "Từ từ nhả tay cầm nâng lên đỉnh mà không khóa cứng khớp cùi chỏ.",
        "Lưu ý kỹ thuật: Kéo mạnh cùi chỏ hướng xuống dưới và ép vào trong",
        "Lưu ý kỹ thuật: Luôn giữ ngực ưỡn cao",
        "Lưu ý kỹ thuật: Không đung đưa ngả người ra phía sau"
      ],
      "breathing": [
        "Thở ra khi kéo tay cầm xuống, hít vào khi nhả tay đưa lên.",
        "Tránh: Ngả người ra sau quá mức",
        "Tránh: Dùng đà quán tính để giật tạ"
      ]
    }
  },

  # 38: 0154
  {
    "id": "0154",
    "stepsVi": {
      "prepare": [
        "Cài hai đầu tay cầm dây cáp ở vị trí ròng rọc thấp nhất và đứng vào chính giữa hai trụ cáp.",
        "Tay phải bắt chéo nắm tay cầm bên trái, tay trái nắm tay cầm bên phải, sau đó bước lên một bước nhỏ để tạo độ căng cho dây cáp."
      ],
      "execution": [
        "Hơi gập người về phía trước với đầu gối chùng nhẹ, giữ ngực ưỡn và lưng thẳng tự nhiên.",
        "Bắt đầu với hai cánh tay hướng chếch xuống và bắt chéo trước người, cùi chỏ hơi cong nhẹ.",
        "Kéo mở rộng hai cánh tay sang hai bên và ra sau theo một vòng cung rộng cho đến khi hai bàn tay ngang tầm vai.",
        "Siết chặt cơ vai sau và cơ lưng trên ở vị trí co rút tối đa.",
        "Nhả tay cầm từ từ về vị trí ban đầu mà không nhún vai hoặc thay đổi góc nghiêng của thân người.",
        "Lưu ý kỹ thuật: Dẫn hướng chuyển động bằng cùi chỏ",
        "Lưu ý kỹ thuật: Giữ cùi chỏ luôn cong nhẹ cố định",
        "Lưu ý kỹ thuật: Ngực ưỡn cao, giữ lưng luôn thẳng"
      ],
      "breathing": [
        "Hít vào khi nhả tay cầm trở về vị trí bắt đầu, thở ra khi kéo mở hai cánh tay sang ngang và ra sau.",
        "Tránh: Đứng thẳng người lên biến bài tập thành động tác kéo chèo xô",
        "Tránh: Gập và duỗi cùi chỏ liên tục trong suốt nhịp tập"
      ]
    }
  },

  # 39: 0175
  {
    "id": "0175",
    "stepsVi": {
      "prepare": [
        "Gắn tay cầm dây thừng vào ròng rọc ở vị trí cao nhất và quỳ gối hướng mặt vào máy kéo cáp.",
        "Nắm hai đầu dây thừng và giữ hai bàn tay áp sát hai bên tai với cùi chỏ hơi hướng ra trước."
      ],
      "execution": [
        "Gồng chặt cơ bụng và giữ khớp hông cố định thẳng phía trên đầu gối.",
        "Cuộn lồng ngực gập về phía xương chậu và kéo hai cùi chỏ hướng xuống về phía đùi.",
        "Dừng lại 1 nhịp ở vị trí thấp nhất trong khi vẫn duy trì độ căng siết trên dây thừng.",
        "Từ từ mở cột sống đưa người trở về vị trí bắt đầu mà không để bánh tạ va đập vào nhau.",
        "Lưu ý kỹ thuật: Cuộn sườn về phía xương hông để ép chặt cơ bụng",
        "Lưu ý kỹ thuật: Giữ phần hông cố định, không di chuyển",
        "Lưu ý kỹ thuật: Chủ động cuộn tròn cột sống thay vì gập bản lề hông"
      ],
      "breathing": [
        "Thở ra khi cuộn người gập bụng xuống, hít vào khi từ từ đưa thân người trở về vị trí ban đầu.",
        "Tránh: Dùng lực cánh tay kéo dây thừng xuống thay vì cuộn cơ bụng",
        "Tránh: Đẩy mông ngồi thụt lùi ra sau biến bài tập thành động tác gập hông"
      ]
    }
  },

  # 40: 0178
  {
    "id": "0178",
    "stepsVi": {
      "prepare": [
        "Cài đặt chốt ròng rọc dây cáp ở vị trí thấp nhất và đứng nghiêng một bên so với máy.",
        "Dùng bàn tay phía ngoài nắm lấy tay cầm cáp và để cánh tay buông tự nhiên bên cạnh đùi."
      ],
      "execution": [
        "Đứng thẳng người với cùi chỏ hơi cong nhẹ và gồng chặt cơ bụng.",
        "Nâng cánh tay dang rộng sang bên cho đến khi bàn tay ngang tầm vai.",
        "Dừng lại 1 nhịp mà không nhún vai lên.",
        "Hạ tay cầm xuống từ từ có kiểm soát trở về vị trí ban đầu.",
        "Lưu ý kỹ thuật: Dẫn hướng chuyển động bằng cùi chỏ",
        "Lưu ý kỹ thuật: Dừng lại khi tay đạt ngang tầm vai",
        "Lưu ý kỹ thuật: Giữ các cơ vùng cổ luôn thư giãn thả lỏng"
      ],
      "breathing": [
        "Thở ra khi nâng tay cầm sang ngang, hít vào khi hạ tay cầm trở xuống.",
        "Tránh: Nhún vai lên sát tai khi nâng tạ",
        "Tránh: Đung đưa thân người để lấy đà giật tạ lên"
      ]
    }
  },

  # 41: 0186
  {
    "id": "0186",
    "stepsVi": {
      "prepare": [
        "Gắn tay cầm dây thừng vào ròng rọc cáp thấp và đặt một chiếc ghế tập nằm phẳng thẳng hàng với ròng rọc.",
        "Nằm ngửa trên ghế với đầu hướng về phía máy cáp và nắm dây thừng bằng kiểu nắm lòng bàn tay hướng vào nhau."
      ],
      "execution": [
        "Đẩy duỗi thẳng hai tay giữ dây thừng ngay phía trên ngực.",
        "Giữ cố định cánh tay trên và gập cùi chỏ để hạ dây thừng về phía trán.",
        "Dừng lại 1 nhịp khi cùi chỏ gập sâu.",
        "Duỗi thẳng cùi chỏ để đưa dây thừng trở lại vị trí bắt đầu phía trên ngực.",
        "Lưu ý kỹ thuật: Giữ hai cùi chỏ luôn khép gọn vào trong",
        "Lưu ý kỹ thuật: Cánh tay trên giữ cố định không đung đưa",
        "Lưu ý kỹ thuật: Chỉ chuyển động duy nhất tại khớp cùi chỏ"
      ],
      "breathing": [
        "Hít vào khi hạ dây thừng về phía trán, thở ra khi duỗi thẳng cùi chỏ đẩy dây về vị trí bắt đầu.",
        "Tránh: Để hai cùi chỏ bành rộng sang hai bên",
        "Tránh: Trôi cánh tay trên ra sau biến bài tập thành động tác vớt tạ"
      ]
    }
  },

  # 42: 0190
  {
    "id": "0190",
    "stepsVi": {
      "prepare": [
        "Đứng cạnh máy kéo cáp và dùng một tay nắm lấy tay cầm đơn với lòng bàn tay hướng lên.",
        "Bước ra ngoài một bước cho đến khi dây cáp căng đều, sau đó đứng thẳng người với cùi chỏ khép sát bên hông."
      ],
      "execution": [
        "Gập cùi chỏ cuốn tay cầm lên trên mà không để cánh tay trên bị trôi ra phía trước.",
        "Nâng tay cầm lên cho đến khi cẳng tay áp sát cơ tay trước, sau đó siết chặt bắp tay trong 1 nhịp.",
        "Hạ tay cầm xuống từ từ cho đến khi cánh tay duỗi thẳng trong khi vẫn duy trì độ căng của dây cáp.",
        "Hoàn thành toàn bộ số lần lặp cho một tay, sau đó đổi sang tay còn lại.",
        "Lưu ý kỹ thuật: Giữ cùi chỏ luôn ghim chặt bên hông",
        "Lưu ý kỹ thuật: Giữ lòng bàn tay luôn ngửa hướng lên trên",
        "Lưu ý kỹ thuật: Luôn đứng thẳng người và ổn định thân mình"
      ],
      "breathing": [
        "Thở ra khi cuốn tay cầm lên, hít vào khi hạ tay cầm xuống.",
        "Tránh: Cùi chỏ bị vung đưa ra phía trước trong khi cuốn tạ",
        "Tránh: Nhún vai lên sát tai khi nâng tạ"
      ]
    }
  },

  # 43: 0162
  {
    "id": "0162",
    "stepsVi": {
      "prepare": [
        "Gắn tay cầm đơn vào ròng rọc thấp và đứng quay lưng về phía máy tập.",
        "Một tay nắm lấy tay cầm cáp, cánh tay buông tự nhiên bên cạnh đùi."
      ],
      "execution": [
        "Giữ cánh tay thẳng, nâng tay ra phía trước lên ngang tầm vai.",
        "Dừng lại 1 nhịp ở điểm cao nhất.",
        "Hạ tay xuống từ từ về vị trí ban đầu và lặp lại động tác.",
        "Lưu ý kỹ thuật: Luôn gồng chặt cơ bụng để giữ vững thân người",
        "Lưu ý kỹ thuật: Nâng bằng lực co cơ vai, không kéo giật bằng bàn tay",
        "Lưu ý kỹ thuật: Tuyệt đối không đung đưa thân người lấy đà"
      ],
      "breathing": [
        "Thở ra khi nâng tay lên, hít vào khi hạ tay xuống.",
        "Tránh: Dùng đà quán tính để giật nâng tạ",
        "Tránh: Nhún vai lên sát tai khi thực hiện động tác"
      ]
    }
  },

  # 44: 2616
  {
    "id": "2616",
    "stepsVi": {
      "prepare": [
        "Gắn một tay cầm đơn vào ròng rọc cáp ở vị trí cao nhất.",
        "Ngồi hoặc đứng thẳng, một tay vươn thẳng qua đầu nắm lấy tay cầm."
      ],
      "execution": [
        "Ổn định toàn bộ thân người và gồng chặt cơ bụng.",
        "Kéo tay cầm xuống ngang tầm vai hoặc ngực trên.",
        "Dừng lại 1 nhịp, sau đó từ từ nhả tay cầm đưa trở lên.",
        "Lưu ý kỹ thuật: Kéo cùi chỏ hướng xuống dưới và ép sát vào trong",
        "Lưu ý kỹ thuật: Không nhún vai khi kéo tạ",
        "Lưu ý kỹ thuật: Giữ thân người luôn thẳng đứng"
      ],
      "breathing": [
        "Thở ra trong khi kéo tạ xuống, hít vào khi nhả tay đưa tạ lên.",
        "Tránh: Ưỡn cong lưng quá mức",
        "Tránh: Để khớp vai bị cuộn đổ về phía trước"
      ]
    }
  }
]

# Validation
with open('/Users/cp/code/ai/shaken/scripts/en_batch_3.json') as f:
    en_data = json.load(f)

print(f"Total EN exercises: {len(en_data)}")
print(f"Total VI exercises: {len(DATA)}")
assert len(en_data) == len(DATA), "Counts mismatch!"

en_dict = {x['id']: x for x in en_data}

ENGLISH_WORDS_TO_CHECK = [
    r'\bbarbell\b', r'\bdumbbell\b', r'\bbench\b', r'\brack\b', r'\bsquat\b',
    r'\bcurl\b', r'\bcable\b', r'\bcore\b', r'\bhamstring\b', r'\bhamstrings\b',
    r'\bquad\b', r'\bquads\b', r'\bglute\b', r'\bglutes\b', r'\blat\b', r'\blats\b',
    r'\btrap\b', r'\btraps\b', r'\bpec\b', r'\bpecs\b', r'\bdelt\b', r'\bdelts\b',
    r'\btricep\b', r'\btriceps\b', r'\bbicep\b', r'\bbiceps\b', r'\bpress\b',
    r'\bdeadlift\b', r'\brow\b', r'\bpulldown\b', r'\bextension\b', r'\bhack\b',
    r'\bsmith\b', r'\bsled\b', r'\bform cue\b', r'\bavoid\b', r'\brep\b', r'\breps\b',
    r'\blockout\b', r'\block out\b', r'\broller\b', r'\bpivot\b', r'\bseat\b', r'\bpad\b'
]

errors = []
for i, vi_item in enumerate(DATA):
    vid = vi_item['id']
    if vid not in en_dict:
        errors.append(f"ID {vid} not in EN batch!")
        continue
    en_item = en_dict[vid]
    
    # check keys
    if "stepsVi" not in vi_item:
        errors.append(f"[{vid}] missing stepsVi")
        continue
    
    for section in ["prepare", "execution", "breathing"]:
        en_sec = en_item["steps"].get(section, [])
        vi_sec = vi_item["stepsVi"].get(section, [])
        if len(en_sec) != len(vi_sec):
            errors.append(f"[{vid}] Section {section} length mismatch: EN={len(en_sec)}, VI={len(vi_sec)}")
            
        # check Form cue -> Lưu ý kỹ thuật
        for line_idx, (en_line, vi_line) in enumerate(zip(en_sec, vi_sec)):
            if en_line.startswith("Form cue:"):
                if not vi_line.startswith("Lưu ý kỹ thuật:"):
                    errors.append(f"[{vid}][{section}][{line_idx}] Expected 'Lưu ý kỹ thuật:', got '{vi_line}'")
            elif en_line.startswith("Avoid:"):
                if not vi_line.startswith("Tránh:"):
                    errors.append(f"[{vid}][{section}][{line_idx}] Expected 'Tránh:', got '{vi_line}'")
            
            # check English words
            for pat in ENGLISH_WORDS_TO_CHECK:
                if re.search(pat, vi_line, re.IGNORECASE):
                    errors.append(f"[{vid}][{section}][{line_idx}] Leaked English '{pat}': '{vi_line}'")

if errors:
    print(f"Found {len(errors)} errors:")
    for e in errors:
        print("  -", e)
    exit(1)
else:
    print("ALL 45 EXERCISES PASSED VALIDATION PERFECTLY!")
    out_path = '/Users/cp/code/ai/shaken/scripts/vi_batch_3.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(DATA, f, indent=2, ensure_ascii=False)
    print(f"Saved to {out_path}")
