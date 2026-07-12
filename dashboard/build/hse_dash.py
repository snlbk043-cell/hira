"""Dashboards for the Integrated EHS Management System."""
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell
import hse_data as HD
from hse_build import (BLUE_D,BLUE_M,BLUE_L,GREY_D,GREY_M,GREY_L,GREEN,GREEN_L,
                       AMBER,AMBER_L,RED,RED_L,WHITE,INK,ACCENT,ACC,
                       NAVY_BG,NAVY_CARD,NAVY_CARD2,BORDER,TEAL,GOLD,PURPLE,CORAL,ORANGE,TXT,TXT_MUTED,DACC,
                       spec_of, rng, has)

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
def gridcols(ws, e=None):
    bg = e.FD["bg"] if e else None
    ws.set_column("A:A",2.0,bg)
    for c in range(1,19): ws.set_column(c,c,8.8,bg)

def header(e, ws, emoji, title, subtitle):
    F=e.FD; ws.hide_gridlines(2); ws.set_row(0,6)
    ws.merge_range(1,1,3,12, "%s  %s"%(emoji,title), F["title"])
    ws.merge_range(4,1,4,12, subtitle, F["sub"])
    logo=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=NAVY_BG,bg_color=TEAL,
        align="center",valign="vcenter",border=2,border_color=NAVY_BG)
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
    F=e.FD
    chip=e._fmt(font_name="Segoe UI",font_size=9,bold=True,font_color=NAVY_BG,bg_color=TEAL,
        align="center",valign="vcenter",border=1,border_color=NAVY_BG)
    ws.write_url(row,1,"internal:'Home'!A1",chip,"⌂ Home")
    ws.write_url(row,2,"internal:'Executive Dashboard'!A1",chip,"Executive")
    ws.merge_range(row,3,row,4,"",chip); ws.write_url(row,3,"internal:'Leadership Review'!A1",chip,"Leadership")
    if extra:
        ws.merge_range(row,5,row,7,"",chip); ws.write_url(row,5,"internal:'%s'!A1"%extra,chip,"◀ Register")
    return row+2

def tile(e, ws, r, c, label, valformula, kind, accent, w=3):
    strip,tt,vv,ss=e.cardfmt_dark(accent, kind)
    ws.merge_range(r,c,r,c+w-1,"",strip); ws.set_row(r,4)
    ws.merge_range(r+1,c,r+1,c+w-1,label.upper(),tt)
    ws.merge_range(r+2,c,r+3,c+w-1,valformula,vv)
    ws.merge_range(r+4,c,r+4,c+w-1,"live · auto-calculated",ss)

def vtile(e, ws, r, c, label, ex, kind, accent, w=3, drillsheet=None):
    """RCPL-style KPI card: strip colour = live RAG-vs-target status, number = current value,
    corner = prior value, bottom row = period-on-period variance (▲/▼, polarity-coloured),
    plus a 12-month sparkline. Optionally hyperlinked to a tracker dashboard for drill-down."""
    strip,tt,vv,ss=e.cardfmt_dark(accent, kind)
    neutral=e._fmt(bg_color=BORDER)
    ws.merge_range(r,c,r,c+w-1,"",neutral); ws.set_row(r,4)
    if "rag" in ex:
        ws.conditional_format(r,c,r,c+w-1,{"type":"formula","criteria":"=%s=2"%ex["ragname"],
            "format":e._fmt(bg_color=GREEN)})
        ws.conditional_format(r,c,r,c+w-1,{"type":"formula","criteria":"=%s=1"%ex["ragname"],
            "format":e._fmt(bg_color=AMBER)})
        ws.conditional_format(r,c,r,c+w-1,{"type":"formula","criteria":"=%s=0"%ex["ragname"],
            "format":e._fmt(bg_color=RED)})
    if drillsheet:
        ws.merge_range(r+1,c,r+1,c+w-1,"",tt)
        ws.write_url(r+1,c,"internal:'%s'!A1"%dash_name(spec_of(drillsheet)),tt,label.upper())
    else:
        ws.merge_range(r+1,c,r+1,c+w-1,label.upper(),tt)
    ws.merge_range(r+2,c,r+3,c+w-2,"="+ex["cur"],vv)
    if "spark" in ex:
        ws.write_blank(r+3,c+w-1,"",vv)
        ws.add_sparkline(r+3,c+w-1,{"range":ex["spark"],"type":"line",
            "series_color":ACC[accent],"high_point":True,"low_point":True})
    vgood=e._fmt(font_name="Segoe UI",font_size=8,bold=True,font_color=GREEN,bg_color=NAVY_CARD,align="left",
        valign="vcenter",left=1,right=1,bottom=1,border_color=BORDER)
    ws.merge_range(r+4,c,r+4,c+w-1,
        '=IF(%s=0,IF(%s>0,"▲ new","● flat"),IF(%s=%s,"● flat",'
        '(IF(%s>%s,"▲ ","▼ "))&TEXT(ABS(%s),"0.0%%")&" vs prior"))'%(
        ex["prior"],ex["cur"],ex["cur"],ex["prior"],ex["cur"],ex["prior"],ex["delta"]),
        vgood)
    ws.conditional_format(r+4,c,r+4,c+w-1,{"type":"formula","criteria":"=%s<0"%ex["goodname"],
        "format":e._fmt(font_name="Segoe UI",font_size=8,bold=True,font_color=RED,bg_color=NAVY_CARD,
        align="left",valign="vcenter",left=1,right=1,bottom=1,border_color=BORDER)})

def print_setup(ws, last_row=60, last_col=18):
    """Landscape, fit-to-1-page-wide, bounded print area so PDF/Print exports read as clean pages."""
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, last_row, last_col)
    ws.set_margins(left=0.3, right=0.3, top=0.4, bottom=0.4)

def place_chart(e, ws, r, c, ch, w=470, h=260):
    ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)

# ---- Cover Page (for the Board Pack PDF export) --------------------------
def build_cover(e):
    F=e.FD; ws=e.wb.add_worksheet("Cover Page"); ws.set_tab_color(TEAL)
    ws.hide_gridlines(2); ws.set_column("A:A",3,F["bg"]); ws.set_column("B:M",10,F["bg"]); ws.set_zoom(100)
    big=e._fmt(font_name="Segoe UI",font_size=32,bold=True,font_color=TXT,bg_color=NAVY_CARD,align="center",valign="vcenter")
    sub=e._fmt(font_name="Segoe UI",font_size=13,font_color=TEAL,bg_color=NAVY_CARD,align="center",valign="vcenter")
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
        strip,tt,vv,ss=e.cardfmt_dark(["red","red","amber","green"][i],kind)
        ws.merge_range(r,cc,r,cc+2,"",strip); ws.set_row(r,4)
        ws.merge_range(r+1,cc,r+1,cc+2,lbl.upper(),tt)
        ws.merge_range(r+2,cc,r+3,cc+2,"="+cell,vv)
        ws.merge_range(r+4,cc,r+4,cc+2,"",ss)
    r+=7
    ws.merge_range(r,3,r+3,9,
        "This board pack combines the Executive Dashboard and Leadership Review into a single "
        "PDF via the ExportBoardPack macro (Home). Every figure is live at the moment of export.",
        F["note"])
    print_setup(ws, last_row=r+5, last_col=12)

