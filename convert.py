import pandas as pd
from pathlib import Path

# 파일 경로
DATA_PATH = Path("data") / "Faults.NNA"
OUT_PATH = Path("data") / "steel_plates_faults_clean.csv"

# 공백 구분 파일 읽기
df = pd.read_csv(DATA_PATH, sep=r"\s+", header=None, engine="python")

# 마지막 K개 컬럼 = one-hot fault label 자동 추정
def guess_label_k(dataframe, k_min=5, k_max=15):
    ncol = dataframe.shape[1]
    for k in range(k_min, min(k_max, ncol - 1) + 1):
        label_part = dataframe.iloc[:, -k:]
        if label_part.isin([0, 1]).all().all():
            if (label_part.sum(axis=1) == 1).mean() > 0.95:
                return k
    raise ValueError("Label columns not detected")

K = guess_label_k(df)

# feature / label 분리
X = df.iloc[:, :-K].copy()
Y_onehot = df.iloc[:, -K:].copy()

# 컬럼 이름 설정
X.columns = [f"feat_{i+1}" for i in range(X.shape[1])]
label_names = [f"fault_{i}" for i in range(K)]
Y_onehot.columns = label_names

# one-hot → 단일 fault_type
fault_idx = Y_onehot.values.argmax(axis=1)
fault_type = [label_names[i] for i in fault_idx]

# 최종 데이터프레임
out = X.copy()
out["fault_type"] = fault_type

# CSV 저장
out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
