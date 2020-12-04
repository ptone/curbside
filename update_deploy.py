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
This script updates a timestamp in the database that notifies the front end
that there may be changes and it should be refreshed
'''

import os
from datetime import datetime, timedelta, timezone
from firebase_admin import initialize_app, credentials, firestore

# Use the application default credentials
cred = credentials.ApplicationDefault()
initialize_app(cred, {
  'projectId': os.getenv('GOOGLE_CLOUD_PROJECT'),
})

db = firestore.client()

db.collection('settings').document("system").set({
    'release_stable': datetime.now(timezone.utc)
})