# ---- Home ----------------------------------------------------------------
def build_home(e):
    F=e.FD; ws=e.wb.add_worksheet("Home"); ws.set_tab_color(TEAL)
    ws.hide_gridlines(2); ws.set_column("A:A",2,F["bg"]); ws.set_column("B:M",11,F["bg"]); ws.set_zoom(100)
    ws.set_row(1,8)
    big=e._fmt(font_name="Segoe UI",font_size=30,bold=True,font_color=TXT,bg_color=NAVY_CARD,align="center",valign="vcenter")
    sub=e._fmt(font_name="Segoe UI",font_size=12,font_color=TEAL,bg_color=NAVY_CARD,align="center",valign="vcenter")
    ws.merge_range("B3:M5","RCPL INTEGRATED EHS MANAGEMENT SYSTEM",big)
    ws.merge_range("B6:M7","Reliance Consumer Products Ltd  ·  Campa Cola CSD Plant  ·  25 Registers · 25 Dashboards",sub)
    ws.merge_range("B8:M8","",F["accent"]); ws.set_row(7,4)
    import datetime
    ws.write("I10","Last Refresh:",F["refl"]); ws.write_datetime("K10",datetime.datetime.now(),F["refv"])
    e.wb.define_name("LastRefresh","='Home'!$K$10")
    # top-level nav
    ws.merge_range("B11:M11","EXECUTIVE VIEWS",F["section"])
    tilef=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=NAVY_BG,bg_color=TEAL,
        align="center",valign="vcenter",border=2,border_color=NAVY_BG)
    tilef2=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=NAVY_BG,bg_color=CORAL,
        align="center",valign="vcenter",border=2,border_color=NAVY_BG)
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
    ws.insert_button(btnrow,11,{"macro":"BuildTrackerSlicers","caption":"🎚 Add Tracker Slicers",
        "width":170,"height":26,"x_offset":2,"y_offset":4})
    btnrow2=btnrow+1
    ws.set_row(btnrow2,32)
    ws.insert_button(btnrow2,1,{"macro":"BuildActionTracker","caption":"🗂 Build Action Tracker (all overdue items)",
        "width":270,"height":26,"x_offset":2,"y_offset":4})
    ws.insert_button(btnrow2,5,{"macro":"SendOverdueAlerts","caption":"📧 Draft Overdue Alerts (Outlook)",
        "width":210,"height":26,"x_offset":2,"y_offset":4})
    ws.insert_button(btnrow2,9,{"macro":"ExportDepartmentReport","caption":"📄 Export Department Report",
        "width":210,"height":26,"x_offset":2,"y_offset":4})
    # register + dashboard index (two columns: tracker name -> register | dashboard)
    ws.merge_range("B16:M16","TRACKER REGISTERS & DASHBOARDS  (click either link)",F["section"])
    lblf=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=TXT,bg_color=NAVY_CARD,
        align="left",valign="vcenter",border=1,border_color=BORDER)
    linkf=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=NAVY_BG,bg_color=TEAL,
        align="center",valign="vcenter",border=1,border_color=BORDER,underline=True)
    r=17
    for i,spec in enumerate(HD.REGISTERS):
        rr=17+(i//2); base=1+(i%2)*9
        ws.merge_range(rr,base,rr,base+3,"%s  %s"%(spec["emoji"],spec["sheet"]),lblf)
        ws.merge_range(rr,base+4,rr,base+5,"",linkf); ws.write_url(rr,base+4,"internal:'%s'!A1"%spec["sheet"],linkf,"Register")
        ws.merge_range(rr,base+6,rr,base+7,"",linkf); ws.write_url(rr,base+6,"internal:'%s'!A1"%dash_name(spec),linkf,"Dashboard")
    last=17+((len(HD.REGISTERS)-1)//2)
    # data & docs
    r2=last+2
    ws.merge_range(r2,1,r2,12,"DATA & CONFIGURATION",F["section"]); r2+=1
    links=[("Master Data","Master Data"),("Settings","Settings"),("Help","Help"),
           ("Calculations","Calculations"),("Incident Register","Incident"),("Corrective Actions","Corrective Actions"),
           ("Data Quality","Data Quality"),("Investigation Log","Investigation Log")]
    lf=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=TXT_MUTED,bg_color=NAVY_CARD,
        align="center",valign="vcenter",border=1,border_color=BORDER,underline=True)
    for i,(cap,sh) in enumerate(links):
        rr=r2+(i//3); cc=1+(i%3)*4
        ws.merge_range(rr,cc,rr,cc+3,"",lf); ws.write_url(rr,cc,"internal:'%s'!A1"%sh,lf,cap)
    r3=r2+((len(links)-1)//3)+2
    ws.merge_range(r3,1,r3+2,12,
        "Fully dynamic: every KPI, chart and RAG status recalculates automatically from the 25 registers. "
        "Set your man-hours & targets on the Settings sheet, choose a Period (month/quarter) & Department on "
        "the Executive Dashboard, add rows to any register and click ⟳ Refresh — no manual updates required.",F["note"])
    print_setup(ws, last_row=r3+5, last_col=12)

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

# one representative EX label per tracker, for the Leadership "System Health" radar -
# prefers a closure/compliance-rate metric (a real health signal) over a raw count
TRACKER_HEALTH_LABEL = {
    "toolbox":"Toolbox Avg Attendance","jsa":"JSA % Approved","training":"Training Compliance",
    "hseobs":"Obs Closure","wpinsp":"Workplace Insp. Closure","eqinsp":"Equipment Critical Findings",
    "walk":"Safety Walkthroughs","meetings":"Meetings Close-out","bulletins":"Bulletin Reach",
    "drills":"Drill Participation","iaudit":"Internal Audit NCs","eaudit":"External Audit NCs",
    "mgmtvisit":"Mgmt Visit Close-out","mgmtreview":"Mgmt Review Attendance","disc":"Disciplinary",
    "awards":"Safety Awards","swa":"Stop Work Authority","alcohol":"Alcohol Positive %",
    "ptwaudit":"PTW Compliance","ca":"CA Closure","nc":"NC Closure","unsafeact":"Unsafe Act Closure",
    "unsafecond":"Unsafe Condition Closure","incident":"TRIR",
}

def _ragname(lbl):
    return "rg"+"".join(ch for ch in lbl if ch.isalnum())

def build_exec(e):
    F=e.FD; RR=e.RR; EX=e.EX; ws=e.wb.add_worksheet("Executive Dashboard"); ws.set_tab_color(TEAL)
    gridcols(ws,e); ws.set_zoom(75)
    row=header(e,ws,"🏆","EXECUTIVE EHS DASHBOARD","All 24 trackers  ·  Leading vs Lagging  ·  period-on-period variance")
    row=navchips(e,ws,row)
    ws.freeze_panes(row,0)
    # filters : Period (month/quarter) + Department drive the whole sheet
    ws.merge_range(row,1,row,18,"FILTERS  ·  select a period to compare against the previous period",F["section"]); row+=1
    ws.write(row,1,"Period",F["th"]); ws.merge_range(row,2,row,3,"Jun",e.FD["set_val"])
    e.wb.define_name("SelPeriod","='Executive Dashboard'!$C$%d"%(row+1))
    ws.data_validation(row,2,row,2,{"validate":"list","source":"=F_Period"})
    ws.write(row,5,"Department",F["th"]); ws.merge_range(row,6,row,7,"All",e.FD["set_val"])
    e.wb.define_name("SelDept","='Executive Dashboard'!$G$%d"%(row+1))
    ws.data_validation(row,6,row,6,{"validate":"list","source":"=F_Dept"})
    # register-month filter (drives per-tracker dashboards + the cross-tracker analytics section)
    ws.write(row,9,"Register Month",F["th"]); ws.merge_range(row,10,row,11,"All",e.FD["set_val"])
    e.wb.define_name("SelMonth","='Executive Dashboard'!$K$%d"%(row+1))
    ws.data_validation(row,10,row,10,{"validate":"list","source":"=F_Month"})
    ws.merge_range(row,13,row,18,"Period drives the KPI wall vs prior. Register Month drives cross-tracker analytics & all 25 tracker dashboards.",F["note"])
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
    c4=e.wb.add_chart({"type":"line"})
    c4.add_series({"name":"TRIR","categories":_months(e),"values":MS["trir_m"],
        "line":{"color":RED,"width":2.25},"marker":{"type":"circle","size":5,"fill":{"color":RED}}})
    c4.add_series({"name":"Industry Benchmark TRIR","categories":_months(e),"values":MS["bench_trir_m"],
        "line":{"color":GREY_M,"width":1.5,"dash_type":"dash"}})
    e._style(c4,"TRIR Trend vs Industry Benchmark")
    c4b=e.wb.add_chart({"type":"line"})
    c4b.add_series({"name":"LTIFR","categories":_months(e),"values":MS["ltifr_m"],"y2_axis":True,
        "line":{"color":ACCENT,"width":2.25},"marker":{"type":"circle","size":5,"fill":{"color":ACCENT}}})
    c4b.add_series({"name":"Industry Benchmark LTIFR","categories":_months(e),"values":MS["bench_ltifr_m"],"y2_axis":True,
        "line":{"color":GREY_D,"width":1.5,"dash_type":"dash"}})
    c4.combine(c4b); c4.set_y2_axis({"num_font":{"size":8}})
    c4.set_title({"name":"TRIR & LTIFR Trend vs Industry Benchmark (dual-axis)","name_font":{"name":"Segoe UI","size":10.5,"bold":True,"color":BLUE_D}})
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
    radar.add_series({"name":"Actual","categories":RR["_radar_lbl"],"values":RR["_radar_val"],
        "line":{"color":BLUE_M,"width":2},"fill":{"color":BLUE_L,"transparency":30},
        "marker":{"type":"circle","size":5,"fill":{"color":BLUE_D}}})
    radar.add_series({"name":"Target","categories":RR["_radar_lbl"],"values":RR["_radar_tgt"],
        "line":{"color":ACCENT,"width":1.5,"dash_type":"dash"},"marker":{"type":"diamond","size":4,"fill":{"color":ACCENT}}})
    e._style(radar,"Compliance Profile: Actual vs Target"); radar.set_legend({"position":"bottom","font":{"size":8}})
    heat_note = e._fmt(font_name="Segoe UI",font_size=9,italic=True,font_color=TXT_MUTED,bg_color=NAVY_BG)
    ct1=e.bar_chart(RR["_topact_lbl"],RR["_topact_val"],"Top 10 Unsafe Acts",AMBER)
    ct2=e.bar_chart(RR["_topcond_lbl"],RR["_topcond_val"],"Top 10 Unsafe Conditions",RED)
    place_chart(e,ws,row,1,radar,486,300); place_chart(e,ws,row,7,ct1,486,300); place_chart(e,ws,row,13,ct2,486,300)
    row+=17
    ct3=e.bar_chart(RR["_toparea_lbl"],RR["_toparea_val"],"Top 10 High-Risk Areas",ACCENT)
    place_chart(e,ws,row,1,ct3,486,300)
    ws.merge_range(row,7,row+1,18,"Risk Heat Map (Risk Level × Department) — see 'Calculations' sheet, range: %s (auto colour-scaled green→red)"%RR["_heat_range"],F["note"])
    row+=17

    row=_risk_matrix_block(e,ws,row)

    ws.merge_range(row,1,row,18,"COMPLIANCE GAUGES  ·  cross-tracker leading vs lagging",F["section"]); row+=1
    for i,(name,info) in enumerate(e.GAUGE.items()):
        g=_gauge(e,info["range"],name); g.set_size({"width":250,"height":180}); ws.insert_chart(row,1+i*3,g)
        gv=e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=GOLD,bg_color=NAVY_CARD2,align="center",valign="vcenter",num_format='0.0"%"')
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
    print_setup(ws, last_row=row+n_rag+3, last_col=18)

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
        "points":[{"fill":{"color":TEAL}},{"fill":{"color":BORDER}},{"fill":{"none":True}}]})
    ch.set_rotation(270); ch.set_hole_size(62); ch.set_legend({"none":True})
    ch.set_title({"name":title,"name_font":{"size":9.5,"bold":True,"color":TXT}})
    ch.set_chartarea({"border":{"none":True},"fill":{"none":True}})
    return ch

