
import functools
import datetime
import plotly
import plotly.graph_objs as go

from flask import Flask, session, g
from flask import redirect
from flask import request, make_response
from flask import render_template
from flask import url_for

from db import *

def get_moneyorcustomer(save,check,loan,bank,t):
    y = []
    savebank = [j[0] for j in save]
    try:
        k_save = savebank.index(bank)
        y.append(save[k_save][t])
    except:
        y.append(0)

    checkbank = [j[0] for j in check]
    try:
        k_check = checkbank.index(bank)
        y.append(check[k_check][t])
    except:
        y.append(0)
    loanbank = [j[0] for j in loan]
    try:
        k_loan = loanbank.index(bank)
        y.append(loan[k_loan][t])
    except:
        y.append(0)
    return y

# 生成一个app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'lab3'

# 对app执行请求页面地址到函数的绑定
@app.route("/", methods=("GET", "POST"))
@app.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        # 客户端在login页面发起的POST请求
        username = request.form["username"]
        password = request.form["password"]
        ipaddr   = request.form["ipaddr"]
        database = request.form["database"]

        db = db_login(username, password, ipaddr, database)

        if db == None:
            return render_template("login_fail.html")
        else:
            session['username'] = username
            session['password'] = password
            session['ipaddr'] = ipaddr
            session['database'] = database

            return redirect(url_for('statistics'))
    else :
        # 客户端GET 请求login页面时
        return render_template("login.html")

@app.route("/statistics", methods=(["GET", "POST"]))
def statistics():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    cursor = db.cursor()
    sql = "select * from savestat;"
    cursor.execute(sql)
    save = list(cursor.fetchall())
    sql = "select * from checkstat;"
    cursor.execute(sql)
    check = list(cursor.fetchall())
    sql = "select * from loanstat;"
    cursor.execute(sql)
    loan = list(cursor.fetchall())
    sql = "select bankname from bank;"
    cursor.execute(sql)
    bank = list(cursor.fetchall())

    if request.method == "GET":
        return render_template("statistics.html",save = save,check = check,loan = loan)
    else:
        if 'money' in request.form:
            pyplt = plotly.offline.plot
            x = ['储蓄账户','支票账户','贷款']
            # Traces
            trace = []
            for i in bank:
                y = get_moneyorcustomer(save,check,loan,i[0],1)
                trace.append(go.Bar(x = x,y = y,name=i[0]))
            # Layout
            layout = go.Layout(
                title='按业务统计各支行总金额'
            )
            # Figure
            figure = go.Figure(data=trace, layout=layout)
            # Plot
            pyplt(figure, filename="money.html")
        if 'customer' in request.form:
            pyplt = plotly.offline.plot
            x = ['储蓄账户', '支票账户', '贷款']
            trace = []
            for i in bank:
                y = get_moneyorcustomer(save,check,loan,i[0],2)
                trace.append(go.Bar(x = x,y = y,name=i[0]))
            # Layout
            layout = go.Layout(
                title='按业务统计各支行总用户数'
            )
            # Figure
            figure = go.Figure(data=trace, layout=layout)
            # Plot
            pyplt(figure, filename="customer.html")
        return render_template("statistics.html",save = save,check = check,loan = loan)

@app.route("/customer/create", methods=(["GET", "POST"]))
def customer_create():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("customer_create.html")
    else:
        cusID = request.form["id"]
        cusname = request.form["name"]
        cusphone = request.form["phone"]
        address = request.form["place"]
        contact_name = request.form["name2"]
        contact_phone = request.form["phone2"]
        contact_email = request.form["email2"]
        relation = request.form["relation"]
        try:
            x = int(cusID)
            x = int(cusphone)
            x = int(contact_phone)
            if len(cusID) != 18 or len(cusphone)!= 11 or len(contact_phone)!= 11:
                return render_template("customer_create.html", failed=1)
        except:
            return render_template("customer_create.html", failed=1)
        cursor = db.cursor()
        sql = "INSERT INTO customer VALUES('%s','%s','%s','%s','%s','%s','%s','%s',null,null)" % (cusID,cusname,cusphone,address,contact_phone,contact_name,contact_email,relation)
        try:
            cursor.execute(sql)
            db.commit()
            return render_template("customer_create.html", success = 1)
        except:
            db.rollback()
            return render_template("customer_create.html",failed = 2)

