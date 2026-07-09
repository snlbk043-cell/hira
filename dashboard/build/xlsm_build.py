#!/usr/bin/env python3
"""
RCPL Executive EHS KPI Dashboard  ->  fully-functional macro-enabled workbook (.xlsm)

Generates:
  * 20 raw-data registers (structured Excel Tables) with realistic sample data
  * A live KPI calculation engine (COUNTIFS/SUMIFS, 100k-row dynamic ranges)
  * 9 interactive dashboards + Home navigation, 20+ native charts, gauges,
    conditional formatting, sparklines, data-validation filters
  * Real embedded, working VBA (Refresh / Reset / Navigate / Print / Export PDF)
"""
import os
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

import data_gen
import vba_code
import vbabin

DATA = data_gen.build_all()
MONTHS = data_gen.MONTHS
ROWS = 100001          # dynamic range depth -> supports 100,000 records

# ------------------------------------------------------------------ palette
BLUE_D   = "#0F4C81"   # primary
BLUE_M   = "#0B6EA8"
BLUE_L   = "#E8F3FB"
GREY_D   = "#334155"
GREY_M   = "#64748B"
GREY_L   = "#F1F5F9"
GREEN    = "#16A34A"
GREEN_L  = "#DCFCE7"
AMBER    = "#F59E0B"
RED      = "#DC2626"
RED_L    = "#FEE2E2"
WHITE    = "#FFFFFF"
INK      = "#1F2937"
ACCENT   = "#D71920"   # Campa red

# ------------------------------------------------------------------ registers
# key -> (sheet_name, table_name, headers, data_key, date_cols_idx)
REG = {
    "incident": ("Incident Register", "tIncident",
        ["Incident ID","Date","Year","Month","Month Name","Department","Area","Shift",
         "Incident Type","Severity","Severity Score","Root Cause","Contractor",
         "Employee Category","Lost Days","Status","Date Closed"], "incidents", [1,16]),
    "firstaid": ("First Aid Register", "tFirstAid",
        ["FA ID","Date","Year","Month","Month Name","Department","Area","Shift",
         "Body Part","Root Cause","Employee Category","Status"], "firstaid", [1]),
    "nearmiss": ("Near Miss Register", "tNearMiss",
        ["NM ID","Date","Year","Month","Month Name","Department","Area","Shift",
         "Description","Potential","Root Cause","Employee Category","Status"], "nearmiss", [1]),
    "safetyobs": ("Safety Observation Register", "tSafetyObs",
        ["SO ID","Date","Year","Month","Month Name","Department","Area","Shift",
         "Category","Description","Severity","Employee Category","Status"], "safety_obs", [1]),
    "unsafeact": ("Unsafe Act Register", "tUnsafeAct",
        ["UA ID","Date","Year","Month","Month Name","Department","Area",
         "Unsafe Act","Severity","Shift","Status"], "unsafe_act", [1]),
    "unsafecond": ("Unsafe Condition Register", "tUnsafeCond",
        ["UC ID","Date","Year","Month","Month Name","Department","Area",
         "Unsafe Condition","Severity","Shift","Status"], "unsafe_cond", [1]),
    "inspection": ("Inspection Register", "tInspection",
        ["INS ID","Date","Year","Month","Month Name","Department","Area",
         "Inspection Type","Planned","Completed","Findings","Closed Findings","Status"], "inspection", [1]),
    "audit": ("Audit Register", "tAudit",
        ["Audit ID","Date","Year","Month","Month Name","Department","Audit Type",
         "Score","NCRs","NCRs Closed","Status"], "audit", [1]),
    "statutory": ("Statutory Compliance Register", "tStatutory",
        ["Ref","Compliance Item","Department","Validity","Due Date","Compliance","Category"],
        "statutory", [4]),
    "ptw": ("Permit To Work Register", "tPTW",
        ["Permit ID","Date","Year","Month","Month Name","Department","Area",
         "Permit Type","Contractor","Shift","Compliance","Status"], "ptw", [1]),
    "training": ("Training Register", "tTraining",
        ["Training ID","Date","Year","Month","Month Name","Department","Topic",
         "Planned","Completed","Completion %"], "training", [1]),
    "ppe": ("PPE Compliance Register", "tPPE",
        ["PPE ID","Date","Year","Month","Month Name","Department","Area",
         "Checked","Compliant","Compliance %"], "ppe", [1]),
    "contractor": ("Contractor Safety Register", "tContractor",
        ["Ref","Contractor","Year","Workers","Trained","Trained %","Incidents","Safety Score"],
        "contractor", []),
    "toolbox": ("Toolbox Talk Register", "tToolbox",
        ["TBT ID","Date","Year","Month","Month Name","Department","Topic","Attendance","Shift"],
        "toolbox", [1]),
    "bbs": ("BBS Observation Register", "tBBS",
        ["BBS ID","Date","Year","Month","Month Name","Department","Area","Behaviour",
         "Observed Act","Employee Category"], "bbs", [1]),
    "drill": ("Emergency Drill Register", "tDrill",
        ["Drill ID","Date","Year","Month","Month Name","Drill Type",
         "Response Time (min)","Rating","Participants"], "drill", [1]),
    "fireeq": ("Fire Equipment Inspection", "tFireEq",
        ["FE ID","Date","Year","Month","Month Name","Equipment","Area","Condition","Status"],
        "fire_equip", [1]),
    "risk": ("Risk Assessment Register", "tRisk",
        ["RA ID","Date","Year","Month","Month Name","Department","Area","Hazard",
         "Likelihood","Severity","Risk Score","Risk Level","Status"], "risk", [1]),
    "capa": ("CAPA Tracker", "tCAPA",
        ["CAPA ID","Date","Year","Month","Month Name","Source","Department","Root Cause",
         "Action Type","Severity","Due Date","Status","Owner"], "capa", [1,10]),
    "manhours": ("Man-hours Master", "tManhours",
        ["Year","Month","Month Name","Department","Man-hours"], "manhours", []),
}


def col_of(key, field):
    """Return the A1 column letter for a field in a register."""
    headers = REG[key][2]
    return xl_col_to_name(headers.index(field))


def rng(key, field):
    """Return an absolute 100k-row range for a register field (excludes header)."""
    sheet = REG[key][0]
    c = col_of(key, field)
    return "'%s'!$%s$2:$%s$%d" % (sheet, c, c, ROWS)


