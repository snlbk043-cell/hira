"""VBA module source for the RCPL EHS dashboard workbook."""

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
    Sheets("Home").Range("LastRefresh").Value = Now
    Sheets("Home").Activate
    MsgBox "Welcome to the RCPL Executive EHS KPI Dashboard." & vbCrLf & _
           "Use the navigation buttons to explore each dashboard." & vbCrLf & _
           "Click REFRESH on any dashboard to recalculate all KPIs.", _
           vbInformation, "RCPL EHS Dashboard"
End Sub
'''

MOD_DASHBOARD = '''Attribute VB_Name = "modDashboard"
Option Explicit

'==========================================================
' RCPL Executive EHS KPI Dashboard - Automation Module
'==========================================================

Public Sub RefreshDashboard()
    Dim ws As Worksheet
    Application.ScreenUpdating = False
    On Error Resume Next
    ' Refresh any pivot tables / queries if present
    ThisWorkbook.RefreshAll
    ' Force a full recalculation of every dynamic KPI formula
    Application.CalculateFull
    Sheets("Home").Range("LastRefresh").Value = Now
    Application.ScreenUpdating = True
    MsgBox "Dashboard refreshed successfully." & vbCrLf & _
           "Last refresh: " & Format(Now, "dd-mmm-yyyy hh:nn"), _
           vbInformation, "Refresh Complete"
End Sub

Public Sub RefreshAllData()
    Application.ScreenUpdating = False
    On Error Resume Next
    ThisWorkbook.RefreshAll
    Application.CalculateFull
    Sheets("Home").Range("LastRefresh").Value = Now
    Application.ScreenUpdating = True
End Sub

Public Sub ResetFilters()
    On Error Resume Next
    With Sheets("Executive Dashboard")
        .Range("SelYear").Value = "All"
        .Range("SelMonth").Value = "All"
        .Range("SelDept").Value = "All"
        .Range("SelArea").Value = "All"
        .Range("SelShift").Value = "All"
    End With
    Application.CalculateFull
    MsgBox "All filters have been reset to 'All'.", vbInformation, "Filters Reset"
End Sub

Public Sub GoHome()
    Sheets("Home").Activate
    ActiveWindow.ScrollRow = 1
    ActiveWindow.ScrollColumn = 1
End Sub

Public Sub NavExecutive():   NavTo "Executive Dashboard":   End Sub
Public Sub NavIncident():    NavTo "Incident Dashboard":    End Sub
Public Sub NavInspection():  NavTo "Inspection Dashboard":  End Sub
Public Sub NavAudit():       NavTo "Audit Dashboard":       End Sub
Public Sub NavTraining():    NavTo "Training Dashboard":    End Sub
Public Sub NavPTW():         NavTo "PTW Dashboard":         End Sub
Public Sub NavStatutory():   NavTo "Statutory Dashboard":   End Sub
Public Sub NavCAPA():        NavTo "CAPA Dashboard":        End Sub
Public Sub NavDepartment():  NavTo "Department Dashboard":  End Sub

Private Sub NavTo(ByVal sheetName As String)
    On Error Resume Next
    Sheets(sheetName).Activate
    ActiveWindow.ScrollRow = 1
    ActiveWindow.ScrollColumn = 1
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
        Quality:=xlQualityStandard, IncludeDocProperties:=True, _
        IgnorePrintAreas:=False, OpenAfterPublish:=False
    MsgBox "Dashboard exported to PDF:" & vbCrLf & fName, vbInformation, "Export Complete"
End Sub

Public Sub ExportAllDashboardsPDF()
    Dim fName As String
    Dim arr As Variant
    arr = Array("Executive Dashboard", "Incident Dashboard", "Inspection Dashboard", _
                "Audit Dashboard", "Training Dashboard", "PTW Dashboard", _
                "Statutory Dashboard", "CAPA Dashboard", "Department Dashboard")
    On Error Resume Next
    fName = ThisWorkbook.Path & Application.PathSeparator & _
            "RCPL_EHS_Dashboards_" & Format(Now, "yyyymmdd") & ".pdf"
    Sheets(arr).Select
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fName, _
        Quality:=xlQualityStandard, OpenAfterPublish:=False
    Sheets("Home").Select
    MsgBox "All dashboards exported to PDF:" & vbCrLf & fName, vbInformation, "Export Complete"
End Sub
'''


def modules():
    return [
        {"name": "ThisWorkbook", "type": "document", "code": THISWORKBOOK},
        {"name": "modDashboard", "type": "standard", "code": MOD_DASHBOARD},
    ]
