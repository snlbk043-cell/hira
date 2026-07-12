#!/usr/bin/env python3
"""
RCPL Integrated EHS Management System  ->  macro-enabled workbook (.xlsm)

Adopts the structure/taxonomy of HSE_Full_System.xlsx:
  24 registers (exact headers) + 24 per-register interactive dashboards
  + Executive Dashboard + Leadership Review + Master Data + Settings + Help,
with a live rollup engine, native charts, conditional formatting and working VBA.
"""
import os, datetime
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

import hse_data as HD
import vbabin, vba_code_hse

DATA = HD.build_all()
MONTHS = HD.MONTHS
D0, DN = 4, 100003        # register data rows (header row 3) -> supports 100,000 records

BLUE_D="#0F3D6E"; BLUE_M="#0B6EA8"; BLUE_L="#E8F1FA"; GREY_D="#334155"
GREY_M="#64748B"; GREY_L="#F1F5F9"; GREEN="#15A34A"; GREEN_L="#DCFCE7"
AMBER="#F59E0B"; AMBER_L="#FEF3C7"; RED="#DC2626"; RED_L="#FEE2E2"
WHITE="#FFFFFF"; INK="#1F2937"; ACCENT="#D71920"; CARDBG="#FFFFFF"
ACC={"blue":BLUE_M,"green":GREEN,"red":RED,"amber":AMBER,"grey":GREY_M}

CLOSED_VALUES = {"Closed","Completed","Resolved","Approved","Compliant","Issued",
                 "Acknowledged","Presented"}
OPEN_VALUES = {"Open","In Progress","Overdue","Pending","Pending Review","Scheduled",
               "Under Review","Action Pending"}


def spec_of(key): return next(s for s in HD.REGISTERS if s["key"]==key)
def has(spec, name): return name in spec["headers"]
def col(spec, name): return xl_col_to_name(spec["headers"].index(name))
def rng(spec, name):
    return "'%s'!$%s$%d:$%s$%d" % (spec["sheet"], col(spec,name), D0, col(spec,name), DN)


