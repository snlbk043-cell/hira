"""VBA for the Integrated EHS Management System."""
from xlsxwriter.utility import xl_col_to_name
import hse_data as HD

# the 8 registers with a genuine due-date + owner field, feeding the My Actions tracker -
# (register key, display label, owner-field header, description-field header, due-date-field header)
ACTION_TRACKER_SPECS = [
    ("ca","Corrective Actions","Assigned To","Corrective Action","Due Date"),
    ("nc","NC Management","Assigned To","NC Description","Target Close Date"),
    ("hseobs","HSE Observations","Responsible Person","Description","Due Date"),
    ("wpinsp","Workplace Inspections","Inspector","Inspection Area/Item","Due Date"),
    ("eqinsp","Equipment Inspections","Inspector","Inspection Area/Item","Due Date"),
    ("walk","Safety Walkthroughs","Inspector","Inspection Area/Item","Due Date"),
    ("unsafeact","Unsafe Acts","Reported By","Description","Due Date"),
    ("unsafecond","Unsafe Conditions","Reported By","Description","Due Date"),
]

THISWORKBOOK = '''Attribute VB_Name = "ThisWorkbook"
Attribute VB_Base = "0{00020819-0000-0000-C000-000000000046}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

Private Sub Workbook_Open()
    On Error Resume Next
    Application.Calculation = xlCalculationAutomatic
    Application.CalculateFull
    modEHS.ProtectAllSheets
    Sheets("Home").Range("LastRefresh").Value = Now
    Sheets("Home").Activate
End Sub

'==========================================================
' CHANGE LOG (audit trail)
'   SelectionChange caches the value of the cell about to be
'   edited; SheetChange then logs old -> new to "Change Log"
'   whenever the edit is on one of the 24 registers. Only
'   single-cell edits get a real Old Value (multi-cell pastes
'   log "(n/a)" for Old Value - see modEHS.LogChange).
'==========================================================
Private Sub Workbook_SheetSelectionChange(ByVal Sh As Object, ByVal Target As Range)
    On Error Resume Next
    If Target.Cells.Count = 1 Then
        modEHS.PrevChangeAddress = Sh.Name & "!" & Target.Address(False, False)
        modEHS.PrevChangeValue = Target.Value
    Else
        modEHS.PrevChangeAddress = ""
    End If
End Sub

Private Sub Workbook_SheetChange(ByVal Sh As Object, ByVal Target As Range)
    modEHS.LogChange Sh, Target
End Sub
'''