@app.route("/customer/", methods=(["GET", "POST"]))
@app.route("/customer/search", methods=(["GET", "POST"]))
def customer_search():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("customer_search.html")
    else:
        id = request.form["id"]
        if not id:
            cursor = db.cursor()
            sql = "select * from customer"
            cursor.execute(sql)
            results = cursor.fetchall()
            return render_template("customer_search.html", find_all = 1,r = results)
        cursor = db.cursor()
        sql = "select * from customer where cusID = '%s'" % (id)
        try:
            x = int(id)
            if len(id) != 18:
                return render_template("customer_search.html", failed=1)
        except:
            return render_template("customer_search.html", failed=1)
        try:
            cursor.execute(sql)
            results = cursor.fetchall()[0]
            return render_template("customer_search.html", success = 1,r = results)
        except:
            return render_template("customer_search.html",failed = 2)

@app.route("/customer/change", methods=(["GET", "POST"]))
def customer_change():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("customer_change.html")
    else:
        if 'change' in request.form:
            id = request.form["id"]
            try:
                x = int(id)
                if len(id) != 18:
                    return render_template("customer_change.html", failed=1)
            except:
                return render_template("customer_change.html", failed=1)
            cursor = db.cursor()
            sql = "select * from customer where cusID = '%s'" % (id)
            try:
                cursor.execute(sql)
                results = cursor.fetchall()[0]
                return render_template("customer_change.html", success=1, r=results)
            except:
                return render_template("customer_change.html", failed=2)
        elif 'save' in request.form:
            cusID = request.form["id2"]
            cusname = request.form["name"]
            cusphone = request.form["phone"]
            address = request.form["place"]
            contact_name = request.form["name2"]
            contact_phone = request.form["phone2"]
            contact_email = request.form["email2"]
            relation = request.form["relation"]
            try:
                x = int(cusphone)
                x = int(contact_phone)
                if len(cusphone) != 11 or len(contact_phone) != 11:
                    return render_template("customer_change.html", failed=1)
            except:
                return render_template("customer_change.html", failed=1)
            cursor = db.cursor()
            sql = "update customer set cusname = '%s',cusphone = '%s',address = '%s',contact_phone = '%s',contact_name = '%s',contact_email = '%s',relation = '%s' where cusID = '%s'" % (cusname, cusphone, address, contact_phone, contact_name, contact_email, relation,cusID)
            try:
                cursor.execute(sql)
                db.commit()
                return render_template("customer_change.html", success=2)
            except:
                db.rollback()
                return render_template("customer_change.html", failed=3)

@app.route("/customer/delete", methods=(["GET", "POST"]))
def customer_delete():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("customer_delete.html")
    else:
        if 'change' in request.form:
            id = request.form["id"]
            try:
                x = int(id)
                if len(id) != 18:
                    return render_template("customer_delete.html", failed=1)
            except:
                return render_template("customer_delete.html", failed=1)
            cursor = db.cursor()
            sql = "select * from customer where cusID = '%s'" % (id)
            try:
                cursor.execute(sql)
                results = cursor.fetchall()[0]
                return render_template("customer_delete.html", success=1, r=results)
            except:
                return render_template("customer_delete.html", failed=2)
        if 'delete' in request.form:
            cursor = db.cursor()
            cusID = request.form["id2"]
            sql = "delete from customer where cusID = '%s'" % (cusID)
            try:
                cursor.execute(sql)
                db.commit()
                return render_template("customer_delete.html", success=2)
            except:
                db.rollback()
                return render_template("customer_delete.html", failed=3)

