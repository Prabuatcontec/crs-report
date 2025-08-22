from __future__ import print_function  # In python 2.7
import sys
from flask import Flask, render_template, jsonify, request
import socket
import json
from config import Config
import os

conf = Config()
import time
from datetime import datetime, date, timedelta
import os
import pyodbc
from operator import itemgetter
import numpy as np
from itertools import groupby
import json
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = conf.DATABASE_CONFIG["user"]
app.config["MYSQL_DATABASE_PASSWORD"] = conf.DATABASE_CONFIG["password"]
app.config["MYSQL_DATABASE_DB"] = conf.DATABASE_CONFIG["name"]
app.config["MYSQL_DATABASE_HOST"] = conf.DATABASE_CONFIG["server"]
mysql.init_app(app)
import logging
import requests
from flask_apscheduler import APScheduler
from time import gmtime, strftime
import math


@app.route("/turnon/data")
def index_turn_on():
    try:
        cmd = "curl http://admin:1234@10.10.155.16:80/outlet?1=ON"
        os.system(cmd)
        return render_template("index.html", wh="222")
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/turnoff/data")
def index_turn_off():
    try:
        cmd = "curl http://admin:1234@10.10.155.16:80/outlet?1=OFF"
        os.system(cmd)
        return render_template("index.html", wh="222")
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/<wh>")
def index(wh):
    try:
        return render_template("index.html", wh=wh)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/abb/model", methods=["POST", "GET"])
def index_abb():
    try:
        if request.method == "POST":
            serial = request.form["serial"]
            model = request.form["model"]
            conn = pyodbc.connect(
                driver="{ODBC Driver 17 for SQL Server}",
                host=conf.DATABASE_UNIT_CONFIG["server"],
                database=conf.DATABASE_UNIT_CONFIG["name"],
                user=conf.DATABASE_UNIT_CONFIG["user"],
                password=conf.DATABASE_UNIT_CONFIG["password"],
                autocommit=True,
            )
            cursor = conn.cursor()
            cursor.fast_executemany = True
            sql = (
                "Update Deepblu_Unit.dbo.ABUT SET ABUT_ModelEqp ='"
                + model
                + "' Where  ABUT_EqpSerial='"
                + serial
                + "'"
            )
            # print(sql)
            cursor.execute(sql)
            return render_template("abb.html", ws="Changed Successfully!!!")
        return render_template("abb.html", ws="")
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/assembly/<wh>")
def indexasm(wh):
    try:
        return render_template("assembly.html", wh=wh)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/assemblyreport/<wh>")
def indexasmreport(wh):
    try:
        return render_template("assemblyrep.html", wh=wh)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/assemblydata/<wh>")
def indexasmdata2(wh):
    try:
        return render_template("assemblydatarep.html", wh=wh)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/target/updatetarget", methods=["POST"])
def llm2query():
    id = request.form["id"]
    count = request.form["count"]
    conn = pyodbc.connect(
        driver="{ODBC Driver 17 for SQL Server}",
        host=conf.DATABASE_UNIT_CONFIG["server"],
        database=conf.DATABASE_UNIT_CONFIG["name"],
        user=conf.DATABASE_UNIT_CONFIG["user"],
        password=conf.DATABASE_UNIT_CONFIG["password"],
        autocommit=True,
    )
    cursor = conn.cursor()
    cursor.fast_executemany = True
    sql = (
        "Update Deepblu_Unit..ASTT SET ASTT_Target = "
        + str(int(count))
        + " Where  ASTT_ID="
        + str(int(id))
        + " "
    )
    cursor.execute(sql)
    return {"result": True}


@app.route("/target/<wh>")
def indexasmtarget(wh):
    try:
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        sql = (
            "select ASTT_ID, IPMT_Label, IPMT_Desc,ASTT_Target,ASTT_Hr, ASTT_Warehouse from Deepblu_Unit..ASTT \
LEFT JOIN Deepblu..IPMT ON ASTT_Station = IPMT_ID \
Where ASTT_Warehouse = '"
            + str(wh)
            + "' AND IPMT_Desc is NOT NULL ORDER BY IPMT_Desc "
        )
        cursor.execute(sql)
        result = cursor.fetchall()
        stations = []
        station_count = []

        for station in result:
            hr = station[4]
            if station[5] == "bloomington" or station[5] == "brownsville":
                hr = hr + 2
            if station[5] == "charlotte":
                hr = hr + 3
            stations.append(
                {
                    "id": station[0],
                    "name": station[1] + "(" + str(station[2]) + ")",
                    "target": station[3],
                    "hr": hr,
                    "wh": station[5],
                }
            )

        cursor.close()
        conn.close()
        return render_template("target.html", wh=wh, stations=stations)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/receiving1/<wh>")
def indexrec(wh):
    try:
        return render_template("receiving.html", wh=wh)
    except Exception as a:
        # print(a)
        return render_template("error.html")

@app.route("/receiving/<wh>")
def index_med(wh):
    try:
        return render_template("receivingmed.html", wh=wh)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/testing/<wh>")
def indextesting(wh):
    try:
        return render_template("testing.html", wh=wh)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/wh-data/<wh>")
def index_wh(wh):
    try:
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        d1 = date.today()
        d2 = date.today() + timedelta(days=1)
        sql = (
            "select SOIT_Station, Count(1) from deepblu_digest..SOIT_cms WITH (NOLOCK) Where SOIT_ProcessTime BETWEEN \
        '"
            + str(d1)
            + "' AND '"
            + str(d2)
            + "'  \
        GROUP BY SOIT_Station"
        )
        cursor.execute(sql)
        result = cursor.fetchall()
        dbserials = []
        total = 0

        for res in result:
            if res[0] != None:
                if res[0].find(wh.upper()) == 0:
                    str_ = res[0].replace(wh.upper() + "-", "")
                    if str_ == "MRBFDXUPS":
                        str_ = "SHIP08"
                    if str_ == "SHIP16":
                        str_ = "SHIP03"
                    if str_ == "SHIP21":
                        str_ = "SHIP04"
                    total = total + res[1]
                    dbserials.append({"station": str_, "count": res[1]})

        dbserials = sorted(dbserials, key=itemgetter("station"))
        dbserials.append({"station": "Total", "count": total})

        sql = (
            "select SOIT_Station, Count(1),DATEPART(HOUR, SOIT_ProcessTime)  from deepblu_digest..SOIT_cms WITH (NOLOCK) Where SOIT_ProcessTime BETWEEN \
                '"
            + str(d1)
            + "' AND '"
            + str(d2)
            + "'  \
                GROUP BY SOIT_Station,DATEPART(HOUR, SOIT_ProcessTime) Order by DATEPART(HOUR, SOIT_ProcessTime) DESC"
        )
        cursor.execute(sql)
        result = cursor.fetchall()
        dbserials2 = []
        dbserials2 = {}
        hrs_today = []
        shp_tday = []
        for res in result:
            if res[0] != None:
                if res[0].find(wh.upper()) == 0:
                    str_ = res[0].replace(wh.upper() + "-", "")

                    if str_ == "MRBFDXUPS":
                        str_ = "SHIP08"
                    if str_ == "SHIP16":
                        str_ = "SHIP03"
                    if str_ == "SHIP21":
                        str_ = "SHIP04"
                    if str_ not in shp_tday:
                        shp_tday.append(str_)
                    if wh == "cld":
                        res[2] = res[2] + 3
                    if wh == "bld" or wh == "brd":
                        res[2] = res[2] + 2

                    res[2] = str(res[2])

                    if res[2] not in hrs_today:
                        hrs_today.append(res[2])
                    if res[2] not in dbserials2:
                        dbserials2[res[2]] = {}
                    if str_ not in dbserials2[res[2]]:
                        dbserials2[res[2]][str_] = 0
                    dbserials2[res[2]][str_] = dbserials2[res[2]][str_] + res[1]

                    if "Total" not in dbserials2[res[2]]:
                        dbserials2[res[2]]["Total"] = 0
                    dbserials2[res[2]]["Total"] = dbserials2[res[2]]["Total"] + res[1]
        shp_tday.append("Total")
        cursor.close()
        conn.close()
        res = {
            "today": dbserials,
            "hrs": dbserials2,
            "ahrs": hrs_today,
            "shp_tday": shp_tday,
        }
        return jsonify(res)
    except Exception as a:
        # print(a)
        return render_template("error.html")


