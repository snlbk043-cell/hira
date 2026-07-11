"""Dashboards for the Integrated EHS Management System."""
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell
import hse_data as HD
from hse_build import (BLUE_D,BLUE_M,BLUE_L,GREY_D,GREY_M,GREY_L,GREEN,GREEN_L,
                       AMBER,AMBER_L,RED,RED_L,WHITE,INK,ACCENT,ACC, spec_of)

MONTHS=HD.MONTHS

def dash_name(spec): return "Dash · "+spec["sheet"]

# --------------------------------------------------------------------------
def build(e):
    build_home(e)
    build_exec(e)
    build_leadership(e)
    for spec in HD.REGISTERS:
        build_register_dash(e, spec)

# ---- shared pieces -------------------------------------------------------
def gridcols(ws):
    ws.set_column("A:A",2.0)
    for c in range(1,19): ws.set_column(c,c,8.8)

def header(e, ws, emoji, title, subtitle):
    F=e.F; ws.hide_gridlines(2); ws.set_row(0,6)
    ws.merge_range(1,1,3,12, "%s  %s"%(emoji,title), F["title"])
    ws.merge_range(4,1,4,12, subtitle, F["sub"])
    logo=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=ACCENT,bg_color=WHITE,
        align="center",valign="vcenter",border=2,border_color=WHITE)
    ws.merge_range(1,13,4,18,"RCPL  ·  campa", logo)
    ws.merge_range(5,1,5,18,"",F["accent"]); ws.set_row(5,3)
    ws.write(6,14,"Last Refresh:",F["refl"]); ws.write_formula(6,16,"=LastRefresh",F["refv"],0)
    btns=[("⟳ Refresh","RefreshAllData"),("⟲ Reset","ResetFilters"),("⌂ Home","GoHome"),
          ("🖨 Print","PrintDashboard"),("PDF","ExportDashboardPDF")]
    x=1
    for cap,mac in btns:
        ws.insert_button(6,x,{"macro":mac,"caption":cap,"width":96,"height":24,"x_offset":2,"y_offset":2}); x+=2
    return 8

def navchips(e, ws, row, extra=None):
    F=e.F
    chip=e._fmt(font_name="Segoe UI",font_size=9,bold=True,font_color=WHITE,bg_color=BLUE_M,
        align="center",valign="vcenter",border=1,border_color=WHITE)
    ws.write_url(row,1,"internal:'Home'!A1",chip,"⌂ Home")
    ws.write_url(row,2,"internal:'Executive Dashboard'!A1",chip,"Executive")
    ws.merge_range(row,3,row,4,"",chip); ws.write_url(row,3,"internal:'Leadership Review'!A1",chip,"Leadership")
    if extra:
        ws.merge_range(row,5,row,7,"",chip); ws.write_url(row,5,"internal:'%s'!A1"%extra,chip,"◀ Register")
    return row+2

def tile(e, ws, r, c, label, valformula, kind, accent, w=3):
    strip,tt,vv,ss=e.cardfmt(accent, kind)
    ws.merge_range(r,c,r,c+w-1,"",strip); ws.set_row(r,4)
    ws.merge_range(r+1,c,r+1,c+w-1,label.upper(),tt)
    ws.merge_range(r+2,c,r+3,c+w-1,valformula,vv)
    ws.merge_range(r+4,c,r+4,c+w-1,"live · auto-calculated",ss)

def place_chart(e, ws, r, c, ch, w=470, h=260):
    ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)

