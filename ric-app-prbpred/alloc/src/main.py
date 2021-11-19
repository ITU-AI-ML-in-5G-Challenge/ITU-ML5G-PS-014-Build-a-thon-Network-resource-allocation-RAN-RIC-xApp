# ==================================================================================
#  This SW is developed as part of ITU-5G-AI/ML challenge
#  ITU-ML5G-PS-014: Build-a-thon(PoC) Network resource allocation
#  for emergency management based on closed loop analysis
#  Team : RAN-RIC-xApp
#  Authors : Deena Mukundan
#  Description : This file has the main implementation of alloc xApp
# ==================================================================================

import os
import json
import schedule
#from mdclogpy import Logger
from ricxappframe.xapp_frame import Xapp, rmr
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import requests
import logging
from .constants import Constants
logger = ""


xapp = ""
def post_init(self):
    """
    Function that runs when xapp initialization is complete
    """
    self.predict_requests = 0
    logger.debug("post_init::Alloc xApp started")

def conf_logger():
    # Create and configure logger
    global logger
    #logging.basicConfig(format='%(asctime)s %(message)s')
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    # Creating an object
    logger = logging.getLogger()
    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)

def alloc_default_handler(self, summary, sbuf):
    """
    Function that processes messages for which no handler is defined
    """
    logger.debug("default handler received message type {}".format(summary[rmr.RMR_MS_MSG_TYPE]))
    # we don't use rts here; free this
    self.rmr_free(sbuf)

def generate_input_time_series():
    time_point = itertools.cycle(range(_TIME_SERIES_RANGE))
    while True:
        yield np.array((next(time_point),)).reshape(-1, 1)


def get_gnb_list(self):
    """  This function gets the gnb list
         as stored in RNIB
    """
    gnblist = self.get_list_gnb_ids()  # yet to come in library
    logger.debug("gnblist{}".format(gnblist))
    return gnblist


def get_enb_list(self):
    """  This function gets the enb list
         as stored in RNIB
    """
    enblist = self.get_list_enb_ids()  # yet to come in library
    logger.debug("SubscriptionManager.sdlGetGnbList:: Handler processed request: {}".format(json.dumps(enblist)))
    return enblist

#Divyani
def send_subscription_request(xnb_id):
    """  This function forms the json payload for each
         gnb's/enb's
    """
    f = open("./alloc/subscription_req.json", )
    payload = json.load(f)
    f.close()
    payload = "'" + str(payload) + "'"
    logger.debug("req {}".format(payload))
    url = Constants.SUBSCRIPTION_PATH.format(Constants.PLT_NAMESPACE,
                                             Constants.SUBSCRIPTION_SERVICE,
                                             Constants.SUBSCRIPTION_PORT)
    try:
        response = requests.post(url , json=payload)
        logger.debug("response",response.json)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err_h:
        return "An Http Error occurred:" + repr(err_h)
    except requests.exceptions.ConnectionError as err_c:
        return "An Error Connecting to the API occurred:" + repr(err_c)
    except requests.exceptions.Timeout as err_t:
        return "A Timeout Error occurred:" + repr(err_t)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)

def send_subscription_requests_all(self):
    """  This function sends subscription request for all
         gnb's/enb's
    """

    list_gnb = get_gnb_list(self)
    list_enb = get_enb_list(self)
    for enb in list_enb:
        send_subscription_request(enb)
    list_gnb = [10110101110001100111011110001]
    for gnb in list_gnb:
        send_subscription_request(gnb)


def verifySubscription(req: dict):

    for i in ["SubscriptionId", "SubscriptionInstances"]:
        if i not in req:
            return False
    return True

def handle_subscription_resp(self, summary, sbuf):
    """  This function handles subscription response from
         Subscription Manager
    """
    self.rmr_free(sbuf)
    try:
        req = json.loads(summary[rmr.RMR_MS_PAYLOAD])  # input should be a json encoded as bytes
    except (json.decoder.JSONDecodeError, KeyError):
        logger.error("Subscription.resp_handler:: Handler failed to parse request")
        return

    if verifySubscription(req):
        logger.debug("SubscriptionHandler.resp_handler:: Handler processed request: {}".format(req))
    else:
        logger.error("SubscriptionHandler.resp_handler:: Request verification failed: {}".format(req))
        return

