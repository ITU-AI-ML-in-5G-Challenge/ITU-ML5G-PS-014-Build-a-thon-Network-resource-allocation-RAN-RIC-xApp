# ==================================================================================
#  This SW is developed as part of ITU-5G-AI/ML challenge
#  ITU-ML5G-PS-014: Build-a-thon(PoC) Network resource allocation
#  for emergency management based on closed loop analysis
#  Team : RAN-RIC-xApp
#  Author : Deena Mukundan
#  Description : This file has the main implementation of predictor xApp
# ==================================================================================

import json
import os
import warnings
import schedule
import numpy as np
import itertools
from ricxappframe.xapp_frame import RMRXapp, rmr
from constants import Constants
from a1PolicyInterface import A1PolicyInterface
from prediction import Predictor
from log import logger


pred_xapp = ""
pred = ""

def post_init(self):
    """
    Function that runs when xapp initialization is complete
    """
    #self.predict_requests = 0
    logger.debug("calling post_init")
    #schedule.every(1).minutes.do(predict, self)

def predict_handler(self, summary, sbuf):
    """
    Function that processes messages for type 30000
    """
    logger.debug("predict handler received payload {}".format(summary[rmr.RMR_MS_PAYLOAD]))
    generate_input_time_series()
    in_data = generate_input_time_series()
    predicted_value_slice1 = pred.predict(next(in_data))
    predicted_value_slice2 = pred.predict(next(in_data))
    predicted_value = [predicted_value_slice1,predicted_value_slice2]
    val = json.dumps({"prediction": predicted_value}).encode() 
    logger.debug(f"Predicted value for Slice 1&2 : {val }")
    success = self.rmr_rts(sbuf, new_payload=val, new_mtype=Constants.PRB_PRED_RSP, retries=10)
    logger.debug("Sending message to alloc xApp : {}".format(val))  # For debug purpose
    if success:
        logger.debug("predict handler: sent message successfully")
    else:
        logger.error("predict handler: failed to send message")
    self.rmr_free(sbuf)



def pred_default_handler(self, summary, sbuf):
    """
    Function that processes messages for which no handler is defined
    """
    #logger.debug("default handler received message type {}".format(summary[rmr.RMR_MS_MSG_TYPE]))
    logger.debug("default handler received message type {}".format(summary[rmr.RMR_MS_MSG_TYPE]))
    # we don't use rts here; free this
    self.rmr_free(sbuf)



def start(thread=False):
    """
    This is a convenience function that allows this xapp to run in Docker
    for "real" (no thread, real SDL), but also easily modified for unit testing
    (e.g., use_fake_sdl). The defaults for this function are for the Dockerized xapp.
    """
    logger.debug("pred xApp starting")
    global pred_xapp, pred
    fake_sdl = os.environ.get("USE_FAKE_SDL", None)
    pred_xapp = RMRXapp(pred_default_handler, rmr_port=4560, post_init=post_init, use_fake_sdl=bool(fake_sdl))
    logger.debug("pred_xapp created@@@")
    pred = Predictor(pred_xapp)
    a1_intf = A1PolicyInterface(pred_xapp, pred)
    pred_xapp.register_callback(pred.request_handler, Constants.PRB_PRED_REQ)
    pred_xapp.register_callback(a1_intf.request_handler,Constants.A1_POLICY_REQ)
    a1_intf.send_a1_policy_query()
    pred_xapp.run(thread)