class EHS:
    def __init__(self, path):
        self.wb = xlsxwriter.Workbook(path, {"nan_inf_to_errors":True})
        self.wb.set_calc_mode("auto")
        self.F = {}
        self._formats()
        self.RR = {}   # per-register chart/kpi ranges

    # ---------------------------------------------------------------- formats
    def _fmt(self, **k): return self.wb.add_format(k)
    def _formats(self):
        F=self.F; seg="Segoe UI"
        F["title"]=self._fmt(font_name=seg,font_size=22,bold=True,font_color=WHITE,
            bg_color=BLUE_D,align="left",valign="vcenter")
        F["sub"]=self._fmt(font_name=seg,font_size=10,font_color="#CFE0F0",bg_color=BLUE_D,
            align="left",valign="vcenter")
        F["accent"]=self._fmt(bg_color=ACCENT)
        F["section"]=self._fmt(font_name=seg,font_size=12,bold=True,font_color=BLUE_D,
            align="left",valign="vcenter",bottom=2,border_color=BLUE_M)
        F["th"]=self._fmt(font_name=seg,font_size=9,bold=True,font_color=WHITE,bg_color=BLUE_M,
            align="center",valign="vcenter",border=1,border_color=WHITE,text_wrap=True)
        F["td"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#D8E1EB")
        F["tdl"]=self._fmt(font_name=seg,font_size=9,align="left",valign="vcenter",
            border=1,border_color="#D8E1EB")
        F["tdn"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#D8E1EB",num_format="#,##0")
        F["tdp"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#D8E1EB",num_format='0.0"%"')
        # register entry sheet formats
        F["reg_title"]=self._fmt(font_name=seg,font_size=15,bold=True,font_color=WHITE,
            bg_color=BLUE_D,align="left",valign="vcenter")
        F["reg_legend"]=self._fmt(font_name=seg,font_size=9,italic=True,font_color=BLUE_D,
            bg_color=BLUE_L,align="left",valign="vcenter")
        F["reg_hdr"]=self._fmt(font_name=seg,font_size=9,bold=True,font_color=WHITE,
            bg_color=BLUE_M,align="center",valign="vcenter",border=1,border_color=WHITE,text_wrap=True)
        F["cell"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#E2E8F0")
        F["cell_l"]=self._fmt(font_name=seg,font_size=9,align="left",valign="vcenter",
            border=1,border_color="#E2E8F0")
        # unlocked variants: genuine user-input cells, so sheet protection can lock formulas only
        F["cell_in"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#E2E8F0",locked=False,bg_color="#FBFDFF")
        F["cell_in_l"]=self._fmt(font_name=seg,font_size=9,align="left",valign="vcenter",
            border=1,border_color="#E2E8F0",locked=False,bg_color="#FBFDFF")
        F["date_in"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#E2E8F0",num_format="dd-mmm-yy",locked=False,bg_color="#FBFDFF")
        F["cell_calc"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#E2E8F0",bg_color=GREY_L,num_format='0.0"%"')
        F["cell_calcn"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#E2E8F0",bg_color=GREY_L,num_format="#,##0")
        F["date"]=self._fmt(font_name=seg,font_size=9,align="center",valign="vcenter",
            border=1,border_color="#E2E8F0",num_format="dd-mmm-yy")
        F["note"]=self._fmt(font_name=seg,font_size=9,font_color=GREY_M,text_wrap=True,valign="top")
        F["h1"]=self._fmt(font_name=seg,font_size=17,bold=True,font_color=BLUE_D)
        F["h2"]=self._fmt(font_name=seg,font_size=12,bold=True,font_color=BLUE_M)
        F["body"]=self._fmt(font_name=seg,font_size=10,font_color=INK,text_wrap=True,valign="top")
        F["bodyb"]=self._fmt(font_name=seg,font_size=10,bold=True,font_color=INK,valign="top")
        F["refl"]=self._fmt(font_name=seg,font_size=9,italic=True,font_color=GREY_M,align="right",valign="vcenter")
        F["refv"]=self._fmt(font_name=seg,font_size=9,bold=True,font_color=BLUE_D,align="left",
            valign="vcenter",num_format="dd-mmm-yyyy hh:mm")
        F["set_lbl"]=self._fmt(font_name=seg,font_size=10,font_color=INK,align="left",valign="vcenter")
        F["set_val"]=self._fmt(font_name=seg,font_size=10,bold=True,font_color=BLUE_D,align="center",
            valign="vcenter",bg_color=AMBER_L,border=1,border_color="#E2C97A",locked=False)
        F["set_note"]=self._fmt(font_name=seg,font_size=9,italic=True,font_color=GREY_M,align="left",valign="vcenter")
        F["heat"]=self._fmt(font_name=seg,font_size=9,bold=True,align="center",valign="vcenter",
            border=1,border_color=WHITE,num_format="0")

    def cardfmt(self, accent, kind):
        key=("card",accent,kind)
        if key in self.F: return self.F[key]
        seg="Segoe UI"
        strip=self._fmt(bg_color=ACC[accent])
        tt=self._fmt(font_name=seg,font_size=8.5,bold=True,font_color=GREY_M,bg_color=WHITE,
            align="left",valign="vcenter",left=1,right=1,border_color="#E2E8F0")
        nf={"num":"#,##0","dec":"0.00","pct":'0.0"%"'}[kind]
        vv=self._fmt(font_name=seg,font_size=19,bold=True,font_color=BLUE_D,bg_color=WHITE,
            align="left",valign="vcenter",num_format=nf,left=1,right=1,border_color="#E2E8F0")
        ss=self._fmt(font_name=seg,font_size=8,font_color=GREY_M,bg_color=WHITE,align="left",
            valign="vcenter",left=1,right=1,bottom=1,border_color="#E2E8F0")
        self.F[key]=(strip,tt,vv,ss)
        return self.F[key]

    # ---------------------------------------------------------------- charts
    def _style(self, ch, title):
        ch.set_title({"name":title,"name_font":{"name":"Segoe UI","size":10.5,"bold":True,"color":BLUE_D}})
        ch.set_chartarea({"border":{"color":"#E2E8F0"},"fill":{"color":WHITE}})
        ch.set_plotarea({"fill":{"color":WHITE}})
        ch.set_legend({"position":"bottom","font":{"size":8}})
        ch.set_x_axis({"num_font":{"size":8},"line":{"color":"#CBD5E1"}})
        ch.set_y_axis({"num_font":{"size":8},"major_gridlines":{"visible":True,"line":{"color":"#EEF2F7"}}})
    def col_chart(self,cats,series,title,stacked=False):
        ch=self.wb.add_chart({"type":"column","subtype":"stacked" if stacked else None})
        for nm,v,c in series:
            ch.add_series({"name":nm,"categories":cats,"values":v,"fill":{"color":c},"border":{"none":True},"gap":50})
        self._style(ch,title); return ch
    def bar_chart(self,cats,vals,title,color=BLUE_M):
        ch=self.wb.add_chart({"type":"bar"})
        ch.add_series({"categories":cats,"values":vals,"fill":{"color":color},"border":{"none":True},
            "data_labels":{"value":True,"font":{"size":8}}})
        self._style(ch,title); ch.set_legend({"none":True}); return ch
    def line_chart(self,cats,vals,title,color=BLUE_M):
        ch=self.wb.add_chart({"type":"line"})
        ch.add_series({"categories":cats,"values":vals,"line":{"color":color,"width":2.25},
            "marker":{"type":"circle","size":5,"fill":{"color":color},"border":{"none":True}}})
        self._style(ch,title); ch.set_legend({"none":True}); return ch
    def dough(self,lbl,val,title,colors=None):
        ch=self.wb.add_chart({"type":"doughnut"})
        s={"categories":lbl,"values":val,"data_labels":{"percentage":True,"font":{"size":8,"color":WHITE,"bold":True}}}
        if colors: s["points"]=[{"fill":{"color":x}} for x in colors]
        ch.add_series(s); ch.set_hole_size(52); self._style(ch,title)
        ch.set_legend({"position":"right","font":{"size":8}}); return ch

    # ---------------------------------------------------------------- registers
    def write_registers(self):
        for spec in HD.REGISTERS:
            self._write_register(spec)

    def _write_register(self, spec):
        F=self.F; ws=self.wb.add_worksheet(spec["sheet"]); ws.set_tab_color(GREY_M)
        headers=spec["headers"]; nc=len(headers)
        ws.merge_range(0,0,0,nc-1, "%s  %s — DATA ENTRY"%(spec["emoji"],spec["sheet"].upper()), F["reg_title"])
        ws.set_row(0,22)
        ws.merge_range(1,0,1,nc-1,
            "Blue = user input   ·   Gray = auto-calculated   ·   use dropdowns where available", F["reg_legend"])
        rows=DATA[spec["key"]]
        auto=spec.get("auto",{})
        calc_cols = set(auto.keys())
        if spec["key"]=="incident": calc_cols.add("Ageing (Days)")
        if spec["key"]=="ca": calc_cols.add("Timeliness")
        if spec["key"]=="training": calc_cols.add("Certificate Expiry")
        FORMULA_BUFFER = 1000   # auto-calc formulas are pre-filled this many rows for frictionless growth
        for r,row in enumerate(rows):
            er=D0-1+r   # 0-indexed excel row (D0=4 -> er=3 for first data row after header at row index 2)
            for c,val in enumerate(row):
                h=headers[c]
                if h in calc_cols:
                    continue  # formula written below
                if isinstance(val, datetime.date):
                    ws.write_datetime(er,c, datetime.datetime(val.year,val.month,val.day), F["date_in"])
                elif isinstance(val,(int,float)):
                    ws.write_number(er,c,val, F["cell_in"])
                else:
                    ws.write(er,c, val, F["cell_in_l"] if c in (4,5) else F["cell_in"])
        # pre-fill calculated-column formulas for the sample rows + a growth buffer (frictionless data entry)
        for r in range(max(len(rows), FORMULA_BUFFER)):
            er=D0-1+r
            for tgt,(num,den) in auto.items():
                ci=headers.index(tgt)
                if num=="__ptw__":
                    tc=xl_rowcol_to_cell(er, headers.index("Total Checkpoints"))
                    dv=xl_rowcol_to_cell(er, headers.index("Deviations Found"))
                    ws.write_formula(er,ci,"=IFERROR((%s-%s)/%s*100,0)"%(tc,dv,tc), F["cell_calc"],0)
                else:
                    nn=xl_rowcol_to_cell(er, headers.index(num))
                    dd=xl_rowcol_to_cell(er, headers.index(den))
                    ws.write_formula(er,ci,"=IFERROR(%s/%s*100,0)"%(nn,dd), F["cell_calc"],0)
            if spec["key"]=="incident":
                ci=headers.index("Ageing (Days)")
                dt=xl_rowcol_to_cell(er,headers.index("Date"))
                cl=xl_rowcol_to_cell(er,headers.index("Closure Date"))
                st=xl_rowcol_to_cell(er,headers.index("Status"))
                ws.write_formula(er,ci,'=IF(%s="","",IF(%s="Closed",%s-%s,TODAY()-%s))'%(dt,st,cl,dt,dt),F["cell_calcn"],0)
            if spec["key"]=="ca":
                ci=headers.index("Timeliness")
                cd=xl_rowcol_to_cell(er,headers.index("Completion Date"))
                du=xl_rowcol_to_cell(er,headers.index("Due Date"))
                st=xl_rowcol_to_cell(er,headers.index("Status"))
                ws.write_formula(er,ci,'=IF(%s="","",IF(%s="Closed",IF(%s<=%s,"On-Time","Delayed"),"Pending"))'%(st,st,cd,du),F["cell_l"],0)
            if spec["key"]=="training":
                ci=headers.index("Certificate Expiry")
                dt=xl_rowcol_to_cell(er,headers.index("Date"))
                cert=xl_rowcol_to_cell(er,headers.index("Certificate Issued"))
                ws.write_formula(er,ci,'=IF(%s="Yes",%s+CertValidityDays,"")'%(cert,dt),F["date"],0)
        last=D0-1+max(len(rows), FORMULA_BUFFER)
        ws.add_table(2,0,last,nc-1, {"name":"t_"+spec["key"],"style":"Table Style Medium 9",
            "columns":[{"header":h} for h in headers]})
        for i,h in enumerate(headers):
            if h in calc_cols:
                if spec["key"]=="ca" and h=="Timeliness": colfmt=F["cell_l"]
                elif spec["key"]=="training" and h=="Certificate Expiry": colfmt=F["date"]
                else: colfmt=F["cell_calc"]
            else:
                colfmt = F["cell_in"]
            ws.set_column(i,i, max(9,min(24,len(h)+2)), colfmt)
        ws.freeze_panes(3,0); ws.set_zoom(90)
        ws.repeat_rows(0,2); ws.set_landscape(); ws.fit_to_pages(1,0)
        ws.write_url(0,nc+1,"internal:'Home'!A1", F["reg_legend"], "Home")
        # data validation dropdowns
        self._validations(ws, spec)

    def _validations(self, ws, spec):
        headers=spec["headers"]
        mp={"Department":"L_Dept","Location":"L_Loc","Area":"L_Loc","Status":"L_Status",
            "Risk Level":"L_Risk","Risk Rating":"L_Risk","Severity":"L_Risk","Priority":"L_Risk"}
        for h,name in mp.items():
            if h in headers:
                ci=headers.index(h)
                ws.data_validation(D0-1,ci,DN-1,ci,{"validate":"list","source":"="+name})

    # ---------------------------------------------------------------- master/settings/help
    def write_master(self):
        F=self.F; ws=self.wb.add_worksheet("Master Data"); ws.set_tab_color(BLUE_M)
        ws.hide_gridlines(2); ws.set_column("A:A",2)
        ws.merge_range("B2:K2","📚  MASTER DATA — single source of truth for dropdown lists", F["section"])
        lists=[("Department",HD.DEPARTMENTS,"L_Dept"),("Location",HD.LOCATIONS,"L_Loc"),
               ("Status",HD.STATUS,"L_Status"),("Risk Level",HD.RISK,"L_Risk"),
               ("Rating",HD.RATING,"L_Rating"),("Result",HD.RESULT,"L_Result"),
               ("Month",MONTHS,"L_Month")]
        c=1
        for title,vals,name in lists:
            ws.write(3,c,title,F["th"])
            for i,v in enumerate(vals): ws.write(4+i,c,v,F["tdl"])
            cL=xl_col_to_name(c)
            self.wb.define_name(name, "='Master Data'!$%s$5:$%s$%d"%(cL,cL,4+len(vals)))
            ws.set_column(c,c,18); c+=1
        # filter lists (with All)
        fl=[("F_Month",["All"]+MONTHS),("F_Dept",["All"]+HD.DEPARTMENTS),
            ("F_Period",MONTHS+["Q1","Q2","Q3","Q4"])]
        for title,vals in fl:
            ws.write(3,c,title,F["th"])
            for i,v in enumerate(vals): ws.write(4+i,c,v,F["tdl"])
            cL=xl_col_to_name(c)
            self.wb.define_name(title,"='Master Data'!$%s$5:$%s$%d"%(cL,cL,4+len(vals)))
            ws.set_column(c,c,14); c+=1
        ws.write_url(0,1,"internal:'Home'!A1",F["note"],"Home")

    def write_settings(self):
        F=self.F; ws=self.wb.add_worksheet("Settings"); ws.set_tab_color(GREY_D)
        ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",34)
        ws.set_column("C:C",16); ws.set_column("D:D",40)
        ws.merge_range("B2:D2","⚙️  SYSTEM SETTINGS — central configuration", F["section"])
        def block(r,t): ws.merge_range(r,1,r,3,t,F["h2"]); return r+1
        r=4; r=block(r,"ORGANISATION")
        for lbl,val in [("Company Name","RCPL — Campa Cola"),("Plant / Site","CSD Manufacturing Plant"),
                        ("Location","India"),("Reporting Year",HD.YEAR)]:
            ws.write(r,1,lbl,F["set_lbl"])
            if lbl=="Reporting Year":
                ws.write_number(r,2,val,F["set_val"]); self.wb.define_name("ReportYear","=Settings!$C$%d"%(r+1))
            else:
                ws.write(r,2,val,F["set_val"])
            r+=1
        r+=1; r=block(r,"EHS CALCULATION PARAMETERS")
        ws.write(r,1,"Monthly Man-Hours Worked",F["bodyb"])
        ws.write(r,3,"Edit per month for accuracy — TRIR/LTIFR use the exact hours for the selected period, not a flat average.",F["set_note"])
        r+=1
        mh_first=r+1
        for i,mn in enumerate(MONTHS):
            ws.write(r,1,mn,F["set_lbl"]); ws.write_number(r,2,1000000//12,F["set_val"]); r+=1
        mh_last=r
        self.wb.define_name("ManhoursM","=Settings!$C$%d:$C$%d"%(mh_first,mh_last))
        ws.write(r,1,"Total Man-Hours (annual, auto-sum)",F["set_lbl"])
        mh_fmt=self._fmt(font_name="Segoe UI",font_size=10,bold=True,font_color=BLUE_D,align="center",
            valign="vcenter",bg_color=GREY_L,border=1,border_color="#D8E1EB",num_format="#,##0")
        ws.write_formula(r,2,"=SUM(C%d:C%d)"%(mh_first,mh_last),mh_fmt,0)
        self.wb.define_name("Manhours","=Settings!$C$%d"%(r+1)); r+=2
        self._mh_first=mh_first   # Settings!$C$<row> of Jan man-hours; used by the period engine
        params=[("TRIR Multiplier",200000,"OSHA standard = 200,000","TRIRmult"),
                ("LTIFR Multiplier",1000000,"Per million man-hours","LTIFRmult")]
        for lbl,val,note,name in params:
            ws.write(r,1,lbl,F["set_lbl"]); ws.write_number(r,2,val,F["set_val"])
            ws.write(r,3,note,F["set_note"])
            self.wb.define_name(name,"=Settings!$C$%d"%(r+1)); r+=1
        r+=1; r=block(r,"TARGETS / RAG THRESHOLDS")
        tg=[("Observation Closure Target",0.9,"Green if ≥ target","TgtObs"),
            ("Training Compliance Target",0.95,"","TgtTrain"),
            ("Corrective Action Closure Target",0.9,"","TgtCA"),
            ("PTW Compliance Target",0.95,"","TgtPTW"),
            ("Generic Close-out % Target",0.85,"Used by Meetings/Visits/Insp/Unsafe-Act/NC/JSA/Bulletin closure-type KPIs","TgtCloseout"),
            ("Generic Attendance/Participation % Target",0.85,"Used by Toolbox/Drill/Mgmt-Review attendance-type KPIs","TgtAttendance"),
            ("Alcohol Positive Rate Target (max acceptable)",0.05,"Green if actual ≤ target","TgtAlcoholPositive"),
            ("TRIR Target (max acceptable)",1.0,"Green if actual ≤ target","TgtTRIR"),
            ("LTIFR Target (max acceptable)",2.0,"Green if actual ≤ target","TgtLTIFR"),
            ("RAG Amber band (fraction of target)",0.8,"Below this vs target = Red","AmberBand")]
        for lbl,val,note,name in tg:
            ws.write(r,1,lbl,F["set_lbl"]); ws.write_number(r,2,val,F["set_val"])
            ws.write(r,3,note,F["set_note"])
            self.wb.define_name(name,"=Settings!$C$%d"%(r+1)); r+=1
        r+=1; r=block(r,"COST PARAMETERS  ·  used only by the optional cost-impact rollups")
        cp=[("Downtime Cost per Minute (₹)",150,"Stop Work Authority downtime → estimated cost","CostPerDowntimeMin"),
            ("Lost-Day Cost per Day (₹)",8000,"Incident lost days → estimated cost","CostPerLostDay")]
        for lbl,val,note,name in cp:
            ws.write(r,1,lbl,F["set_lbl"]); ws.write_number(r,2,val,F["set_val"])
            ws.write(r,3,note,F["set_note"])
            self.wb.define_name(name,"=Settings!$C$%d"%(r+1)); r+=1

        r+=1; r=block(r,"INDUSTRY BENCHMARKING")
        bm=[("Industry Benchmark TRIR",1.5,"Reference line on the Executive TRIR trend chart","BenchTRIR"),
            ("Industry Benchmark LTIFR",2.5,"Reference line on the Executive LTIFR trend chart","BenchLTIFR")]
        for lbl,val,note,name in bm:
            ws.write(r,1,lbl,F["set_lbl"]); ws.write_number(r,2,val,F["set_val"])
            ws.write(r,3,note,F["set_note"])
            self.wb.define_name(name,"=Settings!$C$%d"%(r+1)); r+=1

        r+=1; r=block(r,"TRAINING PARAMETERS")
        ws.write(r,1,"Certificate Validity (days)",F["set_lbl"]); ws.write_number(r,2,365,F["set_val"])
        ws.write(r,3,"Certificate Issued date + this many days = expiry (Training dashboard)",F["set_note"])
        self.wb.define_name("CertValidityDays","=Settings!$C$%d"%(r+1)); r+=1

        r+=1; r=block(r,"PRIOR YEAR ACTUALS  ·  type in last year's year-end figures for a genuine YoY comparison "
                        "(left blank/0 until entered - never fabricated)")
        py=[("Prior Year TRIR",0,"","PYTRIR"),("Prior Year LTIFR",0,"","PYLTIFR"),
            ("Prior Year Total Incidents",0,"","PYTotalInc"),("Prior Year Training Compliance %",0,"","PYTrain"),
            ("Prior Year Obs Closure %",0,"","PYObs"),("Prior Year CA Closure %",0,"","PYCA")]
        for lbl,val,note,name in py:
            ws.write(r,1,lbl,F["set_lbl"]); ws.write_number(r,2,val,F["set_val"])
            ws.write(r,3,note,F["set_note"])
            self.wb.define_name(name,"=Settings!$C$%d"%(r+1)); r+=1
        ws.write_url(0,1,"internal:'Home'!A1",F["note"],"Home")

    def write_help(self):
        F=self.F; ws=self.wb.add_worksheet("Help"); ws.set_tab_color(GREEN)
        ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",22); ws.set_column("C:J",14)
        ws.write("B2","❓  Help & User Guide — Integrated EHS Management System", F["h1"])
        ws.write_url("B3","internal:'Home'!A1",F["h2"],"⌂ Back to Home")
        rows=[("Purpose","Single-workbook EHS system: 24 registers, each with its own live dashboard, plus Executive & Leadership rollups."),
              ("Enter data","Open any register (colored tab), type new rows under the table. Blue = input, Gray = auto-calculated."),
              ("Dropdowns","Driven by the Master Data sheet — edit a list there and every register dropdown updates."),
              ("Filters","Executive Dashboard has Month & Department drop-downs that drive the rollups."),
              ("Refresh","Click Refresh (or press F9). Workbook is set to automatic calculation."),
              ("TRIR","Recordable × TRIR-multiplier ÷ man-hours (man-hours & multipliers live on the Settings sheet)."),
              ("LTIFR","(LTI + Fatality) × LTIFR-multiplier ÷ man-hours."),
              ("RAG logic","🟢 Green = meets target · 🟡 Amber = within amber band · 🔴 Red = below."),
              ("Scalability","Each register + dashboard supports thousands of rows; add rows and refresh — no manual updates."),
              ("Extending","New registers follow the same 3-row header pattern (title / legend / column headers).")]
        r=4
        for k,v in rows:
            ws.write(r,1,k,F["bodyb"]); ws.merge_range(r,2,r,9,v,F["body"]); ws.set_row(r,30); r+=1

    # ---------------------------------------------------------------- calc engine
    def write_calc(self):
        F=self.F; ws=self.wb.add_worksheet("Calculations"); ws.set_tab_color(GREEN)
        ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",22)
        for cc in range(2,14): ws.set_column(cc,cc,11)
        self.calc=ws
        ws.merge_range("B2:H2","EHS ROLLUP ENGINE — auto-recalculates from every register", F["section"])
        # resolved criteria
        self.wb.define_name("mCrit",'=IF(SelMonth="All","<>",SelMonth)')
        self.wb.define_name("dCrit",'=IF(SelDept="All","<>",SelDept)')
        r=4
        ws.write(r,1,"Resolved Filters",F["bodyb"]); r+=1
        ws.write(r,1,"Month criteria",F["set_lbl"]); ws.write_formula(r,2,'=IF(SelMonth="All","<>",SelMonth)',F["td"],0)
        self._mCritCell="Calculations!$C$%d"%(r+1); r+=1
        ws.write(r,1,"Dept criteria",F["set_lbl"]); ws.write_formula(r,2,'=IF(SelDept="All","<>",SelDept)',F["td"],0)
        self._dCritCell="Calculations!$C$%d"%(r+1); r+=2
        # redefine names to concrete cells (so COUNTIFS can reference)
        self.wb.define_name("mCrit","="+self._mCritCell)
        self.wb.define_name("dCrit","="+self._dCritCell)

        # ---- executive variance engine (period vs prior period) ----
        r = self._exec_engine(ws, r)
        # ---- cross-tracker analytics (Register-Month filtered: Pareto, heat map, dept score, Top-10) ----
        r = self._exec_analytics(ws, r)
        # ---- per-register calc blocks ----
        cur=r
        for spec in HD.REGISTERS:
            self.RR[spec["key"]]=self._register_calc(ws, spec, cur)
            cur += 26
        ws.write_url(0,1,"internal:'Home'!A1",F["note"],"Home")

    def _cf(self, ws, r, c, formula, fmt=None):
        ws.write_formula(r,c,"="+formula, fmt or self.F["tdn"], 0)

    def _exec_calc(self, ws, r0):
        F=self.F; sp=spec_of("incident")
        Cls=rng(sp,"Classification"); Mn=rng(sp,"Month"); Dp=rng(sp,"Department"); Ld=rng(sp,"Lost Days")
        # month+dept filter suffix
        flt='%s,mCrit,%s,dCrit'%(Mn,Dp)
        def cif(*crit): return "COUNTIFS(%s)"%(",".join(crit))
        ws.write(r0,1,"EXECUTIVE ROLLUP",F["bodyb"])
        defs=[("Fatality",'COUNTIFS(%s,"Fatality",%s)'%(Cls,flt)),
              ("LostTime",'COUNTIFS(%s,"Lost Time Injury",%s)'%(Cls,flt)),
              ("Restricted",'COUNTIFS(%s,"Restricted Work",%s)'%(Cls,flt)),
              ("Medical",'COUNTIFS(%s,"Medical Treatment",%s)'%(Cls,flt)),
              ("FirstAid",'COUNTIFS(%s,"First Aid",%s)'%(Cls,flt)),
              ("NearMiss",'COUNTIFS(%s,"Near Miss",%s)'%(Cls,flt)),
              ("TotalInc",'COUNTIFS(%s,mCrit,%s,dCrit)'%(Mn,Dp)),
              ("LostDays",'SUMIFS(%s,%s,mCrit,%s,dCrit)'%(Ld,Mn,Dp)),
              ("Recordable","Medical+Restricted+LostTime+Fatality"),
              ("TRIR","IFERROR(Recordable*TRIRmult/Manhours,0)"),
              ("LTIFR","IFERROR((LostTime+Fatality)*LTIFRmult/Manhours,0)")]
        rr=r0+1
        for name,f in defs:
            ws.write(rr,1,name,F["set_lbl"])
            nf=F["td"] if name in ("TRIR","LTIFR") else F["tdn"]
            ws.write_formula(rr,2,"="+f,nf,0)
            self.wb.define_name(name,"=Calculations!$C$%d"%(rr+1)); rr+=1
        # closure metrics from HSE obs, training, corrective actions
        obs=spec_of("hseobs"); tr=spec_of("training"); ca=spec_of("ca")
        ws.write(rr,1,"ObsClosure",F["set_lbl"])
        ws.write_formula(rr,2,'=IFERROR(COUNTIFS(%s,"Closed",%s,mCrit,%s,dCrit)/COUNTIFS(%s,mCrit,%s,dCrit),0)*100'%(
            rng(obs,"Status"),rng(obs,"Month"),rng(obs,"Department"),rng(obs,"Month"),rng(obs,"Department")),F["td"],0)
        self.wb.define_name("ObsClosure","=Calculations!$C$%d"%(rr+1)); rr+=1
        ws.write(rr,1,"TrainCompliance",F["set_lbl"])
        ws.write_formula(rr,2,'=IFERROR(COUNTIFS(%s,"Completed",%s,mCrit,%s,dCrit)/COUNTIFS(%s,mCrit,%s,dCrit),0)*100'%(
            rng(tr,"Status"),rng(tr,"Month"),rng(tr,"Department"),rng(tr,"Month"),rng(tr,"Department")),F["td"],0)
        self.wb.define_name("TrainCompliance","=Calculations!$C$%d"%(rr+1)); rr+=1
        ws.write(rr,1,"CAClosure",F["set_lbl"])
        ws.write_formula(rr,2,'=IFERROR(COUNTIFS(%s,"Closed",%s,mCrit,%s,dCrit)/COUNTIFS(%s,mCrit,%s,dCrit),0)*100'%(
            rng(ca,"Status"),rng(ca,"Month"),rng(ca,"Department"),rng(ca,"Month"),rng(ca,"Department")),F["td"],0)
        self.wb.define_name("CAClosure","=Calculations!$C$%d"%(rr+1)); rr+=1

        # Heinrich pyramid table
        pr=r0+1; pc=5
        ws.write(pr-1,pc,"Incident Pyramid",F["th"]); ws.write(pr-1,pc+1,"Count",F["th"])
        pyr=[("Fatality","Fatality"),("Lost Time Injury","LostTime"),("Restricted Work","Restricted"),
             ("Medical Treatment","Medical"),("First Aid","FirstAid"),("Near Miss","NearMiss")]
        for i,(lbl,nm) in enumerate(pyr):
            ws.write(pr+i,pc,lbl,F["tdl"]); ws.write_formula(pr+i,pc+1,"="+nm,F["tdn"],0)
        # at-risk observations
        ua=spec_of("unsafeact"); uc=spec_of("unsafecond")
        ws.write(pr+6,pc,"At-Risk Observations",F["tdl"])
        ws.write_formula(pr+6,pc+1,'=COUNTIFS(%s,mCrit)+COUNTIFS(%s,mCrit)'%(rng(ua,"Month"),rng(uc,"Month")),F["tdn"],0)
        self.RR["_pyramid"]={"lbl":self._a1(pr,pc,pr+6),"val":self._a1(pr,pc+1,pr+6)}

        # 12-month incident trend
        tr_r=r0+10; tc=5
        ws.write(tr_r-1,tc,"Incident 12-Month Trend",F["th"])
        ws.write(tr_r,tc,"Month",F["th"]); ws.write(tr_r,tc+1,"Incidents",F["th"])
        for i,mn in enumerate(MONTHS):
            ws.write(tr_r+1+i,tc,mn,F["td"])
            ws.write_formula(tr_r+1+i,tc+1,'=COUNTIFS(%s,"%s",%s,dCrit)'%(Mn,mn,Dp),F["tdn"],0)
        self.RR["_inctrend"]={"lbl":self._a1(tr_r+1,tc,tr_r+12),"val":self._a1(tr_r+1,tc+1,tr_r+12)}

        # leading indicators
        lr=r0+1; lc=8
        ws.write(lr-1,lc,"Leading Indicator",F["th"]); ws.write(lr-1,lc+1,"Count",F["th"])
        lead=[("Observations","hseobs"),("Toolbox Talks","toolbox"),("Trainings","training"),
              ("Inspections","wpinsp"),("Audits","iaudit"),("Emergency Drills","drills"),("PTW Audits","ptwaudit")]
        for i,(lbl,k) in enumerate(lead):
            s=spec_of(k)
            ws.write(lr+i,lc,lbl,F["tdl"])
            ws.write_formula(lr+i,lc+1,'=COUNTIFS(%s,mCrit)'%(rng(s,"Month")),F["tdn"],0)
        self.RR["_leading"]={"lbl":self._a1(lr,lc,lr+6),"val":self._a1(lr,lc+1,lr+6)}

        # RAG scorecard
        gr=r0+12; gc=8
        ws.write(gr-1,gc,"RAG Scorecard",F["th"]); ws.write(gr-1,gc+1,"Actual",F["th"])
        ws.write(gr-1,gc+2,"Target",F["th"]); ws.write(gr-1,gc+3,"Status",F["th"])
        rag=[("TRIR","TRIR","TgtTRIR",True),("Obs Closure","ObsClosure","TgtObs",False),
             ("Training","TrainCompliance","TgtTrain",False),("CA Closure","CAClosure","TgtCA",False)]
        for i,(lbl,act,tgt,lowergood) in enumerate(rag):
            rrow=gr+i
            ws.write(rrow,gc,lbl,F["tdl"])
            # actual: closures are in %, target in fraction -> normalize
            if lowergood:
                ws.write_formula(rrow,gc+1,"="+act,F["td"],0)
                ws.write_formula(rrow,gc+2,"="+tgt,F["td"],0)
                ws.write_formula(rrow,gc+3,
                    '=IF(%s<=%s,"🟢 GREEN",IF(%s<=%s/AmberBand,"🟡 AMBER","🔴 RED"))'%(act,tgt,act,tgt),F["tdl"],0)
            else:
                ws.write_formula(rrow,gc+1,"=%s/100"%act,F["tdp"] if False else F["td"],0)
                ws.write_formula(rrow,gc+2,"="+tgt,F["td"],0)
                ws.write_formula(rrow,gc+3,
                    '=IF(%s/100>=%s,"🟢 GREEN",IF(%s/100>=%s*AmberBand,"🟡 AMBER","🔴 RED"))'%(act,tgt,act,tgt),F["tdl"],0)
        self.RR["_rag"]={"first":gr,"last":gr+3,"c":gc}

    def _exec_engine(self, ws, r0):
        """Period-aware executive engine: 12-month series + Cur/Prior masks + variance.
        Returns the next free row so callers can chain further calc blocks safely."""
        F=self.F
        inc=spec_of("incident"); Cls=rng(inc,"Classification"); IM=rng(inc,"Month")
        ID=rng(inc,"Department"); ILd=rng(inc,"Lost Days")
        # ---- month/mask matrix (cols B=1 name, C=2 no, D=3 curmask, E=4 priormask) ----
        mr=r0+2                    # first data row (0-indexed); header at mr-1
        ws.write(r0,1,"PERIOD ENGINE (current vs prior)",F["bodyb"])
        # control helpers
        ws.write(r0+1,1,"IsQuarter",F["set_lbl"]); ws.write_formula(r0+1,2,'=IF(LEFT(SelPeriod,1)="Q",1,0)',F["td"],0)
        isq="Calculations!$C$%d"%(r0+2)
        ws.write(r0+1,4,"CurQ",F["set_lbl"]); ws.write_formula(r0+1,5,
            '=IF(%s=1,VALUE(MID(SelPeriod,2,1)),ROUNDUP(MATCH(SelPeriod,L_Month,0)/3,0))'%isq,F["td"],0)
        curq="Calculations!$F$%d"%(r0+2)
        ws.write(r0+1,7,"CurMonthNo",F["set_lbl"]); ws.write_formula(r0+1,8,
            '=IF(%s=1,0,MATCH(SelPeriod,L_Month,0))'%isq,F["td"],0)
        curm="Calculations!$I$%d"%(r0+2)
        self.wb.define_name("CurMonthNo","="+curm)
        hr=mr+1
        for j,h in enumerate(["Month","No","Cur","Prior"]): ws.write(hr-1,1+j,h,F["th"])
        for i,mn in enumerate(MONTHS):
            rr=hr+i
            ws.write(rr,1,mn,F["td"]); ws.write_number(rr,2,i+1,F["td"])
            cc="$C$%d"%(rr+1)
            ws.write_formula(rr,3,'=IF(%s=1,IF(ROUNDUP(%s/3,0)=%s,1,0),IF(%s=%s,1,0))'%(isq,cc,curq,cc,curm),F["td"],0)
            ws.write_formula(rr,4,'=IF(%s=1,IF(ROUNDUP(%s/3,0)=%s-1,1,0),IF(%s=%s-1,1,0))'%(isq,cc,curq,cc,curm),F["td"],0)
        curmask="Calculations!$D$%d:$D$%d"%(hr+1,hr+12)
        prmask="Calculations!$E$%d:$E$%d"%(hr+1,hr+12)
        self._month_cat_range="Calculations!$B$%d:$B$%d"%(hr+1,hr+12)
        nmonths_cur="SUMPRODUCT(%s)"%curmask.replace("Calculations!","Calculations!")

        # ---- 12-month series matrix (col F=5 onward) ----
        scol={}; scol_col={}; c0=5
        def series(name, per_month):
            nonlocal c0
            ws.write(hr-1,c0,name,F["th"])
            for i,mn in enumerate(MONTHS):
                ws.write_formula(hr+i,c0,"="+per_month(mn),F["tdn"],0)
            scol[name]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12)
            scol_col[name]=xl_col_to_name(c0)
            c0+=1
        # incident classification counts
        def inc_cls(v): return lambda mn:'COUNTIFS(%s,"%s",%s,"%s",%s,dCrit)'%(Cls,v,IM,mn,ID)
        series("recordable", lambda mn:('COUNTIFS(%s,"Medical Treatment",%s,"%s",%s,dCrit)+COUNTIFS(%s,"Restricted Work",%s,"%s",%s,dCrit)'
            '+COUNTIFS(%s,"Lost Time Injury",%s,"%s",%s,dCrit)+COUNTIFS(%s,"Fatality",%s,"%s",%s,dCrit)')%(
            Cls,IM,mn,ID,Cls,IM,mn,ID,Cls,IM,mn,ID,Cls,IM,mn,ID))
        series("ltifat", lambda mn:'COUNTIFS(%s,"Lost Time Injury",%s,"%s",%s,dCrit)+COUNTIFS(%s,"Fatality",%s,"%s",%s,dCrit)'%(Cls,IM,mn,ID,Cls,IM,mn,ID))
        series("nearmiss", inc_cls("Near Miss"))
        series("firstaid", inc_cls("First Aid"))
        series("medical", inc_cls("Medical Treatment"))
        series("restricted", inc_cls("Restricted Work"))
        series("lti", inc_cls("Lost Time Injury"))
        series("fatality", inc_cls("Fatality"))
        series("lostdays", lambda mn:'SUMIFS(%s,%s,"%s",%s,dCrit)'%(ILd,IM,mn,ID))
        series("totalinc", lambda mn:'COUNTIFS(%s,"%s",%s,dCrit)'%(IM,mn,ID))
        # simple register monthly count (dept-filtered) helper
        def rcount(key, extra=""):
            s=spec_of(key)
            if has(s,"Department"):
                return lambda mn:'COUNTIFS(%s,"%s",%s,dCrit%s)'%(rng(s,"Month"),mn,rng(s,"Department"),extra%('' ) if "%s" in extra else extra)
            return lambda mn:'COUNTIFS(%s,"%s"%s)'%(rng(s,"Month"),mn,extra)
        def rstatus(key, statusheader, val):
            s=spec_of(key)
            dep=(",%s,dCrit"%rng(s,"Department")) if has(s,"Department") else ""
            return lambda mn:'COUNTIFS(%s,"%s",%s,"%s"%s)'%(rng(s,statusheader),val,rng(s,"Month"),mn,dep)
        def rsum(key, colname):
            s=spec_of(key)
            dep=(",%s,dCrit"%rng(s,"Department")) if has(s,"Department") else ""
            return lambda mn:'SUMIFS(%s,%s,"%s"%s)'%(rng(s,colname),rng(s,"Month"),mn,dep)
        def rsum2(key, c1, c2):
            s=spec_of(key)
            dep=(",%s,dCrit"%rng(s,"Department")) if has(s,"Department") else ""
            return lambda mn:'SUMIFS(%s,%s,"%s"%s)+SUMIFS(%s,%s,"%s"%s)'%(
                rng(s,c1),rng(s,"Month"),mn,dep,rng(s,c2),rng(s,"Month"),mn,dep)
        def rvalcount(key, colname, val):
            s=spec_of(key)
            dep=(",%s,dCrit"%rng(s,"Department")) if has(s,"Department") else ""
            return lambda mn:'COUNTIFS(%s,"%s",%s,"%s"%s)'%(rng(s,colname),val,rng(s,"Month"),mn,dep)
        series("disc", rcount("disc"))
        s_nc=spec_of("nc")
        series("nc_open", lambda mn:'COUNTIFS(%s,"Open",%s,"%s",%s,dCrit)+COUNTIFS(%s,"Overdue",%s,"%s",%s,dCrit)'%(
            rng(s_nc,"Status"),rng(s_nc,"Month"),mn,rng(s_nc,"Department"),rng(s_nc,"Status"),rng(s_nc,"Month"),mn,rng(s_nc,"Department")))
        series("training_total", rcount("training"))
        series("train_completed", rstatus("training","Status","Completed"))
        series("obs_total", rcount("hseobs"))
        series("obs_closed", rstatus("hseobs","Status","Completed"))
        series("toolbox", rcount("toolbox"))
        s_wp=spec_of("wpinsp"); s_eq=spec_of("eqinsp"); s_wk=spec_of("walk")
        series("inspections", lambda mn:'COUNTIFS(%s,"%s",%s,dCrit)+COUNTIFS(%s,"%s",%s,dCrit)+COUNTIFS(%s,"%s",%s,dCrit)'%(
            rng(s_wp,"Month"),mn,rng(s_wp,"Department"),rng(s_eq,"Month"),mn,rng(s_eq,"Department"),rng(s_wk,"Month"),mn,rng(s_wk,"Department")))
        s_ia=spec_of("iaudit"); s_ea=spec_of("eaudit")
        series("audits", lambda mn:'COUNTIFS(%s,"%s",%s,dCrit)+COUNTIFS(%s,"%s",%s,dCrit)'%(
            rng(s_ia,"Month"),mn,rng(s_ia,"Department"),rng(s_ea,"Month"),mn,rng(s_ea,"Department")))
        series("ptw_total", rcount("ptwaudit"))
        series("ptw_compliant", rstatus("ptwaudit","Verdict","Compliant"))
        s_dr=spec_of("drills")
        series("drills", lambda mn:'COUNTIFS(%s,"%s")'%(rng(s_dr,"Month"),mn))
        series("ca_total", rcount("ca"))
        series("ca_closed", rstatus("ca","Status","Completed"))
        series("jsa", rcount("jsa"))
        series("meetings", rcount("meetings"))
        s_ua=spec_of("unsafeact"); s_uc=spec_of("unsafecond")
        series("unsafe_reports", lambda mn:'COUNTIFS(%s,"%s",%s,dCrit)+COUNTIFS(%s,"%s",%s,dCrit)'%(
            rng(s_ua,"Month"),mn,rng(s_ua,"Department"),rng(s_uc,"Month"),mn,rng(s_uc,"Department")))
        # trend-chart-only series (Unsafe Act vs Condition, monthly TRIR/LTIFR)
        series("ua_m", rcount("unsafeact"))
        series("uc_m", rcount("unsafecond"))

        # ---- full tracker-coverage series (headline KPI per register) ----
        series("toolbox_att_actual", rsum("toolbox","Actual Attendees"))
        series("toolbox_att_target", rsum("toolbox","Target Attendees"))
        series("jsa_approved", rstatus("jsa","Approval Status","Approved"))
        series("wpinsp_total", rcount("wpinsp"))
        series("wpinsp_closed", rstatus("wpinsp","Status","Completed"))
        series("eqinsp_total", rcount("eqinsp"))
        series("eqinsp_critical", rsum("eqinsp","Critical Findings"))
        series("walk_total", rcount("walk"))
        series("meetings_raised", rsum("meetings","Action Items Raised"))
        series("meetings_closed", rsum("meetings","Actions Closed"))
        series("bulletins_total", rcount("bulletins"))
        series("bulletins_target", rsum("bulletins","Target Reach"))
        series("bulletins_actual", rsum("bulletins","Actual Reach"))
        series("drills_target", rsum("drills","Target Participants"))
        series("drills_actual", rsum("drills","Actual Participants"))
        series("iaudit_total", rcount("iaudit"))
        series("iaudit_nc", rsum2("iaudit","Minor NC","Major NC"))
        series("eaudit_total", rcount("eaudit"))
        series("eaudit_nc", rsum2("eaudit","Minor NC","Major NC"))
        series("mgmtvisit_total", rcount("mgmtvisit"))
        series("mgmtvisit_raised", rsum("mgmtvisit","Actions Raised"))
        series("mgmtvisit_closed", rsum("mgmtvisit","Actions Closed"))
        series("mgmtreview_total", rcount("mgmtreview"))
        series("mgmtreview_attended", rsum("mgmtreview","Members Attended"))
        series("mgmtreview_invited", rsum("mgmtreview","Members Invited"))
        series("awards_total", rcount("awards"))
        series("swa_total", rcount("swa"))
        series("alcohol_total", rcount("alcohol"))
        series("alcohol_positive", rvalcount("alcohol","Result","Positive"))
        series("unsafeact_total", rcount("unsafeact"))
        series("unsafeact_closed", rstatus("unsafeact","Status","Completed"))
        series("unsafecond_total", rcount("unsafecond"))
        series("unsafecond_closed", rstatus("unsafecond","Status","Completed"))
        series("nc_total", rcount("nc"))
        series("nc_closed", rstatus("nc","Status","Closed"))

        # ---- monthly series feeding each tracker's bespoke "signature" chart ----
        def ravg(key, colname):
            s=spec_of(key)
            dep=(",%s,dCrit"%rng(s,"Department")) if has(s,"Department") else ""
            return lambda mn:'IFERROR(AVERAGEIFS(%s,%s,"%s"%s),0)'%(rng(s,colname),rng(s,"Month"),mn,dep)
        series("hseobs_safe", lambda mn:'COUNTIFS(%s,"Safe Act",%s,"%s",%s,dCrit)+COUNTIFS(%s,"Safe Condition",%s,"%s",%s,dCrit)'%(
            rng(spec_of("hseobs"),"Observation Type"),rng(spec_of("hseobs"),"Month"),mn,rng(spec_of("hseobs"),"Department"),
            rng(spec_of("hseobs"),"Observation Type"),rng(spec_of("hseobs"),"Month"),mn,rng(spec_of("hseobs"),"Department")))
        series("hseobs_atrisk", lambda mn:'COUNTIFS(%s,"Unsafe Act",%s,"%s",%s,dCrit)+COUNTIFS(%s,"Unsafe Condition",%s,"%s",%s,dCrit)'%(
            rng(spec_of("hseobs"),"Observation Type"),rng(spec_of("hseobs"),"Month"),mn,rng(spec_of("hseobs"),"Department"),
            rng(spec_of("hseobs"),"Observation Type"),rng(spec_of("hseobs"),"Month"),mn,rng(spec_of("hseobs"),"Department")))
        series("drill_resp_actual", ravg("drills","Actual Response (min)"))
        series("drill_resp_target", ravg("drills","Target Response (min)"))
        series("iaudit_major", rsum("iaudit","Major NC"))
        series("eaudit_major", rsum("eaudit","Major NC"))
        series("mgmtreview_decisions", rsum("mgmtreview","Decisions Made"))
        series("mgmtreview_actions", rsum("mgmtreview","Actions Assigned"))
        series("swa_downtime", rsum("swa","Downtime (min)"))
        series("training_hours", rsum("training","Duration (hrs)"))
        series("wpinsp_nc", rsum("wpinsp","Non-Conformances"))
        series("ca_ontime", rvalcount("ca","Timeliness","On-Time"))
        series("ca_delayed", rvalcount("ca","Timeliness","Delayed"))
        series("jsa_critical", rvalcount("jsa","Risk Level","Critical"))
        series("jsa_high", rvalcount("jsa","Risk Level","High"))
        series("jsa_medium", rvalcount("jsa","Risk Level","Medium"))
        series("jsa_low", rvalcount("jsa","Risk Level","Low"))

        # monthly TRIR/LTIFR trend (direct per-month reference to recordable/ltifat columns)
        rc_col=scol_col["recordable"]; lf_col=scol_col["ltifat"]
        ws.write(hr-1,c0,"trir_m",F["th"])
        for i in range(12):
            ws.write_formula(hr+i,c0,"=IFERROR($%s$%d*TRIRmult/Settings!$C$%d,0)"%(rc_col,hr+1+i,self._mh_first+i),F["td"],0)
        scol["trir_m"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12); c0+=1
        ws.write(hr-1,c0,"ltifr_m",F["th"])
        for i in range(12):
            ws.write_formula(hr+i,c0,"=IFERROR($%s$%d*LTIFRmult/Settings!$C$%d,0)"%(lf_col,hr+1+i,self._mh_first+i),F["td"],0)
        scol["ltifr_m"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12); c0+=1
        # industry benchmark reference lines (flat, one repeated Settings value per month)
        ws.write(hr-1,c0,"bench_trir_m",F["th"])
        for i in range(12): ws.write_formula(hr+i,c0,"=BenchTRIR",F["td"],0)
        scol["bench_trir_m"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12); c0+=1
        ws.write(hr-1,c0,"bench_ltifr_m",F["th"])
        for i in range(12): ws.write_formula(hr+i,c0,"=BenchLTIFR",F["td"],0)
        scol["bench_ltifr_m"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12); c0+=1
        # alcohol positive-rate % trend (direct per-month reference to alcohol_positive/alcohol_total)
        ap_col=scol_col["alcohol_positive"]; at_col=scol_col["alcohol_total"]
        ws.write(hr-1,c0,"alcohol_rate_m",F["th"])
        for i in range(12):
            ws.write_formula(hr+i,c0,"=IFERROR($%s$%d/$%s$%d*100,0)"%(ap_col,hr+1+i,at_col,hr+1+i),F["tdp"],0)
        scol["alcohol_rate_m"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12); c0+=1

        # ---- Leading:Lagging ratio trend (pure column-arithmetic on already-built monthly series) ----
        def cellref(colname, mn):
            i=MONTHS.index(mn)
            return "$%s$%d"%(scol_col[colname], hr+1+i)
        leading_parts=["toolbox","training_total","obs_total","inspections","audits","drills","ptw_total","meetings","jsa"]
        lagging_parts=["totalinc","nc_total","disc"]
        ws.write(hr-1,c0,"leading_total",F["th"])
        for i,mn in enumerate(MONTHS):
            ws.write_formula(hr+i,c0,"="+"+".join(cellref(p,mn) for p in leading_parts),F["tdn"],0)
        scol["leading_total"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12)
        scol_col["leading_total"]=xl_col_to_name(c0); c0+=1
        ws.write(hr-1,c0,"lagging_total",F["th"])
        for i,mn in enumerate(MONTHS):
            ws.write_formula(hr+i,c0,"="+"+".join(cellref(p,mn) for p in lagging_parts),F["tdn"],0)
        scol["lagging_total"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12)
        scol_col["lagging_total"]=xl_col_to_name(c0); c0+=1
        ws.write(hr-1,c0,"leadlag_ratio",F["th"])
        for i,mn in enumerate(MONTHS):
            ws.write_formula(hr+i,c0,"=IFERROR(%s/%s,0)"%(cellref("leading_total",mn),cellref("lagging_total",mn)),F["td"],0)
        scol["leadlag_ratio"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12); c0+=1

        # ---- Target-vs-Actual forecast blocks: 12 actual months + a 13th "Next" point
        # projected with Excel's own TREND() (a real linear regression, not a fabricated number) ----
        FORECAST_PAIRS=[("toolbox_att_target","toolbox_att_actual","fc_toolbox"),
                        ("bulletins_target","bulletins_actual","fc_bulletins"),
                        ("drills_target","drills_actual","fc_drills"),
                        ("mgmtreview_invited","mgmtreview_attended","fc_mgmtreview")]
        fc_row=hr+14
        for tgt_name,act_name,tag in FORECAST_PAIRS:
            tgt_col=scol_col[tgt_name]; act_col=scol_col[act_name]
            ws.write(fc_row-1,c0,"Period",F["th"]); ws.write(fc_row-1,c0+1,"Target",F["th"]); ws.write(fc_row-1,c0+2,"Actual",F["th"])
            for i,mn in enumerate(MONTHS):
                ws.write(fc_row+i,c0,mn,F["td"])
                ws.write_formula(fc_row+i,c0+1,"=$%s$%d"%(tgt_col,hr+1+i),F["tdn"],0)
                ws.write_formula(fc_row+i,c0+2,"=$%s$%d"%(act_col,hr+1+i),F["tdn"],0)
            ws.write(fc_row+12,c0,"Next (fcst)",F["td"])
            actrange="$%s$%d:$%s$%d"%(act_col,hr+1,act_col,hr+12)
            xrange="{1,2,3,4,5,6,7,8,9,10,11,12}"
            ws.write_formula(fc_row+12,c0+1,"=$%s$%d"%(tgt_col,hr+12),F["tdn"],0)
            ws.write_formula(fc_row+12,c0+2,"=ROUND(TREND(%s,%s,13),0)"%(actrange,xrange),F["tdn"],0)
            lc=xl_col_to_name(c0); tc_=xl_col_to_name(c0+1); ac=xl_col_to_name(c0+2)
            scol[tag+"_lbl"]="Calculations!$%s$%d:$%s$%d"%(lc,fc_row+1,lc,fc_row+13)
            scol[tag+"_tgt"]="Calculations!$%s$%d:$%s$%d"%(tc_,fc_row+1,tc_,fc_row+13)
            scol[tag+"_act"]="Calculations!$%s$%d:$%s$%d"%(ac,fc_row+1,ac,fc_row+13)
            c0+=4

        self.MSER=scol   # expose monthly-series ranges for direct trend-chart reuse

        MH="Manhours"; nmc="SUM(%s)"%curmask; nmp="SUM(%s)"%prmask
        def sp(series_name,mask): return "SUMPRODUCT(%s,%s)"%(scol[series_name],mask)
        # ---- Exec KPI variance table ----
        kt=r0+2; kc=c0+2   # dynamic: placed just past the last monthly-series column
        ws.write(kt-1,kc,"Executive KPI (period variance)",F["bodyb"])
        heads=["KPI","Band","Cur","Prior","Delta%","Good"]
        for j,h in enumerate(heads): ws.write(kt,kc+j,h,F["th"])
        # (label, band, kind, polarity, kind_of_calc, args)
        # 8th field = explicit Settings target name, or None -> auto rolling-average baseline
        KP=[
         # ---- LAGGING (reactive outcomes; lower is better) ----
         ("TRIR","Lagging","dec",-1,"trir",None,None,"TgtTRIR"),
         ("LTIFR","Lagging","dec",-1,"ltifr",None,None,"TgtLTIFR"),
         ("Total Incidents","Lagging","num",-1,"sum","totalinc","Incident",None),
         ("Recordable","Lagging","num",-1,"sum","recordable","Incident",None),
         ("LTI + Fatality","Lagging","num",-1,"sum","ltifat","Incident",None),
         ("Near Miss","Lagging","num",-1,"sum","nearmiss","Incident",None),
         ("First Aid","Lagging","num",-1,"sum","firstaid","Incident",None),
         ("Lost Days","Lagging","num",-1,"sum","lostdays","Incident",None),
         ("Disciplinary","Lagging","num",-1,"sum","disc","Disciplinary Actions",None),
         ("Open NCs","Lagging","num",-1,"sum","nc_open","NC Management",None),
         ("NC Closure","Lagging","pct",1,"ratio",("nc_closed","nc_total"),"NC Management","TgtCloseout"),
         ("Alcohol Positive %","Lagging","pct",-1,"ratio",("alcohol_positive","alcohol_total"),"Alcohol Tests","TgtAlcoholPositive"),
         # ---- LEADING (proactive activity; higher is better) ----
         ("Toolbox Talks","Leading","num",1,"sum","toolbox","Toolbox Talks",None),
         ("Toolbox Avg Attendance","Leading","pct",1,"ratio",("toolbox_att_actual","toolbox_att_target"),"Toolbox Talks","TgtAttendance"),
         ("JSA Assessments","Leading","num",1,"sum","jsa","JSA Risk Assessment",None),
         ("JSA % Approved","Leading","pct",1,"ratio",("jsa_approved","jsa"),"JSA Risk Assessment","TgtCloseout"),
         ("Trainings","Leading","num",1,"sum","training_total","Training",None),
         ("Training Compliance","Leading","pct",1,"ratio",("train_completed","training_total"),"Training","TgtTrain"),
         ("HSE Observations","Leading","num",1,"sum","obs_total","HSE Observations",None),
         ("Obs Closure","Leading","pct",1,"ratio",("obs_closed","obs_total"),"HSE Observations","TgtObs"),
         ("Workplace Inspections","Leading","num",1,"sum","wpinsp_total","Workplace Inspections",None),
         ("Workplace Insp. Closure","Leading","pct",1,"ratio",("wpinsp_closed","wpinsp_total"),"Workplace Inspections","TgtCloseout"),
         ("Equipment Inspections","Leading","num",1,"sum","eqinsp_total","Equipment Inspections",None),
         ("Equipment Critical Findings","Leading","num",-1,"sum","eqinsp_critical","Equipment Inspections",None),
         ("Safety Walkthroughs","Leading","num",1,"sum","walk_total","Safety Walkthroughs",None),
         ("Safety Meetings","Leading","num",1,"sum","meetings","Safety Meetings",None),
         ("Meetings Close-out","Leading","pct",1,"ratio",("meetings_closed","meetings_raised"),"Safety Meetings","TgtCloseout"),
         ("Safety Bulletins","Leading","num",1,"sum","bulletins_total","Safety Bulletins",None),
         ("Bulletin Reach","Leading","pct",1,"ratio",("bulletins_actual","bulletins_target"),"Safety Bulletins","TgtCloseout"),
         ("Emergency Drills","Leading","num",1,"sum","drills","Emergency Drills",None),
         ("Drill Participation","Leading","pct",1,"ratio",("drills_actual","drills_target"),"Emergency Drills","TgtAttendance"),
         ("Internal Audits","Leading","num",1,"sum","iaudit_total","Internal Audits",None),
         ("Internal Audit NCs","Leading","num",-1,"sum","iaudit_nc","Internal Audits",None),
         ("External Audits","Leading","num",1,"sum","eaudit_total","External Audits",None),
         ("External Audit NCs","Leading","num",-1,"sum","eaudit_nc","External Audits",None),
         ("Management Visits","Leading","num",1,"sum","mgmtvisit_total","Management Visits",None),
         ("Mgmt Visit Close-out","Leading","pct",1,"ratio",("mgmtvisit_closed","mgmtvisit_raised"),"Management Visits","TgtCloseout"),
         ("Management Reviews","Leading","num",1,"sum","mgmtreview_total","Management Reviews",None),
         ("Mgmt Review Attendance","Leading","pct",1,"ratio",("mgmtreview_attended","mgmtreview_invited"),"Management Reviews","TgtAttendance"),
         ("Safety Awards","Leading","num",1,"sum","awards_total","Safety Awards",None),
         ("Stop Work Authority","Leading","num",1,"sum","swa_total","Stop Work Authority",None),
         ("Alcohol Tests","Leading","num",1,"sum","alcohol_total","Alcohol Tests",None),
         ("PTW Audits","Leading","num",1,"sum","ptw_total","PTW Audits",None),
         ("PTW Compliance","Leading","pct",1,"ratio",("ptw_compliant","ptw_total"),"PTW Audits","TgtPTW"),
         ("Corrective Actions","Leading","num",1,"sum","ca_total","Corrective Actions",None),
         ("CA Closure","Leading","pct",1,"ratio",("ca_closed","ca_total"),"Corrective Actions","TgtCA"),
         ("Unsafe Acts Reported","Leading","num",1,"sum","unsafeact_total","Unsafe Acts",None),
         ("Unsafe Act Closure","Leading","pct",1,"ratio",("unsafeact_closed","unsafeact_total"),"Unsafe Acts","TgtCloseout"),
         ("Unsafe Conditions Reported","Leading","num",1,"sum","unsafecond_total","Unsafe Conditions",None),
         ("Unsafe Condition Closure","Leading","pct",1,"ratio",("unsafecond_closed","unsafecond_total"),"Unsafe Conditions","TgtCloseout"),
        ]
        def calc(kind,args,mask,nm):
            if kind=="sum": return sp(args,mask)
            if kind=="ratio": return "IFERROR(%s/%s,0)*100"%(sp(args[0],mask),sp(args[1],mask))
            if kind=="trir": return "IFERROR(%s*TRIRmult/SUMPRODUCT(ManhoursM,%s),0)"%(sp("recordable",mask),mask)
            if kind=="ltifr": return "IFERROR(%s*LTIFRmult/SUMPRODUCT(ManhoursM,%s),0)"%(sp("ltifat",mask),mask)
        EX={}
        names={"TRIR":"TRIR","LTIFR":"LTIFR","Total Incidents":"TotalInc","Recordable":"Recordable",
               "Near Miss":"NearMiss","Lost Days":"LostDays","LTI + Fatality":"LTIfat",
               "Training Compliance":"TrainCompliance","Obs Closure":"ObsClosure","CA Closure":"CAClosure",
               "PTW Compliance":"PTWauditComp"}
        for i,(lbl,band,kind,pol,ck,args,drill,tgtname) in enumerate(KP):
            rr=kt+1+i
            ws.write(rr,kc,lbl,F["tdl"]); ws.write(rr,kc+1,band,F["td"])
            nf=F["td"] if kind=="dec" else (F["tdp"] if kind=="pct" else F["tdn"])
            ws.write_formula(rr,kc+2,"="+calc(ck,args,curmask,nmc),nf,0)
            ws.write_formula(rr,kc+3,"="+calc(ck,args,prmask,nmp),nf,0)
            cur="$%s$%d"%(xl_col_to_name(kc+2),rr+1); pri="$%s$%d"%(xl_col_to_name(kc+3),rr+1)
            ws.write_formula(rr,kc+4,"=IFERROR((%s-%s)/%s,IF(%s>0,1,0))"%(cur,pri,pri,cur),F["tdp"],0)
            ws.write_formula(rr,kc+5,"=(%s-%s)*%d"%(cur,pri,pol),F["td"],0)
            goodcell="Calculations!$%s$%d"%(xl_col_to_name(kc+5),rr+1)
            gname="gd"+"".join(ch for ch in lbl if ch.isalnum())
            self.wb.define_name(gname,"="+goodcell)
            # ---- Target (explicit corporate target, or auto rolling 12-month baseline) + RAG code ----
            if tgtname:
                tgtformula = tgtname if kind=="dec" else "%s*100"%tgtname
            else:
                tgtformula = "IFERROR(AVERAGE(%s)*SUM(%s),0)"%(scol[args],curmask)
            ws.write_formula(rr,kc+6,"="+tgtformula,nf,0)
            tgt="$%s$%d"%(xl_col_to_name(kc+6),rr+1)
            if pol==1:
                ragf='IF(%s>=%s,2,IF(%s>=%s*AmberBand,1,0))'%(cur,tgt,cur,tgt)
            else:
                ragf='IF(%s<=%s,2,IF(%s<=%s/AmberBand,1,0))'%(cur,tgt,cur,tgt)
            ws.write_formula(rr,kc+7,"=IFERROR(%s,1)"%ragf,F["td"],0)
            ragcell="Calculations!$%s$%d"%(xl_col_to_name(kc+7),rr+1)
            ragname="rg"+"".join(ch for ch in lbl if ch.isalnum())
            self.wb.define_name(ragname,"="+ragcell)
            EX[lbl]={"cur":"Calculations!%s"%cur,"prior":"Calculations!%s"%pri,
                     "delta":"Calculations!$%s$%d"%(xl_col_to_name(kc+4),rr+1),
                     "good":goodcell,"goodname":gname,"target":"Calculations!%s"%tgt,
                     "rag":ragcell,"ragname":ragname,"band":band,"kind":kind,"drill":drill}
            if lbl in names: self.wb.define_name(names[lbl],"=Calculations!%s"%cur)
        self.EX=EX
        # ---- gauge helper cells (value/2, remainder, hidden 50) ----
        gauges=[("Training",EX["Training Compliance"]["cur"]),("PTW Audit",EX["PTW Compliance"]["cur"]),
                ("Obs Closure",EX["Obs Closure"]["cur"]),("CA Closure",EX["CA Closure"]["cur"]),
                ("Inspection",EX["Workplace Insp. Closure"]["cur"]),
                ("Statutory",EX["NC Closure"]["cur"])]
        g0=kt+1+len(KP)+3   # dynamic: sit just below the (now much longer) KPI table
        ws.write(g0-1,kc,"Gauge helpers",F["bodyb"])
        self.GAUGE={}
        for i,(nm,cur) in enumerate(gauges):
            grow=g0+i
            ws.write(grow,kc,nm,F["tdl"])
            ws.write_formula(grow,kc+1,"=MIN(100,%s)/2"%cur,F["td"],0)
            vcell="$%s$%d"%(xl_col_to_name(kc+1),grow+1)
            ws.write_formula(grow,kc+2,"=50-%s"%vcell,F["td"],0)
            ws.write_number(grow,kc+3,50,F["td"])
            self.GAUGE[nm]={"range":"Calculations!$%s$%d:$%s$%d"%(
                xl_col_to_name(kc+1),grow+1,xl_col_to_name(kc+3),grow+1),"val":cur}
        # pyramid (current period), leading & lagging bars, 12-month trend, RAG
        py=[("Fatality","fatality"),("Lost Time Injury","lti"),("Restricted Work","restricted"),
            ("Medical Treatment","medical"),("First Aid","firstaid"),("Near Miss","nearmiss")]
        pr=kt; pc=kc+9   # +9 leaves room for the Target(+6)/RAGCode(+7) columns just added
        ws.write(pr-1,pc,"Incident Pyramid (period)",F["th"]); ws.write(pr-1,pc+1,"Count",F["th"])
        for i,(l,s) in enumerate(py):
            ws.write(pr+i,pc,l,F["tdl"]); ws.write_formula(pr+i,pc+1,"="+sp(s,curmask),F["tdn"],0)
        ws.write(pr+6,pc,"At-Risk Obs",F["tdl"]); ws.write_formula(pr+6,pc+1,"="+sp("unsafe_reports",curmask),F["tdn"],0)
        self.RR["_pyramid"]={"lbl":self._a1(pr,pc,pr+6),"val":self._a1(pr,pc+1,pr+6)}
        # leading vs lagging bars (current period)
        lead=[("Toolbox","toolbox"),("Trainings","training_total"),("Observations","obs_total"),
              ("Inspections","inspections"),("Audits","audits"),("Drills","drills"),
              ("PTW Audits","ptw_total"),("Meetings","meetings"),("JSA","jsa")]
        lr=pr+9
        ws.write(lr-1,pc,"Leading Activity",F["th"]); ws.write(lr-1,pc+1,"Count",F["th"])
        for i,(l,s) in enumerate(lead):
            ws.write(lr+i,pc,l,F["tdl"]); ws.write_formula(lr+i,pc+1,"="+sp(s,curmask),F["tdn"],0)
        self.RR["_leading"]={"lbl":self._a1(lr,pc,lr+len(lead)-1),"val":self._a1(lr,pc+1,lr+len(lead)-1)}
        lag=[("Total Inc","totalinc"),("Recordable","recordable"),("Near Miss","nearmiss"),
             ("First Aid","firstaid"),("LTI+Fatal","ltifat"),("Lost Days","lostdays"),
             ("Disciplinary","disc"),("Open NC","nc_open")]
        gr=lr+len(lead)+2
        ws.write(gr-1,pc,"Lagging Outcome",F["th"]); ws.write(gr-1,pc+1,"Count",F["th"])
        for i,(l,s) in enumerate(lag):
            ws.write(gr+i,pc,l,F["tdl"]); ws.write_formula(gr+i,pc+1,"="+sp(s,curmask),F["tdn"],0)
        self.RR["_lagging"]={"lbl":self._a1(gr,pc,gr+len(lag)-1),"val":self._a1(gr,pc+1,gr+len(lag)-1)}
        # 12-month incident trend (full year, dept filtered)
        tc=pc+3
        ws.write(pr-1,tc,"Incident Trend",F["th"]); ws.write(pr-1,tc+1,"Inc",F["th"])
        for i,mn in enumerate(MONTHS):
            ws.write(pr+i-1+1,tc,mn,F["td"]) if False else None
        tr_r=pr
        for i,mn in enumerate(MONTHS):
            ws.write(tr_r+i,tc,mn,F["td"])
            ws.write_formula(tr_r+i,tc+1,'=COUNTIFS(%s,"%s",%s,dCrit)'%(IM,mn,ID),F["tdn"],0)
        self.RR["_inctrend"]={"lbl":self._a1(tr_r,tc,tr_r+11),"val":self._a1(tr_r,tc+1,tr_r+11)}
        # RAG scorecard (6 metrics, matching the 6 gauges)
        rg=gr+len(lag)+2; rc=pc
        ws.write(rg-1,rc,"RAG",F["th"]); ws.write(rg-1,rc+1,"Act",F["th"]); ws.write(rg-1,rc+2,"Tgt",F["th"]); ws.write(rg-1,rc+3,"Status",F["th"])
        rag=[("TRIR","TRIR","TgtTRIR",True),("Obs Closure","ObsClosure","TgtObs",False),
             ("Training","TrainCompliance","TgtTrain",False),("CA Closure","CAClosure","TgtCA",False),
             ("Workplace Insp. Closure",EX["Workplace Insp. Closure"]["cur"],"TgtObs",False),
             ("PTW Compliance","PTWauditComp","TgtObs",False)]
        for i,(l,act,tgt,low) in enumerate(rag):
            rr=rg+i; ws.write(rr,rc,l,F["tdl"])
            if low:
                ws.write_formula(rr,rc+1,"="+act,F["td"],0); ws.write_formula(rr,rc+2,"="+tgt,F["td"],0)
                ws.write_formula(rr,rc+3,'=IF(%s<=%s,"🟢 GREEN",IF(%s<=%s/AmberBand,"🟡 AMBER","🔴 RED"))'%(act,tgt,act,tgt),F["tdl"],0)
            else:
                ws.write_formula(rr,rc+1,"=%s/100"%act,F["td"],0); ws.write_formula(rr,rc+2,"="+tgt,F["td"],0)
                ws.write_formula(rr,rc+3,'=IF(%s/100>=%s,"🟢 GREEN",IF(%s/100>=%s*AmberBand,"🟡 AMBER","🔴 RED"))'%(act,tgt,act,tgt),F["tdl"],0)
        self.RR["_rag"]={"first":rg,"last":rg+len(rag)-1,"c":rc}

        # ---- sparkline source series for every KPI card (12-month trend) ----
        sc0 = tc + 3
        for i,(lbl,band,kind,pol,ck,args,drill,tgtname) in enumerate(KP):
            if ck=="sum":
                self.EX[lbl]["spark"] = scol[args]
            elif ck=="trir":
                self.EX[lbl]["spark"] = scol["trir_m"]
            elif ck=="ltifr":
                self.EX[lbl]["spark"] = scol["ltifr_m"]
            elif ck=="ratio":
                numcol=scol[args[0]]; dencol=scol[args[1]]
                ws.write(hr-1,sc0,lbl[:24],F["th"])
                for j in range(12):
                    ncell="$%s$%d"%(numcol.split("$")[1],hr+1+j)
                    dcell="$%s$%d"%(dencol.split("$")[1],hr+1+j)
                    ws.write_formula(hr+j,sc0,"=IFERROR(%s/%s*100,0)"%(ncell,dcell),F["td"],0)
                self.EX[lbl]["spark"]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(sc0),hr+1,xl_col_to_name(sc0),hr+12)
                sc0+=1

        # ---- Top Movers ranking (delta% x polarity, normalised & comparable across all KPIs) ----
        mv0=g0+8; mvc=kc
        ws.write(mv0-1,mvc,"KPI",F["th"]); ws.write(mv0-1,mvc+1,"MoveScore",F["th"]); ws.write(mv0-1,mvc+2,"Adj",F["th"])
        for i,(lbl,band,kind,pol,ck,args,drill,tgtname) in enumerate(KP):
            rr=mv0+i
            ws.write(rr,mvc,lbl,F["tdl"])
            ws.write_formula(rr,mvc+1,"=%s*%d"%(self.EX[lbl]["delta"],pol),F["td"],0)
            ws.write_formula(rr,mvc+2,"=%s+ROW()/100000"%xl_rowcol_to_cell(rr,mvc+1),self._numfmt("0.00000"),0)
        af=xl_rowcol_to_cell(mv0,mvc+2,True,True); al=xl_rowcol_to_cell(mv0+len(KP)-1,mvc+2,True,True)
        nf_=xl_rowcol_to_cell(mv0,mvc,True,True); nl=xl_rowcol_to_cell(mv0+len(KP)-1,mvc,True,True)
        vf=xl_rowcol_to_cell(mv0,mvc+1,True,True); vl=xl_rowcol_to_cell(mv0+len(KP)-1,mvc+1,True,True)
        best0=mv0+len(KP)+2; ws.write(best0-1,mvc,"Top 3 Improved",F["th"]); ws.write(best0-1,mvc+1,"Δ%",F["th"])
        for k in range(3):
            rr=best0+k; large="LARGE(%s:%s,%d)"%(af,al,k+1)
            ws.write_formula(rr,mvc,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf_,nl,large,af,al),F["tdl"],0)
            ws.write_formula(rr,mvc+1,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(vf,vl,large,af,al),self._numfmt('+0.0%;-0.0%'),0)
        worst0=best0+4; ws.write(worst0-1,mvc,"Top 3 Regressed",F["th"]); ws.write(worst0-1,mvc+1,"Δ%",F["th"])
        for k in range(3):
            rr=worst0+k; small="SMALL(%s:%s,%d)"%(af,al,k+1)
            ws.write_formula(rr,mvc,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf_,nl,small,af,al),F["tdl"],0)
            ws.write_formula(rr,mvc+1,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(vf,vl,small,af,al),self._numfmt('+0.0%;-0.0%'),0)
        self.RR["_movers_best"]={"lbl":self._a1(best0,mvc,best0+2),"val":self._a1(best0,mvc+1,best0+2)}
        self.RR["_movers_worst"]={"lbl":self._a1(worst0,mvc,worst0+2),"val":self._a1(worst0,mvc+1,worst0+2)}

        # ---- next free row for chained calc blocks (max of all sub-block bottoms) ----
        bottom = max(g0+6, kt+1+len(KP), rg+len(rag), worst0+2)
        return bottom + 3

    def _exec_analytics(self, ws, r0):
        """Cross-tracker analytics (Register-Month + Department filtered, via mCrit/dCrit):
        Root-Cause Pareto, Department Safety Score, Risk Heat Map, Top-10 Unsafe Acts/
        Conditions/Areas, and a compliance Radar (period-based, reusing EX cur cells).
        Returns the next free row."""
        F=self.F; EX=self.EX
        inc=spec_of("incident")
        c0=1
        ws.merge_range(r0,c0,r0,c0+9,"CROSS-TRACKER ANALYTICS  (filtered by Register Month & Department)",F["bodyb"])
        r=r0+2

        # ---- Root Cause Pareto (Incident, 8 causes) ----
        RC=rng(inc,"Root Cause")
        causes=HD.ROOT_CAUSES
        p0=r
        ws.write(p0-1,c0,"Root Cause",F["th"]); ws.write(p0-1,c0+1,"Count",F["th"])
        ws.write(p0-1,c0+2,"Adj",F["th"]); ws.write(p0-1,c0+3,"Sorted Cause",F["th"])
        ws.write(p0-1,c0+4,"Sorted Count",F["th"]); ws.write(p0-1,c0+5,"Cumulative %",F["th"])
        for i,c in enumerate(causes):
            rr=p0+i
            ws.write(rr,c0,c,F["tdl"])
            ws.write_formula(rr,c0+1,'=COUNTIFS(%s,"%s",%s,mCrit,%s,dCrit)'%(RC,c,rng(inc,"Month"),rng(inc,"Department")),F["tdn"],0)
            ws.write_formula(rr,c0+2,"=%s+ROW()/100000"%xl_rowcol_to_cell(rr,c0+1),self._numfmt("0.00000"),0)
        af=xl_rowcol_to_cell(p0,c0+2,True,True); al=xl_rowcol_to_cell(p0+len(causes)-1,c0+2,True,True)
        nf_=xl_rowcol_to_cell(p0,c0,True,True); nl=xl_rowcol_to_cell(p0+len(causes)-1,c0,True,True)
        cf=xl_rowcol_to_cell(p0,c0+1,True,True); cl_=xl_rowcol_to_cell(p0+len(causes)-1,c0+1,True,True)
        for i in range(len(causes)):
            rr=p0+i; k=i+1
            large="LARGE(%s:%s,%d)"%(af,al,k)
            ws.write_formula(rr,c0+3,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf_,nl,large,af,al),F["tdl"],0)
            ws.write_formula(rr,c0+4,"=INT(%s)"%large,F["tdn"],0)
            sc_first=xl_rowcol_to_cell(p0,c0+4,True,True); sc_this=xl_rowcol_to_cell(rr,c0+4,True,False)
            ws.write_formula(rr,c0+5,"=IFERROR(SUM(%s:%s)/SUM(%s:%s)*100,0)"%(sc_first,sc_this,cf,cl_),self._numfmt('0.0"%"'),0)
        sc=xl_col_to_name(c0+3); vc=xl_col_to_name(c0+4); pc_=xl_col_to_name(c0+5)
        self.RR["_pareto_lbl"]="Calculations!$%s$%d:$%s$%d"%(sc,p0+1,sc,p0+len(causes))
        self.RR["_pareto_val"]="Calculations!$%s$%d:$%s$%d"%(vc,p0+1,vc,p0+len(causes))
        self.RR["_pareto_cum"]="Calculations!$%s$%d:$%s$%d"%(pc_,p0+1,pc_,p0+len(causes))
        r=p0+len(causes)+2

        # ---- Department Safety Score ----
        d0=r; depts=HD.DEPARTMENTS
        ws.write(d0-1,c0,"Department",F["th"]); ws.write(d0-1,c0+1,"Score",F["th"])
        ws.write(d0-1,c0+2,"Recordable",F["th"]); ws.write(d0-1,c0+3,"Near Miss",F["th"])
        IClsD=rng(inc,"Classification"); IMD=rng(inc,"Month"); IDD=rng(inc,"Department")
        nm_sp=spec_of("nearmiss") if False else None
        for i,d in enumerate(depts):
            rr=d0+i
            ws.write(rr,c0,d,F["tdl"])
            recd=('COUNTIFS(%s,"Lost Time Injury",%s,mCrit,%s,"%s")+COUNTIFS(%s,"Medical Treatment",%s,mCrit,%s,"%s")'
                  '+COUNTIFS(%s,"Restricted Work",%s,mCrit,%s,"%s")+COUNTIFS(%s,"Fatality",%s,mCrit,%s,"%s")')%(
                IClsD,IMD,IDD,d,IClsD,IMD,IDD,d,IClsD,IMD,IDD,d,IClsD,IMD,IDD,d)
            uad=rng(spec_of("unsafeact"),"Department"); uam=rng(spec_of("unsafeact"),"Month")
            ucd=rng(spec_of("unsafecond"),"Department"); ucm=rng(spec_of("unsafecond"),"Month")
            nmd='COUNTIFS(%s,mCrit,%s,"%s")+COUNTIFS(%s,mCrit,%s,"%s")'%(uam,uad,d,ucm,ucd,d)
            ws.write_formula(rr,c0+2,"="+recd,F["tdn"],0)
            ws.write_formula(rr,c0+3,"="+nmd,F["tdn"],0)
            ws.write_formula(rr,c0+1,"=MAX(45,MIN(100,ROUND(100-%s*8-%s*1.5,0)))"%(
                xl_rowcol_to_cell(rr,c0+2),xl_rowcol_to_cell(rr,c0+3)),F["tdn"],0)
        dc=xl_col_to_name(c0); ssc=xl_col_to_name(c0+1)
        self.RR["_dept_lbl"]="Calculations!$%s$%d:$%s$%d"%(dc,d0+1,dc,d0+len(depts))
        self.RR["_dept_val"]="Calculations!$%s$%d:$%s$%d"%(ssc,d0+1,ssc,d0+len(depts))
        r=d0+len(depts)+2

        # ---- Risk Heat Map (Risk Rating x Department, Incident register) ----
        h0=r
        ws.write(h0-1,c0,"L \\ Dept",F["th"])
        topdepts=depts[:6]
        for j,d in enumerate(topdepts): ws.write(h0-1,c0+1+j,d[:8],F["th"])
        levels=["Critical","High","Medium","Low"]
        IR=rng(inc,"Risk Rating")
        for i,lvl in enumerate(levels):
            rr=h0+i
            ws.write(rr,c0,lvl,F["th"])
            for j,d in enumerate(topdepts):
                ws.write_formula(rr,c0+1+j,'=COUNTIFS(%s,"%s",%s,mCrit,%s,"%s")'%(IR,lvl,IMD,IDD,d),F["heat"],0)
        first=xl_rowcol_to_cell(h0,c0+1); last=xl_rowcol_to_cell(h0+3,c0+len(topdepts))
        ws.conditional_format("%s:%s"%(first,last),{"type":"3_color_scale",
            "min_color":GREEN_L,"mid_color":"#FEF08A","max_color":RED})
        self.RR["_heat_range"]="Calculations!%s:%s"%(first,last)
        r=h0+5

        # ---- Top-10 Unsafe Acts / Unsafe Conditions / High-Risk Areas ----
        r=self._top10_block(ws,r,c0,"Unsafe Act",spec_of("unsafeact"),"Description",HD.UNSAFE_ACT_TYPES,"_topact")
        r=self._top10_block(ws,r,c0,"Unsafe Condition",spec_of("unsafecond"),"Description",HD.UNSAFE_COND_TYPES,"_topcond")
        r=self._top10_block(ws,r,c0,"High-Risk Area",inc,"Area",HD.LOCATIONS,"_toparea")

        # ---- Compliance Radar (period-based; Actual + Target rings from EX cur/target cells) ----
        rd0=r
        ws.write(rd0-1,c0,"Radar Metric",F["th"]); ws.write(rd0-1,c0+1,"Actual",F["th"]); ws.write(rd0-1,c0+2,"Target",F["th"])
        radar=[("Training",EX["Training Compliance"]),("PTW Audit",EX["PTW Compliance"]),
               ("HSE Observations",EX["Obs Closure"]),("Workplace Insp.",EX["Workplace Insp. Closure"]),
               ("Corrective Actions",EX["CA Closure"]),("NC Mgmt",EX["NC Closure"]),
               ("Bulletin Reach",EX["Bulletin Reach"]),("Unsafe Act Closure",EX["Unsafe Act Closure"])]
        for i,(lbl,exd) in enumerate(radar):
            ws.write(rd0+i,c0,lbl,F["tdl"])
            ws.write_formula(rd0+i,c0+1,"="+exd["cur"],F["tdp"],0)
            ws.write_formula(rd0+i,c0+2,"="+exd["target"],F["tdp"],0)
        rl=xl_col_to_name(c0); rv=xl_col_to_name(c0+1); rt=xl_col_to_name(c0+2)
        self.RR["_radar_lbl"]="Calculations!$%s$%d:$%s$%d"%(rl,rd0+1,rl,rd0+len(radar))
        self.RR["_radar_val"]="Calculations!$%s$%d:$%s$%d"%(rv,rd0+1,rv,rd0+len(radar))
        self.RR["_radar_tgt"]="Calculations!$%s$%d:$%s$%d"%(rt,rd0+1,rt,rd0+len(radar))
        r=rd0+len(radar)+2

        # ---- per-tracker "signature chart" aggregates (Register-Month + Department filtered) ----
        # Bulletin reach % by Distribution Method
        b0=r; sb=spec_of("bulletins")
        ws.write(b0-1,c0,"Distribution Method",F["th"]); ws.write(b0-1,c0+1,"Avg Reach %",F["th"])
        for i,v in enumerate(HD.POOLS["Distribution Method"]):
            ws.write(b0+i,c0,v,F["tdl"])
            ws.write_formula(b0+i,c0+1,'=IFERROR(AVERAGEIFS(%s,%s,"%s",%s,mCrit),0)'%(
                rng(sb,"Reach %"),rng(sb,"Distribution Method"),v,rng(sb,"Month")),F["tdp"],0)
        self.RR["_bulletin_method_lbl"]=self._a1(b0,c0,b0+3); self.RR["_bulletin_method_val"]=self._a1(b0,c0+1,b0+3)
        r=b0+6

        # PTW compliance % by Permit Type
        p0=r; sp_=spec_of("ptwaudit")
        ws.write(p0-1,c0,"Permit Type",F["th"]); ws.write(p0-1,c0+1,"Avg Compliance %",F["th"])
        for i,v in enumerate(HD.POOLS["Permit Type Audited"]):
            ws.write(p0+i,c0,v,F["tdl"])
            ws.write_formula(p0+i,c0+1,'=IFERROR(AVERAGEIFS(%s,%s,"%s",%s,mCrit),0)'%(
                rng(sp_,"Compliance %"),rng(sp_,"Permit Type Audited"),v,rng(sp_,"Month")),F["tdp"],0)
        self.RR["_ptw_type_lbl"]=self._a1(p0,c0,p0+6); self.RR["_ptw_type_val"]=self._a1(p0,c0+1,p0+6)
        r=p0+9

        # Training pass rate % by Training Type
        t0=r; st=spec_of("training")
        ws.write(t0-1,c0,"Training Type",F["th"]); ws.write(t0-1,c0+1,"Pass Rate %",F["th"])
        for i,v in enumerate(HD.POOLS["Training Type"]):
            ws.write(t0+i,c0,v,F["tdl"])
            passc='COUNTIFS(%s,"%s",%s,"Pass",%s,mCrit)'%(rng(st,"Training Type"),v,rng(st,"Assessment Result"),rng(st,"Month"))
            totc='COUNTIFS(%s,"%s",%s,mCrit)'%(rng(st,"Training Type"),v,rng(st,"Month"))
            ws.write_formula(t0+i,c0+1,'=IFERROR(%s/%s*100,0)'%(passc,totc),F["tdp"],0)
        self.RR["_train_type_lbl"]=self._a1(t0,c0,t0+5); self.RR["_train_type_val"]=self._a1(t0,c0+1,t0+5)
        r=t0+8

        # Stop Work: avg Downtime by Severity
        s0=r; ssw=spec_of("swa")
        ws.write(s0-1,c0,"Severity",F["th"]); ws.write(s0-1,c0+1,"Avg Downtime (min)",F["th"])
        for i,v in enumerate(HD.SEVERITY):
            ws.write(s0+i,c0,v,F["tdl"])
            ws.write_formula(s0+i,c0+1,'=IFERROR(AVERAGEIFS(%s,%s,"%s",%s,mCrit),0)'%(
                rng(ssw,"Downtime (min)"),rng(ssw,"Severity"),v,rng(ssw,"Month")),F["tdn"],0)
        self.RR["_swa_severity_lbl"]=self._a1(s0,c0,s0+3); self.RR["_swa_severity_val"]=self._a1(s0,c0+1,s0+3)
        r=s0+6

        # NC Management: Root Cause Pareto (now a real cause pool, fixed in hse_data.py)
        r=self._top10_block(ws,r,c0,"NC Root Cause",spec_of("nc"),"Root Cause / CAPA",HD.ROOT_CAUSES,"_ncroot")
        # Workplace Inspections: NC-heavy Areas (top 8 by Non-Conformances sum, not just count)
        wa0=r; swp=spec_of("wpinsp")
        ws.write(wa0-1,c0,"Inspection Area",F["th"]); ws.write(wa0-1,c0+1,"Non-Conformances",F["th"])
        ws.write(wa0-1,c0+2,"Adj",F["th"]); ws.write(wa0-1,c0+3,"Sorted Area",F["th"]); ws.write(wa0-1,c0+4,"Sorted NCs",F["th"])
        areas8=HD.TOPICS[:8]
        for i,a in enumerate(areas8):
            ws.write(wa0+i,c0,a,F["tdl"])
            ws.write_formula(wa0+i,c0+1,'=SUMIFS(%s,%s,"%s",%s,mCrit,%s,dCrit)'%(
                rng(swp,"Non-Conformances"),rng(swp,"Inspection Area/Item"),a,rng(swp,"Month"),rng(swp,"Department")),F["tdn"],0)
            ws.write_formula(wa0+i,c0+2,"=%s+ROW()/100000"%xl_rowcol_to_cell(wa0+i,c0+1),self._numfmt("0.00000"),0)
        waf=xl_rowcol_to_cell(wa0,c0+2,True,True); wal=xl_rowcol_to_cell(wa0+7,c0+2,True,True)
        wnf=xl_rowcol_to_cell(wa0,c0,True,True); wnl=xl_rowcol_to_cell(wa0+7,c0,True,True)
        for i in range(8):
            rr=wa0+i; large="LARGE(%s:%s,%d)"%(waf,wal,i+1)
            ws.write_formula(rr,c0+3,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(wnf,wnl,large,waf,wal),F["tdl"],0)
            ws.write_formula(rr,c0+4,"=INT(%s)"%large,F["tdn"],0)
        self.RR["_wpinsp_area_lbl"]=self._a1(wa0,c0+3,wa0+7); self.RR["_wpinsp_area_val"]=self._a1(wa0,c0+4,wa0+7)
        r=wa0+10

        # Incident: ageing buckets (open incidents only) + Person Type mix
        a0=r; sinc=spec_of("incident")
        ws.write(a0-1,c0,"Ageing Bucket (open)",F["th"]); ws.write(a0-1,c0+1,"Count",F["th"])
        buckets=[("0-7 days",0,7),("8-15 days",8,15),("16-30 days",16,30),("31+ days",31,None)]
        AG=rng(sinc,"Ageing (Days)"); IST=rng(sinc,"Status"); IMn=rng(sinc,"Month"); IDp=rng(sinc,"Department")
        for i,(lbl,lo,hi) in enumerate(buckets):
            ws.write(a0+i,c0,lbl,F["tdl"])
            if hi is None:
                f='COUNTIFS(%s,"Open",%s,">=%d",%s,mCrit,%s,dCrit)'%(IST,AG,lo,IMn,IDp)
            else:
                f='COUNTIFS(%s,"Open",%s,">=%d",%s,"<=%d",%s,mCrit,%s,dCrit)'%(IST,AG,lo,AG,hi,IMn,IDp)
            ws.write_formula(a0+i,c0+1,"="+f,F["tdn"],0)
        self.RR["_incident_aging_lbl"]=self._a1(a0,c0,a0+3); self.RR["_incident_aging_val"]=self._a1(a0,c0+1,a0+3)
        r=a0+6
        pt0=r
        ws.write(pt0-1,c0,"Person Type",F["th"]); ws.write(pt0-1,c0+1,"Count",F["th"])
        for i,v in enumerate(HD.POOLS["Person Type"]):
            ws.write(pt0+i,c0,v,F["tdl"])
            ws.write_formula(pt0+i,c0+1,'=COUNTIFS(%s,"%s",%s,mCrit,%s,dCrit)'%(
                rng(sinc,"Person Type"),v,IMn,IDp),F["tdn"],0)
        self.RR["_incident_persontype_lbl"]=self._a1(pt0,c0,pt0+3); self.RR["_incident_persontype_val"]=self._a1(pt0,c0+1,pt0+3)
        r=pt0+6

        # Toolbox: Topic x Department heat-map
        tb0=r; stb=spec_of("toolbox")
        topics=HD.TOPICS[:8]; topdepts2=HD.DEPARTMENTS[:6]
        ws.write(tb0-1,c0,"Topic \\ Dept",F["th"])
        for j,d in enumerate(topdepts2): ws.write(tb0-1,c0+1+j,d[:8],F["th"])
        for i,tp in enumerate(topics):
            ws.write(tb0+i,c0,tp,F["tdl"])
            for j,d in enumerate(topdepts2):
                ws.write_formula(tb0+i,c0+1+j,'=COUNTIFS(%s,"%s",%s,"%s",%s,mCrit)'%(
                    rng(stb,"Topic"),tp,rng(stb,"Department"),d,rng(stb,"Month")),F["heat"],0)
        tfirst=xl_rowcol_to_cell(tb0,c0+1); tlast=xl_rowcol_to_cell(tb0+len(topics)-1,c0+len(topdepts2))
        ws.conditional_format("%s:%s"%(tfirst,tlast),{"type":"3_color_scale",
            "min_color":WHITE,"mid_color":BLUE_L,"max_color":BLUE_D})
        self.RR["_toolbox_heat_range"]="Calculations!%s:%s"%(tfirst,tlast)
        self.RR["_toolbox_heat_meta"]={"top":tb0,"col0":c0,"nrows":len(topics),"ncols":len(topdepts2)}
        r=tb0+len(topics)+2

        # ---- Training: Certificates Expiring Soon (30/60/90 days) ----
        tr_sp=spec_of("training"); CE=rng(tr_sp,"Certificate Expiry"); TD=rng(tr_sp,"Department")
        ce0=r
        ws.write(ce0-1,c0,"Window",F["th"]); ws.write(ce0-1,c0+1,"Count",F["th"])
        windows=[("Next 30 days",30),("Next 60 days",60),("Next 90 days",90)]
        for i,(lbl,days) in enumerate(windows):
            ws.write(ce0+i,c0,lbl,F["tdl"])
            f='COUNTIFS(%s,"<>",%s,"<="&(TODAY()+%d),%s,">="&TODAY(),%s,dCrit)'%(CE,CE,days,CE,TD)
            ws.write_formula(ce0+i,c0+1,"="+f,F["tdn"],0)
        self.RR["_cert_expiry_lbl"]=self._a1(ce0,c0,ce0+2); self.RR["_cert_expiry_val"]=self._a1(ce0,c0+1,ce0+2)
        r=ce0+5
        ced0=r; cedepts=HD.DEPARTMENTS
        ws.write(ced0-1,c0,"Department",F["th"]); ws.write(ced0-1,c0+1,"Expiring (90d)",F["th"])
        for i,d in enumerate(cedepts):
            ws.write(ced0+i,c0,d,F["tdl"])
            f='COUNTIFS(%s,"<>",%s,"<="&(TODAY()+90),%s,">="&TODAY(),%s,"%s")'%(CE,CE,CE,TD,d)
            ws.write_formula(ced0+i,c0+1,"="+f,F["tdn"],0)
        self.RR["_cert_expiry_dept_lbl"]=self._a1(ced0,c0,ced0+len(cedepts)-1)
        self.RR["_cert_expiry_dept_val"]=self._a1(ced0,c0+1,ced0+len(cedepts)-1)
        r=ced0+len(cedepts)+2

        # ---- Per-tracker Overdue Ageing (0-7/8-15/16-30/31+ days) for every tracker with a
        # due-date field, feeding both that tracker's own dashboard chart and the system-wide
        # backlog rollup below ----
        BACKLOG_SPECS=[("ca","Due Date"),("nc","Target Close Date"),("hseobs","Due Date"),
                       ("wpinsp","Due Date"),("eqinsp","Due Date"),("walk","Due Date"),
                       ("unsafeact","Due Date"),("unsafecond","Due Date")]
        age_buckets=[("0-7 days",0,7),("8-15 days",8,15),("16-30 days",16,30),("31+ days",31,None)]
        bucket_cells={lbl:[] for lbl,_,_ in age_buckets}
        backlog_total_cells=[]
        for key,duefield in BACKLOG_SPECS:
            s=spec_of(key)
            a0=r
            ws.write(a0-1,c0,"Ageing (open)",F["th"]); ws.write(a0-1,c0+1,"Count",F["th"])
            DUE=rng(s,duefield); ST=rng(s,"Status"); SM=rng(s,"Month")
            depsuf=(",%s,dCrit"%rng(s,"Department")) if has(s,"Department") else ""
            for i,(lbl,lo,hi) in enumerate(age_buckets):
                ws.write(a0+i,c0,lbl,F["tdl"])
                if hi is None:
                    f='COUNTIFS(%s,"Overdue",%s,"<="&(TODAY()-%d),%s,mCrit%s)'%(ST,DUE,lo,SM,depsuf)
                else:
                    f='COUNTIFS(%s,"Overdue",%s,"<="&(TODAY()-%d),%s,">="&(TODAY()-%d),%s,mCrit%s)'%(ST,DUE,lo,DUE,hi,SM,depsuf)
                ws.write_formula(a0+i,c0+1,"="+f,F["tdn"],0)
                bucket_cells[lbl].append(xl_rowcol_to_cell(a0+i,c0+1,True,True))
            self.RR[key+"_aging_lbl"]=self._a1(a0,c0,a0+3)
            self.RR[key+"_aging_val"]=self._a1(a0,c0+1,a0+3)
            total_rng="%s:%s"%(xl_rowcol_to_cell(a0,c0+1,True,True),xl_rowcol_to_cell(a0+3,c0+1,True,True))
            backlog_total_cells.append((key,"SUM(%s)"%total_rng))
            r=a0+6

        # ---- System-Wide Action Backlog: overdue count by tracker + aggregate ageing ----
        bt0=r
        ws.write(bt0-1,c0,"Tracker",F["th"]); ws.write(bt0-1,c0+1,"Overdue Count",F["th"])
        for i,(key,formula) in enumerate(backlog_total_cells):
            s=spec_of(key)
            ws.write(bt0+i,c0,s["sheet"],F["tdl"])
            ws.write_formula(bt0+i,c0+1,"="+formula,F["tdn"],0)
        self.RR["_backlog_tracker_lbl"]=self._a1(bt0,c0,bt0+len(backlog_total_cells)-1)
        self.RR["_backlog_tracker_val"]=self._a1(bt0,c0+1,bt0+len(backlog_total_cells)-1)
        r=bt0+len(backlog_total_cells)+2

        sb0=r
        ws.write(sb0-1,c0,"Ageing Bucket (system-wide)",F["th"]); ws.write(sb0-1,c0+1,"Count",F["th"])
        for i,(lbl,_,_) in enumerate(age_buckets):
            ws.write(sb0+i,c0,lbl,F["tdl"])
            ws.write_formula(sb0+i,c0+1,"="+"+".join(bucket_cells[lbl]),F["tdn"],0)
        self.RR["_backlog_aging_lbl"]=self._a1(sb0,c0,sb0+3)
        self.RR["_backlog_aging_val"]=self._a1(sb0,c0+1,sb0+3)
        gt_rng="%s:%s"%(xl_rowcol_to_cell(sb0,c0+1,True,True),xl_rowcol_to_cell(sb0+3,c0+1,True,True))
        ws.write(sb0+5,c0,"TOTAL SYSTEM BACKLOG",F["th"])
        ws.write_formula(sb0+5,c0+1,"=SUM(%s)"%gt_rng,F["tdn"],0)
        self.RR["_backlog_total_cell"]="Calculations!%s"%xl_rowcol_to_cell(sb0+5,c0+1,True,True)
        r=sb0+8

        # ---- Department League Table: composite score across TRIR/Training/Obs/CA per dept ----
        dl0=r; depts=HD.DEPARTMENTS
        ws.write(dl0-1,c0,"Department",F["th"]); ws.write(dl0-1,c0+1,"Recordable",F["th"])
        ws.write(dl0-1,c0+2,"Training %",F["th"]); ws.write(dl0-1,c0+3,"Obs Closure %",F["th"])
        ws.write(dl0-1,c0+4,"CA Closure %",F["th"]); ws.write(dl0-1,c0+5,"Score",F["th"])
        ws.write(dl0-1,c0+6,"Adj",F["th"])
        tr_sp=spec_of("training"); ob_sp=spec_of("hseobs"); ca_sp=spec_of("ca")
        for i,d in enumerate(depts):
            rr=dl0+i
            ws.write(rr,c0,d,F["tdl"])
            recd=('COUNTIFS(%s,"Lost Time Injury",%s,mCrit,%s,"%s")+COUNTIFS(%s,"Medical Treatment",%s,mCrit,%s,"%s")'
                  '+COUNTIFS(%s,"Restricted Work",%s,mCrit,%s,"%s")+COUNTIFS(%s,"Fatality",%s,mCrit,%s,"%s")')%(
                IClsD,IMD,IDD,d,IClsD,IMD,IDD,d,IClsD,IMD,IDD,d,IClsD,IMD,IDD,d)
            ws.write_formula(rr,c0+1,"="+recd,F["tdn"],0)
            trainc='IFERROR(COUNTIFS(%s,"Completed",%s,mCrit,%s,"%s")/COUNTIFS(%s,mCrit,%s,"%s")*100,0)'%(
                rng(tr_sp,"Status"),rng(tr_sp,"Month"),rng(tr_sp,"Department"),d,rng(tr_sp,"Month"),rng(tr_sp,"Department"),d)
            ws.write_formula(rr,c0+2,"="+trainc,F["tdp"],0)
            obsc='IFERROR(COUNTIFS(%s,"Completed",%s,mCrit,%s,"%s")/COUNTIFS(%s,mCrit,%s,"%s")*100,0)'%(
                rng(ob_sp,"Status"),rng(ob_sp,"Month"),rng(ob_sp,"Department"),d,rng(ob_sp,"Month"),rng(ob_sp,"Department"),d)
            ws.write_formula(rr,c0+3,"="+obsc,F["tdp"],0)
            cac='IFERROR(COUNTIFS(%s,"Completed",%s,mCrit,%s,"%s")/COUNTIFS(%s,mCrit,%s,"%s")*100,0)'%(
                rng(ca_sp,"Status"),rng(ca_sp,"Month"),rng(ca_sp,"Department"),d,rng(ca_sp,"Month"),rng(ca_sp,"Department"),d)
            ws.write_formula(rr,c0+4,"="+cac,F["tdp"],0)
            tc=xl_rowcol_to_cell(rr,c0+2); oc=xl_rowcol_to_cell(rr,c0+3); cc_=xl_rowcol_to_cell(rr,c0+4); rc=xl_rowcol_to_cell(rr,c0+1)
            ws.write_formula(rr,c0+5,"=MAX(0,MIN(100,ROUND(AVERAGE(%s,%s,%s)-%s*5,0)))"%(tc,oc,cc_,rc),F["tdn"],0)
            ws.write_formula(rr,c0+6,"=%s+ROW()/100000"%xl_rowcol_to_cell(rr,c0+5),self._numfmt("0.00000"),0)
        self.RR["_league_dept_lbl"]=self._a1(dl0,c0,dl0+len(depts)-1)
        self.RR["_league_recordable"]=self._a1(dl0,c0+1,dl0+len(depts)-1)
        self.RR["_league_train"]=self._a1(dl0,c0+2,dl0+len(depts)-1)
        self.RR["_league_obs"]=self._a1(dl0,c0+3,dl0+len(depts)-1)
        self.RR["_league_ca"]=self._a1(dl0,c0+4,dl0+len(depts)-1)
        af=xl_rowcol_to_cell(dl0,c0+6,True,True); al=xl_rowcol_to_cell(dl0+len(depts)-1,c0+6,True,True)
        nf_=xl_rowcol_to_cell(dl0,c0,True,True); nl=xl_rowcol_to_cell(dl0+len(depts)-1,c0,True,True)
        sc0=c0+8
        ws.write(dl0-1,sc0,"Rank Dept",F["th"]); ws.write(dl0-1,sc0+1,"Rank Score",F["th"])
        for i in range(len(depts)):
            rr=dl0+i; k=i+1
            large="LARGE(%s:%s,%d)"%(af,al,k)
            ws.write_formula(rr,sc0,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf_,nl,large,af,al),F["tdl"],0)
            ws.write_formula(rr,sc0+1,"=INT(%s)"%large,F["tdn"],0)
        self.RR["_league_lbl"]=self._a1(dl0,sc0,dl0+len(depts)-1)
        self.RR["_league_val"]=self._a1(dl0,sc0+1,dl0+len(depts)-1)
        r=dl0+len(depts)+2

        # ---- Repeat-offender hotspot watchlists (top-5 departments by severity) ----
        HOTSPOTS=[("jsa","cat","Risk Level",["Critical","High"]),
                  ("hseobs","cat","Risk Level",["Critical","High"]),
                  ("wpinsp","sum","Critical Findings",None),
                  ("eqinsp","sum","Critical Findings",None),
                  ("walk","sum","Critical Findings",None),
                  ("unsafeact","cat","Risk Level",["Critical","High"]),
                  ("unsafecond","cat","Risk Level",["Critical","High"]),
                  ("nc","cat","Severity",["Major"]),
                  ("swa","cat","Severity",["Critical","High"])]
        for key,mode,field,severe in HOTSPOTS:
            r=self._hotspot_block(ws,r,c0,spec_of(key),mode,field,severe,key+"_hotspot")

        return r

    def _top10_block(self, ws, r0, c0, title, spec, field, pool, tag):
        F=self.F
        items=pool[:10]
        ws.write(r0-1,c0,"Top 10 "+title,F["th"]); ws.write(r0-1,c0+1,"Count",F["th"])
        ws.write(r0-1,c0+2,"Adj",F["th"]); ws.write(r0-1,c0+3,"Rank Item",F["th"]); ws.write(r0-1,c0+4,"Rank Count",F["th"])
        fr=rng(spec,field); mr_=rng(spec,"Month")
        dep_suf=(",%s,dCrit"%rng(spec,"Department")) if has(spec,"Department") else ""
        for i,it in enumerate(items):
            rr=r0+i
            ws.write(rr,c0,it,F["tdl"])
            ws.write_formula(rr,c0+1,'=COUNTIFS(%s,"%s",%s,mCrit%s)'%(fr,it,mr_,dep_suf),F["tdn"],0)
            ws.write_formula(rr,c0+2,"=%s+ROW()/100000"%xl_rowcol_to_cell(rr,c0+1),self._numfmt("0.00000"),0)
        af=xl_rowcol_to_cell(r0,c0+2,True,True); al=xl_rowcol_to_cell(r0+len(items)-1,c0+2,True,True)
        nf_=xl_rowcol_to_cell(r0,c0,True,True); nl=xl_rowcol_to_cell(r0+len(items)-1,c0,True,True)
        for i in range(len(items)):
            rr=r0+i; k=i+1
            large="LARGE(%s:%s,%d)"%(af,al,k)
            ws.write_formula(rr,c0+3,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf_,nl,large,af,al),F["tdl"],0)
            ws.write_formula(rr,c0+4,"=INT(%s)"%large,F["tdn"],0)
        lc=xl_col_to_name(c0+3); vc=xl_col_to_name(c0+4)
        self.RR[tag+"_lbl"]="Calculations!$%s$%d:$%s$%d"%(lc,r0+1,lc,r0+len(items))
        self.RR[tag+"_val"]="Calculations!$%s$%d:$%s$%d"%(vc,r0+1,vc,r0+len(items))
        return r0+len(items)+2

    def _hotspot_block(self, ws, r0, c0, spec, mode, field, severe_vals, tag, top_n=5):
        """Top-N departments by High/Critical severity count (mode='cat') or a numeric
        column sum (mode='sum') for one tracker - a repeat-offender watchlist. Deliberately
        month-filtered only (mCrit), never department-filtered (dCrit), since the whole point
        is comparing departments against each other."""
        F=self.F; depts=HD.DEPARTMENTS
        Mn=rng(spec,"Month"); Dp=rng(spec,"Department")
        ws.write(r0-1,c0,"Department",F["th"]); ws.write(r0-1,c0+1,"Count",F["th"])
        ws.write(r0-1,c0+2,"Adj",F["th"])
        for i,d in enumerate(depts):
            rr=r0+i
            ws.write(rr,c0,d,F["tdl"])
            if mode=="cat":
                fsum="+".join('COUNTIFS(%s,"%s",%s,mCrit,%s,"%s")'%(rng(spec,field),v,Mn,Dp,d) for v in severe_vals)
            else:
                fsum='SUMIFS(%s,%s,mCrit,%s,"%s")'%(rng(spec,field),Mn,Dp,d)
            ws.write_formula(rr,c0+1,"="+fsum,F["tdn"],0)
            ws.write_formula(rr,c0+2,"=%s+ROW()/100000"%xl_rowcol_to_cell(rr,c0+1),self._numfmt("0.00000"),0)
        af=xl_rowcol_to_cell(r0,c0+2,True,True); al=xl_rowcol_to_cell(r0+len(depts)-1,c0+2,True,True)
        nf_=xl_rowcol_to_cell(r0,c0,True,True); nl=xl_rowcol_to_cell(r0+len(depts)-1,c0,True,True)
        sc0=c0+4
        ws.write(r0-1,sc0,"Rank Dept",F["th"]); ws.write(r0-1,sc0+1,"Rank Count",F["th"])
        for i in range(top_n):
            rr=r0+i; k=i+1
            large="LARGE(%s:%s,%d)"%(af,al,k)
            ws.write_formula(rr,sc0,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(nf_,nl,large,af,al),F["tdl"],0)
            ws.write_formula(rr,sc0+1,"=INT(%s)"%large,F["tdn"],0)
        self.RR[tag+"_lbl"]=self._a1(r0,sc0,r0+top_n-1)
        self.RR[tag+"_val"]=self._a1(r0,sc0+1,r0+top_n-1)
        return r0+len(depts)+2

    def _numfmt(self, nf):
        return self.wb.add_format({"font_name":"Segoe UI","font_size":9,"align":"center",
            "valign":"vcenter","border":1,"border_color":"#D8E1EB","num_format":nf})

    def _register_calc(self, ws, spec, sr):
        """Monthly volume + category + status + KPI scalars for one register."""
        F=self.F; key=spec["key"]; headers=spec["headers"]
        ws.write(sr-1,1,"▸ %s"%spec["sheet"],F["bodyb"])
        Mn=rng(spec,"Month")
        dep = has(spec,"Department")
        Dp=rng(spec,"Department") if dep else None
        def dsuf(): return (",%s,dCrit"%Dp) if dep else ""
        # monthly volume (col B/C)
        ws.write(sr,1,"Month",F["th"]); ws.write(sr,2,"Count",F["th"])
        for i,mn in enumerate(MONTHS):
            ws.write(sr+1+i,1,mn,F["td"])
            ws.write_formula(sr+1+i,2,'=COUNTIFS(%s,"%s"%s)'%(Mn,mn,dsuf()),F["tdn"],0)
        out={"month_lbl":self._a1(sr+1,1,sr+12),"month_val":self._a1(sr+1,2,sr+12)}
        # category breakdown (col E/F)
        cat=spec.get("cat")
        if cat and cat in headers:
            vals=HD.POOLS.get(cat) or self._distinct(spec,cat)
            vals=vals[:8]
            ws.write(sr,4,cat,F["th"]); ws.write(sr,5,"Count",F["th"])
            for i,v in enumerate(vals):
                ws.write(sr+1+i,4,v,F["tdl"])
                ws.write_formula(sr+1+i,5,'=COUNTIFS(%s,"%s",%s,mCrit%s)'%(rng(spec,cat),v,Mn,dsuf()),F["tdn"],0)
            out["cat_lbl"]=self._a1(sr+1,4,sr+len(vals)); out["cat_val"]=self._a1(sr+1,5,sr+len(vals))
        # secondary distribution (col G/H) - Mode/Frequency/Result/Verdict-style
        cat2=spec.get("cat2")
        if cat2 and cat2 in headers:
            vals2=HD.POOLS.get(cat2) or self._distinct(spec,cat2)
            vals2=vals2[:8]
            ws.write(sr,6,cat2,F["th"]); ws.write(sr,7,"Count",F["th"])
            for i,v in enumerate(vals2):
                ws.write(sr+1+i,6,v,F["tdl"])
                ws.write_formula(sr+1+i,7,'=COUNTIFS(%s,"%s",%s,mCrit%s)'%(rng(spec,cat2),v,Mn,dsuf()),F["tdn"],0)
            out["cat2_lbl"]=self._a1(sr+1,6,sr+len(vals2)); out["cat2_val"]=self._a1(sr+1,7,sr+len(vals2))
        # status breakdown (col J/K)
        st=spec.get("status")
        if st and st in headers:
            svals=HD.POOLS.get(st) or self._distinct(spec,st)
            svals=svals[:6]
            ws.write(sr,9,st,F["th"]); ws.write(sr,10,"Count",F["th"])
            for i,v in enumerate(svals):
                ws.write(sr+1+i,9,v,F["tdl"])
                ws.write_formula(sr+1+i,10,'=COUNTIFS(%s,"%s",%s,mCrit%s)'%(rng(spec,st),v,Mn,dsuf()),F["tdn"],0)
            out["st_lbl"]=self._a1(sr+1,9,sr+len(svals)); out["st_val"]=self._a1(sr+1,10,sr+len(svals))
        # KPI scalars (col M/N) - up to 8 tiles
        kc=12
        kpis=self._kpi_defs(spec)
        ws.write(sr,kc,"KPI",F["th"]); ws.write(sr,kc+1,"Value",F["th"])
        out["kpi"]=[]
        for i,(lbl,formula,kind) in enumerate(kpis):
            ws.write(sr+1+i,kc,lbl,F["tdl"])
            nf={"num":F["tdn"],"pct":F["tdp"]}[kind]
            ws.write_formula(sr+1+i,kc+1,"="+formula,nf,0)
            out["kpi"].append((lbl,"Calculations!$%s$%d"%(xl_col_to_name(kc+1),sr+2+i),kind))
        # ---- Department Performance table (col P onward) ----
        if dep:
            dc0=15
            depts=HD.DEPARTMENTS
            ws.write(sr,dc0,"Department",F["th"]); ws.write(sr,dc0+1,"Count",F["th"])
            met1,met2 = self._dept_table_metrics(spec)
            ws.write(sr,dc0+2,met1[0],F["th"]); ws.write(sr,dc0+3,met2[0],F["th"])
            for i,d in enumerate(depts):
                rr=sr+1+i
                ws.write(rr,dc0,d,F["tdl"])
                ws.write_formula(rr,dc0+1,'=COUNTIFS(%s,mCrit,%s,"%s")'%(Mn,Dp,d),F["tdn"],0)
                ws.write_formula(rr,dc0+2,"="+met1[1](d),F["tdn"] if met1[2]=="num" else F["tdp"],0)
                ws.write_formula(rr,dc0+3,"="+met2[1](d),F["tdn"] if met2[2]=="num" else F["tdp"],0)
            out["dept_lbl"]=self._a1(sr+1,dc0,sr+len(depts))
            out["dept_val"]=self._a1(sr+1,dc0+1,sr+len(depts))
            out["dept_top"]=sr; out["dept_dc0"]=dc0; out["dept_n"]=len(depts)
            out["dept_met1_name"]=met1[0]; out["dept_met2_name"]=met2[0]
            out["dept_met1_kind"]=met1[2]; out["dept_met2_kind"]=met2[2]
        # ---- Monthly Performance Matrix (col U onward: measure rows x Jan..Dec + YTD) ----
        mc0=20
        measures=self._matrix_measures(spec)
        ws.write(sr,mc0,"Metric",F["th"])
        for j,mn in enumerate(MONTHS): ws.write(sr,mc0+1+j,mn,F["th"])
        ws.write(sr,mc0+13,"YTD",F["th"])
        for i,(lbl,fmonth,kind,agg) in enumerate(measures):
            rr=sr+1+i
            ws.write(rr,mc0,lbl,F["tdl"])
            for j,mn in enumerate(MONTHS):
                ws.write_formula(rr,mc0+1+j,"="+fmonth(mn),F["tdn"] if kind=="num" else F["tdp"],0)
            first=xl_rowcol_to_cell(rr,mc0+1); last=xl_rowcol_to_cell(rr,mc0+12)
            if agg=="sum":
                ws.write_formula(rr,mc0+13,"=SUM(%s:%s)"%(first,last),F["tdn"],0)
            elif agg=="avg":
                ws.write_formula(rr,mc0+13,"=IFERROR(AVERAGE(%s:%s),0)"%(first,last),F["tdp"] if kind=="pct" else F["tdn"],0)
        out["matrix_top"]=sr
        out["matrix_kinds"]=[kind for (_,_,kind,_) in measures]
        return out

    def _status_vals(self, spec):
        """The real status-like value pool for this tracker (matches the data generator),
        not a generic fallback - critical now that pools differ sharply per tracker."""
        pool = HD.STATUS_POOLS.get(spec["key"])
        if pool: return pool[0]
        st = spec.get("status")
        if st: return HD.POOLS.get(st, HD.STATUS)
        return HD.STATUS

    def _dept_table_metrics(self, spec):
        """Two department-level metric column defs: (label, fn(dept)->formula, kind)."""
        Mn=rng(spec,"Month"); Dp=rng(spec,"Department")
        st=spec.get("status")
        if st and st in spec["headers"]:
            svals=self._status_vals(spec)
            closed=[v for v in svals if v in CLOSED_VALUES] or [svals[0]]
            def closedpct(d):
                cf="+".join('COUNTIFS(%s,"%s",%s,mCrit,%s,"%s")'%(rng(spec,st),v,Mn,Dp,d) for v in closed)
                tot='COUNTIFS(%s,mCrit,%s,"%s")'%(Mn,Dp,d)
                return "IFERROR((%s)/%s*100,0)"%(cf,tot)
            met1=("Closed %",closedpct,"pct")
        else:
            met1=("Records",lambda d:'COUNTIFS(%s,mCrit,%s,"%s")'%(Mn,Dp,d),"num")
        auto=spec.get("auto",{})
        if auto:
            pcol=list(auto)[0]
            met2=("Avg "+pcol,lambda d:'IFERROR(AVERAGEIFS(%s,%s,mCrit,%s,"%s"),0)'%(rng(spec,pcol),Mn,Dp,d),"pct")
        else:
            met2=("Records",lambda d:'COUNTIFS(%s,mCrit,%s,"%s")'%(Mn,Dp,d),"num")
        return met1,met2

    def _matrix_measures(self, spec):
        """Monthly-performance-matrix rows: list of (label, fn(month)->formula, kind, agg)."""
        Mn=rng(spec,"Month"); dep=has(spec,"Department")
        Dp=rng(spec,"Department") if dep else None
        dsuf=lambda: (",%s,dCrit"%Dp) if dep else ""
        def cnt(mn): return 'COUNTIFS(%s,"%s"%s)'%(Mn,mn,dsuf())
        rows=[("Records", cnt, "num","sum")]
        st=spec.get("status")
        if st and st in spec["headers"]:
            svals=self._status_vals(spec)
            closed=[v for v in svals if v in CLOSED_VALUES] or [svals[0]]
            def compl(mn):
                cf="+".join('COUNTIFS(%s,"%s",%s,"%s"%s)'%(rng(spec,st),v,Mn,mn,dsuf()) for v in closed)
                return "IFERROR((%s)/COUNTIFS(%s,\"%s\"%s)*100,0)"%(cf,Mn,mn,dsuf())
            rows.append(("Closed/Completed %", compl, "pct","avg"))
        auto=spec.get("auto",{})
        if auto:
            pcol=list(auto)[0]
            rows.append(("Avg "+pcol, lambda mn:'IFERROR(AVERAGEIFS(%s,%s,"%s"%s),0)'%(rng(spec,pcol),Mn,mn,dsuf()), "pct","avg"))
        if has(spec,"Lost Days"):
            rows.append(("Lost Days", lambda mn:'SUMIFS(%s,%s,"%s"%s)'%(rng(spec,"Lost Days"),Mn,mn,dsuf()), "num","sum"))
        return rows[:6]

    def _kpi_defs(self, spec):
        """The exact 8 KPI cards (2 rows x 4) for this tracker, matching the client's reference
        dashboard (Share_HSE_Full_System2.xlsx) card-for-card - not a generic template."""
        key=spec["key"]; Mn=rng(spec,"Month")
        dep=has(spec,"Department"); Dp=rng(spec,"Department") if dep else None
        dsuf=(",%s,dCrit"%Dp) if dep else ""
        total='COUNTIFS(%s,mCrit%s)'%(Mn,dsuf)
        def cnt(col,val): return 'COUNTIFS(%s,"%s",%s,mCrit%s)'%(rng(spec,col),val,Mn,dsuf)
        def ssum(col): return 'SUMIFS(%s,%s,mCrit%s)'%(rng(spec,col),Mn,dsuf)
        def savg(col): return 'IFERROR(AVERAGEIFS(%s,%s,mCrit%s),0)'%(rng(spec,col),Mn,dsuf)
        def pctof(numf): return 'IFERROR((%s)/(%s)*100,0)'%(numf,total)
        def nonblank(col): return 'COUNTIFS(%s,"<>",%s,mCrit%s)'%(rng(spec,col),Mn,dsuf)
        def distinct(col, pool):
            f='+'.join('--(COUNTIFS(%s,"%s",%s,mCrit%s)>0)'%(rng(spec,col),v,Mn,dsuf) for v in pool)
            return f

        if key=="toolbox":
            defs=[("Total","num",total),("Action: Yes","num",cnt("Action Required","Yes")),
                ("Action: No","num",cnt("Action Required","No")),("Avg Attendance","pct",savg("Attendance %")),
                ("Total Target","num",ssum("Target Attendees")),("Total Actual","num",ssum("Actual Attendees")),
                ("Avg Duration","num",savg("Duration (min)")),
                ("Topics Covered","num",distinct("Topic", HD.TOPICS))]
        elif key=="jsa":
            defs=[("Total JSAs","num",total),("Approved","num",cnt("Approval Status","Approved")),
                ("Pending","num",cnt("Approval Status","Pending Review")),("High Risk","num",cnt("Risk Level","High")),
                ("Medium Risk","num",cnt("Risk Level","Medium")),("Low Risk","num",cnt("Risk Level","Low")),
                ("Total Hazards","num",ssum("Hazards Identified")),("Controls Done","num",cnt("Compliance","Compliant"))]
        elif key=="training":
            defs=[("Total Trainings","num",total),("Completed","num",cnt("Status","Completed")),
                ("In Progress","num",cnt("Status","In Progress")),("Scheduled","num",cnt("Status","Scheduled")),
                ("Avg Attendance %","pct",savg("Attendance %")),("Total Hours","num",ssum("Duration (hrs)")),
                ("Pass Rate","pct",pctof(cnt("Assessment Result","Pass"))),("Certificates","num",cnt("Certificate Issued","Yes"))]
        elif key=="hseobs":
            defs=[("Total Obs","num",total),("Completed","num",cnt("Status","Completed")),
                ("In Progress","num",cnt("Status","In Progress")),("Overdue","num",cnt("Status","Overdue")),
                ("Safe Acts","num",cnt("Observation Type","Safe Act")+"+"+cnt("Observation Type","Safe Condition")),
                ("Unsafe Acts","num",cnt("Observation Type","Unsafe Act")+"+"+cnt("Observation Type","Unsafe Condition")),
                ("High Risk","num",cnt("Risk Level","High")),("Comp %","pct",pctof(cnt("Status","Completed")))]
        elif key in ("wpinsp","eqinsp","walk"):
            defs=[("Total","num",total),("Completed","num",cnt("Status","Completed")),
                ("Overdue","num",cnt("Status","Overdue")),("Critical","num",ssum("Critical Findings")),
                ("Checkpoints","num",ssum("Checkpoints Inspected")),("Non-Conf","num",ssum("Non-Conformances")),
                ("NC Rate","pct",pctof(ssum("Non-Conformances"))),("Comp %","pct",pctof(cnt("Status","Completed")))]
        elif key=="meetings":
            defs=[("Total Meetings","num",total),("Avg Attendance","pct",savg("Attendance %")),
                ("Actions Raised","num",ssum("Action Items Raised")),("Actions Closed","num",ssum("Actions Closed")),
                ("Close-out %","pct",savg("Close-out %")),("Total Hours","num","(%s)/60"%ssum("Duration (min)")),
                ("MoM Done","num",cnt("MoM Circulated","Yes")),("MoM Pending","num",cnt("MoM Circulated","No"))]
        elif key=="bulletins":
            defs=[("Total","num",total),("Issued","num",cnt("Status","Issued")),
                ("Acknowledged","num",cnt("Status","Acknowledged")),("Closed","num",cnt("Status","Closed")),
                ("Target Reach","num",ssum("Target Reach")),("Actual Reach","num",ssum("Actual Reach")),
                ("Reach %","pct",savg("Reach %")),("High Priority","num",cnt("Priority","High"))]
        elif key=="drills":
            defs=[("Total Drills","num",total),("Completed","num",cnt("Status","Completed")),
                ("Pending","num",cnt("Status","Action Pending")),("Avg Participation","pct",savg("Participation %")),
                ("Target Resp","num",savg("Target Response (min)")),("Actual Resp","num",savg("Actual Response (min)")),
                ("Total Participants","num",ssum("Actual Participants")),("Improvements","num",nonblank("Improvement Areas"))]
        elif key in ("iaudit","eaudit"):
            defs=[("Total Audits","num",total),("Completed","num",cnt("Status","Completed")),
                ("In Progress","num",cnt("Status","In Progress")),("Scheduled","num",cnt("Status","Scheduled")),
                ("Checklist Items","num",ssum("Checklist Items")),("Minor NC","num",ssum("Minor NC")),
                ("Major NC","num",ssum("Major NC")),("Observations","num",ssum("Observations"))]
        elif key=="mgmtvisit":
            defs=[("Total Visits","num",total),("Completed","num",cnt("Status","Completed")),
                ("Action Pending","num",cnt("Status","Action Pending")),("Observations","num",ssum("Observations Made")),
                ("Actions Raised","num",ssum("Actions Raised")),("Actions Closed","num",ssum("Actions Closed")),
                ("Close-out %","pct",savg("Close-out %")),("Avg Duration","num",savg("Duration (min)"))]
        elif key=="mgmtreview":
            defs=[("Total Reviews","num",total),("Completed","num",cnt("Status","Completed")),
                ("In Progress","num",cnt("Status","In Progress")),("Avg Attendance","pct",savg("Attendance %")),
                ("Decisions","num",ssum("Decisions Made")),("Actions","num",ssum("Actions Assigned")),
                ("Close-out","pct",savg("Close-out %")),("MoM Done","num",cnt("MoM Distributed","Yes"))]
        elif key=="disc":
            defs=[("Total Cases","num",total),("Completed","num",cnt("Status","Completed")),
                ("Under Review","num",cnt("Status","Under Review")),("Appealed","num",cnt("Status","Appealed")),
                ("1st Offense","num",cnt("Offense Level","1st Offense")),("Repeat","num",cnt("Offense Level","Repeat")),
                ("Suspensions","num",cnt("Action Taken","Suspension")),("Terminations","num",cnt("Action Taken","Termination"))]
        elif key=="awards":
            defs=[("Total Awards","num",total),("Presented","num",cnt("Status","Presented")),
                ("Scheduled","num",cnt("Status","Scheduled")),("Nominated","num",cnt("Status","Nominated")),
                ("Certificates","num",cnt("Reward Type","Certificate")),("Cash Bonus","num",cnt("Reward Type","Cash Bonus")),
                ("Trophies","num",cnt("Reward Type","Trophy")),("Vouchers","num",cnt("Reward Type","Gift Voucher"))]
        elif key=="swa":
            defs=[("Total SWA","num",total),("Resolved","num",cnt("Resolution","Resolved")),
                ("Investigating","num",cnt("Resolution","Under Investigation")),("Fixed","num",cnt("Resolution","Permanent Fix Applied")),
                ("Critical","num",cnt("Severity","Critical")),("High","num",cnt("Severity","High")),
                ("Total Downtime","num",ssum("Downtime (min)")),("Investigated","num",cnt("Investigation Done","Yes"))]
        elif key=="alcohol":
            defs=[("Total Tests","num",total),("Negative","num",cnt("Result","Negative")),
                ("Positive","num",cnt("Result","Positive")),("Pass Rate","pct",pctof(cnt("Result","Negative"))),
                ("Random Tests","num",cnt("Test Type","Random")),("Pre-Shift","num",cnt("Test Type","Pre-Shift")),
                ("Post-Incident","num",cnt("Test Type","Post-Incident")),("Suspicion","num",cnt("Test Type","Reasonable Suspicion"))]
        elif key=="ptwaudit":
            defs=[("Total Audits","num",total),("Compliant","num",cnt("Verdict","Compliant")),
                ("Non-Compliant","num",cnt("Verdict","Non-Compliant")),("Partial","num",cnt("Verdict","Partially Compliant")),
                ("Permits Reviewed","num",ssum("Permits Reviewed")),("Deviations","num",ssum("Deviations Found")),
                ("Avg Compliance","pct",savg("Compliance %")),("Compliance Rate","pct",pctof(cnt("Verdict","Compliant")))]
        elif key=="ca":
            defs=[("Total CAs","num",total),("Completed","num",cnt("Status","Completed")),
                ("In Progress","num",cnt("Status","In Progress")),("Overdue","num",cnt("Status","Overdue")),
                ("Comp %","pct",pctof(cnt("Status","Completed"))),("High Priority","num",cnt("Priority","High")),
                ("Medium","num",cnt("Priority","Medium")),("Low","num",cnt("Priority","Low"))]
        elif key=="nc":
            defs=[("Total NCs","num",total),("Closed","num",cnt("Status","Closed")),
                ("Open","num",cnt("Status","Open")),("Overdue","num",cnt("Status","Overdue")),
                ("Closure %","pct",pctof(cnt("Status","Closed"))),("Major","num",cnt("Severity","Major")),
                ("Minor","num",cnt("Severity","Minor")),("Observations","num",cnt("Severity","Observation"))]
        elif key in ("unsafeact","unsafecond"):
            defs=[("Total Reports","num",total),("Completed","num",cnt("Status","Completed")),
                ("In Progress","num",cnt("Status","In Progress")),("Overdue","num",cnt("Status","Overdue")),
                ("High Risk","num",cnt("Risk Level","High")),("Medium Risk","num",cnt("Risk Level","Medium")),
                ("Low Risk","num",cnt("Risk Level","Low")),("Closure %","pct",pctof(cnt("Status","Completed")))]
        elif key=="incident":
            IM=rng(spec,"Month"); ID=rng(spec,"Department"); ICls=rng(spec,"Classification")
            IAge=rng(spec,"Ageing (Days)"); IStat=rng(spec,"Status")
            defs=[("Total","num",total),("Open","num",cnt("Status","Open")),("Closed","num",cnt("Status","Closed")),
                ("Overdue","num",'COUNTIFS(%s,"<>Closed",%s,">30",%s,mCrit%s)'%(IStat,IAge,IM,dsuf)),
                ("Near Miss","num",cnt("Classification","Near Miss")),
                ("Recordable","num",cnt("Classification","Lost Time Injury")+"+"+cnt("Classification","Medical Treatment")
                    +"+"+cnt("Classification","Restricted Work")+"+"+cnt("Classification","Fatality")),
                ("LTI+Fatality","num",cnt("Classification","Lost Time Injury")+"+"+cnt("Classification","Fatality")),
                ("Avg Close (d)","num",'IFERROR(AVERAGEIFS(%s,%s,"Closed",%s,mCrit%s),0)'%(IAge,IStat,IM,dsuf))]
        else:
            raise KeyError("no KPI card definitions for tracker key %r" % key)
        return [(lbl,f,kind) for lbl,kind,f in defs][:8]

    def _distinct(self, spec, header):
        idx=spec["headers"].index(header)
        seen=[]
        for row in DATA[spec["key"]]:
            v=row[idx]
            if v not in seen and v not in ("",None): seen.append(v)
        return seen

    def _a1(self, r0, c, r1):
        cL=xl_col_to_name(c)
        return "Calculations!$%s$%d:$%s$%d"%(cL,r0+1,cL,r1+1)

    def _rng_bounded(self, spec, name, n):
        """Like rng(), but bounded to the actual data rows (not the 100,000-row growth
        buffer) - required for any O(n^2)-ish check like duplicate-ID detection."""
        c=col(spec,name)
        return "'%s'!$%s$%d:$%s$%d"%(spec["sheet"],c,D0,c,D0-1+n)

    # ---------------------------------------------------------------- data quality
    def write_data_quality(self):
        """Pure-formula integrity checks across all 24 registers: blank required fields,
        duplicate IDs, dates outside the reporting year, and end-date-before-start-date
        logic errors - catches bad manual entry, doesn't just trust the data."""
        F=self.F; ws=self.wb.add_worksheet("Data Quality"); ws.set_tab_color(RED)
        ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",26)
        for cc in range(2,10): ws.set_column(cc,cc,15)
        ws.merge_range("B2:J2","🔎  DATA QUALITY — automatic integrity checks across all 24 registers", F["section"])
        ws.write("B3","Recalculates on every Refresh. A register only needs attention if a count is greater than 0.",F["note"])
        hdrs=["Register","Records","Blank Dept","Blank Date","Duplicate IDs","Outside Report Year","Date-Logic Issues","Flag"]
        for j,h in enumerate(hdrs): ws.write(4,1+j,h,F["th"])
        DATE_LOGIC={"ca":("Date Raised","Completion Date"),"nc":("Date Raised","Actual Close Date"),
                    "incident":("Date","Closure Date")}
        r=5
        for spec in HD.REGISTERS:
            n=len(DATA[spec["key"]]); headers=spec["headers"]
            ws.write(r,1,spec["sheet"],F["tdl"])
            idcol=self._rng_bounded(spec,headers[1],n)
            ws.write_formula(r,2,"=COUNTA(%s)"%idcol,F["tdn"],0)
            if has(spec,"Department"):
                deptcol=self._rng_bounded(spec,"Department",n)
                ws.write_formula(r,3,"=COUNTBLANK(%s)"%deptcol,F["tdn"],0)
            else:
                ws.write(r,3,"n/a",F["td"])
            datefield=None
            for cand in ("Date","Date Raised","Date Issued"):
                if cand in headers: datefield=cand; break
            if datefield:
                datecol=self._rng_bounded(spec,datefield,n)
                ws.write_formula(r,4,"=COUNTBLANK(%s)"%datecol,F["tdn"],0)
            else:
                ws.write(r,4,"n/a",F["td"])
            ws.write_formula(r,5,"=SUMPRODUCT((COUNTIF(%s,%s)>1)*1)"%(idcol,idcol),F["tdn"],0)
            if datefield:
                ws.write_formula(r,6,'=SUMPRODUCT((%s<>"")*(YEAR(%s)<>ReportYear))'%(datecol,datecol),F["tdn"],0)
            else:
                ws.write(r,6,"n/a",F["td"])
            if spec["key"] in DATE_LOGIC:
                startf,endf=DATE_LOGIC[spec["key"]]
                startcol=self._rng_bounded(spec,startf,n); endcol=self._rng_bounded(spec,endf,n)
                ws.write_formula(r,7,'=SUMPRODUCT((%s<>"")*(%s<%s))'%(endcol,endcol,startcol),F["tdn"],0)
            else:
                ws.write(r,7,"n/a",F["td"])
            cD=xl_rowcol_to_cell(r,3); cE=xl_rowcol_to_cell(r,4); cF=xl_rowcol_to_cell(r,5)
            cG=xl_rowcol_to_cell(r,6); cH=xl_rowcol_to_cell(r,7)
            ws.write_formula(r,8,'=IF(N(%s)+N(%s)+N(%s)+N(%s)+N(%s)>0,"⚠ REVIEW","✅ OK")'%(cD,cE,cF,cG,cH),F["tdl"],0)
            r+=1
        last=r-1
        ws.conditional_format(5,8,last,8,{"type":"text","criteria":"containing","value":"REVIEW",
            "format":self._fmt(bg_color=RED_L,font_color=RED,bold=True)})
        ws.conditional_format(5,8,last,8,{"type":"text","criteria":"containing","value":"OK",
            "format":self._fmt(bg_color=GREEN_L,font_color=GREEN,bold=True)})
        r+=1
        ws.write(r,1,"TOTAL ISSUES (all registers)",F["bodyb"])
        totf=self._fmt(font_name="Segoe UI",font_size=11,bold=True,font_color=RED,align="center",
            valign="vcenter",bg_color=GREY_L,border=1,border_color="#D8E1EB")
        for cc in (3,4,5,6,7):
            colL=xl_col_to_name(cc)
            ws.write_formula(r,cc,"=SUMPRODUCT(N(%s$6:%s$%d))"%(colL,colL,last+1),totf,0)
        ws.write_url(0,1,"internal:'Home'!A1",F["note"],"Home")

    # ---------------------------------------------------------------- investigation log
    def write_investigation_log(self):
        """5-Why root-cause investigation template, linked to an Incident ID or NC No. -
        picking either auto-fills Department & Classification/Severity from that record."""
        F=self.F; ws=self.wb.add_worksheet("Investigation Log"); ws.set_tab_color(ACCENT)
        headers=["S.No","Investigation ID","Date","Incident ID","NC No.","Department","Classification / Severity",
                  "Why 1","Why 2","Why 3","Why 4","Why 5","Root Cause","Corrective Action","Investigator","Status"]
        nc=len(headers)
        ws.merge_range(0,0,0,nc-1,"🔬  INVESTIGATION LOG — 5-Why Root-Cause Analysis  —  DATA ENTRY",F["reg_title"])
        ws.set_row(0,22)
        ws.merge_range(1,0,1,nc-1,
            "Pick an Incident ID OR an NC No. (not both) — Department & Classification/Severity auto-fill. "
            "Blue = user input   ·   Gray = auto-calculated", F["reg_legend"])
        for i,h in enumerate(headers):
            ws.write(2,i,h,F["reg_hdr"])
        inc=spec_of("incident"); ncs=spec_of("nc")
        n_inc=len(DATA["incident"]); n_nc=len(DATA["nc"])
        inc_id_bounded=self._rng_bounded(inc,"Incident ID",n_inc)
        nc_id_bounded=self._rng_bounded(ncs,"NC No.",n_nc)
        inc_id_full=rng(inc,"Incident ID"); inc_dept_full=rng(inc,"Department"); inc_cls_full=rng(inc,"Classification")
        nc_id_full=rng(ncs,"NC No."); nc_dept_full=rng(ncs,"Department"); nc_sev_full=rng(ncs,"Severity")
        ROWS=300
        for r in range(ROWS):
            er=3+r
            ws.write_number(er,0,r+1,F["cell_in"])
            for c in (1,2,3,4,7,8,9,10,11,12,13,14,15):
                fmt=F["date_in"] if c==2 else (F["cell_in_l"] if c in (1,7,8,9,10,11,12,13,14) else F["cell_in"])
                ws.write(er,c,"",fmt)
            iid=xl_rowcol_to_cell(er,3); ncid=xl_rowcol_to_cell(er,4)
            ws.write_formula(er,5,'=IFERROR(INDEX(%s,MATCH(%s,%s,0)),IFERROR(INDEX(%s,MATCH(%s,%s,0)),""))'%(
                inc_dept_full,iid,inc_id_full,nc_dept_full,ncid,nc_id_full),F["cell_calc"],0)
            ws.write_formula(er,6,'=IFERROR(INDEX(%s,MATCH(%s,%s,0)),IFERROR(INDEX(%s,MATCH(%s,%s,0)),""))'%(
                inc_cls_full,iid,inc_id_full,nc_sev_full,ncid,nc_id_full),F["cell_calc"],0)
        ws.add_table(2,0,2+ROWS,nc-1,{"name":"t_investigation","style":"Table Style Medium 9",
            "columns":[{"header":h} for h in headers]})
        ws.data_validation(3,3,2+ROWS,3,{"validate":"list","source":"=%s"%inc_id_bounded.replace("'","")})
        ws.data_validation(3,4,2+ROWS,4,{"validate":"list","source":"=%s"%nc_id_bounded.replace("'","")})
        ws.data_validation(3,15,2+ROWS,15,{"validate":"list","source":"=L_Status"})
        for i,h in enumerate(headers):
            width = 12 if h in ("S.No","Date","Incident ID","NC No.","Status") else (18 if h in ("Department","Classification / Severity","Investigator") else 26)
            colfmt = F["cell_calc"] if h in ("Department","Classification / Severity") else F["cell_in"]
            ws.set_column(i,i,width,colfmt)
        ws.freeze_panes(3,0); ws.set_zoom(90)
        ws.repeat_rows(0,2); ws.set_landscape(); ws.fit_to_pages(1,0)
        ws.write_url(0,nc+1,"internal:'Home'!A1",F["reg_legend"],"Home")

    # ---------------------------------------------------------------- change log
    def write_change_log(self):
        """Empty audit-trail sheet, appended to by the Workbook_SheetChange VBA handler
        whenever someone edits a cell on any of the 24 registers - who, what, when, old/new
        value. Nothing to pre-fill; the log only grows as the workbook is actually used."""
        F=self.F; ws=self.wb.add_worksheet("Change Log"); ws.set_tab_color(GREY_D)
        ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",20)
        ws.set_column("C:C",24); ws.set_column("D:D",12); ws.set_column("E:F",20); ws.set_column("G:G",18)
        ws.merge_range("B2:G2","📝  CHANGE LOG — automatic audit trail of register edits (who, what, when)",F["section"])
        ws.write("B3","Populated automatically by Workbook_SheetChange whenever a register cell is edited. "
                       "Old Value shows '(n/a)' for multi-cell pastes (only single-cell edits are tracked before/after).",F["note"])
        hdrs=["Timestamp","Sheet","Cell","Old Value","New Value","User"]
        for j,h in enumerate(hdrs): ws.write(4,1+j,h,F["th"])
        ws.write_url(0,1,"internal:'Home'!A1",F["note"],"Home")


def _to_dt(v):
    if isinstance(v, datetime.date): return datetime.datetime(v.year,v.month,v.day)
    return v


if __name__ == "__main__":
    out=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","RCPL_Integrated_EHS_Management_System.xlsm"))
    e=EHS(out)
    e.write_registers()
    e.write_master()
    e.write_settings()
    e.write_help()
    e.write_data_quality()
    e.write_investigation_log()
    e.write_change_log()
    e.write_calc()
    import hse_dash
    hse_dash.build(e)
    vba=vbabin.build_vba_project(vba_code_hse.modules())
    bp=os.path.join(os.path.dirname(__file__),"vbaProject_hse.bin")
    open(bp,"wb").write(vba)
    e.wb.add_vba_project(bp)
    e.wb.set_vba_name("ThisWorkbook")
    e.wb.close()
    print("WROTE",out,os.path.getsize(out),"bytes")