def send_pred_req_to_predxApp(self):
    """  This function does the following
    1) Upon timer trigger sends PRB_PRED_REQ to pred-xApp
    2) Sends ack message to pred-xApp once PRB_PRED_RESP is received
    3) Handling subscription response from Subscription Manager
    """
    # send message from ad to ts
    logger.debug("[msg_to_pred] " "")
    val = json.dumps(1).encode()
    success = self.rmr_send(val, Constants.PRB_PRED_REQ)
    if success:
        logger.debug("[INFO] Message to pred : message sent Successfully")
    # rmr receive to get the acknowledgement message from the traffic steering.
    for (summary, sbuf) in self.rmr_get_messages():
        mtype = summary[rmr.RMR_MS_MSG_TYPE]
        if mtype == Constants.PRB_PRED_RSP:
            logger.debug("[INFO] Received acknowldgement from pred (PRB_PRED_RSP): {}".format(summary))
            allocate(self,summary,sbuf)
        elif mtype == Constants.SUBSCRIPTION_REQ:
            logger.debug("mtype:{}".format(mtype))
            handle_subscription_resp(self,summary, sbuf )
        else:
            logger.warning("unknown message ")
        self.rmr_free(sbuf)

def check_rmr_messages(self):
    for (summary, sbuf) in self.rmr_get_messages():
        mtype = summary[rmr.RMR_MS_MSG_TYPE]
        if mtype == Constants.RIC_HEALTH_CHECK_REQ:
            logger.debug("[INFO] Received (RIC_HEALTH_CHECK_REQ): {}".format(summary))
            send_health_check_resp(self,summary,sbuf)
        else:
            logger.warning("unknown message ")
        self.rmr_free(sbuf)

def send_health_check_resp(self,summary,sbuf):
    ok = self.healthcheck()
    if ok:
        payload = b"OK\n"
    else:
        payload = b"ERROR [RMR or SDL is unhealthy]\n"
    self.rmr_rts(sbuf, new_payload=payload, new_mtype=Constants.RIC_HEALTH_CHECK_RESP)
    self.rmr_free(sbuf)

def allocate(self,summary,sbuf):

    val_list= json.loads(summary[rmr.RMR_MS_PAYLOAD])
    pred = val_list["prediction"]

    # Out of 100 PRB's in the system 20 PRB's are reserved for emergency services
    # in addition to 20 PRB's allocate the available PRB's unutilized from Slice 1 &2
    #Assuming 35 PRB's are allocated to both slice 1&2

    utilised_slice1_prb = round(float(Constants.PRB_ALLOC_SLICE1*(pred[0]/100)))
    utilised_slice2_prb = round(float(Constants.PRB_ALLOC_SLICE2*(pred[1]/100)))
    logger.debug("Estimated PRB usage of Slice 1:{}".format(utilised_slice1_prb))
    logger.debug("Estimated PRB usage of Slice 2:{}".format(utilised_slice2_prb))
    total_prb_avail = Constants.TOTAL_PRBS - (utilised_slice1_prb + utilised_slice1_prb)
    logger.debug("PRB allocated to Emgerceny SLice :{}".format(total_prb_avail))
    hostname = os.environ.get("HOSTNAME")
    logger.debug("hostname :{}".format(hostname))

def entry(self):
    """  This function sends subscription request to SUbscription manager for RAN updates
         and is scheduled every 1 minute to send prediction request to Predict xApp
    """
    logger.debug("entry:::")
    send_subscription_requests_all(self) #TO DO later
    #check_rmr_messages(self)
    schedule.every(1).minute.do(send_pred_req_to_predxApp, self)
    while True:
        schedule.run_pending()

def start(thread=False):
    """
    This is a convenience function that allows this xapp to run in Docker
    for "real" (no thread, real SDL), but also easily modified for unit testing
    (e.g., use_fake_sdl). The defaults for this function are for the Dockerized xapp.
    """
    global alloc_xapp
    # Initiates xapp api and runs the entry() using xapp.run()
    conf_logger()
    alloc_xapp = Xapp(entrypoint=entry, rmr_port=4560, use_fake_sdl=False)
    alloc_xapp.run()
