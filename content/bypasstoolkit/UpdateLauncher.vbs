Set WshShell = CreateObject("WScript.Shell")
currentDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
WshShell.CurrentDirectory = currentDir
WshShell.Run "pythonw.exe updater.py", 0, False