MOD_BASE = '''Attribute VB_Name = "modEHS"
Option Explicit

Public Sub RefreshAllData()
    Application.ScreenUpdating = False
    On Error Resume Next
    ThisWorkbook.RefreshAll
    Application.CalculateFull
    Sheets("Home").Range("LastRefresh").Value = Now
    Application.ScreenUpdating = True
    MsgBox "EHS system refreshed." & vbCrLf & "Last refresh: " & _
           Format(Now, "dd-mmm-yyyy hh:nn"), vbInformation, "Refresh Complete"
End Sub

Public Sub ResetFilters()
    On Error Resume Next
    With Sheets("Executive Dashboard")
        .Range("SelPeriod").Value = "Jan"
        .Range("SelMonth").Value = "All"
        .Range("SelDept").Value = "All"
    End With
    Application.CalculateFull
    MsgBox "Filters reset.", vbInformation, "Filters Reset"
End Sub

'==========================================================
' SHEET PROTECTION
'   Locks every formula/label cell so it can't be typed over
'   by accident; genuine input cells (registers' blue columns,
'   Settings' amber cells, the Executive filter drop-downs)
'   stay editable. UserInterfaceOnly:=True means these macros
'   (and Workbook_Open) can still write to any cell regardless.
'==========================================================
Public Sub ProtectAllSheets()
    Dim ws As Worksheet
    On Error Resume Next
    For Each ws In ThisWorkbook.Worksheets
        If ws.Name <> "Master Data" And ws.Name <> "Pivot Analysis" And ws.Name <> "My Actions" And ws.Name <> "Change Log" Then
            ws.Protect Password:="", DrawingObjects:=False, Contents:=True, _
                Scenarios:=True, UserInterfaceOnly:=True, AllowFiltering:=True, _
                AllowSorting:=True, AllowInsertingRows:=True
        End If
    Next ws
End Sub

Public Sub UnprotectAllSheets()
    Dim ws As Worksheet
    On Error Resume Next
    For Each ws In ThisWorkbook.Worksheets
        ws.Unprotect Password:=""
    Next ws
    MsgBox "All sheets unprotected for editing. Run ProtectAllSheets (or reopen the file) to re-lock.", _
           vbInformation, "Unprotected"
End Sub

'==========================================================
' NATIVE PIVOT TABLES + SLICERS
'   Builds real, fully-interactive PivotTables (not formulas)
'   from the underlying Tables, with Slicers for point-and-click
'   analysis. Safe to re-run - rebuilds the sheet each time.
'==========================================================
Public Sub BuildPivotAnalysis()
    Dim wsP As Worksheet
    Dim pc As PivotCache
    Dim pt As PivotTable
    Dim destRow As Long

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    On Error Resume Next
    ThisWorkbook.Worksheets("Pivot Analysis").Delete
    On Error GoTo 0
    Application.DisplayAlerts = True

    Set wsP = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
    wsP.Name = "Pivot Analysis"
    wsP.Tab.Color = RGB(15, 61, 110)
    wsP.Range("B2").Value = "PIVOT ANALYSIS  -  native Excel PivotTables & Slicers"
    wsP.Range("B2").Font.Size = 16
    wsP.Range("B2").Font.Bold = True
    wsP.Range("B3").Value = "Drag fields in the PivotTable Fields pane to explore further. Right-click any table then Refresh after adding new register rows."
    wsP.Hyperlinks.Add Anchor:=wsP.Range("B4"), Address:="", SubAddress:="'Home'!A1", TextToDisplay:="Home"

    ' --- Pivot 1: Incident (Department x Classification) ---
    On Error Resume Next
    Set pc = ThisWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:="t_incident")
    Set pt = pc.CreatePivotTable(TableDestination:=wsP.Range("B6"), TableName:="PT_Incident")
    With pt
        .PivotFields("Department").Orientation = xlRowField
        .PivotFields("Classification").Orientation = xlColumnField
        .AddDataField .PivotFields("Incident ID"), "Count of Incidents", xlCount
    End With
    On Error Resume Next
    ActiveWorkbook.SlicerCaches.Add2(pt, "Department").Slicers.Add _
        SlicerDestination:=wsP, Caption:="Department", Left:=520, Top:=95, Width:=140, Height:=180

    ' --- Pivot 2: Training (Department x Status) ---
    On Error Resume Next
    Set pc = ThisWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:="t_training")
    Set pt = pc.CreatePivotTable(TableDestination:=wsP.Range("B26"), TableName:="PT_Training")
    With pt
        .PivotFields("Department").Orientation = xlRowField
        .PivotFields("Status").Orientation = xlColumnField
        .AddDataField .PivotFields("Training ID"), "Count of Trainings", xlCount
    End With
    On Error Resume Next
    ActiveWorkbook.SlicerCaches.Add2(pt, "Training Type").Slicers.Add _
        SlicerDestination:=wsP, Caption:="Training Type", Left:=520, Top:=290, Width:=140, Height:=180

    ' --- Pivot 3: Corrective Actions (Department x Status) ---
    On Error Resume Next
    Set pc = ThisWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:="t_ca")
    Set pt = pc.CreatePivotTable(TableDestination:=wsP.Range("B46"), TableName:="PT_CorrectiveActions")
    With pt
        .PivotFields("Department").Orientation = xlRowField
        .PivotFields("Status").Orientation = xlColumnField
        .AddDataField .PivotFields("CA No."), "Count of CAPAs", xlCount
    End With
    On Error Resume Next
    ActiveWorkbook.SlicerCaches.Add2(pt, "Priority").Slicers.Add _
        SlicerDestination:=wsP, Caption:="Priority", Left:=520, Top:=485, Width:=140, Height:=180

    wsP.Columns("B:J").AutoFit
    Application.ScreenUpdating = True
    MsgBox "Pivot Analysis built: Incident, Training and Corrective Action PivotTables " & _
           "with Slicers. Right-click any table -> Refresh after new data is added.", _
           vbInformation, "Pivot Analysis Ready"
End Sub

'==========================================================
' BOARD PACK PDF
'==========================================================
Public Sub ExportBoardPack()
    Dim fName As String
    Dim arr As Variant
    On Error Resume Next
    arr = Array("Cover Page", "Executive Dashboard", "Leadership Review")
    fName = ThisWorkbook.Path & Application.PathSeparator & _
            "RCPL_EHS_Board_Pack_" & Format(Now, "yyyymmdd_hhnn") & ".pdf"
    Sheets(arr).Select
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fName, _
        Quality:=xlQualityStandard, OpenAfterPublish:=False
    Sheets("Home").Select
    MsgBox "Board pack exported:" & vbCrLf & fName, vbInformation, "Board Pack Ready"
End Sub

Public Sub GoHome()
    Sheets("Home").Activate
    ActiveWindow.ScrollRow = 1: ActiveWindow.ScrollColumn = 1
End Sub

Public Sub PrintDashboard()
    On Error Resume Next
    ActiveSheet.PrintOut
End Sub

Public Sub ExportDashboardPDF()
    Dim fName As String
    On Error Resume Next
    fName = ThisWorkbook.Path & Application.PathSeparator & _
            ActiveSheet.Name & "_" & Format(Now, "yyyymmdd_hhnn") & ".pdf"
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fName, _
        Quality:=xlQualityStandard, OpenAfterPublish:=False
    MsgBox "Exported:" & vbCrLf & fName, vbInformation, "PDF Export"
End Sub

'==========================================================
' DEPARTMENT-SPECIFIC ONE-PAGE REPORT
'   Temporarily sets the Executive Department filter, exports
'   Executive Dashboard + Leadership Review as one PDF, then
'   restores whatever filter was previously selected.
'==========================================================
Public Sub ExportDepartmentReport()
    Dim dept As String, fName As String, prevDept As String
    dept = InputBox("Enter the Department exactly as it appears in the dropdown " & _
                     "(e.g. Production, Quality, Maintenance, Warehouse, ...):", _
                     "Department Report", "All")
    If dept = "" Then Exit Sub
    On Error Resume Next
    prevDept = Sheets("Executive Dashboard").Range("SelDept").Value
    Application.ScreenUpdating = False
    Sheets("Executive Dashboard").Range("SelDept").Value = dept
    Application.CalculateFull
    fName = ThisWorkbook.Path & Application.PathSeparator & _
            "RCPL_EHS_Report_" & Replace(Replace(dept, " ", "_"), "/", "-") & "_" & Format(Now, "yyyymmdd_hhnn") & ".pdf"
    Sheets(Array("Executive Dashboard", "Leadership Review")).Select
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fName, _
        Quality:=xlQualityStandard, OpenAfterPublish:=False
    Sheets("Executive Dashboard").Range("SelDept").Value = prevDept
    Application.CalculateFull
    Sheets("Home").Select
    Application.ScreenUpdating = True
    MsgBox "Department report exported:" & vbCrLf & fName, vbInformation, "Department Report Ready"
End Sub
'''

