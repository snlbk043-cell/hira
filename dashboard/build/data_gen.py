"""Realistic sample-data generator for the RCPL Executive EHS KPI Dashboard."""
import random
from datetime import date, timedelta

random.seed(2026)

YEARS = [2024, 2025, 2026]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# 2026 data only up to June (current date 2026-07-09)
MAX_MONTH = {2024: 12, 2025: 12, 2026: 6}

DEPARTMENTS = [
    "Production-CSD", "Production-Blowing", "Utilities", "Warehouse",
    "Quality", "Engineering", "Water Treatment", "Syrup Room",
    "Packaging", "Logistics",
]
AREAS = [
    "Filling Line 1", "Filling Line 2", "Blow Molding", "Syrup Room",
    "Boiler House", "ETP/WTP", "RM Warehouse", "FG Warehouse",
    "Compressor Room", "QC Lab", "Workshop", "Loading Bay",
]
SHIFTS = ["Shift A", "Shift B", "Shift C", "General"]
CONTRACTORS = ["RCPL Direct", "SafeBuild Infra", "PowerMech Services",
               "CleanPro Facility", "LogiTrans", "AquaTech"]
EMP_CATEGORY = ["Permanent", "Contract", "Trainee", "Visitor"]
SEVERITY = ["Low", "Medium", "High", "Critical", "Catastrophic"]  # 1..5

INCIDENT_TYPES = ["First Aid Case", "Medical Treatment Case", "Lost Time Injury",
                  "Restricted Work Case", "Property Damage", "Fire", "Environmental Spill"]
ROOT_CAUSES = ["Slip/Trip/Fall", "Caught In/Between", "Struck by Object",
               "Chemical Exposure", "Ergonomic Strain", "Electrical",
               "Machine Guarding", "PPE Non-Use", "Procedure Not Followed",
               "Poor Housekeeping"]
UNSAFE_ACTS = ["Bypassing Safety Device", "Not Using PPE", "Improper Lifting",
               "Working Without Permit", "Operating Without Authority",
               "Using Defective Equipment", "Horseplay", "Wrong Tool Use",
               "LOTO Not Followed", "Forklift Overspeeding"]
UNSAFE_CONDITIONS = ["Slippery Floor", "Poor Housekeeping", "Inadequate Lighting",
                     "Damaged Machine Guard", "Exposed Wiring", "Blocked Walkway",
                     "Missing Signage", "Chemical Leak", "Faulty Ladder",
                     "Blocked Fire Exit"]
PERMIT_TYPES = ["Hot Work", "Work at Height", "Confined Space", "Electrical",
                "Excavation", "Lifting", "Cold Work", "Line Breaking"]
TRAINING_TOPICS = ["Induction Safety", "Fire Fighting", "First Aid", "Work at Height",
                   "Confined Space", "Chemical Handling", "Forklift Operation",
                   "LOTO", "Emergency Response", "BBS Awareness"]
AUDIT_TYPES = ["Internal EHS Audit", "External Audit", "ISO 45001", "FSSAI Safety",
               "Legal Compliance", "Fire Safety Audit", "Management Walkthrough"]
INSPECTION_TYPES = ["Workplace Inspection", "Fire Equipment", "Electrical Safety",
                    "Machine Guarding", "PPE Inspection", "Housekeeping", "Ladder/Scaffold"]
STATUTORY_ITEMS = ["Factory License", "Consent to Operate (Air)", "Consent to Operate (Water)",
                   "Fire NOC", "Pressure Vessel Cert.", "Lift License", "Boiler License",
                   "Hazardous Waste Authorization", "Form-11 Health Check", "Safety Committee"]

STATUS_OPEN_CLOSED = ["Open", "In Progress", "Closed"]


def month_iter():
    for y in YEARS:
        for mi in range(MAX_MONTH[y]):
            yield y, mi + 1, MONTHS[mi]


def rdate(y, m):
    day = random.randint(1, 28)
    return date(y, m, day)


def trend_factor(y, m):
    """Improving safety trend -> fewer incidents over time (0.6..1.3)."""
    idx = (y - 2024) * 12 + (m - 1)
    total = 30.0
    return 1.30 - 0.7 * (idx / total)


# --------------------------------------------------------------------------
def gen_manhours():
    """Master man-hours by year/month/department."""
    rows = []
    for y, m, mn in month_iter():
        for d in DEPARTMENTS:
            base = random.randint(28000, 46000)
            rows.append([y, m, mn, d, base])
    return rows


