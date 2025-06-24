from typing import List

class ZoiWindow:
    """
    A simple container for a Zone-Of-Interest (ZOI) window.
    start/end are timestamps (or any comparable), activated is a bool.
    """
    def __init__(self, start, end, activated: bool = False):
        self.start = start
        self.end = end
        self.activated = activated

    def replace(self, activated: bool):
        # Return a brand-new ZoiWindow with the same start/end but new activated flag
        return ZoiWindow(self.start, self.end, activated)

def compute_zois(df, lookback: int) -> List[ZoiWindow]:
    """
    Slide a window of `lookback` bars over `df.index` and return a list of ZoiWindow(start, end).
    This does NOT look at price columns at all, so it works on any df with a datetime-like index.
    """
    times = df.index
    zois = []
    # for each point after the first lookback bars
    for i in range(lookback, len(times)):
        start = times[i - lookback]
        end = times[i]
        zois.append(ZoiWindow(start, end))
    return zois

def activate_zois(zois: List[ZoiWindow], timestamp) -> List[ZoiWindow]:
    """
    Given a list of ZoiWindow(s) and a timestamp, return a **new** list
    where each window’s `.activated` flag is True iff start <= timestamp < end.
    """
    activated_list = []
    for z in zois:
        is_active = (z.start <= timestamp < z.end)
        activated_list.append(z.replace(is_active))
    return activated_list
