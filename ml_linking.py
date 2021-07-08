#Script to create app & db tables and define the app

import os
from sqlalchemy import func, desc, or_, and_
from flask import Flask, render_template, request, redirect, flash, session
#import linking and login tables:
#from app_for_nber.models import *
import sys
sys.path.append("/Users/myerarashid/Dropbox/MassMobility/app_for_hand_linking")
from models import *
from datetime import datetime

################################################################
#(1). Create app, database's tables and configure it

ml_linking = Flask(__name__)

#ml_linking.config.from_object('app_for_nber.config_sqlite')
ml_linking.config.from_object('config_sqlite')

db.init_app(ml_linking)
db.create_all(app=ml_linking)

################################################################
#(2). Run app

#1. Login

@ml_linking.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('already_logged.html')

@ml_linking.route('/login', methods=['POST'])
def do_admin_login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    #Connect to database
    #con, meta = connect('alvaro', 'password1', 'pg_test1')

    #create session:
    #Session = sessionmaker(bind=con, autocommit=False)
    #s = Session()
    query = User.query.filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]))
    result0 = query.first()
    if result0:
        session['logged_in'] = True
        session['user'] = POST_USERNAME
        time_now = datetime.utcnow() #puse "datetime." al inicio y funciono, nose pq
        new_login = Track_logins(POST_USERNAME, time_now)
        db.session.add(new_login) #note that the add works here, maybe because the new instance "new_login" is not really doing a change in the dataset by itself.
        db.session.commit()

        return redirect("/choose_project", code=302)
    else:
        flash('wrong password!')
        return "Wrong user name or password! <a href='/'>Back to login</a>"


@ml_linking.route("/logout")
def logout():
    
    ###
    # Solve cases in which user has some seen records without training
    # If user logs out, those records assigned to her are set to user=None.
    ids_wo_training = base_results.query.with_entities(base_results.idA).filter(and_(base_results.trained==0, base_results.user==session['user'])).order_by(desc(base_results.first_2link), base_results.idA).limit(100).all()    

    if ids_wo_training!=[]:
        for id_a_wo_train in ids_wo_training:
            base_results.query.filter_by(idA=id_a_wo_train.idA).update(dict(user=None))
        db.session.commit()
    ###

    session['logged_in'] = False #log out
    
    return home()


########################################################################
#2. Linking

@ml_linking.route('/choose_project')
def choose_project():
    return render_template('choose_project.html')

@ml_linking.route('/linking', methods=['POST', 'GET'])
def linking():
    #record the time the page is loaded
    time_1 = datetime.utcnow()
    session['time_1'] = time_1

    # 2. query for idA of the record I want to link
    #id_1 = base_results.query.with_entities(base_results.idA).filter_by(trained=0).order_by(desc(base_results.first_2link), base_results.idA).limit(1).all() #this was replaced by next line

    ###
    id_1 = base_results.query.with_entities(base_results.idA).filter(or_(and_(base_results.trained==0, base_results.user==session['user']), and_(base_results.trained==0, base_results.user==None))).order_by(desc(base_results.first_2link), base_results.idA).limit(1).all() # (search in pool of candidates for not trained (with your user_name or without an assigned username))

    if id_1!=[]:
        ## Assign the user_name to the first user that sees this record (to avoid showing same record to different people)
        base_results.query.filter_by(idA=id_1[0].idA).update(dict(user=session['user']))
        db.session.commit()
        ###
        
        # 3. Bring information from base_a for this id_1
        info_a_1 = base_a.query.filter_by(idA=id_1[0].idA).first()

        # 4. Bring all possible matches for id_1
        pot_mat_1 = base_potmatches.query.with_entities(base_potmatches.idB).filter_by(idA=id_1[0].idA, to_drop_jscore=0).order_by(desc(base_potmatches.jscore)).limit(50).all()

        # 4.1. create list of indexes for potential matches in base B
        id_2 = []
        for element in pot_mat_1:
            id_2.append(element.idB)

        # 5. Bring information from base_b for every id_2
        info_b_2 = base_b.query.filter(base_b.idB.in_(id_2)).all()

        ## Order information according to the jscore (the order in pot_mat_1)
        info_b_2_temp = []
        for index_jscore_order in id_2:
            for element_from_b in info_b_2:
                if index_jscore_order==element_from_b.idB:
                    info_b_2_temp.append(element_from_b)

        info_b_2 = info_b_2_temp

        #6. Translate data into a nice way
        ia1 = [info_a_1.man_first_nameA, info_a_1.man_last_nameA, info_a_1.man_yobA, info_a_1.wife_first_nameA, info_a_1.wife_yobA, info_a_1.idA]
        ib2=[]
        for element in info_b_2:
            ib2.append([element.man_first_nameB, element.man_last_nameB, element.man_yobB, element.wife_first_nameB, element.wife_yobB, element.idB])

        # Show how many matches someone has done
        total_matches = base_results.query.with_entities(func.sum(base_results.trained)).filter_by(user=session['user']).scalar()

        return render_template('choose_link.html', ia1=ia1, ib2=ib2, time_1=time_1, total_matches=total_matches) #, old_id_1=old_id_1

    elif id_1==[]:
        return render_template('no_exercises.html') #, old_id_1=old_id_1



@ml_linking.route('/picklink', methods=['POST'])
def picklink():
    #record the time a match is chosen
    time_2 = datetime.utcnow()
    id_1 = request.form.get('id_1')
    id_2 = request.form.get('id_2')
    time_1 = session['time_1']
    result = base_results.query.filter_by(idA=id_1).update(dict(result_idB=id_2, trained=1, time_start=time_1, time_end=time_2, user=session['user']))
    #db.session.add(result) #(i think) you cannot add because the query already adds the change to the db, while using something like Track_logins(.,.) does not add anything but creates an instance of a class that can be add later. So you just need to commit the changes.
    db.session.commit()

    #save last id_A in case user wants to undo
    session['last_id_a'] = id_1

    return redirect("/linking", code=307)

@ml_linking.route('/clean')
def clean():
    for num in range(3):
        id_1 = num+1
        result_clean = base_results.query.filter_by(idA=id_1).update(dict(result_idB=None, trained=0, time_start=None, time_end=None, user=None))
        #db.session.add(result_clean)
        db.session.commit()
    return redirect("/linking", code=302)

@ml_linking.route('/undo', methods=['POST'])
def undo():
    if session['last_id_a'] is not None:
        result_undo = base_results.query.filter_by(idA=session['last_id_a']).update(
            dict(result_idB=None, trained=0, time_start=None, time_end=None, user=session['user']))
        # db.session.add(result_undo)
        db.session.commit()

    return redirect("/linking", code=307)


os.chdir(r"/Users/myerarashid/Dropbox/MassMobility/app_for_hand_linking")

if __name__ == '__main__':
    ml_linking.run() #(host = "127.0.0.1", port = 5001)

####


#if __name__ == "__main__":
    #from waitress import serve
    #serve(ml_linking, host="0.0.0.0", port=8080)