# ---- Home ----------------------------------------------------------------
def build_home(e):
    F=e.F; ws=e.wb.add_worksheet("Home"); ws.set_tab_color(BLUE_D)
    ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:M",11); ws.set_zoom(100)
    ws.set_row(1,8)
    big=e._fmt(font_name="Segoe UI",font_size=30,bold=True,font_color=WHITE,bg_color=BLUE_D,align="center",valign="vcenter")
    sub=e._fmt(font_name="Segoe UI",font_size=12,font_color="#CFE0F0",bg_color=BLUE_D,align="center",valign="vcenter")
    ws.merge_range("B3:M5","RCPL INTEGRATED EHS MANAGEMENT SYSTEM",big)
    ws.merge_range("B6:M7","Reliance Consumer Products Ltd  ·  Campa Cola CSD Plant  ·  24 Registers · 24 Dashboards",sub)
    ws.merge_range("B8:M8","",F["accent"]); ws.set_row(7,4)
    import datetime
    ws.write("I10","Last Refresh:",F["refl"]); ws.write_datetime("K10",datetime.datetime.now(),F["refv"])
    e.wb.define_name("LastRefresh","='Home'!$K$10")
    # top-level nav
    ws.merge_range("B11:M11","EXECUTIVE VIEWS",F["section"])
    tilef=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=WHITE,bg_color=BLUE_D,
        align="center",valign="vcenter",border=2,border_color=WHITE)
    tilef2=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=WHITE,bg_color=ACCENT,
        align="center",valign="vcenter",border=2,border_color=WHITE)
    ws.merge_range("B12:F13","",tilef); ws.write_url("B12","internal:'Executive Dashboard'!A1",tilef,"🏆  EXECUTIVE DASHBOARD")
    ws.merge_range("H12:M13","",tilef2); ws.write_url("H12","internal:'Leadership Review'!A1",tilef2,"🧭  LEADERSHIP REVIEW")
    # register dashboards grid
    ws.merge_range("B15:M15","REGISTER DASHBOARDS  (click to open)",F["section"])
    cell=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=BLUE_D,bg_color=BLUE_L,
        align="left",valign="vcenter",border=1,border_color=WHITE,underline=True)
    r=16
    for i,spec in enumerate(HD.REGISTERS):
        rr=16+(i//3)*1; cc=1+(i%3)*4
        if i%3==0 and i>0: pass
        rr=16+(i//3); cc=1+(i%3)*4
        ws.merge_range(rr,cc,rr,cc+3,"",cell)
        ws.write_url(rr,cc,"internal:'%s'!A1"%dash_name(spec),cell,"%s  %s"%(spec["emoji"],spec["sheet"]))
    last=16+((len(HD.REGISTERS)-1)//3)
    # data & docs
    r2=last+2
    ws.merge_range(r2,1,r2,12,"DATA & CONFIGURATION",F["section"]); r2+=1
    links=[("Master Data","Master Data"),("Settings","Settings"),("Help","Help"),
           ("Calculations","Calculations"),("Incident Register","Incident"),("Corrective Actions","Corrective Actions")]
    lf=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=GREY_D,bg_color=GREY_L,
        align="center",valign="vcenter",border=1,border_color=WHITE,underline=True)
    for i,(cap,sh) in enumerate(links):
        rr=r2+(i//3); cc=1+(i%3)*4
        ws.merge_range(rr,cc,rr,cc+3,"",lf); ws.write_url(rr,cc,"internal:'%s'!A1"%sh,lf,cap)
    r3=r2+((len(links)-1)//3)+2
    ws.merge_range(r3,1,r3+2,12,
        "Fully dynamic: every KPI, chart and RAG status recalculates automatically from the 24 registers. "
        "Set your man-hours & targets on the Settings sheet, filter by Month/Department on the Executive Dashboard, "
        "add rows to any register and click ⟳ Refresh — no manual updates required.",F["note"])

# ---- Executive -----------------------------------------------------------
def build_exec(e):
    F=e.F; RR=e.RR; ws=e.wb.add_worksheet("Executive Dashboard"); ws.set_tab_color(BLUE_D)
    gridcols(ws); ws.set_zoom(80)
    row=header(e,ws,"🏆","EXECUTIVE EHS DASHBOARD","Corporate leading & lagging indicators  ·  Campa CSD Plant")
    row=navchips(e,ws,row)
    # filters
    ws.merge_range(row,1,row,18,"GLOBAL FILTERS",F["section"]); row+=1
    ws.write(row,1,"Month",F["th"]); ws.merge_range(row,2,row,3,"All",e.F["set_val"])
    e.wb.define_name("SelMonth","='Executive Dashboard'!$C$%d"%(row+1))
    ws.data_validation(row,2,row,2,{"validate":"list","source":"=F_Month"})
    ws.write(row,5,"Department",F["th"]); ws.merge_range(row,6,row,7,"All",e.F["set_val"])
    e.wb.define_name("SelDept","='Executive Dashboard'!$G$%d"%(row+1))
    ws.data_validation(row,6,row,6,{"validate":"list","source":"=F_Dept"})
    ws.merge_range(row,9,row,18,"Man-hours & RAG targets are configured on the Settings sheet.",F["note"])
    row+=2
    # KPI tiles
    ws.merge_range(row,1,row,18,"KEY PERFORMANCE INDICATORS",F["section"]); row+=1
    tiles=[("TRIR","=TRIR","dec","red"),("LTIFR","=LTIFR","dec","red"),
           ("Total Incidents","=TotalInc","num","amber"),("Near Miss","=NearMiss","num","blue"),
           ("Obs Closure %","=ObsClosure","pct","green"),("Training Compliance %","=TrainCompliance","pct","green"),
           ("CA Closure %","=CAClosure","pct","green"),("Lost Days","=LostDays","num","red")]
    for i,(lbl,f,k,a) in enumerate(tiles):
        rr=row+(i//4)*6; cc=1+(i%4)*4
        tile(e,ws,rr,cc,lbl,f,k,a,w=4)
    row=row+12
    # charts
    ws.merge_range(row,1,row,18,"INCIDENT ANALYTICS",F["section"]); row+=1
    ch1=e.col_chart(RR["_inctrend"]["lbl"],[("Incidents",RR["_inctrend"]["val"],BLUE_M)],"12-Month Incident Trend")
    ch2=e.bar_chart(RR["_pyramid"]["lbl"],RR["_pyramid"]["val"],"Incident Pyramid (Heinrich)",ACCENT)
    ch3=e.bar_chart(RR["_leading"]["lbl"],RR["_leading"]["val"],"Leading Indicators (Activity Volume)",GREEN)
    place_chart(e,ws,row,1,ch1,486,290); place_chart(e,ws,row,7,ch2,486,290); place_chart(e,ws,row,13,ch3,486,290)
    row+=16
    # RAG scorecard mirrored from Calculations
    ws.merge_range(row,1,row,10,"RAG COMPLIANCE SCORECARD",F["section"]); row+=1
    for j,h in enumerate(["Metric","Actual","Target","Status"]):
        ws.write(row,1+j*2 if False else 1+j*2,h,F["th"])
    # header cells at cols B,D,F,H
    cols=[1,3,5,7]
    for j,h in enumerate(["Metric","Actual","Target","Status"]):
        ws.merge_range(row,cols[j],row,cols[j]+1,h,F["th"])
    rag=RR["_rag"]; c=rag["c"]
    lblcol=xl_col_to_name(c); actcol=xl_col_to_name(c+1); tgtcol=xl_col_to_name(c+2); stcol=xl_col_to_name(c+3)
    for i in range(4):
        er=rag["first"]+i+1  # excel row
        rr=row+1+i
        ws.merge_range(rr,1,rr,2,"","");
        ws.write_formula(rr,1,"=Calculations!$%s$%d"%(lblcol,er),F["tdl"],0)
        ws.merge_range(rr,3,rr,4,"","")
        ws.write_formula(rr,3,"=Calculations!$%s$%d"%(actcol,er),F["td"],0)
        ws.merge_range(rr,5,rr,6,"","")
        ws.write_formula(rr,5,"=Calculations!$%s$%d"%(tgtcol,er),F["td"],0)
        ws.merge_range(rr,7,rr,8,"","")
        ws.write_formula(rr,7,"=Calculations!$%s$%d"%(stcol,er),F["tdl"],0)

# ---- Leadership ----------------------------------------------------------
def build_leadership(e):
    F=e.F; RR=e.RR; ws=e.wb.add_worksheet("Leadership Review"); ws.set_tab_color(ACCENT)
    gridcols(ws); ws.set_zoom(85)
    row=header(e,ws,"🧭","EXECUTIVE LEADERSHIP REVIEW","Monthly corporate safety scorecard  ·  prepared for Plant Head")
    row=navchips(e,ws,row)
    ws.merge_range(row,1,row,18,"CORPORATE SAFETY SCORECARD",F["section"]); row+=1
    tiles=[("TRIR","=TRIR","dec","red"),("LTIFR","=LTIFR","dec","red"),
           ("Recordable","=Recordable","num","amber"),("Lost Days","=LostDays","num","red"),
           ("Obs Closure %","=ObsClosure","pct","green"),("Training %","=TrainCompliance","pct","green"),
           ("CA Closure %","=CAClosure","pct","green"),("Near Miss","=NearMiss","num","blue")]
    for i,(lbl,f,k,a) in enumerate(tiles):
        rr=row+(i//4)*6; cc=1+(i%4)*4
        tile(e,ws,rr,cc,lbl,f,k,a,w=4)
    row=row+12
    ws.merge_range(row,1,row,18,"INCIDENT PROFILE & LEADING ACTIVITY",F["section"]); row+=1
    ch1=e.dough(RR["_pyramid"]["lbl"],RR["_pyramid"]["val"],"Incident Severity Mix",
                [RED,"#EA580C",AMBER,"#EAB308",GREEN,BLUE_M,GREY_M])
    ch2=e.col_chart(RR["_inctrend"]["lbl"],[("Incidents",RR["_inctrend"]["val"],ACCENT)],"12-Month Incident Trend")
    ch3=e.bar_chart(RR["_leading"]["lbl"],RR["_leading"]["val"],"Leading Indicators",GREEN)
    place_chart(e,ws,row,1,ch1,486,300); place_chart(e,ws,row,7,ch2,486,300); place_chart(e,ws,row,13,ch3,486,300)

# ---- per-register dashboard ---------------------------------------------
def build_register_dash(e, spec):
    F=e.F; RR=e.RR[spec["key"]]; ws=e.wb.add_worksheet(dash_name(spec)); ws.set_tab_color(BLUE_M)
    gridcols(ws); ws.set_zoom(85)
    row=header(e,ws,spec["emoji"],spec["sheet"].upper()+" DASHBOARD",
               "Live from the %s register  ·  filtered by Month & Department"%spec["sheet"])
    row=navchips(e,ws,row,extra=spec["sheet"])
    ws.merge_range(row,1,row,18,"KEY METRICS",F["section"]); row+=1
    for i,(lbl,cellref,kind) in enumerate(RR["kpi"]):
        cc=1+(i%4)*4
        tile(e,ws,row,cc,lbl,"="+cellref,kind,["blue","green","amber","red"][i%4],w=4)
    row=row+6
    ws.merge_range(row,1,row,18,"ANALYTICS",F["section"]); row+=1
    charts=[]
    charts.append(e.col_chart(RR["month_lbl"],[("Volume",RR["month_val"],BLUE_M)],"Monthly Volume"))
    if "cat_val" in RR:
        charts.append(e.bar_chart(RR["cat_lbl"],RR["cat_val"],"Breakdown by %s"%spec.get("cat"),GREEN))
    if "st_val" in RR:
        charts.append(e.dough(RR["st_lbl"],RR["st_val"],"Status Distribution",
            [AMBER,BLUE_M,GREEN,RED,GREY_M,"#8B5CF6"]))
    cols=[1,7,13]
    for i,ch in enumerate(charts[:3]):
        place_chart(e,ws,row,cols[i],ch,486,300)
