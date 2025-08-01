"""
Improved Display Module - Enhanced visualization and control interface.

This module provides an improved UI with:
- Cleaner layout and better organization
- Real-time controller selection
- Improved visual feedback
- Better data formatting
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.transforms as transforms
from matplotlib.widgets import TextBox
import numpy as np

from .Display import display as BaseDisplay
from .Map import regionPolygon, loadGrib
from ..core.Variables import Angle, Vector
from ..control.ControlModular import ModularController
from ..control.controllers import (
    SimpleRudderController, WaypointRudderController,
    SimpleSailController, SimplePathfindingController
)


class ImprovedDisplay(BaseDisplay):
    """
    Enhanced display system with improved UI and controller selection.
    """
    
    def __init__(self, location, boat):
        """Initialize the improved display."""
        # Store boat reference before calling parent init
        self.boat_ref = boat
        self.location = location
        
        # Controller options
        self.available_rudder_controllers = {
            'Simple': SimpleRudderController,
            'Waypoint': WaypointRudderController,
        }
        
        self.available_sail_controllers = {
            'Simple': SimpleSailController,
        }
        
        self.available_pathfinding_controllers = {
            'Simple': SimplePathfindingController,
        }
        
        # Create modular controller
        self.modular_controller = None
        
        # Initialize with improved layout
        self.create_improved_layout()
        
        # Call parent initialization with custom layout
        super().__init__(location, boat)
        
    def create_improved_layout(self):
        """Create an improved layout with better organization."""
        # Create figure with better proportions
        self.f = plt.figure(figsize=(16, 10))
        self.f.suptitle(f'Physics Sailing Simulator - {self.location}', fontsize=16, fontweight='bold')
        
        # Define improved layout grid
        # Main display takes more space, controls are better organized
        gs = self.f.add_gridspec(4, 4, 
                                width_ratios=[3, 1, 1, 1],
                                height_ratios=[1, 1, 1, 1],
                                hspace=0.3, wspace=0.3)
        
        # Create axes
        self.axes = {}
        self.axes['A'] = self.f.add_subplot(gs[:, 0])  # Main map - full left side
        self.axes['B'] = self.f.add_subplot(gs[0, 1:])  # Controller selection - top right
        self.axes['C'] = self.f.add_subplot(gs[1, 1:])  # Boat controls - middle right
        self.axes['D'] = self.f.add_subplot(gs[2, 1:])  # Simulation controls - lower middle right
        self.axes['E'] = self.f.add_subplot(gs[3, 1:])  # Telemetry - bottom right
        
        # Style the panels
        for key, ax in self.axes.items():
            if key != 'A':  # Don't box the main map
                ax.set_facecolor('#f8f9fa')
                for spine in ax.spines.values():
                    spine.set_edgecolor('#dee2e6')
                    spine.set_linewidth(1)
        
        # Adjust main map appearance
        self.axes['A'].set_aspect('equal')
        
    def __init__(self, location, boat):
        """Override parent init to use our layout."""
        # Skip parent init, implement our own
        self.location = location
        self.boat_ref = boat
        
        # Create improved layout first
        self.create_improved_layout()
        
        # Initialize display components
        self.pause = False
        self.track = True
        self.auto = False
        self.forceShow = True
        self.time = 0
        
        # Import boat display shell from parent
        from .Display import boatDisplayShell
        self.boat = boatDisplayShell(boat, self.axes['A'], boat.position.ycomp())
        
        # Initialize map
        self.map(location)
        
        # Initialize boat visualization
        self.boat.initAuto()
        self.boat.createHulls()
        self.boat.createWindIndicator()
        self.boat.update(self.auto, self.forceShow)
        self.boat.plotCourse()
        
        # Create all UI components
        self.create_controller_selection()
        self.create_boat_controls()
        self.create_simulation_controls()
        self.create_telemetry_display()
        
        # Initialize modular controller
        self.init_modular_controller()
        
    def create_controller_selection(self):
        """Create the controller selection panel."""
        ax = self.axes['B']
        ax.clear()
        ax.set_title('Controller Selection', fontsize=12, fontweight='bold', pad=10)
        ax.axis('off')
        
        # Calculate positions
        y_positions = np.linspace(0.8, 0.1, 3)
        
        # Rudder controller selection
        self.rudder_label = ax.text(0.05, y_positions[0], 'Rudder Controller:', 
                                   fontsize=10, fontweight='bold')
        
        rudder_rax = plt.axes([0.52, 0.88, 0.15, 0.08])
        self.rudder_radio = RadioButtons(rudder_rax, list(self.available_rudder_controllers.keys()))
        self.rudder_radio.on_clicked(self.on_rudder_controller_change)
        
        # Sail controller selection  
        self.sail_label = ax.text(0.05, y_positions[1], 'Sail Controller:', 
                                 fontsize=10, fontweight='bold')
        
        sail_rax = plt.axes([0.52, 0.78, 0.15, 0.08])
        self.sail_radio = RadioButtons(sail_rax, list(self.available_sail_controllers.keys()))
        self.sail_radio.on_clicked(self.on_sail_controller_change)
        
        # Pathfinding controller selection
        self.path_label = ax.text(0.05, y_positions[2], 'Pathfinding:', 
                                 fontsize=10, fontweight='bold')
        
        path_rax = plt.axes([0.52, 0.68, 0.15, 0.08])
        self.path_radio = RadioButtons(path_rax, list(self.available_pathfinding_controllers.keys()))
        self.path_radio.on_clicked(self.on_pathfinding_controller_change)
        
        # Reset simulation button
        reset_ax = plt.axes([0.52, 0.55, 0.15, 0.05])
        self.reset_button = Button(reset_ax, 'Reset Simulation', 
                                  color='#dc3545', hovercolor='#c82333')
        self.reset_button.on_clicked(self.reset_simulation)
        
    def create_boat_controls(self):
        """Create improved boat control panel."""
        ax = self.axes['C']
        ax.clear()
        ax.set_title('Boat Controls', fontsize=12, fontweight='bold', pad=10)
        ax.axis('off')
        
        # Control sliders with better styling
        slider_configs = [
            ('Rudder', -20, 20, 0, 0.75),
            ('Sail Trim', -90, 90, 0, 0.50),
            ('Wind Dir', 0, 360, 270, 0.25)
        ]
        
        self.sliders = {}
        for name, vmin, vmax, vinit, y_pos in slider_configs:
            # Label
            ax.text(0.05, y_pos + 0.08, f'{name}:', fontsize=10)
            
            # Value display
            value_text = ax.text(0.85, y_pos + 0.08, f'{vinit}°', 
                               fontsize=10, ha='right')
            
            # Slider
            slider_ax = plt.axes([0.52, 0.14 + y_pos * 0.65, 0.35, 0.03])
            slider = Slider(slider_ax, '', vmin, vmax, valinit=vinit,
                          color='#007bff', alpha=0.7)
            
            # Store references
            self.sliders[name] = {
                'slider': slider,
                'value_text': value_text
            }
            
            # Connect update function
            if name == 'Rudder':
                slider.on_changed(lambda val: self.update_control('rudder', val))
            elif name == 'Sail Trim':
                slider.on_changed(lambda val: self.update_control('sail', val))
            else:
                slider.on_changed(lambda val: self.update_control('wind', val))
    
    def create_simulation_controls(self):
        """Create simulation control panel."""
        ax = self.axes['D']
        ax.clear()
        ax.set_title('Simulation Controls', fontsize=12, fontweight='bold', pad=10)
        ax.axis('off')
        
        # Create buttons with better styling
        button_configs = [
            ('Pause', 0.1, 0.7, '#ffc107', '#e0a800', self.pause_toggle),
            ('Autopilot', 0.35, 0.7, '#28a745', '#218838', self.autopilot_toggle),
            ('Show Forces', 0.6, 0.7, '#17a2b8', '#138496', self.forces_toggle),
            ('Track Boat', 0.1, 0.4, '#6c757d', '#5a6268', self.tracking_toggle),
        ]
        
        self.buttons = {}
        for name, x, y, color, hover_color, callback in button_configs:
            button_ax = plt.axes([x + 0.4, y, 0.12, 0.15])
            button = Button(button_ax, name, color=color, hovercolor=hover_color)
            button.on_clicked(callback)
            self.buttons[name] = button
            
        # Speed control slider
        ax.text(0.05, 0.1, 'Sim Speed:', fontsize=10)
        speed_ax = plt.axes([0.52, 0.15, 0.35, 0.03])
        self.speed_slider = Slider(speed_ax, '', 1, 50, valinit=1, 
                                 color='#6f42c1', alpha=0.7)
        self.speed_text = ax.text(0.85, 0.1, '1x', fontsize=10, ha='right')
        self.speed_slider.on_changed(self.update_speed)
        
    def create_telemetry_display(self):
        """Create improved telemetry panel."""
        ax = self.axes['E']
        ax.clear()
        ax.set_title('Telemetry', fontsize=12, fontweight='bold', pad=10)
        ax.axis('off')
        
        # Create formatted telemetry display
        self.telemetry_texts = {
            'speed': ax.text(0.05, 0.85, '', fontsize=9),
            'heading': ax.text(0.05, 0.70, '', fontsize=9),
            'wind': ax.text(0.05, 0.55, '', fontsize=9),
            'position': ax.text(0.05, 0.40, '', fontsize=9),
            'forces': ax.text(0.05, 0.25, '', fontsize=9),
            'controller': ax.text(0.05, 0.10, '', fontsize=9),
        }
        
    def init_modular_controller(self):
        """Initialize the modular controller system."""
        if not hasattr(self.boat, 'boat'):
            return
            
        # Create modular controller with default controllers
        self.modular_controller = ModularController(
            self.boat.boat,
            rudder_controller=WaypointRudderController(self.boat.boat),
            sail_controller=SimpleSailController(self.boat.boat),
            pathfinding_controller=SimplePathfindingController(self.boat.boat, None)
        )
        
        # Set pathfinding controller reference
        self.modular_controller.pathfinding_controller.controller = self.modular_controller
        
        # Copy waypoints from boat autopilot if exists
        if hasattr(self.boat, 'autopilot') and hasattr(self.boat.autopilot, 'waypoints'):
            self.modular_controller.waypoints = self.boat.autopilot.waypoints
            self.modular_controller.course_type = self.boat.courseType
            self.modular_controller.calculate_next_leg()
        
        # Replace boat autopilot with modular controller
        self.boat.autopilot = self.modular_controller
        
    def on_rudder_controller_change(self, label):
        """Handle rudder controller selection change."""
        if self.modular_controller:
            controller_class = self.available_rudder_controllers[label]
            new_controller = controller_class(self.boat.boat)
            self.modular_controller.set_rudder_controller(new_controller)
            self.update_telemetry()
            
    def on_sail_controller_change(self, label):
        """Handle sail controller selection change."""
        if self.modular_controller:
            controller_class = self.available_sail_controllers[label]
            new_controller = controller_class(self.boat.boat)
            self.modular_controller.set_sail_controller(new_controller)
            self.update_telemetry()
            
    def on_pathfinding_controller_change(self, label):
        """Handle pathfinding controller selection change."""
        if self.modular_controller:
            controller_class = self.available_pathfinding_controllers[label]
            new_controller = controller_class(self.boat.boat, self.modular_controller)
            self.modular_controller.set_pathfinding_controller(new_controller)
            # Recalculate path with new controller
            self.modular_controller.calculate_next_leg()
            self.boat.plotCourse()
            self.update_telemetry()
            
    def reset_simulation(self, event):
        """Reset the simulation to initial state."""
        # Reset boat position and state
        self.boat.boat.position = Vector(Angle(1, 90), 0)
        self.boat.boat.angle = Angle(1, -93)
        self.boat.boat.linearVelocity = Vector(Angle(1, 0), 0)
        self.boat.boat.rotationalVelocity = 0
        
        # Reset controller state
        if self.modular_controller:
            self.modular_controller.calculate_next_leg()
        
        # Reset time
        self.time = 0
        
        # Update display
        self.boat.update(self.auto, self.forceShow)
        self.update_telemetry()
        
    def update_control(self, control_type, value):
        """Update boat controls with value display."""
        if control_type == 'rudder':
            self.boat.boat.hulls[-1].angle = Angle(1, value)
            self.sliders['Rudder']['value_text'].set_text(f'{value:.1f}°')
        elif control_type == 'sail':
            if self.boat.boat.sails:
                self.boat.boat.sails[0].angle = Angle(1, value)
            self.sliders['Sail Trim']['value_text'].set_text(f'{value:.1f}°')
        elif control_type == 'wind':
            self.boat.boat.wind.angle = Angle(1, value)
            self.sliders['Wind Dir']['value_text'].set_text(f'{value:.0f}°')
            
    def update_speed(self, value):
        """Update simulation speed."""
        self.cycles = int(value)
        self.speed_text.set_text(f'{int(value)}x')
        
    def pause_toggle(self, event):
        """Toggle pause state."""
        self.pause = not self.pause
        self.buttons['Pause'].label.set_text('Resume' if self.pause else 'Pause')
        
    def autopilot_toggle(self, event):
        """Toggle autopilot."""
        self.auto = not self.auto
        if self.modular_controller:
            self.modular_controller.autopilot_enabled = self.auto
        self.buttons['Autopilot'].color = '#28a745' if self.auto else '#6c757d'
        
    def forces_toggle(self, event):
        """Toggle force display."""
        self.forceShow = not self.forceShow
        self.boat.toggleForces()
        
    def tracking_toggle(self, event):
        """Toggle boat tracking."""
        self.track = not self.track
        
    def update_telemetry(self):
        """Update telemetry display with formatted data."""
        if not hasattr(self.boat, 'boat'):
            return
            
        boat = self.boat.boat
        
        # Speed and heading
        speed_ms = boat.linearVelocity.norm
        speed_kts = speed_ms * 1.94384
        self.telemetry_texts['speed'].set_text(f'Speed: {speed_ms:.2f} m/s ({speed_kts:.1f} kts)')
        self.telemetry_texts['heading'].set_text(f'Heading: {boat.angle.calc():.1f}°')
        
        # Wind
        wind_angle = boat.wind.angle.calc()
        wind_speed = boat.wind.norm
        self.telemetry_texts['wind'].set_text(f'Wind: {wind_speed:.1f} m/s from {wind_angle:.0f}°')
        
        # Position
        lat = boat.position.ycomp()
        lon = boat.position.xcomp()
        self.telemetry_texts['position'].set_text(f'Pos: ({lon:.6f}, {lat:.6f})')
        
        # Forces (simplified)
        if boat.sails:
            sail_force = boat.sailLiftForce(0).norm + boat.sailDragForce(0).norm
            self.telemetry_texts['forces'].set_text(f'Sail Force: {sail_force:.1f} N')
        
        # Controller info
        if self.modular_controller:
            rudder_name = type(self.modular_controller.rudder_controller).__name__
            self.telemetry_texts['controller'].set_text(f'Controller: {rudder_name[:15]}...')
            
    def updateCycle(self, n):
        """Main update cycle with improved features."""
        if not self.pause:
            # Update physics
            for _ in range(self.cycles):
                self.boat.boat.update(1/70)
                self.time += 1/70
                
                # Update controller
                if self.auto and self.modular_controller:
                    self.modular_controller.update(1/70)
                    
            # Update visualization
            self.boat.update(self.auto, self.forceShow)
            
            # Update telemetry
            self.update_telemetry()
            
            # Track boat if enabled
            if self.track:
                # Center view on boat
                x, y = self.boat.boat.position.xcomp(), self.boat.boat.position.ycomp()
                xlim = self.axes['A'].get_xlim()
                ylim = self.axes['A'].get_ylim()
                dx = xlim[1] - xlim[0]
                dy = ylim[1] - ylim[0]
                self.axes['A'].set_xlim(x - dx/2, x + dx/2)
                self.axes['A'].set_ylim(y - dy/2, y + dy/2)
                
    def run_animation(self):
        """Run the animation with improved display."""
        self.anim = FuncAnimation(self.f, self.updateCycle, interval=1000/70, 
                                 blit=False, cache_frame_data=False)
        plt.show()


# Create convenience function
def improved_display(location, boat):
    """Create and return an improved display instance."""
    return ImprovedDisplay(location, boat)