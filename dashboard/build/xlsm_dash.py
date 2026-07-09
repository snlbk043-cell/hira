"""Dashboards, charts, gauges, navigation and documentation sheets."""
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell
import data_gen

BLUE_D="#0F4C81"; BLUE_M="#0B6EA8"; BLUE_L="#E8F3FB"; GREY_D="#334155"
GREY_M="#64748B"; GREY_L="#F1F5F9"; GREEN="#16A34A"; GREEN_L="#DCFCE7"
AMBER="#F59E0B"; RED="#DC2626"; RED_L="#FEE2E2"; WHITE="#FFFFFF"; INK="#1F2937"; ACCENT="#D71920"

ACC = {"blue":BLUE_M, "green":GREEN, "red":RED, "amber":AMBER}

# 20 KPI cards: (title, engine name, fmt, accent, spark key)
KPIS = [
    ("Total Man-hours","Manhours","num","blue","mh_m"),
    ("TRIR","TRIR","dec","red","trir_m"),
    ("LTIFR","LTIFR","dec","red","ltifr_m"),
    ("Lost Time Injury","LTI","num","red","recordable_m"),
    ("Medical Treatment","MTC","num","amber","recordable_m"),
    ("First Aid Cases","FirstAid","num","amber","firstaid_m"),
    ("Near Misses","NearMiss","num","blue","nearmiss_m"),
    ("HiPo Near Miss","HiPoNM","num","red","nearmiss_m"),
    ("Safety Observations","SafetyObs","num","green","so_m"),
    ("Unsafe Acts","UnsafeActs","num","amber","ua_m"),
    ("Unsafe Conditions","UnsafeConds","num","amber","uc_m"),
    ("Good Catch","GoodCatch","num","green","so_m"),
    ("PTW Compliance","PTWComp","pct","green","ptw_m"),
    ("Inspection Compliance","InspComp","pct","green",None),
    ("Audit Compliance","AuditComp","pct","green",None),
    ("Training Compliance","TrainComp","pct","green","train_m"),
    ("PPE Compliance","PPEComp","pct","green",None),
    ("Statutory Compliance","StatComp","pct","blue",None),
    ("Action Closure","ActionClosure","pct","green",None),
    ("Safety Score","SafetyScore","num","blue",None),
]


def _fmt_cache(b):
    if not hasattr(b, "_dc"):
        b._dc = {}
    return b._dc

def cardfmt(b, accent, kind):
    """Return (strip, title, value, sub) formats for a card accent + value kind."""
    key = (accent, kind)
    c = _fmt_cache(b)
    if key in c:
        return c[key]
    wb = b.wb
    strip = wb.add_format({"bg_color":ACC[accent]})
    title = wb.add_format({"font_name":"Segoe UI","font_size":9,"bold":True,
        "font_color":GREY_M,"bg_color":WHITE,"align":"left","valign":"vcenter",
        "left":1,"right":1,"border_color":"#E2E8F0"})
    nf = {"num":"#,##0","dec":"0.00","pct":'0.0"%"'}[kind]
    value = wb.add_format({"font_name":"Segoe UI","font_size":21,"bold":True,
        "font_color":BLUE_D,"bg_color":WHITE,"align":"left","valign":"vcenter",
        "num_format":nf,"left":1,"right":1,"border_color":"#E2E8F0"})
    sub = wb.add_format({"font_name":"Segoe UI","font_size":8,"font_color":GREY_M,
        "bg_color":WHITE,"align":"left","valign":"vcenter","left":1,"right":1,
        "bottom":1,"border_color":"#E2E8F0"})
    c[key]=(strip,title,value,sub)
    return c[key]


def place_card(b, ws, r, c, title, engine, kind, accent, spark=None):
    """5-row x 3-col KPI card."""
    strip,tfmt,vfmt,sfmt = cardfmt(b, accent, kind)
    ws.merge_range(r, c, r, c+2, "", strip)
    ws.set_row(r, 4)
    ws.merge_range(r+1, c, r+1, c+2, title.upper(), tfmt)
    ws.merge_range(r+2, c, r+3, c+2, "=%s" % engine, vfmt)
    # sub row: status text + sparkline
    ws.merge_range(r+4, c, r+4, c+1, "vs prior period", sfmt)
    ws.write_blank(r+4, c+2, "", sfmt)
    if spark and spark in b.R:
        ws.add_sparkline(r+4, c+2, {"range": b.R[spark], "type":"line",
            "series_color":ACC[accent], "high_point":True, "low_point":True})


def chart_frame(b, ws, r, c, title):
    """section title above a chart."""
    ws.merge_range(r, c, r, c+7, title, b.F["section"])


def add_line(b, cats, series, title, y2=None):
    ch = b.wb.add_chart({"type":"line"})
    for nm, val, color in series:
        ch.add_series({"name":nm,"categories":cats,"values":val,
            "line":{"color":color,"width":2.25},"marker":{"type":"circle","size":5,
            "fill":{"color":color},"border":{"none":True}},"smooth":False})
    _style(ch, title)
    return ch

