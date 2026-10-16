import sys
from pathlib import Path
root = Path(r'D:\scan chain dianosis agent')
sys.path.insert(0, str(root / 'src'))
sys.path.insert(0, str(root / 'api'))

from adapters.data_loader import load_failures
failures, source = load_failures()  # returns tuple
from model_lifecycle import maybe_retrain, lifecycle_summary
from review_queue import queue_summary, load_queue

# Ensure seeded_fingerprint is set on current queue so pending stays 0 for same data
q = load_queue()
print('queue', queue_summary())
print('seeded_fp', q.get('seeded_fingerprint'))

result = maybe_retrain(failures, force=True)
print(result)
print(lifecycle_summary())
print('queue_after', queue_summary())
