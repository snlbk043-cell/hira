"""Dashboards for the Integrated EHS Management System."""
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell
import hse_data as HD
from hse_build import (BLUE_D,BLUE_M,BLUE_L,GREY_D,GREY_M,GREY_L,GREEN,GREEN_L,
                       AMBER,AMBER_L,RED,RED_L,WHITE,INK,ACCENT,ACC, spec_of)

MONTHS=HD.MONTHS

def dash_name(spec): return "Dash · "+spec["sheet"]

# --------------------------------------------------------------------------
def build(e):
    build_cover(e)
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

def vtile(e, ws, r, c, label, ex, kind, accent, w=3, drillsheet=None):
    """RCPL-style KPI card with period variance (▲/▼ + Δ% vs prior, polarity-coloured),
    optionally hyperlinked to a tracker dashboard for drill-down."""
    strip,tt,vv,ss=e.cardfmt(accent, kind)
    ws.merge_range(r,c,r,c+w-1,"",strip); ws.set_row(r,4)
    if drillsheet:
        ws.merge_range(r+1,c,r+1,c+w-1,"",tt)
        ws.write_url(r+1,c,"internal:'%s'!A1"%dash_name(spec_of(drillsheet)),tt,label.upper())
    else:
        ws.merge_range(r+1,c,r+1,c+w-1,label.upper(),tt)
    ws.merge_range(r+2,c,r+3,c+w-1,"="+ex["cur"],vv)
    vgood=e._fmt(font_name="Segoe UI",font_size=8,bold=True,font_color=GREEN,bg_color=WHITE,align="left",
        valign="vcenter",left=1,right=1,bottom=1,border_color="#E2E8F0")
    ws.merge_range(r+4,c,r+4,c+w-1,
        '=IF(%s=0,IF(%s>0,"▲ new","● flat"),IF(%s=%s,"● flat",'
        '(IF(%s>%s,"▲ ","▼ "))&TEXT(ABS(%s),"0.0%%")&" vs prior"))'%(
        ex["prior"],ex["cur"],ex["cur"],ex["prior"],ex["cur"],ex["prior"],ex["delta"]),
        vgood)
    ws.conditional_format(r+4,c,r+4,c+w-1,{"type":"formula","criteria":"=%s<0"%ex["goodname"],
        "format":e._fmt(font_name="Segoe UI",font_size=8,bold=True,font_color=RED,bg_color=WHITE,
        align="left",valign="vcenter",left=1,right=1,bottom=1,border_color="#E2E8F0")})

def place_chart(e, ws, r, c, ch, w=470, h=260):
    ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)