def add_col(b, cats, series, title, stacked=False):
    ch = b.wb.add_chart({"type":"column","subtype":"stacked" if stacked else None})
    for nm,val,color in series:
        ch.add_series({"name":nm,"categories":cats,"values":val,"fill":{"color":color},
            "border":{"none":True},"gap":60})
    _style(ch, title)
    return ch

def add_bar(b, cats, vals, title, color=BLUE_M):
    ch=b.wb.add_chart({"type":"bar"})
    ch.add_series({"categories":cats,"values":vals,"fill":{"color":color},
        "border":{"none":True},"data_labels":{"value":True,"font":{"size":8}}})
    _style(ch, title); ch.set_legend({"none":True})
    return ch

def add_area(b, cats, vals, title, color=BLUE_M):
    ch=b.wb.add_chart({"type":"area"})
    ch.add_series({"categories":cats,"values":vals,
        "fill":{"color":color,"transparency":40},"border":{"color":color}})
    _style(ch, title); ch.set_legend({"none":True})
    return ch

def add_doughnut(b, lbl, val, title, colors=None):
    ch=b.wb.add_chart({"type":"doughnut"})
    s={"categories":lbl,"values":val,"data_labels":{"percentage":True,"font":{"size":8,"color":WHITE,"bold":True}}}
    if colors:
        s["points"]=[{"fill":{"color":x}} for x in colors]
    ch.add_series(s)
    ch.set_hole_size(55); _style(ch, title)
    ch.set_legend({"position":"right","font":{"size":8}})
    return ch

def add_radar(b, lbl, val, title):
    ch=b.wb.add_chart({"type":"radar","subtype":"with_markers"})
    ch.add_series({"categories":lbl,"values":val,"line":{"color":BLUE_M,"width":2},
        "fill":{"color":BLUE_L,"transparency":30},"marker":{"type":"circle","size":5,"fill":{"color":BLUE_D}}})
    _style(ch, title); ch.set_legend({"none":True})
    return ch

def add_pareto(b, lbl, val, cum, title):
    ch=b.wb.add_chart({"type":"column"})
    ch.add_series({"name":"Count","categories":lbl,"values":val,"fill":{"color":BLUE_M},
        "border":{"none":True},"gap":40})
    line=b.wb.add_chart({"type":"line"})
    line.add_series({"name":"Cumulative %","categories":lbl,"values":cum,"y2_axis":True,
        "line":{"color":ACCENT,"width":2.25},"marker":{"type":"circle","size":5,"fill":{"color":ACCENT}}})
    ch.combine(line)
    ch.set_y2_axis({"min":0,"max":100,"num_format":'0"%"'})
    _style(ch, title)
    return ch

def add_gauge(b, gauge_range, title, color=GREEN):
    ch=b.wb.add_chart({"type":"doughnut"})
    ch.add_series({"values":gauge_range,
        "points":[{"fill":{"color":color}},{"fill":{"color":GREY_L}},{"fill":{"none":True}}]})
    ch.set_rotation(270); ch.set_hole_size(62)
    ch.set_legend({"none":True})
    ch.set_title({"name":title,"name_font":{"size":10,"bold":True,"color":BLUE_D}})
    ch.set_chartarea({"border":{"none":True},"fill":{"none":True}})
    return ch

def _style(ch, title):
    ch.set_title({"name":title,"name_font":{"name":"Segoe UI","size":11,"bold":True,"color":BLUE_D}})
    ch.set_chartarea({"border":{"color":"#E2E8F0"},"fill":{"color":WHITE}})
    ch.set_plotarea({"fill":{"color":WHITE}})
    ch.set_legend({"position":"bottom","font":{"size":8}})
    ch.set_x_axis({"num_font":{"size":8},"line":{"color":"#CBD5E1"}})
    ch.set_y_axis({"num_font":{"size":8},"major_gridlines":{"visible":True,"line":{"color":"#EEF2F7"}}})


# --------------------------------------------------------------------------
NAV = [("Executive","Executive Dashboard","NavExecutive"),
       ("Incident","Incident Dashboard","NavIncident"),
       ("Inspection","Inspection Dashboard","NavInspection"),
       ("Audit","Audit Dashboard","NavAudit"),
       ("Training","Training Dashboard","NavTraining"),
       ("PTW","PTW Dashboard","NavPTW"),
       ("Statutory","Statutory Dashboard","NavStatutory"),
       ("CAPA","CAPA Dashboard","NavCAPA"),
       ("Department","Department Dashboard","NavDepartment")]


