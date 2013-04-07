import os, sys
import simplejson
import time, datetime

#from flask import Flask, request, redirect, url_for
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import werkzeug
import random
from werkzeug import secure_filename

from dao.models import User, Request

import logging

import utils

SETTINGS = {"PORT": 6500}


app = Flask(__name__)
#Customize max content length
app.config['MAX_CONTENT_LENGTH']=1024*1024*1024
#Configure For Upload Folder
#app.config['UPLOAD_FOLDER'] = SETTINGS['UPLOAD_FOLDER']
#Default Logger for our Calls
utils.addFileLogger(app.logger, "bms_server.log", 2)
#Logger for Werkzerg / Flask Related Requests
request_logger = logging.getLogger("request_log")
utils.addFileLogger(request_logger, "request_log.log", 2)
werkzeug._internal._logger = request_logger

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def get_pring_context(request):
    #return {'sessionkey': "1123",
    #        'Username': "abdul",
    #        'UserGUID': "11234",
    #        'Fullname': "Abdul Majeed"}
    #return {'sessionkey': "123",
    #        'Username': "abdul",
    #        'UserGUID': "1234",
    #        'Fullname': "Abdul Majeed"}
    #return {'sessionkey': request.form.get('SessionKey', None),
    #        'Username': request.form.get('Username', None),
    #        'UserGUID': request.form.get('UserID', None),
    #        'Fullname': request.form.get('Fullname', None)}
    return {'sessionkey': session.get('SessionKey', None),
            'Username': session.get('Username', None),
            'UserGUID': session.get('UserID', None),
            'Fullname': session.get('Fullname', None)}

@app.route('/registersession/', methods=['GET', 'POST'])
def register_session():
    context = {'sessionkey': request.form.get('SessionKey', None),
            'Username': request.form.get('Username', None),
            'UserGUID': request.form.get('UserID', None),
            'Fullname': request.form.get('Fullname', None)}
    for key in context:
        session[key] = context[key]

@app.route('/', methods=['GET', 'POST'])
def landing():
    """
        if registered
            -> update donation date
        else
            -> registeration process
    """
    user_context = get_pring_context(request)
    if User.get_user_from_id(user_context["UserGUID"]):
        return render_template('register_user_general.html')
        #Form to Update Last Registeration Date
        #raise Exception("Not Implemented")
    else:
        return render_template('register_user_general.html')

@app.route('/pring/register/general/', methods=['GET', 'POST'])
def general_registeration():
    user_context = get_pring_context(request)
    is_donor = request.form.get("is_donor")
    name = request.form.get("name")
    guid = user_context["UserGUID"]
    if not guid:
        raise Exception("Guid not coming in from Pring")
    else:
        if not guid.strip():
            raise Exception("Guid not coming in from Pring")
    User.update_user({'guid': guid,'is_donor': True, 'name': name})
    if is_donor == "yes":
        return render_template('register_user_donor.html')
    else:
        return render_template('register_user_receiver.html')

@app.route('/pring/register/donor/', methods=['GET', 'POST'])
def donor_registeration():
    user_context = get_pring_context(request)
    bloodgroup = request.form.get("bloodgroup")
    last_donation_date = request.form.get("last_donation_date")
    (day, month, year) = tuple(last_donation_date.split("/"))
    maketime = lambda d,m,y: time.mktime(datetime.datetime(year=int(y), month=int(m), day=int(d)).timetuple())
    timestamp = maketime(day, month, year)
    User.update_user({'guid': user_context["UserGUID"], 'bloodgroup': bloodgroup, 'last_donation_date': timestamp})
    return render_template('register_user_donor_complete.html')

@app.route('/pring/register/receiver/', methods=['GET', 'POST'])
def receiver_registeration():
    user_context = get_pring_context(request)
    bottles = request.form.get("bottles")
    specificity = True if request.form.get("specificity") == "yes" else False
    Request.create_request({'guid': user_context["UserGUID"],'bottles': int(bottles), 'specificity': specificity})
    if specificity:
        raise Exception("Not Implemented")
        #return render_template('register_user_receiver_s.html')
    return render_template('register_user_receiver_complete.html')

@app.route('/pring/register/receiver/specific/', methods=['GET', 'POST'])
def receiver_registeration_specific():
    user_context = get_pring_context(request)
    bloodgroup = request.form.get("bloodgroup")
    db.update_user({'guid': user_context["UserGUID"],'bloodgroup': int(bloodgroup)})
    return render_template('register_user_receiver_complete.html')

@app.route('/usermatching/', methods=['GET', 'POST'])
def user_matching():
    user_context = get_pring_context(request)
    user_guid = user_context["UserGUID"]
    req = Request.get_request_from_user_id(user_guid)
    if not req:
        return "</p>You dont have an open request at a moment</p>"
    user_names = []
    if not req["specificity"]:
        newtime = time.mktime(datetime.datetime.now().timetuple())
        matchedtime = newtime - 4*31*24*3600
        matched_users = User.collection.find({})
        for matched_user in matched_users:
            if "last_donation_date" not in matched_user:
                continue
            if matched_user["last_donation_date"] < matchedtime:
                #This will be replaced with Pring User Name
                user_names.append(matched_user["name"])
                req["bottles"] -= 1
                matched_user["last_donation_date"] = newtime
                matched_user.save()
                req.save()
                if req["bottles"] <= 0:
                    req["is_matched"] = True
                    req.save()
                    break
    if user_names:
        return "<p>Please message the following users on pring %s</p>"%(",".join(user_names))
    else:
        return "<p>System unable to detect matches please try again</p>"

@app.route('/matching/', methods=['GET', 'POST'])
def matching():
    user_context = get_pring_context(request)
    st = ""
    reqs = list(Request.collection.find({'is_expired': False, 'is_matched': False}))
    for req in reqs:
        if not req["specificity"]:
            st += "Not Specific \r\n"
            newtime = time.mktime(datetime.datetime.now().timetuple())
            matchedtime = newtime - 4*31*24*3600
            matched_users = User.collection.find({})
            for matched_user in matched_users:
                if matched_user["last_donation_date"] < matchedtime:
                    #{"last_donation_date": { "$gt": matchedtime}}                
                    req["bottles"] -= 1
                    matched_user["last_donation_date"] = newtime
                    matched_user.save()
                    req.save()
                    if req["bottles"] <= 0:
                        req["is_matched"] = True
                        req.save()
                        break
        else:
            raise Exception("Not Implemented")
    raise Exception("Matching Complete")
    return "Matching Complete"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=SETTINGS['PORT'])
