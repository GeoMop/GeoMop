# GeoMop nsi build script for Windows x86 platform
# 
#--------------------------------

# Define directories.
!define GIT_DIR ".\"
!define SRC_DIR "${GIT_DIR}\src"
!define BUILD_DIR "${GIT_DIR}\build\win_x86"

!define PYTHON_MAJOR   "3"
!define PYTHON_MINOR   "4"

# THe following are derived from the above.
!define PYTHON_VERS    "${PYTHON_MAJOR}.${PYTHON_MINOR}"
!define PYTHON_HK      "Software\Python\PythonCore\${PYTHON_VERS}\InstallPath"
!define PYTHON_HK_64   "Software\Wow6432Node\Python\PythonCore\${PYTHON_VERS}\InstallPath"


# Include the tools we use.
!include MUI2.nsh
!include LogicLib.nsh


Name "GeoMop"
Caption "GeoMop Setup"
InstallDir "$PROGRAMFILES\GeoMop"
OutFile "${GIT_DIR}\dist\geomop_x86.exe"

# Registry key to check for directory (so if you install again, it will 
# overwrite the old one automatically)
InstallDirRegKey HKLM "Software\GeoMop" "Install_Dir"

# Request application privileges for Windows Vista and newer
RequestExecutionLevel admin

#--------------------------------

# Define the different pages.
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${GIT_DIR}\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

# Other settings.
!insertmacro MUI_LANGUAGE "English"

#--------------------------------
# Init

Var PYTHON_EXE
Var PYTHON_SCRIPTS

Function .onInit

  CheckPython:
    # Check if 32b Python is installed.
    ReadRegStr $PYTHON_EXE HKCU "${PYTHON_HK}" ""

    ${If} $PYTHON_EXE == ""
        ReadRegStr $PYTHON_EXE HKLM "${PYTHON_HK}" ""
    ${Endif}

    # Install Python.
    ${If} $PYTHON_EXE == ""
      MessageBox MB_YESNO|MB_ICONQUESTION "Python ${PYTHON_VERS} 32b is not installed. Do you wish to install it?" IDYES InstallPython
                  Abort
      InstallPython:
        SetOutPath $INSTDIR\prerequisites
        File "${BUILD_DIR}\python-3.4.3.msi"
        ExecWait 'msiexec /i python-3.4.3.msi'

        # Check installation.
        Goto CheckPython
    ${Endif}

    # Set the path to the python.exe instead of directory.
    StrCpy $PYTHON_EXE "$PYTHON_EXEpython.exe"

FunctionEnd

#--------------------------------
# The stuff to install

# These are the programs that are needed by GeoMop.
Section "Runtime Environment" SecRuntime
  
  # Section is mandatory.
  SectionIn RO

  # Install virtualenv.
  SetOutPath $INSTDIR\prerequisites
  File "${BUILD_DIR}\virtualenv-13.1.2-py2.py3-none-any.whl"
  ExecWait '"$PYTHON_EXE" -m pip install "$INSTDIR\prerequisites\virtualenv-13.1.2-py2.py3-none-any.whl"'
  ExecWait '"$PYTHON_EXE" -m virtualenv "$INSTDIR\env"'

  # Copy PyQt5 and other Python packages.
  SetOutPath $INSTDIR
  File /r "${BUILD_DIR}\env"

  # Copy the common folder.
  SetOutPath $INSTDIR
  File /r "${SRC_DIR}\common"

  # Set the varible with path to python virtual environment scripts.
  StrCpy $PYTHON_SCRIPTS "$INSTDIR\env\Scripts"

SectionEnd


Section "JobsScheduler" SecJobsScheduler

  SetOutPath $INSTDIR
  File /r "${SRC_DIR}\JobsScheduler"

SectionEnd


Section /o "LayerEditor" SecLayerEditor

  SetOutPath $INSTDIR
  File /r "${SRC_DIR}\LayerEditor"

SectionEnd


Section "ModelEditor" SecModelEditor

  SetOutPath $INSTDIR
  File /r "${SRC_DIR}\ModelEditor"

SectionEnd


