# ROS2 Çalışma Alanı Dosya Yapısı

[English](file_structure.md) | [Türkçe](file_structure_tr.md)

ROBODOST, izole geliştirmeyi sağlamak, kod birleştirme çakışmalarını önlemek ve düğüm kümelerinin sistem bellek kısıtlamalarına göre dinamik olarak ölçeklenmesine olanak tanımak için **"Takım Başına Paket" ("Package-per-Team")** tasarımı kullanır.

## Dizin Özeti

```text
robodost_ws/
├── src/
│   ├── robodost_msgs/                 # Küresel API Sözleşmesi (Takım Entegrasyonu)
│   │   ├── msg/                       # Özel konular (VisionUpdate, SpeechText)
│   │   └── srv/                       # Özel servisler (LLMQuery)
│   │
│   ├── robodost_hri/                  # Takım C: Ses ve Kullanıcı Arayüzü
│   │   ├── core/                      # Saf Python Sanal Alanı (ROS Yok)
│   │   ├── wakeword_node.py
│   │   ├── asr_node.py
│   │   └── tts_node.py
│   │
│   ├── robodost_vision/               # Takım B: Kamera, YOLO, OCR, MediaPipe
│   │   ├── core/                      # Saf Python Sanal Alanı (ROS Yok)
│   │   ├── yolo_node.py
│   │   └── sign_language_node.py
│   │
│   ├── robodost_llm/                  # Takım A: Akıl Yürütme ve Metin Motoru
│   │   ├── core/                      # Saf Python Sanal Alanı (ROS Yok)
│   │   ├── llm_node.py                # Jenerik OpenAI İstemci Arayüzü
│   │   └── config/llm_params.yaml     # Mod geçişi (use_cloud=true/false)
│   │
│   ├── robodost_core/                 # Sistem Entegrasyonu (Beyin Sapı)
│   │   ├── core/                      # Saf Python Sanal Alanı (ROS Yok)
│   │   ├── orchestrator_node.py       # FSM Eylem Motoru
│   │   ├── context_store_node.py      # Anlık Görüntü (Snapshot) Birleştirici
│   │   └── watchdog_node.py           # Kalp Atışı İndirgenmiş Modlar Kurulumu
│   │
│   ├── robodost_mechatronics/         # Takım E: Arduino İletişimi ve Kinematik
│   │   ├── hardware_bridge_node.py
│   │   └── firmware/arduino_controller/
│   │
│   └── robodost_bringup/              # Başlatma Orkestrasyonu
│       ├── launch/system_local.launch.py
│       ├── launch/system_full.launch.py
│       └── launch/system_minimal.launch.py
│
├── system_deploy/                     # Bağımlılık yönetimi ve UDEV betikleri
└── docs/                              # Proje Mimari Belgeleri
```

## Neden bu spesifik çerçeve?

1. **`robodost_msgs` Bağımlılık Çapası**: Çapraz takım bağımlılığı. Karmaşık kodlama başlamadan önce takımlar, bu `*.msg` şemalarındaki değişken dizileri üzerinde karşılıklı olarak anlaşmalıdır. Bu, Takım A'nın, B takımının geri kalanını geliştirmesini beklerken sahte çıktılı (mocked) `yolo_node.py` yazmasını sağlar.
2. **Saf Python Çekirdek Mantığı (`core/`)**: Yerel Python mantığını (örn. Whisper, YOLO modelleri) ROS ara katman yazılımı sarmalayıcısından (wrapper) kesinlikle ayırıyoruz. Geliştiriciler, ROS `*_node.py` sarmalayıcısına köprü kurmadan *önce* ilgili paketin `core/` alt klasörü içindeki Windows dizüstü bilgisayarlarında (örneğin `speech_pipeline.py` gibi) sahte orkestratör ardışık düzenlerini kullanarak mantıklarını yerel olarak oluşturur ve test ederler.
3. **Başlatma Birleştirilebilirliği (Launch Composability)**: `robodost_bringup` paketi küresel şef olarak davranır. Belirgin başlatma parametreleri (`system_local.launch.py`) yazarak, hafif testler veya ağır hizmet tipi derecelendirme gösterileri için özel olarak tasarlanmış, tamamen izole edilmiş operasyonel kapsamlar oluşturuyoruz.