@app.route("/testing/wh-testing/<wh>")
def testing_report(wh):
    try:
        d1 = date.today()
        d2 = date.today() + timedelta(days=1)
        wh_qry = " 1=1 AND "
        if wh != "all":
            wh_qry = " DataWhse.dimHubs.id = " + str(int(wh)) + " AND  "
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = (
            "SELECT  DataWhse.dimHubs.Description as SiteName, \
        TestTypes.Name,  \
        Count(1), \
        CASE WHEN Count(Testing.TestResults.SN) = 1 \
        and Testing.TestResults.UUTResult = 'P' THEN 'STP' WHEN Count(Testing.TestResults.SN) = 1 \
        and Testing.TestResults.UUTResult = 'F' THEN 'STF' WHEN Count(Testing.TestResults.SN) > 1 \
        and ( \
            Select \
                UUTResult \
            FROM \
                Testing.TestResults as ts \
            Where \
            ts.SN = Testing.TestResults.SN \
            order by \
                ts.DWid desc \
                    limit 1  \
        ) = 'P' THEN 'MTP' WHEN Count(Testing.TestResults.SN) > 1  \
            and ( Select UUTResult FROM Testing.TestResults as ts \
                Where ts.SN = Testing.TestResults.SN order by  ts.DWid desc  limit 1 ) = 'F' \
                    THEN 'MTF' ELSE 'MTF' END AS QuantityText  \
        FROM  \
            Testing.TestResults  INNER JOIN (  \
            Select  UUTResult FROM Testing.TestResults Where TestResults.SN = Testing.TestResults.SN  \
            order by DWid desc limit 1 ) c2  \
        LEFT JOIN TestTypes ON Testing.TestResults.TestTypeID = TestTypes.TestTypeID  \
        LEFT JOIN DataWhse.dimHubs ON DataWhse.dimHubs.id = Testing.TestResults.Hub \
        Where "
            + wh_qry
            + "  TestDate BETWEEN '"
            + str(d1)
            + " 00:00:00' AND '"
            + str(d1)
            + " 23:59:36'   \
        GRoup by  \
        Testing.TestResults.SN  ORDER by DWid, Testing.TestResults.SN"
        )

        cursor.execute(sql)
        data_added = cursor.fetchall()

        single = {}
        single["MTP"] = 0
        single["STP"] = 0
        single["MTF"] = 0
        single["STF"] = 0
        single["Single"] = 0
        single["Repeated"] = 0
        single["Total"] = 0
        single_qt = {}

        test_type = []

        for data in data_added:
            if data[1] not in single_qt:
                single_qt[data[1]] = {}
                single_qt[data[1]]["MTP"] = 0
                single_qt[data[1]]["STP"] = 0
                single_qt[data[1]]["MTF"] = 0
                single_qt[data[1]]["STF"] = 0
                single_qt[data[1]]["Single"] = 0
                single_qt[data[1]]["Repeated"] = 0
                single_qt[data[1]]["Total"] = 0
            if data[3] == "MTP":
                single["Repeated"] = single["Repeated"] + data[2]
                single["MTP"] = single["MTP"] + data[2]
                single_qt[data[1]]["Repeated"] = (
                    single_qt[data[1]]["Repeated"] + data[2]
                )
                single_qt[data[1]]["MTP"] = single_qt[data[1]]["MTP"] + data[2]
            if data[3] == "MTF":
                single["Repeated"] = single["Repeated"] + data[2]
                single["MTF"] = single["MTF"] + data[2]
                single_qt[data[1]]["Repeated"] = (
                    single_qt[data[1]]["Repeated"] + data[2]
                )
                single_qt[data[1]]["MTF"] = single_qt[data[1]]["MTF"] + data[2]
            if data[3] == "STP":
                single["Single"] = single["Single"] + data[2]
                single["STP"] = single["STP"] + data[2]
                single_qt[data[1]]["Single"] = single_qt[data[1]]["Single"] + data[2]
                single_qt[data[1]]["STP"] = single_qt[data[1]]["STP"] + data[2]
            if data[3] == "STF":
                single["Single"] = single["Single"] + data[2]
                single["STF"] = single["STF"] + data[2]
                single_qt[data[1]]["Single"] = single_qt[data[1]]["Single"] + data[2]
                single_qt[data[1]]["STF"] = single_qt[data[1]]["STF"] + data[2]
            single["Total"] = single["Total"] + data[2]
            single_qt[data[1]]["Total"] = single_qt[data[1]]["Total"] + data[2]
            if data[1] not in test_type:
                test_type.append(data[1])
        res = {"today": single, "testtype": single_qt, "testtypes": test_type}
        return jsonify(res)
    except Exception as a:
        # print(a)
        return jsonify(a)


