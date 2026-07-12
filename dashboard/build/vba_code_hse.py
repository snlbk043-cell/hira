"""VBA for the Integrated EHS Management System."""
import hse_data as HD

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
'''

MOD = '''Attribute VB_Name = "modEHS"
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
        If ws.Name <> "Master Data" And ws.Name <> "Pivot Analysis" Then
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
'''


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


def modules():
    return [
        {"name":"ThisWorkbook","type":"document","code":THISWORKBOOK},
        {"name":"modEHS","type":"standard","code":MOD},
        {"name":"modSlicers","type":"standard","code":_build_slicer_module()},
    ]