def header(b, ws, subtitle, home=True):
    """Standard dashboard header band + action buttons. Returns first free row."""
    F=b.F
    ws.hide_gridlines(2)
    ws.set_row(0, 8)
    ws.merge_range(1, 1, 3, 12, "EXECUTIVE EHS KPI DASHBOARD", F["title"])
    ws.merge_range(4, 1, 4, 12, "Reliance Consumer Products Ltd  •  Campa CSD Plant  •  " + subtitle, F["subtitle"])
    # accent underline
    ws.merge_range(5, 1, 5, 18, "", F["accentband"]); ws.set_row(5, 3)
    # logo box
    logo=b.wb.add_format({"font_name":"Segoe UI","font_size":15,"bold":True,"font_color":ACCENT,
        "bg_color":WHITE,"align":"center","valign":"vcenter","border":2,"border_color":WHITE})
    ws.merge_range(1,13,4,18,"RCPL  campa", logo)
    # last refresh
    ws.write(6, 14, "Last Refresh:", F["refresh_lbl"])
    ws.write_formula(6, 16, "=LastRefresh", F["refresh_val"], 0)
    # action buttons (macros)
    btns=[("⟳ REFRESH","RefreshDashboard"),("⟲ RESET FILTERS","ResetFilters"),
          ("⌂ HOME","GoHome"),("🖨 PRINT","PrintDashboard"),("PDF","ExportDashboardPDF")]
    x=1
    for cap,mac in btns:
        ws.insert_button(6, x, {"macro":mac,"caption":cap,"width":118,"height":26,
                                "x_offset":2,"y_offset":2})
        x+=2
    return 8


def navstrip(b, ws, row):
    """Row of hyperlink navigation chips."""
    F=b.F
    chip=b.wb.add_format({"font_name":"Segoe UI","font_size":9,"bold":True,"font_color":WHITE,
        "bg_color":BLUE_M,"align":"center","valign":"vcenter","border":1,"border_color":WHITE})
    ws.write_url(row,0,"internal:'Home'!A1",chip,"⌂ Home")
    c=1
    for label,sheet,_ in NAV:
        ws.write_url(row,c,"internal:'%s'!A1"%sheet,chip,label)
        c+=1
    return row+2


def gridcols(ws):
    ws.set_column("A:A", 2.0)
    for col in range(1, 19):
        ws.set_column(col, col, 8.6)


# --------------------------------------------------------------------------
def build_dashboards(b):
    _filter_lists(b)
    build_home(b)
    build_executive(b)
    build_incident(b)
    build_inspection(b)
    build_audit(b)
    build_training(b)
    build_ptw(b)
    build_statutory(b)
    build_capa(b)
    build_department(b)


def _filter_lists(b):
    """Write filter drop-down source lists (with 'All') onto Master Data."""
    ws=b.master_ws; F=b.F
    lists=[("FYear",["All",2024,2025,2026]),
           ("FMonth",["All"]+data_gen.MONTHS),
           ("FDept",["All"]+data_gen.DEPARTMENTS),
           ("FArea",["All"]+data_gen.AREAS),
           ("FShift",["All"]+data_gen.SHIFTS)]
    col=16
    b.filter_ranges={}
    for name,vals in lists:
        ws.write(3,col,name,F["th"])
        for i,v in enumerate(vals):
            ws.write(4+i,col,v,F["td_l"])
        cL=xl_col_to_name(col)
        b.filter_ranges[name]="'Master Data'!$%s$5:$%s$%d"%(cL,cL,4+len(vals))
        ws.set_column(col,col,14)
        col+=1


