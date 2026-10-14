"""v257: gameplay tuning. The ground pound is ready 4 seconds into a match (it was 10); after each pound the wait is still 6."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    s = rep(s, "SLAM_CD = 6, SLAM_FIRST = 10, SLAM_COST", "SLAM_CD = 6, SLAM_FIRST = 4, SLAM_COST")
    return s