def _risk_matrix_block(e, ws, row):
    """A genuine Likelihood x Consequence 5x5 risk matrix (from the JSA Risk Assessment
    register's Likelihood/Consequence fields). Cell colour is a fixed property of the matrix
    design (the risk band for that L x C score, standard 4-band convention) - the number inside
    is a live COUNTIFS count mirrored from the Calculations cross-tab."""
    F=e.FD
    top=e.RR.get("_riskmatrix_top"); c0=e.RR.get("_riskmatrix_c0")
    if top is None: return row
    ws.merge_range(row,1,row,18,
        "TRUE RISK MATRIX  ·  Likelihood × Consequence (JSA Risk Assessment)  ·  colour = fixed risk band, number = live count",
        F["section"]); row+=1
    hdr=e._fmt(font_name="Segoe UI",font_size=9,bold=True,font_color=NAVY_BG,bg_color=TEAL,
        align="center",valign="vcenter",border=1,border_color=NAVY_BG,text_wrap=True)
    corner=e._fmt(font_name="Segoe UI",font_size=8,bold=True,font_color=TXT,bg_color=NAVY_CARD,
        align="center",valign="vcenter",border=1,border_color=BORDER,text_wrap=True)
    hdr_row=row
    ws.merge_range(hdr_row,1,hdr_row,2,"LIKELIHOOD ▼ / CONSEQUENCE ▶",corner)
    cons_labels=["1 Negligible","2 Minor","3 Moderate","4 Major","5 Catastrophic"]
    for j,lbl in enumerate(cons_labels):
        ws.merge_range(hdr_row,3+j*3,hdr_row,5+j*3,lbl,hdr)
    lik_labels={5:"5 Almost Certain",4:"4 Likely",3:"3 Possible",2:"2 Unlikely",1:"1 Rare"}
    def band_fmt(score):
        if score<=4: bg=TEAL
        elif score<=9: bg=GOLD
        elif score<=14: bg=ORANGE
        else: bg=CORAL
        return e._fmt(font_name="Segoe UI",font_size=13,bold=True,font_color=NAVY_BG,bg_color=bg,
            align="center",valign="vcenter",border=1,border_color=NAVY_BG)
    for i in range(5):
        lik=5-i; rr=hdr_row+1+i
        ws.merge_range(rr,1,rr,2,lik_labels[lik],hdr)
        for j in range(5):
            cons=j+1; score=lik*cons
            cellref="Calculations!%s"%xl_rowcol_to_cell(top+i, c0+1+j, True, True)
            ws.merge_range(rr,3+j*3,rr,5+j*3,"="+cellref,band_fmt(score))
    legend=e._fmt(font_name="Segoe UI",font_size=8.5,font_color=TXT_MUTED,bg_color=NAVY_BG,align="left",valign="vcenter")
    lr=hdr_row+6
    ws.merge_range(lr,1,lr,18,
        "🟢 Low (score 1-4)   🟡 Medium (5-9)   🟠 High (10-14)   🔴 Extreme (15-25)   ·  "
        "score = Likelihood × Consequence (both rated 1-5 on the JSA Risk Assessment register)",
        legend)
    return lr+2

