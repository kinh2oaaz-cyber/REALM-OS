; Inno Setup script for REALM OS.
; Build a one-click Windows installer ("REALM OS Setup.exe").
; Requires Inno Setup 6 (https://jrsoftware.org/isinfo.php) + PyInstaller output in ..\..\dist\REALM OS
;
;   ISCC.exe packaging\inno\realmos.iss
;   ; or: .\scripts\build-installer.ps1

#define AppName "REALM OS"
#define AppVersion "1.0.0"
#define AppPublisher "REALM"
#define AppExeName "REALM OS.exe"
#define AppId {{D9173050-DC4A-4A7A-9FF6-6A075BFDB384}}   ; stable GUID; change if forking

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=https://github.com
AppSupportURL=https://github.com
AppUpdatesURL=https://github.com
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
; per-user install (no admin required)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\..\dist
OutputBaseFilename={#AppName} Setup
SetupIconFile=..\..\assets\REALM OS LOGO.ico
UninstallIconName=Uninstall {#AppName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\..\LICENSE
; create uninstaller
Uninstallable=yes
; don't ship anything private
; (PyInstaller output should already exclude data; app stores data in %LOCALAPPDATA%)

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; bundle the PyInstaller one-folder output
Source: "..\..\dist\REALM OS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; logo fallback at app root
Source: "..\..\REALM OS LOGO.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\assets\REALM OS LOGO.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\REALM OS LOGO.ico"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\REALM OS LOGO.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
