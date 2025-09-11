import os
import shutil
from pathlib import Path
from typing import Optional

base_path = os.path.dirname(os.path.realpath(__file__))


class UpdaterError(Exception):
    """Custom exception for updater operations."""
    pass


class WindowsUpdater:
    """Handles Windows updater file operations for ComfyUI."""
    
    EXPECTED_BAT_PREFIX = b"..\\python_embeded\\python.exe .\\update.py"
    OLD_CONTENT = b'..\\python_embeded\\python.exe .\\update.py ..\\ComfyUI\\'
    NEW_CONTENT = b'call update_comfyui.bat nopause'
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.top_path = self.base_path.parent
        
        self.source_updater = self.base_path / ".ci" / "update_windows" / "update.py"
        self.source_bat = self.base_path / ".ci" / "update_windows" / "update_comfyui.bat"
        
        self.dest_updater = self.top_path / "update" / "update.py"
        self.dest_bat = self.top_path / "update" / "update_comfyui.bat"
        self.dest_bat_deps = self.top_path / "update" / "update_comfyui_and_python_dependencies.bat"
    
    def _validate_paths(self) -> None:
        """Validate that source files exist."""
        if not self.source_updater.exists():
            raise UpdaterError(f"Source updater file not found: {self.source_updater}")
        if not self.source_bat.exists():
            raise UpdaterError(f"Source batch file not found: {self.source_bat}")
    
    def _read_file_content(self, file_path: Path) -> Optional[bytes]:
        """Safely read file content, return None if file doesn't exist or can't be read."""
        try:
            return file_path.read_bytes()
        except (FileNotFoundError, PermissionError, OSError):
            return None
    
    def _write_file_content(self, file_path: Path, content: bytes) -> bool:
        """Safely write file content, return True if successful."""
        try:
            file_path.write_bytes(content)
            return True
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not write to {file_path}: {e}")
            return False
    
    def _should_update(self) -> bool:
        """Check if the destination bat file needs updating."""
        content = self._read_file_content(self.dest_bat)
        if content is None:
            return False
        return content.startswith(self.EXPECTED_BAT_PREFIX)
    
    def _update_dependencies_file(self) -> None:
        """Update the dependencies batch file with new content."""
        content = self._read_file_content(self.dest_bat_deps)
        if content is None:
            return
        
        updated_content = content.replace(self.OLD_CONTENT, self.NEW_CONTENT)
        self._write_file_content(self.dest_bat_deps, updated_content)
    
    def _copy_files(self) -> None:
        """Copy source files to destination."""
        try:
            shutil.copy2(self.source_updater, self.dest_updater)
            shutil.copy2(self.source_bat, self.dest_bat)
        except (FileNotFoundError, PermissionError, OSError) as e:
            raise UpdaterError(f"Failed to copy files: {e}")
    
    def update(self) -> bool:
        """Perform the update operation."""
        try:
            self._validate_paths()
            
            if not self._should_update():
                return False
            
            self._copy_files()
            self._update_dependencies_file()
            
            print("Updated the windows standalone package updater.")
            return True
            
        except UpdaterError as e:
            print(f"Update failed: {e}")
            return False


def update_windows_updater() -> bool:
    """Update Windows updater files for ComfyUI standalone package.
    
    Returns:
        bool: True if update was successful, False otherwise.
    """
    updater = WindowsUpdater(base_path)
    return updater.update()
