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

from datetime import datetime, timedelta, timezone
from firebase_admin import firestore, auth
from flask import Flask, abort, request, jsonify, g
from functools import wraps
import logging
import os
import sys
from uuid import uuid4
from .db import db

from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client

# not using signed cookies in flask
# SECRET_KEY = 'a secret key'

app = Flask(__name__)
app.config.from_object(__name__)

logging.basicConfig(level=logging.INFO)

tw_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
# tw_api_key = os.environ.get('TWILIO_API_KEY')
# tw_api_secret = os.environ.get('TWILIO_API_SECRET')
tw_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

# if not all([tw_account_sid, tw_api_secret, tw_api_key, tw_auth_token]):
if not all([tw_account_sid, tw_auth_token]):
    sys.exit("Twilio API auth incomplete")

client = Client(tw_account_sid, tw_auth_token)

def validate_user_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        id_token = request.headers['Authorization'].split(' ').pop()
        try:
            g.decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            logging.warning(e)
            return abort(401)
        if 'decoded_token' not in g or 'curbside_number' not in g.decoded_token:
            logging.warning('No from number in user claims uid: {}'.format(g.decoded_token['uid']))
            return abort(400)  
        return f(*args, **kwargs)
    return decorated_function


def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(tw_auth_token)
        # validator = RequestValidator(tw_api_secret)

        # Validate the request using its URL, POST data,
        # and X_TWILIO_SIGNATURE header
        logging.info(request.url)
        if not ('ngrok' in str(request.url)):
            request_valid = validator.validate(
                str(request.url).replace('http', 'https'),
                request.form,
                request.headers.get('X-TWILIO-SIGNATURE', ''))
        else:
            request_valid = validator.validate(
                # str(request.url),
                str(request.url).replace('http', 'https'),
                request.form,
                request.headers.get('X-TWILIO-SIGNATURE', ''))

        # Continue processing the request if it's valid, 
        # return a 403 error if it's not
        if request_valid:
            return f(*args, **kwargs)
        else:
            logging.warning("Signature invalid")
            logging.info(request.url)
            logging.info(request.headers)
            return abort(403)
    return decorated_function


