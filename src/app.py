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

@app.route("/fedex/token", methods=["POST"])
def fedex_token():
    flat_dict = request.form.to_dict(flat=True) 
    
    post_url = 'https://apis-sandbox.fedex.com/oauth/token'
    payload = flat_dict
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(post_url, data=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    return response.json() 


@app.route("/fedex/rates", methods=["POST"])
def fedex_rates():
    flat_dict = request.json 
    authorization = request.headers.get('Authorization')
    
    post_url = 'https://apis-sandbox.fedex.com/fedex/rates'
    payload = flat_dict
    headers = {'Content-Type': 'application/json',
               'Authorization': authorization} 
    response = requests.post(post_url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    return response.json() 

@app.route("/fedex/shipments", methods=["POST"])
def fedex_shipments():
    flat_dict = request.json 
    authorization = request.headers.get('Authorization')
    
    post_url = 'https://apis-sandbox.fedex.com/ship/v1/shipments'
    payload = flat_dict
    headers = {'Content-Type': 'application/json',
               'X-locale': "en_US",
               'Authorization': authorization} 
    print(payload)
    payload["labelSpecification"] = {
            "labelFormatType": "COMMON2D",
            "labelOrder": "SHIPPING_LABEL_FIRST",
            "printedLabelOrigin": {},
            "labelStockType": "PAPER_7X475",
            "labelRotation": "UPSIDE_DOWN",
            "imageType": "PDF",
            "customerSpecifiedDetail": {
                "maskedData": [],
                "regulatoryLabels": [
                    {
                        "generationOptions": "CONTENT_ON_SHIPPING_LABEL_ONLY",
                        "type": "ALCOHOL_SHIPMENT_LABEL"
                    }
                ],
                "additionalLabels": [],
                "docTabContent": {}
            },
            "resolution": 300
        }
    print(headers)
    response = requests.post(post_url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    return response.json() 

@app.route("/crs/q4")
def index_crs_q4wh():
        from werkzeug.datastructures import ImmutableMultiDict
        dateFrom = None
        dateTo = None
        warehouse = None
        customer = None 
        flat_dict = request.args.to_dict(flat=True) 
        
        if 'dateFrom' in flat_dict:
            dateFrom = flat_dict['dateFrom']
        if 'dateTo' in flat_dict:
            dateTo = flat_dict['dateTo']

        if 'warehouse' in flat_dict:
            warehouse = flat_dict['warehouse']
        if 'customer' in flat_dict:
            customer = flat_dict['customer']
        qrWarehose = ""
        stationId = ""
        if warehouse is not None:
            qrWarehose = " AND SiteName='"+warehouse+"'"
            if warehouse == "Charlotte":
                stationId = "CLD"
            if warehouse == "Brownsvelli":
                stationId = "BRD"
            if warehouse == "San Jose":
                stationId = "SJD"
        qrCustomer = ""
        if customer is not None:
            qrCustomer = " AND SiteName='"+customer+"'"
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
       
        if dateFrom is None:
            dateFrom = now.strftime("%Y-%m-%d")
        if dateTo is None:
            dateTo = now.strftime("%Y-%m-%d")
        sql = "Select * from ( \
        select SiteName, date(DefectDate) as Date, QD.QualityDefect as Defect, count(1)  from QualityDefects  Q \
        inner join RepairStatus r on Q.SN = r.SN and CRSModelName like 'CRSF%' \
        inner join QualityDefectList QD on QD.DefectID = Q.QualityDefectID and CRSModelName like 'CRSF%' \
        inner join WorkSites W on W.SiteID = r.SiteID   \
        where date(DefectDate) BETWEEN '"+dateFrom+" 00:00:00' and '"+dateTo+" 23:59:59' "+qrWarehose+"  \
        GROUP BY W.SiteID,date(DefectDate) , QD.QualityDefect \
        UNION ALL  \
        select  SiteName, date(p.Processed) as Date ,'Total' as Defect, count(*) count from ProductionHub_QI  p \
        inner join RepairStatus r on p.SN = r.SN and CRSModelName like 'CRSF%' \
        inner join WorkSites W on W.SiteID = r.SiteID  \
        where date(p.Processed) BETWEEN '"+dateFrom+" 00:00:00' and '"+dateTo+" 23:59:59' "+qrWarehose+"    \
        GROUP BY W.SiteID, date(p.Processed) \
        UNION ALL \
        select  \
        CASE \
        WHEN StationId LIKE 'CLD%' THEN 'Charlotte' \
        WHEN StationId LIKE 'BRD%' THEN 'Brownsvelli' \
        WHEN StationId LIKE 'SJD%' THEN 'San Jose' \
        ELSE 'Charlotte' \
        END AS SiteName , date(p.Processed) as Date ,'AWAP' as Defect, count(*) count from ProductionHub  p \
        where   StationId LIKE '%"+stationId+"-FTR%' AND StationType = 'AWAP'   AND date(p.Processed) BETWEEN '"+dateFrom+" 00:00:00' and '"+dateTo+" 23:59:59' " "\
        GROUP BY   date(p.Processed) ) as s Order by SiteName, Date , Defect";
        conn = mysql.connect()  
        cursor = conn.cursor()
        cursor.execute(sql)
        data_added = cursor.fetchall()
        dbserials = [] 
        
        defect = {}
        for res in data_added: 
            if res[0] not in defect:
                defect[res[0]] = {}
            if str(res[1]) not in defect[str(res[0])]:
                 defect[res[0]][str(res[1])] = {}
            if str(res[2]) != "Total": 
                if "defect" not in defect[str(res[0])][str(res[1])]: 
                    defect[str(res[0])][str(res[1])]["defect"]  = {}
                
                if str(res[1]) not in defect[res[0]][str(res[1])]["defect"]:
                    defect[str(res[0])][str(res[1])]["defect"][str(res[2])] = res[3]
            if str(res[2]) == "Total": 
                defect[str(res[0])][str(res[1])]["total"] = res[3]
            if "total" not in defect[str(res[0])][str(res[1])]:
                defect[str(res[0])][str(res[1])]["total"]  = 0
        dbserials.append(defect)
        return dbserials

@app.route("/crs/testing")
def index_crs_testing_q4wh():
        from werkzeug.datastructures import ImmutableMultiDict
        dateFrom = None
        dateTo = None
        warehouse = None
        customer = None 
        flat_dict = request.args.to_dict(flat=True) 
        print(flat_dict)
        if 'dateFrom' in flat_dict:
            dateFrom = flat_dict['dateFrom']
        if 'dateTo' in flat_dict:
            dateTo = flat_dict['dateTo']

        if 'warehouse' in flat_dict:
            warehouse = flat_dict['warehouse']
        if 'customer' in flat_dict:
            customer = flat_dict['customer']
        qrOperator = ""
        if 'operator' in flat_dict:
            operator = flat_dict['operator']
            qrOperator = " AND Operator='"+operator+"'"
        qrWarehose = ""
        if warehouse is not None:
            qrWarehose = " AND SiteName='"+warehouse+"'"
            
        qrCustomer = ""
        if customer is not None:
            qrCustomer = " AND Customers.BillName='"+customer+"'"
        now = datetime.now() 
       
        if dateFrom is None:
            dateFrom = now.strftime("%Y-%m-%d")
        if dateTo is None:
            dateTo = now.strftime("%Y-%m-%d")
        sql = "Select \
  SiteName as warehouse, Operator as operator, \
  Station, \
  Customers.BillName Customer, \
  Model , DATE(TestDate), HOUR(TestDate) ,  \
  TestResult Result, \
  FailureMsg Failure, \
  count(1) count \
from \
  TestResults \
  JOIN Customers ON Customers.CustomerID = TestResults.CustomerID \
  inner join WorkSites W on W.SiteID = TestResults.SiteID   \
where \
  TestDate   BETWEEN '"+dateFrom+" 00:00:00' and '"+dateTo+" 23:59:59' "+qrWarehose+" "+qrCustomer+" "+qrOperator+"  \
GROUP BY \
SiteName, \
  Operator, \
  Station, \
  Customers.BillName, \
  Model, DATE(TestDate), HOUR(TestDate) , \
  TestResult, \
  FailureMsg";
         
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        data_added = cursor.fetchall()
        dbserials = [] 
        
        
        for res in data_added: 
            defect = {}
            defect['warehouse'] = res[0]
            defect['operator'] = res[1]
            defect['station'] = res[2]
            defect['customer'] = res[3]
            defect['model'] = res[4]
            defect['date'] = res[5]
            defect['hour'] = res[6]
            defect['result'] = res[7]
            defect['failure'] = res[8]
            defect['count'] = res[9]
            dbserials.append(defect)
        return dbserials



@app.route("/crs/check_status/certificate")
def index_crs_testing_q4_certificate_wh():
        from werkzeug.datastructures import ImmutableMultiDict
        dateFrom = None
        dateTo = None
        warehouse = None
        customer = None 
        flat_dict = request.args.to_dict(flat=True) 
        Sn = None
        if 'sn' in flat_dict:
            Sn = flat_dict['sn']
        sql = " Select count(1) from CRS_Prod.TestResults where  Details Like '%XFN_NVG_CERT_SET_GET%' AND Sn ='"+Sn+"'";
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        data_added = cursor.fetchall()
        dbserials = [] 
        print(data_added);
        for res in data_added: 
            return {"result": res[0]}
        return {"result": 0}


@app.route("/crs/update_status/certificate", methods=["POST"])
def index_crs_testing_update_certificate_wh():
        data = request.json
        now = datetime.now()
        if 'sn' in data:
            sn = data['sn']
            dateFrom = now.strftime("%Y-%m-%d %H:%M:%S")
            sql = "CALL sp_insert_missing_certificate_NVG("\
            "'"+dateFrom+"',741,'P', 'XFN_NVG_CERT_SET_GET','2','"+str(sn)+"');"; 
        
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        try:
            res = cursor.callproc('sp_insert_missing_certificate_NVG', (str(dateFrom),741, 'P', 'XFN_NVG_CERT_SET_GET', '2', str(sn)))
            print("============")
            print(res)
            print("============")
            #cursor.execute(sql) 
            return {"result": sn}
        except:
              return {"result": "Unable to Save"}


         
 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8990, debug=True)