def build_home(b):
    F=b.F; ws=b.wb.add_worksheet("Home"); ws.set_tab_color(BLUE_D)
    ws.hide_gridlines(2); ws.set_zoom(100)
    ws.set_column("A:A",2); ws.set_column("B:M",11)
    ws.set_row(1,10)
    ws.merge_range("B3:M5","RCPL EXECUTIVE EHS KPI DASHBOARD", F["homehdr"])
    ws.merge_range("B6:M7","Reliance Consumer Products Ltd  •  Campa Cola CSD Plant  •  Food & Beverage Manufacturing", F["homesub"])
    ws.merge_range("B8:M8","", F["accentband"]); ws.set_row(7,4)
    # last refresh named cell
    ws.write("I10","Last Refresh:", F["refresh_lbl"])
    import datetime
    ws.write_datetime("K10", datetime.datetime.now(), F["refresh_val"])
    b.wb.define_name("LastRefresh", "='Home'!$K$10")
    ws.merge_range("B10:H10","Select a dashboard below or use the ⟳ Refresh button on any page.", F["note"])
    # nav grid of macro buttons + hyperlinks
    ws.merge_range("B12:M12","DASHBOARD NAVIGATION", F["section"])
    r=13; c=1
    tiles=[("EXECUTIVE","Executive Dashboard","NavExecutive"),
           ("INCIDENT","Incident Dashboard","NavIncident"),
           ("INSPECTION","Inspection Dashboard","NavInspection"),
           ("AUDIT","Audit Dashboard","NavAudit"),
           ("TRAINING","Training Dashboard","NavTraining"),
           ("PTW","PTW Dashboard","NavPTW"),
           ("STATUTORY","Statutory Dashboard","NavStatutory"),
           ("CAPA","CAPA Dashboard","NavCAPA"),
           ("DEPARTMENT","Department Dashboard","NavDepartment")]
    tile=b.wb.add_format({"font_name":"Segoe UI","font_size":13,"bold":True,"font_color":WHITE,
        "bg_color":BLUE_M,"align":"center","valign":"vcenter","border":2,"border_color":WHITE})
    for i,(cap,sheet,mac) in enumerate(tiles):
        rr=13+(i//3)*3; cc=1+(i%3)*4
        ws.merge_range(rr,cc,rr+1,cc+3,"", tile)
        ws.write_url(rr,cc,"internal:'%s'!A1"%sheet, tile, cap)
        ws.insert_button(rr, cc+3, {"macro":mac,"caption":"Open ▸","width":70,"height":24,"x_offset":6,"y_offset":6})
    # quick links to registers & docs
    ws.merge_range("B23:M23","DATA & DOCUMENTATION", F["section"])
    links=[("Calculations","Calculations"),("Master Data","Master Data"),
           ("Documentation","Documentation"),("Instructions","Instructions"),
           ("Formula Sheet","Formula Sheet"),("Incident Register","Incident Register"),
           ("CAPA Tracker","CAPA Tracker"),("Audit Register","Audit Register")]
    lf=b.wb.add_format({"font_name":"Segoe UI","font_size":10,"bold":True,"font_color":BLUE_D,
        "bg_color":BLUE_L,"align":"center","valign":"vcenter","border":1,"border_color":WHITE,"underline":True})
    for i,(cap,sheet) in enumerate(links):
        rr=24+(i//4); cc=1+(i%4)*3
        ws.merge_range(rr,cc,rr,cc+2,"",lf)
        ws.write_url(rr,cc,"internal:'%s'!A1"%sheet, lf, cap)
    ws.merge_range("B28:M30",
        "This workbook is fully dynamic: every KPI recalculates automatically from the 20 raw-data "
        "registers. Change the filters on the Executive Dashboard (Year / Month / Department / Area / "
        "Shift) and all cards, charts and gauges update instantly. Add new rows to any register and "
        "click ⟳ Refresh — no manual updates required.", F["note"])


def build_executive(b):
    F=b.F; R=b.R
    ws=b.wb.add_worksheet("Executive Dashboard"); ws.set_tab_color(BLUE_D)
    gridcols(ws); ws.set_zoom(80)
    row=header(b, ws, "Executive Overview")
    row=navstrip(b, ws, row)

    # ----- filter panel -----
    ws.merge_range(row,1,row,18,"GLOBAL FILTERS  (drive every KPI, chart & gauge)", F["section"]); row+=1
    filters=[("Year","SelYear","FYear"),("Month","SelMonth","FMonth"),
             ("Department","SelDept","FDept"),("Area","SelArea","FArea"),
             ("Shift","SelShift","FShift")]
    c=1
    for lbl,name,src in filters:
        ws.write(row,c,lbl,F["filter_lbl"])
        ws.merge_range(row,c+1,row,c+2,"All",F["filter_val"])
        b.wb.define_name(name, "='Executive Dashboard'!$%s$%d"%(xl_col_to_name(c+1),row+1))
        ws.data_validation(row,c+1,row,c+1,{"validate":"list","source":b.filter_ranges[src]})
        c+=3
    row+=2

    # ----- KPI cards (20, 5 per row) -----
    ws.merge_range(row,1,row,18,"KEY PERFORMANCE INDICATORS", F["section"]); row+=1
    start=row
    for i,(title,eng,kind,acc,spark) in enumerate(KPIS):
        rr=start+(i//5)*6; cc=1+(i%5)*3
        place_card(b, ws, rr, cc, title, eng, kind, acc, spark)
    row=start+ (len(KPIS)//5)*6 + 1

    # traffic-light conditional formatting on compliance safety score already via colors
    # ----- charts -----
    ws.merge_range(row,1,row,18,"TRENDS & ANALYTICS", F["section"]); row+=1
    def place(ch, r, c, w=486, h=270):
        ch.set_size({"width":w,"height":h})
        ws.insert_chart(r, c, ch)
    ch1=add_line(b, R["months"], [("Total Incidents",R["tot_m"],BLUE_D)], "Monthly Incident Trend")
    ch2=add_line(b, R["months"], [("TRIR",R["trir_m"],BLUE_D)], "TRIR & LTIFR Trend")
    ch2b=b.wb.add_chart({"type":"line"})
    ch2b.add_series({"name":"LTIFR","categories":R["months"],"values":R["ltifr_m"],"y2_axis":True,
        "line":{"color":ACCENT,"width":2.25},"marker":{"type":"circle","size":5,"fill":{"color":ACCENT}}})
    ch2.combine(ch2b); ch2.set_y2_axis({"num_font":{"size":8}})
    ch3=add_doughnut(b, R["clsf_lbl"], R["clsf_val"], "Incident Classification")
    place(ch1,row,1); place(ch2,row,7); place(ch3,row,13); row+=15

    ch4=add_col(b, R["months"], [("Unsafe Act",R["ua_m"],AMBER),("Unsafe Condition",R["uc_m"],BLUE_M)],
                "Unsafe Act vs Unsafe Condition", stacked=True)
    ch5=add_col(b, R["months"], [("Near Miss",R["nearmiss_m"],GREEN)], "Near Miss Trend")
    ch6=add_area(b, R["months"], R["so_m"], "Safety Observation Trend", BLUE_M)
    place(ch4,row,1); place(ch5,row,7); place(ch6,row,13); row+=15

    ch7=add_bar(b, R["dept_lbl"], R["dept_val"], "Department-wise Safety Score", BLUE_M)
    ch8=add_radar(b, R["radar_lbl"], R["radar_val"], "Monthly Performance Profile")
    ch9=add_pareto(b, R["pareto_lbl"], R["pareto_val"], R["pareto_cum"], "Root Cause Analysis (Pareto)")
    place(ch7,row,1,486,300); place(ch8,row,7,486,300); place(ch9,row,13,486,300); row+=17

    # gauges
    ws.merge_range(row,1,row,18,"COMPLIANCE GAUGES", F["section"]); row+=1
    gm=b.gmap
    gauges=[("Training",gm["TrainComp"],GREEN,"TrainComp"),("PTW",gm["PTWComp"],BLUE_M,"PTWComp"),
            ("Statutory",gm["StatComp"],AMBER,"StatComp"),("Action Closure",gm["ActionClosure"],GREEN,"ActionClosure")]
    gc=1
    bigpct=b.wb.add_format({"font_name":"Segoe UI","font_size":16,"bold":True,"font_color":BLUE_D,
        "align":"center","valign":"vcenter","num_format":'0.0"%"'})
    for title,grange,color,eng in gauges:
        g=add_gauge(b, grange, title+" Compliance", color); g.set_size({"width":300,"height":220})
        ws.insert_chart(row, gc, g)
        ws.merge_range(row+9, gc+1, row+9, gc+2, "=%s"%eng, bigpct)
        gc+=4
    ws.set_column("A:A",2)


# ---- secondary dashboards ------------------------------------------------
def _mini(b, ws, row, cards):
    """place a row of KPI cards; cards=[(title,eng,kind,acc,spark)]"""
    for i,(t,e,k,a,s) in enumerate(cards):
        place_card(b, ws, row, 1+(i%5)*3, t, e, k, a, s)
    return row+6

def _sec_header(b, ws, subtitle):
    gridcols(ws); ws.set_zoom(85)
    row=header(b, ws, subtitle)
    row=navstrip(b, ws, row)
    return row

def build_incident(b):
    F=b.F; R=b.R
    ws=b.wb.add_worksheet("Incident Dashboard"); ws.set_tab_color(RED)
    row=_sec_header(b, ws, "Incident & Injury Analysis")
    ws.merge_range(row,1,row,18,"INCIDENT KPIs (respond to Executive filters)", F["section"]); row+=1
    row=_mini(b, ws, row, [("TRIR","TRIR","dec","red","trir_m"),("LTIFR","LTIFR","dec","red","ltifr_m"),
        ("Lost Time Injury","LTI","num","red","recordable_m"),("Medical Treatment","MTC","num","amber",None),
        ("Recordable","Recordable","num","red",None)])
    row=_mini(b, ws, row, [("First Aid","FirstAid","num","amber","firstaid_m"),("Near Miss","NearMiss","num","blue","nearmiss_m"),
        ("HiPo Near Miss","HiPoNM","num","red",None),("Severity Rate","SeverityRate","dec","amber",None),
        ("Lost Days","LostDays","num","red",None)])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    def place(ch,r,c,w=486,h=290): ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)
    c1=add_line(b,R["months"],[("Total Incidents",R["tot_m"],BLUE_D)],"Monthly Incident Trend")
    c2=add_col(b,R["months"],[("First Aid",R["firstaid_m"],AMBER)],"First Aid Trend")
    c3=add_doughnut(b,R["clsf_lbl"],R["clsf_val"],"Incident Classification")
    place(c1,row,1);place(c2,row,7);place(c3,row,13);row+=16
    c4=add_pareto(b,R["pareto_lbl"],R["pareto_val"],R["pareto_cum"],"Root Cause Analysis (Pareto)")
    c5=add_bar(b,R["toparea_lbl"],R["toparea_val"],"Top 10 High-Risk Areas",RED)
    place(c4,row,1);place(c5,row,7);row+=1
    # risk heat map (native grid on this dashboard via link note)
    ws.merge_range(row+15,13,row+15,18,"Risk Heat Map → see Calculations sheet (5×5 auto-coloured matrix)", F["note"])

def build_inspection(b):
    F=b.F;R=b.R
    ws=b.wb.add_worksheet("Inspection Dashboard"); ws.set_tab_color(BLUE_M)
    row=_sec_header(b, ws, "Workplace Inspection Performance")
    ws.merge_range(row,1,row,18,"INSPECTION KPIs", F["section"]); row+=1
    row=_mini(b, ws, row, [("Inspection Compliance","InspComp","pct","green",None),
        ("PPE Compliance","PPEComp","pct","green",None),("Fire Equipment OK %","InspComp","pct","green",None),
        ("Safety Score","SafetyScore","num","blue",None),("Safety Obs","SafetyObs","num","green","so_m")])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    def place(ch,r,c,w=560,h=300): ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)
    c1=add_col(b,R["insp_lbl"],[("Completed",R["insp_done"],GREEN),("Pending",R["insp_pend"],AMBER)],
               "Inspection Status by Type", stacked=True)
    c2=add_gauge(b,b.gmap["InspComp"],"Inspection Compliance",GREEN); c2.set_size({"width":320,"height":260})
    place(c1,row,1); ws.insert_chart(row,11,c2)

def build_audit(b):
    F=b.F;R=b.R
    ws=b.wb.add_worksheet("Audit Dashboard"); ws.set_tab_color(BLUE_M)
    row=_sec_header(b, ws, "EHS Audit & NCR Management")
    ws.merge_range(row,1,row,18,"AUDIT KPIs", F["section"]); row+=1
    row=_mini(b, ws, row, [("Audit Compliance","AuditComp","pct","green",None),
        ("Action Closure","ActionClosure","pct","green",None),("Safety Score","SafetyScore","num","blue",None),
        ("Statutory Compliance","StatComp","pct","amber",None),("PTW Compliance","PTWComp","pct","green","ptw_m")])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    def place(ch,r,c,w=560,h=300): ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)
    c1=add_col(b,R["aud_lbl"],[("Closed",R["aud_closed"],GREEN),("Open",R["aud_open"],RED)],
               "Audit NCR Status by Type", stacked=True)
    c2=add_gauge(b,b.gmap["AuditComp"],"Audit Compliance",BLUE_M); c2.set_size({"width":320,"height":260})
    place(c1,row,1); ws.insert_chart(row,11,c2)

def build_training(b):
    F=b.F;R=b.R
    ws=b.wb.add_worksheet("Training Dashboard"); ws.set_tab_color(GREEN)
    row=_sec_header(b, ws, "Training & Competency")
    ws.merge_range(row,1,row,18,"TRAINING KPIs", F["section"]); row+=1
    row=_mini(b, ws, row, [("Training Compliance","TrainComp","pct","green","train_m"),
        ("Safety Score","SafetyScore","num","blue",None),("Safety Obs","SafetyObs","num","green","so_m"),
        ("Good Catch","GoodCatch","num","green",None),("Near Miss Rate","NearMissRate","dec","blue",None)])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    def place(ch,r,c,w=560,h=300): ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)
    c1=add_line(b,R["months"],[("Training %",R["train_m"],GREEN)],"Monthly Training Compliance")
    c2=add_gauge(b,b.gmap["TrainComp"],"Training Compliance",GREEN); c2.set_size({"width":320,"height":260})
    place(c1,row,1); ws.insert_chart(row,11,c2)