def gen_incidents():
    rows = []
    iid = 1000
    weights = [0.42, 0.20, 0.10, 0.10, 0.10, 0.03, 0.05]
    for y, m, mn in month_iter():
        n = max(1, int(round(random.randint(2, 6) * trend_factor(y, m))))
        for _ in range(n):
            iid += 1
            itype = random.choices(INCIDENT_TYPES, weights=weights)[0]
            sev_i = random.randint(1, 5)
            if itype == "Lost Time Injury":
                sev_i = max(sev_i, 3)
                lost = random.randint(3, 45)
            elif itype == "Restricted Work Case":
                lost = random.randint(1, 10)
            else:
                lost = 0
            d = rdate(y, m)
            status = random.choices(STATUS_OPEN_CLOSED, [0.12, 0.18, 0.70])[0]
            closed = "" if status != "Closed" else (d + timedelta(days=random.randint(3, 40)))
            rows.append([
                "INC-%d" % iid, d, y, m, mn, random.choice(DEPARTMENTS),
                random.choice(AREAS), random.choice(SHIFTS), itype,
                SEVERITY[sev_i - 1], sev_i, random.choice(ROOT_CAUSES),
                random.choice(CONTRACTORS), random.choice(EMP_CATEGORY),
                lost, status, closed,
            ])
    return rows


def gen_firstaid():
    rows = []
    fid = 2000
    body = ["Hand", "Finger", "Eye", "Foot", "Leg", "Arm", "Head", "Back", "Torso"]
    for y, m, mn in month_iter():
        n = max(2, int(round(random.randint(4, 10) * trend_factor(y, m))))
        for _ in range(n):
            fid += 1
            rows.append([
                "FA-%d" % fid, rdate(y, m), y, m, mn, random.choice(DEPARTMENTS),
                random.choice(AREAS), random.choice(SHIFTS), random.choice(body),
                random.choice(ROOT_CAUSES), random.choice(EMP_CATEGORY), "Closed",
            ])
    return rows


def gen_nearmiss():
    rows = []
    nid = 3000
    for y, m, mn in month_iter():
        n = max(3, int(round(random.randint(8, 20) * (2 - trend_factor(y, m) + 0.3))))
        for _ in range(n):
            nid += 1
            hipo = random.random() < 0.18
            status = random.choices(STATUS_OPEN_CLOSED, [0.10, 0.15, 0.75])[0]
            rows.append([
                "NM-%d" % nid, rdate(y, m), y, m, mn, random.choice(DEPARTMENTS),
                random.choice(AREAS), random.choice(SHIFTS),
                random.choice(UNSAFE_CONDITIONS + UNSAFE_ACTS),
                "High Potential" if hipo else "Standard",
                random.choice(ROOT_CAUSES), random.choice(EMP_CATEGORY), status,
            ])
    return rows


def gen_safety_obs():
    rows = []
    sid = 4000
    cats = ["Unsafe Act", "Unsafe Condition", "Good Catch", "Positive Observation"]
    for y, m, mn in month_iter():
        n = max(5, int(round(random.randint(15, 35) * (2 - trend_factor(y, m) + 0.4))))
        for _ in range(n):
            sid += 1
            cat = random.choices(cats, [0.35, 0.35, 0.15, 0.15])[0]
            if cat == "Unsafe Act":
                desc = random.choice(UNSAFE_ACTS)
            elif cat == "Unsafe Condition":
                desc = random.choice(UNSAFE_CONDITIONS)
            else:
                desc = "Proactive reporting"
            status = random.choices(["Open", "Closed"], [0.22, 0.78])[0]
            rows.append([
                "SO-%d" % sid, rdate(y, m), y, m, mn, random.choice(DEPARTMENTS),
                random.choice(AREAS), random.choice(SHIFTS), cat, desc,
                random.choice(SEVERITY), random.choice(EMP_CATEGORY), status,
            ])
    return rows


def gen_register_top(prefix, items, start, per_month=(4, 12)):
    rows = []
    rid = start
    for y, m, mn in month_iter():
        n = random.randint(*per_month)
        for _ in range(n):
            rid += 1
            status = random.choices(["Open", "Closed"], [0.25, 0.75])[0]
            rows.append([
                "%s-%d" % (prefix, rid), rdate(y, m), y, m, mn,
                random.choice(DEPARTMENTS), random.choice(AREAS),
                random.choice(items), random.choice(SEVERITY),
                random.choice(SHIFTS), status,
            ])
    return rows


