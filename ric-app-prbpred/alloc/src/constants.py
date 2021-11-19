# ==================================================================================
#  This SW is developed as part of ITU-5G-AI/ML challenge
#  ITU-ML5G-PS-014: Build-a-thon(PoC) Network resource allocation
#  for emergency management based on closed loop analysis
#  Team : RAN-RIC-xApp
#  Author : Deena Mukundan
#  Description : This file defines the values for the constants that are used in this module
# ==================================================================================

class Constants:
    ACTION_TYPE = "REPORT"
    SUBSCRIPTION_PATH = "http://service-{}-{}-http:{}"
    PLT_NAMESPACE = "ricplt"
    SUBSCRIPTION_SERVICE = "submgr"
    SUBSCRIPTION_PORT = "3800"
    SUBSCRIPTION_REQ = 12011
    PRB_PRED_RSP = 30002
    PRB_PRED_REQ = 30003
    TOTAL_PRBS = 100
    PRB_RSRD_EMGY = 30
    PRB_ALLOC_SLICE1 = 35
    PRB_ALLOC_SLICE2 = 35
    RIC_HEALTH_CHECK_REQ = 100