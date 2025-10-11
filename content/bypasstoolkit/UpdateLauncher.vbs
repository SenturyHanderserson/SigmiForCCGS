Set WshShell = CreateObject("WScript.Shell")
currentDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
WshShell.CurrentDirectory = currentDir
' Run hidden (0 = hidden, 1 = normal, 2 = minimized)
WshShell.Run "pythonw.exe updater.py", 0, False