def _build_logchange_code():
    """The Change Log's LogChange sub, with the 24 register sheet names computed from
    HD.REGISTERS (never hand-typed) so new registers are covered automatically."""
    reg_names = [s["sheet"] for s in HD.REGISTERS]
    names_arr = "Array(" + ", ".join('"%s"' % n.replace('"', '""') for n in reg_names) + ")"
    return '''

'==========================================================
' CHANGE LOG helper (called from ThisWorkbook's Workbook_SheetChange)
'==========================================================
Public PrevChangeAddress As String
Public PrevChangeValue As Variant

Public Sub LogChange(ByVal Sh As Object, ByVal Target As Range)
    Dim regNames As Variant, isReg As Boolean, i As Long
    Dim wsLog As Worksheet, r As Long, c As Range, oldVal As String, curAddr As String

    regNames = %s
    isReg = False
    For i = LBound(regNames) To UBound(regNames)
        If Sh.Name = CStr(regNames(i)) Then isReg = True: Exit For
    Next i
    If Not isReg Then Exit Sub

    On Error Resume Next
    Set wsLog = ThisWorkbook.Worksheets("Change Log")
    If wsLog Is Nothing Then Exit Sub
    r = wsLog.Cells(wsLog.Rows.Count, "B").End(xlUp).Row + 1
    If r < 6 Then r = 6

    For Each c In Target.Cells
        curAddr = Sh.Name & "!" & c.Address(False, False)
        If curAddr = PrevChangeAddress Then
            oldVal = CStr(PrevChangeValue)
        Else
            oldVal = "(n/a)"
        End If
        wsLog.Cells(r, 2).Value = Now
        wsLog.Cells(r, 2).NumberFormat = "dd-mmm-yy hh:nn:ss"
        wsLog.Cells(r, 3).Value = Sh.Name
        wsLog.Cells(r, 4).Value = c.Address(False, False)
        wsLog.Cells(r, 5).Value = oldVal
        wsLog.Cells(r, 6).Value = CStr(c.Value)
        wsLog.Cells(r, 7).Value = Application.UserName
        r = r + 1
    Next c
    PrevChangeAddress = ""
End Sub
''' % names_arr

