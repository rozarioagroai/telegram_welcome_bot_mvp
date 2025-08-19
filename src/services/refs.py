from typing import Optional
from ..config import settings as global_settings
from ..utils.tg import build_ref_utm

def build_url(source: str, base_url: str, campaign: str) -> str:
    return build_ref_utm(base_url, campaign, source)

def build_url_from_config(source: str, settings: Optional[object] = None) -> str:
    s = settings or global_settings
    return build_url(source, s.REF_BASE_URL, s.UTM_CAMPAIGN)