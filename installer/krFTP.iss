#define AppName "krFTP Server Manager"
#define AppVersion "0.10.0.0"
#define AppPublisher "Leon1217"
#define AppURL "https://github.com/Leon1217/KrFTP"
#define AppExeName "krFTP.exe"

[Setup]
AppId={{9FAE245A-9BFE-4C55-8CC2-9DD70C065B7C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\krFTP
DefaultGroupName=krFTP
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
InfoAfterFile=..\NOTICE.txt
OutputDir=..\dist\installer
OutputBaseFilename=krFTP-Setup-x64-0.10.0
SetupIconFile=..\resource\images\logo.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\krFTP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\krFTP Server Manager"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\krFTP Server Manager"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,krFTP Server Manager}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  if not IsWin64 then begin
    MsgBox('krFTP requires a 64-bit version of Windows. Windows 7 and 32-bit systems are not supported.', mbError, MB_OK);
    Result := False;
  end else begin
    Result := True;
  end;
end;