Section "Start Menu shortcuts" SecStartShortcuts

  CreateDirectory "$SMPROGRAMS\GeoMop"

  # Make sure this is clean and tidy.
  RMDir /r "$SMPROGRAMS\GeoMop"
  CreateDirectory "$SMPROGRAMS\GeoMop"

  # Uninstall shortcut.
  SetOutPath $INSTDIR
  CreateShortcut "$SMPROGRAMS\GeoMop\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

  IfFileExists "$INSTDIR\JobsScheduler\job_scheduler.py" 0 +3
    SetOutPath $INSTDIR\JobsScheduler
    CreateShortcut "$SMPROGRAMS\GeoMop\JobsScheduler.lnk" "$PYTHON_SCRIPTS\pythonw.exe" '"$INSTDIR\JobsScheduler\job_scheduler.py"' "$PYTHON_SCRIPTS\python.exe" 0

  IfFileExists "$INSTDIR\LayerEditor\layer_editor.py" 0 +3
    SetOutPath $INSTDIR\LayerEditor
    CreateShortcut "$SMPROGRAMS\GeoMop\LayerEditor.lnk" "$PYTHON_SCRIPTS\pythonw.exe"'"$INSTDIR\LayerEditor\layer_editor.py"' "$PYTHON_SCRIPTS\python.exe" 0

  IfFileExists "$INSTDIR\ModelEditor\model_editor.py" 0 +3
    SetOutPath $INSTDIR\ModelEditor
    CreateShortcut "$SMPROGRAMS\GeoMop\ModelEditor.lnk" "$PYTHON_SCRIPTS\pythonw.exe" '"$INSTDIR\ModelEditor\model_editor.py"' "$PYTHON_SCRIPTS\python.exe" 0

SectionEnd


Section "Desktop icons" SecDesktopIcons

  IfFileExists "$INSTDIR\JobsScheduler\job_scheduler.py" 0 +3
    SetOutPath $INSTDIR\JobsScheduler
    CreateShortCut "$DESKTOP\JobsScheduler.lnk" "$PYTHON_SCRIPTS\pythonw.exe" '"$INSTDIR\JobsScheduler\job_scheduler.py"' "$PYTHON_SCRIPTS\python.exe" 0

  IfFileExists "$INSTDIR\LayerEditor\layer_editor.py" 0 +3
    SetOutPath $INSTDIR\LayerEditor
    CreateShortCut "$DESKTOP\LayerEditor.lnk" "$PYTHON_SCRIPTS\pythonw.exe"'"$INSTDIR\LayerEditor\layer_editor.py"' "$PYTHON_SCRIPTS\python.exe" 0

  IfFileExists "$INSTDIR\ModelEditor\model_editor.py" 0 +3
    SetOutPath $INSTDIR\ModelEditor
    CreateShortCut "$DESKTOP\ModelEditor.lnk" "$PYTHON_SCRIPTS\pythonw.exe" '"$INSTDIR\ModelEditor\model_editor.py"' "$PYTHON_SCRIPTS\python.exe" 0

SectionEnd


Section -post
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\GeoMop "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "DisplayName" "GeoMop"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
SectionEnd


# Section description text.
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecRuntime} \
"The runtime environment for GeoMop - Python 3.4 with PyQt5."
!insertmacro MUI_DESCRIPTION_TEXT ${SecJobsScheduler} \
"The jobs scheduler."
!insertmacro MUI_DESCRIPTION_TEXT ${SecLayerEditor} \
"The layer editor."
!insertmacro MUI_DESCRIPTION_TEXT ${SecModelEditor} \
"The interactive editor for Flow123d configuration files."
!insertmacro MUI_DESCRIPTION_TEXT ${SecStartShortcuts} \
"This adds shortcuts to your Start Menu."
!insertmacro MUI_DESCRIPTION_TEXT ${SecDesktopIcons} \
"This creates icons on your Desktop."
!insertmacro MUI_FUNCTION_DESCRIPTION_END


# Uninstaller
Section "Uninstall"
  
  # Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop"
  DeleteRegKey HKLM SOFTWARE\GeoMop

  # Delete desktop icons.
  Delete "$DESKTOP\JobsScheduler.lnk"
  Delete "$DESKTOP\LayerEditor.lnk"
  Delete "$DESKTOP\ModelEditor.lnk"

  # Remove start menu shortcuts.
  RMDir /r "$SMPROGRAMS\GeoMop"

  # Remove GeoMop installation directory and all files within.
  RMDir /r "$INSTDIR"

SectionEnd
