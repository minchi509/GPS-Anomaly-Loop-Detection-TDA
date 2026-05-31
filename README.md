# Project 6: Phát hiện vòng lặp bất thường trong hành trình GPS

Project này tự động sinh và phân tích các kịch bản quỹ đạo GPS giả lập có nhiễu Gaussian sigma = 0.05:

- `KC1`: Đi thẳng + 1 vòng tròn bán kính 1
- `KC2`: Đi thẳng + hình số 8 (2 vòng)
- `KC3`: Negative control (chỉ đi thẳng kèm nhiễu)

## Cài thư viện

```bash
pip install -r requirements.txt
python -m pip install -r requirements.txt

```

## Chạy project

Đảm bảo tất cả các file code nằm cùng thư mục, sau đó chạy:

```bash
python main.py

```

## Output

Kết quả được lưu trong 2 thư mục `results` và `figures`, gồm:

* `h1_persistence_results.csv`: bảng chi tiết các vòng lặp (birth, death, persistence, phân loại tín hiệu/nhiễu)
* `centroid_estimations.csv`: tọa độ tâm và ước lượng bán kính của các vòng lặp bền vững
* `KC1_barcode.png`, `KC2_barcode.png`, `KC3_barcode.png`: biểu đồ barcode H1
* `KC1_persistence_diagram.png`, `KC2_persistence_diagram.png`, `KC3_persistence_diagram.png`: biểu đồ persistence diagram
* `KC1_gps_map.png`, `KC2_gps_map.png`, `KC3_gps_map.png`: bản đồ hành trình GPS có tô màu vòng lặp và vị trí tâm

## Lưu ý

Code tự cài đặt Vietoris--Rips filtration và tính H1 persistent homology để phát hiện vòng lặp.
Việc trích xuất tâm và bán kính được thực hiện thực nghiệm thông qua tập đỉnh (vertices) của chu trình.
Hệ thống sử dụng threshold = 0.15 để phân biệt vòng lặp thực sự (có chủ đích) và vòng lặp nhỏ do nhiễu GPS tạo ra.