def build_ptw(b):
    F=b.F;R=b.R
    ws=b.wb.add_worksheet("PTW Dashboard"); ws.set_tab_color(AMBER)
    row=_sec_header(b, ws, "Permit To Work Compliance")
    ws.merge_range(row,1,row,18,"PTW KPIs", F["section"]); row+=1
    row=_mini(b, ws, row, [("PTW Compliance","PTWComp","pct","green","ptw_m"),
        ("Safety Score","SafetyScore","num","blue",None),("Near Miss","NearMiss","num","blue","nearmiss_m"),
        ("Unsafe Acts","UnsafeActs","num","amber","ua_m"),("Action Closure","ActionClosure","pct","green",None)])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    def place(ch,r,c,w=560,h=300): ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)
    c1=add_line(b,R["months"],[("PTW %",R["ptw_m"],AMBER)],"Monthly PTW Compliance")
    c2=add_gauge(b,b.gmap["PTWComp"],"PTW Compliance",AMBER); c2.set_size({"width":320,"height":260})
    place(c1,row,1); ws.insert_chart(row,11,c2)

def build_statutory(b):
    F=b.F;R=b.R
    ws=b.wb.add_worksheet("Statutory Dashboard"); ws.set_tab_color(GREY_D)
    row=_sec_header(b, ws, "Statutory & Legal Compliance")
    ws.merge_range(row,1,row,18,"STATUTORY KPIs", F["section"]); row+=1
    row=_mini(b, ws, row, [("Statutory Compliance","StatComp","pct","green",None),
        ("Action Closure","ActionClosure","pct","green",None),("Audit Compliance","AuditComp","pct","blue",None),
        ("Safety Score","SafetyScore","num","blue",None),("PPE Compliance","PPEComp","pct","green",None)])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    g=add_gauge(b,b.gmap["StatComp"],"Statutory Compliance",GREY_D); g.set_size({"width":340,"height":270})
    ws.insert_chart(row,1,g)
    ws.merge_range(row,7,row,18,"Statutory Compliance Register drives this gauge. Filter by Department on the Executive Dashboard.", F["note"])

