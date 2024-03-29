# GeoMop nsi build script for Windows x86_64 platform
# 
#--------------------------------

# Unicode target
Unicode True

# Maximum compression.
SetCompressor /SOLID lzma


# installation only for current user
!define MULTIUSER_EXECUTIONLEVEL Standard
!define MULTIUSER_INSTALLMODE_INSTDIR "GeoMop"
!include MultiUser.nsh

# Define directories.
!define GIT_DIR "..\.."
!define SRC_DIR "${GIT_DIR}\src"
!define BUILD_DIR "${GIT_DIR}\build\win_x86"
!define DATA_DIR "${GIT_DIR}\data"

!define PYTHON_MAJOR   "3"
!define PYTHON_MINOR   "9"

# The following are derived from the above.
!define PYTHON_VERS    "${PYTHON_MAJOR}.${PYTHON_MINOR}"
!define PYTHON_HK      "Software\Python\PythonCore\${PYTHON_VERS}\InstallPath"
!define PYTHON_HK_64   "Software\Wow6432Node\Python\PythonCore\${PYTHON_VERS}\InstallPath"

!define FLOW_VER "3.9.0"

# Include the tools we use.
!include MUI2.nsh
!include LogicLib.nsh


# Read version information from file.
#!searchparse /file "${GIT_DIR}\VERSION" '' VERSION ''

Name "GeoMop ${VERSION}"
Caption "GeoMop ${VERSION} Setup"
#InstallDir "$PROGRAMFILES\GeoMop"
OutFile "${GIT_DIR}\dist\geomop_${VERSION}_x86_64.exe"

# Registry key to check for directory (so if you install again, it will 
# overwrite the old one automatically)
InstallDirRegKey HKCU "Software\GeoMop" "Install_Dir"

# Request application privileges for Windows Vista and newer
#RequestExecutionLevel admin

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

  !insertmacro MULTIUSER_INIT

  !define APP_HOME_DIR "$APPDATA\GeoMop"

  CheckPython:
    # Check if Python is installed.
    ReadRegStr $PYTHON_EXE HKCU "${PYTHON_HK}" ""

    ${If} $PYTHON_EXE == ""
        ReadRegStr $PYTHON_EXE HKLM "${PYTHON_HK}" ""
    ${Endif}

    # Install Python.
    ${If} $PYTHON_EXE == ""
      MessageBox MB_YESNO|MB_ICONQUESTION "Python ${PYTHON_VERS} 64b is not installed. Do you wish to install it?" IDYES InstallPython
                  Abort
      InstallPython:
        SetOutPath $INSTDIR\prerequisites
        File "${BUILD_DIR}\python-3.9.13-amd64.exe"
        ExecWait 'python-3.9.13-amd64.exe'

        # Check installation.
        Goto CheckPython
    ${Endif}

    # Set the path to the python.exe instead of directory.
    StrCpy $PYTHON_EXE "$PYTHON_EXEpython.exe"

FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
FunctionEnd

#--------------------------------
# The stuff to install

