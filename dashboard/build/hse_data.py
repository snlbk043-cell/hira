"""
Register specifications + sample-data generator for the
RCPL Integrated EHS Management System (structure adopted from HSE_Full_System.xlsx).
"""
import random
from datetime import date, timedelta

random.seed(2026)
YEAR = 2026
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MAX_MONTH = 12   # full-year sample

DEPARTMENTS = ["Operations","Maintenance","Engineering","Construction","Safety",
               "Logistics","Quality","Admin","Projects","Contractor"]
LOCATIONS = ["Plant A","Plant B","Warehouse","Workshop","Field Site","Control Room",
             "Office","Tank Farm","Boiler House","ETP Plant","Admin Block","Loading Bay"]
RISK = ["Critical","High","Medium","Low"]
SEVERITY = ["Critical","High","Medium","Low"]
STATUS = ["Open","In Progress","Closed","Overdue"]
RATING = ["Excellent","Good","Satisfactory","Needs Improvement","Unsatisfactory"]
RESULT = ["Pass","Fail","N/A"]
PEOPLE = ["A. Sharma","R. Verma","S. Iyer","M. Khan","P. Nair","K. Reddy","J. Mehta",
          "T. Bose","V. Rao","N. Gupta","D. Singh","L. Fernandes","H. Patel","G. Das"]
PRIORITY = ["Critical","High","Medium","Low"]

# canonical value pools keyed by header keyword (first match wins)
POOLS = {
    "Training Type":["Induction","Refresher","Advanced","On-the-Job","Awareness","Competency"],
    "Mode":["Internal","External","Online","On-the-Job"],
    "Assessment Result":RESULT, "Result":["Negative","Positive"],
    "Observation Type":["Safe Act","Unsafe Act","Safe Condition","Unsafe Condition"],
    "Category":["BBS","General","PPE","Housekeeping","Ergonomics","Process Safety"],
    "Overall Rating":RATING, "Rating":RATING, "Effectiveness":RATING,
    "Assessment Type":["HIRA","Task RA","HAZOP","What-If","Bow Tie","JSA"],
    "Approval Status":["Approved","Pending Review","Revision Required","Rejected"],
    "Compliance":["Compliant","Non-Compliant","Partially Compliant"],
    "Frequency":["Weekly","Monthly","Quarterly","Annual"],
    "Drill Type":["Fire Evacuation","Chemical Spill","Medical Emergency","Gas Leak",
                  "Confined Space Rescue","Earthquake"],
    "Audit Type":["System Audit","Compliance Audit","Process Audit","Surveillance",
                  "Customer Audit","Regulatory Inspection"],
    "Visit Type":["Site Walk","Plant Visit","Safety Observation","Project Visit"],
    "Violation Type":["PPE Violation","Safety Rule Breach","Permit Violation",
                      "Unauthorized Work","Reckless Behavior","Substance Abuse"],
    "Action Taken":["Verbal Warning","Written Warning","Suspension","Retraining","Fine"],
    "Offense Level":["1st Offense","2nd Offense","3rd Offense"],
    "Award Category":["Safe Worker of Month","Best Safety Suggestion","Zero Incident Award",
                      "HSE Champion","Safety Innovation","Best Department"],
    "Reward Type":["Certificate","Trophy","Cash Bonus","Gift Voucher","Recognition Letter"],
    "Severity":SEVERITY, "Resolution":["Resolved","Under Investigation","Permanent Fix Applied"],
    "Test Type":["Pre-Shift","Random","Post-Incident","Reasonable Suspicion"],
    "Permit Type Audited":["Hot Work","Confined Space","Working at Height","Electrical",
                           "Cold Work","Lifting","Excavation"],
    "Verdict":["Compliant","Non-Compliant","Partially Compliant"],
    "Source":["Audit Finding","Inspection Finding","Incident Follow-up","Observation",
              "Drill Finding","Management Review"],
    "Type":["Safety Alert","Bulletin","Toolbox Topic","Lesson Learned","Best Practice","Advisory"],
    "Distribution Method":["Email","Notice Board","App Notification","All Channels"],
    "Priority":PRIORITY, "Risk Level":RISK, "Risk Rating":RISK,
    "Incident Type":["Injury/Illness","Property Damage","Environmental","Fire","Vehicle"],
    "Classification":["Near Miss","First Aid","Medical Treatment","Restricted Work",
                      "Lost Time Injury","Fatality"],
    "Person Type":["Employee","Contractor","Visitor","Third Party"],
    "Body Part":["Head","Eye","Hand/Finger","Arm","Foot/Leg","Back","Torso","Multiple"],
    "Root Cause":["Human Error","Unsafe Act","Unsafe Condition","Inadequate Procedure",
                  "Lack of Training","Equipment Failure","PPE Not Used","Poor Housekeeping"],
    "Immediate Cause":["Unsafe Act","Unsafe Condition","Equipment Failure","Environmental"],
    "Shift":["Shift A","Shift B","Shift C","General"],
    "Production Line":["Line 1","Line 2","Line 3","Line 4","PET Line","Can Line"],
    "Area":LOCATIONS,
    "Certificate Issued":["Yes","No"], "Action Required":["Yes","No"],
    "MoM Circulated":["Yes","No"], "MoM Distributed":["Yes","No"],
    "Investigation Done":["Yes","No"], "Timeliness":["On-Time","Delayed"],
    "Timeliness ":["On-Time","Delayed"],
}

