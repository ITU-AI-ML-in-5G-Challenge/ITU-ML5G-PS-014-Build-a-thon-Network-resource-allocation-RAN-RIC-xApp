# ==================================================================================
#  This SW is developed as part of ITU-5G-AI/ML challenge
#  ITU-ML5G-PS-014: Build-a-thon(PoC) Network resource allocation
#  for emergency management based on closed loop analysis
#  Team : RAN-RIC-xApp
#  Author : Deena Mukundan
#         : Divyani Achari
#  Description : This file has the main implementation of predictor xApp
# ==================================================================================
import pickle
from typing import List
from ricxappframe.xapp_frame import RMRXapp, rmr
import numpy as np
import os
import urllib.request
import itertools
import json
from constants import Constants

from log import logger

_TIME_SERIES_RANGE = 150

def generate_input_time_series():
    time_point = itertools.cycle(range(_TIME_SERIES_RANGE))
    while True:
        yield np.array((next(time_point),)).reshape(-1, 1)

class Predictor:
    def __init__(self,rmrXapp: RMRXapp) -> None:
        """constructor to initialise."""


        self.model_info = {}
        self.model = [0] * 5
        self.model_path = ""
        self._rmr_xapp = rmrXapp

    def send_pred_rsp_to_alloc(self):
        generate_input_time_series()
        in_data = generate_input_time_series()
        predicted_value_slice1 = self.predict(next(in_data))
        predicted_value_slice2 = self.predict(next(in_data))
        predicted_value = [predicted_value_slice1, predicted_value_slice2]
        val = json.dumps({"prediction": predicted_value}).encode()
        success = self._rmr_xapp.rmr_send(val, Constants.PRB_PRED_RSP)
        if success:
            logger.debug("send_pred_rsp_to_alloc:: Sent PRB_PRED_RSP " + policy_query)
        else:
            logger.error("send_a1_policy_query:: Error sending A1 policy query = " + policy_query)

    def request_handler(self, rmrXapp: RMRXapp,summary, sbuf):
        logger.debug("predict handler received payload {}".format(summary[rmr.RMR_MS_PAYLOAD]))
        in_data = generate_input_time_series()
        predicted_value_slice1 = self.predict(next(in_data))
        predicted_value_slice2 = self.predict(next(in_data))
        predicted_value = [predicted_value_slice1, predicted_value_slice2]
        val = json.dumps({"prediction": predicted_value}).encode()
        logger.debug(f"Predicted value for Slice 1&2 : {val}")
        success = rmrXapp.rmr_rts(sbuf, new_payload=val, new_mtype=Constants.PRB_PRED_RSP, retries=10)
        logger.debug("Sending message to alloc xApp : {}".format(val))  # For debug purpose
        if success:
            logger.debug("predict handler: sent message successfully")
        else:
            logger.error("predict handler: failed to send message")
        rmrXapp.rmr_free(sbuf)

    def predict(self, data: np.ndarray) -> List[float]:
        """ Returns predicted value.

        Parameters
        ----------
        data: Input data for the predictor model.

        Returns
        -------
        prediction: np.ndarray
        """
        global logger
        logger.debug("Predictor::predict()")
        path = self.model_path
        try:
            self.model = pickle.load(open(path, "rb"))
            return self.model.predict(data).item()
        except Exception as e:
            logger.error("Predictor:: exception encountered in loading model {}".format(e))

    def pull_model(self, url, version, model_name):
        data_folder = "./prbpred"
        file_server = url+"/"+version+"/"
        self.model_path = os.path.join(data_folder, model_name)
        logger.debug("pull_model::Sent Download request to model store {}".format(file_server))
        try:
            urllib.request.urlretrieve(os.path.join(file_server, model_name), self.model_path)
            logger.debug("pull_model::Successfully Downloaded model to {}".format(self.model_path))
        except Exception as e:
            logger.debug("Error Downloading model{}".format(e))


    def store_model_info(self, data: dict):
        logger.debug("store_model_info:: Fetch model from model store {}".format(data))
        self.model_info = data
        model_file = self.model_info['modelname']
        file_path = os.path.join(os.getcwd(), "prbpred",model_file)
        self.pull_model(self.model_info['modelstoreUrl'], self.model_info['modelVersion'], self.model_info['modelname'])
        try:
            self.model = pickle.load(open(file_path, "rb"))
        except Exception as e:
            logger.error("Predictor:: store_model_info value error encountered {}".format(e))
        logger.debug("store_model_info::Saved Model info ")