# These are the programs that are needed by GeoMop.
Section "Runtime Environment" SecRuntime
  
  # Section is mandatory.
  SectionIn RO

  # Clean GeoMop source, env directories.
  RMDir /r "$INSTDIR\env"
  RMDir /r "$INSTDIR\gm_base"

  # Install virtualenv.
  SetOutPath $INSTDIR\prerequisites
  #File "${BUILD_DIR}\virtualenv-16.1.0-py2.py3-none-any.whl"
  #ExecWait '"$PYTHON_EXE" -m pip install "$INSTDIR\prerequisites\virtualenv-16.1.0-py2.py3-none-any.whl"'
  #ExecWait '"$PYTHON_EXE" -m virtualenv "$INSTDIR\env"'
  ExecWait '"$PYTHON_EXE" -m venv "$INSTDIR\env"'

  # Copy PyQt5 and other Python packages.
  SetOutPath $INSTDIR
  #File /r "${BUILD_DIR}\env"

  # Copy the gm_base folder.
  File /r /x *~ /x __pycache__ /x pylintrc /x *.pyc "${SRC_DIR}\gm_base"

  # Copy LICENSE, CHANGELOG, VERSION.
  File "${GIT_DIR}\version.yml"
  File "${GIT_DIR}\changes.md"
  File "${GIT_DIR}\LICENSE"

  # Copy documentation
  #SetOutPath $INSTDIR\doc
  #File "${BUILD_DIR}\Geomop 1.1.0 reference guide.pdf"

  # Set the varible with path to python virtual environment scripts.
  StrCpy $PYTHON_SCRIPTS "$INSTDIR\env\Scripts"

  # Install python packages.
  ExecWait '"$PYTHON_SCRIPTS\python.exe" -m pip install --upgrade pip'
  ExecWait '"$PYTHON_SCRIPTS\python.exe" -m pip install Markdown PyYAML PyQt5 PyQtWebEngine QScintilla numpy scipy pyshp ruamel.yaml psutil pyDes bgem'

  # Install gmsh.
  #SetOutPath $INSTDIR
  #File /r "${BUILD_DIR}\gmsh"

  # Install intersections.
  #SetOutPath $INSTDIR
  #File /r "${GIT_DIR}\submodules\intersections"

  # Install yaml_converter.
  SetOutPath $INSTDIR
  File /r "${GIT_DIR}\submodules\yaml_converter"

  # Create directories with samples.
  CreateDirectory "$INSTDIR\sample"
  CreateDirectory "$INSTDIR\sample\ModelEditor"
  CreateDirectory "$INSTDIR\sample\ModelEditor\ConFiles"
  SetOutPath "$INSTDIR\sample\ModelEditor\ConFiles"
  File /r /x *~ "${GIT_DIR}\sample\ModelEditor\ConFiles\*"
  CreateDirectory "$INSTDIR\sample\ModelEditor\YamlFiles"
  SetOutPath "$INSTDIR\sample\ModelEditor\YamlFiles"
  # Copy selected YAML samples.
  File "${GIT_DIR}\sample\ModelEditor\YamlFiles\flow_21d.yaml"
  File "${GIT_DIR}\sample\ModelEditor\YamlFiles\flow_time_dep.yaml"
  File "${GIT_DIR}\sample\ModelEditor\YamlFiles\flow_trans_explicit.yaml"
  File "${GIT_DIR}\sample\ModelEditor\YamlFiles\flow_vtk.yaml"
  File "${GIT_DIR}\sample\ModelEditor\YamlFiles\flow_vtk_source.yaml"

  # Copy the DLLs.
  #SetOutPath "$WINDIR\System32\"
  #File /r "${BUILD_DIR}\dll\"

SectionEnd


# Flow123d with support for GeoMop.
Section "Flow123d" SecFlow

  # Section is mandatory.
  SectionIn RO

  #RMDir /r "$INSTDIR\flow123d"
  #SetOutPath $INSTDIR
  #File /r "${BUILD_DIR}\flow123d"
  #SetOutPath "$INSTDIR\flow123d"
  #ExecWait '"$INSTDIR\flow123d\install.bat"'
  SetOutPath $INSTDIR\prerequisites
  File "${BUILD_DIR}\flow123d_${FLOW_VER}_windows_install.exe"
  ExecShellWait "" '"$INSTDIR\prerequisites\flow123d_${FLOW_VER}_windows_install.exe"'

SectionEnd


Section "-JobsScheduler" SecJobsScheduler

  # Section is mandatory.
  SectionIn RO

  RMDir /r "$INSTDIR\JobsScheduler"

SectionEnd


Section "Analysis" SecAnalysis

  # Section is mandatory.
  SectionIn RO

  RMDir /r "$INSTDIR\Analysis"
  SetOutPath $INSTDIR
  File /r /x *~ /x __pycache__ /x pylintrc /x *.pyc "${SRC_DIR}\Analysis"

SectionEnd


Section "JobPanel" SecJobPanel

  # Section is mandatory.
  SectionIn RO

  RMDir /r "$INSTDIR\JobPanel"
  SetOutPath $INSTDIR
  File /r /x *~ /x __pycache__ /x pylintrc /x *.pyc /x jobs /x log "${SRC_DIR}\JobPanel"

  CreateDirectory "$INSTDIR\JobPanel\jobs"
  CreateDirectory "$INSTDIR\JobPanel\log"
  CreateDirectory "$INSTDIR\JobPanel\versions"

  # Grant jobs, lock folder permissions to Users
  #ExecWait 'icacls "$INSTDIR\JobPanel\jobs" /grant *S-1-5-32-545:(F)'
  #ExecWait 'icacls "$INSTDIR\JobPanel\lock" /grant *S-1-5-32-545:(F)'
  #ExecWait 'icacls "$INSTDIR\JobPanel\log" /grant *S-1-5-32-545:(F)'
  #ExecWait 'icacls "$INSTDIR\JobPanel\versions" /grant *S-1-5-32-545:(F)'

SectionEnd