# ---- Cover Page (for the Board Pack PDF export) --------------------------
def build_cover(e):
    F=e.F; ws=e.wb.add_worksheet("Cover Page"); ws.set_tab_color(BLUE_D)
    ws.hide_gridlines(2); ws.set_column("A:A",3); ws.set_column("B:M",10); ws.set_zoom(100)
    big=e._fmt(font_name="Segoe UI",font_size=32,bold=True,font_color=WHITE,bg_color=BLUE_D,align="center",valign="vcenter")
    sub=e._fmt(font_name="Segoe UI",font_size=13,font_color="#CFE0F0",bg_color=BLUE_D,align="center",valign="vcenter")
    ws.set_row(2,10)
    for r in range(0,16): ws.set_row(r,26)
    ws.merge_range("B4:M9","",big); ws.write_url("B4","internal:'Home'!A1",big,"RCPL INTEGRATED EHS MANAGEMENT SYSTEM")
    ws.merge_range("B10:M11","Executive Safety Board Pack  ·  Reliance Consumer Products Ltd  ·  Campa Cola CSD Plant",sub)
    ws.merge_range("B12:M12","",F["accent"])
    ws.write("F14","Prepared for:",F["refl"]); ws.write("H14","Plant Head / Leadership Team",F["bodyb"])
    ws.write("F15","Report period:",F["refl"]); ws.write_formula("H15","=SelPeriod",F["bodyb"],0)
    ws.write("F16","Generated:",F["refl"]); ws.write_formula("H16","=LastRefresh",F["refv"],0)
    r=18
    ws.merge_range(r,3,r,9,"HEADLINE SAFETY PERFORMANCE",F["section"]); r+=1
    ex=e.EX
    heads=[("TRIR",ex["TRIR"]["cur"],"dec"),("LTIFR",ex["LTIFR"]["cur"],"dec"),
           ("Total Incidents",ex["Total Incidents"]["cur"],"num"),
           ("Training Compliance",ex["Training Compliance"]["cur"],"pct")]
    for i,(lbl,cell,kind) in enumerate(heads):
        cc=3+i*3
        strip,tt,vv,ss=e.cardfmt(["red","red","amber","green"][i],kind)
        ws.merge_range(r,cc,r,cc+2,"",strip); ws.set_row(r,4)
        ws.merge_range(r+1,cc,r+1,cc+2,lbl.upper(),tt)
        ws.merge_range(r+2,cc,r+3,cc+2,"="+cell,vv)
        ws.merge_range(r+4,cc,r+4,cc+2,"",ss)
    r+=7
    ws.merge_range(r,3,r+3,9,
        "This board pack combines the Executive Dashboard and Leadership Review into a single "
        "PDF via the ExportBoardPack macro (Home). Every figure is live at the moment of export.",
        F["note"])

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
    # advanced-analysis action buttons
    btnrow=13
    ws.set_row(btnrow,32)
    ws.insert_button(btnrow,1,{"macro":"BuildPivotAnalysis","caption":"📊 Build Pivot Analysis (native PivotTables + Slicers)",
        "width":270,"height":26,"x_offset":2,"y_offset":4})
    ws.insert_button(btnrow,5,{"macro":"ExportBoardPack","caption":"📦 Export Board Pack PDF",
        "width":180,"height":26,"x_offset":2,"y_offset":4})
    ws.insert_button(btnrow,8,{"macro":"UnprotectAllSheets","caption":"🔓 Unlock Sheets to Edit",
        "width":170,"height":26,"x_offset":2,"y_offset":4})
    # register + dashboard index (two columns: tracker name -> register | dashboard)
    ws.merge_range("B15:M15","TRACKER REGISTERS & DASHBOARDS  (click either link)",F["section"])
    lblf=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=INK,bg_color=GREY_L,
        align="left",valign="vcenter",border=1,border_color=WHITE)
    linkf=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=BLUE_D,bg_color=BLUE_L,
        align="center",valign="vcenter",border=1,border_color=WHITE,underline=True)
    r=16
    for i,spec in enumerate(HD.REGISTERS):
        rr=16+(i//2); base=1+(i%2)*9
        ws.merge_range(rr,base,rr,base+3,"%s  %s"%(spec["emoji"],spec["sheet"]),lblf)
        ws.merge_range(rr,base+4,rr,base+5,"",linkf); ws.write_url(rr,base+4,"internal:'%s'!A1"%spec["sheet"],linkf,"Register")
        ws.merge_range(rr,base+6,rr,base+7,"",linkf); ws.write_url(rr,base+6,"internal:'%s'!A1"%dash_name(spec),linkf,"Dashboard")
    last=16+((len(HD.REGISTERS)-1)//2)
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
        "Set your man-hours & targets on the Settings sheet, choose a Period (month/quarter) & Department on "
        "the Executive Dashboard, add rows to any register and click ⟳ Refresh — no manual updates required.",F["note"])

# ---- Executive -----------------------------------------------------------
LAGGING_CARDS = ["TRIR","LTIFR","Total Incidents","Recordable","LTI + Fatality","Near Miss",
    "First Aid","Lost Days","Disciplinary","Open NCs","NC Closure","Alcohol Positive %"]
LEADING_CARDS = ["Toolbox Talks","Toolbox Avg Attendance","JSA Assessments","JSA % Approved",
    "Trainings","Training Compliance","HSE Observations","Obs Closure",
    "Workplace Inspections","Workplace Insp. Closure","Equipment Inspections","Equipment Critical Findings",
    "Safety Walkthroughs","Safety Meetings","Meetings Close-out","Safety Bulletins","Bulletin Reach",
    "Emergency Drills","Drill Participation","Internal Audits","Internal Audit NCs",
    "External Audits","External Audit NCs","Management Visits","Mgmt Visit Close-out",
    "Management Reviews","Mgmt Review Attendance","Safety Awards","Stop Work Authority",
    "Alcohol Tests","PTW Audits","PTW Compliance","Corrective Actions","CA Closure",
    "Unsafe Acts Reported","Unsafe Act Closure","Unsafe Conditions Reported","Unsafe Condition Closure"]

DRILL_MAP = {
    "Toolbox Talks":"toolbox","Toolbox Avg Attendance":"toolbox","JSA Assessments":"jsa","JSA % Approved":"jsa",
    "Trainings":"training","Training Compliance":"training","HSE Observations":"hseobs","Obs Closure":"hseobs",
    "Workplace Inspections":"wpinsp","Workplace Insp. Closure":"wpinsp","Equipment Inspections":"eqinsp",
    "Equipment Critical Findings":"eqinsp","Safety Walkthroughs":"walk","Safety Meetings":"meetings",
    "Meetings Close-out":"meetings","Safety Bulletins":"bulletins","Bulletin Reach":"bulletins",
    "Emergency Drills":"drills","Drill Participation":"drills","Internal Audits":"iaudit",
    "Internal Audit NCs":"iaudit","External Audits":"eaudit","External Audit NCs":"eaudit",
    "Management Visits":"mgmtvisit","Mgmt Visit Close-out":"mgmtvisit","Management Reviews":"mgmtreview",
    "Mgmt Review Attendance":"mgmtreview","Safety Awards":"awards","Stop Work Authority":"swa",
    "Alcohol Tests":"alcohol","Alcohol Positive %":"alcohol","PTW Audits":"ptwaudit","PTW Compliance":"ptwaudit",
    "Corrective Actions":"ca","CA Closure":"ca","Unsafe Acts Reported":"unsafeact","Unsafe Act Closure":"unsafeact",
    "Unsafe Conditions Reported":"unsafecond","Unsafe Condition Closure":"unsafecond",
    "Disciplinary":"disc","Open NCs":"nc","NC Closure":"nc",
    "Total Incidents":"incident","Recordable":"incident","LTI + Fatality":"incident","Near Miss":"incident",
    "First Aid":"incident","Lost Days":"incident","TRIR":"incident","LTIFR":"incident",
}

def build_exec(e):
    F=e.F; RR=e.RR; EX=e.EX; ws=e.wb.add_worksheet("Executive Dashboard"); ws.set_tab_color(BLUE_D)
    gridcols(ws); ws.set_zoom(75)
    row=header(e,ws,"🏆","EXECUTIVE EHS DASHBOARD","All 24 trackers  ·  Leading vs Lagging  ·  period-on-period variance")
    row=navchips(e,ws,row)
    # filters : Period (month/quarter) + Department drive the whole sheet
    ws.merge_range(row,1,row,18,"FILTERS  ·  select a period to compare against the previous period",F["section"]); row+=1
    ws.write(row,1,"Period",F["th"]); ws.merge_range(row,2,row,3,"Jun",e.F["set_val"])
    e.wb.define_name("SelPeriod","='Executive Dashboard'!$C$%d"%(row+1))
    ws.data_validation(row,2,row,2,{"validate":"list","source":"=F_Period"})
    ws.write(row,5,"Department",F["th"]); ws.merge_range(row,6,row,7,"All",e.F["set_val"])
    e.wb.define_name("SelDept","='Executive Dashboard'!$G$%d"%(row+1))
    ws.data_validation(row,6,row,6,{"validate":"list","source":"=F_Dept"})
    # register-month filter (drives per-tracker dashboards + the cross-tracker analytics section)
    ws.write(row,9,"Register Month",F["th"]); ws.merge_range(row,10,row,11,"All",e.F["set_val"])
    e.wb.define_name("SelMonth","='Executive Dashboard'!$K$%d"%(row+1))
    ws.data_validation(row,10,row,10,{"validate":"list","source":"=F_Month"})
    ws.merge_range(row,13,row,18,"Period drives the KPI wall vs prior. Register Month drives cross-tracker analytics & all 24 tracker dashboards.",F["note"])
    row+=2

    # ===== LAGGING band: every reactive/outcome tracker =====
    lagband=e._fmt(font_name="Segoe UI",font_size=12,bold=True,font_color=WHITE,bg_color=RED,
        align="left",valign="vcenter",indent=1)
    ws.merge_range(row,1,row,18,"🟥  LAGGING INDICATORS  —  reactive outcomes (lower is better)  ·  click a card to drill down",lagband)
    ws.set_row(row,20); row+=1
    row=_cardwall(e,ws,row,LAGGING_CARDS,"red")
    row+=1

    # ===== LEADING band: every proactive tracker =====
    leadband=e._fmt(font_name="Segoe UI",font_size=12,bold=True,font_color=WHITE,bg_color=GREEN,
        align="left",valign="vcenter",indent=1)
    ws.merge_range(row,1,row,18,"🟩  LEADING INDICATORS  —  proactive activity across all trackers (higher is better)  ·  click a card to drill down",leadband)
    ws.set_row(row,20); row+=1
    row=_cardwall(e,ws,row,LEADING_CARDS,"green")
    row+=1

    # ===== FULL RCPL EXECUTIVE CHART SUITE =====
    ws.merge_range(row,1,row,18,"MONTHLY TRENDS",F["section"]); row+=1
    MS=e.MSER
    c1=e.line_chart(_months(e),MS["totalinc"],"Monthly Incident Trend",BLUE_D)
    c2=e.col_chart(_months(e),[("First Aid",MS["firstaid"],AMBER)],"First Aid Trend")
    c3=e.col_chart(_months(e),[("Near Miss",MS["nearmiss"],GREEN)],"Near Miss Trend")
    place_chart(e,ws,row,1,c1,486,280); place_chart(e,ws,row,7,c2,486,280); place_chart(e,ws,row,13,c3,486,280)
    row+=15
    c4=e.line_chart(_months(e),MS["trir_m"],"TRIR Trend",RED)
    c4b=e.wb.add_chart({"type":"line"})
    c4b.add_series({"name":"LTIFR","categories":_months(e),"values":MS["ltifr_m"],"y2_axis":True,
        "line":{"color":ACCENT,"width":2.25},"marker":{"type":"circle","size":5,"fill":{"color":ACCENT}}})
    c4.combine(c4b); c4.set_y2_axis({"num_font":{"size":8}})
    c4.set_title({"name":"TRIR & LTIFR Trend (dual-axis)","name_font":{"name":"Segoe UI","size":10.5,"bold":True,"color":BLUE_D}})
    c5=e.col_chart(_months(e),[("Unsafe Act",MS["ua_m"],AMBER),("Unsafe Condition",MS["uc_m"],BLUE_M)],
        "Unsafe Act vs Unsafe Condition",stacked=True)
    c6=e.dough(RR["incident"]["cat_lbl"],RR["incident"]["cat_val"],"Incident Classification",
        [RED,"#EA580C",AMBER,"#EAB308",GREEN,BLUE_M])
    place_chart(e,ws,row,1,c4,486,280); place_chart(e,ws,row,7,c5,486,280); place_chart(e,ws,row,13,c6,486,280)
    row+=15
    area=e.wb.add_chart({"type":"area"})
    area.add_series({"categories":_months(e),"values":MS["obs_total"],"fill":{"color":BLUE_M,"transparency":40},"border":{"color":BLUE_M}})
    e._style(area,"Safety Observation Trend"); area.set_legend({"none":True})
    c8=e.bar_chart(RR["_pareto_lbl"],RR["_pareto_val"],"Root Cause Analysis",BLUE_M)
    c8b=e.wb.add_chart({"type":"line"})
    c8b.add_series({"name":"Cumulative %","categories":RR["_pareto_lbl"],"values":RR["_pareto_cum"],"y2_axis":True,
        "line":{"color":ACCENT,"width":2}})
    c9=e.bar_chart(RR["_dept_lbl"],RR["_dept_val"],"Department-wise Safety Score",BLUE_M)
    place_chart(e,ws,row,1,area,486,280); place_chart(e,ws,row,7,c8,486,280); place_chart(e,ws,row,13,c9,486,280)
    row+=15

    ws.merge_range(row,1,row,18,"RISK PROFILE & TOP-10 ANALYSIS",F["section"]); row+=1
    radar=e.wb.add_chart({"type":"radar","subtype":"with_markers"})
    radar.add_series({"categories":RR["_radar_lbl"],"values":RR["_radar_val"],"line":{"color":BLUE_M,"width":2},
        "fill":{"color":BLUE_L,"transparency":30},"marker":{"type":"circle","size":5,"fill":{"color":BLUE_D}}})
    e._style(radar,"Monthly Performance Profile"); radar.set_legend({"none":True})
    heat_note = e._fmt(font_name="Segoe UI",font_size=9,italic=True,font_color=GREY_M)
    ct1=e.bar_chart(RR["_topact_lbl"],RR["_topact_val"],"Top 10 Unsafe Acts",AMBER)
    ct2=e.bar_chart(RR["_topcond_lbl"],RR["_topcond_val"],"Top 10 Unsafe Conditions",RED)
    place_chart(e,ws,row,1,radar,486,300); place_chart(e,ws,row,7,ct1,486,300); place_chart(e,ws,row,13,ct2,486,300)
    row+=17
    ct3=e.bar_chart(RR["_toparea_lbl"],RR["_toparea_val"],"Top 10 High-Risk Areas",ACCENT)
    place_chart(e,ws,row,1,ct3,486,300)
    ws.merge_range(row,7,row+1,18,"Risk Heat Map (Risk Level × Department) — see 'Calculations' sheet, range: %s (auto colour-scaled green→red)"%RR["_heat_range"],F["note"])
    row+=17

    ws.merge_range(row,1,row,18,"COMPLIANCE GAUGES  ·  cross-tracker leading vs lagging",F["section"]); row+=1
    for i,(name,info) in enumerate(e.GAUGE.items()):
        g=_gauge(e,info["range"],name); g.set_size({"width":250,"height":180}); ws.insert_chart(row,1+i*3,g)
        gv=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=BLUE_D,align="center",valign="vcenter",num_format='0.0"%"')
        ws.merge_range(row+8,1+i*3,row+8,1+i*3+2,"="+info["val"],gv)
    row+=11
    lb=e.bar_chart(RR["_leading"]["lbl"],RR["_leading"]["val"],"Leading Activity Volume (period)",GREEN)
    la=e.bar_chart(RR["_lagging"]["lbl"],RR["_lagging"]["val"],"Lagging Outcomes (period)",RED)
    py=e.bar_chart(RR["_pyramid"]["lbl"],RR["_pyramid"]["val"],"Incident Pyramid (Heinrich)",ACCENT)
    place_chart(e,ws,row,1,lb,486,290); place_chart(e,ws,row,7,la,486,290); place_chart(e,ws,row,13,py,486,290)
    row+=16

    # RAG scorecard
    ws.merge_range(row,1,row,8,"RAG COMPLIANCE SCORECARD",F["section"]); row+=1
    cols=[1,3,5,7]
    for j,h in enumerate(["Metric","Actual","Target","Status"]):
        ws.merge_range(row,cols[j],row,cols[j]+1,h,F["th"])
    rag=RR["_rag"]; c=rag["c"]
    L=xl_col_to_name(c); A=xl_col_to_name(c+1); T=xl_col_to_name(c+2); S=xl_col_to_name(c+3)
    n_rag=rag["last"]-rag["first"]+1
    for i in range(n_rag):
        er=rag["first"]+i+1; rr=row+1+i
        ws.merge_range(rr,1,rr,2,"=Calculations!$%s$%d"%(L,er),F["tdl"])
        ws.merge_range(rr,3,rr,4,"=Calculations!$%s$%d"%(A,er),F["td"])
        ws.merge_range(rr,5,rr,6,"=Calculations!$%s$%d"%(T,er),F["td"])
        ws.merge_range(rr,7,rr,8,"=Calculations!$%s$%d"%(S,er),F["tdl"])

