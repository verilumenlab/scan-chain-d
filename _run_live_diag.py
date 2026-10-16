import traceback
from pathlib import Path
Path('_live_error.txt').write_text('starting\n')
try:
    from api.adapters.diagnosis_service import _build_from_live, get_dashboard
    try:
        d = _build_from_live(None, None)
        Path('_live_error.txt').write_text(f'SUCCESS data_source={d.data_source}\nconfidence={d.confidence}\n')
    except Exception:
        Path('_live_error.txt').write_text('BUILD_FROM_LIVE FAILED:\n' + traceback.format_exc())
except Exception:
    Path('_live_error.txt').write_text('IMPORT/OUTER FAILED:\n' + traceback.format_exc())
