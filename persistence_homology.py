import numpy as np
import csv
import os


# HÀM PHỤ TRỢ: Tính boundary (mặt biên) của một simplex.
def _boundary_of(simplex: tuple) -> list[tuple]:
    if len(simplex) <= 1:
        return []
    faces = []
    for i in range(len(simplex)):
        face = simplex[:i] + simplex[i + 1:]
        faces.append(tuple(sorted(face)))
    return faces


# HÀM CHÍNH: TÍNH PERSISTENT HOMOLOGY H1
def compute_persistence(rips_tree) -> list[tuple[float, float]]:
    # BƯỚC 1: Lấy tất cả simplex từ cây và sắp xếp theo thứ tự filtration
    tat_ca_simplex = sorted(
        rips_tree.get_simplexes(),
        key=lambda x: (x[1], len(x[0]) - 1)
    )

    # BƯỚC 2: Đánh số thứ tự cho từng simplex (dùng để tra cứu nhanh)
    simplex_to_idx = {
        simplex: i
        for i, (simplex, filt_val) in enumerate(tat_ca_simplex)
    }

    # BƯỚC 3: Xây dựng boundary matrix R (ma trận biên)
    R: dict[int, set] = {}
    for i, (simplex, filt_val) in enumerate(tat_ca_simplex):
        col = set()
        for face in _boundary_of(simplex):
            if face in simplex_to_idx:
                col.add(simplex_to_idx[face])
        R[i] = col

    # BƯỚC 4: Khởi tạo ma trận V — dùng để truy vết representative cycle.
    V: dict[int, set] = {i: {i} for i in range(len(tat_ca_simplex))}

    # BƯỚC 5: Khử cột boundary matrix R (Column Reduction) — cập nhật V song song
    pivot_to_col: dict[int, int] = {}

    for j in range(len(tat_ca_simplex)):
        col_R = R[j].copy()
        col_V = V[j].copy()

        while col_R:
            pivot = max(col_R)
            if pivot not in pivot_to_col:
                # Đây là pivot mới — lưu lại và ghi kết quả vào R, V
                pivot_to_col[pivot] = j
                R[j] = col_R
                V[j] = col_V
                break
            else:
                # Cộng (XOR) với cột đã có pivot trùng — cập nhật cả R lẫn V
                k = pivot_to_col[pivot]
                col_R = col_R.symmetric_difference(R[k])
                col_V = col_V.symmetric_difference(V[k])
        else:
            R[j] = set()
            V[j] = col_V

    # BƯỚC 6: Đọc kết quả persistence pairs H1 và truy vết representative cycle
    h1_pairs: list[tuple[float, float, frozenset]] = []

    for pivot_row, col_j in pivot_to_col.items():
        simplex_hang, filt_hang = tat_ca_simplex[pivot_row]
        simplex_cot, filt_cot = tat_ca_simplex[col_j]
        dim_hang = len(simplex_hang) - 1
        dim_cot = len(simplex_cot) - 1

        if dim_hang == 1 and dim_cot == 2:
            birth = float(filt_hang)
            death = float(filt_cot)
            if death > birth:
                cycle_edges: set = set()
                for v_idx in V[col_j]:
                    s_v, _ = tat_ca_simplex[v_idx]
                    if len(s_v) - 1 == 2:  # chỉ xét 2-simplex trong V
                        for face in _boundary_of(s_v):
                            if face in simplex_to_idx:
                                if face in cycle_edges:
                                    cycle_edges.remove(face)
                                else:
                                    cycle_edges.add(face)

                # Thu thập tất cả đỉnh từ các cạnh trong cycle
                cycle_vertices: set = set()
                for edge in cycle_edges:
                    for v in edge:
                        cycle_vertices.add(v)

                # Fallback: nếu cycle rỗng (hiếm gặp), dùng đỉnh của death simplex
                if not cycle_vertices:
                    cycle_vertices = set(simplex_cot)

                h1_pairs.append((birth, death, frozenset(cycle_vertices)))

    return h1_pairs


# HÀM MỚI 1: classify_pairs — tách thật / nhiễu, gán pair_id
def classify_pairs(
    pairs: list[tuple[float, float, frozenset]],
    threshold: float = 0.15
) -> dict:
    all_sorted = sorted(pairs, key=lambda x: -(x[1] - x[0]))
    significant = []
    noise = []
    for pair_id, (birth, death, vertices) in enumerate(all_sorted):
        persistence = death - birth
        record = {
            "pair_id":        pair_id,
            "birth":          round(birth, 6),
            "death":          round(death, 6),
            "persistence":    round(persistence, 6),
            "is_significant": persistence > threshold,
            "threshold":      threshold,
            "vertices":       vertices   # frozenset đỉnh của TOÀN BỘ vòng lặp
        }
        if persistence > threshold:
            significant.append(record)
        else:
            noise.append(record)
    return {"significant": significant, "noise": noise, "threshold": threshold}