# ==========================================================================
class Builder:
    def __init__(self, path):
        self.wb = xlsxwriter.Workbook(path, {"nan_inf_to_errors": True})
        self.wb.set_calc_mode("auto")
        self.path = path
        self._make_formats()

    # ---------------------------------------------------------------- formats
    def _make_formats(self):
        wb = self.wb
        F = {}
        F["title"] = wb.add_format({"font_name":"Segoe UI","font_size":26,"bold":True,
            "font_color":WHITE,"bg_color":BLUE_D,"align":"left","valign":"vcenter"})
        F["subtitle"] = wb.add_format({"font_name":"Segoe UI","font_size":11,
            "font_color":"#DCEBF7","bg_color":BLUE_D,"align":"left","valign":"vcenter"})
        F["hdrband"] = wb.add_format({"bg_color":BLUE_D})
        F["accentband"] = wb.add_format({"bg_color":ACCENT})
        F["section"] = wb.add_format({"font_name":"Segoe UI","font_size":13,"bold":True,
            "font_color":BLUE_D,"align":"left","valign":"vcenter","bottom":2,"border_color":BLUE_M})
        F["card_title"] = wb.add_format({"font_name":"Segoe UI","font_size":9,"bold":True,
            "font_color":GREY_M,"bg_color":WHITE,"align":"left","valign":"vcenter"})
        F["card_big"] = wb.add_format({"font_name":"Segoe UI","font_size":22,"bold":True,
            "font_color":BLUE_D,"bg_color":WHITE,"align":"left","valign":"vcenter"})
        F["card_big_pct"] = wb.add_format({"font_name":"Segoe UI","font_size":22,"bold":True,
            "font_color":BLUE_D,"bg_color":WHITE,"align":"left","valign":"vcenter","num_format":'0.0"%"'})
        F["card_big_num"] = wb.add_format({"font_name":"Segoe UI","font_size":22,"bold":True,
            "font_color":BLUE_D,"bg_color":WHITE,"align":"left","valign":"vcenter","num_format":"#,##0"})
        F["card_big_dec"] = wb.add_format({"font_name":"Segoe UI","font_size":22,"bold":True,
            "font_color":BLUE_D,"bg_color":WHITE,"align":"left","valign":"vcenter","num_format":"0.00"})
        F["card_unit"] = wb.add_format({"font_name":"Segoe UI","font_size":9,
            "font_color":GREY_M,"bg_color":WHITE,"align":"left","valign":"top"})
        F["card_left"] = wb.add_format({"bg_color":WHITE,"left":5,"border_color":BLUE_M})
        F["card_left_g"] = wb.add_format({"bg_color":WHITE,"left":5,"border_color":GREEN})
        F["card_left_r"] = wb.add_format({"bg_color":WHITE,"left":5,"border_color":RED})
        F["card_left_a"] = wb.add_format({"bg_color":WHITE,"left":5,"border_color":AMBER})
        F["card_bg"] = wb.add_format({"bg_color":WHITE})
        F["filter_lbl"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"bold":True,
            "font_color":WHITE,"bg_color":BLUE_M,"align":"center","valign":"vcenter","border":1,"border_color":WHITE})
        F["filter_val"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"bold":True,
            "font_color":BLUE_D,"bg_color":GREY_L,"align":"center","valign":"vcenter","border":1,"border_color":"#CBD5E1"})
        F["th"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"bold":True,
            "font_color":WHITE,"bg_color":BLUE_M,"align":"center","valign":"vcenter","border":1,"border_color":WHITE,"text_wrap":True})
        F["td"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"align":"center",
            "valign":"vcenter","border":1,"border_color":"#D8E1EB"})
        F["td_l"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"align":"left",
            "valign":"vcenter","border":1,"border_color":"#D8E1EB"})
        F["td_pct"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"align":"center",
            "valign":"vcenter","border":1,"border_color":"#D8E1EB","num_format":'0.0"%"'})
        F["td_num"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"align":"center",
            "valign":"vcenter","border":1,"border_color":"#D8E1EB","num_format":"#,##0"})
        F["calc_lbl"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"bold":True,
            "font_color":INK,"align":"left","valign":"vcenter"})
        F["calc_val"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"align":"right",
            "valign":"vcenter","bg_color":GREY_L,"border":1,"border_color":"#D8E1EB","num_format":"0.00"})
        F["note"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"font_color":GREY_M,"text_wrap":True,"valign":"top"})
        F["h1"] = wb.add_format({"font_name":"Segoe UI","font_size":18,"bold":True,"font_color":BLUE_D})
        F["h2"] = wb.add_format({"font_name":"Segoe UI","font_size":13,"bold":True,"font_color":BLUE_M})
        F["body"] = wb.add_format({"font_name":"Segoe UI","font_size":11,"font_color":INK,"text_wrap":True,"valign":"top"})
        F["bodyb"] = wb.add_format({"font_name":"Segoe UI","font_size":11,"bold":True,"font_color":INK,"valign":"top"})
        F["date"] = wb.add_format({"num_format":"dd-mmm-yy"})
        F["heat"] = wb.add_format({"font_name":"Segoe UI","font_size":11,"bold":True,
            "align":"center","valign":"vcenter","border":1,"border_color":WHITE,"num_format":"0"})
        F["heat_axis"] = wb.add_format({"font_name":"Segoe UI","font_size":9,"bold":True,
            "font_color":WHITE,"bg_color":GREY_D,"align":"center","valign":"vcenter","border":1,"border_color":WHITE})
        F["navbtn"] = wb.add_format({"font_name":"Segoe UI","font_size":12,"bold":True,
            "font_color":WHITE,"bg_color":BLUE_M,"align":"center","valign":"vcenter","border":1,"border_color":WHITE})
        F["homehdr"] = wb.add_format({"font_name":"Segoe UI","font_size":34,"bold":True,
            "font_color":WHITE,"bg_color":BLUE_D,"align":"center","valign":"vcenter"})
        F["homesub"] = wb.add_format({"font_name":"Segoe UI","font_size":13,
            "font_color":"#DCEBF7","bg_color":BLUE_D,"align":"center","valign":"vcenter"})
        F["refresh_lbl"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"italic":True,
            "font_color":GREY_M,"align":"right","valign":"vcenter"})
        F["refresh_val"] = wb.add_format({"font_name":"Segoe UI","font_size":10,"bold":True,
            "font_color":BLUE_D,"align":"left","valign":"vcenter","num_format":"dd-mmm-yyyy hh:mm"})
        self.F = F

    # ---------------------------------------------------------------- registers
    def write_registers(self):
        for key, (sheet, tname, headers, dkey, datecols) in REG.items():
            ws = self.wb.add_worksheet(sheet)
            ws.set_tab_color(GREY_M)
            rows = DATA[dkey]
            ncols = len(headers)
            # write data first (table will re-apply headers)
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    if c in datecols and val not in ("", None):
                        ws.write_datetime(r + 1, c, _to_dt(val), self.F["date"])
                    else:
                        ws.write(r + 1, c, val)
            last = max(len(rows), 1)
            ws.add_table(0, 0, last, ncols - 1, {
                "name": tname, "style": "Table Style Medium 2",
                "columns": [{"header": h} for h in headers]})
            widths = [14 if i == 0 else 11 for i in range(ncols)]
            for i, h in enumerate(headers):
                ws.set_column(i, i, max(widths[i], min(24, len(h) + 3)))
            ws.freeze_panes(1, 0)
            ws.set_zoom(90)
            # back-home hyperlink
            ws.write_url(0, ncols + 1, "internal:'Home'!A1", self.F["card_title"], "Home")

    # ---------------------------------------------------------------- master data
    def write_master(self):
        F = self.F
        ws = self.wb.add_worksheet("Master Data")
        ws.set_tab_color(BLUE_M)
        ws.set_column("A:A", 2)
        ws.merge_range("B2:H2", "MASTER DATA  •  Lookup Lists & Reference Tables", F["section"])
        lists = {
            "Departments": data_gen.DEPARTMENTS, "Areas": data_gen.AREAS,
            "Shifts": data_gen.SHIFTS, "Contractors": data_gen.CONTRACTORS,
            "Employee Category": data_gen.EMP_CATEGORY, "Severity": data_gen.SEVERITY,
            "Incident Type": data_gen.INCIDENT_TYPES, "Root Cause": data_gen.ROOT_CAUSES,
            "Permit Type": data_gen.PERMIT_TYPES, "Unsafe Act": data_gen.UNSAFE_ACTS,
            "Unsafe Condition": data_gen.UNSAFE_CONDITIONS, "Years": [2024, 2025, 2026],
            "Months": MONTHS,
        }
        col = 1
        for name, vals in lists.items():
            ws.write(3, col, name, F["th"])
            for i, v in enumerate(vals):
                ws.write(4 + i, col, v, F["td_l"])
            ws.set_column(col, col, 20)
            col += 1
        ws.write_url(0, 1, "internal:'Home'!A1", F["card_title"], "Home")
        self.master_ws = ws

    # ---------------------------------------------------------------- calc engine
    def write_calculations(self):
        F = self.F
        ws = self.wb.add_worksheet("Calculations")
        ws.set_tab_color(GREEN)
        ws.hide_gridlines(2)
        ws.set_column("A:A", 2)
        ws.set_column("B:B", 26)
        ws.set_column("C:C", 14)
        ws.set_column("D:R", 12)
        self.calc = ws
        R = {}   # range registry for charts

        ws.merge_range("B2:H2", "KPI CALCULATION ENGINE  (auto-recalculates from raw registers)", F["section"])

        # ---- resolved filter criteria (reference filter cells on Exec dashboard)
        crit = {
            "yCrit":  'IF(SelYear="All","<>",SelYear)',
            "mCrit":  'IF(SelMonth="All","<>",SelMonth)',
            "dCrit":  'IF(SelDept="All","<>",SelDept)',
            "aCrit":  'IF(SelArea="All","<>",SelArea)',
            "sCrit":  'IF(SelShift="All","<>",SelShift)',
            "DashYear": 'IF(SelYear="All",MAX(%s),SelYear)' % rng("manhours", "Year"),
        }
        r = 3
        ws.write(r, 1, "Resolved Filter Criteria", F["card_title"]); r += 1
        for name, formula in crit.items():
            ws.write(r, 1, name, F["calc_lbl"])
            ws.write_formula(r, 2, "=" + formula, F["calc_val"], 0)
            self.wb.define_name(name, "='Calculations'!$C$%d" % (r + 1))
            r += 1

        # short helpers for filter argument tuples ---------------------------
        def f5(key):  # year, monthname, dept, area, shift
            return (rng(key,"Year")+",yCrit,"+rng(key,"Month Name")+",mCrit,"+
                    rng(key,"Department")+",dCrit,"+rng(key,"Area")+",aCrit,"+
                    rng(key,"Shift")+",sCrit")
        def f3(key):  # year, monthname, dept
            return (rng(key,"Year")+",yCrit,"+rng(key,"Month Name")+",mCrit,"+
                    rng(key,"Department")+",dCrit")
        def f4(key):  # year, monthname, dept, area
            return (rng(key,"Year")+",yCrit,"+rng(key,"Month Name")+",mCrit,"+
                    rng(key,"Department")+",dCrit,"+rng(key,"Area")+",aCrit")

        # ---- KPI engine cells (named) --------------------------------------
        r += 1
        ws.write(r, 1, "Core KPI Values", F["card_title"]); r += 1
        eng = {}
        def eng_cell(name, formula, numfmt="0.00"):
            nonlocal r
            fmt = self.wb.add_format({"font_name":"Segoe UI","font_size":10,"align":"right",
                "valign":"vcenter","bg_color":GREY_L,"border":1,"border_color":"#D8E1EB","num_format":numfmt})
            ws.write(r, 1, name, F["calc_lbl"])
            ws.write_formula(r, 2, "=" + formula, fmt, 0)
            self.wb.define_name(name, "='Calculations'!$C$%d" % (r + 1))
            eng[name] = "'Calculations'!$C$%d" % (r + 1)
            r += 1

        I_TYPE = rng("incident","Incident Type")
        eng_cell("Manhours", "IFERROR(SUMIFS(%s,%s,yCrit,%s,mCrit,%s,dCrit),0)" % (
            rng("manhours","Man-hours"), rng("manhours","Year"),
            rng("manhours","Month Name"), rng("manhours","Department")), "#,##0")
        eng_cell("LTI", 'COUNTIFS(%s,"Lost Time Injury",%s)' % (I_TYPE, f5("incident")), "0")
        eng_cell("MTC", 'COUNTIFS(%s,"Medical Treatment Case",%s)' % (I_TYPE, f5("incident")), "0")
        eng_cell("RWC", 'COUNTIFS(%s,"Restricted Work Case",%s)' % (I_TYPE, f5("incident")), "0")
        eng_cell("Recordable", "LTI+MTC+RWC", "0")
        eng_cell("FirstAid", "COUNTIFS(%s)" % f5("firstaid"), "0")
        eng_cell("NearMiss", "COUNTIFS(%s)" % f5("nearmiss"), "0")
        eng_cell("HiPoNM", 'COUNTIFS(%s,"High Potential",%s)' % (rng("nearmiss","Potential"), f5("nearmiss")), "0")
        eng_cell("SafetyObs", "COUNTIFS(%s)" % f5("safetyobs"), "0")
        SO_CAT = rng("safetyobs","Category")
        eng_cell("UnsafeActs", 'COUNTIFS(%s,"Unsafe Act",%s)' % (SO_CAT, f5("safetyobs")), "0")
        eng_cell("UnsafeConds", 'COUNTIFS(%s,"Unsafe Condition",%s)' % (SO_CAT, f5("safetyobs")), "0")
        eng_cell("GoodCatch", 'COUNTIFS(%s,"Good Catch",%s)' % (SO_CAT, f5("safetyobs")), "0")
        eng_cell("LostDays", "SUMIFS(%s,%s)" % (rng("incident","Lost Days"), f5("incident")), "0")
        eng_cell("TRIR", "IFERROR(Recordable*200000/Manhours,0)", "0.00")
        eng_cell("LTIFR", "IFERROR(LTI*1000000/Manhours,0)", "0.00")
        eng_cell("SeverityRate", "IFERROR(LostDays*1000000/Manhours,0)", "0.00")
        eng_cell("FrequencyRate", "IFERROR((LTI+RWC)*1000000/Manhours,0)", "0.00")
        eng_cell("NearMissRate", "IFERROR(NearMiss*200000/Manhours,0)", "0.00")
        # compliance %
        eng_cell("PTWComp", "IFERROR(COUNTIFS(%s,\"Compliant\",%s)/COUNTIFS(%s),0)*100" % (
            rng("ptw","Compliance"), f5("ptw"), f5("ptw")), '0.0"%"')
        eng_cell("InspComp", "IFERROR(SUMIFS(%s,%s)/SUMIFS(%s,%s),0)*100" % (
            rng("inspection","Completed"), f4("inspection"),
            rng("inspection","Planned"), f4("inspection")), '0.0"%"')
        eng_cell("AuditComp", "IFERROR(AVERAGEIFS(%s,%s),0)" % (
            rng("audit","Score"), f3("audit")), '0.0"%"')
        eng_cell("TrainComp", "IFERROR(SUMIFS(%s,%s)/SUMIFS(%s,%s),0)*100" % (
            rng("training","Completed"), f3("training"),
            rng("training","Planned"), f3("training")), '0.0"%"')
        eng_cell("PPEComp", "IFERROR(SUMIFS(%s,%s)/SUMIFS(%s,%s),0)*100" % (
            rng("ppe","Compliant"), f4("ppe"),
            rng("ppe","Checked"), f4("ppe")), '0.0"%"')
        eng_cell("StatComp", "IFERROR(COUNTIFS(%s,\"Compliant\",%s,dCrit)/COUNTIFS(%s,dCrit),0)*100" % (
            rng("statutory","Compliance"), rng("statutory","Department"),
            rng("statutory","Department")), '0.0"%"')
        # CAPA dept is a different column position -> f3 uses Department field name (works)
        eng_cell("ActionClosure", "IFERROR(COUNTIFS(%s,\"Closed\",%s)/COUNTIFS(%s),0)*100" % (
            rng("capa","Status"), f3("capa"), f3("capa")), '0.0"%"')
        eng_cell("ObsClosure", "IFERROR(COUNTIFS(%s,\"Closed\",%s)/COUNTIFS(%s),0)*100" % (
            rng("safetyobs","Status"), f5("safetyobs"), f5("safetyobs")), '0.0"%"')
        eng_cell("SafetyScore",
            "ROUND(PTWComp*0.18+InspComp*0.15+AuditComp*0.12+TrainComp*0.15+"
            "PPEComp*0.15+StatComp*0.10+ActionClosure*0.15,0)", "0")
        eng_cell("SafetyPerfIndex",
            "MAX(0,MIN(100,ROUND(100-TRIR*6-LTIFR*4-(SafetyObs=0)*0,0)))", "0")

        self.eng = eng

        # ---- monthly trend matrix -----------------------------------------
        mr = 3
        mc = 5   # column F (index 5)
        ws.write(mr - 1, mc, "MONTHLY TREND (Dashboard Year & Dept)", F["card_title"])
        headers = ["Month","Recordable","First Aid","Near Miss","Unsafe Act",
                   "Unsafe Cond","Safety Obs","Total Incident","Man-hours",
                   "TRIR","LTIFR","Train %","PTW %"]
        for j, h in enumerate(headers):
            ws.write(mr, mc + j, h, F["th"])
        Iy = rng("incident","Year"); Im = rng("incident","Month"); Id = rng("incident","Department")
        for i, mn in enumerate(MONTHS):
            rr = mr + 1 + i
            m = i + 1
            ws.write(rr, mc + 0, mn, F["td"])
            # recordable = LTI+MTC+RWC that month
            base = "%s,DashYear,%s,%d,%s,dCrit" % (Iy, Im, m, Id)
            rec = ('COUNTIFS(%s,"Lost Time Injury",%s)+COUNTIFS(%s,"Medical Treatment Case",%s)'
                   '+COUNTIFS(%s,"Restricted Work Case",%s)') % (I_TYPE, base, I_TYPE, base, I_TYPE, base)
            ws.write_formula(rr, mc + 1, "=" + rec, F["td_num"], 0)
            fa = "COUNTIFS(%s,DashYear,%s,%d,%s,dCrit)" % (
                rng("firstaid","Year"), rng("firstaid","Month"), m, rng("firstaid","Department"))
            ws.write_formula(rr, mc + 2, "=" + fa, F["td_num"], 0)
            nm = "COUNTIFS(%s,DashYear,%s,%d,%s,dCrit)" % (
                rng("nearmiss","Year"), rng("nearmiss","Month"), m, rng("nearmiss","Department"))
            ws.write_formula(rr, mc + 3, "=" + nm, F["td_num"], 0)
            soy=rng("safetyobs","Year"); som=rng("safetyobs","Month"); sod=rng("safetyobs","Department")
            ua = 'COUNTIFS(%s,"Unsafe Act",%s,DashYear,%s,%d,%s,dCrit)' % (SO_CAT, soy, som, m, sod)
            uc = 'COUNTIFS(%s,"Unsafe Condition",%s,DashYear,%s,%d,%s,dCrit)' % (SO_CAT, soy, som, m, sod)
            ws.write_formula(rr, mc + 4, "=" + ua, F["td_num"], 0)
            ws.write_formula(rr, mc + 5, "=" + uc, F["td_num"], 0)
            so = "COUNTIFS(%s,DashYear,%s,%d,%s,dCrit)" % (soy, som, m, sod)
            ws.write_formula(rr, mc + 6, "=" + so, F["td_num"], 0)
            tot = "%s+%s" % (xl_rowcol_to_cell(rr, mc+1), xl_rowcol_to_cell(rr, mc+2))
            ws.write_formula(rr, mc + 7, "=" + tot, F["td_num"], 0)
            mh = "SUMIFS(%s,%s,DashYear,%s,%d,%s,dCrit)" % (
                rng("manhours","Man-hours"), rng("manhours","Year"),
                rng("manhours","Month"), m, rng("manhours","Department"))
            ws.write_formula(rr, mc + 8, "=" + mh, F["td_num"], 0)
            recc = xl_rowcol_to_cell(rr, mc+1); lticell = "COUNTIFS(%s,\"Lost Time Injury\",%s)" % (I_TYPE, base)
            mhcell = xl_rowcol_to_cell(rr, mc+8)
            ws.write_formula(rr, mc + 9, "=IFERROR(%s*200000/%s,0)" % (recc, mhcell),
                self._num(ws, "0.00"), 0)
            ws.write_formula(rr, mc + 10, "=IFERROR((%s)*1000000/%s,0)" % (lticell, mhcell),
                self._num(ws, "0.00"), 0)
            tc = "IFERROR(SUMIFS(%s,%s,DashYear,%s,%d,%s,dCrit)/SUMIFS(%s,%s,DashYear,%s,%d,%s,dCrit),0)*100" % (
                rng("training","Completed"), rng("training","Year"), rng("training","Month"), m, rng("training","Department"),
                rng("training","Planned"), rng("training","Year"), rng("training","Month"), m, rng("training","Department"))
            ws.write_formula(rr, mc + 11, "=" + tc, self._num(ws, '0.0"%"'), 0)
            pc = "IFERROR(COUNTIFS(%s,\"Compliant\",%s,DashYear,%s,%d,%s,dCrit)/COUNTIFS(%s,DashYear,%s,%d,%s,dCrit),0)*100" % (
                rng("ptw","Compliance"), rng("ptw","Year"), rng("ptw","Month"), m, rng("ptw","Department"),
                rng("ptw","Year"), rng("ptw","Month"), m, rng("ptw","Department"))
            ws.write_formula(rr, mc + 12, "=" + pc, self._num(ws, '0.0"%"'), 0)
        self.mm = {"first": mr + 1, "last": mr + 12, "c0": mc}
        # named month-range helpers for charts
        def mcol(idx):
            c = xl_col_to_name(mc + idx)
            return "'Calculations'!$%s$%d:$%s$%d" % (c, mr+2, c, mr+13)
        R["months"] = mcol(0)
        R["recordable_m"]=mcol(1); R["firstaid_m"]=mcol(2); R["nearmiss_m"]=mcol(3)
        R["ua_m"]=mcol(4); R["uc_m"]=mcol(5); R["so_m"]=mcol(6); R["tot_m"]=mcol(7)
        R["mh_m"]=mcol(8); R["trir_m"]=mcol(9); R["ltifr_m"]=mcol(10)
        R["train_m"]=mcol(11); R["ptw_m"]=mcol(12)

        # ---- incident classification (doughnut) ----------------------------
        r2 = mr + 16
        ws.write(r2, mc, "Incident Classification", F["th"])
        ws.write(r2, mc + 1, "Count", F["th"])
        for i, t in enumerate(data_gen.INCIDENT_TYPES):
            rr = r2 + 1 + i
            ws.write(rr, mc, t, F["td_l"])
            ws.write_formula(rr, mc + 1, '=COUNTIFS(%s,"%s",%s)' % (I_TYPE, t, f5("incident")), F["td_num"], 0)
        cc = xl_col_to_name(mc); vc = xl_col_to_name(mc + 1)
        R["clsf_lbl"] = "'Calculations'!$%s$%d:$%s$%d" % (cc, r2+2, cc, r2+1+len(data_gen.INCIDENT_TYPES))
        R["clsf_val"] = "'Calculations'!$%s$%d:$%s$%d" % (vc, r2+2, vc, r2+1+len(data_gen.INCIDENT_TYPES))

        # ---- root cause pareto ---------------------------------------------
        rp = r2 + 12
        ws.write(rp - 1, mc, "ROOT CAUSE PARETO", F["card_title"])
        ws.write(rp, mc, "Root Cause", F["th"]); ws.write(rp, mc+1,"Count",F["th"])
        ws.write(rp, mc+2,"Adj",F["th"]); ws.write(rp, mc+3,"Sorted Cause",F["th"])
        ws.write(rp, mc+4,"Sorted Count",F["th"]); ws.write(rp, mc+5,"Cumulative %",F["th"])
        RC = rng("incident","Root Cause")
        causes = data_gen.ROOT_CAUSES
        for i, c in enumerate(causes):
            rr = rp + 1 + i
            ws.write(rr, mc, c, F["td_l"])
            ws.write_formula(rr, mc+1, '=COUNTIFS(%s,"%s",%s)' % (RC, c, f5("incident")), F["td_num"], 0)
            ws.write_formula(rr, mc+2, "=%s+ROW()/100000" % xl_rowcol_to_cell(rr, mc+1), self._num(ws,"0.00000"), 0)
        adj_first = xl_rowcol_to_cell(rp+1, mc+2, True, True)
        adj_last = xl_rowcol_to_cell(rp+len(causes), mc+2, True, True)
        cnt_first = xl_rowcol_to_cell(rp+1, mc+1, True, True); cnt_last = xl_rowcol_to_cell(rp+len(causes), mc+1, True, True)
        name_first = xl_rowcol_to_cell(rp+1, mc, True, True); name_last = xl_rowcol_to_cell(rp+len(causes), mc, True, True)
        for i in range(len(causes)):
            rr = rp + 1 + i; k = i + 1
            large = "LARGE(%s:%s,%d)" % (adj_first, adj_last, k)
            ws.write_formula(rr, mc+3, "=INDEX(%s:%s,MATCH(%s,%s:%s,0))" % (
                name_first, name_last, large, adj_first, adj_last), F["td_l"], 0)
            ws.write_formula(rr, mc+4, "=INT(%s)" % large, F["td_num"], 0)
            sc_first = xl_rowcol_to_cell(rp+1, mc+4, True, True); sc_this = xl_rowcol_to_cell(rr, mc+4, True, False)
            ws.write_formula(rr, mc+5, "=IFERROR(SUM(%s:%s)/SUM(%s:%s)*100,0)" % (
                sc_first, sc_this, cnt_first, cnt_last), self._num(ws, '0.0"%"'), 0)
        sc = xl_col_to_name(mc+3); vc2 = xl_col_to_name(mc+4); pc2 = xl_col_to_name(mc+5)
        R["pareto_lbl"]="'Calculations'!$%s$%d:$%s$%d"%(sc,rp+2,sc,rp+1+len(causes))
        R["pareto_val"]="'Calculations'!$%s$%d:$%s$%d"%(vc2,rp+2,vc2,rp+1+len(causes))
        R["pareto_cum"]="'Calculations'!$%s$%d:$%s$%d"%(pc2,rp+2,pc2,rp+1+len(causes))

        # ---- department safety score (bar) ---------------------------------
        rd = rp + len(causes) + 3
        ws.write(rd - 1, mc, "DEPARTMENT SAFETY SCORE", F["card_title"])
        ws.write(rd, mc, "Department", F["th"]); ws.write(rd, mc+1, "Score", F["th"])
        ws.write(rd, mc+2, "Recordable", F["th"]); ws.write(rd, mc+3, "Near Miss", F["th"])
        for i, d in enumerate(data_gen.DEPARTMENTS):
            rr = rd + 1 + i
            ws.write(rr, mc, d, F["td_l"])
            recd = ('COUNTIFS(%s,"Lost Time Injury",%s,DashYear,%s,"%s")'
                    '+COUNTIFS(%s,"Medical Treatment Case",%s,DashYear,%s,"%s")'
                    '+COUNTIFS(%s,"Restricted Work Case",%s,DashYear,%s,"%s")') % (
                I_TYPE, Iy, Id, d, I_TYPE, Iy, Id, d, I_TYPE, Iy, Id, d)
            nmd = 'COUNTIFS(%s,DashYear,%s,"%s")' % (rng("nearmiss","Year"), rng("nearmiss","Department"), d)
            fad = 'COUNTIFS(%s,DashYear,%s,"%s")' % (rng("firstaid","Year"), rng("firstaid","Department"), d)
            ws.write_formula(rr, mc+2, "=" + recd, F["td_num"], 0)
            ws.write_formula(rr, mc+3, "=" + nmd, F["td_num"], 0)
            recc = xl_rowcol_to_cell(rr, mc+2); fac = fad
            ws.write_formula(rr, mc+1, "=MAX(45,MIN(100,ROUND(100-%s*8-%s*1.5,0)))" % (recc, fad),
                             F["td_num"], 0)
        dc = xl_col_to_name(mc); ssc = xl_col_to_name(mc+1)
        R["dept_lbl"]="'Calculations'!$%s$%d:$%s$%d"%(dc,rd+2,dc,rd+1+len(data_gen.DEPARTMENTS))
        R["dept_val"]="'Calculations'!$%s$%d:$%s$%d"%(ssc,rd+2,ssc,rd+1+len(data_gen.DEPARTMENTS))
        # traffic-light icon set on department safety score
        ws.conditional_format("$%s$%d:$%s$%d"%(ssc,rd+2,ssc,rd+1+len(data_gen.DEPARTMENTS)),
            {"type":"icon_set","icon_style":"3_traffic_lights","icons":[
                {"criteria":">=","type":"number","value":85},
                {"criteria":">=","type":"number","value":70}]})
        # data bars on monthly trend count columns
        mc0=self.mm["c0"]
        ws.conditional_format(self.mm["first"], mc0+1, self.mm["last"], mc0+3,
            {"type":"data_bar","bar_color":BLUE_M})
        ws.conditional_format(self.mm["first"], mc0+9, self.mm["last"], mc0+10,
            {"type":"3_color_scale","min_color":GREEN_L,"mid_color":"#FEF08A","max_color":RED})

        # ---- Top 10 tables (unsafe act / condition / high-risk area) -------
        R.update(self._top10(ws, "unsafeact", "Unsafe Act", data_gen.UNSAFE_ACTS, rd+14, mc, "topact"))
        R.update(self._top10(ws, "unsafecond", "Unsafe Condition", data_gen.UNSAFE_CONDITIONS, rd+14, mc+4, "topcond"))
        R.update(self._top_area(ws, rd+14, mc+8, "toparea"))

        # ---- risk heat map 5x5 ---------------------------------------------
        R.update(self._heatmap(ws, rd+30, mc))

        # ---- radar metrics -------------------------------------------------
        rr = rd + 42
        ws.write(rr-1, mc, "RADAR: Compliance Profile", F["card_title"])
        ws.write(rr, mc, "Metric", F["th"]); ws.write(rr, mc+1, "Value", F["th"])
        radar = [("PTW", "PTWComp"), ("Inspection","InspComp"), ("Audit","AuditComp"),
                 ("Training","TrainComp"), ("PPE","PPEComp"), ("Statutory","StatComp"),
                 ("Action Closure","ActionClosure")]
        for i, (lbl, nm) in enumerate(radar):
            ws.write(rr+1+i, mc, lbl, F["td_l"])
            ws.write_formula(rr+1+i, mc+1, "=%s" % nm, self._num(ws,'0.0"%"'), 0)
        rl = xl_col_to_name(mc); rv = xl_col_to_name(mc+1)
        R["radar_lbl"]="'Calculations'!$%s$%d:$%s$%d"%(rl,rr+2,rl,rr+1+len(radar))
        R["radar_val"]="'Calculations'!$%s$%d:$%s$%d"%(rv,rr+2,rv,rr+1+len(radar))

        # ---- gauge helper values (value + remainder + hidden half) ---------
        rg = rr + 12
        ws.write(rg-1, mc, "GAUGE HELPERS", F["card_title"])
        gcfg = [("Training","TrainComp"),("PTW","PTWComp"),("Statutory","StatComp"),
                ("Action Closure","ActionClosure"),("Inspection","InspComp"),("Audit","AuditComp")]
        ws.write(rg, mc, "Gauge", F["th"]); ws.write(rg, mc+1,"Value",F["th"])
        ws.write(rg, mc+2,"Remainder",F["th"]); ws.write(rg, mc+3,"Hidden",F["th"])
        gmap = {}
        for i,(lbl,nm) in enumerate(gcfg):
            gr = rg+1+i
            ws.write(gr, mc, lbl, F["td_l"])
            ws.write_formula(gr, mc+1, "=MIN(100,%s)/2" % nm, self._num(ws,"0.0"),0)
            ws.write_formula(gr, mc+2, "=50-%s" % xl_rowcol_to_cell(gr,mc+1), self._num(ws,"0.0"),0)
            ws.write(gr, mc+3, 50, self._num(ws,"0.0"))
            vc3 = xl_col_to_name(mc+1)
            gmap[nm] = "'Calculations'!$%s$%d:$%s$%d" % (vc3, gr+1, xl_col_to_name(mc+3), gr+1)
        self.gmap = gmap
        R["gauge_names"] = gmap

        # ---- CAPA by status (doughnut) & source (bar) ----------------------
        R.update(self._capa_tables(ws, rg+10, mc))
        # ---- inspection / audit stacked helpers ----------------------------
        R.update(self._insp_audit(ws, rg+22, mc))

        ws.write_url(0, 1, "internal:'Home'!A1", F["card_title"], "Home")
        self.R = R

    # helpers ------------------------------------------------------------
    def _num(self, ws, nf):
        return self.wb.add_format({"font_name":"Segoe UI","font_size":10,"align":"center",
            "valign":"vcenter","border":1,"border_color":"#D8E1EB","num_format":nf})

    def _top10(self, ws, key, field, items, r0, c0, tag):
        F = self.F
        ws.write(r0-1, c0, "TOP: "+field, F["card_title"])
        ws.write(r0, c0, field, F["th"]); ws.write(r0, c0+1, "Count", F["th"])
        ws.write(r0, c0+2, "Adj", F["th"]); ws.write(r0, c0+3, "Rank Item", F["th"])
        ws.write(r0, c0+4, "Rank Count", F["th"])
        rngf = rng(key, field); ry = rng(key,"Year"); rd = rng(key,"Department")
        for i, it in enumerate(items):
            rr = r0+1+i
            ws.write(rr, c0, it, F["td_l"])
            ws.write_formula(rr, c0+1, '=COUNTIFS(%s,"%s",%s,DashYear,%s,dCrit)' % (rngf,it,ry,rd), F["td_num"],0)
            ws.write_formula(rr, c0+2, "=%s+ROW()/100000" % xl_rowcol_to_cell(rr,c0+1), self._num(ws,"0.00000"),0)
        af=xl_rowcol_to_cell(r0+1,c0+2,True,True); al=xl_rowcol_to_cell(r0+len(items),c0+2,True,True)
        nf=xl_rowcol_to_cell(r0+1,c0,True,True); nl=xl_rowcol_to_cell(r0+len(items),c0,True,True)
        for i in range(len(items)):
            rr=r0+1+i; k=i+1
            large="LARGE(%s:%s,%d)"%(af,al,k)
            ws.write_formula(rr,c0+3,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf,nl,large,af,al),F["td_l"],0)
            ws.write_formula(rr,c0+4,"=INT(%s)"%large,F["td_num"],0)
        lc=xl_col_to_name(c0+3); vc=xl_col_to_name(c0+4)
        return {tag+"_lbl":"'Calculations'!$%s$%d:$%s$%d"%(lc,r0+2,lc,r0+1+len(items)),
                tag+"_val":"'Calculations'!$%s$%d:$%s$%d"%(vc,r0+2,vc,r0+1+len(items))}

    def _top_area(self, ws, r0, c0, tag):
        F=self.F; areas=data_gen.AREAS
        ws.write(r0-1,c0,"TOP HIGH-RISK AREAS",F["card_title"])
        ws.write(r0,c0,"Area",F["th"]); ws.write(r0,c0+1,"Incidents",F["th"])
        ws.write(r0,c0+2,"Adj",F["th"]); ws.write(r0,c0+3,"Rank Area",F["th"]); ws.write(r0,c0+4,"Rank Count",F["th"])
        ry=rng("incident","Year"); ra=rng("incident","Area"); rd=rng("incident","Department")
        for i,a in enumerate(areas):
            rr=r0+1+i
            ws.write(rr,c0,a,F["td_l"])
            ws.write_formula(rr,c0+1,'=COUNTIFS(%s,"%s",%s,DashYear,%s,dCrit)'%(ra,a,ry,rd),F["td_num"],0)
            ws.write_formula(rr,c0+2,"=%s+ROW()/100000"%xl_rowcol_to_cell(rr,c0+1),self._num(ws,"0.00000"),0)
        af=xl_rowcol_to_cell(r0+1,c0+2,True,True); al=xl_rowcol_to_cell(r0+len(areas),c0+2,True,True)
        nf=xl_rowcol_to_cell(r0+1,c0,True,True); nl=xl_rowcol_to_cell(r0+len(areas),c0,True,True)
        for i in range(min(10,len(areas))):
            rr=r0+1+i;k=i+1;large="LARGE(%s:%s,%d)"%(af,al,k)
            ws.write_formula(rr,c0+3,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf,nl,large,af,al),F["td_l"],0)
            ws.write_formula(rr,c0+4,"=INT(%s)"%large,F["td_num"],0)
        lc=xl_col_to_name(c0+3); vc=xl_col_to_name(c0+4)
        return {tag+"_lbl":"'Calculations'!$%s$%d:$%s$%d"%(lc,r0+2,lc,r0+11),
                tag+"_val":"'Calculations'!$%s$%d:$%s$%d"%(vc,r0+2,vc,r0+11)}

    def _heatmap(self, ws, r0, c0):
        F=self.F
        ws.write(r0-1,c0,"RISK HEAT MAP (Likelihood x Severity)",F["card_title"])
        # top-left corner label
        ws.write(r0, c0, "L \\ S", F["heat_axis"])
        for s in range(1,6):
            ws.write(r0, c0+s, "S%d"%s, F["heat_axis"])
        ry=rng("risk","Year"); rL=rng("risk","Likelihood"); rS=rng("risk","Severity"); rd=rng("risk","Department")
        for li in range(1,6):
            rr=r0+li
            ws.write(rr, c0, "L%d"%li, F["heat_axis"])
            for s in range(1,6):
                ws.write_formula(rr, c0+s,
                    '=COUNTIFS(%s,%d,%s,%d,%s,DashYear,%s,dCrit)'%(rL,li,rS,s,ry,rd),
                    F["heat"], 0)
        first=xl_rowcol_to_cell(r0+1,c0+1); last=xl_rowcol_to_cell(r0+5,c0+5)
        ws.conditional_format("%s:%s"%(first,last), {"type":"3_color_scale",
            "min_color":GREEN_L,"mid_color":"#FEF08A","max_color":RED,
            "min_type":"num","min_value":0,"mid_type":"percentile","mid_value":50,
            "max_type":"num","max_value":8})
        return {"heat_first":first,"heat_last":last,
                "heat_range":"'Calculations'!%s:%s"%(first,last)}

    def _capa_tables(self, ws, r0, c0):
        F=self.F
        statuses=["Open","In Progress","Closed","Overdue"]
        ws.write(r0-1,c0,"CAPA STATUS",F["card_title"])
        ws.write(r0,c0,"Status",F["th"]); ws.write(r0,c0+1,"Count",F["th"])
        st=rng("capa","Status")
        for i,s in enumerate(statuses):
            ws.write(r0+1+i,c0,s,F["td_l"])
            ws.write_formula(r0+1+i,c0+1,'=COUNTIFS(%s,"%s",%s)'%(st,s,self._capa_f3()),F["td_num"],0)
        lc=xl_col_to_name(c0); vc=xl_col_to_name(c0+1)
        out={"capast_lbl":"'Calculations'!$%s$%d:$%s$%d"%(lc,r0+2,lc,r0+1+len(statuses)),
             "capast_val":"'Calculations'!$%s$%d:$%s$%d"%(vc,r0+2,vc,r0+1+len(statuses))}
        # by source
        r1=r0; c1=c0+3
        sources=["Incident","Audit","Inspection","Near Miss","Observation","Drill"]
        ws.write(r1,c1,"Source",F["th"]); ws.write(r1,c1+1,"Count",F["th"])
        sc=rng("capa","Source")
        for i,s in enumerate(sources):
            ws.write(r1+1+i,c1,s,F["td_l"])
            ws.write_formula(r1+1+i,c1+1,'=COUNTIFS(%s,"%s",%s)'%(sc,s,self._capa_f3()),F["td_num"],0)
        lc2=xl_col_to_name(c1); vc2=xl_col_to_name(c1+1)
        out["capasrc_lbl"]="'Calculations'!$%s$%d:$%s$%d"%(lc2,r1+2,lc2,r1+1+len(sources))
        out["capasrc_val"]="'Calculations'!$%s$%d:$%s$%d"%(vc2,r1+2,vc2,r1+1+len(sources))
        return out

    def _capa_f3(self):
        return (rng("capa","Year")+",yCrit,"+rng("capa","Month Name")+",mCrit,"+
                rng("capa","Department")+",dCrit")

    def _insp_audit(self, ws, r0, c0):
        F=self.F
        ws.write(r0-1,c0,"INSPECTION STATUS (by Type)",F["card_title"])
        ws.write(r0,c0,"Type",F["th"]); ws.write(r0,c0+1,"Planned",F["th"])
        ws.write(r0,c0+2,"Completed",F["th"]); ws.write(r0,c0+3,"Pending",F["th"])
        it=rng("inspection","Inspection Type"); ry=rng("inspection","Year"); rd=rng("inspection","Department")
        pl=rng("inspection","Planned"); cp=rng("inspection","Completed")
        for i,t in enumerate(data_gen.INSPECTION_TYPES):
            rr=r0+1+i
            ws.write(rr,c0,t,F["td_l"])
            base='%s,"%s",%s,DashYear,%s,dCrit'%(it,t,ry,rd)
            ws.write_formula(rr,c0+1,'=SUMIFS(%s,%s)'%(pl,base),F["td_num"],0)
            ws.write_formula(rr,c0+2,'=SUMIFS(%s,%s)'%(cp,base),F["td_num"],0)
            ws.write_formula(rr,c0+3,"=%s-%s"%(xl_rowcol_to_cell(rr,c0+1),xl_rowcol_to_cell(rr,c0+2)),F["td_num"],0)
        n=len(data_gen.INSPECTION_TYPES)
        lc=xl_col_to_name(c0);pc=xl_col_to_name(c0+2);qc=xl_col_to_name(c0+3)
        out={"insp_lbl":"'Calculations'!$%s$%d:$%s$%d"%(lc,r0+2,lc,r0+1+n),
             "insp_done":"'Calculations'!$%s$%d:$%s$%d"%(pc,r0+2,pc,r0+1+n),
             "insp_pend":"'Calculations'!$%s$%d:$%s$%d"%(qc,r0+2,qc,r0+1+n)}
        # audit status by type
        r1=r0; c1=c0+5
        ws.write(r1,c1,"Audit Type",F["th"]); ws.write(r1,c1+1,"NCR",F["th"])
        ws.write(r1,c1+2,"Closed",F["th"]); ws.write(r1,c1+3,"Open",F["th"])
        at=rng("audit","Audit Type"); ay=rng("audit","Year"); ad=rng("audit","Department")
        ncr=rng("audit","NCRs"); ncc=rng("audit","NCRs Closed")
        for i,t in enumerate(data_gen.AUDIT_TYPES):
            rr=r1+1+i
            ws.write(rr,c1,t,F["td_l"])
            base='%s,"%s",%s,DashYear,%s,dCrit'%(at,t,ay,ad)
            ws.write_formula(rr,c1+1,'=SUMIFS(%s,%s)'%(ncr,base),F["td_num"],0)
            ws.write_formula(rr,c1+2,'=SUMIFS(%s,%s)'%(ncc,base),F["td_num"],0)
            ws.write_formula(rr,c1+3,"=%s-%s"%(xl_rowcol_to_cell(rr,c1+1),xl_rowcol_to_cell(rr,c1+2)),F["td_num"],0)
        na=len(data_gen.AUDIT_TYPES)
        lc2=xl_col_to_name(c1);cc2=xl_col_to_name(c1+2);oc2=xl_col_to_name(c1+3)
        out["aud_lbl"]="'Calculations'!$%s$%d:$%s$%d"%(lc2,r1+2,lc2,r1+1+na)
        out["aud_closed"]="'Calculations'!$%s$%d:$%s$%d"%(cc2,r1+2,cc2,r1+1+na)
        out["aud_open"]="'Calculations'!$%s$%d:$%s$%d"%(oc2,r1+2,oc2,r1+1+na)
        return out


def _to_dt(v):
    import datetime
    if isinstance(v, datetime.date):
        return datetime.datetime(v.year, v.month, v.day)
    return v


# --------------------------------------------------------------------------
if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..",
                       "RCPL_Executive_EHS_KPI_Dashboard.xlsm")
    out = os.path.abspath(out)
    b = Builder(out)
    b.write_registers()
    b.write_master()
    b.write_calculations()
    # dashboards + docs added in xlsm_dash.py
    import xlsm_dash
    xlsm_dash.build_dashboards(b)
    xlsm_dash.build_docs(b)
    # embed VBA
    vba = vbabin.build_vba_project(vba_code.modules())
    binpath = os.path.join(os.path.dirname(__file__), "vbaProject.bin")
    with open(binpath, "wb") as fh:
        fh.write(vba)
    b.wb.add_vba_project(binpath)
    b.wb.set_vba_name("ThisWorkbook")
    b.wb.close()
    print("WROTE", out, os.path.getsize(out), "bytes")
