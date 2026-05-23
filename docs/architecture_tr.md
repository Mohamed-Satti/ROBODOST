# ROBODOST Sistem Mimarisi

[English](architecture.md) | [Türkçe](architecture_tr.md)

Hedef Sistem: **NVIDIA Jetson Orin Nano Super (8GB)**  
Ara Katman (Middleware): **ROS2 Humble**

## 1. Üst Düzey Düğüm (Node) Düzeni

Mimari açıkça beş ana hesaplama alanına ayrılmıştır. İletişim, `robodost_msgs` içinde yapılandırılmış özel mesajlar aracılığıyla eşzamansız (asynchronous) yayınla-abone ol (publish-subscribe) modelini izler.

1. **HRI (İnsan-Robot Etkileşimi)**: Sesi yakalar -> Silero VAD'yi tetikler -> `faster-whisper-tiny` (INT8) modeline yönlendirir -> metni çözer. Sistem çıktısı, düşük algısal gecikme için metin parçalarını doğrudan Piper streaming TTS'e eşler.
2. **Görsel Ardışık Düzen (CV)**: USB kare alımı -> TensorRT üzerinden YOLOv8-nano Nesne Tespiti. MediaPipe, 20 kelimelik izole Türk İşaret Dili komut sözlüğü için jestleri izler.
3. **Zeka Merkezi (LLM)**: Jenerik bir Çıkarım Motoru (quantized 3B yerel model veya OpenAI sarmalayıcısı arasında geçiş yapılabilir) aracılığıyla metin analizini birleştirir.
4. **Çekirdek Sistem (Entegrasyon)**: Sürekli Bağlam Anlık Görüntüsü (Context Snapshot) ile robotun gerçekliğini tanımlar, FSM yürütmesini denetler ve Watchdog aracılığıyla indirgenmiş (degraded) geri dönüşleri zorlar.
5. **Mekatronik**: Doğrudan Arduino Nano denetleyicisine donanım düzeyinde gerçek zamanlı PID yürütme yüklerini ileten Seri UART köprüsü.

## 2. Eşzamansız Bağlam Deposu (Context Store)

Görsel ve işitsel çapraz referansları değerlendirirken CPU kilitlenmelerini önlemek için `context_store_node` bellekte **Yalnızca Eklenebilir Bir Halka Tamponu (Append-Only Ring Buffer)** (standart bir Python `deque`) tutar.
- 2Hz hızında `/context/snapshot` üzerinde birleştirilmiş bir anlık görüntü (Son 3 konuşma sırası + En Son Görsel Sınırlayıcı Kutular + Sistem Telemetrisi) oluşturur.
- LLM, bir kullanıcı istemi (prompt) aldığında kamera döngüsünü asla bloke etmeden bu ortam anlık görüntüsünü dinamik olarak değerlendirir.

## 3. Orkestratör FSM

Orkestratör, robotun fiziksel olarak hangi eylemleri gerçekleştirmesine izin verildiğini tanımlar.
* **Durum Makinesi Akışı**: `BOŞTA (IDLE) -> DİNLİYOR (LISTENING) -> İŞLİYOR (PROCESSING) -> YÜRÜTÜYOR (EXECUTING) -> BOŞTA (IDLE)`
* **Öncelik Alma/Araya Girme (Preemption/Barge-in)**: `YÜRÜTÜYOR` durumundayken (Robot konuşurken/hareket ederken) görsel bir uyandırma kelimesi veya işitsel bir anahtar kelime araya girerse, mevcut rutini bırakır, TTS motorunu susturur ve Mekatroniği durdurur.

## 4. Donanım Geri Dönüş Alt Sistemleri (Watchdog)

Katı 8GB paylaşılan RAM sınırını ele alan sistem, basamaklı arızaları önlemek için kalp atışı (heartbeat) paketlerini izler:
- **Mod 0 (Tam Yapay Zeka)**: Llama/Qwen + YOLO + HRI Çevrimiçi.
- **Mod 1 (Bulut Geri Dönüşü)**: Yerel GPU RAM kullanımı %90'ı aşarsa veya yerel düğüm çökerse çıkarım yükünü Bulut Uç Noktasına (Cloud Endpoint) kaydırır.
- **Mod 2 (Minimum Hayatta Kalma)**: Görüş ve LLM devre dışı; Sistem yalnızca sabit kodlu Regex ASR komutlarına (örn. "DUR") güvenir.

## 5. Çift Yollu Acil Durum Önceliği

1. **Donanım Yolu**: Analog fiziksel kırmızı düğme, MOSFET motor sürücülerine giden harici Li-ion pil gücünü Röle modülü aracılığıyla doğrudan keser. Bu anında durmayı garanti eder.
2. **Yazılım Yolu**: Düğmeyi tetiklemek aynı anda doğrudan Jetson GPIO pininde bir kesme (interrupt) kaydeder. `emergency_node` anında `/emergency/status = true` işaretini verir. Orkestratör bunu küresel olarak engeller ve tüm aktif hareket kuyruklarını iptal eder.