@app.route("/account/create", methods=(["GET", "POST"]))
def account_create():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    cursor = db.cursor()
    sql = "select * from bank"
    cursor.execute(sql)
    results = cursor.fetchall()
    bank0 = [i[0] for i in results]
    if request.method == "GET":
        return render_template("account_create.html",bank = bank0)
    else:
        accountID = request.form["id"]
        money = request.form["money"]
        bank = request.form["bank"]
        settime = request.form["date"]
        account_type = request.form["op"]
        try:
            x = int(accountID)
            x = float(money)
            x = int(settime[0:4])
            x = int(settime[5:7])
            x = int(settime[8:])
            if len(accountID) != 6 or settime[4]!= '-' or settime[7]!= '-' or len(settime)!=10:
                return render_template("account_create.html", failed=1,bank = bank0)
        except:
            return render_template("account_create.html", failed=1,bank = bank0)
        cursor = db.cursor()
        sql1 = "INSERT INTO accounts VALUES('%s','%s','%s','%s')" % (accountID,money,settime,account_type)
        sql2 = ""
        if account_type == '储蓄账户':
            savetype = request.form["type"]
            interestrate = request.form["interest_rate"]
            try:
                if len(savetype)!= 1:return render_template("account_create.html", failed=1,bank = bank0)
                x = float(interestrate)
            except:
                return render_template("account_create.html", failed=1,bank = bank0)
            sql2 = "INSERT INTO saveacc VALUES('%s','%s','%s')" % (accountID, interestrate,savetype)
        if account_type == '支票账户':
            overdraft = request.form["overdraft"]
            try:
                x = float(overdraft)
            except:
                return render_template("account_create.html", failed=1,bank = bank0)
            sql2 = "INSERT INTO checkacc VALUES('%s','%s')" % (accountID,overdraft)
        customer = request.form["customer"]
        try:
            x = int(customer)
            if len(customer) != 18:
                return render_template("account_create.html", failed=1,bank = bank0)
        except:
            return render_template("account_create.html", failed=1,bank = bank0)
        sql = "select * from customer where cusID = '%s'" % (customer)
        cursor.execute(sql)
        results = cursor.fetchall()
        if not results:
            return render_template("account_create.html", failed = 3,bank = bank0)

        sql3 = "INSERT INTO cusforacc VALUES('%s','%s','%s',null,'%s')" % (accountID,bank,customer,account_type)
        try:
            cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.execute(sql3)
            db.commit()
            return render_template("account_create.html",success = 1, bank=bank0)
        except:
            db.rollback()
            return render_template("account_create.html", failed=2,bank = bank0)

@app.route("/account/", methods=(["GET", "POST"]))
@app.route("/account/search", methods=(["GET", "POST"]))
def account_search():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("account_search.html")
    else:
        way = request.form["way"]
        id = request.form["id0"]
        if not id:
            cursor = db.cursor()
            sql = "select accountID from accounts"
            cursor.execute(sql)
            results = cursor.fetchall()
            return render_template("account_search.html", find_all = 1,r = results)
        if way == '账户号':
            try:
                x = int(id)
                if len(id) != 6:
                    return render_template("account_search.html", failed=1)
            except:
                return render_template("account_search.html", failed=1)
            cursor = db.cursor()
            sql = "select accounts.accountID,money,bank,settime,accounts.accounttype,cusID,visit,overdraft from accounts,checkacc,cusforacc where accounts.accountID='%s' and accounts.accountID=checkacc.accountID and cusforacc.accountID=accounts.accountID" % (id)
            cursor.execute(sql)
            results1 = cursor.fetchall()
            sql = "select accounts.accountID,money,bank,settime,accounts.accounttype,cusID,visit,interestrate,savetype from accounts,saveacc,cusforacc where accounts.accountID='%s' and accounts.accountID=saveacc.accountID and cusforacc.accountID=accounts.accountID" % (id)
            cursor.execute(sql)
            results2 = cursor.fetchall()
            if not (results1+results2):
                return render_template("account_search.html", failed = 4)
            return render_template("account_search.html", results = results1+results2)
        if way == '身份证号':
            try:
                x = int(id)
                if len(id) != 18:
                    return render_template("account_search.html", failed=1)
            except:
                return render_template("account_search.html", failed=1)
            cursor = db.cursor()
            sql = "select accounts.accountID,money,bank,settime,accounts.accounttype,cusID,visit,overdraft from accounts,checkacc,cusforacc where cusID='%s' and accounts.accountID=checkacc.accountID and cusforacc.accountID=accounts.accountID" % (id)
            cursor.execute(sql)
            results1 = cursor.fetchall()
            sql = "select accounts.accountID,money,bank,settime,accounts.accounttype,cusID,visit,interestrate,savetype from accounts,saveacc,cusforacc where cusID='%s' and accounts.accountID=saveacc.accountID and cusforacc.accountID=accounts.accountID" % (id)
            cursor.execute(sql)
            results2 = cursor.fetchall()
            if not (results1+results2):
                return render_template("account_search.html", failed = 3)
            return render_template("account_search.html", results=results1 + results2)