MOD = MOD_BASE + _build_logchange_code()


def _build_slicer_module():
    """Generate a Table-bound Department slicer for every tracker dashboard that has one,
    from the same register list the workbook itself is built from (keeps sheet/table names
    in lock-step with the Python generator instead of hand-typing 24 entries in VBA)."""
    dash_names, reg_names, tbl_names = [], [], []
    for spec in HD.REGISTERS:
        if "Department" not in spec["headers"]:
            continue
        dash_names.append("Dash \xb7 " + spec["sheet"])
        reg_names.append(spec["sheet"])
        tbl_names.append("t_" + spec["key"])

    def vba_arr(items):
        return "Array(" + ", ".join('"%s"' % s.replace('"', '""') for s in items) + ")"

    return '''Attribute VB_Name = "modSlicers"
Option Explicit

'==========================================================
' PER-TRACKER SLICERS
'   Adds a real, Table-bound Department slicer to every tracker
'   dashboard (skips the couple of registers with no Department
'   column). Safe to re-run: removes any prior slicer of the same
'   name first. Sheets are briefly unprotected while the slicer is
'   inserted, then re-protected exactly as ProtectAllSheets does.
'==========================================================
Public Sub BuildTrackerSlicers()
    Dim dashNames As Variant, regNames As Variant, tblNames As Variant
    Dim i As Long
    Dim wsD As Worksheet
    Dim tbl As ListObject
    Dim sc As SlicerCache
    Dim built As Long

    dashNames = %s
    regNames = %s
    tblNames = %s

    Application.ScreenUpdating = False
    built = 0
    For i = LBound(dashNames) To UBound(dashNames)
        On Error Resume Next
        Set wsD = Nothing
        Set wsD = ThisWorkbook.Worksheets(CStr(dashNames(i)))
        On Error GoTo 0
        If Not wsD Is Nothing Then
            On Error Resume Next
            wsD.Unprotect Password:=""
            ' remove a same-named slicer from a previous run so this is re-runnable
            ActiveWorkbook.SlicerCaches("Slicer_" & CStr(tblNames(i)) & "_Department").Delete
            Set tbl = Nothing
            Set tbl = ThisWorkbook.Worksheets(CStr(regNames(i))).ListObjects(CStr(tblNames(i)))
            If Not tbl Is Nothing Then
                Set sc = ActiveWorkbook.SlicerCaches.Add2(tbl, "Department")
                sc.Slicers.Add SlicerDestination:=wsD, Name:="Slicer_" & CStr(tblNames(i)) & "_Department", _
                    Caption:="Department", Left:=910, Top:=55, Width:=135, Height:=190
                built = built + 1
            End If
            wsD.Protect Password:="", DrawingObjects:=False, Contents:=True, Scenarios:=True, _
                UserInterfaceOnly:=True, AllowFiltering:=True, AllowSorting:=True, AllowInsertingRows:=True
            On Error GoTo 0
        End If
    Next i
    Application.ScreenUpdating = True
    MsgBox "Added " & built & " Department slicers to tracker dashboards (top-right of each). " & _
           "Click a slicer button to filter that register live - independent of the Executive filters.", _
           vbInformation, "Tracker Slicers Ready"
End Sub
''' % (vba_arr(dash_names), vba_arr(reg_names), vba_arr(tbl_names))


