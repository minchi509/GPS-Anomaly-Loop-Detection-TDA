# GPS-Anomaly-Loop-Detection-TDA
# Phát hiện vòng lặp bất thường trong hành trình GPS sử dụng Phân tích dữ liệu Topo (TDA)

## 📌 Tổng quan đề tài
Dự án này là nội dung nghiên cứu và triển khai thực nghiệm thuộc môn **Giải tích ma trận và Topo tính toán (Học kỳ 252)** – Trường Đại học Bách Khoa TP.HCM.

Mục tiêu của đề tài là ứng dụng kỹ thuật **Phân tích dữ liệu Topo (Topological Data Analysis - TDA)**, cụ thể là quy trình lọc *Vietoris–Rips (Vietoris–Rips filtration)* và cấu trúc *Đồng điều bền vững (Persistent Homology)* kết hợp Giải tích ma trận để tự động phát hiện, định vị các vòng lặp dị thường hoặc hành vi di chuyển bất thường từ tập dữ liệu tọa độ GPS có nhiễu lớn. Phương pháp này hỗ trợ đắc lực cho các hệ thống giám sát hành trình vận tải, tối ưu hóa logistics và phát hiện gian lận lộ trình.

---

## 👥 Thành viên thực hiện
* **Giáo viên hướng dẫn:** TS. Nguyễn Hữu Hiệp
* **Lớp:** 101 — **Nhóm:** 6 — **Ngành:** Khoa học dữ liệu
* **Danh sách nhóm:**
  1. Nguyễn Minh Trí (MSSV: 2413637)
  2. Nguyễn Huỳnh Lâm (MSSV: 2411841)
  3. Nguyễn Minh Nguyên (MSSV: 2412357)
  4. Nguyễn Ngọc Ánh (MSSV: 2410169)
  5. Nguyễn Ngọc Nhi (MSSV: 2412506)

---

## 🔬 Thuật toán & Phương pháp cốt lõi
Hệ thống xử lý dòng luồng dữ liệu không gian qua các giai đoạn toán học nghiêm ngặt:
1. **Mô phỏng Quỹ đạo & Nhiễu:** Xây dựng dữ liệu hành trình dựa trên 3 kịch bản thực nghiệm phức tạp tích hợp nhiễu ngẫu nhiên Gaussian ($\sigma = 0.05$).
2. **Xây dựng phức hợp Simplex:** Cài đặt thủ công thuật toán *Vietoris–Rips filtration* nhằm quét không gian dữ liệu đám mây điểm theo các bán kính thực nghiệm tăng dần ($\epsilon$).
3. **Giải tích ma trận đồng điều:** Can thiệp sâu vào ma trận biến đổi bậc cao ($V$) để bóc tách tính toán các đặc trưng số Betti thế hệ $H_0$ (thành phần liên thông) và $H_1$ (vòng lặp không gian).
4. **Ước lượng thông số hình học:** Theo dõi thời gian xuất hiện (Birth) và biến mất (Death) của vòng qua biểu đồ mã vạch (Barcode) để lọc nhiễu nền, từ đó dùng giải tích số lượng ước tính tọa độ tâm (Centroid) và bán kính vòng lặp dị thường.

---

## 📂 Cấu trúc thư mục dự án
```text
├── data/
│   └── gps_simulated_paths/     # Thư mục chứa các tệp tọa độ GPS kịch bản mẫu
├── figures/
│   ├── barcode_plots.png        # Đồ thị biểu diễn Persistence Barcode (H0 & H1)
│   ├── persistence_diagrams.png # Đồ thị Persistence Diagram (Birth vs Death)
│   └── gps_loop_maps.png        # Bản đồ hành trình thực tế kèm vị trí tâm dị thường tìm được
├── results/
│   ├── h1_persistence_results.csv # Bảng thông số Birth, Death và phân loại cấu trúc vòng
│   └── centroid_estimations.csv   # Tọa độ tâm và bán kính ước lượng của các vòng lặp
├── src/
│   ├── main.py                  # Tập lệnh khởi chạy toàn bộ quy trình thực nghiệm
│   ├── tda_engine.py            # Module cài đặt thuật toán Vietoris-Rips và ma trận boundary
│   └── geometry_solver.py       # Thuật toán tính toán hình học, ước lượng tâm và bán kính
├── README.md                    # File hướng dẫn dự án (tệp hiện tại)
└── requirements.txt             # Danh sách các thư viện Python cần cài đặt