Section "LayerEditor" SecLayerEditor

  # Section is mandatory.
  SectionIn RO

  RMDir /r "$INSTDIR\LayerEditor"
  SetOutPath $INSTDIR
  File /r /x *~ /x __pycache__ /x pylintrc /x *.pyc "${SRC_DIR}\LayerEditor"

SectionEnd


Section "ModelEditor" SecModelEditor

  # Section is mandatory.
  SectionIn RO

  RMDir /r "$INSTDIR\ModelEditor"
  SetOutPath $INSTDIR
  File /r /x *~ /x __pycache__ /x pylintrc /x *.pyc "${SRC_DIR}\ModelEditor"

SectionEnd


Section "-Batch files" SecBatchFiles

  CreateDirectory "$INSTDIR\bin"
  SetOutPath $INSTDIR\bin

  IfFileExists "$INSTDIR\JobPanel\job_panel.py" 0 +6
    FileOpen $0 "job_panel.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 'set "PYTHONPATH=$INSTDIR"$\r$\n'
    FileWrite $0 '"$PYTHON_SCRIPTS\python.exe" "$INSTDIR\JobPanel\job_panel.py" %*$\r$\n'
    FileClose $0

  IfFileExists "$INSTDIR\LayerEditor\layer_editor.py" 0 +6
    FileOpen $0 "layer_editor.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 'set "PYTHONPATH=$INSTDIR"$\r$\n'
    FileWrite $0 '"$PYTHON_SCRIPTS\python.exe" "$INSTDIR\LayerEditor\layer_editor.py" %*$\r$\n'
    FileClose $0

  IfFileExists "$INSTDIR\ModelEditor\model_editor.py" 0 +6
    FileOpen $0 "model_editor.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 'set "PYTHONPATH=$INSTDIR"$\r$\n'
    FileWrite $0 '"$PYTHON_SCRIPTS\python.exe" "$INSTDIR\ModelEditor\model_editor.py" %*$\r$\n'
    FileClose $0

  IfFileExists "$INSTDIR\LayerEditor\geometry.py" 0 +6
    FileOpen $0 "geometry.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 'set "PYTHONPATH=$INSTDIR"$\r$\n'
    FileWrite $0 '"$PYTHON_SCRIPTS\python.exe" "$INSTDIR\LayerEditor\geometry.py" %*$\r$\n'
    FileClose $0

  IfFileExists "$INSTDIR\gmsh\gmsh.exe" 0 +5
    FileOpen $0 "gmsh.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 '"$INSTDIR\gmsh\gmsh.exe" %*$\r$\n'
    FileClose $0

  FileOpen $0 "pythonw.bat" w
  FileWrite $0 "@echo off$\r$\n"
  FileWrite $0 'set "PYTHONPATH=$INSTDIR"$\r$\n'
  FileWrite $0 'start "" "$PYTHON_SCRIPTS\pythonw.exe" %*$\r$\n'
  FileClose $0

SectionEnd


Section "Start Menu shortcuts" SecStartShortcuts

  CreateDirectory "$SMPROGRAMS\GeoMop"

  # Make sure this is clean and tidy.
  RMDir /r "$SMPROGRAMS\GeoMop"
  CreateDirectory "$SMPROGRAMS\GeoMop"
  
  # Uninstall shortcut.
  SetOutPath $INSTDIR
  CreateShortcut "$SMPROGRAMS\GeoMop\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

  IfFileExists "$INSTDIR\JobPanel\job_panel.py" 0 +3
    SetOutPath $INSTDIR\JobPanel
    CreateShortcut "$SMPROGRAMS\GeoMop\JobPanel.lnk" "$INSTDIR\bin\pythonw.bat" '"$INSTDIR\JobPanel\job_panel.py"' "$INSTDIR\gm_base\resources\icons\ico\geomap.ico" 0

  IfFileExists "$INSTDIR\LayerEditor\layer_editor.py" 0 +3
    SetOutPath $INSTDIR\LayerEditor
    CreateShortcut "$SMPROGRAMS\GeoMop\LayerEditor.lnk" "$INSTDIR\bin\pythonw.bat" '"$INSTDIR\LayerEditor\layer_editor.py"' "$INSTDIR\gm_base\resources\icons\ico\le-geomap.ico" 0

  IfFileExists "$INSTDIR\ModelEditor\model_editor.py" 0 +3
    SetOutPath $INSTDIR\ModelEditor
    CreateShortcut "$SMPROGRAMS\GeoMop\ModelEditor.lnk" "$INSTDIR\bin\pythonw.bat" '"$INSTDIR\ModelEditor\model_editor.py"' "$INSTDIR\gm_base\resources\icons\ico\me-geomap.ico" 0

