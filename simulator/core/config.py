"""
Configuration management for the Physics Sailing Simulator

Provides centralized configuration with validation, defaults, and type safety.
"""

from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import yaml
from dataclasses import dataclass, field
from .exceptions import ConfigurationError
from .validators import Validator
from .logger import logger


@dataclass
class PhysicsConfig:
    """Physics simulation configuration"""
    timestep: float = 0.03  # seconds
    sub_iterations: int = 30  # Number of sub-iterations per timestep
    max_speed: float = 50.0  # m/s - maximum realistic boat speed
    max_angular_velocity: float = 10.0  # rad/s - maximum rotation rate
    
    def validate(self):
        """Validate physics configuration"""
        Validator.validate_positive(self.timestep, "timestep")
        Validator.validate_range(self.sub_iterations, 1, 100, "sub_iterations")
        Validator.validate_positive(self.max_speed, "max_speed")
        Validator.validate_positive(self.max_angular_velocity, "max_angular_velocity")


@dataclass
class ControlConfig:
    """Control system configuration"""
    rudder_max_angle: float = 10.0  # degrees
    rudder_min_angle: float = -10.0  # degrees
    heading_error_scale: float = 40.0  # degrees
    stability_factor: float = 1.0
    noise_factor: float = 2.0
    waypoint_arrival_radius: float = 5.0  # meters
    path_recalc_interval: float = 1.0  # seconds
    
    def validate(self):
        """Validate control configuration"""
        Validator.validate_range(self.rudder_max_angle, 0, 45, "rudder_max_angle")
        Validator.validate_range(self.rudder_min_angle, -45, 0, "rudder_min_angle")
        Validator.validate_positive(self.heading_error_scale, "heading_error_scale")
        Validator.validate_positive(self.stability_factor, "stability_factor")
        Validator.validate_positive(self.waypoint_arrival_radius, "waypoint_arrival_radius")


@dataclass
class NavigationConfig:
    """Navigation configuration"""
    upwind_no_go_angle: float = 45.0  # degrees
    downwind_no_go_angle: float = 30.0  # degrees
    tack_angle: float = 45.0  # degrees
    jibe_angle: float = 150.0  # degrees
    
    def validate(self):
        """Validate navigation configuration"""
        Validator.validate_range(self.upwind_no_go_angle, 0, 90, "upwind_no_go_angle")
        Validator.validate_range(self.downwind_no_go_angle, 0, 90, "downwind_no_go_angle")
        Validator.validate_range(self.tack_angle, 0, 90, "tack_angle")
        Validator.validate_range(self.jibe_angle, 90, 180, "jibe_angle")


@dataclass
class DisplayConfig:
    """Display configuration"""
    fps: int = 70
    update_interval: int = 1  # frames between updates
    show_forces: bool = True
    show_velocity: bool = True
    show_course: bool = True
    track_boat: bool = True
    
    def validate(self):
        """Validate display configuration"""
        Validator.validate_range(self.fps, 1, 120, "fps")
        Validator.validate_range(self.update_interval, 1, 100, "update_interval")


@dataclass
class SimulatorConfig:
    """Main simulator configuration"""
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    control: ControlConfig = field(default_factory=ControlConfig)
    navigation: NavigationConfig = field(default_factory=NavigationConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    
    # Paths
    data_dir: Path = field(default_factory=lambda: Path("data"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    
    def validate(self):
        """Validate all configuration"""
        self.physics.validate()
        self.control.validate()
        self.navigation.validate()
        self.display.validate()
        
        # Validate paths
        if not self.data_dir.exists():
            logger.warning(f"Data directory does not exist: {self.data_dir}")
        
        # Create log directory if needed
        if self.log_to_file:
            self.log_dir.mkdir(exist_ok=True)
        
        logger.info("Configuration validated successfully")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SimulatorConfig':
        """
        Create configuration from dictionary
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            SimulatorConfig instance
        """
        config = cls()
        
        # Update physics config
        if 'physics' in config_dict:
            for key, value in config_dict['physics'].items():
                if hasattr(config.physics, key):
                    setattr(config.physics, key, value)
        
        # Update control config
        if 'control' in config_dict:
            for key, value in config_dict['control'].items():
                if hasattr(config.control, key):
                    setattr(config.control, key, value)
        
        # Update navigation config
        if 'navigation' in config_dict:
            for key, value in config_dict['navigation'].items():
                if hasattr(config.navigation, key):
                    setattr(config.navigation, key, value)
        
        # Update display config
        if 'display' in config_dict:
            for key, value in config_dict['display'].items():
                if hasattr(config.display, key):
                    setattr(config.display, key, value)
        
        # Update top-level config
        for key in ['data_dir', 'log_dir', 'log_level', 'log_to_file', 'log_to_console']:
            if key in config_dict:
                value = config_dict[key]
                if key in ['data_dir', 'log_dir']:
                    value = Path(value)
                setattr(config, key, value)
        
        config.validate()
        return config
    
    @classmethod
    def from_yaml(cls, filepath: Union[str, Path]) -> 'SimulatorConfig':
        """
        Load configuration from YAML file
        
        Args:
            filepath: Path to YAML configuration file
            
        Returns:
            SimulatorConfig instance
            
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        path = Validator.validate_file_exists(filepath, "configuration file")
        
        try:
            with open(path, 'r') as f:
                config_dict = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {filepath}")
            return cls.from_dict(config_dict)
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML configuration: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Configuration as dictionary
        """
        return {
            'physics': {
                'timestep': self.physics.timestep,
                'sub_iterations': self.physics.sub_iterations,
                'max_speed': self.physics.max_speed,
                'max_angular_velocity': self.physics.max_angular_velocity,
            },
            'control': {
                'rudder_max_angle': self.control.rudder_max_angle,
                'rudder_min_angle': self.control.rudder_min_angle,
                'heading_error_scale': self.control.heading_error_scale,
                'stability_factor': self.control.stability_factor,
                'noise_factor': self.control.noise_factor,
                'waypoint_arrival_radius': self.control.waypoint_arrival_radius,
                'path_recalc_interval': self.control.path_recalc_interval,
            },
            'navigation': {
                'upwind_no_go_angle': self.navigation.upwind_no_go_angle,
                'downwind_no_go_angle': self.navigation.downwind_no_go_angle,
                'tack_angle': self.navigation.tack_angle,
                'jibe_angle': self.navigation.jibe_angle,
            },
            'display': {
                'fps': self.display.fps,
                'update_interval': self.display.update_interval,
                'show_forces': self.display.show_forces,
                'show_velocity': self.display.show_velocity,
                'show_course': self.display.show_course,
                'track_boat': self.display.track_boat,
            },
            'data_dir': str(self.data_dir),
            'log_dir': str(self.log_dir),
            'log_level': self.log_level,
            'log_to_file': self.log_to_file,
            'log_to_console': self.log_to_console,
        }
    
    def save_to_yaml(self, filepath: Union[str, Path]):
        """
        Save configuration to YAML file
        
        Args:
            filepath: Path to save configuration
        """
        try:
            with open(filepath, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Saved configuration to {filepath}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")


# Global configuration instance
_global_config: Optional[SimulatorConfig] = None


def get_config() -> SimulatorConfig:
    """Get global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = SimulatorConfig()
        _global_config.validate()
    return _global_config


def set_config(config: SimulatorConfig):
    """Set global configuration instance"""
    global _global_config
    config.validate()
    _global_config = config
    logger.info("Global configuration updated")


def load_config(filepath: Union[str, Path]):
    """Load and set global configuration from file"""
    config = SimulatorConfig.from_yaml(filepath)
    set_config(config)
    return config