def gen_inspection():
    rows = []
    iid = 6000
    for y, m, mn in month_iter():
        for d in random.sample(DEPARTMENTS, k=random.randint(6, 10)):
            iid += 1
            planned = 1
            done = random.random() < (0.80 + 0.03 * (y - 2024))
            findings = random.randint(0, 8) if done else 0
            closed = random.randint(0, findings)
            rows.append([
                "INS-%d" % iid, rdate(y, m), y, m, mn, d, random.choice(AREAS),
                random.choice(INSPECTION_TYPES), planned, 1 if done else 0,
                findings, closed, "Closed" if done and closed == findings else "Open",
            ])
    return rows


def gen_audit():
    rows = []
    aid = 7000
    for y, m, mn in month_iter():
        for _ in range(random.randint(1, 3)):
            aid += 1
            score = random.randint(68, 98)
            ncr = random.randint(0, 12)
            closed = random.randint(0, ncr)
            rows.append([
                "AUD-%d" % aid, rdate(y, m), y, m, mn, random.choice(DEPARTMENTS),
                random.choice(AUDIT_TYPES), score, ncr, closed,
                "Closed" if closed == ncr else "Open",
            ])
    return rows


def gen_statutory():
    rows = []
    cid = 8000
    for item in STATUTORY_ITEMS:
        for d in random.sample(DEPARTMENTS, k=3):
            cid += 1
            valid = random.random() < 0.9
            due = date(2026, random.randint(1, 12), random.randint(1, 28))
            rows.append([
                "STAT-%d" % cid, item, d, "Valid" if valid else "Expired",
                due, "Compliant" if valid else "Non-Compliant",
                random.choice(["Regulatory", "Statutory", "Certification"]),
            ])
    return rows


def gen_ptw():
    rows = []
    pid = 9000
    for y, m, mn in month_iter():
        n = random.randint(20, 45)
        for _ in range(n):
            pid += 1
            compliant = random.random() < (0.86 + 0.03 * (y - 2024))
            rows.append([
                "PTW-%d" % pid, rdate(y, m), y, m, mn, random.choice(DEPARTMENTS),
                random.choice(AREAS), random.choice(PERMIT_TYPES),
                random.choice(CONTRACTORS), random.choice(SHIFTS),
                "Compliant" if compliant else "Non-Compliant",
                "Closed" if random.random() < 0.9 else "Open",
            ])
    return rows


def gen_training():
    rows = []
    tid = 10000
    for y, m, mn in month_iter():
        for d in DEPARTMENTS:
            tid += 1
            planned = random.randint(10, 40)
            done = int(planned * random.uniform(0.72, 1.0))
            rows.append([
                "TRN-%d" % tid, rdate(y, m), y, m, mn, d,
                random.choice(TRAINING_TOPICS), planned, done,
                round(done / planned * 100, 1),
            ])
    return rows


def gen_ppe():
    rows = []
    pid = 11000
    for y, m, mn in month_iter():
        for d in DEPARTMENTS:
            pid += 1
            checked = random.randint(20, 60)
            compliant = int(checked * random.uniform(0.82, 1.0))
            rows.append([
                "PPE-%d" % pid, rdate(y, m), y, m, mn, d, random.choice(AREAS),
                checked, compliant, round(compliant / checked * 100, 1),
            ])
    return rows


def gen_contractor():
    rows = []
    cid = 12000
    for c in CONTRACTORS:
        for y in YEARS:
            cid += 1
            workers = random.randint(15, 120)
            trained = int(workers * random.uniform(0.8, 1.0))
            incidents = random.randint(0, 6)
            rows.append([
                "CON-%d" % cid, c, y, workers, trained,
                round(trained / workers * 100, 1), incidents,
                round(random.uniform(75, 98), 1),
            ])
    return rows


def gen_simple_register(prefix, start, topic_list, cols_extra):
    rows = []
    rid = start
    for y, m, mn in month_iter():
        for _ in range(random.randint(2, 6)):
            rid += 1
            extra = [random.choice(topic_list)]
            rows.append(["%s-%d" % (prefix, rid), rdate(y, m), y, m, mn,
                         random.choice(DEPARTMENTS)] + extra + cols_extra())
    return rows


def gen_toolbox():
    rows = []
    tid = 13000
    for y, m, mn in month_iter():
        for d in DEPARTMENTS:
            tid += 1
            attend = random.randint(8, 35)
            rows.append(["TBT-%d" % tid, rdate(y, m), y, m, mn, d,
                         random.choice(TRAINING_TOPICS), attend, random.choice(SHIFTS)])
    return rows


