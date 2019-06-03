from datetime import datetime, timedelta

import flask_cors
from bson import json_util, ObjectId
from flask import Flask, render_template, request, session, json
from src.common.database import Database
from src.models.education_officers import EducationOfficers
from src.models.garmentICO import GarmentICO
from src.models.garmentOvr import GarmentDistrict
from src.models.installment import Installment
from src.models.intent import Intent
from src.models.memberProfile import memberProfile
from src.models.memberTransactions import memberTransactions
from src.models.user import User

app = Flask(__name__)  # main
flask_cors.CORS(app)
app.secret_key = "commercial"


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def login_form():
    return render_template('login.html')


@app.route('/register')
def register_form():
    return render_template('register.html')


@app.route('/authorize/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    valid = User.valid_login(email, password)
    User.login(email)
    user = User.get_by_email(email)

    if valid:
        if user.designation == 'HQ Staff':
            return render_template('profile_hq.html', user=user)
        elif user.designation == 'Accountant':
            return render_template('profile_accountant.html', user=user)
        else:
            return render_template('profile_dswo.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/authorize/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    designation = request.form['designation']
    district = request.form['district']
    society = request.form['society']

    User.register(email, password, username, designation, district, society)

    user = User.get_by_email(email)

    if user.designation == 'HQ Staff':
        return render_template('profile_hq.html', user=user)
    elif user.designation == 'Accountant':
        return render_template('profile_accountant.html', user=user)
    else:
        return render_template('profile_dswo.html', user=user)


@app.route('/change_password/<string:_id>', methods=['POST', 'GET'])
def change_password(_id):
    if len(_id) <= 3:
        user = User.get_by_id(int(_id))
    else:
        user = User.get_by_id(_id)
    if request.method == 'GET':
        return render_template('update_password.html', user=user)
    else:
        old_password = request.form['oldPassword']
        newPassword = request.form['newPassword']
        newPasswordAgain = request.form['newPasswordAgain']

    if user.password == old_password:
        if newPassword == newPasswordAgain:
            User.change_password(user._id, new_password=newPassword)
            return render_template('passwords_changed.html', user=user)
        else:
            return render_template('passwords_dont_match.html', user=user)
    else:
        return render_template('passwords_dont_match.html', user=user)


##########################
# Add Installment
##########################

@app.route('/add_installment/<string:intent_id>', methods=['POST', 'GET'])
def installment_form(intent_id):
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        if request.method == 'GET':
            return render_template('installment_form.html', user=user, intent_id=intent_id)

        else:
            installment_num = request.form['installmentNum']
            district = request.form['district']
            center = request.form['society']
            garment_type = request.form['gType']
            garment_size = request.form['gSize']
            set_id = request.form['setID']
            issue_date = request.form['issueDate']
            units_required = request.form['unitsRequired']
            deadline = request.form['deadline']
            units_pm = request.form['unitsPM']
            total_wages = request.form['totalWages']
            eo_name = request.form['EO']
            user_id = user._id

            installment = Installment(intent_id=intent_id, district=district, center=center, garment_type=garment_type,
                                      units_required=units_required, deadline=deadline,
                                      total_wages=total_wages,
                                      units_pm=units_pm, user_id=user_id, set_id=set_id, garment_size=garment_size,
                                      installment_num=installment_num, uploaded_date=issue_date, eo=eo_name)

            installment.save_to_mongo()

            return render_template('installment_added.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/update_installment/<string:_id>', methods=['POST', 'GET'])
def update_installment_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            if user.designation == 'DSWO/ICO':
                return render_template('update_installment_form.html', user=user, installment_id=_id)
            else:
                return render_template('update_installment_form_society.html', user=user, installment_id=_id)

        else:
            if user.designation == 'DSWO/ICO':
                installment_num = request.form['installmentNum']
                district = request.form['district']
                center = request.form['society']
                garment_type = request.form['gType']
                issue_date = request.form['issueDate']
                units_required = request.form['unitsRequired']
                deadline = request.form['deadline']
                units_pm = request.form['unitsPM']
                set_id = request.form['setID']
                eo_name = request.form['EO']
                user_id = user._id

                garment = Database.find("GarmentICO", {"garment_type": garment_type})
                wage_per_unit = None

                for result_object in garment[0:1]:
                    wage_per_unit = result_object['wage_per_unit']

                total_wages = int(units_required)*int(wage_per_unit)

                Installment.update_installments(installment_num=installment_num, district=district, center=center,
                                                garment_type=garment_type, received_date=issue_date,
                                                units_required=units_required, deadline=deadline, total_wages=total_wages,
                                                units_pm=units_pm, set_id=set_id, eo=eo_name, _id=_id)

                if len(user_id) <= 3:
                    user = User.get_by_id(int(user_id))
                else:
                    user = User.get_by_id(user_id)

            else:
                date_received = request.form['receivedDate']
                units = request.form['unitsReceived']

                Installment.update_received(cut_piece_units=units, material_received_date=date_received, _id=_id)

            return render_template('intent_added.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/update_installment_delivery/<string:_id>', methods=['POST', 'GET'])
def update_installment_delivery_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('update_installment_delivery_form.html', user=user, installment_id=_id)
        else:
            units_for_delivery = request.form['unitsForDelivery']
            Installment.update_delivery(_id=_id, units_delivered=units_for_delivery)

            return render_template('intent_added.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/View_Intents', methods=['POST', 'GET'])
def view_intents_ovr_district():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if user.society_name is not None:
            return render_template('ViewIntents.html', user=user, society=user.society_name, district=user.district)

    else:
        return render_template('login_fail.html')


@app.route('/view_installments/<string:_id>', methods=['POST', 'GET'])
def view_installments(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if user.designation == 'DSWO/ICO':
            print(user.designation)
            return render_template('ViewInstallments.html', user=user, society=user.society_name,
                                   district=user.district, intent_id=_id)
        elif user.designation == 'Accountant':
            return render_template('ViewInstallments_acc.html', user=user, society=user.society_name,
                                   district=user.district, intent_id=_id)

    else:
        return render_template('login_fail.html')


@app.route('/view_installments_received')
def view_installments_received():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('ViewInstallmentsReceived.html', user=user, society=user.society_name,
                               district=user.district)

    else:
        return render_template('login_fail.html')


@app.route('/rawInstallmentsByIntent/<string:_id>')
def raw_installments_by_intent(_id):
    district_intents_array = []
    district_intents = Database.find("installments", {"intent_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawSingleInstallment/<string:_id>')
def raw_single_installment(_id):
    district_intents_array = []
    district_intents = Database.find("installments", {"_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/new_intent/<string:user_id>', methods=['POST', 'GET'])
def intent_form(user_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            if len(user_id) <= 3:
                user = User.get_by_id(int(user_id))
            else:
                user = User.get_by_id(user_id)
            return render_template('intent_form.html', user=user, district=user.district,
                                   society=user.society_name)

        else:
            intent_id = request.form['intentId']
            district = request.form['district']
            center = request.form['center']
            received_date = request.form['receivedDate']
            garment_type = request.form['garmentType']
            garment_size = request.form['garmentSize']
            units_required = request.form['unitsRequired']
            deadline = request.form['deadline']
            total_wages = request.form['totalWages']
            units_pm = request.form['unitsPm']
            set_id = request.form['setID']
            eo_name = request.form['eo']
            user_id = user_id

            intent = Intent(intent_id=intent_id, district=district, center=center, received_date=received_date,
                            garment_type=garment_type, units_required=units_required, units_received=0,
                            deadline=deadline, total_wages=total_wages, units_pm=units_pm, user_id=user_id,
                            set_id=set_id, eo=eo_name, garment_size=garment_size)

            intent.save_to_mongo()

            if len(user_id) <= 3:
                user = User.get_by_id(int(user_id))
            else:
                user = User.get_by_id(user_id)

            return render_template('intent_added.html', intent=intent, intent_id=intent._id, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/add_another_intent/<string:_id>', methods=['POST', 'GET'])
def another_intent_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('another_intent_form.html', user=user, district=user.district,
                                   society=user.society_name, intent_id=_id)

        else:
            intent_id = request.form['intentID']
            district = request.form['district']
            center = request.form['center']
            received_date = request.form['receivedDate']
            garment_type = request.form['garmentType']
            garment_size = request.form['garmentSize']
            units_required = request.form['unitsRequired']
            deadline = request.form['deadline']
            total_wages = request.form['totalWages']
            units_pm = request.form['unitsPm']
            set_id = request.form['setID']
            eo_name = request.form['eo']
            user_id = user._id

            intent = Intent(intent_id=intent_id, district=district, center=center, received_date=received_date,
                            garment_type=garment_type, units_required=units_required, units_received=0,
                            deadline=deadline, total_wages=total_wages, units_pm=units_pm, user_id=user_id,
                            set_id=set_id, eo=eo_name, garment_size=garment_size)

            intent.save_to_mongo()

            if len(user_id) <= 3:
                user = User.get_by_id(int(user_id))
            else:
                user = User.get_by_id(user_id)

            return render_template('intent_added.html', intent_id=intent._id, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/update_intent/<string:_id>', methods=['POST', 'GET'])
def update_intent_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('update_intent_form.html', user=user, intent_id=_id)

        else:
            intent_id = request.form['intentId']
            district = request.form['district']
            center = request.form['center']
            received_date = request.form['receivedDate']
            garment_type = request.form['garmentType']
            garment_size = request.form['garmentSize']
            units_required = request.form['unitsRequired']
            units_received = request.form['unitsReceived']
            deadline = request.form['deadline']
            total_wages = request.form['totalWages']
            units_pm = request.form['unitsPm']
            set_id = request.form['setID']
            eo_name = request.form['eo']
            user_id = user._id

            intent = Intent(intent_id=intent_id, district=district, center=center, received_date=received_date,
                            garment_type=garment_type, units_required=units_required, units_received=units_received,
                            deadline=deadline, total_wages=total_wages, units_pm=units_pm, user_id=user_id, eo=eo_name,
                            set_id=set_id, garment_size=garment_size)

            intent.save_to_mongo()

            if len(user_id) <= 3:
                user = User.get_by_id(int(user_id))
            else:
                user = User.get_by_id(user_id)

            return render_template('intent_added.html', intent=intent, user=user)

    else:
        return render_template('login_fail.html')


##########################################
#  Add / View / Update Member Transaction
##########################################

@app.route('/assign_member/<string:installment_id>', methods=['POST', 'GET'])
def add_member_transaction_form(installment_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('member_transaction_form.html', user=user, district=user.district,
                                   society=user.society_name, installment_id=installment_id)

        else:
            name = request.form['memberName']
            member_id = request.form['MID']
            district = user.district
            society = user.society_name
            garment_name = request.form['gName']
            garment_type = request.form['gType']
            assigned_units = request.form['assignedUnits']
            wage_per_unit = request.form['wpu']
            deductions = request.form['deductions']
            advances = request.form['advances']
            deadline = request.form['deadlineDate']
            issue_date = request.form['issueDate']

            wage_expected = float(assigned_units)*float(wage_per_unit)

            contact_details, member_identifier, bank_account, ifsc = None, None, None, None

            if Database.is_valid(member_id):
                member = Database.find("members", {"_id": ObjectId(member_id)})
            else:
                member = Database.find("members", {"_id": member_id})

            for result_object in member[0:1]:
                member_identifier = result_object['member_id']
                bank_account = result_object['bank_account_number']
                ifsc = result_object['bank_ifsc_code']
                contact_details = result_object['contact_details']

            garment_size, intent_id, assUnits, assUnitsIntent = None, None, None, None

            installment = Database.find("installments", {"_id": installment_id})

            for result_object in installment[0:1]:
                intent_id = result_object['intent_id']
                assUnits = result_object['units_assigned']

            intent = Database.find("intents", {"_id": intent_id})

            for result_object in intent[0:1]:
                assUnitsIntent = result_object['units_assigned']
                garment_size = result_object['garment_size']

            memberTransaction = memberTransactions(name=name, member_id=member_identifier, garment_name=garment_name,
                                                   wage_expected=wage_expected, advance_paid=advances, deductions=deductions,
                                                   installment_id=installment_id, intent_id=intent_id,
                                                   deadline=deadline, no_of_units=assigned_units,
                                                   issue_date=issue_date, district=district, society=society,
                                                   bank_account=bank_account, ifsc=ifsc, garment_type=garment_type,
                                                   garment_size=garment_size, contact_details=contact_details)

            memberTransaction.save_to_mongo()

            Installment.update_assigned(_id=installment_id, units_assigned=int(assigned_units)+int(assUnits),
                                        units_received=0)
            Intent.update_assigned(_id=intent_id, units_assigned=int(assigned_units)+int(assUnitsIntent),
                                   units_received=0)

            return render_template('member_transaction_added.html', name=name, district=user.district, user=user,
                                   installment_id=installment_id, society=user.society_name)

    else:
        return render_template('login_fail.html')


@app.route('/update_member_transaction/<string:_id>', methods=['POST', 'GET'])
def update_member_transaction_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('update_member_transaction_form.html', user=user, district=user.district,
                                   society=user.society_name, transaction_id=_id)

        else:
            name = request.form['memberName']
            member_id = request.form['memberPicker']
            garment_name = request.form['gName']
            assigned_units = request.form['assignedUnits']
            returned_units = request.form['returnedUnits']
            advance = request.form['advances']
            deductions = int(request.form['deductions'])
            wage_per_unit = request.form['wpu']
            deadline = request.form['deadlineDate']
            status = request.form['statusSelect']
            issue_date = request.form['issueDate']
            wage_paid = request.form['wagePaid']

            wage_to_pay = int(returned_units)*float(wage_per_unit)

            intent_id, assUnits, installment_id, assUnitsIntent, mem_mongo_id = None, None, None, None, None
            District, Society, overall_current_thrift, overall_current_share = None, None, None, None
            received_units_intent, received_units_installment, units_returned_previous = None, None, None
            garment_size, units_assigned_previous, required_units_installment = None, None, None

            member_trans = Database.find("memberTransactions", {"_id": _id})

            for result_object in member_trans[0:1]:
                installment_id = result_object['installment_id']
                units_returned_previous = result_object['units_returned']
                units_assigned_previous = result_object['no_of_units']

                if units_returned_previous != 0:
                    units_returned_previous = int(returned_units)-int(units_returned_previous)
                else:
                    units_returned_previous = int(returned_units)

                if units_assigned_previous != 0:
                    units_assigned_previous = int(assigned_units) - int(units_assigned_previous)
                else:
                    units_assigned_previous = int(assigned_units)

            installment = Database.find("installments", {"_id": installment_id})

            for result_object in installment[0:1]:
                intent_id = result_object['intent_id']
                assUnits = result_object['units_assigned']
                received_units_installment = result_object['units_received']
                required_units_installment = result_object['units_required']

            intent = Database.find("intents", {"_id": intent_id})

            for result_object in intent[0:1]:
                assUnitsIntent = result_object['units_assigned']
                District = result_object['district']
                Society = result_object['center']
                received_units_intent = result_object['units_received']
                garment_size = result_object['garment_size']

            member = Database.find("members", {"$and": [{"district": District},
                                                        {"center": Society},
                                                        {"member_id": member_id}]})

            for result_object in member[0:1]:
                mem_mongo_id = result_object['_id']
                overall_current_share = result_object['share_value']
                overall_current_thrift = result_object['current_thrift_value']

            total_thrift_value = 0.10 * wage_to_pay

            decimal_part_wage = float(wage_to_pay) % 1
            decimal_part_deductions = float(deductions) % 1
            wage_to_pay -= decimal_part_wage
            deductions -= decimal_part_deductions

            total_decimal_part = decimal_part_wage+decimal_part_deductions
            total_thrift_value += total_decimal_part

            current_thrift = total_thrift_value % 1000
            current_share = total_thrift_value - current_thrift

            memberTransactions.update_member_transaction(name=name, member_id=member_id, garment_name=garment_name,
                                                         wage_expected=wage_to_pay, advance_paid=advance,
                                                         remaining_amount=(int(wage_to_pay)-int(advance)),
                                                         deadline=deadline, user_id=user._id,
                                                         no_of_units=assigned_units, transaction_id=_id,
                                                         units_returned=returned_units, transaction_status=status,
                                                         thrift=current_thrift, share=current_share,
                                                         issue_date=issue_date, deductions=deductions,
                                                         garment_size=garment_size)

            if status == 'Closed':
                overall_thrift = overall_current_thrift+current_thrift
                overall_share = overall_current_share+current_share

                memberProfile.update_member_share(mem_id=mem_mongo_id, thrift=overall_thrift, share=overall_share)

            Installment.update_assigned(_id=installment_id, units_assigned=int(units_assigned_previous)+int(assUnits),
                                        units_received=int(units_returned_previous)+int(received_units_installment))
            Intent.update_assigned(_id=intent_id, units_assigned=int(units_assigned_previous)+int(assUnitsIntent),
                                   units_received=int(units_returned_previous) + int(received_units_intent))
            memberTransactions.update_paid_wages(_id=_id, wage_paid=wage_paid)

            if int(required_units_installment) >= int(units_returned_previous) + int(received_units_installment):
                Installment.update_status(_id=installment_id)
            else:
                Installment.update_status_reverse(_id=installment_id)

            return render_template('member_transaction_added.html', name=name, district=user.district, user=user)

    else:
        return render_template('login_fail.html')


################################
#  Get Member Transaction
################################

@app.route('/rawTransaction/<string:_id>')
def get_single_transaction_details(_id):
    district_intents_array = []
    district_intents = Database.find("memberTransactions", {"_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
#  Get Society Transactions
################################

@app.route('/viewTransactionsByInstallment/<string:installment_id>')
def get_single_installment_transaction_details(installment_id):
    district_intents_array = []
    district_intents = Database.find("memberTransactions", {"installment_id": installment_id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/View_Transactions/<string:installment_id>', methods=['POST', 'GET'])
def view_transactions(installment_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if user.society_name is not None:
            return render_template('ViewTransactions.html', user=user, society=user.society_name,
                                   district=user.district, installment_id=installment_id)

    else:
        return render_template('login_fail.html')


################################
#  Add / View / Update Member
################################

@app.route('/new_member/<string:user_id>', methods=['POST', 'GET'])
def add_member_form(user_id):
    email = session['email']
    if len(user_id) <= 3:
        user = User.get_by_id(int(user_id))
    else:
        user = User.get_by_id(user_id)
    if email is not None:
        if request.method == 'GET':
            return render_template('member_form.html', user=user, user_id=user_id)

        else:
            name = request.form['memberName']
            district = request.form['district']
            society = request.form['society']
            memberID = request.form['memberID']
            address = request.form['address']
            contact = request.form['contact']
            enrollDate = request.form['enrollDate']
            bank_account = request.form['bankAccount']
            ifsc = request.form['IFSC']
            bank_name = request.form['bankName']
            aadhar = request.form['aadhar']
            status = request.form['socialStatus']
            caste = request.form['caste']
            dob = request.form['dob']
            shares = request.form['shares']
            thrift = request.form['thrift']

            member = memberProfile(name=name, district=district, center=society, member_id=memberID, address=address,
                                   contact_details=contact, enrollment_date=enrollDate, user_id=user_id,
                                   bank_account_number=bank_account, bank_ifsc_code=ifsc, bank_name=bank_name,
                                   aadhar_no=aadhar, social_status=status, date_of_birth=dob, caste=caste,
                                   share_value=shares, thrift_value=thrift)

            member.save_to_mongo()

            return render_template('member_added.html', name=name, district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/update_member/<string:_id>', methods=['POST', 'GET'])
def update_member_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('update_member_form.html', user=user, member_id=_id)

        else:
            name = request.form['memberName']
            district = request.form['district']
            society = request.form['society']
            memberID = request.form['memberID']
            address = request.form['address']
            contact = request.form['contact']
            enrollDate = request.form['enrollDate']
            bank_account = request.form['bankAccount']
            ifsc = request.form['IFSC']
            bank_name = request.form['bankName']
            aadhar = request.form['aadhar']
            status = request.form['socialStatus']
            dob = request.form['dob']
            shares = request.form['shares']
            thrift = request.form['thrift']
            caste = request.form['caste']

            member = memberProfile(name=name, district=district, center=society, member_id=memberID,
                                   address=address, contact_details=contact, enrollment_date=enrollDate,
                                   user_id=user._id, aadhar_no=aadhar, social_status=status,
                                   date_of_birth=dob)

            member.update_member(name=name, district=district, center=society, member_id=memberID,
                                 address=address, contact_details=contact, enrollment_date=enrollDate,
                                 user_id=user._id, mem_id=_id, bank_account_number=bank_account,
                                 bank_ifsc_code=ifsc, bank_name=bank_name, aadhar=aadhar, status=status,
                                 dob=dob, share_value=shares, thrift_value=thrift, caste=caste)

            return render_template('member_added.html', name=name, district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/View_Members')
def view_members():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if user.society_name is not None:
            return render_template('ViewMembers.html', user=user, society=user.society_name, district=user.district)

    else:
        return render_template('login_fail.html')


@app.route('/loggedOut')
def log_out():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if user.society_name is not None:
            user.logout()
            return render_template('logged_out.html', user=user.username)

    else:
        return render_template('login_fail.html')


################################
#  Get Member
################################

@app.route('/rawMember/<string:_id>')
def get_single_member_details(_id):
    district_intents_array = []
    if Database.is_valid(_id):
        district_intents = Database.find("members", {"_id": ObjectId(_id)})
    else:
        district_intents = Database.find("members", {"_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictMembers/<string:District>')
def get_district_member_details(District):
    district_intents_array = []
    district_intents = Database.find("members", {"district": District})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictSocietyMembers/<string:District>/<string:Society>')
def get_district_society_member_details(District, Society):
    district_intents_array = []
    district_intents = Database.find("members", {"$and": [{"district": District},
                                                          {"center": Society}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictSocietyIDMember/<string:District>/<string:Society>/<string:memID>')
def get_district_society_id_member_details(District, Society, memID):
    district_intents_array = []
    mid = int(memID)
    district_intents = Database.find("members", {"$and": [{"district": District},
                                                          {"center": Society},
                                                          {"member_id": mid}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
#  Delete Member
################################

@app.route('/delete_member/<string:_id>')
def delete_member(_id):

    email = session['email']
    user = User.get_by_email(email)

    if Database.is_valid(_id):
        memberProfile.delete_from_mongo(_id=ObjectId(_id))
    else:
        memberProfile.delete_from_mongo(_id=_id)

    return render_template('deleted_society.html', user=user)


################################
#  Delete Member
################################

@app.route('/delete_indent/<string:_id>')
def delete_indent(_id):

    email = session['email']
    user = User.get_by_email(email)

    if Database.is_valid(_id):
        Intent.delete_from_mongo(_id=ObjectId(_id))
    else:
        Intent.delete_from_mongo(_id=_id)

    return render_template('deleted.html', user=user)


################################
#  Add EO / View EO / Update EO
################################

@app.route('/new_EO/<string:user_id>', methods=['POST', 'GET'])
def add_eo_form(user_id):
    email = session['email']
    if len(user_id) <= 3:
        user = User.get_by_id(int(user_id))
    else:
        user = User.get_by_id(user_id)
    if email is not None:
        if request.method == 'GET':
            return render_template('eo_form.html', user=user)

        else:
            name = request.form['name']
            numCenters = request.form['numCenters']
            district = request.form['district']
            block = request.form['block']

            for i in range(int(numCenters)):
                society_name = "sn" + str(i)
                travel_charges = "tc" + str(i)
                sname = request.form[society_name]
                tcharges = request.form[travel_charges]

                eo = EducationOfficers(name=name, district=district, block=block, society_name=sname,
                                       travel_charge=tcharges, user_id=user._id)

                eo.save_to_mongo()

            return render_template('eo_added.html', name=name, block=block, district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/updateEO/<string:_id>', methods=['POST', 'GET'])
def update_eo_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('update_eo_form.html', eo_id=_id, user=user)

        else:
            name = request.form['name']
            district = request.form['district']
            block = request.form['block']
            sname = request.form['societyName']
            tcharges = request.form['travelCharges']

            EducationOfficers.update_eo_details(name=name, district=district, block=block, society_name=sname,
                                                travel_charge=tcharges, user_id=user._id, eo_id=_id)

            return render_template('eo_added.html', name=name, block=block, district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/View_EO', methods=['POST', 'GET'])
def view_eos():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('ViewEOs.html', user=user, district=user.district)

    else:
        return render_template('login_fail.html')


@app.route('/viewEODetails/<string:District>/<string:Name>')
def view_district_name_eos(District, Name):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('ViewEOsByDistrictName.html', user=user, district=District, Name=Name)

    else:
        return render_template('login_fail.html')


################################
#  Delete EO
################################

@app.route('/deleteEO/<string:_id>')
def delete_application(_id):

    email = session['email']
    user = User.get_by_email(email)

    EducationOfficers.delete_from_mongo(_id=_id)

    return render_template('deleted.html', user=user)


################################
#  Delete Garment
################################

@app.route('/delete_garment/<string:_id>')
def delete_garment(_id):

    email = session['email']
    user = User.get_by_email(email)

    GarmentDistrict.delete_from_mongo(_id=_id)

    if user.designation == "DSWO/ICO":
        return render_template('deleted.html', user=user)
    else:
        return render_template('deleted_society.html', user=user)


################################
#  Delete ICO Garment
################################

@app.route('/delete_ICO_garment/<string:_id>')
def delete_ICO_garment(_id):

    user = User.get_by_email(session['email'])

    GarmentICO.delete_from_mongo(_id=_id)

    if user.designation == "DSWO/ICO":
        return render_template('deleted.html', user=user)
    else:
        return render_template('deleted_society.html', user=user)


################################
#  Delete Member Transaction
################################

@app.route('/delete_member_transaction/<string:_id>')
def delete_member_transaction(_id):

    user = User.get_by_email(session['email'])

    member = Database.find("memberTransactions", {"_id": _id})

    intent_id, installment_id = None, None
    no_of_units, intent_units, installment_units = 0, 0, 0

    for result_object in member[0:1]:
        intent_id = result_object['intent_id']
        installment_id = result_object['installment_id']
        no_of_units = result_object['no_of_units']

    intent = Database.find("intents", {"_id": _id})
    installment = Database.find("installments", {"_id": _id})

    for result_object in intent[0:1]:
        intent_units = result_object['units_assigned']

    for result_object in installment[0:1]:
        installment_units = result_object['units_assigned']

    memberTransactions.delete_from_mongo(_id=_id)
    Intent.update_transaction_delete(_id=intent_id, units_assigned_new=int(intent_units)-int(no_of_units))
    Installment.update_installment_transaction_delete(_id=intent_id, units_assigned_new=(int(installment_units)-int(no_of_units)))

    return render_template('deleted_society.html', user=user)


################################
#  Get EO
################################

@app.route('/rawEO/<string:_id>')
def get_single_eo_details(_id):
    district_intents_array = []
    district_intents = Database.find("eoDetails", {"_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictEOs/<string:District>')
def get_district_eo_details(District):
    district_intents_array = []
    district_intents = Database.find("eoDetails", {"district": District})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictNameEOs/<string:District>/<string:Name>')
def get_district_name_eo_details(District, Name):
    district_intents_array = []
    district_intents = Database.find("eoDetails", {"$and": [{"district": District},
                                                            {"name": Name}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictSocietyEOs/<string:District>/<string:Society>')
def get_district_society_eo_details(District, Society):
    district_intents_array = []
    district_intents = Database.find("eoDetails", {"$and": [{"district": District},
                                                            {"society_name": Society}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
#  Get Garment
################################

@app.route('/rawGarment/<string:_id>')
def get_single_garment_details(_id):
    district_intents_array = []
    district_intents = Database.find("GarmentDistrict", {"_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictGarments/<string:District>')
def get_district_garment_details(District):
    district_intents_array = []
    district_intents = Database.find("GarmentDistrict", {"district": District})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictSocietyGarments/<string:District>/<string:Society>')
def get_district_society_garment_details(District, Society):
    district_intents_array = []
    district_intents = Database.find("GarmentDistrict", {"$and": [{"district": District},
                                                                  {"society": Society}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictSocietyGarmentsByType/<string:District>/<string:Society>/<string:gtype>')
def get_district_society_bygarment_type_details(District, Society, gtype):
    district_intents_array = []
    district_intents = Database.find("GarmentDistrict", {"$and": [{"district": District},
                                                                  {"society": Society},
                                                                  {"garment_type": gtype}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictSocietyGarmentsByName/<string:District>/<string:Society>/<string:gname>')
def get_district_society_by_garment_name_details(District, Society, gname):
    district_intents_array = []
    district_intents = Database.find("GarmentDistrict", {"$and": [{"district": District},
                                                                  {"society": Society},
                                                                  {"garment_name": gname}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
#  Get Garment ICO
################################

@app.route('/rawICOGarment/<string:_id>')
def get_single_ico_garment_details(_id):
    district_intents_array = []
    district_intents = Database.find("GarmentICO", {"_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictICOGarments/<string:District>')
def get_district_ico_garment_details(District):
    district_intents_array = []
    district_intents = Database.find("GarmentICO", {"district": District})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


@app.route('/rawDistrictTypeICOGarments/<string:District>/<string:gtype>')
def get_district_type_ico_garment_details(District, gtype):
    district_intents_array = []
    district_intents = Database.find("GarmentICO", {"$and": [{"district": District},
                                                             {"garment_type": gtype}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
#  Add Garment District
################################

@app.route('/new_garment/<string:user_id>', methods=['POST', 'GET'])
def add_garment_form(user_id):
    email = session['email']
    if len(user_id) <= 3:
        user = User.get_by_id(int(user_id))
    else:
        user = User.get_by_id(user_id)
    if email is not None:
        if request.method == 'GET':

            district_intents_array = []
            district_intents = Database.find("GarmentDistrict", {"$and": [{"district": user.district},
                                                                          {"society": user.society_name}]})

            for intent in district_intents:
                district_intents_array.append(intent)

            print(len(district_intents_array))

            if len(district_intents_array) > 0:
                return render_template('garment_form.html', user=user)
            else:
                return render_template('initial_garment_form.html', user=user)

        else:
            numCenters = request.form['numCenters']
            district = request.form['district']
            society = request.form['society']

            for i in range(int(numCenters)):
                garment_type = "gt" + str(i)
                garment_name = "gn" + str(i)
                wage_per_unit = "wpu" + str(i)
                cutting_charges = "cc" + str(i)
                deductions = "d" + str(i)

                gtype = request.form[garment_type]
                gname = request.form[garment_name]
                ccharges = request.form[cutting_charges]
                wpu = request.form[wage_per_unit]
                deductions = request.form[deductions]

                eo = GarmentDistrict(district=district, garment_type=gtype, garment_name=gname,
                                     cutting_charges=ccharges, wage_per_unit=wpu,
                                     user_id=user._id, deductions=deductions, society=society)

                eo.save_to_mongo()

            return render_template('garment_added.html', district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/updateGarment/<string:_id>', methods=['POST', 'GET'])
def update_garment_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('update_garment_form.html', garment_id=_id, user=user)

        else:
            gName = request.form['gName']
            district = request.form['district']
            society = request.form['society']
            gType = request.form['gType']
            cCharges = request.form['cCharges']
            wpu = request.form['wpu']
            deductions = request.form['deductions']

            GarmentDistrict.update_garment_district(district=district, garment_name=gName, garment_type=gType,
                                                    cutting_charges=cCharges, wage_per_unit=wpu, deductions=deductions,
                                                    garment_id=_id, user_id=user._id, society=society)

            return render_template('garment_added.html', district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/View_Garment')
def view_garments():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('ViewGarments.html', user=user, district=user.district)

    else:
        return render_template('login_fail.html')


################################
#  Add Garment ICO
################################

@app.route('/new_garment_ico/<string:user_id>', methods=['POST', 'GET'])
def add_ico_garment_form(user_id):
    email = session['email']
    if len(user_id) <= 3:
        user = User.get_by_id(int(user_id))
    else:
        user = User.get_by_id(user_id)
    if email is not None:
        if request.method == 'GET':
            district_intents_array = []
            district_intents = Database.find("GarmentICO", {"$and": [{"district": user.district},
                                                                     {"society": user.society_name}]})

            for intent in district_intents:
                district_intents_array.append(intent)

            print(len(district_intents_array))

            if len(district_intents_array) > 0:
                return render_template('ico_garment_form.html', user=user)
            else:
                return render_template('initial_garment_form_ico.html', user=user)

        else:
            numCenters = request.form['numCenters']
            district = request.form['district']

            for i in range(int(numCenters)):
                garment_type = "gt" + str(i)
                garment_name = "gn" + str(i)
                wage_per_unit = "wpu" + str(i)
                cutting_charges = "cc" + str(i)

                gtype = request.form[garment_type]
                gname = request.form[garment_name]
                ccharges = request.form[cutting_charges]
                wpu = request.form[wage_per_unit]

                eo = GarmentICO(district=district, garment_type=gtype,
                                garment_name=gname,
                                cutting_charges=ccharges, wage_per_unit=wpu,
                                user_id=user._id)

                eo.save_to_mongo()

            return render_template('ico_garment_added.html', district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/updateICOGarment/<string:_id>', methods=['POST', 'GET'])
def update_ico_garment_form(_id):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('update_ico_garment_form.html', garment_id=_id, user=user)

        else:
            district = request.form['district']
            gType = request.form['gType']
            gName = request.form['gName']
            cCharges = request.form['cCharges']
            wpu = request.form['wpu']

            GarmentICO.update_ico_garment(district=district, garment_type=gType, garment_name=gName,
                                          cutting_charges=cCharges, wage_per_unit=wpu, garment_id=_id,
                                          user_id=user._id)

            return render_template('ico_garment_added.html', district=district, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/View_ICOGarment')
def view_ico_garments():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('ViewICOGarments.html', user=user, district=user.district)

    else:
        return render_template('login_fail.html')


################################
# Get Single Intent
################################

@app.route('/rawIntentSingle/<string:_id>')
def raw_single_intents(_id):
    district_intents_array = []
    district_intents = Database.find("intents", {"_id": _id})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get District Intents
################################

@app.route('/rawIntentsByDistrict/<string:District>')
def raw_intents_by_district(District):
    district_intents_array = []
    district_intents = Database.find("intents", {"district": District})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get Completed Intent
################################

@app.route('/RawCompletedIntents/<string:district>')
def raw_completed_intents(district):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"$where": "this.units_received == this.units_required"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get Ongoing Intent
################################

@app.route('/RawOngoingIntents/<string:district>')
def raw_ongoing_intents(district):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"deadline": {"$gte": datetime.now()}},
                                                          {"$where": "(this.units_received < this.units_required) &&"
                                                                     "(this.units_assigned == this.units_required)"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get yta Intent
################################

@app.route('/RawOngoingYTAIntents/<string:district>')
def raw_ongoing_intents_yta(district):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"deadline": {"$gte": datetime.now()}},
                                                          {"$where": "(this.units_received < this.units_required) &&"
                                                                     "(this.units_assigned < this.units_required)"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get Violated Intents
################################

@app.route('/RawViolations/<string:district>')
def raw_violations(district):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"deadline": {"$lte": datetime.now()}},
                                                          {"$where": "this.units_received < this.units_required"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Intents Yet To Be Assigned
################################

@app.route('/rawYTAIntents/<string:district>/<string:society>')
def raw_yta_intents(district, society):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"center": society},
                                                          {"$where": "this.units_assigned < this.units_required"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get Overall Garment Details
################################

@app.route('/RawGarmentOverallDetails')
def raw_ovr_garment_details():
    district_intents_array = []
    district_intents = Database.find("GarmentDistrict", {})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# View Completed Intent
################################

@app.route('/CompletedIntents')
def satisfied_intents():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('completedIntents.html', district=user_district, user=user)

    else:
        return render_template('login_fail.html')


################################
# View yet to assign Intents
################################

@app.route('/YTAIntents')
def yta_intents():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('ytaIntents.html', district=user_district, user=user)
    else:
        return render_template('login_fail.html')


################################
# View Ongoing Intent
################################

@app.route('/OngoingIntents')
def ongoing_intents():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('ongoingIntents.html', district=user_district, user=user)
    else:
        return render_template('login_fail.html')


################################
# View Violated Intent
################################

@app.route('/ViolatedIntents')
def violated_intents():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('violatedIntents.html', district=user_district, user=user)
    else:
        return render_template('login_fail.html')


################################
# Get Completed Intent Society
################################

@app.route('/RawCompletedIntentsSociety/<string:district>/<string:society>')
def raw_completed_intents_society(district, society):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"center": society},
                                                          {"$where": "this.units_received == this.units_required"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get Ongoing Intent Society
################################

@app.route('/RawOngoingIntentsSociety/<string:district>/<string:society>')
def raw_ongoing_intents_society(district, society):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"center": society},
                                                          {"deadline": {"$gte": datetime.now()}},
                                                          {"$where": "(this.units_received < this.units_required) &&"
                                                                     "(this.units_assigned == this.units_required)"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get yta Intent Society
################################

@app.route('/RawOngoingIntentsYTASociety/<string:district>/<string:society>')
def raw_yta_ongoing_intents(district, society):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"center": society},
                                                          {"deadline": {"$gte": datetime.now()}},
                                                          {"$where": "this.units_assigned < this.units_required"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# Get Violated Intents Society
################################

@app.route('/RawViolationsSociety/<string:district>/<string:society>')
def raw_violations_society(district, society):
    district_intents_array = []
    district_intents = Database.find("intents", {"$and": [{"district": district},
                                                          {"center": society},
                                                          {"deadline": {"$lte": datetime.now()}},
                                                          {"$where": "this.units_received < this.units_required"}]})

    for intent in district_intents:
        district_intents_array.append(intent)

    completed_intents = json.dumps(district_intents_array, default=json_util.default)

    return completed_intents


################################
# View Completed Intent
################################

@app.route('/CompletedIntentsSociety')
def satisfied_intents_society():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('completedIntentsSociety.html', district=user_district, user=user,
                               society=user.society_name)

    else:
        return render_template('login_fail.html')


################################
# View yet to assign Intents
################################

@app.route('/YTAIntentsSociety')
def yta_intents_society():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('ytaIntentsSociety.html', district=user_district, user=user,
                               society=user.society_name)

    else:
        return render_template('login_fail.html')


################################
# View Ongoing Intent
################################

@app.route('/OngoingIntentsSociety')
def ongoing_intents_society():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('ongoingIntentsSociety.html', district=user_district, user=user,
                               society=user.society_name)
    else:
        return render_template('login_fail.html')


################################
# View Violated Intent
################################

@app.route('/ViolatedIntentsSociety')
def violated_intents_society():
    email = session['email']
    if email is not None:
        user = User.get_by_email(email)
        user_district = user.district
        return render_template('violatedIntentsSociety.html', district=user_district, user=user,
                               society=user.society_name)
    else:
        return render_template('login_fail.html')


@app.route('/bonus_calculation/<string:start_date>/<string:end_date>/<string:district>/<string:society>/<int:profits>')
def accounts_between_bank(start_date, end_date, district, society, profits):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())

    accounts_dict = Database.find("memberTransactions", {"$and": [{"issue_date": {"$gte": start, "$lt": end}},
                                                                  {"district": district},
                                                                  {"society": society}]})

    total_wages = 0
    prof = int(profits)/2

    for tran in accounts_dict:
        total_wages += int(tran['wage_expected'])

    ratio_multiplier = int(prof)/int(total_wages)

    for tran in accounts_dict:
        tran['bonus'] = int(tran['wage_expected']) * ratio_multiplier
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/BonusCalculationForMembers', methods=['POST', 'GET'])
def bonus_calculations_society():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('bonus_calculation_form.html', user=user)

        else:
            profits = request.form['profits']
            start_date = request.form['startDate']
            end_date = request.form['endDate']

            return render_template('view_bonus_details.html', district=user.district, user=user,
                                   society=user.society_name, start_date=start_date,
                                   end_date=end_date, profits=profits)

    else:
        return render_template('login_fail.html')


################################
# Download Reports Between Dates
################################

@app.route('/enter_dates_society', methods=['POST', 'GET'])
def get_dates_society():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            if user.designation == 'Accountant':
                return render_template('get_dates_society_report.html', user=user)
            else:
                return render_template('get_dates_society_report_ico.html', user=user)

        else:
                start_date = request.form['startDate']
                end_date = request.form['endDate']

                if user.designation == 'Accountant':
                    return render_template('society_reports.html', district=user.district, user=user,
                                           society=user.society_name, start_date=start_date,
                                           end_date=end_date)

                elif user.designation == 'DSWO/ICO':
                    return render_template('district_reports.html', district=user.district, user=user,
                                           society=user.society_name, start_date=start_date,
                                           end_date=end_date)

    else:
        return render_template('login_fail.html')


################################
# Member All Transactions Report
################################

@app.route('/member_historic_transactions', methods=['POST', 'GET'])
def member_historic_all():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('all_member_transactions.html', district=user.district, user=user,
                               society=user.society_name)

    else:
        return render_template('login_fail.html')


@app.route('/rawMemberTransactionsHistoric/<string:installment_id>/<string:member_id>')
def raw_member_transactions_historic(installment_id, member_id):
    accounts = []

    accounts_dict = Database.find("memberTransactions", {"$and": [{"installment_id": installment_id},
                                                                  {"member_id": int(member_id)}]})

    for tran in accounts_dict:
        accounts.append(tran)

    # df = pandas.DataFrame(accounts)
    #
    # print(df)
    #
    # df_agg = df.groupby(['member_id', 'name', 'garment_type']).agg(sum)
    # df_json = json.loads(df_agg.reset_index().to_json(orient='records'))
    #
    # print(df_json)
    #
    # accounts_final = json.dumps(df_json, default=json_util.default)
    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/raw_member_transactions_society_between/<string:start_date>/<string:end_date>/<string:district>/<string:society>')
def raw_member_transactions(start_date, end_date, district, society):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())

    accounts_dict = Database.find("memberTransactions", {"$and": [{"issue_date": {"$gte": start, "$lt": end}},
                                                                  {"district": district},
                                                                  {"society": society}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/raw_member_transactions_all/<string:district>/<string:society>/<string:member_id>')
def all_historic_member_transactions(district, society, member_id):
    accounts = []

    accounts_dict = Database.find("memberTransactions", {"$and": [{"district": district},
                                                                  {"society": society},
                                                                  {"member_id": int(member_id)}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/raw_member_transactions_between/<string:start_date>/<string:end_date>/<string:district>')
def raw_member_transactions_district(start_date, end_date, district):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())

    accounts_dict = Database.find("memberTransactions", {"$and": [{"issue_date": {"$gte": start, "$lt": end}},
                                                                  {"district": district}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/raw_installments_between/<string:start_date>/<string:end_date>/<string:district>')
def raw_installments_between(start_date, end_date, district):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())

    accounts_dict = Database.find("installments", {"$and": [{"uploaded_date": {"$gte": start, "$lt": end}},
                                                            {"district": district}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/raw_installments_for_delivery/<string:district>/<string:society>')
def raw_installments_for_delivery_between(district, society):
    accounts = []

    today_date = datetime.now().date()
    one_week_date = today_date + timedelta(days=10)

    today_date = today_date.strftime('%Y-%m-%d')
    one_week_date = one_week_date.strftime('%Y-%m-%d')

    start = datetime.combine(datetime.strptime(today_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(one_week_date, '%Y-%m-%d').date(),
                           datetime.now().time())

    accounts_dict = Database.find("installments", {"$and": [{"deadline": {"$gte": start, "$lt": end}},
                                                            {"district": district},
                                                            {"center": society}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/raw_all_installments_received/<string:district>/<string:society>')
def raw_installments_for_received(district, society):
    accounts = []

    accounts_dict = Database.find("installments", {"$and": [{"district": district},
                                                            {"center": society},
                                                            {"$where": "this.units_received > this.units_sanctioned"}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/raw_all_unreturned_units/<string:district>/<string:society>')
def raw_unreturned_units(district, society):
    accounts = []

    accounts_dict = Database.find("memberTransactions", {"$and": [{"district": district},
                                                                  {"society": society},
                                                                  {"$where": "this.units_assigned > this.units_returned"}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/installments_up_for_delivery', methods=['POST', 'GET'])
def view_installments_ten_days_delivery():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if user.society_name is not None:
            if user.designation == 'Accountant':
                return render_template('DeliveryInstallments.html', user=user, society=user.society_name,
                                       district=user.district)
            else:
                return render_template('DeliveryInstallmentsDSWO.html', user=user, society=user.society_name,
                                       district=user.district)

    else:
        return render_template('login_fail.html')


@app.route('/raw_intents_between_date/<string:start>/<string:end>/<string:district>')
def raw_intents_between_district(start, end, district):
    accounts = []

    start = datetime.combine(datetime.strptime(start, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end, '%Y-%m-%d').date(),
                           datetime.now().time())

    accounts_dict = Database.find("intents", {"$and": [{"received_date": {"$gte": start, "$lt": end}},
                                                       {"district": district}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


if __name__ == '__main__':
    app.run(port=4035, debug=True)