@app.route("/shipments/data")
def index_asm_shp_with_user():
    try:
        print(request.args)
        if 'dateFrom' in request.args:
            dateFrom = request.args['dateFrom']
        if 'dateTo' in request.args:
            dateTo = request.args['dateTo']
        
        # d1 = '2025-02-05' 
        sql = (" select  SOMT_RecWarehouse As Warehouse, DATEADD(dd, 0, DATEDIFF(dd, 0,SOIT_ProcessTime)) As Date, DATEPART(HOUR, SOIT_ProcessTime)  As Hr,CMIT_CustomerID As Customer, SOIT_User As Shipper , count(1) as ShippedCount from Deepblu_Logging..SOIT_CMSA \
 LEFT JOIN Deepblu_Shipping..SOST ON SOST_ShipID = SOIT_ShipID \
 LEFT JOIN Deepblu_Shipping..SOMT ON SOMT_OrderID = SOST_OrderID \
  LEFT JOIN DeepBlu.dbo.CDIT  ON SOMT_ShipDivID = CDIT_CusDivID \
  LEFT JOIN DeepBlu.dbo.CMIT  ON CMIT_CustomerID = CDIT_CustomerID \
 Where  SOIT_ProcessTime BETWEEN '"+str(dateFrom)+"' AND  '"+str(dateTo)+"'  GROUP BY SOMT_RecWarehouse, DATEADD(dd, 0, DATEDIFF(dd, 0,SOIT_ProcessTime)), DATEPART(HOUR, SOIT_ProcessTime)  ,CMIT_CustomerID, SOIT_User ")
        print(sql)
        conn = pyodbc.connect(
        driver="{ODBC Driver 17 for SQL Server}",
        host=conf.DATABASE_UNIT_CONFIG["server"],
        database=conf.DATABASE_UNIT_CONFIG["name"],
        user=conf.DATABASE_UNIT_CONFIG["user"],
        password=conf.DATABASE_UNIT_CONFIG["password"],
        autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()      
        PalletList = []
        for res in result:
            pallet_dict = {
                'warehouse': res[0],
                'date': str(res[1]),
                'hr': res[2],
                'customer': res[3],
                'user': res[4],
                'shipped': res[5]
            }
            PalletList.append(pallet_dict)            
        return jsonify(PalletList)
    except Exception as a:
        # print(a)
        return jsonify(a)
    
@app.route("/assembly/wh-assembly/<wh>/<user>")
def index_asm_wh_with_user(wh,user):
    try:
        d1 = date.today()
        # d1 = '2025-02-05'
        if wh != 'all':
            where = " AND PATT_Warehouse = '"+wh+"'"
        else:
            where =""
        sql = ("SELECT PAMT_PalletID,PAMT_ItemID,PAMT_FG,PAST_Serial,PATT_TransUser,PATT_Warehouse,PAST_AddDate,PAST_AddTime FROM Deepblu_Unit..PATT JOIN Deepblu_Unit..PAMT ON PAMT_ID = PATT_PalletKey JOIN Deepblu_Unit..PAST ON PAST_PalletKey = PAMT_ID where PATT_TransUser = '"+user+"'" +" "+ where +  "AND PAST_AddDate = '"+str(d1)+"' ")
        # return(sql)
        conn = pyodbc.connect(
        driver="{ODBC Driver 17 for SQL Server}",
        host=conf.DATABASE_UNIT_CONFIG["server"],
        database=conf.DATABASE_UNIT_CONFIG["name"],
        user=conf.DATABASE_UNIT_CONFIG["user"],
        password=conf.DATABASE_UNIT_CONFIG["password"],
        autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()      
        PalletList = []
        for res in result:
            pallet_dict = {
                'palletid': res[0],
                'itemid': res[1],
                'serial': res[3],
                'user': res[4],
                'warehouse': res[5],
                'Adddate': res[6],
                'Addtime': res[7]
            }
            PalletList.append(pallet_dict)            
        return jsonify(PalletList)
    except Exception as a:
        # print(a)
        return jsonify(a)
    
    ""


@app.route("/receiving/bl-receiving", methods=["POST"])
def index_rec_bl_wh():
    try:
        wh = request.form["warehouse"]
        d1 = date.today()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_hr = now.strftime("%H")
        current_min = now.strftime("%M")
        if current_time > '12:10:00' and current_time < '04:00:00':
            return 1
        target = 246
        wh_qry = " 1=1 AND "
        if wh != "all":
            wh_qry = " PAMT_Warehouse = '" + str(wh) + "' AND  "
        t = 0
        if wh == "bloomington":
            t = 2
        if wh == "charlotte":
            t = 3
        date_sel = request.form["date"]
        sql = """SELECT 
            MIBT_InboundUserWarehouse AS Warehouse,
            PAST_AddDate AS AddDate,
            DATEPART(hour, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))) AS Hr,
            COUNT(1) AS RecordCount
         FROM 
            DeepBlu_Unit..MIBT
         JOIN 
            DeepBlu_Unit..PAMT ON PAMT_PalletID = MIBT_ReceivedPalletID
         JOIN 
            DeepBlu_Unit..PAST ON PAST_PalletKey = PAMT_ID AND MIBT_Serial = PAST_Serial
         WHERE 
            MIBT_Scanned = 1
            AND PAST_AddDate = '"""+str(date_sel)+"""'
            AND PAMT_Warehouse = '"""+str(wh)+"""'
         GROUP BY 
            MIBT_InboundUserWarehouse, PAST_AddDate, 
            DATEPART(hour, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108)))
         ORDER BY 
            Hr ASC;"""

        print(sql)
        # Database connection
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        
        PalletList = []
        pallet_dict_val = {}
        
        for res in result:
            if str(d1) == str(date_sel):  # Ensure d1 is defined earlier
                if int(res[2]) + int(t) == int(current_hr) + int(t):  # Ensure current_hr and t are initialized
                    target = int((target / 60) / 60) * int(current_min)  # Ensure target and current_min are defined

            pallet_dict = {
                'hr': int(res[2]) + int(t),
                'cnt': res[3],  # Adjusted to correct index
                'total': res[3] - target,
                'target': target
            }
            PalletList.append(pallet_dict)
        
        pallet_dict_val['result'] = PalletList
        print(pallet_dict_val)
        return jsonify(pallet_dict_val)
    except Exception as a:
        # print(a)
        return jsonify(a)



@app.route("/receiving/bl-receiving-user", methods=["POST"])
def index_rec_bl_wh_user():
    try:
        wh = request.form["warehouse"]
        date_sel = request.form["date"]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        # Fix incorrect time comparison (use datetime for comparison)
        if "12:10:00" < current_time < "04:00:00":  
            return jsonify({"error": "Invalid time range"}), 400  # Return proper error response

        # Database connection
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()

        # Fetch unique users safely using parameterized query
        sql_users = """
        SELECT DISTINCT MIBT_ValidationUser
        FROM DeepBlu_Unit..MIBT
        JOIN DeepBlu_Unit..PAMT ON PAMT_PalletID = MIBT_ReceivedPalletID
        JOIN DeepBlu_Unit..PAST ON PAST_PalletKey = PAMT_ID AND MIBT_Serial = PAST_Serial
        WHERE MIBT_Scanned = 1
        AND PAST_AddDate = ?
        AND PAMT_Warehouse = ?
        """
        cursor.execute(sql_users, (date_sel, wh))
        users = [row[0] for row in cursor.fetchall()]  # Extract user list

        # Dynamic column generation
        user_columns = ", ".join(
            [f"SUM(CASE WHEN MIBT_ValidationUser = ? THEN 1 ELSE 0 END) AS [{user}]" for user in users]
        )
        sql_dynamic = f"""
            SELECT 
                MIBT_InboundUserWarehouse AS Warehouse,
                PAST_AddDate AS AddDate,
                DATEPART(hour, PAST_AddTime) AS Hr,
                {user_columns}
            FROM (
                SELECT 
                    MIBT_InboundUserWarehouse,
                    MIBT_ValidationUser,
                    PAST_AddDate,
                    PAST_AddTime
                FROM DeepBlu_Unit..MIBT
                JOIN DeepBlu_Unit..PAMT ON PAMT_PalletID = MIBT_ReceivedPalletID
                JOIN DeepBlu_Unit..PAST ON PAST_PalletKey = PAMT_ID AND MIBT_Serial = PAST_Serial
                WHERE MIBT_Scanned = 1 
                AND PAST_AddDate = ? 
                AND PAMT_Warehouse = ?
            ) AS Subquery
            GROUP BY MIBT_InboundUserWarehouse, PAST_AddDate, DATEPART(hour, PAST_AddTime)
            ORDER BY Hr ASC;
        """

        # Execute query with dynamic user parameters
        cursor.execute(sql_dynamic, users + [date_sel, wh])
        result = cursor.fetchall()

        # Convert to JSON format
        PalletList = []
        for row in result:
            if row[0] == 'Bloomington':
                row[2] = int(row[2]) + 2
            if row[0] == 'Charlotte':
                row[2] = int(row[2]) + 3
            pallet_dict = {
                "Warehouse": row[0],       
                "AddDate": row[1],        
                "Hr": row[2],             
            }
            for idx, user in enumerate(users):
                pallet_dict[user] = row[3 + idx]
            PalletList.append(pallet_dict)

        return jsonify({"result": PalletList})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

            
@app.route("/assembly/wh-assembly/<wh>")
def index_asm_wh(wh):
    try:
        d1 = date.today()
        # d1 = '2025-01-03'
        wh_qry = " 1=1 AND "
        if wh != "all":
            wh_qry = " PAMT_Warehouse = '" + str(wh) + "' AND  "
        sql = (
            "select  PATT_TransUser, COUNT(PAMT_Qty),DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))), PAMT_Warehouse from Deepblu_unit..PAMT  WITH (NOLOCK) \
                LEFT JOIN Deepblu_unit..PATT  WITH (NOLOCK) ON PAMT_ID = PATT_PalletKey \
				LEFT JOIN Deepblu_unit..PAST  WITH (NOLOCK) ON PAMT_ID = PAST_PalletKey \
                Where "
            + wh_qry
            + "  Past_AddDate = '"
            + str(d1)
            + "' GROUP BY PATT_TransUser ,DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))),PAMT_Warehouse Order by \
				DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))), PATT_TransUser "
        )

        logging.error(sql)
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        dbserials = []
        wh_rec = {}
        tol_1 = 0
        hrs_data = []
        user_data = {}
        all_whs_total = {}
        all_whs = []
        for res in result:
            if res[0] is not None and res[0] != "":
                if res[3].lower() == "charlotte":
                    res[2] = res[2] + 3
                if res[3].lower() == "bloomington" or res[3].lower() == "brownsville":
                    res[2] = res[2] + 2
                if res[3] not in wh_rec:
                    wh_rec[res[3]] = {}

                if res[3] not in all_whs_total:
                    all_whs_total[res[3]] = {}

                if res[2] not in all_whs_total[res[3]]:
                    all_whs_total[res[3]][res[2]] = 0
                all_whs_total[res[3]][res[2]] = all_whs_total[res[3]][res[2]] + res[1]
                if res[0] not in wh_rec[res[3]]:
                    wh_rec[res[3]][res[0]] = {}

                if res[2] not in wh_rec[res[3]][res[0]]:
                    wh_rec[res[3]][res[0]][res[2]] = 0
                wh_rec[res[3]][res[0]][res[2]] = res[1]

                if res[2] not in hrs_data:
                    hrs_data.append(res[2])

                if res[3] not in user_data:
                    user_data[res[3]] = []
                if res[0] not in user_data[res[3]]:
                    user_data[res[3]].append(res[0])

                if res[3] not in all_whs:
                    all_whs.append(res[3])

                tol_1 = tol_1 + res[1]
        dbserials1 = []
        res = {
            "today": dbserials,
            "onehr": dbserials1,
            "wh_rec": wh_rec,
            "hrs_data": hrs_data,
            "user_data": user_data,
            "all_whs": all_whs,
            "all_whs_total": all_whs_total,
        }
        return jsonify(res)
    except Exception as a:
        # print(a)
        return jsonify(a)


@app.route("/assemblyreport/assemblydata/wh-assemblynew/<wh>/<d1>")
def index_asm_wh_new(wh, d1):
    try:
        wh_qry = " 1=1 AND "
        if wh != "all":
            wh_qry = " PAMT_Warehouse = '" + str(wh) + "' AND  "
        sql = (
            "SELECT c1.IPMT_Label as Lab,c1.cont as scanned, c1.im3 as hr,\
                        c1.PAMT_Warehouse,\
                        ( ( c1.im / 60 ) * c1.mint ) as Tar,\
                            c1.im4,\
                        c1.im5,\
                        c1.IPMT_Desc,\
                        ROUND(CAST(( (c1.cont * 100.0 ) / NULLIF((( c1.im / 60 ) * c1.mint ), 0)) AS FLOAT), 2)  as per,\
                        c1.im3 as hr,\
                        c1.im,\
                        c1.IMIT_ItemId,\
                        c1.Pamt_BuildID,\
                        c1.im1,\
                        c1.im2,\
                        c1.im3,\
                        c1.ASTT_Target,\
                        c1.PAMT_ID, \
                        c1.IMIT_ItemId,\
                        c1.mint, c1.PAMT_PalletID\
                    FROM\
                    (SELECT *,\
                        (SELECT count(*)\
                        FROM\
                            (SELECT count(1) AS cnt\
                            FROM Deepblu_unit..PAST WITH (NOLOCK)\
                            WHERE PAST_PalletKey = q1.PAMT_ID\
                            AND DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))) = q1.im3\
                            GROUP BY PAST_UnitNumber\
                            ) AS cnt1) AS cont,\
                            DATEDIFF(MINUTE,\
                                        (SELECT top 1 CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))\
                                        FROM Deepblu_unit..PAST WITH (NOLOCK)\
                                        WHERE PAST_PalletKey = q1.PAMT_ID\
                                            AND DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))) = q1.im3\
                                        ORDER BY PAST_ID ASC) ,\
                                        (SELECT top 1 CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))\
                                        FROM Deepblu_unit..PAST WITH (NOLOCK)\
                                        WHERE PAST_PalletKey = q1.PAMT_ID\
                                            AND DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))) = q1.im3\
                                        ORDER BY PAST_ID DESC)) AS mint\
                    FROM\
                        (SELECT COALESCE (IMIT_UnitsPerHour,\
                                        100) AS im,\
                                        IMIT_ItemId,\
                                        Pamt_BuildID,\
                                        IPMT_Label,\
                                        Count(PAMT_Qty) AS im1,\
                                        Count(PAST_UnitNumber) AS im2,\
                                        DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108)))AS im3,\
                                        PAMT_Warehouse,\
                                        ASTT_Target,\
                                        DATEPART(MINUTE, GETDATE()) AS im4,\
                                        DATEPART(HOUR, GETDATE()) AS im5,\
                                        IPMT_Desc,\
                                        ASTT_Hr,\
                                        PAMT_ID,\
                                        PAST_AddDate,\
                                        PAST_AddTime, PAMT_PalletID\
                        FROM Deepblu_unit..PAMT WITH (NOLOCK)\
                        LEFT JOIN Deepblu_unit..ASTT WITH (NOLOCK) ON ASTT_Station = PAMT_RecvType\
                        LEFT JOIN Deepblu_unit..PAST WITH (NOLOCK) ON PAMT_ID = PAST_PalletKey\
                        AND ASTT_Hr = DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108)))\
                        LEFT JOIN Deepblu..IPMT WITH (NOLOCK) ON IPMT_ID = PAMT_RecvType\
                        LEFT JOIN Deepblu..imit ON PAMT_ItemID = IMIT_ItemId\
                        WHERE "
            + wh_qry
            + "\
                             Pamt_BuildID IS NOT NULL\
                            AND PAST_AddDate = '"
            + str(d1)
            + "'\
                        GROUP BY IPMT_Label,\
                                PAMT_RecvType,\
                                ASTT_Target,\
                                DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))),\
                                PAMT_Warehouse,\
                                IPMT_Desc,\
                                ASTT_Hr,\
                                Pamt_BuildID,\
                                IMIT_UnitsPerHour,\
                                IMIT_ItemId,\
                                PAMT_ID,\
                                PAST_AddDate,PAMT_PalletID,\
                                PAST_AddTime) q1) c1 where c1.cont > 0  \
                    GROUP BY c1.im,\
                            c1.IMIT_ItemId,\
                            c1.Pamt_BuildID,\
                            c1.IPMT_Label,\
                            c1.im1,\
                            c1.im2,\
                            c1.im3,\
                            c1.PAMT_Warehouse,\
                            c1.ASTT_Target,\
                            c1.im4,\
                            c1.im5,\
                            c1.IPMT_Desc,\
                            c1.ASTT_Hr,\
                            c1.PAMT_ID,\
                            c1.cont,\
                            c1.mint,c1.PAMT_PalletID "
        )

        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        dbserials = []
        wh_rec = {}
        wh_rec_per = {}
        wh_rec_per_cnt = {}
        wh_rec_target = {}
        tol_1 = 0
        tol_target = 0
        hrs_data = []
        user_data = {}
        user_desc_data = {}
        all_whs_total = {}
        all_whs_total_per = {}
        items = {}
        items_target = {}
        grid_object = {}
        all_whs = []
        datas_val = result

        for res in datas_val:
            if res[0] is not None and res[0] != "":
                if res[3].lower() == "charlotte":
                    res[2] = res[2] + 3
                    res[6] = res[6] + 3
                if res[3].lower() == "bloomington" or res[3].lower() == "brownsville":
                    res[2] = res[2] + 2
                    res[6] = res[6] + 2

                if res[3] not in wh_rec:
                    wh_rec[res[3]] = {}
                if res[3] not in wh_rec_per:
                    wh_rec_per[res[3]] = {}
                if res[3] not in wh_rec_per_cnt:
                    wh_rec_per_cnt[res[3]] = {}

                if res[3] not in all_whs_total:
                    all_whs_total[res[3]] = {}

                if res[2] not in all_whs_total[res[3]]:
                    all_whs_total[res[3]][res[2]] = 0
                all_whs_total[res[3]][res[2]] = all_whs_total[res[3]][res[2]] + res[1]

                if res[3] not in all_whs_total_per:
                    all_whs_total_per[res[3]] = {}

                if res[4] is not None:
                    target = res[4]

                if target == 0:
                    target = res[1]
                if res[2] not in all_whs_total_per[res[3]]:
                    all_whs_total_per[res[3]][res[2]] = 0
                # print(str(target) +'===>'+ str(res[1]))
                all_whs_total_per[res[3]][res[2]] = round(
                    ((all_whs_total[res[3]][res[2]]) / target) * 100, 0
                )

                if res[0] not in wh_rec[res[3]]:
                    wh_rec[res[3]][res[0]] = {}
                if res[0] not in wh_rec_per[res[3]]:
                    wh_rec_per[res[3]][res[0]] = {}
                if res[0] not in wh_rec_per_cnt[res[3]]:
                    wh_rec_per_cnt[res[3]][res[0]] = {}
                if res[2] not in wh_rec[res[3]][res[0]]:
                    wh_rec[res[3]][res[0]][res[2]] = 0
                if res[2] not in wh_rec_per[res[3]][res[0]]:
                    wh_rec_per[res[3]][res[0]][res[2]] = 0
                if res[2] not in wh_rec_per_cnt[res[3]][res[0]]:
                    wh_rec_per_cnt[res[3]][res[0]][res[2]] = 0
                wh_rec[res[3]][res[0]][res[2]] = res[1] + wh_rec[res[3]][res[0]][res[2]]

                wh_rec_per_cnt[res[3]][res[0]][res[2]] = (
                    wh_rec_per_cnt[res[3]][res[0]][res[2]] + res[4]
                )
                if res[8] is None:
                    res[8] = 100
                # print(str(res[8]) + '=========='+ str(wh_rec_per_cnt[res[3]][res[0]][res[2]])+ '=========='+ str(res[2]))
                wh_rec_per[res[3]][res[0]][res[2]] = round(
                    (res[1] + wh_rec_per[res[3]][res[0]][res[2]]), 0
                )

                if res[2] not in hrs_data:
                    hrs_data.append(res[2])

                if res[3] not in user_data:
                    user_data[res[3]] = []
                if res[0] not in user_data[res[3]]:
                    user_data[res[3]].append(res[0])
                if res[3] not in user_desc_data:
                    user_desc_data[res[3]] = []
                if res[7] not in user_desc_data[res[3]]:
                    user_desc_data[res[3]].append(res[7])

                if res[3] not in all_whs:
                    all_whs.append(res[3])

                tol_1 = tol_1 + res[1]
                tol_target = tol_target + target

                if res[3] not in items:
                    items[res[3]] = {}
                    items_target[res[3]] = {}
                    grid_object[res[3]] = {}
                if res[0] not in items[res[3]]:
                    items[res[3]][res[0]] = {}
                    items_target[res[3]][res[0]] = {}
                    grid_object[res[3]][res[0]] = {}
                if res[2] not in items[res[3]][res[0]]:
                    items[res[3]][res[0]][res[2]] = []
                    items_target[res[3]][res[0]][res[2]] = {}
                    grid_object[res[3]][res[0]][res[2]] = []
                grid_object[res[3]][res[0]][res[2]].append(
                    {
                        "itemid": res[11],
                        "scanned": res[1],
                        "buildid": res[12],
                        "min": res[19],
                        "palletid": res[20],
                    }
                )
                if res[11] not in items_target[res[3]][res[0]][res[2]]:
                    items_target[res[3]][res[0]][res[2]][res[11]] = res[10]
                if res[11] not in items[res[3]][res[0]][res[2]]:
                    items[res[3]][res[0]][res[2]].append(res[11])

        dbserials1 = []
        res = {
            "today": dbserials,
            "grid_object": grid_object,
            "items": items,
            "items_target": items_target,
            "wh_rec_per_cnt": wh_rec_per_cnt,
            "tol_target": tol_target,
            "onehr": dbserials1,
            "wh_rec": wh_rec,
            "hrs_data": hrs_data,
            "user_data": user_data,
            "user_desc_data": user_desc_data,
            "all_whs": all_whs,
            "all_whs_total": all_whs_total,
            "all_whs_total_per": all_whs_total_per,
            "wh_rec_per": wh_rec_per,
        }
        return jsonify(res)
    except Exception as a:
        # print(a)
        return jsonify(a)


@app.route("/assemblydata/assemblydata/wh-assemblynew/<wh>/<d1>")
def index_asm_data_wh_new(wh, d1):
    try:
        wh_qry = " 1=1 AND "
        if wh != "all":
            wh_qry = " PAMT_Warehouse = '" + str(wh) + "' AND  "
        sql = (
            "select  IPMT_Label, Count(PAMT_Qty),DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))), PAMT_Warehouse, ASTT_Target,DATEPART(MINUTE,GETDATE()), DATEPART(HOUR,GETDATE()),IPMT_Desc,ASTT_Hr from Deepblu_unit..PAMT  WITH (NOLOCK) \
                LEFT JOIN Deepblu_unit..ASTT  WITH (NOLOCK) ON ASTT_Station = PAMT_RecvType \
				LEFT JOIN Deepblu_unit..PAST  WITH (NOLOCK) ON PAMT_ID = PAST_PalletKey and ASTT_Hr =   DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))) \
                LEFT JOIN Deepblu..IPMT  WITH (NOLOCK) ON IPMT_ID = PAMT_RecvType \
                Where "
            + wh_qry
            + "   Pamt_BuildID is NOt NULL and  \
                Past_AddDate = '"
            + str(d1)
            + "' GROUP BY IPMT_Label,PAMT_RecvType, ASTT_Target ,DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))),PAMT_Warehouse, IPMT_Desc,ASTT_Hr Order by \
				DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))), PAMT_RecvType "
        )
        # print(sql)
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        dbserials = []
        wh_rec = {}
        wh_rec_per = {}
        wh_rec_target = {}
        tol_1 = 0
        tol_target = 0
        hrs_data = []
        user_data = {}
        user_desc_data = {}
        all_whs_total = {}
        all_whs_total_per = {}
        all_whs = []
        for res in result:
            if res[0] is not None and res[0] != "":
                if res[3].lower() == "charlotte":
                    res[2] = res[2] + 3
                    res[6] = res[6] + 3
                if res[3].lower() == "bloomington" or res[3].lower() == "brownsville":
                    res[2] = res[2] + 2
                    res[6] = res[6] + 2
                if res[3] not in wh_rec:
                    wh_rec[res[3]] = {}
                if res[3] not in wh_rec_per:
                    wh_rec_per[res[3]] = {}

                wh_rec_target
                if res[3] not in all_whs_total:
                    all_whs_total[res[3]] = {}

                if res[2] not in all_whs_total[res[3]]:
                    all_whs_total[res[3]][res[2]] = 0
                all_whs_total[res[3]][res[2]] = all_whs_total[res[3]][res[2]] + res[1]

                if res[3] not in all_whs_total_per:
                    all_whs_total_per[res[3]] = {}
                target = 100
                if res[4] is not None:
                    target = res[4]
                    if res[2] == res[6]:
                        _min = target / 60
                        target = _min * res[5]

                if res[2] not in all_whs_total_per[res[3]]:
                    all_whs_total_per[res[3]][res[2]] = 0

                all_whs_total_per[res[3]][res[2]] = round(
                    ((all_whs_total[res[3]][res[2]]) / target) * 100, 0
                )

                if res[0] not in wh_rec[res[3]]:
                    wh_rec[res[3]][res[0]] = {}
                if res[0] not in wh_rec_per[res[3]]:
                    wh_rec_per[res[3]][res[0]] = {}
                if res[2] not in wh_rec[res[3]][res[0]]:
                    wh_rec[res[3]][res[0]][res[2]] = 0
                if res[2] not in wh_rec_per[res[3]][res[0]]:
                    wh_rec_per[res[3]][res[0]][res[2]] = 0
                wh_rec[res[3]][res[0]][res[2]] = res[1]

                wh_rec_per[res[3]][res[0]][res[2]] = round(
                    ((wh_rec[res[3]][res[0]][res[2]]) / target) * 100, 0
                )

                if res[2] not in hrs_data:
                    hrs_data.append(res[2])

                if res[3] not in user_data:
                    user_data[res[3]] = []
                if res[0] not in user_data[res[3]]:
                    user_data[res[3]].append(res[0])
                if res[3] not in user_desc_data:
                    user_desc_data[res[3]] = []
                if res[7] not in user_desc_data[res[3]]:
                    user_desc_data[res[3]].append(res[7])

                if res[3] not in all_whs:
                    all_whs.append(res[3])

                tol_1 = tol_1 + res[1]
                tol_target = tol_target + target
        dbserials1 = []
        res = {
            "today": dbserials,
            "tol_target": tol_target,
            "onehr": dbserials1,
            "wh_rec": wh_rec,
            "hrs_data": hrs_data,
            "user_data": user_data,
            "user_desc_data": user_desc_data,
            "all_whs": all_whs,
            "all_whs_total": all_whs_total,
            "all_whs_total_per": all_whs_total_per,
            "wh_rec_per": wh_rec_per,
        }
        return jsonify(res)
    except Exception as a:
        # print(a)
        return jsonify(a)


@app.route("/receiving/wh-receiving/<wh>")
def index_rec_wh(wh):
    try:
        d1 = date.today()
        wh_qry = " 1=1 AND "
        if wh != "all":
            wh_qry = " PAMT_Warehouse = '" + str(wh) + "' AND  "
        sql = (
            "select  PATT_TransUser, COUNT(PAMT_Qty),DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))), PAMT_Warehouse from Deepblu_unit..PAMT  WITH (NOLOCK) \
                LEFT JOIN Deepblu_unit..PATT  WITH (NOLOCK) ON PAMT_ID = PATT_PalletKey \
				LEFT JOIN Deepblu_unit..PAST  WITH (NOLOCK) ON PAMT_ID = PAST_PalletKey \
                Where "
            + wh_qry
            + "  (Pamt_source = 'Detrash' OR Pamt_source ='INVENTORY DETRASH' OR Pamt_source ='ARPNC') and  \
                Past_AddDate = '"
            + str(d1)
            + "' GROUP BY PATT_TransUser ,DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))),PAMT_Warehouse Order by \
				DATEPART(HOUR, CONVERT(DATETIME, CONVERT(CHAR(10), PAST_AddDate, 112) \
                + ' ' + CONVERT(CHAR(8), PAST_AddTime, 108))), PATT_TransUser "
        )
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        dbserials = []
        wh_rec = {}
        tol_1 = 0
        hrs_data = []
        user_data = {}
        all_whs_total = {}
        all_whs = []
        for res in result:
            if res[0] is not None and res[0] != "":
                if res[3].lower() == "charlotte":
                    res[2] = res[2] + 3
                if res[3].lower() == "bloomington" or res[3].lower() == "brownsville":
                    res[2] = res[2] + 2
                if res[3] not in wh_rec:
                    wh_rec[res[3]] = {}

                if res[3] not in all_whs_total:
                    all_whs_total[res[3]] = {}

                if res[2] not in all_whs_total[res[3]]:
                    all_whs_total[res[3]][res[2]] = 0
                all_whs_total[res[3]][res[2]] = all_whs_total[res[3]][res[2]] + res[1]
                if res[0] not in wh_rec[res[3]]:
                    wh_rec[res[3]][res[0]] = {}

                if res[2] not in wh_rec[res[3]][res[0]]:
                    wh_rec[res[3]][res[0]][res[2]] = 0
                wh_rec[res[3]][res[0]][res[2]] = res[1]

                if res[2] not in hrs_data:
                    hrs_data.append(res[2])

                if res[3] not in user_data:
                    user_data[res[3]] = []
                if res[0] not in user_data[res[3]]:
                    user_data[res[3]].append(res[0])

                if res[3] not in all_whs:
                    all_whs.append(res[3])

                tol_1 = tol_1 + res[1]
        dbserials1 = []
        res = {
            "today": dbserials,
            "onehr": dbserials1,
            "wh_rec": wh_rec,
            "hrs_data": hrs_data,
            "user_data": user_data,
            "all_whs": all_whs,
            "all_whs_total": all_whs_total,
        }
        return jsonify(res)
    except Exception as a:
        # print(a)
        return jsonify(a)

@app.route("/getTarget/compare/<wh>/getTargets/", methods=["POST", "GET"])
def getCompareTargets(wh):
    return getTargets()

@app.route("/getTarget/sheet/getTargets/", methods=["POST", "GET"])
def getTargets():
    try:
        resp_data = json.loads(request.data)
        cdate = resp_data["date"]
        wh = resp_data["warehouse"]
        line = resp_data["line"]
        sql = (
            " SELECT   pamt_palletid,COALESCE(PAMT_FG, PAMT_ItemID) as pamt_itemid,PAST.past_unitnumber,Min(PAST.past_addtime) AS MINAddTime,COALESCE(Min(nxt.past_addtime),'no') AS nxtUnitAddTime,COALESCE(IMIT_UnitsPerHour, 200) as IMIT_UnitPerHr FROM deepblu_unit..pamt WITH (nolock) LEFT JOIN deepblu_unit..past WITH (nolock) ON pamt_id = past_palletkey LEFT JOIN deepblu_unit..past nxt WITH (nolock) ON pamt_id = nxt.past_palletkey and nxt.PAST_UnitNumber = (PAST.PAST_UnitNumber+1) LEFT JOIN deepblu..ipmt WITH (nolock) ON ipmt_id = pamt_recvtype LEFT JOIN deepblu..imit ON COALESCE(PAMT_FG, PAMT_ItemID) = imit_itemid WHERE  1 = 1 AND pamt_buildid IS NOT NULL  AND PAMT_RecvType!='nydblinux0'   AND PAST.past_adddate = '"
            + str(cdate)
            + "'  AND PAMT_Warehouse = '"
            + str(wh)
            + "' AND ipmt_label = '"
            + str(line)
            + "' GROUP  BY pamt_palletid, COALESCE(PAMT_FG, PAMT_ItemID), PAST.past_unitnumber,IMIT_UnitsPerHour ORDER  BY MAX(PAST.PAST_AddTime) asc"
        )
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        index = 1
        pallet_timing = {}
        pallet_timing_ten = {}
        for res in result:
            if res[0] not in pallet_timing:
                pallet_timing[res[0]] = {}
                pallet_timing[res[0]] = {"start_time": result[index][3]}
                pallet_timing_ten[res[0]] = {}
                pallet_timing_ten[res[0]] = {"start_time": result[index][3]}
                start_time = result[index][3]
                differenceSeconds = 0
                start_time_ten = result[index][3]
                differenceSecondsTen = 0
            # print(pallet_timing)
            if res[4] == "no":
                if index == len(result):
                    res[4] = result[index - 1][3]
                else:
                    res[4] = result[index][3]
            IdentifyUnitFinishSec = calculetUnitPersSec(res[5])
            IdentifyUnitFinishSecs = int(IdentifyUnitFinishSec * res[2])
            if differenceSeconds != 0:
                IdentifyUnitFinishSecs = IdentifyUnitFinishSecs - IdentifyUnitFinishSec
            else:
                IdentifyUnitFinishSecs = 1
            if res[2] == 1:
                res_add = 1
            else:
                res_add = res[2]
            LastEndTime = res[4]
            if IdentifyUnitFinishSecs == 1:
                differenceSeconds_now = DifferenceCalclulater(res[3], res[4])
                differenceSeconds_add = differenceSeconds_now
                differenceSeconds = differenceSeconds_add
                differenceSecondsNow = differenceSeconds_now
                # print(differenceSeconds)
                color = "badge bg-danger"
                if IdentifyUnitFinishSec >= differenceSeconds_now:
                    color = "badge bg-success"
                IdentifyUnitFinishSecs = differenceSeconds
                time_taken = strftime("%H:%M:%S", gmtime(differenceSeconds_now))
            else:
                differenceSeconds_now = DifferenceCalclulater(start_time, res[4])
                differenceSeconds = differenceSeconds_add + differenceSeconds_now
                IdentifyUnitFinishSecs = IdentifyUnitFinishSecs + differenceSecondsNow

                divValue = math.floor(differenceSeconds / res_add)
                color = "badge bg-danger"
                if IdentifyUnitFinishSec >= divValue:
                    color = "badge bg-success"
                time_taken = strftime("%H:%M:%S", gmtime(divValue))

            pallet_timing[res[0]][str(index - 1)] = {
                "end_time": res[4],
                "units_in_sec": IdentifyUnitFinishSecs,
                "different_sec": differenceSeconds,
                "color": color,
                "time": time_taken,
                "div1": differenceSeconds,
                "div2": res_add,
                "differenceSeconds": differenceSeconds,
                "sec": IdentifyUnitFinishSec,
            }  # {"end_time": res[4], "units_in_sec": IdentifyUnitFinishSecs, "different_sec": differenceSeconds, 'color':color, 'time': strftime("%H:%M:%S", gmtime(differenceSeconds/res[2])), 'div1': differenceSeconds,'div2': res[2]}
            if len(pallet_timing_ten[res[0]]) > 10:
                start_time_ten = result[index - 10][3]
                # print(index)

                differenceSeconds_now = DifferenceCalclulater(start_time_ten, res[4])

                differenceSecondsTen = differenceSeconds_now

                # IdentifyUnitFinishSecs = IdentifyUnitFinishSecs + differenceSecondsNow

                divValue = math.floor(differenceSecondsTen / 10)
                color = "badge bg-danger"
                if IdentifyUnitFinishSec >= divValue:
                    color = "badge bg-success"
                time_taken = strftime("%H:%M:%S", gmtime(divValue))

                pallet_timing_ten[res[0]][str(index - 1)] = {
                    "end_time": res[4],
                    "units_in_sec": IdentifyUnitFinishSecs,
                    "different_sec": differenceSecondsTen,
                    "color": color,
                    "time": time_taken,
                    "div1": differenceSecondsTen,
                    "div2": res_add,
                    "differenceSeconds": differenceSeconds,
                }
            else:
                differenceSecondsTen = DifferenceCalclulater(start_time_ten, res[4])
                differenceSecondsTen += res_add
                pallet_timing_ten[res[0]][str(index - 1)] = {
                    "end_time": res[4],
                    "units_in_sec": IdentifyUnitFinishSecs,
                    "different_sec": differenceSeconds,
                    "color": color,
                    "time": time_taken,
                    "div1": differenceSeconds,
                    "div2": res_add,
                    "differenceSeconds": differenceSeconds,
                }
            # print('start_time_ten=='+result[index][3])
            # print(start_time_ten)
            index = index + 1
        # print(pallet_timing_ten)
        finalJson = json.dumps(
            {
                "targetData": np.asarray(result).tolist(),
                "pallet_timing": pallet_timing,
                "pallet_timing_ten": pallet_timing_ten,
            }
        )
        return finalJson
    except Exception as a:
        # print(a)
        return jsonify(a)

@app.route("/getTarget/compare/getShipLines/<wh>/<cdate>", methods=["POST", "GET"])
def getShiplineCompare(wh, cdate):
    return getShipLines(wh, cdate)

@app.route("/getTarget/sheet/getShipLines/<wh>/<cdate>", methods=["POST", "GET"])
def getShipLines(wh, cdate):
    try:
        # print(wh)
        sql = (
            "SELECT DISTINCT IPMT_Label from Deepblu_Unit..PAMT INNER JOIN Deepblu..IPMT ON IPMT_ID = PAMT_RecvType AND PAMT_RecvType IS NOT NULL where PAMT_Warehouse='"
            + str(wh)
            + "' AND PAMT_AddDate ='"
            + str(cdate)
            + "' AND PAMT_RecvType != 'nydblinux0'"
        )
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        return json.dumps(np.asarray(result).tolist())
    except Exception as a:
        print(a)


@app.route("/getTarget/sheet/")
def index_get_target_sheet():
    try:
        sql = "select WHMT_ID from Deepblu..WHMT where WHMT_Active = 1"
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template("tartgetsheet.html", result=result)
    except Exception as a:
        print(a)
        return render_template("error.html")

@app.route("/getTarget/compare/<wh>")
def index_get_target_sheet_new(wh):
    try:
        sql = "select WHMT_ID from Deepblu..WHMT where WHMT_Active = 1"
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        return render_template("comparesheet.html", result=result,wh=wh)
    except Exception as a:
        print(a)
        return render_template("error.html")



def trun_lights(no, status, wh):
    # return 1
    if wh == 'charlotte':
        cmd = Config.API_SWITCH_TURN_LINE + no + "=" + status
        os.system(cmd)
    else:
        cmd = Config.API_SWITCH_TURN_LINE_BL + no + "=" + status
        os.system(cmd) 
    print(cmd)

def update_lights(no, status, printer):
    #return 1
    print(printer)
    if printer in Config.PRINTER_IP:
        
        ACT_IP = Config.PRINTER_IP[printer]
        
        if ACT_IP != None:
            cmd = ACT_IP + no + "=" + status
            print(cmd)
            os.system(cmd)
    
    
def trun_lights_bl(no, status):
    # return 1
    cmd = Config.API_SWITCH_TURN_LINE_BL + no + "=" + status
    os.system(cmd)


def trigger_data(cdate, units, wh, line):
    try:
        print("called")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if current_time > '12:10:00' and current_time < '04:00:00':
            return 1
        print(now.strftime("%Y-%m%d %H:%M:%S"))
        print("===========================")
        units = int(units) + 1
        sql = (
            " SELECT top "
            + str(units)
            + " PAMT_PalletID,COALESCE(PAMT_FG, PAMT_ItemID) as PAMT_ItemID,PAST_UnitNumber,min(PAST_AddTime) as MINAddTime, MAX(PAST_AddTime) as MAXAddTime,COALESCE(IMIT_UnitsPerHour, 200) as IMIT_UnitPerHr FROM Deepblu_unit..PAMT WITH (NOLOCK) LEFT JOIN Deepblu_unit..PAST WITH (NOLOCK) ON PAMT_ID = PAST_PalletKey LEFT JOIN Deepblu..IPMT WITH (NOLOCK) ON IPMT_ID = PAMT_RecvType LEFT JOIN Deepblu..imit ON COALESCE(PAMT_FG, PAMT_ItemID) = IMIT_ItemId  WHERE 1=1 AND Pamt_BuildID IS NOT NULL AND PAST_AddDate = '"
            + str(cdate)
            + "' AND PAMT_ID = (select top 1 PAMT_ID FROM Deepblu_unit..PAMT WITH (NOLOCK) LEFT JOIN Deepblu..IPMT WITH (NOLOCK) ON IPMT_ID = PAMT_RecvType LEFT JOIN Deepblu_Unit..PAST WITH (NOLOCK) ON PAST_PalletKey = PAMT_ID where PAMT_BuildID IS NOT NULL AND PAST_AddDate = '"
            + str(cdate)
            + "' AND PAMT_Warehouse = '"
            + str(wh)
            + "' AND IPMT_Label='"
            + str(line)
            + "' order by PAMT_ID desc) AND PAMT_Warehouse = '"
            + str(wh)
            + "' AND IPMT_Label='"
            + str(line)
            + "'  GROUP BY PAMT_PalletID,COALESCE(PAMT_FG, PAMT_ItemID),PAST_UnitNumber,IMIT_UnitsPerHour ORDER BY MAX(PAST_AddTime) DESC"
        )
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )

        #print(sql)
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql)
        result = cursor.fetchall()
        result = np.asarray(result).tolist()

        starttime = result[0][3]
        current_time = now.strftime("%H:%M:%S")
        differenceinseconds = DifferenceCalclulater(starttime, current_time)
        if len(result) < 2:
            return 1
        # perunitfinishinsec = calculetUnitPersSec(result[0][5])
        if differenceinseconds > 60:
            color = "red"
            trun_lights("2", "OFF", wh)
            trun_lights("1", "ON", wh)
            trun_lights("4", "OFF", wh)
            trun_lights("3", "ON", wh)
            trun_lights("6", "OFF", wh)
            trun_lights("5", "ON", wh)
            return color
        # print(len(result))
        if len(result) == 2:
            differenceSeconds = 0
            IdentifyUnitFinishSec = 0
            index = 1
            for res in result:
                endtime = res[3]
                starttime = result[index][3]
                unitperhr = res[5]
                differenceSeconds += DifferenceCalclulater(starttime, endtime)
                IdentifyUnitFinishSec += calculetUnitPersSec(unitperhr)
                index = index + 1
                if index == len(result):
                    break

            diffSec = differenceSeconds / len(result)
            diffUnit = IdentifyUnitFinishSec / len(result)

            if diffUnit >= diffSec:
                color = "green"
                trun_lights("1", "OFF", wh)
                trun_lights("2", "ON", wh)
            else:
                color = "red"
                trun_lights("2", "OFF", wh)
                trun_lights("1", "ON", wh)

            # print(color)
            # print(color,file=sys.stdout)
            return color
        else:
            startenddict = {}
            i = 0
            for res in result:
                if res[0] in startenddict.values():
                    startenddict["starttime"] = res[4]
                else:
                    i = 0
                    startenddict["pallet"] = res[0]
                    startenddict["endtime"] = res[3]
                i = i + 1
            lastPalletLength = i
            differenceSeconds = DifferenceCalclulater(
                startenddict["starttime"], startenddict["endtime"]
            )
            IdentifyUnitFinishSec = (calculetUnitPersSec(res[5])) * (lastPalletLength)

            if IdentifyUnitFinishSec >= differenceSeconds:
                color = "green"
                if len(result) <= 11:
                    trun_lights("3", "OFF", wh)
                    trun_lights("4", "ON", wh)
                else:
                    trun_lights("5", "OFF", wh)
                    trun_lights("6", "ON", wh)

            else:
                color = "red"
                if len(result) <= 11:
                    trun_lights("4", "OFF", wh)
                    trun_lights("3", "ON", wh)
                else:
                    trun_lights("6", "OFF", wh)
                    trun_lights("5", "ON", wh)
            # print(color)
            return color
        # finalJson = json.dumps({'targetData':np.asarray(result).tolist()})
        # return finalJson
    except Exception as a:
        print(a)
        return jsonify(a)
    
