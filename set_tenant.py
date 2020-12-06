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
            usage="""Create and update users and tenants
            Only one of email or UID is required.
            To create a user, provide email, to add tenant number to existing user
            provide UID.

            To disable the bootstrapping of status settings for a tenant include --no-bootstrap
           """
)
parser.add_argument("-e", "--email", help="email of the user - for creating")
parser.add_argument("-u", "--user", help="UID of Firebased user to add tenant number to")
parser.add_argument("-n", "--number", required=True, help="The Twilio SMS number in the form +1xxxxxxxxxx")
parser.add_argument("-p", "--password", help="password for new user, generated if not provided")
parser.add_argument("--no-bootstrap", help="do not set initialize settings for tenant, use when adding additional users to existing tenant")


# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': os.getenv('GOOGLE_CLOUD_PROJECT'),
})

valid_sms_pattern = re.compile(r"^\+1\d{10}$")


def main():
    args = parser.parse_args()


    tenant = args.number
    if not (valid_sms_pattern.match(tenant)):
        sys.exit("invalid number format, must be +1xxxxxxxxxx")

    email = args.email
    password = args.password
    uid = args.user
    if not password:
        password = generate_password()
    if email:
        user = auth.create_user(
            email=email,
            email_verified=True,
            password=password,
            disabled=False)
        uid = user.uid
        print('Sucessfully created new user: {0}'.format(uid))
        print("created login", email, "pw:", password)
    else:
        if not uid:
            sys.exit("Firebase UID must be provided if email is not given")
        
    auth.set_custom_user_claims(uid, {'curbside_number': tenant})

    if args.no_bootstrap:
        sys.exit(0)

    # continue with tenant intialization
    # A future improvement could use an admin curated "template"
    # set of settings in the DB to copy
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


def generate_password(length=8):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@£$%^&*().,?0123456789'
    password = ''
    for c in range(length):
        password += random.choice(chars)
    return password

if __name__ == '__main__':
   main()