TOPICS = ["PPE Usage","Fire Safety","Working at Heights","Manual Handling","Electrical Safety",
          "Chemical Safety","Housekeeping","Heat Stress","Slip Trip Fall","Confined Space",
          "LOTO","Emergency Procedures","Hot Work","Machine Guarding"]

UNSAFE_ACT_TYPES = ["Bypassing Safety Device","Not Using PPE","Improper Lifting Technique",
    "Working Without Permit","Operating Without Authorization","Using Defective Equipment",
    "Horseplay","Wrong Tool for the Job","LOTO Not Followed","Vehicle/Forklift Overspeeding"]
UNSAFE_COND_TYPES = ["Slippery Floor","Poor Housekeeping","Inadequate Lighting",
    "Damaged Machine Guard","Exposed Wiring","Blocked Walkway/Aisle","Missing Signage",
    "Chemical Leak","Faulty Ladder/Scaffold","Blocked Fire Exit"]
ROOT_CAUSES = ["Human Error","Unsafe Act","Unsafe Condition","Inadequate Procedure",
               "Lack of Training","Equipment Failure","PPE Not Used","Poor Housekeeping"]

# Per-tracker Status value pools + weights, matched to the client reference dashboard
# (Share_HSE_Full_System2.xlsx) so its exact KPI-card labels are meaningful, not cosmetic.
STATUS_POOLS = {
    "training":  (["Completed","Scheduled","In Progress"], [0.55,0.28,0.17]),
    "hseobs":    (["Completed","In Progress","Pending","Overdue"], [0.45,0.25,0.20,0.10]),
    "wpinsp":    (["Completed","In Progress","Overdue","Pending"], [0.45,0.22,0.13,0.20]),
    "eqinsp":    (["Completed","In Progress","Overdue","Pending"], [0.45,0.22,0.13,0.20]),
    "walk":      (["Completed","In Progress","Overdue","Pending"], [0.48,0.22,0.12,0.18]),
    "bulletins": (["Closed","Acknowledged","Issued"], [0.45,0.35,0.20]),
    "drills":    (["Completed","Action Pending","Rescheduled"], [0.68,0.22,0.10]),
    "iaudit":    (["Completed","In Progress","Scheduled"], [0.55,0.25,0.20]),
    "eaudit":    (["Completed","In Progress","Scheduled"], [0.50,0.25,0.25]),
    "mgmtvisit": (["Completed","Action Pending"], [0.70,0.30]),
    "mgmtreview":(["Completed","In Progress","Scheduled"], [0.65,0.20,0.15]),
    "disc":      (["Completed","Under Review","Appealed"], [0.60,0.28,0.12]),
    "awards":    (["Presented","Scheduled","Nominated"], [0.45,0.25,0.30]),
    "ca":        (["Completed","In Progress","Overdue","Pending","Cancelled"], [0.42,0.20,0.13,0.18,0.07]),
    "nc":        (["Closed","Open","Under Review","Overdue"], [0.42,0.25,0.20,0.13]),
    "unsafeact": (["Completed","Pending","In Progress","Overdue"], [0.50,0.24,0.16,0.10]),
    "unsafecond":(["Completed","Pending","In Progress","Overdue"], [0.50,0.24,0.16,0.10]),
    "incident":  (["Closed","In Progress","Open"], [0.70,0.18,0.12]),
}