def trigger_data_new(ip):
    try:        
        d1 = datetime.today()
        d1 = d1.strftime("%Y-%m-%d")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if current_time > '12:10:00' and current_time < '04:00:00':
            return 1
        # d1= '2025-02-03'
        sql1 = "select PAMT_ID from (  SELECT PAMT_ID,PAMT_PalletID,COALESCE(PAMT_FG, PAMT_ItemID) as PAMT_ItemID,PAST_UnitNumber,min(PAST_AddTime) as MINAddTime, MAX(PAST_AddTime) as MAXAddTime,COALESCE(IMIT_UnitsPerHour, 200) as IMIT_UnitPerHr, PAMT_Warehouse,IPMT_Label,IPMT_Desc, row_number() over (partition by IPMT_Label order by MAX(PAST_AddTime) desc) as rn  FROM Deepblu_unit..PAMT WITH (NOLOCK) LEFT JOIN Deepblu_unit..PAST WITH (NOLOCK) ON PAMT_ID = PAST_PalletKey LEFT JOIN Deepblu..IPMT WITH (NOLOCK) ON IPMT_ID = PAMT_RecvType LEFT JOIN Deepblu..imit WITH (NOLOCK) ON COALESCE(PAMT_FG, PAMT_ItemID) = IMIT_ItemId WHERE 1=1 AND IPMT_Label= '"+str(ip)+"' AND IPMT_Desc in ('Line1','Line2','Line3','Line4') AND Pamt_BuildID IS NOT NULL AND PAST_AddDate = '"+str(d1)+"' AND PAMT_Warehouse IN ('Bloomington','Charlotte')  GROUP BY PAMT_ID,PAMT_PalletID,COALESCE(PAMT_FG, PAMT_ItemID),PAST_UnitNumber,IMIT_UnitsPerHour,PAMT_Warehouse,IPMT_Label ,IPMT_Desc   ) with_rn  where rn = 1  "
        
        conn = pyodbc.connect(
            driver="{ODBC Driver 17 for SQL Server}",
            host=conf.DATABASE_UNIT_CONFIG["server"],
            database=conf.DATABASE_UNIT_CONFIG["name"],
            user=conf.DATABASE_UNIT_CONFIG["user"],
            password=conf.DATABASE_UNIT_CONFIG["password"],
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.execute(sql1)
        result = cursor.fetchall()
        pallet_ids = str('1')
        for  value in result:  
            pallet_ids = pallet_ids+','+str(value[0])
        
        sql = ("SELECT PAMT_PalletID,COALESCE(PAMT_FG, PAMT_ItemID) as PAMT_ItemID,PAST_UnitNumber,min(PAST_AddTime) as MINAddTime, MAX(PAST_AddTime) as MAXAddTime,COALESCE(IMIT_UnitsPerHour, 200) as IMIT_UnitPerHr, PAMT_Warehouse,IPMT_Label FROM Deepblu_unit..PAMT WITH (NOLOCK) LEFT JOIN Deepblu_unit..PAST WITH (NOLOCK) ON PAMT_ID = PAST_PalletKey LEFT JOIN Deepblu..IPMT WITH (NOLOCK) ON IPMT_ID = PAMT_RecvType LEFT JOIN Deepblu..imit WITH (NOLOCK) ON COALESCE(PAMT_FG, PAMT_ItemID) = IMIT_ItemId WHERE 1=1 AND Pamt_BuildID IS NOT NULL AND PAST_AddDate = '"+str(d1)+"' AND PAMT_ID IN ("+pallet_ids+") GROUP BY PAMT_PalletID,COALESCE(PAMT_FG, PAMT_ItemID),PAST_UnitNumber,IMIT_UnitsPerHour,PAMT_Warehouse,IPMT_Label  ORDER BY PAMT_Warehouse,IPMT_Label,MAX(PAST_AddTime) DESC")
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        result = np.asarray(result).tolist()
        grouped_data = {}
        for key, group in groupby(sorted(result, key=lambda x: (x[-2], x[-1])), key=lambda x: (x[-2], x[-1])):
            grouped_data[key] = list(group)
        grouped_list = [(key, value) for key, value in grouped_data.items()]
        for key, value in grouped_list:            
            # if(len(value) < 1000):
            #     dataprocess(key[0],key[1], value[len(value)-1],value[len(value)-2],value[len(value)-10], None, len(value))
            # else:
            #print(key)
            #print(value) 
            #print(value[0])
            if(len(value) > 2):
                dataprocess(key[0], key[1], value[len(value)-(len(value)-1)], value[len(value)-(len(value)-2)], '', '', '',0)
                
            if(len(value) > 11):
                dataprocess(key[0], key[1], value[len(value)-(len(value)-1)], '', value[len(value)-(len(value)-10)], '', len(value),1)
                dataprocess(key[0], key[1], value[0], '', '', value[len(value)-1], len(value),1)
            if (len(value) > 2 and len(value) <11 ):
                    dataprocess(key[0], key[1], value[0], '', value[len(value)-1], '', len(value), 1)
                    dataprocess(key[0], key[1], value[0], '', '', value[len(value)-1], len(value), 1)
        return jsonify(grouped_list)   
    
    except Exception as a:
        print(a)
        return jsonify(a)
    
def dataprocess(wh, line, firstRow, SecondRow, TenthRow, ThousandRow, pallsetSize, dontcall=0):
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        if SecondRow !='':
            print('First')
            print(SecondRow)
            print(firstRow)
            differenceinseconds = DifferenceCalclulater(firstRow[3], current_time)
            if differenceinseconds > 500:
                    update_lights("2", "OFF", line)
                    update_lights("1", "ON", line)
                    update_lights("4", "OFF", line)
                    update_lights("3", "ON", line)
                    update_lights("6", "OFF", line)
                    update_lights("5", "ON", line)
                    return 'fail'
            differenceSeconds = DifferenceCalclulater(
                 SecondRow[4],firstRow[3]
            )
            
            IdentifyUnitFinishSec = (calculetUnitPersSec(SecondRow[5]))
            print(str(IdentifyUnitFinishSec)+'>3='+str(differenceSeconds))
            if IdentifyUnitFinishSec >= differenceSeconds:
                color = "green"
                print(color)
                update_lights("1", "OFF", line)
                update_lights("2", "ON", line)
            else:
                color = "red"
                print(color)
                update_lights("2", "OFF", line)
                update_lights("1", "ON", line)

        if TenthRow != '':
            print('Second')
            print(TenthRow)
            print(firstRow)
            differenceinseconds = DifferenceCalclulater(firstRow[3], current_time)
            if differenceinseconds > 500:
                    update_lights("2", "OFF", line)
                    update_lights("1", "ON", line)
                    update_lights("4", "OFF", line)
                    update_lights("3", "ON", line)
                    update_lights("6", "OFF", line)
                    update_lights("5", "ON", line)
                    return 'fail'
            differenceinseconds = DifferenceCalclulater(TenthRow[4], current_time)
            
            differenceSeconds = DifferenceCalclulater(
                TenthRow[4], firstRow[3] 
            )
            
            IdentifyUnitFinishSec = (calculetUnitPersSec(TenthRow[5])) * 10
            print(str(IdentifyUnitFinishSec)+'>3='+str(differenceSeconds))
            if IdentifyUnitFinishSec >= differenceSeconds:
                color = "green"
                print(color)
                update_lights("3", "OFF", line)
                update_lights("4", "ON", line)
            else:                
                color = "red"
                print(color)              
                update_lights("4", "OFF", line)
                update_lights("3", "ON", line)                

        if ThousandRow != '':
            print('Third')
            print(ThousandRow)
            print(firstRow)
            differenceinseconds = DifferenceCalclulater(firstRow[3], current_time)
            if differenceinseconds > 500:
                    update_lights("2", "OFF", line)
                    update_lights("1", "ON", line)
                    update_lights("4", "OFF", line)
                    update_lights("3", "ON", line)
                    update_lights("6", "OFF", line)
                    update_lights("5", "ON", line)
                    return 'fail'
            differenceinseconds = DifferenceCalclulater(ThousandRow[4], current_time)
            
            
            differenceSeconds = DifferenceCalclulater(
                ThousandRow[4], firstRow[3]
            )
            
            IdentifyUnitFinishSec = (calculetUnitPersSec(ThousandRow[5])) * (pallsetSize)
            print(str(IdentifyUnitFinishSec)+'>3='+str(differenceSeconds))
            if IdentifyUnitFinishSec >= differenceSeconds:
                color = "green"
                print(color)
                update_lights("5", "OFF", line)
                update_lights("6", "ON", line)
            else:
                color = "red" 
                print(color)             
                update_lights("6", "OFF", line)
                update_lights("5", "ON", line) 
        return 'done'
    except Exception as a:
        print(a)
        return jsonify(a)    


@app.route("/recent/record", methods=["POST", "GET"])
def get_recent_record_new():
    return trigger_data_new()


@app.route("/recent/record/<cdate>/<units>/<wh>/<line>", methods=["POST", "GET"])
def get_recent_record(cdate, units, wh, line):
    return trigger_data(cdate, units, wh, line)


def calculetUnitPersSec(unitperHr):
    unitpermin = int(unitperHr) / 60
    unitpersec = 60 / unitpermin
    return unitpersec


def DifferenceCalclulater(startTime, endTime):
    # try:
    start = startTime.split(":", 3)
    end = endTime.split(":", 3)
    startseconds = (
        ((int(start[0])) * 60 * 60) + ((int(start[1])) * 60) + (int(start[2]))
    )
    endseconds = ((int(end[0])) * 60 * 60) + ((int(end[1])) * 60) + (int(end[2]))
    # print(startseconds)
    # print(endseconds)
    differenceinSeconds = (int(endseconds)) - (int(startseconds))
    return differenceinSeconds
    # except Exception as a:
    #     print(a)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8989, debug=True)