SectionEnd


Section "Desktop icons" SecDesktopIcons

  IfFileExists "$INSTDIR\JobPanel\job_panel.py" 0 +3
    SetOutPath $INSTDIR\JobPanel
    CreateShortCut "$DESKTOP\JobPanel.lnk" "$INSTDIR\bin\pythonw.bat" '"$INSTDIR\JobPanel\job_panel.py"' "$INSTDIR\gm_base\resources\icons\ico\geomap.ico" 0

  IfFileExists "$INSTDIR\LayerEditor\layer_editor.py" 0 +3
    SetOutPath $INSTDIR\LayerEditor
    CreateShortCut "$DESKTOP\LayerEditor.lnk" "$INSTDIR\bin\pythonw.bat" '"$INSTDIR\LayerEditor\layer_editor.py"' "$INSTDIR\gm_base\resources\icons\ico\le-geomap.ico" 0

  IfFileExists "$INSTDIR\ModelEditor\model_editor.py" 0 +3
    SetOutPath $INSTDIR\ModelEditor
    CreateShortCut "$DESKTOP\ModelEditor.lnk" "$INSTDIR\bin\pythonw.bat" '"$INSTDIR\ModelEditor\model_editor.py"' "$INSTDIR\gm_base\resources\icons\ico\me-geomap.ico" 0

SectionEnd


Section /o "Wipe settings" SecWipeSettings

  # Clear all configuration from APPDATA
  RMDir /r "${APP_HOME_DIR}"

SectionEnd


Section "-Default resources data" SecDefaultResourcesData

  # Section is mandatory.
  SectionIn RO

  IfFileExists "${APP_HOME_DIR}" +2 0
    CreateDirectory "${APP_HOME_DIR}"
    # fill data home to default resources data
    #SetOutPath "${APP_HOME_DIR}"
    #File /r "${DATA_DIR}/*"

SectionEnd


Section -post
 
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  WriteUninstaller "uninstall.exe"

  ; Write the installation path into the registry
  WriteRegStr HKCU SOFTWARE\GeoMop "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "DisplayName" "GeoMop"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop" "NoRepair" 1
  
SectionEnd


# Section description text.
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecRuntime} \
"The runtime environment for GeoMop - Python  with PyQt5."
!insertmacro MUI_DESCRIPTION_TEXT ${SecFlow} \
"Flow123d with support for GeoMop."
!insertmacro MUI_DESCRIPTION_TEXT ${SecJobsScheduler} \
"Remove jobs scheduler."
!insertmacro MUI_DESCRIPTION_TEXT ${SecAnalysis} \
"Module Analysis."
!insertmacro MUI_DESCRIPTION_TEXT ${SecJobPanel} \
"The job panel."
!insertmacro MUI_DESCRIPTION_TEXT ${SecLayerEditor} \
"The layer editor."
!insertmacro MUI_DESCRIPTION_TEXT ${SecModelEditor} \
"The interactive editor for Flow123d configuration files."
!insertmacro MUI_DESCRIPTION_TEXT ${SecBatchFiles} \
"This adds batch files to bin directory."
!insertmacro MUI_DESCRIPTION_TEXT ${SecStartShortcuts} \
"This adds shortcuts to your Start Menu."
!insertmacro MUI_DESCRIPTION_TEXT ${SecDesktopIcons} \
"This creates icons on your Desktop."
!insertmacro MUI_DESCRIPTION_TEXT ${SecWipeSettings} \
"Deletes all user settings. Check this option if you're experiencing issues with launching the applications."
!insertmacro MUI_DESCRIPTION_TEXT ${SecDefaultResourcesData} \
"If user data don't exist, create default resources data."
!insertmacro MUI_FUNCTION_DESCRIPTION_END


# Uninstaller
Section "Uninstall"
  
  # Remove registry keys
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GeoMop"
  DeleteRegKey HKCU SOFTWARE\GeoMop

  # Delete desktop icons.
  Delete "$DESKTOP\JobPanel.lnk"
  Delete "$DESKTOP\LayerEditor.lnk"
  Delete "$DESKTOP\ModelEditor.lnk"

  # Remove start menu shortcuts.
  RMDir /r "$SMPROGRAMS\GeoMop"

  # Uninstall Flow123d
  #ExecWait '"$INSTDIR\flow123d\uninstall.bat"'

  # Remove GeoMop installation directory and all files within.
  RMDir /r "$INSTDIR"

SectionEnd