def build_capa(b):
    F=b.F;R=b.R
    ws=b.wb.add_worksheet("CAPA Dashboard"); ws.set_tab_color(RED)
    row=_sec_header(b, ws, "Corrective & Preventive Actions")
    ws.merge_range(row,1,row,18,"CAPA KPIs", F["section"]); row+=1
    row=_mini(b, ws, row, [("Action Closure","ActionClosure","pct","green",None),
        ("Obs Closure","ObsClosure","pct","green",None),("Safety Score","SafetyScore","num","blue",None),
        ("Near Miss","NearMiss","num","blue","nearmiss_m"),("HiPo Near Miss","HiPoNM","num","red",None)])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    def place(ch,r,c,w=486,h=290): ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)
    c1=add_doughnut(b,R["capast_lbl"],R["capast_val"],"CAPA by Status",[AMBER,BLUE_M,GREEN,RED])
    c2=add_bar(b,R["capasrc_lbl"],R["capasrc_val"],"CAPA by Source",BLUE_M)
    c3=add_gauge(b,b.gmap["ActionClosure"],"Action Closure",GREEN); c3.set_size({"width":320,"height":260})
    place(c1,row,1);place(c2,row,7);ws.insert_chart(row,13,c3)

def build_department(b):
    F=b.F;R=b.R
    ws=b.wb.add_worksheet("Department Dashboard"); ws.set_tab_color(BLUE_M)
    row=_sec_header(b, ws, "Department-wise Performance")
    ws.merge_range(row,1,row,18,"DEPARTMENT KPIs", F["section"]); row+=1
    row=_mini(b, ws, row, [("Safety Score","SafetyScore","num","blue",None),
        ("Recordable","Recordable","num","red",None),("Near Miss","NearMiss","num","blue","nearmiss_m"),
        ("Safety Obs","SafetyObs","num","green","so_m"),("Unsafe Acts","UnsafeActs","num","amber","ua_m")])
    ws.merge_range(row,1,row,18,"ANALYTICS", F["section"]); row+=1
    def place(ch,r,c,w=560,h=320): ch.set_size({"width":w,"height":h}); ws.insert_chart(r,c,ch)
    c1=add_bar(b,R["dept_lbl"],R["dept_val"],"Department-wise Safety Score",BLUE_M)
    c2=add_bar(b,R["topact_lbl"],R["topact_val"],"Top Unsafe Acts",AMBER)
    place(c1,row,1);place(c2,row,10)


