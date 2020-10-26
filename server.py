from flask import Flask, jsonify, request
import logging
import numpy as np
import json


app = Flask(__name__)


def init_db():
    """Initialize databases and setup logging config

    For program requirements and function testing, intialize both patients
    and attendings databases with some fake but well-structuredinfo. Also,
    setup logging with basic configurations.

    Args:
        None
    Returns:
        lists: patient database and attending database, both as lists
    """
    # Initialize the patients database with 3 fake patients
    patient_db = [{'patient_id': 120, 'attending_username': 'Tom',
                   'patient_age': 23,
                   'heart_rate_history': [{'heart_rate': 101,
                                           'status': 'tachycardic',
                                           'timestamp': '2018-03-09 11:00:36'},
                                          {'heart_rate': 104,
                                          'status': 'tachycardic',
                                           'timestamp':
                                               '2018-03-10 11:00:36'}]},
                  {'patient_id': 300, 'attending_username': 'Tom',
                   'patient_age': 25,
                   'heart_rate_history': [{'heart_rate': 75,
                                           'status': 'not tachycardic',
                                           'timestamp':
                                               '2019-10-10 11:00:36'}]},
                  {'patient_id': 500, 'attending_username': 'Tom',
                   'patient_age': 29, 'heart_rate_history': []},
                  {'patient_id': 250, 'attending_username': 'Josh',
                   'patient_age': 20, 'heart_rate_history': []}
                  ]
    print("Initial patient database:")
    print(patient_db)
    print("\n")
    # patient id 120, corresponding to attending Tom
    # patient id 300, corresponding to attending Tom, and has age 25
    # patient id 500, empty heart history

    # Initialize the attending database with the first attending user
    # attending_db = list()
    attending_db = [{'attending_username': 'Tom',
                     'attending_email': 'tom@gmail.com',
                     'attending_phone': '919-865-5674'},
                    {'attending_username': 'Lady',
                     'attending_email': 'Lady@gmail.com',
                     'attending_phone': '919-222-333'}]
    print("Initial attending database:")
    print(attending_db)
    print("\n")

    return patient_db, attending_db


patient_db, attending_db = init_db()


