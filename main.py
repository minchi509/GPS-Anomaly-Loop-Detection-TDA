import numpy as np
import os
import csv
import sys
import generate_data
from vr_builder import build_rips
from persistence_homology import compute_persistence, classify_pairs

def main():
    DATA_DIR = "."
    RESULT_DIR = "results"
    FIGURE_DIR = "figures"
    SCENARIOS = ["KC1", "KC2", "KC3"]
    THRESHOLD = 0.15
    MAX_EDGE = 2.0
    
    for folder in [RESULT_DIR, FIGURE_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    print(">>> Dang sinh du lieu...")
    try:
        generate_data.generate_npy_files(output_dir=DATA_DIR)
        print("   + Sinh du lieu .npy thanh cong!")
    except Exception as e:
        print(f"[Loi] Khong the sinh du lieu: {e}")
        return

    out_centroid_csv = os.path.join(RESULT_DIR, "centroid_estimations.csv")
    out_full_csv = os.path.join(RESULT_DIR, "h1_persistence_results.csv")

    with open(out_centroid_csv, "w", newline="", encoding="utf-8") as f_cent, \
         open(out_full_csv, "w", newline="", encoding="utf-8") as f_full:

        cent_writer = csv.DictWriter(f_cent, fieldnames=["scenario", "loop_id", "centroid_x", "centroid_y", "radius", "persistence"])
        cent_writer.writeheader()

        full_writer = csv.DictWriter(f_full, fieldnames=["scenario", "pair_id", "birth", "death", "persistence", "is_significant", "threshold"])
        full_writer.writeheader()

        for kc in SCENARIOS:
            path = os.path.join(DATA_DIR, f"{kc}.npy")
            if not os.path.exists(path):
                print(f"[!] Bo qua {kc}: Khong tim thay file {path}")
                continue
                
            print(f"\n>>> Dang xu ly {kc}...")
            points = np.load(path)
            
            tree = build_rips(points, max_edge_len=MAX_EDGE)
            pairs = compute_persistence(tree)
            ck = classify_pairs(pairs, threshold=THRESHOLD)
            
            print(f"   + Phat hien {len(ck['significant'])} vong lap ben vung.")

            all_records = ck['significant'] + ck['noise']
            all_records.sort(key=lambda r: r['pair_id']) 
            for rec in all_records:
                full_writer.writerow({
                    "scenario": kc,
                    "pair_id": rec["pair_id"],
                    "birth": rec["birth"],
                    "death": rec["death"],
                    "persistence": rec["persistence"],
                    "is_significant": rec["is_significant"],
                    "threshold": rec["threshold"]
                })
                
            for rec in ck['significant']:
                v_coords = points[list(rec['vertices'])]
                cx, cy = np.mean(v_coords, axis=0)
                radius = np.mean(np.linalg.norm(v_coords - [cx, cy], axis=1))
                
                cent_writer.writerow({
                    "scenario": kc,
                    "loop_id": rec["pair_id"],
                    "centroid_x": round(cx, 4),
                    "centroid_y": round(cy, 4),
                    "radius": round(radius, 4),
                    "persistence": round(rec["persistence"], 4)
                })

    print(f"\n>>> DA XUAT 2 FILE CSV TAI THU MUC: {RESULT_DIR}")

    print("\n>>> Dang ve bieu do (Barcode, Diagram, GPS Map)...")
    
    import visualize 
    
    visualize.DATA_DIR = DATA_DIR
    visualize.OUTPUT_DIR = RESULT_DIR
    visualize.FIGURE_DIR = FIGURE_DIR       
    visualize.H1_FILE = out_full_csv             
    visualize.CENTROID_FILE = out_centroid_csv  

    visualize.main()
    
    print(f"\n=== TDA PIPELINE HOAN TAT ===")
    print(f"Toan bo hinh anh da duoc luu tai thu muc: {FIGURE_DIR}")

if __name__ == "__main__":
    main()