@app.route("/account/change", methods=(["GET", "POST"]))
def account_change():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("account_change.html")
    else:
        if 'change' in request.form:
            id = request.form["id"]
            try:
                x = int(id)
                if len(id) != 6:
                    return render_template("account_change.html", failed=1)
            except:
                return render_template("account_change.html", failed=1)
            cursor = db.cursor()
            sql = "select accounts.accountID,money,bank,settime,accounts.accounttype,cusID,visit,overdraft,interestrate,savetype from accounts,saveacc,checkacc,cusforacc where accounts.accountID='%s' and (accounts.accountID=checkacc.accountID or accounts.accountID=saveacc.accountID) and cusforacc.accountID=accounts.accountID" % (id)
            cursor.execute(sql)
            results = cursor.fetchall()
            if not results:
                return render_template("account_change.html", failed = 2)
            return render_template("account_change.html",success = 1, r=results[0])
        if 'submit' in request.form:
            accountID = request.form["id1"]
            money = request.form["money"]
            account_type = request.form["account_type"]
            try:
                x = float(money)
            except:
                return render_template("account_change.html", failed=1)
            cursor = db.cursor()
            sql1 = "update accounts set money = '%s' where accountID = '%s'" % (money,accountID)
            sql2 = ""
            if account_type == '储蓄账户':
                type = request.form["type"]
                interestrate = request.form["interest_rate"]
                try:
                    if type:
                        if len(type) != 1: return render_template("account_create.html", failed=1)
                    if interestrate:
                        x = float(interestrate)
                except:
                    return render_template("account_change.html", failed=1)
                sql2 = "update saveacc set savetype = '%s',interestrate = '%s' where accountID = '%s'" % (type,interestrate,accountID)
            else:
                overdraft = request.form["overdraft"]
                try:
                    x = float(overdraft)
                except:
                    return render_template("account_change.html", failed=1)
                sql2 = "update checkacc set overdraft = '%s' where accountID = '%s'" % (overdraft,accountID)
            sql3 = "update cusforacc set visit = '%s' where accountID = '%s'" % (datetime.datetime.now().strftime('%Y-%m-%d'), accountID)
            try:
                cursor.execute(sql1)
                cursor.execute(sql2)
                cursor.execute(sql3)
                db.commit()
                return render_template("customer_change.html", success = 2)
            except:
                db.rollback()
                return render_template("customer_change.html", failed=3)

@app.route("/account/delete", methods=(["GET", "POST"]))
def account_delete():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("account_delete.html")
    else:
        if 'change' in request.form:
            id = request.form["id"]
            try:
                x = int(id)
                if len(id) != 6:
                    return render_template("account_delete.html", failed=1)
            except:
                return render_template("account_delete.html", failed=1)
            cursor = db.cursor()
            sql = "select accounts.accountID,money,bank,settime,accounts.accounttype,cusID,visit,overdraft,interestrate,savetype from accounts,saveacc,checkacc,cusforacc where accounts.accountID='%s' and (accounts.accountID=checkacc.accountID or accounts.accountID=saveacc.accountID) and cusforacc.accountID=accounts.accountID" % (id)
            cursor.execute(sql)
            results = cursor.fetchall()
            if not results:
                return render_template("account_delete.html", failed = 2)
            return render_template("account_delete.html",success = 1, r=results[0])
        if 'submit' in request.form:
            cursor = db.cursor()
            accountID = request.form["id1"]
            sql = "delete from accounts where accountID='%s'" %(accountID)
            try:
                cursor.execute(sql)
                db.commit()
                return render_template("customer_delete.html", success = 2)
            except:
                db.rollback()
                return render_template("customer_delete.html", failed=3)

@app.route("/loan/create", methods=(["GET", "POST"]))
def loan_create():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    cursor = db.cursor()
    sql = "select * from bank"
    cursor.execute(sql)
    results = cursor.fetchall()
    bank0 = [i[0] for i in results]
    if request.method == "GET":
        session['number'] = 1
        return render_template("loan_create.html",bank = bank0,number = range(session['number']))
    else:
        if 'add' in request.form:
            session['number'] += 1
            return render_template("loan_create.html", bank=bank0, number=range(session['number']))
        if 'delete' in request.form:
            session['number'] -= 1
            return render_template("loan_create.html", bank=bank0, number=range(session['number']))
        if 'submit' in request.form:
            id = request.form["id"]
            money = request.form["money"]
            bank = request.form["bank"]
            customer = []
            for i in range(session['number']):
                customer.append(request.form["customer"+str(i)])
            try:
                x = int(id)
                x = float(money)
                for i in customer:
                    x = int(i)
                    if len(i)!= 18:
                        return render_template("loan_create.html", failed=1, bank=bank0,number = range(session['number']))
                if len(id) != 4:
                    return render_template("loan_create.html", failed=1,bank = bank0,number = range(session['number']))
            except:
                return render_template("loan_create.html", failed=1,bank = bank0,number = range(session['number']))
            sql = []
            sql.append("INSERT INTO loan (loanID,money,bank) VALUES('%s','%s','%s')" % (id,money,bank))
            for i in customer:
                sql.append("INSERT INTO cusforloan VALUES('%s','%s')" % (id,i))
            try:
                for i in sql:
                    cursor.execute(i)
                db.commit()
                return render_template("loan_create.html", success=1, bank=bank0,number = range(session['number']))
            except:
                db.rollback()
                return render_template("loan_create.html", failed=2, bank=bank0,number = range(session['number']))