# ---- Leadership ----------------------------------------------------------
def build_leadership(e):
    F=e.FD; RR=e.RR; ws=e.wb.add_worksheet("Leadership Review"); ws.set_tab_color(CORAL)
    gridcols(ws,e); ws.set_zoom(85)
    row=header(e,ws,"🧭","EXECUTIVE LEADERSHIP REVIEW","Monthly corporate safety scorecard  ·  prepared for Plant Head")
    row=navchips(e,ws,row)
    ws.freeze_panes(row,0)
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
    row+=16

    # Top Movers - management by exception: biggest improvement / regression this period
    ws.merge_range(row,1,row,18,"TOP MOVERS  ·  biggest change vs prior period, normalised across all 24 trackers",F["section"]); row+=1
    goodf=e._fmt(font_name="Segoe UI",font_size=10,bold=True,font_color=GREEN,bg_color=NAVY_CARD,align="left",valign="vcenter",
        border=1,border_color=BORDER)
    badf=e._fmt(font_name="Segoe UI",font_size=10,bold=True,font_color=RED,bg_color=NAVY_CARD,align="left",valign="vcenter",
        border=1,border_color=BORDER)
    pctf=e._fmt(font_name="Segoe UI",font_size=10,bold=True,font_color=TXT,bg_color=NAVY_CARD,align="center",valign="vcenter",
        border=1,border_color=BORDER,num_format='+0.0%;-0.0%')
    ws.merge_range(row,1,row,4,"🟢 BEST IMPROVEMENT",F["section"]); ws.merge_range(row,7,row,10,"🔴 BIGGEST REGRESSION",F["section"])
    row+=1
    mb=RR["_movers_best"]; mw=RR["_movers_worst"]
    for k in range(3):
        ws.merge_range(row+k,1,row+k,3,"=INDEX(%s,%d)"%(mb["lbl"],k+1),goodf)
        ws.write_formula(row+k,4,"=INDEX(%s,%d)"%(mb["val"],k+1),pctf,0)
        ws.merge_range(row+k,7,row+k,9,"=INDEX(%s,%d)"%(mw["lbl"],k+1),badf)
        ws.write_formula(row+k,10,"=INDEX(%s,%d)"%(mw["val"],k+1),pctf,0)
    row+=6

    # ---- System Health radar: RAG status of all 24 trackers at a glance ----
    ws.merge_range(row,1,row,18,"SYSTEM HEALTH  ·  RAG status of all 24 trackers, at a glance",F["section"]); row+=1
    tbl_top=row
    ws.write(row,1,"Tracker",F["th"]); ws.write(row,2,"Health Metric",F["th"]); ws.write(row,3,"RAG",F["th"])
    keys=list(TRACKER_HEALTH_LABEL.keys())
    for i,k in enumerate(keys):
        lbl=TRACKER_HEALTH_LABEL[k]; s=spec_of(k)
        rr=tbl_top+1+i
        ws.write(rr,1,s["sheet"],F["tdl"]); ws.write(rr,2,lbl,F["tdl"])
        ws.write_formula(rr,3,"="+_ragname(lbl),F["tdn"],0)
    cat_rng="'Leadership Review'!$B$%d:$B$%d"%(tbl_top+2,tbl_top+1+len(keys))
    val_rng="'Leadership Review'!$D$%d:$D$%d"%(tbl_top+2,tbl_top+1+len(keys))
    radar=e.wb.add_chart({"type":"radar","subtype":"with_markers"})
    radar.add_series({"categories":cat_rng,"values":val_rng,"line":{"color":BLUE_M,"width":2},
        "marker":{"type":"circle","size":4,"fill":{"color":BLUE_D}}})
    e._style(radar,"System Health  (0 = Red · 1 = Amber · 2 = Green)")
    radar.set_legend({"none":True}); radar.set_y_axis({"min":0,"max":2,"major_unit":1,"num_font":{"size":8}})
    place_chart(e,ws,tbl_top,7,radar,700,430)
    row=tbl_top+1+len(keys)+2

    # ---- Department League Table: composite score ranking ----
    ws.merge_range(row,1,row,18,
        "DEPARTMENT LEAGUE TABLE  ·  score = avg(Training %, Obs Closure %, CA Closure %) − Recordable×5",F["section"]); row+=1
    lg=e.RR["_league_lbl"]; lv=e.RR["_league_val"]
    raw_dept=e.RR["_league_dept_lbl"]; raw_rec=e.RR["_league_recordable"]
    raw_tr=e.RR["_league_train"]; raw_obs=e.RR["_league_obs"]; raw_ca=e.RR["_league_ca"]
    hdrs=["Rank","Department","Score","Recordable","Training %","Obs Closure %","CA Closure %"]
    for j,h in enumerate(hdrs): ws.write(row,1+j,h,F["th"])
    for i in range(8):
        rr=row+1+i
        ws.write(rr,1,i+1,F["td"])
        ws.write_formula(rr,2,"=INDEX(%s,%d)"%(lg,i+1),F["tdl"],0)
        ws.write_formula(rr,3,"=INDEX(%s,%d)"%(lv,i+1),F["tdn"],0)
        matchidx="MATCH(INDEX(%s,%d),%s,0)"%(lg,i+1,raw_dept)
        ws.write_formula(rr,4,"=INDEX(%s,%s)"%(raw_rec,matchidx),F["tdn"],0)
        ws.write_formula(rr,5,"=INDEX(%s,%s)"%(raw_tr,matchidx),F["tdp"],0)
        ws.write_formula(rr,6,"=INDEX(%s,%s)"%(raw_obs,matchidx),F["tdp"],0)
        ws.write_formula(rr,7,"=INDEX(%s,%s)"%(raw_ca,matchidx),F["tdp"],0)
    ws.conditional_format(row+1,3,row+8,3,{"type":"data_bar","bar_color":GREEN})
    row+=11

    # ---- System-Wide Action Backlog ----
    ws.merge_range(row,1,row,18,
        "SYSTEM-WIDE ACTION BACKLOG  ·  open/overdue items across CA, NC, Inspections & Unsafe Act/Condition registers",F["section"]); row+=1
    c1=e.bar_chart(e.RR["_backlog_tracker_lbl"],e.RR["_backlog_tracker_val"],"Overdue Items by Tracker",RED)
    c2=e.dough(e.RR["_backlog_aging_lbl"],e.RR["_backlog_aging_val"],"Ageing Mix (open items)",[GREEN,AMBER,"#EA580C",RED])
    place_chart(e,ws,row,1,c1,486,290); place_chart(e,ws,row,7,c2,486,290)
    totf=e._fmt(font_name="Segoe UI",font_size=26,bold=True,font_color=CORAL,bg_color=NAVY_BG,align="center",valign="vcenter")
    lblf2=e._fmt(font_name="Segoe UI",font_size=9,bold=True,font_color=TXT_MUTED,bg_color=NAVY_BG,align="center",valign="vcenter")
    ws.merge_range(row,13,row,17,"TOTAL SYSTEM BACKLOG",lblf2)
    ws.merge_range(row+1,13,row+6,17,"="+e.RR["_backlog_total_cell"],totf)
    row+=16

    # ---- Leading:Lagging Ratio trend + Quarterly Trend strip ----
    ws.merge_range(row,1,row,18,"LEADING : LAGGING RATIO  &  QUARTERLY TREND",F["section"]); row+=1
    MS=e.MSER
    c3=e.line_chart(_months(e),MS["leadlag_ratio"],"Leading : Lagging Ratio (12-Month Trend)",GREEN)
    place_chart(e,ws,row,1,c3,486,290)
    qcol=8
    ws.write(row,qcol,"Metric (quarterly)",F["th"])
    for j,q in enumerate(["Q1","Q2","Q3","Q4"]): ws.write(row,qcol+1+j,q,F["th"])
    qmetrics=[("Total Incidents","totalinc",None),
              ("Training Compliance %","train_completed","training_total"),
              ("CA Closure %","ca_closed","ca_total")]
    for i,(lbl,numname,denname) in enumerate(qmetrics):
        rr=row+1+i
        ws.write(rr,qcol,lbl,F["tdl"])
        numparts=_qtr_parts(MS[numname])
        denparts=_qtr_parts(MS[denname]) if denname else None
        for j in range(4):
            if denparts:
                ws.write_formula(rr,qcol+1+j,"=IFERROR(%s/%s*100,0)"%(numparts[j],denparts[j]),F["tdp"],0)
            else:
                ws.write_formula(rr,qcol+1+j,"="+numparts[j],F["tdn"],0)
    row+=16

    # ---- Year-over-Year comparison (current YTD vs Settings' Prior Year Actuals) ----
    ws.merge_range(row,1,row,18,
        "YEAR-OVER-YEAR COMPARISON  ·  current year-to-date vs last year's actuals (enter last year's figures on Settings)",
        F["section"]); row+=1
    ytd_n="IF(CurMonthNo=0,12,CurMonthNo)"
    def ytd_sum(seriesname):
        rngstr=MS[seriesname]
        return "SUM(INDEX(%s,1):INDEX(%s,%s))"%(rngstr,rngstr,ytd_n)
    def ytd_avg(seriesname):
        rngstr=MS[seriesname]
        return "AVERAGE(INDEX(%s,1):INDEX(%s,%s))"%(rngstr,rngstr,ytd_n)
    yoy=[("TRIR",ytd_avg("trir_m"),"PYTRIR","dec"),
         ("LTIFR",ytd_avg("ltifr_m"),"PYLTIFR","dec"),
         ("Total Incidents",ytd_sum("totalinc"),"PYTotalInc","num"),
         ("Training Compliance %","IFERROR(%s/%s*100,0)"%(ytd_sum("train_completed"),ytd_sum("training_total")),"PYTrain","pct"),
         ("Obs Closure %","IFERROR(%s/%s*100,0)"%(ytd_sum("obs_closed"),ytd_sum("obs_total")),"PYObs","pct"),
         ("CA Closure %","IFERROR(%s/%s*100,0)"%(ytd_sum("ca_closed"),ytd_sum("ca_total")),"PYCA","pct")]
    hdrs=["Metric","Current YTD","Prior Year","Δ vs Prior Year"]
    for j,h in enumerate(hdrs): ws.write(row,1+j,h,F["th"])
    for i,(lbl,curf,pyname,kind) in enumerate(yoy):
        rr=row+1+i; nf=F["td"] if kind=="dec" else (F["tdp"] if kind=="pct" else F["tdn"])
        ws.write(rr,1,lbl,F["tdl"])
        ws.write_formula(rr,2,"="+curf,nf,0)
        ws.write_formula(rr,3,"="+pyname,nf,0)
        curcell=xl_rowcol_to_cell(rr,2)
        ws.write_formula(rr,4,'=IF(%s=0,"(enter prior year data)",TEXT((%s-%s)/%s,"+0.0%%;-0.0%%"))'%(
            pyname,curcell,pyname,pyname),F["tdl"],0)
    row+=len(yoy)+3

    # ---- Auto-generated insight bullets ----
    ws.merge_range(row,1,row,18,"KEY INSIGHTS  ·  auto-generated from this period's data",F["section"]); row+=1
    insf=e._fmt(font_name="Segoe UI",font_size=10,font_color=TXT,bg_color=NAVY_CARD,align="left",
        valign="vcenter",text_wrap=True,indent=1,border=1,border_color=BORDER)
    bullets=[
        '="• TRIR is "&TEXT(TRIR,"0.00")&"  ("&TEXT(%s,"+0.0%%;-0.0%%")&" vs the prior period)"'%e.EX["TRIR"]["delta"],
        '="• Department League: "&INDEX(%s,8)&" has the lowest composite safety score this period ("&INDEX(%s,8)&"/100) — review its training, observation-closure and CA-closure rates."'%(lg,lv),
        '="• System-wide backlog: "&%s&" items are currently overdue across CA, NC, Inspections and Unsafe Act/Condition registers; "&INDEX(%s,4)&" have been open more than 30 days."'%(e.RR["_backlog_total_cell"],e.RR["_backlog_aging_val"]),
        '="• Leading:Lagging ratio is "&TEXT(INDEX(%s,12),"0.0")&":1 this month, versus "&TEXT(INDEX(%s,11),"0.0")&":1 last month."'%(MS["leadlag_ratio"],MS["leadlag_ratio"]),
    ]
    for i,b in enumerate(bullets):
        ws.set_row(row+i,28)
        ws.merge_range(row+i,1,row+i,18,b,insf)
    row+=len(bullets)+1

    print_setup(ws, last_row=row+2, last_col=18)