def logging(level, description):
    """Log all the events
    log all the events, user can decide the level and customize the
    description
    Args:
        level (int): the logging level
        description (string): The string add to the log
    Returns:
        None
    """
    import logging
    # only log the level above INFO
    logging.basicConfig(filename="HR_Sentinel.log", level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(message)s")
    if level == 0:
        logging.info(description)
    elif level == 1:
        logging.warning(description)
    elif level == 2:
        logging.error(description)
    return


def add_patient_to_database(patient_id=None, attending_username=None,
                            patient_age=None):
    """Add a new patient with his info to patient database

    Add, or say register, a new patient info in a dictionary, with
    his id, username and age to existing patient database

    Args:
        patient_id(int): the id number of the added patient
        attending_username(str): the corresponding username of the
                                 added patient's attending
        patient_age(int): the age number of the added patient

    Returns:
        None, but the patient database 'patient_db' is enlarged
    """
    new_patient = {"patient_id": patient_id,
                   "attending_username": attending_username,
                   "patient_age": patient_age,
                   "heart_rate_history": list()}
    patient_db.append(new_patient)
    logging(0, "New patient added. Patient ID:{}".format(patient_id))
    print("patient database:\r")
    print(patient_db)


def add_attending_to_database(attending_username, attending_email=None,
                              attending_phone=None):
    """Add a new attending with his info to patient database

    Add, or say register, a new attending info in a dictionary,
    with his username, email and phone number to existing
    attending database

    Args:
        attending_username(str): the username of the added
                                 attending
        attending_email(str): the email address of the added
                              attending
        attending_phone(str): the phone number of the added
                              attending but it is in the form
                              of string, either numeric or
                              with necessary symbols
    Returns:
        None, but the attending database 'attending_db' is
        enlarged
    """
    new_attending = {"attending_username": attending_username,
                     "attending_email": attending_email,
                     "attending_phone": attending_phone}
    attending_db.append(new_attending)
    logging(0, "New attending added. Username:{} Email:{}".
            format(attending_username, attending_email))
    print("attending database:\r")
    print(attending_db)


@app.route("/api/new_patient", methods=["POST"])
def post_new_patient():
    """Post a new patient to patient database

    A new route for users to post a new patient to database
    after processing and checking the input data

    Args:
        None
    Returns:
        Correct server response and the corresponding status code
    """
    # Receive request data
    in_data = request.get_json()
    # Call functions
    answer, server_status = process_new_patient(in_data)
    # Return results
    return answer, server_status


def process_new_patient(in_data):
    """Process and add the new patient to patient_db

    Process new patient information, check the input format, validate age and
    add the new patient information to the data base

    Args:
        in_data (dict): Include the "patient_id",
        "attending_username", "patient_age" information

    Returns:
        str, int: The server's response and corresponding status code

    """
    expected_key = ["patient_id", "attending_username", "patient_age"]
    expected_types = [int, str, int]
    parse_string(in_data, "patient_id")
    parse_string(in_data, "patient_age")
    validate_input = validate_post_input(in_data, expected_key, expected_types)
    if validate_input is not True:
        return validate_input, 400
    valid_age = validate_age(in_data["patient_age"])
    if valid_age is not True:
        return valid_age, 400
    valid_primary_key = primary_key(patient_db, "patient_id",
                                    in_data["patient_id"])
    if valid_primary_key is not True:
        return valid_primary_key, 400
    add_patient_to_database(in_data["patient_id"],
                            in_data["attending_username"],
                            in_data["patient_age"])
    return "Patient successfully added", 200


def validate_age(age):
    """ Validate the age

    Determine if the input age of patient is valid. If it os too small (<=0) or
    too big (>=150) it is determined as a invalid number.

    Args:
        age (int): The age of the new patient

    Returns:

    """
    if age <= 0:
        return "Invalid age, must be greater than 0!"
    if age >= 150:
        return "Invalid age, human can't live so long!"
    else:
        return True


def primary_key(data_base, key, key_value):
    """Check the primary key value duplicate or not

    Make sure the primary key of the database is unique, check if the primary
    key value has been existed in the database.

    Args:
        data_base (dict): The data base you want to check
        key (str): The primary key
        key_value : This can be multiple datatype, determines the primary key
        value you want to compare to see if has existed

    Returns:
        True or str: indicate if the primary key value is unique

    """
    for record in data_base:
        if record[key] == key_value:
            return "{} is the primary key, should be unique!".format(key)
    return True


def parse_string(dict_in, key_to_parse):
    """parse the string of a key value of the dict

    By use this function, we can turn a string which only includes the digits
    into an int. If the string also contains chars or it is a integer itself,
    the function will return the dictionary unchanged

    Args:
        dict_in (dict): The dictionary you want to parse
        key_to_parse (str): The key name of the key value you want to parse

    Returns:
        str: indicate if the key values has been parsed or don't need to be
        parsed

    """
    try:
        if type(dict_in[key_to_parse]) is str:
            if dict_in[key_to_parse].isdigit() is True:
                dict_in[key_to_parse] = int(dict_in[key_to_parse])
                return "Successfully parsed!"
    except KeyError:
        return "The key to parse does not exist."
    return "No need to parse."


@app.route("/api/new_attending", methods=["POST"])  # YT
def post_new_attending():
    """Post a new attending to attending database

    A new route for users to post a new attending to database
    after processing and checking the input data.

    Args:
        None
    Returns:
        Correct server response and the corresponding status code
    """
    in_data = request.get_json()
    answer, server_status = process_new_attending(in_data)
    return answer, server_status


def process_new_attending(in_data):
    """process the new attending information to be add to database

    Process the new attending information and add it into the attending
    database. Check if the input meets with the stype and the correct
    information.

    Args:
        in_data (dict): The dictionary contains the following information.
        "attending_username", "attending_email", "attending_phone"

    Returns:
        str, int: The internal status information of the server and
        the corresponding status code.

    """
    expected_key = ["attending_username", "attending_email", "attending_phone"]
    expected_types = [str, str, str]
    validate_input = validate_post_input(in_data, expected_key, expected_types)
    if validate_input is not True:
        return validate_input + ", please make sure all your info are " \
                            "in the type of string!", 400
    info_valid = attending_info_detect(in_data)
    attending_exist = if_attending_exist(in_data)
    if attending_exist is not False:
        return attending_exist + "Please create a non redundant username to " \
                                 "write a new attending into database", 400
    if info_valid is not True:
        return info_valid + "please make sure you've entered correct info", 400
    add_attending_to_database(attending_username=in_data["attending_username"],
                              attending_email=in_data["attending_email"],
                              attending_phone=in_data["attending_phone"])
    return "Attending:'{}' successfully added"\
           .format(in_data["attending_username"]), 200


def if_attending_exist(in_data):
    """Check if the attending name already exist

    Check if the attending has already exist in the database. (prevent
    duplicate attending)

    Args:
        in_data (dict): the dictionary includes the attending information

    Returns:
        False or str: indicate if the attending already existed in the database

    """
    attending_username_list = []
    for attending in attending_db:
        attending_username_list.append(attending["attending_username"])
    if in_data["attending_username"] in attending_username_list:
        return "The attending already exists in database! "
    return False


def validate_post_input(in_data, expected_key, expected_types):
    """Validate the post input

    Validate if the posted input has all the required keys.Or if the input
    information has the correct datatype. If not send a warning from the server
    to the client.

    Args:
        in_data (dict): The post input information
        expected_key: The keys should exist in the input dictionary
        expected_types (type): The expected type of the corresponding
        key values

    Returns:
        True or str: indicate if the posted input meets with the requirements

    """
    for key, v_type in zip(expected_key, expected_types):
        if key not in in_data.keys():
            return "{} key not found in input".format(key)
        if type(in_data[key]) != v_type:
            return "{} key value has wrong variable type".format(key)
    return True


def attending_info_detect(in_data):
    """Detect if the email address is validate or not

    See if the email address include the @ sign to determine if it is a valid
    email address

    Args:
        in_data (dict): The dictionary that includes the attending's email
        address

    Returns:
        str or True: Indicate if it is a valid email address

    """
    good_email = "@" in in_data["attending_email"]
    if good_email is not True:
        return "You entered a invalid email address, "
    return True


@app.route("/api/heart_rate", methods=["POST"])
def post_add_heart_rate():
    """Post a patient's heart rate data to patient database

    A new route for users to post a patient's heart rate
    record to database in the correct list for recording,
    after processing and checking the input data. Also,
    an email will be sent to that patient's attending if
    a tachycardic heart rate is posted.

    Args:
        None
    Returns:
        str, int: Correct server response and the corresponding status code
    """
    in_data = request.get_json()
    answer, status_code = process_add_heart_rate(in_data)
    return answer, status_code


def process_add_heart_rate(in_data):
    """process the input heart rate data and add to database

    The function that call other subfunctions to process the heart rate
    information and attach them to the database. It also determine if it is
    tachycardia or not. If it is , it will send an email to the attending with
    the information of heart rate, time stamp.

    Args:
        in_data (dict): The dictionary that include the following information
        "patient_id", "heart_rate"

    Returns:
        str, int: indicate the the heart rate information has been successfully
        added to the database. Besides it will also send an email to the
        attending if problem(tachycardia) happened.

    """
    import datetime
    time = datetime.datetime.now()
    timestamp = time_formatter(time, "%Y-%m-%d %H:%M:%S")
    expected_key = ["patient_id", "heart_rate"]
    expected_types = [int, int]
    parse_string(in_data, "patient_id")
    parse_string(in_data, "heart_rate")
    valid_data = validate_post_input(in_data, expected_key, expected_types)
    if valid_data is not True:
        return valid_data, 400
    patient = find_correct_patient(in_data["patient_id"])
    if patient is False:
        return "Could not find this patient in database", 400
    attending = find_correct_attending(patient["attending_username"])
    if attending is False:
        return "Could not find attending of this patient in database", 400
    add_heart_rate_to_database(patient, in_data["heart_rate"],
                               is_tachycardic(in_data, patient,
                                              attending, timestamp), timestamp)
    print(patient_db)
    return "Heart rate info successfully added", 200


def add_heart_rate_to_database(patient, heart_rate, status, timestamp):
    """ Add the heart_rate information to the database

    Add the heart rate information which includes the following keys to the
    database. heart_rate": heart_rate, "status": status,"timestamp": timestamp

    Args:
        patient (dict): The correct patient found by the helper function
        heart_rate (int): The current heart rate of the patient
        status (str): is tachycardic or not
        timestamp (datetime.datetime): The timestamp of now

    Returns:
        None

    """
    data_to_add = {"heart_rate": heart_rate,
                   "status": status,
                   "timestamp": timestamp}
    patient["heart_rate_history"].append(data_to_add)


# This function will not be test, since it is directly calling the
# Function of datetime.dateime.strftime
def time_formatter(time_in, time_format):
    """Time stamp format checker

    Check if the input time stamp meet with the required time format, if not,
    change it to the correct format

    Args:
        time_in (datetime.datetime): The input timestamp
        time_format (str): The format you want the timestamp to follow

    Returns:
        datetime.datetime: the timestamp with the corresponding format

    """
    time_out = str(time_in.strftime(time_format))
    return time_out


def is_tachycardic(dict_in, patient, attending, timestamp):
    """ See if the heart rate is normal or not and send the email

    Args:
        dict_in (dict): The dictionary of patient information
        patient (dict): The patient found by the helper function
        attending (dict): The attending found by the helper function
        timestamp (datetime.datetime): The timestamp of now

    Returns:
        str: "tachycardic" or "not tachycardic"

    """
    flag = 0
    patient_id = dict_in["patient_id"]
    age = patient["patient_age"]
    rate = dict_in["heart_rate"]
    email = attending["attending_email"]
    if age < 1:
        if rate > 169:
            flag = 1
    elif 1 <= age <= 2:
        if rate > 151:
            flag = 1
    elif 3 <= age <= 4:
        if rate > 137:
            flag = 1
    elif 5 <= age <= 7:
        if rate > 133:
            flag = 1
    elif 8 <= age <= 11:
        if rate > 130:
            flag = 1
    elif 12 <= age <= 15:
        if rate > 119:
            flag = 1
    else:
        if rate > 100:
            flag = 1

    if flag == 0:
        return "not tachycardic"
    elif flag == 1:
        email_sender(email, patient_id, rate, timestamp)
        return "tachycardic"


def email_sender(email, patient_id, rate, timestamp):
    """ The helper function that send the email to attendings

    This function will post information to the Duke server and call the
    function there to send the email

    Args:
        email (str): The email address of the recepient
        patient_id: The id of the patient
        rate: The current heart rate of the patient
        timestamp: The time stamp of now

    Returns:
        str: the status code, returned text from the server and the email
        contents

    """
    import requests
    new_email = {
        "from_email": "sentinel_server@duke.edu",
        "to_email": email,
        "subject": "Tachycardia Detected! Patient ID: {}".format(patient_id),
        "content": "Warning! The heart rate of patient ID {}"
                   " is {} bpm @ {}!"
                   "A tachycardia happened!".format(patient_id,
                                                    rate, timestamp)
    }
    logging(0, "Warning! Tachycardic detected!"
               " patient ID:{} heart rate:{} --> "
               "Attending email:{}".format(patient_id, email, rate))
    r = requests.post("http://vcm-7631.vm.duke.edu:5007/hrss/send_email",
                      json=new_email)
    print(r.status_code)
    print(r.text)
    print(new_email)
    return r.status_code, r.text, new_email


def find_correct_patient(patient_id):
    """The helper function to find the correct patient

    This function will help to find the correct patient in the patient data
    base according to the patient id. If the id does not exist, it will send
    a warning information to the client to indicate this.

    Args:
        patient_id (int): The id of the patient you want to find in the
        data base.

    Returns:
        dict or str: if the patient is found return the patient, otherwise,
        indicate that this patient does not exist in the database.

    """
    # patient_id must be an int
    for patient in patient_db:
        if patient["patient_id"] == patient_id:
            return patient
    return False


def find_correct_attending(attending_username):
    """The helper function to find the correct attending

    This function will help to find the correct attending in the attending data
    base according to the attending_usename.
    If the use_name does not exist, it will send
    a warning information to the client to indicate this.

    Args:
        attending_username (int): The id of the attending you want to
        find in the
        data base.

    Returns:
        dict or str: if the attending is found return the attending information
        ,otherwise indicate that this attending does not exist in the database.

    """
    for attending in attending_db:
        if attending["attending_username"] == attending_username:
            return attending
    return False


@app.route("/api/status/<patient_id>", methods=["GET"])
def get_latest_result(patient_id):
    """Get a patient's latest heart rate info in a dictionary

    A new route for users to get a dictionary of patient's
    heart rate history from database in the form of .json
    after processing and checking the input data

    Args:
        patient_id(str): the numeric string of target patient
    Returns:
        Correct server response and the corresponding status code
    """
    answer, server_status = get_test(patient_id)
    return answer, server_status


def get_test(patient_id):
    """ Get the latest test result

    The get function that get the lastest heartrate information and diagnosis
    information

    Args:
        patient_id (int): patient's id

    Returns:
        str, id: the satus of the server and the corresponding server code

    """
    int_id = id_is_int(patient_id)
    if int_id is True:
        patient = find_correct_patient(int(patient_id))
        if patient is False:
            return "Could not find a matched patient in database", 400
        have_latest_hr = latest_hr(patient)
        if have_latest_hr is False:
            return "This patient doesn't have any heart rate history", 400
        return jsonify(have_latest_hr), 200
    return int_id, 400


def id_is_int(patient_id):
    """ Check if patient id is integer

    Check if the patient's id is a integer

    Args:
        patient_id (int): id number of the patient

    Returns:
        True or str: indicate if the input patient id is an integer

    """
    try:
        int(patient_id)
        return True
    except ValueError:
        return "Please use an integer or a numeric string containing " \
           "an ID number but without any letter"


def latest_hr(patient):
    """Get the latest heart rate history.

    This function will fetch the lasted information of patient. Include
    "heart rate", "status", "timestamp". It will also inform the client if
    the patient's heart rate history does not exist.

    Args:
        patient (dict): The correct patient you find

    Returns:
        dict: The latest heart history

    """
    if len(patient["heart_rate_history"]) == 0:
        return False
    newest_hr = patient["heart_rate_history"][-1]
    latest_heart_rate = {"heart_rate":
                         newest_hr["heart_rate"],
                         "status":
                         newest_hr["status"],
                         "timestamp":
                         newest_hr["timestamp"]}
    return latest_heart_rate


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_heart_rate_list(patient_id):
    """Get a patient's all heart rate info in a list

    A new route for users to get a list of patient's
    heart rate history from database after processing and
    checking the input data

    Args:
        patient_id(str): the numeric string of target patient
    Returns:
        Correct server response and the corresponding status code
    """
    patient = find_correct_patient(int(patient_id))
    if patient is False:
        return "Could not find patient in database", 400
    heart_rate_list = []
    for heart_rate_data in patient["heart_rate_history"]:
        heart_rate_list.append(heart_rate_data["heart_rate"])
    print("The heart rate history of patient {} is retrieved!\n".
          format(patient_id))
    print(heart_rate_list)
    return jsonify(heart_rate_list), 200


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def get_average_results(patient_id):
    """Get a patient's average heart rate as a float number

    A new route for users to get a float number of patient's
    heart rate history from database in the form of .json
    after processing and checking the input data

    Args:
        patient_id(str): the numeric string of target patient
    Returns:
        Correct server response and the corresponding status code
    """
    answer, server_status = get_average(patient_id)
    return jsonify(answer), server_status


def get_average(patient_id):
    """ Find the average value of all the heart rate history

    This is the function that get the average heart rate of a patient.
    This Function will also check if the user does exist or if if the patient
    has the heart rate history .

    Args:
        patient_id (int): The id of the patient

    Returns:
        int, int or str, int: indicate if the average heart rate is get or not,
        with the corresponding status code
    """
    int_id = id_is_int(patient_id)
    # function id_is_int() has been defined in Route /status/<patient_id>
    if int_id is True:
        patient = find_correct_patient(int(patient_id))
        # function find_id() has been defined in Route /status/<patient_id>
        if patient is False:
            return "Could not find a matched patient in database", 400
        have_average_hr = average_hr(patient)
        if have_average_hr is False:
            return "This patient doesn't have any heart rate history", 400
        return have_average_hr, 200
    return "Please use an integer or a numeric string containing " \
           "an ID number but without any letter", 400


def average_hr(patient):
    """get the average heart rate

    calculate  the average hear trate of the patient of all the heart rate
    records

    Args:
        patient (dict): The correct patient found in the database

    Returns:
        int or False: the average heart rate of the patient's all heart rate
        record is returned or report the problem if no heart rate record is
        found

    """
    if len(patient["heart_rate_history"]) == 0:
        return False
    hr_list = []
    for single_hr in patient["heart_rate_history"]:
        hr_list.append(single_hr["heart_rate"])
    avg_hr = float(np.mean(hr_list))
    return avg_hr


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def post_average():
    """Post a time tage and get a patient's average heart rate
       since that time

    A new route for users to post a specific time and get that
    patient's heart rate average value from database as integer
    in the  form of .json after processing and checking the
    input data

    Args:
        None
    Returns:
        Correct server response and the corresponding status code
    """
    in_data = request.get_json()
    answer, server_status = calculate_interval_average(in_data)
    return jsonify(answer), server_status


def calculate_interval_average(in_data):
    """ Calculate the ave heart rate in an time interval (after a time stamp)

    This function will call other helper functions to calculate the average
    heart rate after a time stamp. If the patient can not be found in the
    database it will send a warning information to the client, if no data found
    after the appointed timestamp, the client will be informed. And if the
    average value is calculated it will be sent to the client.

    Args:
        in_data (dict): With the information of patient id and timestamp

    Returns:
        str, int or int, int: return the average heart rate in the time
        interval or report the error information to the client with the
        status code.
    """
    expected_key = ["patient_id", "heart_rate_average_since"]
    expected_types = [int, str]
    parse_string(in_data, "patient_id")
    validate_input = validate_post_input(in_data, expected_key, expected_types)
    if validate_input is not True:
        return validate_input, 400
    time_format = validate_time_format(in_data)
    if time_format is not True:
        return time_format, 400
    patient = find_correct_patient(in_data["patient_id"])
    if patient is False:
        return "Could not find patient in database", 400
    interval_list = find_interval_rates(in_data, patient)
    if (not interval_list) is True:
        return "Could not find heart rate since the given time", 400
    average_rate = int(list_average(interval_list))
    return average_rate, 200


def list_average(list_in):
    """List average calculator

    Calculate the average value of a list of numbers

    Args:
        list_in (list): a list of number

    Returns:
        float: The average value of a list number

    """
    answer = sum(list_in)/len(list_in)
    return answer


def find_interval_rates(in_data, patient):
    """ Find heart rate in a given time interval

    Find the list of heart rate that is recorded after the given time stamp.

    Args:
        in_data (dict): The dictionary include the information of the patients
        id and the time stamp that we want to calculate the average heart rate
        since the time stamp
        patient (dict): The correct patient we found in the data base

    Returns:
        list: a list of heart rate value or a empty list

    """
    from datetime import datetime
    t1 = in_data["heart_rate_average_since"]
    timestamp1 = datetime.strptime(t1, '%Y-%m-%d %H:%M:%S')
    get_heart_rate_list = []
    for heart_rate_data in patient["heart_rate_history"]:
        timestamp2 = datetime.strptime(heart_rate_data["timestamp"],
                                       '%Y-%m-%d %H:%M:%S')
        if max(timestamp1, timestamp2) == timestamp2:
            get_heart_rate_list.append(heart_rate_data["heart_rate"])
    return get_heart_rate_list


def validate_time_format(time_in):
    """time stamp format checker

    validate if the timestamp since is given in the correct format or not.
    if not give an warning for the client to change the timestamp format.

    Args:
        time_in (datetime.datetime): The time stamp in for check

    Returns:
        True or str: depends on if the format of the timestamp meets the
        requirements or not

    """
    from datetime import datetime
    try:
        datetime.strptime(time_in["heart_rate_average_since"],
                          '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return "The time in does not satisfy the format, " \
               "e.g. '2018-03-09 11:00:36'"


@app.route("/api/patients/<attending_username>", methods=["GET"])
def get_all_patients(attending_username):
    """Get an attending's all patients' latest heart rate
       in a list

    A new route for users to get a list of dictionary of
    all patients' lastest heart rate info which is registered
    to the wanted attending, from database, in the form of .json
    after processing and checking the input data.

    Args:
        attending_username(str): the username of target attending
    Returns:
        Correct server response and the corresponding status code
    """
    answer, server_status = all_patients(attending_username)
    return answer, server_status


def all_patients(attending_username):
    """Return correct results or server errors and their
       status code

    If the attending's username as an input can't match patients,
    or the name itself is invalid, returns error and code 400;
    otherwise return all patients' latest heart rate in a list
    of the target attending.

    Args:
        attending_username(str): the username of target attending
    Returns:
        A list of dictionaries with required patients' heart rate
        info and status code 200, or relevant error statements
        and status code 400
    """
    if_str_username = str_username(attending_username)
    if if_str_username is True:
        if_username_match = match_username(attending_username)
        if if_username_match is True:
            all_patients_data = return_data_list(attending_username)
#           return jsonify({"Attending {}'s all patients' info:"
            #           .format(attending_username):
#                                all_patients_data}), 200
            return json.dumps(all_patients_data), 200
        return if_username_match, 400
    return if_str_username, 400


def str_username(attending_username):
    """Determine if the input username is valid and meaningful

    Check if the attending's username contain any number and
    return corresponding results

    Args:
        attending_username(str): the username of target attending
    Returns:
        A string that states the attending's username is invalid
        due to the numeric elements it contains, or a bool
        variable True that indicates the username is valid.
    """
    import re
    if bool(re.search(r'\d', attending_username)) is False:
        return True
    else:
        return "Please enter a valid username string with no numbers!"


def match_username(attending_username):
    """Match the attending's name with curren database and return
       appropriate results

    Match the patients' attending in database with the target
    attending, return True if matched and a string of error
    description if unmatched.

    Args:
        attending_username(str): the username of target attending
    Returns:
        A string that states the attending's username can't match
        any patient in the database, or a bool variable True that
        indicates the username does have matched patient.
    """
    patients_attending_list = []
    for patient in patient_db:
        patients_attending_list.append(patient["attending_username"])
    if attending_username not in patients_attending_list:
        return "Sorry, this physician attending doesn't have any " \
               "matched patient in the database"
    return True


def return_data_list(attending_username):
    """Return an attending's all patients' latest heart rate
       in a list

    Match the patients' attending in database with the target
    attending, and accumulate all matched patients' latest
    heart rate in a list of pre-designed dictionaries

    Args:
        attending_username(str): the username of target attending
    Returns:
        A list which consists of dictionaries
    """
    data_list = []
    # try:
    for patient in patient_db:
        if patient["attending_username"] == attending_username:
            if len(patient["heart_rate_history"]) == 0:
                dic = {"patient_id": patient["patient_id"],
                       "last_heart_rate": "No heart rate available"}
            else:
                dic = {"patient_id": patient["patient_id"],
                       "last_heart_rate": patient["heart_rate_"
                                                  "history"][-1]["heart_rate"],
                       "last_time":
                           patient["heart_rate_history"][-1]["timestamp"],
                       "status": patient["heart_rate_history"][-1]["status"]}
            data_list.append(dic)
    return data_list
    # except IndexError:
    #     return


if __name__ == '__main__':
    # The main entrance of the function
    # No main() function is designed so no docstring
    print("running")
    logging(0, "The Data base is initialized!")
    app.run(debug=True)
