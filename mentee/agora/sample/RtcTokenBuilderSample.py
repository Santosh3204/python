#! /usr/bin/python
# ! -*- coding: utf-8 -*-

import sys
import os
import time
from random import randint
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mentee.agora.src.RtcTokenBuilder import RtcTokenBuilder,Role_Attendee

appID = "840e67b9d38c44ee8c975b9338546e69"
appCertificate = "8f3fc6f306bd4d53a8063254b1bc5de1"
channelName = "11-10-2020 12:12:12 python"
uid = 2882341273

expireTimeInSeconds = 3600
currentTimestamp = int(time.time())
privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

def main():
    token = RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channelName, uid, Role_Attendee, privilegeExpiredTs)
    print("Token with int uid: {}".format(token))


if __name__ == "__main__":
    main()