def _qtr_parts(rngstr):
    """Split a 12-cell monthly Calculations range into 4 SUM(Q1..Q4) sub-formula strings."""
    import re
    m=re.match(r"Calculations!\$([A-Z]+)\$(\d+):\$([A-Z]+)\$(\d+)", rngstr)
    col=m.group(1); r1=int(m.group(2))
    parts=[]
    for q in range(4):
        parts.append("SUM(Calculations!$%s$%d:$%s$%d)"%(col,r1+3*q,col,r1+3*q+2))
    return parts

def _leadership_tiles(e, ws, row, defs):
    for i,(lbl,ex,kind,acc) in enumerate(defs):
        rr=row+(i//4)*6; cc=1+(i%4)*4
        vtile(e,ws,rr,cc,lbl,ex,kind,acc,w=4)
    return row+((len(defs)-1)//4+1)*6

# ---- per-register dashboard (rich HSE-Full-System analysis layout) ------
def build_register_dash(e, spec):
    F=e.FD; RR=e.RR[spec["key"]]; ws=e.wb.add_worksheet(dash_name(spec)); ws.set_tab_color(TEAL)
    gridcols(ws,e); ws.set_zoom(82)
    row=header(e,ws,spec["emoji"],spec["sheet"].upper()+" PERFORMANCE",
               "Live data from the %s register  ·  filtered by Register Month & Department"%spec["sheet"])
    row=navchips(e,ws,row,extra=spec["sheet"])
    ws.freeze_panes(row,0)

    # 8 KPI tiles, 2 rows x 4
    ws.merge_range(row,1,row,18,"KEY METRICS",F["section"]); row+=1
    kpis=RR["kpi"]
    for i,(lbl,cellref,kind) in enumerate(kpis):
        rr=row+(i//4)*6; cc=1+(i%4)*4
        tile(e,ws,rr,cc,lbl,"="+cellref,kind,["blue","green","amber","red"][i%4],w=4)
    row=row+((len(kpis)-1)//4+1)*6

    row=_month_delta_row(e, ws, row, RR)

    # Monthly Volume (kept - always a useful activity view) + this tracker's SIGNATURE analysis
    ws.merge_range(row,1,row,18,"MONTHLY VOLUME & SIGNATURE ANALYSIS",F["section"]); row+=1
    charts=[e.col_chart(RR["month_lbl"],[("Volume",RR["month_val"],BLUE_M)],"Monthly Volume")]
    charts.extend(_signature_charts(e, spec, RR))
    cols=[1,7,13]
    heat_placed=False
    for i,ch in enumerate(charts[:3]):
        if ch=="TOOLBOX_HEAT":
            heat_placed=True; continue
        place_chart(e,ws,row,cols[i],ch,486,290)
    row+=16
    if spec["key"]=="toolbox" and "_toolbox_heat_meta" in e.RR:
        ws.merge_range(row,1,row,18,"TOPIC × DEPARTMENT COVERAGE  ·  brighter = more sessions delivered",F["section"]); row+=1
        row=_mirror_heat(e, ws, row, e.RR["_toolbox_heat_meta"], [BLUE_M,GREEN,AMBER,RED,GREY_M])
    if spec["key"]=="jsa":
        row=_risk_matrix_block(e,ws,row)

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
    # live Department Performance table (real numbers, not just a chart), with data bars
    if "dept_top" in RR:
        _dept_table(e, ws, row, RR)
    row+=16

    # Monthly Performance Matrix (rows=measures, cols=Jan..Dec+YTD) - live table, not a chart
    ws.merge_range(row,1,row,18,"MONTHLY PERFORMANCE MATRIX",F["section"]); row+=1
    _matrix_table(e, ws, row, spec, RR)
    row+=9

    row=_advanced_analysis(e, ws, row, spec, RR)
    print_setup(ws, last_row=row+2, last_col=18)

def _month_delta_row(e, ws, row, RR):
    """This-month-vs-last-month delta strip under the KPI cards, using the tracker's own
    Monthly Volume series (independent of the Register Month filter, which already drives
    the KPI cards above) so it always shows a concrete number even when 'All' is selected."""
    F=e.FD; mv=RR["month_val"]
    f=('=IF(CurMonthNo=0,"Select a specific Register Month (Executive Dashboard) to see month-over-month change",'
       'IF(CurMonthNo=1,"Jan is the first month of the year — no in-year prior month to compare",'
       '"This month ("&INDEX(L_Month,CurMonthNo)&"): "&INDEX(%s,CurMonthNo)&"   vs   "&INDEX(L_Month,CurMonthNo-1)&'
       '": "&INDEX(%s,CurMonthNo-1)&"   "&IF(INDEX(%s,CurMonthNo)>=INDEX(%s,CurMonthNo-1),"▲ ","▼ ")&'
       'TEXT(IFERROR((INDEX(%s,CurMonthNo)-INDEX(%s,CurMonthNo-1))/INDEX(%s,CurMonthNo-1),0),"+0.0%%;-0.0%%")))')%(
        mv,mv,mv,mv,mv,mv,mv)
    fmt=e._fmt(font_name="Segoe UI",font_size=9.5,bold=True,font_color=TEAL,bg_color=NAVY_CARD,
        align="left",valign="vcenter",border=1,border_color=BORDER,indent=1)
    ws.merge_range(row,1,row,18,f,fmt)
    return row+2

def _advanced_analysis(e, ws, row, spec, RR):
    """Tracker-specific extras that don't fit the generic 24-tracker template: overdue-ageing
    chart (registers with a due-date field), a repeat-offender department watchlist (registers
    with a severity/risk field), a Target-vs-Actual trend with a next-month forecast (registers
    with both a target and actual field tracked monthly), and cost-impact rollups where a rate
    is configured on Settings. Only emits a section if this tracker has at least one of these."""
    key=spec["key"]; F=e.FD
    AGING_KEYS={"ca","nc","hseobs","wpinsp","eqinsp","walk","unsafeact","unsafecond"}
    HOTSPOT_KEYS={"jsa","hseobs","wpinsp","eqinsp","walk","unsafeact","unsafecond","nc","swa"}
    FORECAST={"toolbox":("fc_toolbox","Attendees"),"bulletins":("fc_bulletins","Reach"),
              "drills":("fc_drills","Participants"),"mgmtreview":("fc_mgmtreview","Attendance")}
    has_aging = key in AGING_KEYS
    has_hotspot = key in HOTSPOT_KEYS
    has_forecast = key in FORECAST
    has_cost = key in ("swa","incident")
    has_certexp = key=="training"
    if not (has_aging or has_hotspot or has_forecast or has_cost or has_certexp):
        return row

    ws.merge_range(row,1,row,18,"ADVANCED ANALYSIS",F["section"]); row+=1

    if has_certexp:
        ce_lbl=e.RR["_cert_expiry_lbl"]; ce_val=e.RR["_cert_expiry_val"]
        for i in range(3):
            tf=e._fmt(font_name="Segoe UI",font_size=8.5,bold=True,font_color=TXT_MUTED,bg_color=NAVY_BG,align="left",valign="vcenter")
            vf=e._fmt(font_name="Segoe UI",font_size=17,bold=True,font_color=GOLD,bg_color=NAVY_BG,align="left",valign="vcenter")
            ws.write_formula(row,1+i*6,"=INDEX(%s,%d)"%(ce_lbl,i+1),tf,0)
            ws.write_formula(row+1,1+i*6,"=INDEX(%s,%d)"%(ce_val,i+1),vf,0)
        row+=3
        ch=e.bar_chart(e.RR["_cert_expiry_dept_lbl"],e.RR["_cert_expiry_dept_val"],
            "Certificates Expiring Within 90 Days, by Department",AMBER)
        place_chart(e,ws,row,1,ch,486,290)
        row+=16
        return row

    charts=[]
    if has_aging:
        charts.append(e.bar_chart(e.RR[key+"_aging_lbl"],e.RR[key+"_aging_val"],"Overdue Ageing (open items)",AMBER))
    if has_forecast:
        tag,label=FORECAST[key]
        charts.append(_forecast_chart(e, tag, label))
    cols=[1,7,13]
    for i,ch in enumerate(charts[:3]):
        place_chart(e,ws,row,cols[i],ch,486,290)
    if charts:
        if has_hotspot and len(charts)<3:
            _hotspot_table(e, ws, row, spec, 1+len(charts)*6)
        row+=16
    elif has_hotspot:
        _hotspot_table(e, ws, row, spec, 1)
        row+=8

    if has_cost:
        row=_cost_tile(e, ws, row, spec)
    return row

def _forecast_chart(e, tag, label):
    """Target vs Actual trend with a 13th 'Next' point forecast via Excel's own TREND() over
    the 12 actual-series months - a simple linear projection, not a fabricated number."""
    MS=e.MSER
    ch=e.wb.add_chart({"type":"line"})
    ch.add_series({"name":"Target","categories":MS[tag+"_lbl"],"values":MS[tag+"_tgt"],
        "line":{"color":GREY_M,"width":1.75,"dash_type":"dash"},"marker":{"type":"square","size":4,"fill":{"color":GREY_M}}})
    ch.add_series({"name":"Actual","categories":MS[tag+"_lbl"],"values":MS[tag+"_act"],
        "line":{"color":BLUE_M,"width":2.25},"marker":{"type":"circle","size":5,"fill":{"color":BLUE_M}}})
    e._style(ch,"%s: Target vs Actual + Next-Month Forecast"%label)
    return ch

def _hotspot_table(e, ws, row, spec, col0):
    """Live top-5 department watchlist table (mirrors the Calculations hotspot block)."""
    F=e.FD; tag=spec["key"]+"_hotspot"
    lbl=e.RR.get(tag+"_lbl"); val=e.RR.get(tag+"_val")
    if not lbl: return
    ws.write(row,col0,"Department",F["th"]); ws.write(row,col0+1,"Severity Count",F["th"])
    for i in range(5):
        ws.write_formula(row+1+i,col0,"=INDEX(%s,%d)"%(lbl,i+1),F["tdl"],0)
        ws.write_formula(row+1+i,col0+1,"=INDEX(%s,%d)"%(val,i+1),F["tdn"],0)
    ws.conditional_format(row+1,col0+1,row+5,col0+1,{"type":"data_bar","bar_color":RED})

def _cost_tile(e, ws, row, spec):
    """Cost-impact rollup - only for the two trackers with a genuine, Settings-configured rate
    (no fabricated numbers): Stop Work downtime and Incident lost days."""
    F=e.FD; key=spec["key"]
    dsuf=(",%s,dCrit"%rng(spec,"Department")) if has(spec,"Department") else ""
    if key=="swa":
        label="ESTIMATED DOWNTIME COST (this Register Month)"
        formula='=SUMIFS(%s,%s,mCrit%s)*CostPerDowntimeMin'%(rng(spec,"Downtime (min)"),rng(spec,"Month"),dsuf)
    else:
        label="ESTIMATED LOST-DAY COST (this Register Month)"
        formula='=SUMIFS(%s,%s,mCrit%s)*CostPerLostDay'%(rng(spec,"Lost Days"),rng(spec,"Month"),dsuf)
    fmt=e._fmt(font_name="Segoe UI",font_size=17,bold=True,font_color=NAVY_BG,bg_color=GOLD,
        align="left",valign="vcenter",border=1,border_color=GOLD,num_format='"₹"#,##0',indent=1)
    lblf=e._fmt(font_name="Segoe UI",font_size=9,bold=True,font_color=TXT_MUTED,bg_color=NAVY_BG,align="left",valign="vcenter",indent=1)
    ws.merge_range(row,1,row,10,label,lblf)
    ws.merge_range(row+1,1,row+2,10,formula,fmt)
    return row+4

def _dual_line(e, cats, s1name, s1val, s1color, s2name, s2val, s2color, title):
    ch=e.wb.add_chart({"type":"line"})
    ch.add_series({"name":s1name,"categories":cats,"values":s1val,"line":{"color":s1color,"width":2.25},
        "marker":{"type":"circle","size":5,"fill":{"color":s1color}}})
    ch.add_series({"name":s2name,"categories":cats,"values":s2val,"line":{"color":s2color,"width":2.25,"dash_type":"dash"},
        "marker":{"type":"diamond","size":5,"fill":{"color":s2color}}})
    e._style(ch,title)
    return ch

def _signature_charts(e, spec, RR):
    """The one or two tracker-specific 'signature' analysis charts that replace the generic
    category/status block — chosen for what's actually measurable & meaningful per tracker."""
    key=spec["key"]; MS=e.MSER; months=_months(e)
    R=e.RR
    if key=="toolbox":
        out=["TOOLBOX_HEAT"]
        if "cat2_val" in RR:
            out.append(e.dough(RR["cat2_lbl"],RR["cat2_val"],"Effectiveness Rating",
                [GREEN,BLUE_M,AMBER,RED,GREY_M]))
        return out
    if key=="jsa":
        c1=e.col_chart(months,[("Critical",MS["jsa_critical"],RED),("High",MS["jsa_high"],AMBER),
            ("Medium",MS["jsa_medium"],BLUE_M),("Low",MS["jsa_low"],GREEN)],"Risk Level Mix Trend",stacked=True)
        c2=e.bar_chart(RR["st_lbl"],RR["st_val"],"Approval Status",BLUE_M) if "st_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key=="training":
        area=e.wb.add_chart({"type":"line","subtype":"stacked"})
        area.add_series({"name":"Cumulative Hours","categories":months,"values":MS["training_hours"],
            "line":{"color":BLUE_M,"width":2.25},"fill":{"color":BLUE_L}})
        e._style(area,"Monthly Training Hours"); area.set_legend({"none":True})
        c2=e.bar_chart(R["_train_type_lbl"],R["_train_type_val"],"Pass Rate % by Training Type",GREEN)
        return [area,c2]
    if key=="hseobs":
        c1=_dual_line(e,months,"Safe",MS["hseobs_safe"],GREEN,"At-Risk",MS["hseobs_atrisk"],RED,
            "Safe vs At-Risk Observations (BBS)")
        c2=e.dough(RR["cat2_lbl"],RR["cat2_val"],"Category Mix",[BLUE_M,GREEN,AMBER,RED,GREY_M,"#8B5CF6"]) if "cat2_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key=="wpinsp":
        c1=e.bar_chart(R["_wpinsp_area_lbl"],R["_wpinsp_area_val"],"Non-Conformances by Area",RED)
        c2=e.col_chart(months,[("NCs",MS["wpinsp_nc"],AMBER)],"Non-Conformance Trend")
        return [c1,c2]
    if key=="eqinsp":
        return [e.col_chart(months,[("Critical Findings",MS["eqinsp_critical"],RED)],"Critical Findings Trend")]
    if key=="walk":
        return [e.line_chart(months,MS["walk_total"],"Walkthrough Frequency Trend",BLUE_M)]
    if key=="meetings":
        return [_dual_line(e,months,"Raised",MS["meetings_raised"],AMBER,"Closed",MS["meetings_closed"],GREEN,
            "Action Items: Raised vs Closed")]
    if key=="bulletins":
        c1=e.bar_chart(R["_bulletin_method_lbl"],R["_bulletin_method_val"],"Reach % by Distribution Method",BLUE_M)
        c2=e.dough(RR["cat_lbl"],RR["cat_val"],"Bulletin Type Mix",[BLUE_M,GREEN,AMBER,RED,GREY_M,"#8B5CF6"]) if "cat_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key=="drills":
        c1=_dual_line(e,months,"Actual (min)",MS["drill_resp_actual"],RED,"Target (min)",MS["drill_resp_target"],BLUE_M,
            "Emergency Response Time: Actual vs Target")
        c2=e.bar_chart(RR["cat_lbl"],RR["cat_val"],"Drill Type Coverage",GREEN) if "cat_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key in ("iaudit","eaudit"):
        own_series = MS["iaudit_major"] if key=="iaudit" else MS["eaudit_major"]
        c1=e.col_chart(months,[("Major NC",own_series,RED)],"Major NC Trend")
        c2=_dual_line(e,months,"Internal",MS["iaudit_major"],BLUE_M,"External",MS["eaudit_major"],ACCENT,
            "Internal vs External Major NC Rate")
        return [c1,c2]
    if key=="mgmtvisit":
        return [e.bar_chart(RR["dept_lbl"],RR["dept_val"],"Visits by Department (leadership equity)",BLUE_M)]
    if key=="mgmtreview":
        return [_dual_line(e,months,"Decisions Made",MS["mgmtreview_decisions"],BLUE_M,
            "Actions Assigned",MS["mgmtreview_actions"],AMBER,"Decisions vs Actions Assigned")]
    if key=="disc":
        c1=e.bar_chart(RR["cat_lbl"],RR["cat_val"],"Violation Type (Pareto)",RED)
        c2=e.dough(RR["cat2_lbl"],RR["cat2_val"],"Offense Level Mix",[GREEN,AMBER,RED]) if "cat2_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key=="awards":
        c1=e.bar_chart(RR["dept_lbl"],RR["dept_val"],"Recognition by Department",GREEN)
        c2=e.dough(RR["cat_lbl"],RR["cat_val"],"Award Category Mix",[BLUE_M,GREEN,AMBER,RED,GREY_M,"#8B5CF6"]) if "cat_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key=="swa":
        c1=e.col_chart(months,[("Downtime (min)",MS["swa_downtime"],RED)],"Stop-Work Downtime Trend")
        c2=e.bar_chart(R["_swa_severity_lbl"],R["_swa_severity_val"],"Avg Downtime by Severity",AMBER)
        return [c1,c2]
    if key=="alcohol":
        return [e.line_chart(months,MS["alcohol_rate_m"],"Positive Test Rate Trend",RED)]
    if key=="ptwaudit":
        return [e.bar_chart(R["_ptw_type_lbl"],R["_ptw_type_val"],"Compliance % by Permit Type",BLUE_M)]
    if key=="ca":
        c1=e.col_chart(months,[("On-Time",MS["ca_ontime"],GREEN),("Delayed",MS["ca_delayed"],RED)],
            "On-Time vs Delayed Trend",stacked=True)
        c2=e.bar_chart(RR["cat_lbl"],RR["cat_val"],"CAPA Source (Pareto)",BLUE_M) if "cat_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key=="nc":
        c1=e.bar_chart(R["_ncroot_lbl"],R["_ncroot_val"],"Root Cause (Pareto)",RED)
        c2=e.dough(RR["cat_lbl"],RR["cat_val"],"Severity Mix",[RED,AMBER,BLUE_M,GREEN]) if "cat_val" in RR else None
        return [c for c in (c1,c2) if c]
    if key in ("unsafeact","unsafecond"):
        other="unsafecond" if key=="unsafeact" else "unsafeact"
        c1=_dual_line(e,months,"Unsafe Acts",e.RR["unsafeact"]["month_val"],AMBER,
            "Unsafe Conditions",e.RR["unsafecond"]["month_val"],BLUE_M,"Unsafe Act vs Condition Trend")
        toptag = "_topact" if key=="unsafeact" else "_topcond"
        c2=e.bar_chart(R[toptag+"_lbl"],R[toptag+"_val"],"Top 10 Types",AMBER if key=="unsafeact" else BLUE_M)
        return [c1,c2]
    if key=="incident":
        c1=e.bar_chart(R["_incident_aging_lbl"],R["_incident_aging_val"],"Open Incident Ageing",AMBER)
        c2=e.dough(R["_incident_persontype_lbl"],R["_incident_persontype_val"],"Person Type Mix",
            [BLUE_M,GREEN,AMBER,RED])
        return [c1,c2]
    if key=="environment":
        c1=e.dough(RR["cat_lbl"],RR["cat_val"],"Waste Type Mix",[TEAL,CORAL,GOLD,ORANGE,PURPLE,BLUE_M])
        c2=e.bar_chart(RR["dept_lbl"],RR["dept_val"],"Records by Department",TEAL) if "dept_val" in RR else None
        return [c for c in (c1,c2) if c]
    # fallback for anything not itemised above (shouldn't hit, all 25 covered)
    out=[]
    if "cat_val" in RR: out.append(e.bar_chart(RR["cat_lbl"],RR["cat_val"],"Breakdown by %s"%spec.get("cat"),GREEN))
    if "st_val" in RR: out.append(e.dough(RR["st_lbl"],RR["st_val"],"Status Distribution",[AMBER,BLUE_M,GREEN,RED]))
    return out

def _mirror_heat(e, ws, row, meta, colors):
    """Mirror a heat-map block from Calculations onto the dashboard, live, with matching
    3-colour-scale conditional formatting (so it's actually visible, not just a pointer note)."""
    F=e.FD; top=meta["top"]; col0=meta["col0"]; nrows=meta["nrows"]; ncols=meta["ncols"]
    for j in range(ncols+1):
        ws.write_formula(row,1+j,"=Calculations!%s"%xl_rowcol_to_cell(top-1,col0+j,True,True),F["th"])
    for i in range(nrows):
        for j in range(ncols+1):
            fmt = F["tdl"] if j==0 else F["heat"]
            ws.write_formula(row+1+i,1+j,"=Calculations!%s"%xl_rowcol_to_cell(top+i,col0+j,True,True),fmt,0)
    ws.conditional_format(row+1,2,row+nrows,1+ncols,{"type":"3_color_scale",
        "min_color":NAVY_CARD,"mid_color":"#1D7A6E","max_color":TEAL})
    return row+nrows+3

def _dept_table(e, ws, row, RR):
    """Live Department Performance table (Department | Count | 2 metrics), with a data bar
    on Count for instant visual ranking - mirrors the Calculations sheet via formulas."""
    F=e.FD; top=RR["dept_top"]; dc0=RR["dept_dc0"]; n=RR["dept_n"]
    headers=["Department","Count",RR["dept_met1_name"],RR["dept_met2_name"]]
    for j,h in enumerate(headers):
        ws.write(row,1+j,h,F["th"])
    for i in range(n):
        rr=row+1+i; srcrow=top+1+i
        for j,kind in enumerate([("l",None),("n","num"),("n",RR["dept_met1_kind"]),("n",RR["dept_met2_kind"])]):
            align,knd = kind
            fmt = F["tdl"] if align=="l" else (F["tdp"] if knd=="pct" else F["tdn"])
            ws.write_formula(rr,1+j,"=IFERROR(Calculations!$%s$%d,\"\")"%(xl_col_to_name(dc0+j),srcrow+1),fmt,0)
    ws.conditional_format(row+1,2,row+n,2,{"type":"data_bar","bar_color":BLUE_M})

def _matrix_table(e, ws, row, spec, RR):
    """Live Monthly Performance Matrix, mirrored from Calculations. Percentage rows get a
    green-amber-red colour scale across their own 12 months, so a missed month jumps out."""
    F=e.FD
    top=RR.get("matrix_top")
    if top is None: return
    kinds=RR.get("matrix_kinds",[])
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
        if i < len(kinds) and kinds[i]=="pct":
            ws.conditional_format(rr,2,rr,13,{"type":"3_color_scale",
                "min_color":"#5C2323","mid_color":"#5C4419","max_color":"#1D7A6E"})