@app.route("/sms", methods=['GET', 'POST'])
@validate_twilio_request
def sms_reply():

    db_update = {}
    sender = request.values.get('From')
    sender_msg = request.values.get('Body')
    tenant = request.values.get('To')
    db_update['sender'] = sender
    db_update['tenant'] = tenant
    db_update['last_updated_by'] = 'customer'

    now = datetime.now(timezone.utc)
    settings = {}
    doc = db.collection("settings").document(tenant).get()
    if doc.exists:
        settings = doc.to_dict()
    else:
        logging.warning("No settings found")
        abort(500)

    if 'dndEnabled' in settings and settings['dndEnabled']:
        resp = MessagingResponse()
        resp.message(
            settings.get('dndMessage', 'sorry, we are unavailable, please call our main number'))
        return str(resp)

    session_id = ''
    current_status = ''

    session_query = db.collection('sessions').where(
        'sender', '==', sender).where(
        'session_active', '==', True).order_by(
            'last_session_start', direction=firestore.Query.DESCENDING).limit(1)
    sessions = [s for s in session_query.stream()]
    # logging.info(len(sessions))
    if sessions:
        data = sessions[0].to_dict()
        session_id = data['session_id']
        current_status = data['status']
        if (now - data['last_message_time']) > timedelta(hours=2):
            db.collection('sessions').document(session_id).update({
                'status': 'expired',
                'session_active': False
            })
            session_id = ''
        if data['last_updated_by'] == 'system':
            # only update last message time to now if it is the first response to system
            db_update['last_message_time'] = now

    if not session_id:
        # new session
        session_id = str(uuid4())
        current_status = 'arrived'
        # db_update['session_id'] = session_id = str(uuid4())
        db_update['sender'] = sender
        db_update['session_id'] = session_id
        db_update['status'] = "arrived"
        db_update['last_session_start'] = now
        db_update['session_active'] = True
        db_update['first_message'] = sender_msg
        db_update['last_message_time'] = now
        db_update['last_message'] = str(sender_msg)
    else:
        db_update['status'] = "reply"
        # don't update last_message timestamp for customer reply
        # db_update['last_message_time'] = now
        db_update['last_message'] = str(sender_msg)

    # Get reply for status
    reply = ''
    status_stream = db.collection("statuses") \
        .where("label", "==", db_update['status']) \
        .where('tenant', '==', tenant) \
        .limit(1).stream()
    statuses = [s for s in status_stream]

    # logging.info(status_doc.exists)

    if not len(statuses):
        reply = 'oops, we are having some technical issues [nothing for {}]'.format(db_update['status'])
    else:
        status_doc = statuses[0]
        reply = status_doc.to_dict()["response"]
    # if not reply:
    #     reply = 'oops, we are having some technical issues [blank for {}]'.format(db_update['status'])

    added_messages = [{
            "status": current_status,
            "from": "customer",
            "message": db_update['last_message'],
            "time": now,
        }]
    resp = ''
    if reply != '':
        """Respond to incoming calls with a simple text message."""
        # Start our TwiML response
        resp = MessagingResponse()
        # Add a message
        # resp.message(reply, action=callback_base + session_id)
        resp.message(reply)
        added_messages.append({
            "status": db_update['status'],
            "from": "system",
            "message": reply,
            "time": now,
        })

    db_update['messages'] = firestore.ArrayUnion(added_messages)
    # logging.info(db_update)
    if sessions:  # session existed
        db.collection("sessions").document(session_id).update(db_update)
    else:
        db.collection("sessions").document(session_id).set(db_update)
    db.collection("sessions").document(session_id)
    if reply:
        return str(resp)
    return ('', 204)


# TODO could reflect state on sent messages with this callback
# currently these next two routes are not called, as not action is set on reply msgs
@app.route("/sms/callback", methods=['POST'])
@validate_twilio_request
def incoming_sms():
    # message_sid = request.values.get('MessageSid', None)
    # message_status = request.values.get('MessageStatus', None)
    return ('', 204)


@app.route("/sms/action/<session_id>", methods=['POST'])
@validate_twilio_request
def action(session_id):
    # message_sid = request.values.get('MessageSid', None)
    # message_status = request.values.get('MessageStatus', None)
    return ('', 204)


# This endpoint handles requests from the front end, authenticating with Firebase auth
@app.route("/send", methods=['POST'])
@validate_user_request
def sendReply():
    logging.info("step *******************")
    content = request.json
    message = client.messages \
        .create(
            body=content['msg'],
            from_=g.decoded_token['curbside_number'],
            to=content['recipient']
        )
    logging.info(message.sid)
    # all updates done client side
    return jsonify({"sid": message.sid})

# This endpoint handles requests from the front end, requesting caller ID details
@app.route("/cnam", methods=['POST'])
@validate_user_request
def lookupCNAM():
    if os.getenv("DISABLE_CNAM"):
        return jsonify({"cnam": "--"})
    content = request.json
    phone_number = client.lookups \
        .phone_numbers(content['sender']) \
        .fetch(type=['caller-name'])
    cnam = str(phone_number.caller_name["caller_name"])

    db.collection("sessions").document(content['session']).update({
        "caller_id": cnam
    })
    db.collection("caller_ids").document(content['sender']).set({
        "cnam": cnam
    })
    return jsonify({"cnam": cnam})


@app.route("/", defaults={'fpath': None})
@app.route("/<fpath>")
def public(fpath):
    logging.info(fpath)
    if not fpath:
        fpath = 'index.html'
    return app.send_static_file(fpath)


if __name__ == "__main__":
    port = os.getenv("PORT", "8080")
    app.run(debug=True, port=port, host="0.0.0.0")
