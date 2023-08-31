; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Multi Channel Analyzer"
;#define MyAppVersion "0.3.0" ;Gets parsed from version.txt line
#define MyAppExeName "mca.exe"

#define RetrieveVersion(str FileName) \
  Local[0] = AddBackslash(GetEnv("TEMP")) + "version.txt", \
  Local[1] = \
    "-ExecutionPolicy Bypass -Command """ + \
    "$version = ((Get-Content '" + FileName + "'));" + \
    "Set-Content -Path '" + Local[0] + "' -Value $version;" + \
    """", \
  Exec("powershell.exe", Local[1], SourcePath, , SW_HIDE), \
  Local[2] = FileOpen(Local[0]), \
  Local[3] = FileRead(Local[2]), \
  FileClose(Local[2]), \
  DeleteFileNow(Local[0]), \
  Local[3]
#define MyAppVersion RetrieveVersion(".\\dist\\mca\\mca\\version.txt")

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{C6F8816D-B221-425C-8454-76B2C76445FD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
;AppPublisher={#MyAppPublisher}
;AppPublisherURL={#MyAppURL}
;AppSupportURL={#MyAppURL}
;AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=mca-{#MyAppVersion}-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=.\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: ".\dist\mca\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\dist\mca\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

;[Run]
;Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

