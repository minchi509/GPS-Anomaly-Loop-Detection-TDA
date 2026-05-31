import numpy as np
from scipy.spatial.distance import pdist
from typing import Self


class RipsNode():
    def __init__(self) -> None:
        self.children: dict[int, Self] = {}
        self.filt_val: float | None = None


class RipsTree():
    def __init__(self, points: np.ndarray) -> None:
        self.root: RipsNode = RipsNode()
        self.points: np.ndarray = points

    def add_simplex(self, filt_val: float, simplex: tuple[int, ...]):
        # so sánh floating point numbers có thể cho bug do sai số nhỏ nên ta sẽ lưu index trên cây để so sánh simplex dễ hơn
        curr: RipsNode = self.root
        for vertex in sorted(simplex):
            if vertex not in curr.children:
                curr.children[vertex] = RipsNode()
            curr = curr.children[vertex]

        # Đã chạy hết simplex cần thêm => thêm filtration value.
        if curr.filt_val is None:
            # Chưa có filtration value. Thêm vào.
            curr.filt_val = filt_val
        else:
            # Có rồi? Luôn chắc chắn filt_val là nhỏ nhất
            curr.filt_val = min(filt_val, curr.filt_val)

    def get_simplexes(self) -> list[tuple[tuple[int, ...], float]]:
        result: list[tuple[tuple[int, ...], float]] = []

        def dfs(subroot: RipsNode, path: list[int]) -> None:
            # chạy depth-first từ subroot đến lá của subtree có đỉnh tại subroot
            # nếu filtration khác None thì nghĩa là đã gặp được một k-simplex => add path vào result
            if subroot.filt_val is not None:
                result.append((tuple(path), subroot.filt_val))

            for v, child in subroot.children.items():
                dfs(child, path + [v])

        dfs(self.root, [])
        return result

    def get_simplex_points(self) -> list[tuple[np.ndarray, float]]:
        result: list[tuple[np.ndarray, float]] = []

        for simplex, filt in self.get_simplexes():
            pts = self.points[list(simplex)]
            result.append((pts, filt))

        return result

def condensed_index(n: int, i: int, j: int) -> int:
    """
    Ánh xạ tọa độ 2D (i, j) của ma trận khoảng cách sang chỉ số của mảng 1D.
    
    Lý do: Hàm `pdist` của scipy tối ưu bộ nhớ bằng cách không trả về ma trận vuông N x N, 
    mà chỉ trả về mảng 1D (condensed distance matrix) chứa tam giác trên của ma trận.
    Hàm này áp dụng công thức từ tài liệu của SciPy để tính toán chính xác 
    vị trí 1D của khoảng cách giữa hai điểm i và j.
    """
    
    # Cấu trúc tam giác trên yêu cầu chỉ số hàng (i) luôn phải nhỏ hơn chỉ số cột (j).
    # Nếu i > j, ta hoán đổi vị trí để tận dụng tính đối xứng của khoảng cách (dist(i,j) == dist(j,i)).
    if i > j:
        i, j = j, i

    return int(n*i + j - ((i+2) * (i+1))//2)


def build_rips(points: np.ndarray, max_edge_len: float) -> RipsTree:
    # Ta quan tâm đến H_1 persistence nên sẽ chỉ cần đến 2-simplex là đủ
    n: int = len(points)

    # Tính khoảng cách giữa các cặp điểm => Ma trận khoảng cách.
    distances: np.ndarray = pdist(points, 'euclidean')
    # Kiểm tra các khoảng cách đủ để nối cạnh => Ma trận kề.
    adjacency: np.ndarray = distances <= max_edge_len

    rips: RipsTree = RipsTree(points)

    # gắn các 0-simplex vào cây
    for i in range(n):
        filt_val = 0.0
        simplex = tuple([i])
        rips.add_simplex(filt_val, simplex)

    # gắn các 1-simplex vào cây
    neighbors = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            idx = condensed_index(n, i, j)
            if adjacency[idx]:
                neighbors[i].add(j)
                neighbors[j].add(i)

                filt_val = distances[idx]
                simplex = (i, j)
                rips.add_simplex(filt_val, simplex)

    # gắn các 2-simplex vào cây
    for i in range(n):
        for j in neighbors[i]:
            if not (j > i): continue

            common_neighbors = neighbors[i] & neighbors[j]
            for k in common_neighbors:
                if not (k > j): continue

                idx_ij = condensed_index(n, i, j)
                idx_ik = condensed_index(n, i, k)
                idx_jk = condensed_index(n, j, k)

                d_ij = distances[idx_ij]
                d_ik = distances[idx_ik]
                d_jk = distances[idx_jk]

                filt_val = max(d_ij, d_ik, d_jk)
                simplex = (i, j, k)
                rips.add_simplex(filt_val, simplex)

    return rips