# ---- register specs (exact headers from uploaded system) -----------------
REGISTERS = [
 {"key":"toolbox","sheet":"Toolbox Talks","emoji":"🗣️","code":"TBT",
  "headers":["S.No","Ref No.","Date","Month","Topic","Department","Location","Conducted By",
    "Target Attendees","Actual Attendees","Attendance %","Duration (min)","Safety Category",
    "Action Required","Effectiveness"],
  "auto":{"Attendance %":("Actual Attendees","Target Attendees")},
  "cat":"Safety Category","cat2":"Effectiveness","status":None},
 {"key":"jsa","sheet":"JSA Risk Assessment","emoji":"⚠️","code":"JSA",
  "headers":["S.No","JSA No.","Date","Month","Task/Activity","Department","Location","Assessed By",
    "Approved By","Risk Level","Hazards Identified","Assessment Type","Approval Status",
    "Controls Implemented","Compliance"],
  "auto":{},"cat":"Risk Level","cat2":"Assessment Type","status":"Approval Status"},
 {"key":"training","sheet":"Training","emoji":"🎓","code":"TRN",
  "headers":["S.No","Training ID","Date","Month","Course Name","Training Type","Department",
    "Trainer","Mode","Target Attendees","Actual Attendees","Attendance %","Duration (hrs)",
    "Status","Assessment Result","Certificate Issued","Certificate Expiry"],
  "auto":{"Attendance %":("Actual Attendees","Target Attendees")},
  "cat":"Training Type","cat2":"Mode","status":"Status"},
 {"key":"hseobs","sheet":"HSE Observations","emoji":"👁️","code":"OBS",
  "headers":["S.No","Obs No.","Date","Month","Observation Type","Description","Department",
    "Location","Observed By","Responsible Person","Category","Risk Level","Status",
    "Action Taken","Due Date"],
  "auto":{},"cat":"Observation Type","cat2":"Category","status":"Status"},
 {"key":"wpinsp","sheet":"Workplace Inspections","emoji":"🔍","code":"WPI",
  "headers":["S.No","Ref No.","Date","Month","Inspection Area/Item","Department","Location",
    "Inspector","Checkpoints Inspected","Non-Conformances","Critical Findings","Overall Rating",
    "Status","Corrective Action","Due Date"],
  "auto":{},"cat":"Overall Rating","cat2":None,"status":"Status"},
 {"key":"eqinsp","sheet":"Equipment Inspections","emoji":"🛠️","code":"EQI",
  "headers":["S.No","Ref No.","Date","Month","Inspection Area/Item","Department","Location",
    "Inspector","Checkpoints Inspected","Non-Conformances","Critical Findings","Overall Rating",
    "Status","Corrective Action","Due Date"],
  "auto":{},"cat":"Overall Rating","cat2":None,"status":"Status"},
 {"key":"walk","sheet":"Safety Walkthroughs","emoji":"🚶","code":"SW",
  "headers":["S.No","Ref No.","Date","Month","Inspection Area/Item","Department","Location",
    "Inspector","Checkpoints Inspected","Non-Conformances","Critical Findings","Overall Rating",
    "Status","Corrective Action","Due Date"],
  "auto":{},"cat":"Overall Rating","cat2":None,"status":"Status"},
 {"key":"meetings","sheet":"Safety Meetings","emoji":"👥","code":"SM",
  "headers":["S.No","Meeting ID","Date","Month","Frequency","Topic/Agenda","Department",
    "Chaired By","Invited","Attended","Attendance %","Duration (min)","Action Items Raised",
    "Actions Closed","Close-out %","MoM Circulated"],
  "auto":{"Attendance %":("Attended","Invited"),"Close-out %":("Actions Closed","Action Items Raised")},
  "cat":"Frequency","cat2":"MoM Circulated","status":None},
 {"key":"bulletins","sheet":"Safety Bulletins","emoji":"📢","code":"SB",
  "headers":["S.No","Bulletin No.","Date Issued","Month","Type","Subject/Title","Target Audience",
    "Issued By","Distribution Method","Priority","Status","Target Reach","Actual Reach","Reach %"],
  "auto":{"Reach %":("Actual Reach","Target Reach")},"cat":"Type","cat2":"Distribution Method","status":"Status"},
 {"key":"drills","sheet":"Emergency Drills","emoji":"🚨","code":"ED",
  "headers":["S.No","Drill ID","Date","Month","Drill Type","Location","Drill Leader",
    "Target Participants","Actual Participants","Participation %","Target Response (min)",
    "Actual Response (min)","Overall Rating","Improvement Areas","Status"],
  "auto":{"Participation %":("Actual Participants","Target Participants")},
  "cat":"Drill Type","cat2":"Overall Rating","status":"Status"},
 {"key":"iaudit","sheet":"Internal Audits","emoji":"📋","code":"IA",
  "headers":["S.No","Audit No.","Date","Month","Audit Scope","Audit Type","Department","Location",
    "Lead Auditor","Approved By","Checklist Items","Minor NC","Major NC","Observations",
    "Recommendations","Status"],
  "auto":{},"cat":"Audit Type","cat2":None,"status":"Status"},
 {"key":"eaudit","sheet":"External Audits","emoji":"🏛️","code":"EA",
  "headers":["S.No","Audit No.","Date","Month","Audit Scope","Audit Type","Department","Location",
    "Lead Auditor","Approved By","Checklist Items","Minor NC","Major NC","Observations",
    "Recommendations","Status"],
  "auto":{},"cat":"Audit Type","cat2":None,"status":"Status"},
 {"key":"mgmtvisit","sheet":"Management Visits","emoji":"🤝","code":"MV",
  "headers":["S.No","Visit ID","Date","Month","Visit Type","Department","Location","Visited By",
    "Duration (min)","Observations Made","Actions Raised","Actions Closed","Close-out %","Status"],
  "auto":{"Close-out %":("Actions Closed","Actions Raised")},"cat":"Visit Type","cat2":None,"status":"Status"},
 {"key":"mgmtreview","sheet":"Management Reviews","emoji":"🧭","code":"MR",
  "headers":["S.No","Review ID","Date","Month","Review Topic","Chaired By","Members Invited",
    "Members Attended","Attendance %","Duration (min)","Decisions Made","Actions Assigned",
    "Close-out %","MoM Distributed","Status"],
  "auto":{"Attendance %":("Members Attended","Members Invited")},
  "cat":None,"cat2":"MoM Distributed","status":"Status"},
 {"key":"disc","sheet":"Disciplinary Actions","emoji":"⚖️","code":"DA",
  "headers":["S.No","Case No.","Date","Month","Violation Type","Department","Employee Name",
    "Action Taken","Offense Level","Approved By","Status"],
  "auto":{},"cat":"Violation Type","cat2":"Offense Level","status":"Status"},
 {"key":"awards","sheet":"Safety Awards","emoji":"🏆","code":"AW",
  "headers":["S.No","Award ID","Date","Month","Award Category","Department","Recipient",
    "Reward Type","Presented By","Status"],
  "auto":{},"cat":"Award Category","cat2":"Reward Type","status":"Status"},
 {"key":"swa","sheet":"Stop Work Authority","emoji":"✋","code":"SWA",
  "headers":["S.No","SWA No.","Date","Month","Reason for Stop Work","Department","Location",
    "Initiated By","Authorized By","Downtime (min)","Severity","Resolution","Investigation Done"],
  "auto":{},"cat":"Severity","cat2":"Resolution","status":None},
 {"key":"alcohol","sheet":"Alcohol Tests","emoji":"🧪","code":"AT",
  "headers":["S.No","Test ID","Date","Month","Department","Employee Tested","Test Type",
    "Result","Tested By","Status"],
  "auto":{},"cat":"Test Type","cat2":"Result","status":"Status"},
 {"key":"ptwaudit","sheet":"PTW Audits","emoji":"📝","code":"PTA",
  "headers":["S.No","Audit No.","Date","Month","Permit Type Audited","Department","Location",
    "Auditor","Permits Reviewed","Deviations Found","Total Checkpoints","Compliance %","Verdict",
    "Action Required"],
  "auto":{"Compliance %":("__ptw__","Total Checkpoints")},"cat":"Permit Type Audited","cat2":None,"status":"Verdict"},
 {"key":"ca","sheet":"Corrective Actions","emoji":"🔧","code":"CA",
  "headers":["S.No","CA No.","Date Raised","Month","Source","Department","Location",
    "Corrective Action","Priority","Assigned To","Verified By","Due Date","Completion Date",
    "Status","Timeliness"],
  "auto":{},"cat":"Source","cat2":"Priority","status":"Status"},
 {"key":"nc","sheet":"NC Management","emoji":"🚩","code":"NC",
  "headers":["S.No","NC No.","Date Raised","Month","Source","Severity","Department",
    "NC Description","Assigned To","Approved By","Target Close Date","Actual Close Date",
    "Status","Root Cause / CAPA"],
  "auto":{},"cat":"Severity","cat2":"Source","status":"Status"},
 {"key":"unsafeact","sheet":"Unsafe Acts","emoji":"🚫","code":"UA",
  "headers":["S.No","Report No.","Date","Month","Description","Department","Location",
    "Reported By","Risk Level","Immediate Action","Corrective Action","Due Date","Status"],
  "auto":{},"cat":"Risk Level","cat2":"Description","status":"Status"},
 {"key":"unsafecond","sheet":"Unsafe Conditions","emoji":"⛔","code":"UC",
  "headers":["S.No","Report No.","Date","Month","Description","Department","Location",
    "Reported By","Risk Level","Immediate Action","Corrective Action","Due Date","Status"],
  "auto":{},"cat":"Risk Level","cat2":"Description","status":"Status"},
 {"key":"incident","sheet":"Incident","emoji":"🔥","code":"INC",
  "headers":["S.No","Incident ID","Date","Month","Week","Quarter","Financial Year","Department",
    "Area","Production Line","Shift","Location","Incident Type","Classification","Person Involved",
    "Person Type","Body Part","Description","Immediate Cause","Root Cause","Risk Rating",
    "Lost Days","Corrective Action","Preventive Action","Responsible","Target Date","Closure Date",
    "Status","Ageing (Days)","Evidence Link"],
  "auto":{},"cat":"Classification","cat2":"Incident Type","status":"Status"},
]

