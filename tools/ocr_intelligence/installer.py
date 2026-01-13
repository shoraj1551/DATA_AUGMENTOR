"""
Tesseract Auto-Installer
Automatically installs Tesseract OCR if not present
"""
import os
import sys
import platform
import subprocess
from pathlib import Path


class TesseractInstaller:
    """Automatic Tesseract OCR installer"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.tesseract_installed = False
        self.tesseract_path = None
    
    def check_installation(self) -> bool:
        """Check if Tesseract is already installed"""
        try:
            result = subprocess.run(
                ['tesseract', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.tesseract_installed = True
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Check common installation paths
        common_paths = self._get_common_paths()
        for path in common_paths:
            if Path(path).exists():
                self.tesseract_path = path
                self.tesseract_installed = True
                return True
        
        return False
    
    def _get_common_paths(self) -> list:
        """Get common Tesseract installation paths"""
        if self.os_type == 'Windows':
            return [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                str(Path.home() / 'AppData' / 'Local' / 'Tesseract-OCR' / 'tesseract.exe')
            ]
        elif self.os_type == 'Darwin':  # macOS
            return [
                '/usr/local/bin/tesseract',
                '/opt/homebrew/bin/tesseract'
            ]
        else:  # Linux
            return [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract'
            ]
    
    def install(self) -> dict:
        """
        Install Tesseract OCR automatically
        
        Returns:
            dict with success status and message
        """
        if self.check_installation():
            return {
                'success': True,
                'message': 'Tesseract is already installed',
                'path': self.tesseract_path
            }
        
        try:
            if self.os_type == 'Windows':
                return self._install_windows()
            elif self.os_type == 'Darwin':
                return self._install_macos()
            else:
                return self._install_linux()
        except Exception as e:
            return {
                'success': False,
                'message': f'Installation failed: {str(e)}',
                'manual_instructions': self._get_manual_instructions()
            }
    
    def _install_windows(self) -> dict:
        """Install Tesseract on Windows using winget or chocolatey"""
        # Try winget first (Windows 10+)
        try:
            result = subprocess.run(
                ['winget', 'install', '--id=UB-Mannheim.TesseractOCR', '--silent'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Tesseract installed successfully via winget'
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try chocolatey
        try:
            result = subprocess.run(
                ['choco', 'install', 'tesseract', '-y'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Tesseract installed successfully via Chocolatey'
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return {
            'success': False,
            'message': 'Automatic installation not available',
            'manual_instructions': self._get_manual_instructions()
        }
    
    def _install_macos(self) -> dict:
        """Install Tesseract on macOS using Homebrew"""
        try:
            result = subprocess.run(
                ['brew', 'install', 'tesseract'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Tesseract installed successfully via Homebrew'
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return {
            'success': False,
            'message': 'Homebrew not found',
            'manual_instructions': self._get_manual_instructions()
        }
    
    def _install_linux(self) -> dict:
        """Install Tesseract on Linux using apt/yum"""
        # Try apt (Debian/Ubuntu)
        try:
            subprocess.run(['sudo', 'apt-get', 'update'], timeout=60)
            result = subprocess.run(
                ['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Tesseract installed successfully via apt'
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try yum (RedHat/CentOS)
        try:
            result = subprocess.run(
                ['sudo', 'yum', 'install', '-y', 'tesseract'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Tesseract installed successfully via yum'
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return {
            'success': False,
            'message': 'Package manager not found',
            'manual_instructions': self._get_manual_instructions()
        }
    
    def _get_manual_instructions(self) -> str:
        """Get manual installation instructions"""
        if self.os_type == 'Windows':
            return """
**Windows Installation:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Restart the application
"""
        elif self.os_type == 'Darwin':
            return """
**macOS Installation:**
1. Install Homebrew: https://brew.sh
2. Run: `brew install tesseract`
3. Restart the application
"""
        else:
            return """
**Linux Installation:**
Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
RedHat/CentOS: `sudo yum install tesseract`
"""
