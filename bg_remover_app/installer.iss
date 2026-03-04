; installer.iss — Inno Setup 6 script for BG Remover

#ifndef AppVersion
  #define AppVersion "1.2.0"
#endif

#define AppName      "BG Remover"
#define AppPublisher "Long Weekend Labs"
#define AppURL       "https://github.com/longweekendlabs/bg-remover"
#define ExeName      "BGRemover.exe"
#define OutputBase   "BGRemover-v" + AppVersion + "-win64-Setup"

[Setup]
AppId={{E4A9C251-7B3D-4F8E-A0C2-B6D9F3E17A45}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL={#AppURL}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename={#OutputBase}
SetupIconFile=icons\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#ExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\{#ExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#ExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#ExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