# HÀM MỚI 2: export_csv — xuất CSV đầy đủ cả thật lẫn nhiễu
def export_csv(
    scenario_results: dict,
    output_path: str = "h1_persistence_results.csv",
    threshold: float = 0.15,
) -> str:
    fieldnames = [
        "scenario", "pair_id", "birth", "death",
        "persistence", "is_significant", "threshold"
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for scenario, pairs in scenario_results.items():
            classified = classify_pairs(pairs, threshold=threshold)
            all_records = classified["significant"] + classified["noise"]
            all_records.sort(key=lambda r: r["pair_id"])
            for rec in all_records:
                writer.writerow({
                    "scenario":       scenario,
                    "pair_id":        rec["pair_id"],
                    "birth":          rec["birth"],
                    "death":          rec["death"],
                    "persistence":    rec["persistence"],
                    "is_significant": rec["is_significant"],
                    "threshold":      rec["threshold"],
                })
    print(f"[OK] Da xuat CSV: {output_path}")
    return output_path

# CHẠY THỬ ĐỘC LẬP
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from vr_builder import build_rips

    THRESHOLD = 0.15

    # === Test 1: Vòng tròn 8 điểm ===
    print("=" * 55)
    print("TEST 1: 8 điểm trên vòng tròn đơn vị")
    print("=" * 55)

    goc = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    pts_vong_tron = np.column_stack([np.cos(goc), np.sin(goc)])
    rips_test = build_rips(pts_vong_tron, max_edge_len=2.1)
    pairs_test = compute_persistence(rips_test)
    c_test = classify_pairs(pairs_test, threshold=THRESHOLD)

    print(f"Tổng H1 pairs tìm được : {len(pairs_test)}")
    print(f"Vòng significant (>{THRESHOLD}): {len(c_test['significant'])}")
    for r in c_test["significant"]:
        print(f"  [pair {r['pair_id']}] birth={r['birth']:.4f}, death={r['death']:.4f}, "
              f"persistence={r['persistence']:.4f}, so_dinh_vong={len(r['vertices'])}")
    print(f"Vòng nhiễu (<={THRESHOLD}): {len(c_test['noise'])}")

    print()

    # === Test 2: KC1, KC2, KC3 ===
    print("=" * 55)
    print("TEST 2: Ba kịch bản GPS thực tế")
    print("=" * 55)

    ky_vong = {
        "KC1": "1 vòng (đường thẳng + 1 vòng tròn r=1)",
        "KC2": "2 vòng (đường thẳng + hình số 8)",
        "KC3": "0 vòng (chỉ nhiễu — negative control)",
    }

    scenario_results = {}

    for ten_kc in ["KC1", "KC2", "KC3"]:
        du_lieu = np.load(f"{ten_kc}.npy")
        rips_kc = build_rips(du_lieu, max_edge_len=2.0)
        pairs_kc = compute_persistence(rips_kc)
        scenario_results[ten_kc] = pairs_kc

        ck = classify_pairs(pairs_kc, threshold=THRESHOLD)

        print(f"\n{ten_kc} — Kỳ vọng: {ky_vong[ten_kc]}")
        print(f"  Tổng pairs : {len(pairs_kc)}")

        print(f"  -- Vòng thật --")
        if ck["significant"]:
            for r in ck["significant"]:
                print(f"    [pair {r['pair_id']}] birth={r['birth']:.4f}, death={r['death']:.4f}, "
                      f"persistence={r['persistence']:.4f}, so_dinh_trong_vong={len(r['vertices'])}")
        else:
            print("    (không có)")

        print(f"  -- Vòng nhiễu --")
        if ck["noise"]:
            max_p = max(r["persistence"] for r in ck["noise"])
            print(f"    Số lượng: {len(ck['noise'])}  |  max persistence={max_p:.4f}")
        else:
            print("    (không có)")

    # === Xuất CSV ===
    print()
    print("=" * 55)
    export_csv(scenario_results, output_path="h1_persistence_results.csv", threshold=THRESHOLD)
    print("Xong! File CSV xuat cung thu muc voi 3 file .npy.")