def _build_action_tracker_module():
    """Generate the My Actions consolidated tracker + overdue-alert macros, with the 8
    registers' column letters computed from HD.REGISTERS (never hand-typed) so they can
    never drift out of sync with the Python-side register layout."""
    def colletter(spec, header):
        return xl_col_to_name(spec["headers"].index(header))
    reg_names, labels, id_c, dept_c, desc_c, owner_c, due_c, status_c = [],[],[],[],[],[],[],[]
    for spec_key,label,ownerhdr,deschdr,duehdr in ACTION_TRACKER_SPECS:
        spec = next(s for s in HD.REGISTERS if s["key"]==spec_key)
        reg_names.append(spec["sheet"]); labels.append(label)
        id_c.append(colletter(spec, spec["headers"][1]))
        dept_c.append(colletter(spec, "Department"))
        desc_c.append(colletter(spec, deschdr))
        owner_c.append(colletter(spec, ownerhdr))
        due_c.append(colletter(spec, duehdr))
        status_c.append(colletter(spec, "Status"))

    def vba_arr(items):
        return "Array(" + ", ".join('"%s"' % s.replace('"', '""') for s in items) + ")"

    return '''Attribute VB_Name = "modActions"
Option Explicit

'==========================================================
' MY ACTIONS - consolidated overdue-item tracker
'   Scans the 8 registers that carry a due-date + owner field
'   and lists every row currently flagged Status="Overdue",
'   with days-overdue computed from its due-date field. Safe
'   to re-run: rebuilds the sheet from scratch each time.
'==========================================================
Public Sub BuildActionTracker()
    Dim regNames As Variant, labels As Variant
    Dim idCols As Variant, deptCols As Variant, descCols As Variant
    Dim ownerCols As Variant, dueCols As Variant, statusCols As Variant
    Dim wsOut As Worksheet, ws As Worksheet
    Dim i As Long, r As Long, lastRow As Long, outRow As Long
    Dim statusVal As String, dueVal As Variant, hdrF As Object

    regNames = %s
    labels = %s
    idCols = %s
    deptCols = %s
    descCols = %s
    ownerCols = %s
    dueCols = %s
    statusCols = %s

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    On Error Resume Next
    ThisWorkbook.Worksheets("My Actions").Delete
    On Error GoTo 0
    Application.DisplayAlerts = True

    Set wsOut = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
    wsOut.Name = "My Actions"
    wsOut.Tab.Color = RGB(220, 38, 38)
    wsOut.Range("B2").Value = "MY ACTIONS - consolidated overdue items across all registers"
    wsOut.Range("B2").Font.Size = 16: wsOut.Range("B2").Font.Bold = True
    wsOut.Range("B3").Value = "Click Home -> Build Action Tracker to refresh after entering new data."
    wsOut.Hyperlinks.Add Anchor:=wsOut.Range("B4"), Address:="", SubAddress:="'Home'!A1", TextToDisplay:="Home"

    Dim headers As Variant
    headers = Array("Tracker", "ID", "Department", "Description", "Assigned To", "Due Date", "Days Overdue", "Status")
    For i = LBound(headers) To UBound(headers)
        wsOut.Cells(5, 2 + i).Value = headers(i)
        wsOut.Cells(5, 2 + i).Font.Bold = True
    Next i

    outRow = 6
    For i = LBound(regNames) To UBound(regNames)
        Set ws = Nothing
        On Error Resume Next
        Set ws = ThisWorkbook.Worksheets(CStr(regNames(i)))
        On Error GoTo 0
        If Not ws Is Nothing Then
            lastRow = ws.Cells(ws.Rows.Count, CStr(idCols(i))).End(xlUp).Row
            For r = 4 To lastRow
                statusVal = CStr(ws.Range(CStr(statusCols(i)) & r).Value)
                If statusVal = "Overdue" Then
                    wsOut.Cells(outRow, 2).Value = labels(i)
                    wsOut.Cells(outRow, 3).Value = ws.Range(CStr(idCols(i)) & r).Value
                    wsOut.Cells(outRow, 4).Value = ws.Range(CStr(deptCols(i)) & r).Value
                    wsOut.Cells(outRow, 5).Value = ws.Range(CStr(descCols(i)) & r).Value
                    wsOut.Cells(outRow, 6).Value = ws.Range(CStr(ownerCols(i)) & r).Value
                    dueVal = ws.Range(CStr(dueCols(i)) & r).Value
                    wsOut.Cells(outRow, 7).Value = dueVal
                    wsOut.Cells(outRow, 7).NumberFormat = "dd-mmm-yy"
                    On Error Resume Next
                    wsOut.Cells(outRow, 8).Value = Int(Date - CDate(dueVal))
                    On Error GoTo 0
                    wsOut.Cells(outRow, 9).Value = statusVal
                    outRow = outRow + 1
                End If
            Next r
        End If
    Next i

    If outRow > 6 Then
        wsOut.Range("B5:I" & (outRow - 1)).Borders.LineStyle = xlContinuous
        wsOut.Range("B5:I" & (outRow - 1)).Borders.Color = RGB(216, 225, 235)
        wsOut.Range("H6:H" & (outRow - 1)).FormatConditions.AddColorScale ColorScaleType:=3
    End If
    wsOut.Columns("B:I").AutoFit
    wsOut.Range("B3").Offset(0, 3).Value = "Last built: " & Format(Now, "dd-mmm-yyyy hh:nn") & _
        "   ·   " & (outRow - 6) & " overdue item(s)"
    Application.ScreenUpdating = True
    MsgBox "Action Tracker rebuilt: " & (outRow - 6) & " overdue items across all registers.", _
           vbInformation, "Action Tracker Ready"
End Sub

'==========================================================
' OVERDUE ALERT EMAILS (Outlook)
'   Groups My Actions by owner and drafts one Outlook email
'   per owner listing their overdue items. Drafts only - opens
'   each email for review (.Display), never auto-sends, since
'   owner names are not mapped to email addresses here.
'==========================================================
Public Sub SendOverdueAlerts()
    Dim wsA As Worksheet, lastRow As Long, r As Long
    Dim ownerDict As Object, ky As Variant
    Dim olApp As Object, olMail As Object
    Dim ownerName As String, ln As String, cnt As Long

    On Error Resume Next
    Set wsA = ThisWorkbook.Worksheets("My Actions")
    On Error GoTo 0
    If wsA Is Nothing Then
        MsgBox "Run 'Build Action Tracker' first (Home page).", vbExclamation, "No Action Tracker"
        Exit Sub
    End If

    lastRow = wsA.Cells(wsA.Rows.Count, "C").End(xlUp).Row
    If lastRow < 6 Then
        MsgBox "No overdue items found.", vbInformation, "Overdue Alerts"
        Exit Sub
    End If

    Set ownerDict = CreateObject("Scripting.Dictionary")
    For r = 6 To lastRow
        ownerName = Trim(CStr(wsA.Cells(r, 6).Value))
        If ownerName = "" Then ownerName = "Unassigned"
        ln = "  - [" & wsA.Cells(r, 2).Value & "] " & wsA.Cells(r, 3).Value & " (" & _
             wsA.Cells(r, 4).Value & "): " & wsA.Cells(r, 5).Value & " - due " & _
             Format(wsA.Cells(r, 7).Value, "dd-mmm-yyyy") & " (" & wsA.Cells(r, 8).Value & " days overdue)" & vbCrLf
        If ownerDict.Exists(ownerName) Then
            ownerDict(ownerName) = ownerDict(ownerName) & ln
        Else
            ownerDict.Add ownerName, ln
        End If
    Next r

    On Error Resume Next
    Set olApp = CreateObject("Outlook.Application")
    On Error GoTo 0
    If olApp Is Nothing Then
        MsgBox "Microsoft Outlook is not available on this machine - cannot draft alert emails.", _
               vbExclamation, "Outlook Not Found"
        Exit Sub
    End If

    cnt = 0
    For Each ky In ownerDict.Keys
        Set olMail = olApp.CreateItem(0)
        With olMail
            .Subject = "EHS Action Items Overdue - " & CStr(ky)
            .Body = "Hi " & CStr(ky) & "," & vbCrLf & vbCrLf & _
                    "The following EHS action items assigned to you are overdue:" & vbCrLf & vbCrLf & _
                    ownerDict(ky) & vbCrLf & _
                    "Please update the relevant register or contact the EHS team." & vbCrLf & vbCrLf & _
                    "This is an automated draft from the RCPL Integrated EHS Management System - " & _
                    "set the To: address before sending."
            .Display
        End With
        cnt = cnt + 1
    Next ky

    MsgBox "Drafted " & cnt & " overdue-alert email(s) in Outlook, one per owner. Review, add a " & _
           "recipient and send manually.", vbInformation, "Overdue Alerts Drafted"
End Sub
''' % (vba_arr(reg_names), vba_arr(labels), vba_arr(id_c), vba_arr(dept_c), vba_arr(desc_c),
       vba_arr(owner_c), vba_arr(due_c), vba_arr(status_c))


def modules():
    return [
        {"name":"ThisWorkbook","type":"document","code":THISWORKBOOK},
        {"name":"modEHS","type":"standard","code":MOD},
        {"name":"modSlicers","type":"standard","code":_build_slicer_module()},
        {"name":"modActions","type":"standard","code":_build_action_tracker_module()},
    ]
