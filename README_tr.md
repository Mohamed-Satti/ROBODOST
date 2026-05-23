# 🤖 ROBODOST

**Engelli Kullanıcılar İçin Refakatçi Robot (Tüm Yaş Grupları)**

[English](README.md) | [Türkçe](README_tr.md)

ROBODOST, NVIDIA Jetson Orin Nano Super üzerinde ROS2 Humble kullanılarak gerçek zamanlı etkileşim için oluşturulmuş, yerel olarak çalışan, çok modlu bir refakatçi robottur. Güvenlik ve erişilebilirlik merkezinde tasarlanmış olup, Türk işaret dili işlemeyi, duyarlı konuşma ardışık düzenlerini ve fiziksel mekatronik kontrolü destekler.

## 📖 Temel Özellikler
* **Yerel Öncelikli Yapay Zeka**: Kompakt 3B parametreli nicemlenmiş (quantized) bir LLM'i (llama.cpp aracılığıyla) tamamen uçta (on-edge) çalıştırır.
* **Çok Modlu Bağlam**: İşitsel girdileri (Whisper ASR) ve görsel bağlamı (YOLOv8 & MediaPipe) birleştirerek anlık bağlamsal bir anlık görüntü (snapshot) oluşturur.
* **Çift Yollu Acil Durum Güvenliği**: Yazılım düzeyinde olay bastırma ile anında birleştirilmiş donanım düzeyinde güç kesintisi.
* **Erişilebilirlik Odaklı**: İşitme engelli kullanıcılar için "Görsel Uyandırma Kelimeleri" ve sürekli yüz ifadesi takibi etkileşimleri.

## 📂 Dokümantasyon Merkezi
Robotik ardışık düzeninin tam bir dökümü için `docs/` dizinindeki belgelere başvurun:
- [Sistem Mimarisi](docs/architecture_tr.md) - Düğüm (node) eşleme, veri akışları ve güvenli yürütme ardışık düzeni.
- [Çalışma Alanı ve Dosya Yapısı](docs/file_structure_tr.md) - ROS2 paketlerinde ve kaynak dosyalarında gezinme.

## 🚀 Hızlı Başlangıç (Geliştirme)

### Windows / Yerel Yapay Zeka Testi (ROS Yok)
Standart yapay zeka ardışık düzen (pipeline) mantığını dizüstü bilgisayarınızda yerel olarak hızlı bir şekilde test etmek için herhangi bir paketin `core/` klasörüne (ör. `src/robodost_hri/robodost_hri/core/`) gidin. Bunlar, zorlu yapay zeka ardışık düzenlerini (YOLO ve Whisper gibi) ROS ağ kısıtlamalarından ayıran Saf-Python (Pure-Python) sanal alanları işlevi görür. Mantığı ROS 2 düğümlerine taşımadan önce, oluşturduğunuz yerelleştirilmiş ardışık düzen komut dosyalarını (`speech_pipeline.py` veya `vision_pipeline.py` gibi) kullanarak sanal ortamınızı yerel olarak çalıştırın ve test edin.

### Tam Sistem Dağıtımı (ROS 2 / Jetson)
1. Dağıtım yardımcı programı (deployment utility) klasörüne gidin:
   ```bash
   cd system_deploy/
   ```
2. Gerekli ROS2 bağımlılıklarını ve Python paketlerini kurun:
   ```bash
   ./install_deps.sh
   ```
3. Donanım USB takma adlarını başlatın (Sadece Linux/Jetson):
   ```bash
   sudo ./create_udev_rules.sh
   ```
4. ROS2 çalışma alanını yerel olarak derleyin:
   ```bash
   cd ~/robodost_ws
   colcon build --symlink-install
   source install/setup.bash
   ```
5. Birincil yığın (stack) testini başlatın:
   ```bash
   ros2 launch robodost_bringup system_local.launch.py
   ```
