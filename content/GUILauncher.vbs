Set WshShell = CreateObject("WScript.Shell")
appPath = "C:\Users\" & WshShell.ExpandEnvironmentStrings("%USERNAME%") & "\AppData\Local\BypassToolkit"
WshShell.CurrentDirectory = appPath
WshShell.Run "python BypassGUI.py", 0, False