# fix emoji typo
for r in REGISTERS:
    if r["key"]=="bulletins": r["emoji"]="📢"


def pool_for(header):
    if header in POOLS: return POOLS[header]
    return None


def gen_value(header, d, rownum, code, dept, key=None):
    h = header
    if h == "S.No": return rownum
    # realistic safety pyramid for incident classification
    if h == "Classification":
        return random.choices(
            ["Near Miss","First Aid","Medical Treatment","Restricted Work","Lost Time Injury","Fatality"],
            weights=[0.50,0.27,0.12,0.06,0.045,0.005])[0]
    if h == "Approval Status" and key == "jsa":
        return random.choices(["Approved","Pending Review","Revision Required","Rejected"],
                              [0.52,0.28,0.13,0.07])[0]
    # register-appropriate status domains (aligned to the client's reference dashboard cards)
    if h == "Status":
        pool = STATUS_POOLS.get(key)
        if pool:
            vals, weights = pool
            return random.choices(vals, weights)[0]
        return random.choices(["Closed","In Progress","Open","Overdue"],[0.62,0.18,0.12,0.08])[0]
    if h == "Severity" and key == "nc":
        return random.choices(["Major","Minor","Observation"],[0.40,0.35,0.25])[0]
    if h == "Severity" and key == "swa":
        return random.choices(["Critical","High","Medium"],[0.30,0.35,0.35])[0]
    if h == "Action Taken" and key == "disc":
        return random.choices(["Verbal Warning","Written Warning","Suspension","Retraining","Termination"],
                              [0.30,0.28,0.20,0.14,0.08])[0]
    if h == "Offense Level":
        return random.choices(["1st Offense","2nd Offense","3rd Offense","Repeat"],[0.45,0.25,0.10,0.20])[0]
    if h == "Observation Type" and key == "hseobs":
        return random.choices(["Safe Act","Unsafe Act","Safe Condition","Unsafe Condition","Near Miss"],
                              [0.28,0.24,0.16,0.14,0.18])[0]
    if h == "Resolution" and key == "swa":
        return random.choices(["Resolved","Permanent Fix Applied","Under Investigation"],
                              [0.35,0.40,0.25])[0]
    if h in ("Risk Level","Risk Rating","Severity"):
        return random.choices(["Critical","High","Medium","Low"],[0.06,0.20,0.42,0.32])[0]
    # meaningful "type" phrase for Unsafe Act / Unsafe Condition Description (used as category)
    if h == "Description" and key == "unsafeact":
        return random.choice(UNSAFE_ACT_TYPES)
    if h == "Description" and key == "unsafecond":
        return random.choice(UNSAFE_COND_TYPES)
    if h == "Root Cause / CAPA" and key == "nc":
        return random.choice(ROOT_CAUSES)
    if h in ("Date","Date Raised","Date Issued"): return d
    if h == "Month": return MONTHS[d.month-1]
    if h == "Week": return "W%d" % (((d.day-1)//7)+1)
    if h == "Quarter": return "Q%d" % ((d.month-1)//3+1)
    if h == "Financial Year": return "FY%d-%d" % (YEAR, YEAR+1)
    if h.endswith(("No.","No")) or h.endswith("ID") or h in ("Ref No.",):
        return "%s-%04d" % (code, 1000+rownum)
    if h == "Department": return dept
    if h in ("Location","Area","Target Audience"): return random.choice(LOCATIONS)
    if h == "Production Line": return random.choice(POOLS["Production Line"])
    if h == "Shift": return random.choice(POOLS["Shift"])
    # people-ish
    if any(k in h for k in ["By","Trainer","Inspector","Auditor","Leader","Recipient",
        "Employee","Responsible","Assigned","Person Involved","Chaired"]):
        return random.choice(PEOPLE)
    # dates (secondary)
    if "Date" in h:
        return d + timedelta(days=random.randint(5,45))
    # numeric-ish
    if h.endswith("%"): return ""  # filled by formula or later
    if any(k in h for k in ["Target Attendees","Actual Attendees","Invited","Attended",
        "Target Participants","Actual Participants","Target Reach","Actual Reach",
        "Permits Reviewed","Members Invited","Members Attended"]):
        return random.randint(10,60)
    if "Checkpoints" in h: return random.randint(15,50)
    if any(k in h for k in ["Non-Conformances","Minor NC","Major NC","Deviations",
        "Observations Made","Observations","Action Items Raised","Actions Raised",
        "Actions Closed","Actions Assigned","Decisions Made","Recommendations",
        "Hazards Identified","Critical Findings"]):
        return random.randint(0,8)
    if "Duration" in h: return random.randint(15,120)
    if any(k in h for k in ["Downtime","Lost Days","Response","Ageing"]):
        return random.randint(0,30)
    # categorical from pools (longest header key match)
    p = pool_for(h)
    if p: return random.choice(p)
    for key,vals in POOLS.items():
        if key in h: return random.choice(vals)
    if h in ("Status",): return random.choice(STATUS)
    # free text
    if any(k in h for k in ["Topic","Course Name","Task/Activity","Subject","Reason",
        "Description","Scope","Audit Scope","Review Topic","Inspection Area","Item",
        "Corrective Action","Preventive Action","Controls","Immediate Action",
        "NC Description","Root Cause / CAPA","Improvement","Action Required","Evidence Link"]):
        return random.choice(TOPICS)
    return random.choice(TOPICS)


def generate(spec, n=48):
    """Generate n data rows (list of value lists in header order)."""
    headers = spec["headers"]
    rows = []
    for i in range(n):
        m = random.randint(1, MAX_MONTH)
        d = date(YEAR, m, random.randint(1,28))
        dept = random.choice(DEPARTMENTS)
        row = [gen_value(h, d, i+1, spec["code"], dept, spec["key"]) for h in headers]
        rows.append(row)
    rows.sort(key=lambda r: r[headers.index("Month")] and MONTHS.index(r[headers.index("Month")]))
    # re-number S.No
    for i,r in enumerate(rows):
        r[0] = i+1
    return rows


def build_all():
    return {spec["key"]: generate(spec) for spec in REGISTERS}


if __name__ == "__main__":
    data = build_all()
    for spec in REGISTERS:
        print("%-22s %3d rows  %2d cols"%(spec["sheet"], len(data[spec["key"]]), len(spec["headers"])))