# --------------------------------------------------------------------------
def build_docs(b):
    _doc_documentation(b)
    _doc_instructions(b)
    _doc_formula(b)


def _doc_documentation(b):
    F=b.F; ws=b.wb.add_worksheet("Documentation"); ws.set_tab_color(GREY_M)
    ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",30); ws.set_column("C:H",16)
    ws.write("B2","RCPL Executive EHS KPI Dashboard — Documentation", F["h1"])
    ws.write_url("B3","internal:'Home'!A1", F["h2"], "⌂ Back to Home")
    r=4
    def sec(t):
        nonlocal r; ws.write(r,1,t,F["h2"]); r+=1
    def line(t):
        nonlocal r; ws.merge_range(r,1,r,7,t,F["body"]); ws.set_row(r,30); r+=1
    sec("Purpose")
    line("A world-class, fully interactive Executive Safety KPI dashboard for the Reliance Consumer "
         "Products Ltd (Campa Cola) CSD plant. Every KPI, chart and gauge recalculates automatically "
         "from the 20 raw-data registers — zero manual updates.")
    sec("Workbook Structure")
    for name,desc in [
        ("Home","Landing page with navigation buttons and last-refresh stamp."),
        ("Executive Dashboard","20 KPI cards, 9 charts, 4 gauges and the 5 global filters."),
        ("Incident / Inspection / Audit / Training / PTW / Statutory / CAPA / Department Dashboards",
         "Focused drill-down dashboards, all driven by the same global filters."),
        ("Calculations","The KPI engine — COUNTIFS/SUMIFS over 100,000-row dynamic ranges."),
        ("20 Registers","Structured Excel Tables holding the raw EHS data."),
        ("Master Data","Lookup lists and filter drop-down sources."),
        ("Formula Sheet","Every safety formula with definition and Excel implementation."),
        ("Instructions","Step-by-step user guide."),
    ]:
        ws.write(r,1,name,F["bodyb"]); ws.merge_range(r,2,r,7,desc,F["body"]); ws.set_row(r,30); r+=1
    sec("KPI Definitions")
    for k,d in [
        ("TRIR","Total Recordable Incident Rate = Recordable cases × 200,000 / man-hours."),
        ("LTIFR","Lost Time Injury Frequency Rate = LTI × 1,000,000 / man-hours."),
        ("Severity Rate","Lost days × 1,000,000 / man-hours."),
        ("Safety Score","Weighted index of PTW, Inspection, Audit, Training, PPE, Statutory & Action-closure compliance."),
        ("Compliance %","Compliant records ÷ total records (or completed ÷ planned) × 100."),
    ]:
        ws.write(r,1,k,F["bodyb"]); ws.merge_range(r,2,r,7,d,F["body"]); ws.set_row(r,28); r+=1
    sec("Data Governance")
    line("Registers support up to 100,000 records each. Add new rows at the bottom of any Table and "
         "click ⟳ Refresh. Keep the column structure unchanged so the engine ranges stay valid.")


