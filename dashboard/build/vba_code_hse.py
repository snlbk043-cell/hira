"""VBA for the Integrated EHS Management System."""
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
        .Range("SelMonth").Value = "All"
        .Range("SelDept").Value = "All"
    End With
    Application.CalculateFull
    MsgBox "Filters reset to 'All'.", vbInformation, "Filters Reset"
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

def modules():
    return [
        {"name":"ThisWorkbook","type":"document","code":THISWORKBOOK},
        {"name":"modEHS","type":"standard","code":MOD},
    ]
