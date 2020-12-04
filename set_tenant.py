#!/usr/bin/env python

# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
This admin script sets up a new tenant/user in the database

'''

import argparse
import os
from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
import random
import re
import sys

parser = argparse.ArgumentParser(
            description="add a new user and tenant to the system"
)
parser.add_argument("-e", "--email", required=True, help="email of the user")
parser.add_argument("-n", "--number", required=True, help="The Twilio SMS number in the form +1xxxxxxxxxx")
parser.add_argument("-p", "--password", help="password for the user, generated if not provided")


# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': os.getenv('GOOGLE_CLOUD_PROJECT'),
})

valid_sms_pattern = re.compile(r"^\+1\d{10}$")


def main():
    args = parser.parse_args()


    provision = True
    if not (valid_sms_pattern.match(args.number)):
        sys.exit("invalid number format, must be +1xxxxxxxxxx")

    email = args.email
    sms_number = args.number
    tenant = sms_number
    password = args.password
    if not password:
        password = generate_password()
        print("Generated password: ", password)
    if provision:
        user = auth.create_user(
            email=email,
            email_verified=True,
            password=password,
            disabled=False)
        print('Sucessfully created new user: {0}'.format(user.uid))
        uid = user.uid
        db = firestore.client()

        db.collection('settings').document(tenant).set({
            'dndEnable': False,
            'dndMessage': "Sorry this system is not available, please call our main number"
        })
        db.collection('statuses').add({
            "label": "arrived",
            "color": "#155ccf",
            "isFinal": False,
            "created": datetime.now(timezone.utc),
            "sequence": 1,
            "sendImmediately": False,
            "tenant": tenant,
            "response": "Thanks for letting us know you are here, please let us know your vehicle type and location.",
        })
        db.collection('statuses').add({
            "label": "reply",
            "color": "#008e00",
            "isFinal": False,
            "created": datetime.now(timezone.utc),
            "sequence": 2,
            "sendImmediately": False,
            "tenant": tenant,
            "response": "thanks, we got your message",
        })

        db.collection('statuses').add({
            "label": "ended",
            "color": "#d21d23",
            "isFinal": True,
            "created": datetime.now(timezone.utc),
            "sequence": 1000,
            "sendImmediately": True,
            "tenant": tenant,
            "response": "",
        })
        db.collection('settings').document(tenant).set({
            "dndEnabled": False,
            "dndMessage": "Sorry - we are currently closed, this message is for curbside communication only."
        })
        db.collection('settings').document(uid).set({
            "alertOnArrive": "doorbell",
            "alertOnReply": "bell",
            "alertOnOverdue": "alert",
            "notifyOnArrive": False,
            "notifyOnReply": False,
            "notifyOnOverdue": False,
            "overdueDeadline": 200
        })

    auth.set_custom_user_claims(uid, {'curbside_number': tenant})
    print("created login", email, "pw:", password)

def generate_password(length=8):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@£$%^&*().,?0123456789'
    password = ''
    for c in range(length):
        password += random.choice(chars)
    return password

if __name__ == '__main__':
   main()