@app.route("/loan/", methods=(["GET", "POST"]))
@app.route("/loan/search", methods=(["GET", "POST"]))
def loan_search():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("loan_search.html")
    else:
        id = request.form["id"]
        if not id:
            cursor = db.cursor()
            sql = "select * from loan"
            cursor.execute(sql)
            results = cursor.fetchall()
            r = list(results)
            for i in range(len(results)):
                sql = "select cusID from cusforloan where loanID='%s'"% (results[i][0])
                cursor.execute(sql)
                customer = cursor.fetchall()
                r[i] = r[i] + customer
            sql = "select * from payinfo"
            cursor.execute(sql)
            pay = cursor.fetchall()
            return render_template("loan_search.html", success = 1, results = r,pay = pay)
        try:
            x = int(id)
            if len(id)!= 4:
                return render_template("loan_search.html",failed = 1)
        except:
            return render_template("loan_search.html", failed=1)
        cursor = db.cursor()
        sql = "select * from loan where loanID='%s'" %(id)
        cursor.execute(sql)
        results = cursor.fetchall()[0]
        if not results:
            return render_template("loan_search.html", failed=3)
        sql = "select cusID from cusforloan where loanID='%s'"% (id)
        cursor.execute(sql)
        customer = cursor.fetchall()
        sql = "select * from payinfo where loanID='%s'"%(id)
        cursor.execute(sql)
        pay = cursor.fetchall()
        print(results)
        print(customer)
        print(results+customer)
        return render_template("loan_search.html", success=1, results=[results+customer], pay=pay)

@app.route("/loan/grant", methods=(["GET", "POST"]))
def loan_grant():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("loan_grant.html")
    else:
        id = request.form["id"]
        customer = request.form["customer"]
        money = request.form["money"]
        try:
            x = int(id)
            x = int(customer)
            x = float(money)
            if len(id)!= 4 or len(customer)!= 18:
                return render_template("loan_grant.html",failed = 1)
        except:
            return render_template("loan_grant.html", failed=1)
        cursor = db.cursor()
        sql = "select * from cusforloan where loanID='%s' and cusID='%s'" %(id,customer)
        cursor.execute(sql)
        results = cursor.fetchall()
        if not results:
            return render_template("loan_grant.html", failed=2)
        sql = "INSERT INTO payinfo VALUES('%s','%s','%s','%s')" % (id,customer,money,datetime.datetime.now().strftime('%Y-%m-%d'))
        try:
            cursor.execute(sql)
            db.commit()
            return render_template("loan_grant.html", success=1)
        except:
            db.rollback()
            return render_template("loan_grant.html",failed = 3)

@app.route("/loan/delete", methods=(["GET", "POST"]))
def loan_delete():
    if 'username' in session:
        db = db_login(session['username'], session['password'],
                        session['ipaddr'], session['database'])
    else:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("loan_delete.html")
    else:
        if 'delete' in request.form:
            id = request.form["id"]
            try:
                x = int(id)
                if len(id)!=4:
                    return render_template("loan_delete.html",failed = 1)
            except:
                return render_template("loan_delete.html", failed=1)
            session['loanID'] = id
            cursor = db.cursor()
            sql = "select * from loan where loanID='%s'" % (id)
            cursor.execute(sql)
            results = cursor.fetchall()[0]
            if not results:
                return render_template("loan_delete.html", failed=2)
            sql = "select cusID from cusforloan where loanID='%s'" % (id)
            cursor.execute(sql)
            customer = cursor.fetchall()
            return render_template("loan_delete.html", success=1, r=results+customer)
        if 'sure' in request.form:
            sql = "delete from loan where loanID='%s'" % (session['loanID'])
            cursor = db.cursor()
            try:
                cursor.execute(sql)
                db.commit()
                return render_template("loan_delete.html", success=2)
            except:
                db.rollback()
                return render_template("loan_delete.html",failed = 3)

# 测试URL下返回html page
@app.route("/hello")
def hello():
    return "hello world!"

#返回不存在页面的处理
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == "__main__":

    app.run(host = "0.0.0.0", debug=True)