import numpy as np
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# ============ CONFIGURATION ============
PREFIX = "jacob"   # filename prefix after "tie_histogram_", e.g. "jacob", "1.2km", "free"
# ========================================

files = sorted(str(p) for p in DATA_DIR.glob(f"tie_histogram_{PREFIX}_*.npz"))
time_regex = rf"tie_histogram_{re.escape(PREFIX)}_([\d.eE+-]+)s_"

checkpoint_times = []
counts_list = []

for f in files:
    d = np.load(f)
    data = d["data"]
    total_counts = data.sum()

    match = re.search(time_regex, f)
    if match is None:
        print(f"Warning: could not parse time from filename, skipping: {f}")
        continue
    checkpoint_time = float(match.group(1))

    checkpoint_times.append(checkpoint_time)
    counts_list.append(total_counts)

# Sort by checkpoint time for a clean, ordered printout
order = np.argsort(checkpoint_times)
checkpoint_times = np.array(checkpoint_times)[order]
counts_list = np.array(counts_list)[order]

for t, c in zip(checkpoint_times, counts_list):
    print(f"{t:.4g}s — {c} counts")