def gen_bbs():
    rows = []
    bid = 14000
    for y, m, mn in month_iter():
        n = random.randint(10, 30)
        for _ in range(n):
            bid += 1
            safe = random.random() < 0.7
            rows.append(["BBS-%d" % bid, rdate(y, m), y, m, mn,
                         random.choice(DEPARTMENTS), random.choice(AREAS),
                         "Safe" if safe else "At-Risk",
                         random.choice(UNSAFE_ACTS), random.choice(EMP_CATEGORY)])
    return rows


def gen_drill():
    rows = []
    did = 15000
    drills = ["Fire Evacuation", "Chemical Spill", "Medical Emergency",
              "Gas Leak", "Confined Space Rescue"]
    for y, m, mn in month_iter():
        if random.random() < 0.6:
            did += 1
            resp = random.randint(3, 12)
            rows.append(["DRL-%d" % did, rdate(y, m), y, m, mn,
                         random.choice(drills), resp,
                         random.choice(["Satisfactory", "Needs Improvement", "Excellent"]),
                         random.randint(20, 200)])
    return rows


def gen_fire_equip():
    rows = []
    fid = 16000
    equip = ["Fire Extinguisher", "Hydrant", "Sprinkler", "Smoke Detector",
             "Fire Alarm", "Hose Reel", "Emergency Light"]
    for y, m, mn in month_iter():
        for _ in range(random.randint(5, 12)):
            fid += 1
            ok = random.random() < 0.9
            rows.append(["FE-%d" % fid, rdate(y, m), y, m, mn,
                         random.choice(equip), random.choice(AREAS),
                         "OK" if ok else "Defective",
                         "Closed" if ok else "Open"])
    return rows


def gen_risk():
    rows = []
    rid = 17000
    for y, m, mn in month_iter():
        for _ in range(random.randint(2, 5)):
            rid += 1
            lik = random.randint(1, 5)
            sev = random.randint(1, 5)
            score = lik * sev
            level = ("Low" if score <= 4 else "Medium" if score <= 9
                     else "High" if score <= 15 else "Critical")
            rows.append(["RA-%d" % rid, rdate(y, m), y, m, mn,
                         random.choice(DEPARTMENTS), random.choice(AREAS),
                         random.choice(ROOT_CAUSES), lik, sev, score, level,
                         random.choice(["Open", "Mitigated", "Closed"])])
    return rows


def gen_capa():
    rows = []
    cid = 18000
    sources = ["Incident", "Audit", "Inspection", "Near Miss", "Observation", "Drill"]
    for y, m, mn in month_iter():
        for _ in range(random.randint(4, 12)):
            cid += 1
            status = random.choices(["Open", "In Progress", "Closed", "Overdue"],
                                    [0.15, 0.2, 0.55, 0.1])[0]
            due = rdate(y, m) + timedelta(days=random.randint(10, 60))
            rows.append(["CAPA-%d" % cid, rdate(y, m), y, m, mn,
                         random.choice(sources), random.choice(DEPARTMENTS),
                         random.choice(ROOT_CAUSES), random.choice(["Corrective", "Preventive"]),
                         random.choice(SEVERITY), due, status,
                         random.choice(["Safety Officer", "Dept Head", "Engineer", "EHS Manager"])])
    return rows


def build_all():
    return {
        "manhours": gen_manhours(),
        "incidents": gen_incidents(),
        "firstaid": gen_firstaid(),
        "nearmiss": gen_nearmiss(),
        "safety_obs": gen_safety_obs(),
        "unsafe_act": gen_register_top("UA", UNSAFE_ACTS, 5000),
        "unsafe_cond": gen_register_top("UC", UNSAFE_CONDITIONS, 5500),
        "inspection": gen_inspection(),
        "audit": gen_audit(),
        "statutory": gen_statutory(),
        "ptw": gen_ptw(),
        "training": gen_training(),
        "ppe": gen_ppe(),
        "contractor": gen_contractor(),
        "toolbox": gen_toolbox(),
        "bbs": gen_bbs(),
        "drill": gen_drill(),
        "fire_equip": gen_fire_equip(),
        "risk": gen_risk(),
        "capa": gen_capa(),
    }


if __name__ == "__main__":
    data = build_all()
    for k, v in data.items():
        print("%-14s %5d rows" % (k, len(v)))
