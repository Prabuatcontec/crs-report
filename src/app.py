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
 
@app.route("/crs/q4")
def index_crs_q4wh():
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
        qrWarehose = ""
        if warehouse is not None:
            qrWarehose = " AND SiteName='"+warehouse+"'"
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
        where   StationId LIKE '%CLD-FTR%' AND StationType = 'AWAP'   AND date(p.Processed) BETWEEN '"+dateFrom+" 00:00:00' and '"+dateTo+" 23:59:59' "+qrWarehose+"\
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
                    defect[str(res[0])][str(res[1])]["total"]  = 0
                
                if str(res[1]) not in defect[res[0]][str(res[1])]["defect"]:
                    defect[str(res[0])][str(res[1])]["defect"][str(res[2])] = res[3]
            if str(res[2]) == "Total": 
                defect[str(res[0])][str(res[1])]["total"] = res[3]
        dbserials.append(defect)
        return dbserials
         
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8990, debug=True)