def _months(e):
    return e._month_cat_range

def _cardwall(e, ws, row, labels, accentdefault):
    """place a wall of variance KPI cards, 6 per row, each drilling to its tracker dashboard."""
    for i,lbl in enumerate(labels):
        rr=row+(i//6)*6; cc=1+(i%6)*3
        ex=e.EX[lbl]
        kind=ex["kind"]
        vtile(e,ws,rr,cc,lbl,ex,kind,accentdefault,w=3,drillsheet=DRILL_MAP.get(lbl))
    return row+((len(labels)-1)//6+1)*6

def _gauge(e, rng3, title):
    """half-doughnut gauge from a 3-cell range (value/2, remainder, hidden 50)."""
    ch=e.wb.add_chart({"type":"doughnut"})
    ch.add_series({"values":rng3,
        "points":[{"fill":{"color":GREEN}},{"fill":{"color":GREY_L}},{"fill":{"none":True}}]})
    ch.set_rotation(270); ch.set_hole_size(62); ch.set_legend({"none":True})
    ch.set_title({"name":title,"name_font":{"size":9.5,"bold":True,"color":BLUE_D}})
    ch.set_chartarea({"border":{"none":True},"fill":{"none":True}})
    return ch

# ---- Leadership ----------------------------------------------------------
def build_leadership(e):
    F=e.F; RR=e.RR; ws=e.wb.add_worksheet("Leadership Review"); ws.set_tab_color(ACCENT)
    gridcols(ws); ws.set_zoom(85)
    row=header(e,ws,"🧭","EXECUTIVE LEADERSHIP REVIEW","Monthly corporate safety scorecard  ·  prepared for Plant Head")
    row=navchips(e,ws,row)
    ws.merge_range(row,1,row,18,"CORPORATE SAFETY SCORECARD",F["section"]); row+=1
    # use EX cur/prior values (already period-aware) for consistency
    ex=e.EX
    row=_leadership_tiles(e,ws,row,[
        ("TRIR",ex["TRIR"],"dec","red"),("LTIFR",ex["LTIFR"],"dec","red"),
        ("Recordable",ex["Recordable"],"num","amber"),("Lost Days",ex["Lost Days"],"num","red"),
        ("Obs Closure %",ex["Obs Closure"],"pct","green"),("Training %",ex["Training Compliance"],"pct","green"),
        ("CA Closure %",ex["CA Closure"],"pct","green"),("Near Miss",ex["Near Miss"],"num","blue"),
    ])
    ws.merge_range(row,1,row,18,"INCIDENT PROFILE & LEADING ACTIVITY",F["section"]); row+=1
    ch1=e.dough(RR["_pyramid"]["lbl"],RR["_pyramid"]["val"],"Incident Severity Mix",
                [RED,"#EA580C",AMBER,"#EAB308",GREEN,BLUE_M,GREY_M])
    ch2=e.col_chart(RR["_inctrend"]["lbl"],[("Incidents",RR["_inctrend"]["val"],ACCENT)],"12-Month Incident Trend")
    ch3=e.bar_chart(RR["_leading"]["lbl"],RR["_leading"]["val"],"Leading Indicators",GREEN)
    place_chart(e,ws,row,1,ch1,486,300); place_chart(e,ws,row,7,ch2,486,300); place_chart(e,ws,row,13,ch3,486,300)

def _leadership_tiles(e, ws, row, defs):
    for i,(lbl,ex,kind,acc) in enumerate(defs):
        rr=row+(i//4)*6; cc=1+(i%4)*4
        vtile(e,ws,rr,cc,lbl,ex,kind,acc,w=4)
    return row+((len(defs)-1)//4+1)*6

# ---- per-register dashboard (rich HSE-Full-System analysis layout) ------
def build_register_dash(e, spec):
    F=e.F; RR=e.RR[spec["key"]]; ws=e.wb.add_worksheet(dash_name(spec)); ws.set_tab_color(BLUE_M)
    gridcols(ws); ws.set_zoom(82)
    row=header(e,ws,spec["emoji"],spec["sheet"].upper()+" PERFORMANCE",
               "Live data from the %s register  ·  filtered by Register Month & Department"%spec["sheet"])
    row=navchips(e,ws,row,extra=spec["sheet"])

    # 8 KPI tiles, 2 rows x 4
    ws.merge_range(row,1,row,18,"KEY METRICS",F["section"]); row+=1
    kpis=RR["kpi"]
    for i,(lbl,cellref,kind) in enumerate(kpis):
        rr=row+(i//4)*6; cc=1+(i%4)*4
        tile(e,ws,rr,cc,lbl,"="+cellref,kind,["blue","green","amber","red"][i%4],w=4)
    row=row+((len(kpis)-1)//4+1)*6

    # Monthly Volume + Primary Category Breakdown
    ws.merge_range(row,1,row,18,"MONTHLY VOLUME & CATEGORY BREAKDOWN",F["section"]); row+=1
    charts=[]
    charts.append(e.col_chart(RR["month_lbl"],[("Volume",RR["month_val"],BLUE_M)],"Monthly Volume"))
    if "cat_val" in RR:
        charts.append(e.bar_chart(RR["cat_lbl"],RR["cat_val"],"Breakdown by %s"%spec.get("cat"),GREEN))
    if "cat2_val" in RR:
        charts.append(e.dough(RR["cat2_lbl"],RR["cat2_val"],"%s Distribution"%spec.get("cat2"),
            [BLUE_M,GREEN,AMBER,RED,GREY_M,"#8B5CF6","#EAB308","#0EA5E9"]))
    elif "st_val" in RR:
        charts.append(e.dough(RR["st_lbl"],RR["st_val"],"Status Distribution",
            [AMBER,BLUE_M,GREEN,RED,GREY_M,"#8B5CF6"]))
    cols=[1,7,13]
    for i,ch in enumerate(charts[:3]):
        place_chart(e,ws,row,cols[i],ch,486,290)
    row+=16

    # Department Performance + Status Distribution (if not already used above)
    ws.merge_range(row,1,row,18,"DEPARTMENT PERFORMANCE",F["section"]); row+=1
    charts2=[]
    if "dept_val" in RR:
        charts2.append(e.bar_chart(RR["dept_lbl"],RR["dept_val"],"Department Volume",BLUE_M))
    if "cat2_val" in RR and "st_val" in RR:
        charts2.append(e.dough(RR["st_lbl"],RR["st_val"],"Status Distribution",
            [AMBER,BLUE_M,GREEN,RED,GREY_M,"#8B5CF6"]))
    for i,ch in enumerate(charts2[:2]):
        place_chart(e,ws,row,1+i*6,ch,486,290)
    # Department table alongside (real numbers, not just chart)
    if "dept_lbl" in RR:
        ws.merge_range(row,13,row,18,"Department table → Calculations sheet, row %s"%RR["dept_lbl"].split("$")[2],F["note"])
    row+=16

    # Monthly Performance Matrix (rows=measures, cols=Jan..Dec+YTD) - live table, not a chart
    ws.merge_range(row,1,row,18,"MONTHLY PERFORMANCE MATRIX",F["section"]); row+=1
    _matrix_table(e, ws, row, spec, RR)

def _matrix_table(e, ws, row, spec, RR):
    F=e.F
    top=RR.get("matrix_top")
    if top is None: return
    headers=["Metric"]+MONTHS+["YTD"]
    for j,h in enumerate(headers):
        ws.write(row,1+j,h,F["th"])
    calc_sheet="Calculations"
    mc0=20
    for i in range(6):
        rr=row+1+i
        srcrow=top+1+i
        # mirror the label + 12 months + YTD via formula reference (keeps this sheet live)
        ws.write_formula(rr,1,"=IF(%s!$%s$%d=\"\",\"\",%s!$%s$%d)"%(
            calc_sheet,xl_col_to_name(mc0),srcrow+1,calc_sheet,xl_col_to_name(mc0),srcrow+1),F["tdl"],0)
        for j in range(13):
            cL=xl_col_to_name(mc0+1+j)
            ws.write_formula(rr,2+j,"=IFERROR(%s!$%s$%d,\"\")"%(calc_sheet,cL,srcrow+1),F["tdn"],0)
