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
D0, DN = 4, 5003          # register data rows (header row 3)

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
            valign="vcenter",bg_color=AMBER_L,border=1,border_color="#E2C97A")
        F["set_note"]=self._fmt(font_name=seg,font_size=9,italic=True,font_color=GREY_M,align="left",valign="vcenter")

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
        date_idx={headers.index(h) for h in headers if "Date" in h or h=="Month"}
        for r,row in enumerate(rows):
            er=D0-1+r   # 0-indexed excel row (D0=4 -> er=3 for first data row after header at row index 2)
            for c,val in enumerate(row):
                h=headers[c]
                if h in auto:
                    continue  # formula written below
                if h=="Ageing (Days)" or (h=="Timeliness"):
                    continue
                if isinstance(val, datetime.date):
                    ws.write_datetime(er,c, datetime.datetime(val.year,val.month,val.day), F["date"])
                elif isinstance(val,(int,float)):
                    ws.write_number(er,c,val, F["td" if False else "cell"])
                else:
                    ws.write(er,c, val, F["cell_l"] if c in (4,5) else F["cell"])
            # auto-calc percentage formulas
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
            # incident ageing
            if spec["key"]=="incident":
                ci=headers.index("Ageing (Days)")
                dt=xl_rowcol_to_cell(er,headers.index("Date"))
                cl=xl_rowcol_to_cell(er,headers.index("Closure Date"))
                st=xl_rowcol_to_cell(er,headers.index("Status"))
                ws.write_formula(er,ci,'=IF(%s="Closed",%s-%s,TODAY()-%s)'%(st,cl,dt,dt),F["cell_calcn"],0)
            if spec["key"]=="ca":
                ci=headers.index("Timeliness")
                cd=xl_rowcol_to_cell(er,headers.index("Completion Date"))
                du=xl_rowcol_to_cell(er,headers.index("Due Date"))
                st=xl_rowcol_to_cell(er,headers.index("Status"))
                ws.write_formula(er,ci,'=IF(%s="Closed",IF(%s<=%s,"On-Time","Delayed"),"Pending")'%(st,cd,du),F["cell_l"],0)
        last=D0-1+max(len(rows),1)
        ws.add_table(2,0,last,nc-1, {"name":"t_"+spec["key"],"style":"Table Style Medium 9",
            "columns":[{"header":h} for h in headers]})
        for i,h in enumerate(headers):
            ws.set_column(i,i, max(9,min(24,len(h)+2)))
        ws.freeze_panes(3,0); ws.set_zoom(90)
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
            ws.write(r,1,lbl,F["set_lbl"]); ws.write(r,2,val,F["set_val"]); r+=1
        r+=1; r=block(r,"EHS CALCULATION PARAMETERS")
        params=[("Total Man-Hours Worked (annual)",1000000,"Avg employees × hours worked","Manhours"),
                ("TRIR Multiplier",200000,"OSHA standard = 200,000","TRIRmult"),
                ("LTIFR Multiplier",1000000,"Per million man-hours","LTIFRmult")]
        for lbl,val,note,name in params:
            ws.write(r,1,lbl,F["set_lbl"]); ws.write_number(r,2,val,F["set_val"])
            ws.write(r,3,note,F["set_note"])
            self.wb.define_name(name,"=Settings!$C$%d"%(r+1)); r+=1
        r+=1; r=block(r,"TARGETS / RAG THRESHOLDS")
        tg=[("Observation Closure Target",0.9,"Green if ≥ target","TgtObs"),
            ("Training Compliance Target",0.95,"","TgtTrain"),
            ("Corrective Action Closure Target",0.9,"","TgtCA"),
            ("TRIR Target (max acceptable)",1.0,"Green if actual ≤ target","TgtTRIR"),
            ("RAG Amber band (fraction of target)",0.8,"Below this vs target = Red","AmberBand")]
        for lbl,val,note,name in tg:
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
        self._exec_engine(ws, r)
        r += 92
        # ---- per-register calc blocks ----
        cur=r
        for spec in HD.REGISTERS:
            self.RR[spec["key"]]=self._register_calc(ws, spec, cur)
            cur += 17
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
        """Period-aware executive engine: 12-month series + Cur/Prior masks + variance."""
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
        nmonths_cur="SUMPRODUCT(%s)"%curmask.replace("Calculations!","Calculations!")

        # ---- 12-month series matrix (col F=5 onward) ----
        scol={}; c0=5
        def series(name, per_month):
            nonlocal c0
            ws.write(hr-1,c0,name,F["th"])
            for i,mn in enumerate(MONTHS):
                ws.write_formula(hr+i,c0,"="+per_month(mn),F["tdn"],0)
            scol[name]="Calculations!$%s$%d:$%s$%d"%(xl_col_to_name(c0),hr+1,xl_col_to_name(c0),hr+12)
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
        series("disc", rcount("disc"))
        s_nc=spec_of("nc")
        series("nc_open", lambda mn:'COUNTIFS(%s,"Open",%s,"%s",%s,dCrit)+COUNTIFS(%s,"Overdue",%s,"%s",%s,dCrit)'%(
            rng(s_nc,"Status"),rng(s_nc,"Month"),mn,rng(s_nc,"Department"),rng(s_nc,"Status"),rng(s_nc,"Month"),mn,rng(s_nc,"Department")))
        series("training_total", rcount("training"))
        series("train_completed", rstatus("training","Status","Completed"))
        series("obs_total", rcount("hseobs"))
        series("obs_closed", rstatus("hseobs","Status","Closed"))
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
        series("ca_closed", rstatus("ca","Status","Closed"))
        series("jsa", rcount("jsa"))
        series("meetings", rcount("meetings"))
        s_ua=spec_of("unsafeact"); s_uc=spec_of("unsafecond")
        series("unsafe_reports", lambda mn:'COUNTIFS(%s,"%s",%s,dCrit)+COUNTIFS(%s,"%s",%s,dCrit)'%(
            rng(s_ua,"Month"),mn,rng(s_ua,"Department"),rng(s_uc,"Month"),mn,rng(s_uc,"Department")))

        MH="Manhours"; nmc="SUM(%s)"%curmask; nmp="SUM(%s)"%prmask
        def sp(series_name,mask): return "SUMPRODUCT(%s,%s)"%(scol[series_name],mask)
        # ---- Exec KPI variance table ----
        kt=r0+2; kc=31   # far-right column block for the KPI table (AF..)
        ws.write(kt-1,kc,"Executive KPI (period variance)",F["bodyb"])
        heads=["KPI","Band","Cur","Prior","Delta%","Good"]
        for j,h in enumerate(heads): ws.write(kt,kc+j,h,F["th"])
        # (label, band, kind, polarity, kind_of_calc, args)
        KP=[
         ("TRIR","Lagging","dec",-1,"trir",None),
         ("LTIFR","Lagging","dec",-1,"ltifr",None),
         ("Total Incidents","Lagging","num",-1,"sum","totalinc"),
         ("Recordable","Lagging","num",-1,"sum","recordable"),
         ("LTI + Fatality","Lagging","num",-1,"sum","ltifat"),
         ("Near Miss","Lagging","num",-1,"sum","nearmiss"),
         ("First Aid","Lagging","num",-1,"sum","firstaid"),
         ("Lost Days","Lagging","num",-1,"sum","lostdays"),
         ("Disciplinary","Lagging","num",-1,"sum","disc"),
         ("Open NCs","Lagging","num",-1,"sum","nc_open"),
         ("Trainings","Leading","num",1,"sum","training_total"),
         ("Training Compliance","Leading","pct",1,"ratio",("train_completed","training_total")),
         ("HSE Observations","Leading","num",1,"sum","obs_total"),
         ("Obs Closure","Leading","pct",1,"ratio",("obs_closed","obs_total")),
         ("Toolbox Talks","Leading","num",1,"sum","toolbox"),
         ("Inspections","Leading","num",1,"sum","inspections"),
         ("Audits","Leading","num",1,"sum","audits"),
         ("PTW Compliance","Leading","pct",1,"ratio",("ptw_compliant","ptw_total")),
         ("Emergency Drills","Leading","num",1,"sum","drills"),
         ("CA Closure","Leading","pct",1,"ratio",("ca_closed","ca_total")),
        ]
        def calc(kind,args,mask,nm):
            if kind=="sum": return sp(args,mask)
            if kind=="ratio": return "IFERROR(%s/%s,0)*100"%(sp(args[0],mask),sp(args[1],mask))
            if kind=="trir": return "IFERROR(%s*TRIRmult/(%s*Manhours/12),0)"%(sp("recordable",mask),nm)
            if kind=="ltifr": return "IFERROR(%s*LTIFRmult/(%s*Manhours/12),0)"%(sp("ltifat",mask),nm)
        EX={}
        names={"TRIR":"TRIR","LTIFR":"LTIFR","Total Incidents":"TotalInc","Recordable":"Recordable",
               "Near Miss":"NearMiss","Lost Days":"LostDays","LTI + Fatality":"LTIfat",
               "Training Compliance":"TrainCompliance","Obs Closure":"ObsClosure","CA Closure":"CAClosure",
               "PTW Compliance":"PTWauditComp"}
        for i,(lbl,band,kind,pol,ck,args) in enumerate(KP):
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
            EX[lbl]={"cur":"Calculations!%s"%cur,"prior":"Calculations!%s"%pri,
                     "delta":"Calculations!$%s$%d"%(xl_col_to_name(kc+4),rr+1),
                     "good":goodcell,"goodname":gname,"band":band,"kind":kind}
            if lbl in names: self.wb.define_name(names[lbl],"=Calculations!%s"%cur)
        self.EX=EX
        # ---- gauge helper cells (value/2, remainder, hidden 50) ----
        gauges=[("Training",EX["Training Compliance"]["cur"]),("PTW Audit",EX["PTW Compliance"]["cur"]),
                ("Obs Closure",EX["Obs Closure"]["cur"]),("CA Closure",EX["CA Closure"]["cur"])]
        g0=kt+22
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
        pr=kt; pc=kc+7
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
        # RAG scorecard
        rg=gr+len(lag)+2; rc=pc
        ws.write(rg-1,rc,"RAG",F["th"]); ws.write(rg-1,rc+1,"Act",F["th"]); ws.write(rg-1,rc+2,"Tgt",F["th"]); ws.write(rg-1,rc+3,"Status",F["th"])
        rag=[("TRIR","TRIR","TgtTRIR",True),("Obs Closure","ObsClosure","TgtObs",False),
             ("Training","TrainCompliance","TgtTrain",False),("CA Closure","CAClosure","TgtCA",False)]
        for i,(l,act,tgt,low) in enumerate(rag):
            rr=rg+i; ws.write(rr,rc,l,F["tdl"])
            if low:
                ws.write_formula(rr,rc+1,"="+act,F["td"],0); ws.write_formula(rr,rc+2,"="+tgt,F["td"],0)
                ws.write_formula(rr,rc+3,'=IF(%s<=%s,"🟢 GREEN",IF(%s<=%s/AmberBand,"🟡 AMBER","🔴 RED"))'%(act,tgt,act,tgt),F["tdl"],0)
            else:
                ws.write_formula(rr,rc+1,"=%s/100"%act,F["td"],0); ws.write_formula(rr,rc+2,"="+tgt,F["td"],0)
                ws.write_formula(rr,rc+3,'=IF(%s/100>=%s,"🟢 GREEN",IF(%s/100>=%s*AmberBand,"🟡 AMBER","🔴 RED"))'%(act,tgt,act,tgt),F["tdl"],0)
        self.RR["_rag"]={"first":rg,"last":rg+3,"c":rc}

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
        # status breakdown (col H/I)
        st=spec.get("status")
        if st and st in headers:
            svals=HD.POOLS.get(st) or self._distinct(spec,st)
            svals=svals[:6]
            ws.write(sr,7,st,F["th"]); ws.write(sr,8,"Count",F["th"])
            for i,v in enumerate(svals):
                ws.write(sr+1+i,7,v,F["tdl"])
                ws.write_formula(sr+1+i,8,'=COUNTIFS(%s,"%s",%s,mCrit%s)'%(rng(spec,st),v,Mn,dsuf()),F["tdn"],0)
            out["st_lbl"]=self._a1(sr+1,7,sr+len(svals)); out["st_val"]=self._a1(sr+1,8,sr+len(svals))
        # KPI scalars (col K label, L value)
        kc=10
        kpis=self._kpi_defs(spec)
        ws.write(sr,kc,"KPI",F["th"]); ws.write(sr,kc+1,"Value",F["th"])
        out["kpi"]=[]
        for i,(lbl,formula,kind) in enumerate(kpis):
            ws.write(sr+1+i,kc,lbl,F["tdl"])
            nf={"num":F["tdn"],"pct":F["tdp"]}[kind]
            ws.write_formula(sr+1+i,kc+1,"="+formula,nf,0)
            out["kpi"].append((lbl,"Calculations!$%s$%d"%(xl_col_to_name(kc+1),sr+2+i),kind))
        return out

    def _kpi_defs(self, spec):
        headers=spec["headers"]; Mn=rng(spec,"Month")
        dep=has(spec,"Department"); Dp=rng(spec,"Department") if dep else None
        dsuf=(",%s,dCrit"%Dp) if dep else ""
        total='COUNTIFS(%s,mCrit%s)'%(Mn,dsuf)
        kpis=[("Total Records", total,"num")]
        st=spec.get("status")
        if st and st in headers:
            svals=HD.POOLS.get(st,HD.STATUS)
            closed=[v for v in svals if v in CLOSED_VALUES] or [svals[0]]
            cf="+".join('COUNTIFS(%s,"%s",%s,mCrit%s)'%(rng(spec,st),v,Mn,dsuf) for v in closed)
            kpis.append(("Closed / Completed %","IFERROR((%s)/%s*100,0)"%(cf,total),"pct"))
            op=[v for v in svals if v in OPEN_VALUES]
            if op:
                of="+".join('COUNTIFS(%s,"%s",%s,mCrit%s)'%(rng(spec,st),v,Mn,dsuf) for v in op)
                kpis.append(("Open / Pending","%s"%of,"num"))
        # metric
        auto=spec.get("auto",{})
        if auto:
            pc=list(auto.keys())[0]
            kpis.append(("Avg "+pc,"IFERROR(AVERAGEIFS(%s,%s,mCrit%s),0)"%(rng(spec,pc),Mn,dsuf),"pct"))
        elif has(spec,"Non-Conformances"):
            kpis.append(("Total Non-Conformances","SUMIFS(%s,%s,mCrit%s)"%(rng(spec,"Non-Conformances"),Mn,dsuf),"num"))
        elif has(spec,"Minor NC") and has(spec,"Major NC"):
            kpis.append(("Total NCs","SUMIFS(%s,%s,mCrit%s)+SUMIFS(%s,%s,mCrit%s)"%(
                rng(spec,"Minor NC"),Mn,dsuf,rng(spec,"Major NC"),Mn,dsuf),"num"))
        elif has(spec,"Lost Days"):
            kpis.append(("Total Lost Days","SUMIFS(%s,%s,mCrit%s)"%(rng(spec,"Lost Days"),Mn,dsuf),"num"))
        return kpis[:4]

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