def _doc_instructions(b):
    F=b.F; ws=b.wb.add_worksheet("Instructions"); ws.set_tab_color(GREEN)
    ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",6); ws.set_column("C:J",16)
    ws.write("B2","How to Use This Dashboard", F["h1"])
    ws.write_url("B3","internal:'Home'!A1", F["h2"], "⌂ Back to Home")
    steps=[
        "Enable macros when prompted (File ▸ Options ▸ Trust Center ▸ Enable all macros) so the buttons work.",
        "Open the Home sheet and click any dashboard tile to navigate.",
        "On the Executive Dashboard use the five drop-downs (Year, Month, Department, Area, Shift) to filter.",
        "Every KPI card, chart and gauge updates instantly when a filter changes.",
        "Click ⟳ REFRESH to force a full recalculation (also refreshes any pivot tables/queries).",
        "Click ⟲ RESET FILTERS to return every filter to 'All'.",
        "Click 🖨 PRINT to print the active dashboard, or PDF to export it.",
        "To add data, open the relevant register, type a new row directly under the Table, then Refresh.",
        "Sparklines on each KPI card show the 12-month trend for the selected year & department.",
        "The Risk Heat Map (Calculations sheet) auto-colours from green (low) to red (high).",
    ]
    r=4
    numf=b.wb.add_format({"font_name":"Segoe UI","font_size":12,"bold":True,"font_color":WHITE,
        "bg_color":BLUE_M,"align":"center","valign":"vcenter"})
    for i,s in enumerate(steps):
        ws.write(r,1,i+1,numf); ws.merge_range(r,2,r,9,s,F["body"]); ws.set_row(r,30); r+=1
    r+=1
    ws.write(r,1,"", F["body"])
    ws.merge_range(r,1,r,9,"Tip: If the macro buttons are disabled by your security policy, every dashboard "
        "is still fully usable — the hyperlink chips at the top navigate between sheets and all KPIs remain live.", F["note"])
    ws.set_row(r,44)


def _doc_formula(b):
    F=b.F; ws=b.wb.add_worksheet("Formula Sheet"); ws.set_tab_color(BLUE_D)
    ws.hide_gridlines(2); ws.set_column("A:A",2); ws.set_column("B:B",22)
    ws.set_column("C:C",44); ws.set_column("D:D",52)
    ws.write("B2","Safety KPI Formula Reference", F["h1"])
    ws.write_url("B3","internal:'Home'!A1", F["h2"], "⌂ Back to Home")
    hdr=["KPI","Standard Formula","Excel Implementation (dynamic)"]
    r=4
    for i,h in enumerate(hdr): ws.write(r,1+i,h,F["th"])
    r+=1
    rows=[
        ("TRIR","Recordable × 200,000 / Man-hours","=Recordable*200000/Manhours"),
        ("LTIFR","LTI × 1,000,000 / Man-hours","=LTI*1000000/Manhours"),
        ("Severity Rate","Lost Days × 1,000,000 / Man-hours","=LostDays*1000000/Manhours"),
        ("Frequency Rate","(LTI+RWC) × 1,000,000 / Man-hours","=(LTI+RWC)*1000000/Manhours"),
        ("Near Miss Rate","Near Miss × 200,000 / Man-hours","=NearMiss*200000/Manhours"),
        ("Man-hours","Σ department man-hours","=SUMIFS(tManhours[Man-hours],…filters)"),
        ("Recordable","LTI + MTC + RWC","=COUNTIFS(type,\"Lost Time Injury\",…)+…"),
        ("PTW Compliance %","Compliant permits ÷ total permits","=COUNTIFS(Compliance,\"Compliant\")/COUNTIFS(all)*100"),
        ("Inspection Compliance %","Completed ÷ planned","=SUMIFS(Completed)/SUMIFS(Planned)*100"),
        ("Audit Compliance %","Average audit score","=AVERAGEIFS(Score,…filters)"),
        ("Training Compliance %","Completed ÷ planned","=SUMIFS(Completed)/SUMIFS(Planned)*100"),
        ("PPE Compliance %","Compliant ÷ checked","=SUMIFS(Compliant)/SUMIFS(Checked)*100"),
        ("Statutory Compliance %","Compliant items ÷ total items","=COUNTIFS(Compliance,\"Compliant\")/COUNTIFS(all)*100"),
        ("Action Closure %","Closed CAPA ÷ total CAPA","=COUNTIFS(Status,\"Closed\")/COUNTIFS(all)*100"),
        ("Observation Closure %","Closed obs ÷ total obs","=COUNTIFS(Status,\"Closed\")/COUNTIFS(all)*100"),
        ("Safety Score","Weighted compliance index (0–100)","=PTW*.18+Insp*.15+Audit*.12+Train*.15+PPE*.15+Stat*.10+Action*.15"),
        ("Safety Performance Index","100 − TRIR×6 − LTIFR×4","=MAX(0,MIN(100,100-TRIR*6-LTIFR*4))"),
    ]
    tdl=b.F["td_l"]; td=b.F["td"]
    for k,std,xl in rows:
        ws.write(r,1,k,b.F["bodyb"]); ws.write_string(r,2,std,tdl); ws.write_string(r,3,xl,tdl)
        ws.set_row(r,26); r+=1
