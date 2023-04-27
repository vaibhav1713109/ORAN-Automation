@echo off
FOR /F "tokens=* USEBACKQ" %%F IN (`c:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -Command "&{Get-ItemPropertyValue -Path 'Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Keysight\Open RAN Studio' -Name 'InstallLocation'}"`) DO (
SET ORSDIR=%%F
)
if "%ORSDIR%"=="" (
	SET ORSDIR=C:\Program Files\Keysight\Open RAN Studio\
)
echo ORSDIR is %ORSDIR%

if "%1"=="" (
	SET DESTDIR=.
) else (
	SET DESTDIR=%1
)

copy "%ORSDIR%Open RAN Studio API.dll" "%DESTDIR%"
copy "%ORSDIR%xRAN Configuration.dll" "%DESTDIR%"
copy "%ORSDIR%KalApi.dll" "%DESTDIR%"
copy "%ORSDIR%KsfCore-0.dll" "%DESTDIR%"
copy "%ORSDIR%PwMatFile.dll" "%DESTDIR%"
copy "%ORSDIR%MatlabWrapper.dll" "%DESTDIR%"
copy "%ORSDIR%Signal Studio Wrapper.dll" "%DESTDIR%"
copy "%ORSDIR%5G_NR.dll" "%DESTDIR%"
copy "%ORSDIR%eCPRI.dll" "%DESTDIR%"
copy "%ORSDIR%Errors Logging Tracing.dll" "%DESTDIR%"
copy "%ORSDIR%Keysight.Ccl.Wsl.dll" "%DESTDIR%"
copy "%ORSDIR%Lomont.dll" "%DESTDIR%"
copy "%ORSDIR%Pcap.dll" "%DESTDIR%"
copy "%ORSDIR%xRAN CUS-Plane.dll" "%DESTDIR%"
copy "%ORSDIR%xRAN M-Plane.dll" "%DESTDIR%"
copy "%ORSDIR%xRAN Transport.dll" "%DESTDIR%"
copy "%ORSDIR%netstandard.dll" "%DESTDIR%"
copy "%ORSDIR%System.*.dll" "%DESTDIR%"
copy "%ORSDIR%*.xml" "%DESTDIR%"
copy "%ORSDIR%example.api.app.config" "%DESTDIR%"

echo "Dependencies have been copied, please be sure to update your app.config (see API online help or example.api.app.config)"
