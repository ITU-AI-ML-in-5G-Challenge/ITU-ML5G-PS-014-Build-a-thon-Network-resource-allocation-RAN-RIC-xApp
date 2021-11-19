# ========================================================================================
#  This SW is developed as part of ITU-5G-AI/ML challenge
#  ITU-ML5G-PS-014: Build-a-thon(PoC) Network resource allocation
#  for emergency management based on closed loop analysis
#  Team : RAN-RIC-xApp
#  Author : Deena Mukundan
#  Description : This file has the main implementation of interface messages with a1mediator
# ==========================================================================================

import json
from ricxappframe.xapp_frame import RMRXapp, rmr
from constants import Constants
from prediction import Predictor
from log import logger

class A1PolicyInterface:
    def __init__(self, rmr_xapp: RMRXapp, pred: Predictor):
        self._rmr_xapp = rmr_xapp
        self.predObj = pred
        logger.debug("A1PolicyInterface")

    def send_a1_policy_query(self):
        policy_query = '{"policy_type_id":"' + str(Constants.PRB_PRED_POLICY_ID) + '"}'
        success = self._rmr_xapp.rmr_send(policy_query.encode(), Constants.A1_POLICY_QUERY)
        #success = self._rmr_xapp.rmr_send(policy_query.encode(), Constants.PRB_PRED_REQ)
        if success:
            logger.debug("send_a1_policy_query:: Sent A1 policy query (A1_POLICY_QUERY)= " + policy_query)
        else:
            logger.error("send_a1_policy_query:: Error sending A1 policy query = " + policy_query)

    def request_handler(self, rmr_xapp: RMRXapp, summary, sbuf):
        self._rmr_xapp.rmr_free(sbuf)
        try:
            req = json.loads(summary[rmr.RMR_MS_PAYLOAD])  # input should be a json encoded as bytes
            logger.debug("request_handler.resp_handler:: Handler processing A1_POLICY_REQ request")
        except (json.decoder.JSONDecodeError, KeyError):
            logger.error("request_handler.resp_handler:: Handler failed to parse request")
            return

        if self.verifyPolicy(req):
            logger.debug("request_handler.resp_handler:: Handler verified policy request: {}".format(req))
        else:
            logger.error("request_handler.resp_handler:: Request verification failed: {}".format(req))
            return
        # Store the Predictor object
        logger.debug("A1PolicyInterface:::request handler received payload {}".format(req['payload']))
        self.predObj.store_model_info(req['payload'])
        #self.predObj.send_pred_rsp_to_alloc()
        resp = self.buildPolicyResp(req)
        self._rmr_xapp.rmr_send(json.dumps(resp).encode(), Constants.A1_POLICY_RESP)
        logger.debug("request_handler.resp_handler:: A1_POLICY_RESP Response sent: {}".format(resp))

    def verifyPolicy(self, req: dict):
        for i in ["policy_type_id", "operation", "policy_instance_id"]:
            if i not in req:
                return False
        return True

    def buildPolicyResp(self, req: dict):
        req["handler_id"] = "prbpredxapp"
        del req["operation"]
        req["status"] = "OK"
        return req
