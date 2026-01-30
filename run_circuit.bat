@echo off
REM ================================================================
REM Circuit Diagram Generator - Quick Run Script
REM ================================================================

REM Configuration Variables - Edit these to change input/output files
SET CHIPS_FILE=I-O/chips.csv
SET CONNECTIONS_FILE=I-O/connections.csv
SET DATASHEETS_FILE=I-O/chip_datasheets.csv
SET OUTPUT_FILE=I-O/outputs/circuit_diagram.svg

REM Python executable path (auto-detected)
SET PYTHON_EXE=.venv\Scripts\python.exe

REM ================================================================
REM Do not edit below this line unless you know what you're doing
REM ================================================================

echo ================================================================
echo Circuit Diagram Generator
echo ================================================================
echo.
echo Input Files:
echo   Chips:       %CHIPS_FILE%
echo   Connections: %CONNECTIONS_FILE%
echo   Datasheets:  %DATASHEETS_FILE%
echo.
echo Output File:
echo   %OUTPUT_FILE%
echo.
echo ================================================================
echo.

REM Check if Python virtual environment exists
if not exist %PYTHON_EXE% (
    echo ERROR: Python virtual environment not found!
    echo Please ensure .venv folder exists with Python installed.
    pause
    exit /b 1
)

REM Check if input files exist
if not exist %CHIPS_FILE% (
    echo ERROR: Chips file not found: %CHIPS_FILE%
    pause
    exit /b 1
)

if not exist %CONNECTIONS_FILE% (
    echo ERROR: Connections file not found: %CONNECTIONS_FILE%
    pause
    exit /b 1
)

if not exist %DATASHEETS_FILE% (
    echo ERROR: Datasheets file not found: %DATASHEETS_FILE%
    pause
    exit /b 1
)

REM Run the circuit generator
echo Running circuit generator...
echo.

%PYTHON_EXE% -c "from circuit_generator import SVGCircuitGenerator; g = SVGCircuitGenerator('%CHIPS_FILE%', '%CONNECTIONS_FILE%', '%DATASHEETS_FILE%', '%OUTPUT_FILE%'); g.generate_circuit()"

REM Check if generation was successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo SUCCESS! Circuit diagram generated successfully.
    echo Output saved to: %OUTPUT_FILE%
    echo ================================================================
    
    REM Convert SVG to PNG
    echo.
    echo Converting SVG to PNG...
    %PYTHON_EXE% svg_to_png.py "%OUTPUT_FILE%" >nul 2>&1
    
    if %ERRORLEVEL% EQU 0 (
        echo PNG conversion successful!
        echo PNG saved to: I-O/outputs/circuit_diagram.png
    ) else (
        echo.
        echo Note: PNG conversion not available.
        echo SVG file is ready to use: %OUTPUT_FILE%
        echo.
        echo To enable PNG conversion, you can view the SVG directly
        echo or install GTK+ runtime for Windows from:
        echo https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
    )
) else (
    echo.
    echo ================================================================
    echo ERROR! Circuit generation failed.
    echo Please check the error messages above.
    echo ================================================================
)

echo.
exit 0
