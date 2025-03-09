from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class InterverseExtension(ABC):
    """Base interface for all Interverse extensions"""
    
    def __init__(self):
        self.sdk = None
        self.initialized = False
        self.config = {}
    
    @abstractmethod
    def initialize(self, sdk_instance) -> bool:
        """
        Initialize the extension with SDK instance
        
        Args:
            sdk_instance: Interverse SDK instance
            
        Returns:
            bool: True if initialization was successful
        """
        self.sdk = sdk_instance
        return True
    
    @abstractmethod
    def get_extension_info(self) -> Dict[str, Any]:
        """
        Return extension metadata
        
        Returns:
            Dict containing extension information
        """
        pass
    
    @property
    @abstractmethod
    def extension_id(self) -> str:
        """
        Unique identifier for the extension
        
        Returns:
            String identifier
        """
        pass
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the extension with custom settings
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if configuration was successful
        """
        self.config.update(config)
        return True
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current extension configuration
        
        Returns:
            Dict containing configuration
        """
        return self.config
    
    def validate_requirements(self) -> Dict[str, bool]:
        """
        Check if all requirements for the extension are met
        
        Returns:
            Dict of requirement names and their status
        """
        return {"base": True}
    
    def cleanup(self) -> bool:
        """
        Clean up resources when extension is disabled
        
        Returns:
            bool: True if cleanup was successful
        """
        self.initialized = False
        return True


class ExtensionRegistry:
    """Registry for managing extensions"""
    
    def __init__(self, sdk):
        self.sdk = sdk
        self.extensions = {}
        self.enabled_extensions = set()
    
    def register_extension(self, extension_class) -> bool:
        """
        Register an extension class
        
        Args:
            extension_class: Extension class to register
            
        Returns:
            bool: True if registration was successful
        """
        try:
            # Create an instance to get the ID
            temp_instance = extension_class()
            extension_id = temp_instance.extension_id
            
            if extension_id in self.extensions:
                return False
                
            self.extensions[extension_id] = extension_class
            return True
            
        except Exception as e:
            self.sdk.logger.error(f"Extension registration error: {e}")
            return False
    
    def enable_extension(self, extension_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[InterverseExtension]:
        """
        Enable and initialize an extension
        
        Args:
            extension_id: ID of the extension to enable
            config: Optional configuration for the extension
            
        Returns:
            Extension instance if successful, None otherwise
        """
        if extension_id not in self.extensions:
            self.sdk.logger.error(f"Extension not found: {extension_id}")
            return None
            
        if extension_id in self.enabled_extensions:
            # Already enabled, return the existing instance
            return self.get_extension(extension_id)
            
        try:
            # Create instance
            extension_class = self.extensions[extension_id]
            extension = extension_class()
            
            # Initialize with SDK
            if not extension.initialize(self.sdk):
                self.sdk.logger.error(f"Failed to initialize extension: {extension_id}")
                return None
                
            # Configure if config provided
            if config:
                extension.configure(config)
                
            # Add to enabled extensions
            self.enabled_extensions.add(extension_id)
            
            # Store instance
            self.extensions[extension_id] = extension
            
            return extension
            
        except Exception as e:
            self.sdk.logger.error(f"Error enabling extension {extension_id}: {e}")
            return None
    
    def disable_extension(self, extension_id: str) -> bool:
        """
        Disable an extension
        
        Args:
            extension_id: ID of the extension to disable
            
        Returns:
            bool: True if disabling was successful
        """
        if extension_id not in self.enabled_extensions:
            return False
            
        try:
            extension = self.get_extension(extension_id)
            if extension:
                extension.cleanup()
                
            self.enabled_extensions.remove(extension_id)
            return True
            
        except Exception as e:
            self.sdk.logger.error(f"Error disabling extension {extension_id}: {e}")
            return False
    
    def get_extension(self, extension_id: str) -> Optional[InterverseExtension]:
        """
        Get an enabled extension instance
        
        Args:
            extension_id: ID of the extension
            
        Returns:
            Extension instance if enabled, None otherwise
        """
        if extension_id not in self.enabled_extensions:
            return None
            
        return self.extensions.get(extension_id)
    
    def get_all_extensions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered extensions
        
        Returns:
            Dict mapping extension IDs to their info
        """
        result = {}
        
        for ext_id, ext in self.extensions.items():
            if ext_id in self.enabled_extensions:
                # For enabled extensions, use the instance
                if isinstance(ext, InterverseExtension):
                    info = ext.get_extension_info()
                    info["enabled"] = True
                    result[ext_id] = info
            else:
                # For disabled extensions, create temporary instance
                try:
                    if not isinstance(ext, InterverseExtension):
                        temp = ext()
                        info = temp.get_extension_info()
                        info["enabled"] = False
                        result[ext_id] = info
                except Exception:
                    pass
                    
        return result
    
    def cleanup_all(self) -> None:
        """Clean up all enabled extensions"""
        for ext_id in list(self.enabled_extensions):
            self.disable_extension(ext_id)