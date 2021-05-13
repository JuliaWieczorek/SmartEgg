!define PRODUCT_NAME "Smart Egg 3D"
!define PRODUCT_VERSION "1.1"
!define PY_VERSION "2.7.13"
!define PY_MAJOR_VERSION "2.7"
!define BITNESS "32"
!define ARCH_TAG ""
!define INSTALLER_NAME "Smart_Egg_3D_1.1.exe"
!define PRODUCT_ICON "egg.ico"
 
SetCompressor lzma

RequestExecutionLevel admin

; Modern UI installer stuff 
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

; UI pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${INSTALLER_NAME}"
InstallDir "$PROGRAMFILES${BITNESS}\${PRODUCT_NAME}"
ShowInstDetails show

Section -SETTINGS
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
SectionEnd

Section "PyLauncher" sec_pylauncher
    ; Check for the existence of the pyw command, skip installing if it exists
    nsExec::Exec 'where pyw'
    Pop $0
    IntCmp $0 0 SkipPylauncher
    ; Extract the py/pyw launcher msi and run it.
    File "launchwin${ARCH_TAG}.msi"
    ExecWait 'msiexec /i "$INSTDIR\launchwin${ARCH_TAG}.msi" /qb ALLUSERS=1'
    Delete "$INSTDIR\launchwin${ARCH_TAG}.msi"
    SkipPylauncher:
SectionEnd

Section "Python ${PY_VERSION}" sec_py

  DetailPrint "Installing Python ${PY_MAJOR_VERSION}, ${BITNESS} bit"
    File "python-2.7.13.msi"
    ExecWait 'msiexec /i "$INSTDIR\python-2.7.13.msi" \
            /qb ALLUSERS=1 TARGETDIR="$COMMONFILES${BITNESS}\Python\${PY_MAJOR_VERSION}"'
  Delete "$INSTDIR\python-2.7.13.msi"
SectionEnd


Section "!${PRODUCT_NAME}" sec_app
  SetRegView 32
  SectionIn RO
  SetShellVarContext all
  File ${PRODUCT_ICON}
  SetOutPath "$INSTDIR\pkgs"
  File /r "pkgs\*.*"
  SetOutPath "$INSTDIR"

  ; Install files
    SetOutPath "$INSTDIR"
      File "egg.ico"
      File "Smart_Egg_3D.launch.pyw"
  
  ; Install directories
  
  ; Install shortcuts
  ; The output path becomes the working directory for shortcuts
  SetOutPath "%HOMEDRIVE%\%HOMEPATH%"
    CreateShortCut "$SMPROGRAMS\Smart Egg 3D.lnk" "pyw" \
      '"$INSTDIR\Smart_Egg_3D.launch.pyw"' "$INSTDIR\egg.ico"
  SetOutPath "$INSTDIR"

  
  ; Byte-compile Python files.
  DetailPrint "Byte-compiling Python modules..."
  nsExec::ExecToLog 'py -2.7-32 -m compileall -q "$INSTDIR\pkgs"'
  WriteUninstaller $INSTDIR\uninstall.exe
  ; Add ourselves to Add/remove programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayIcon" "$INSTDIR\${PRODUCT_ICON}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "Publisher" "Jacek Lewandowski(jack.lewandowski@gmail.com)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoRepair" 1

  ; Check if we need to reboot
  IfRebootFlag 0 noreboot
    MessageBox MB_YESNO "A reboot is required to finish the installation. Do you wish to reboot now?" \
                /SD IDNO IDNO noreboot
      Reboot
  noreboot:
SectionEnd

Section "Uninstall"
  SetRegView 32
  SetShellVarContext all
  Delete $INSTDIR\uninstall.exe
  Delete "$INSTDIR\${PRODUCT_ICON}"
  RMDir /r "$INSTDIR\pkgs"

  ; Remove ourselves from %PATH%

  ; Uninstall files
    Delete "$INSTDIR\egg.ico"
    Delete "$INSTDIR\Smart_Egg_3D.launch.pyw"
  ; Uninstall directories

  ; Uninstall shortcuts
      Delete "$SMPROGRAMS\Smart Egg 3D.lnk"
  RMDir $INSTDIR
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
SectionEnd




; Functions

Function .onMouseOverSection
    ; Find which section the mouse is over, and set the corresponding description.
    FindWindow $R0 "#32770" "" $HWNDPARENT
    GetDlgItem $R0 $R0 1043 ; description item (must be added to the UI)

    StrCmp $0 ${sec_py} 0 +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:The Python interpreter. \
            This is required for ${PRODUCT_NAME} to run."

    StrCmp $0 ${sec_app} "" +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:${PRODUCT_NAME}"
    


    StrCmp $0 ${sec_app} "" +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:The Python launcher. \
          This is required for ${PRODUCT_NAME} to run."
FunctionEnd