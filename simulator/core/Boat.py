"""
Boat physics simulation module

This module implements the core physics engine for sailing boat simulation,
including forces, moments, velocities, and position updates.

Enhanced with type hints, validation, and error handling.
"""

import math
import copy
from typing import List, Dict, Tuple, Optional
from .Variables import Angle, Vector
from .Foil import foil

# Import validation and error handling
try:
    from .validators import Validator
    from .exceptions import PhysicsError, ValidationError
    from .constants import (
        DEFAULT_SUB_ITERATIONS, MAX_REALISTIC_BOAT_SPEED,
        MAX_REALISTIC_ANGULAR_VELOCITY, MIN_BOAT_MASS,
        DEG_TO_RAD, RAD_TO_DEG, EPSILON
    )
    from .logger import logger, log_performance
except ImportError:
    # Fallback for backward compatibility
    class Validator:
        @staticmethod
        def validate_positive(value, name="value", allow_zero=False):
            return float(value)
        @staticmethod
        def safe_divide(num, denom, default=0.0):
            return num / denom if abs(denom) > 1e-10 else default

    class PhysicsError(Exception):
        pass
    class ValidationError(Exception):
        pass

    DEFAULT_SUB_ITERATIONS = 30
    MAX_REALISTIC_BOAT_SPEED = 50.0
    MAX_REALISTIC_ANGULAR_VELOCITY = 10.0
    MIN_BOAT_MASS = 0.1
    DEG_TO_RAD = math.pi / 180.0
    RAD_TO_DEG = 180.0 / math.pi
    EPSILON = 1e-10

    class logger:
        @staticmethod
        def debug(msg, **kwargs):
            pass
        @staticmethod
        def warning(msg, **kwargs):
            pass
        @staticmethod
        def error(msg, **kwargs):
            pass

    def log_performance(name):
        def decorator(func):
            return func
        return decorator


class Boat:
    """
    Main boat physics simulation class.

    Handles all physics calculations including:
    - Force and moment calculations
    - Linear and rotational velocity updates
    - Position and rotation updates
    - Apparent wind calculations
    """

    def __init__(self,
                 hulls: List[foil],
                 sails: List[foil],
                 wind: Vector,
                 mass: float = 55.0,
                 refLat: float = 37.0):
        """
        Initialize boat

        Args:
            hulls: List of hull foil objects
            sails: List of sail foil objects
            wind: Wind vector
            mass: Boat mass in kg
            refLat: Reference latitude for coordinate conversions

        Raises:
            ValidationError: If inputs are invalid
            PhysicsError: If physics state is invalid
        """
        # Validate inputs
        if not isinstance(hulls, list) or len(hulls) == 0:
            raise ValidationError("Hulls must be a non-empty list")

        if not isinstance(sails, list):
            raise ValidationError("Sails must be a list")

        if not isinstance(wind, Vector):
            raise ValidationError(f"Wind must be a Vector, got {type(wind)}")

        try:
            mass = Validator.validate_positive(mass, "mass")
            if mass < MIN_BOAT_MASS:
                logger.warning(f"Boat mass {mass} kg is very small, minimum recommended: {MIN_BOAT_MASS} kg")
        except Exception as e:
            raise ValidationError(f"Invalid mass: {e}")

        # Validate latitude
        try:
            refLat = Validator.validate_range(refLat, -90, 90, "reference latitude")
        except Exception as e:
            raise ValidationError(f"Invalid reference latitude: {e}")

        # Initialize boat properties
        self.hulls: List[foil] = hulls
        self.sails: List[foil] = sails
        self.wind: Vector = wind
        self.mass: float = mass
        self.refLat: float = refLat

        # Global rotation of boat and all its parts
        self.angle: Angle = Angle(1, 90)

        # Forces on the boat (in Newtons)
        self.forces: Dict[str, Vector] = {
            "sails": Vector(Angle(1, 90), 0),
            "hulls": Vector(Angle(1, 90), 0)
        }

        # Moments on the boat (in Newton-meters)
        self.moments: Dict[str, float] = {
            "sails": 0.0,
            "hulls": 0.0
        }

        # Current boat velocities
        self.linearVelocity: Vector = Vector(Angle(1, 90), 0)  # m/s
        self.rotationalVelocity: float = 0.0  # radians/s, positive is ccw, negative is cw

        # Current boat position (in degrees)
        self.position: Vector = Vector(Angle(1, 90), 0)

        logger.info(f"Boat initialized: mass={mass}kg, hulls={len(hulls)}, sails={len(sails)}")
        logger.debug(f"Initial position: {self.position}, angle: {self.angle}")

    def setPos(self, pos: Vector) -> None:
        """
        Set boat position

        Args:
            pos: New position vector

        Raises:
            ValidationError: If position is invalid
        """
        if not isinstance(pos, Vector):
            raise ValidationError(f"Position must be a Vector, got {type(pos)}")

        self.position = pos
        logger.debug(f"Boat position set to: {pos}")

    def resetValues(self) -> None:
        """Reset all velocities, forces, and moments to zero"""
        self.rotationalVelocity = 0.0
        self.linearVelocity = Vector(Angle(1, 0), 0)
        self.forces = {
            "sails": Vector(Angle(1, 0), 0),
            "hulls": Vector(Angle(1, 0), 0)
        }
        self.moments = {
            "sails": 0.0,
            "hulls": 0.0
        }
        logger.debug("Boat values reset")

    @log_performance("Boat Update")
    def update(self, dt: float = 1.0) -> None:
        """
        Update boat physics for one timestep

        Uses sub-iterations for improved accuracy and stability.

        Args:
            dt: Timestep in seconds

        Raises:
            ValidationError: If timestep is invalid
            PhysicsError: If physics state becomes invalid
        """
        # Validate timestep
        try:
            dt = Validator.validate_positive(dt, "timestep")
        except Exception as e:
            raise ValidationError(f"Invalid timestep: {e}")

        if dt > 1.0:
            logger.warning(f"Large timestep: {dt}s. Physics may be unstable.")

        # Use sub-iterations for accuracy
        num_iterations = DEFAULT_SUB_ITERATIONS

        try:
            # Initial force and moment update
            self.updateSailForcesandMoments(dt / (num_iterations + 1))
            self.updateHullForcesandMoments()

            # Sub-iteration loop for velocity updates
            for i in range(num_iterations):
                self.updateLinearVelocity(dt / num_iterations)
                self.updateRotationalVelocity(dt / (num_iterations + 1))
                self.updateSailForcesandMoments(dt / (num_iterations + 1))
                self.updateHullForcesandMoments()

            # Update position and rotation
            self.updatePosition(dt)
            self.updateRotation(dt)

            # Validate physics state
            self._validate_physics_state()

        except Exception as e:
            logger.error(f"Error during boat update: {e}", exc_info=True)
            raise PhysicsError(f"Physics update failed: {e}")

    def _validate_physics_state(self) -> None:
        """
        Validate that physics state is reasonable

        Raises:
            PhysicsError: If state is invalid
        """
        # Check linear velocity
        speed = self.linearVelocity.speed()
        if speed > MAX_REALISTIC_BOAT_SPEED:
            logger.warning(f"Boat speed {speed:.2f} m/s exceeds realistic maximum {MAX_REALISTIC_BOAT_SPEED} m/s")

        # Check angular velocity
        if abs(self.rotationalVelocity) > MAX_REALISTIC_ANGULAR_VELOCITY:
            logger.warning(f"Angular velocity {self.rotationalVelocity:.2f} rad/s exceeds realistic maximum")

        # Check for NaN or inf
        if math.isnan(speed) or math.isinf(speed):
            raise PhysicsError(f"Invalid linear velocity: {speed}")

        if math.isnan(self.rotationalVelocity) or math.isinf(self.rotationalVelocity):
            raise PhysicsError(f"Invalid rotational velocity: {self.rotationalVelocity}")

    def updatePosition(self, dt: float) -> None:
        """
        Update boat position based on velocity and acceleration

        Uses kinematic equation: d = v*dt + 0.5*a*dt²

        Args:
            dt: Timestep in seconds
        """
        try:
            # Calculate total force
            total_force = self.forces["sails"] + self.forces["hulls"]

            # Calculate acceleration components (F = ma, so a = F/m)
            ax = Validator.safe_divide(total_force.xcomp(), self.mass, 0.0)
            ay = Validator.safe_divide(total_force.ycomp(), self.mass, 0.0)

            # Create acceleration vector
            magnitude = math.sqrt(ax**2 + ay**2)

            # Avoid division by zero in atan2
            if abs(ax) < EPSILON and abs(ay) < EPSILON:
                angle_deg = 0.0
            else:
                angle_deg = math.atan2(ay, ax) * RAD_TO_DEG

            a = Vector(Angle(1, round(angle_deg * 10000) / 10000), magnitude)

            # Calculate displacement: d = v*dt + 0.5*a*dt²
            disp = self.linearVelocity * dt + (a * (dt**2)) * 0.5

            # Convert to degrees and update position
            self.position += disp.meter2degree(self.refLat)

        except Exception as e:
            logger.error(f"Error updating position: {e}", exc_info=True)
            raise PhysicsError(f"Position update failed: {e}")

    def updateRotation(self, dt: float) -> None:
        """
        Update boat rotation based on angular velocity and acceleration

        Uses kinematic equation: dθ = ω*dt + 0.5*α*dt²

        Args:
            dt: Timestep in seconds
        """
        try:
            # Calculate total moment
            total_moment = self.moments["sails"] + self.moments["hulls"]

            # Calculate total rotational inertia
            total_inertia = sum([h.I for h in self.hulls]) + sum([s.I for s in self.sails])

            # Calculate angular acceleration (τ = I*α, so α = τ/I)
            angular_accel = Validator.safe_divide(total_moment, total_inertia, 0.0)

            # Calculate angular displacement: dθ = ω*dt + 0.5*α*dt²
            angular_disp_rad = self.rotationalVelocity * dt + (angular_accel * dt**2) / 2

            # Convert to degrees and update angle
            self.angle += Angle(1, angular_disp_rad * RAD_TO_DEG)

        except Exception as e:
            logger.error(f"Error updating rotation: {e}", exc_info=True)
            raise PhysicsError(f"Rotation update failed: {e}")

    def updateLinearVelocity(self, dt: float) -> None:
        """
        Update linear velocity based on acceleration

        Uses kinematic equation: v_f = v_0 + a*dt

        Args:
            dt: Timestep in seconds
        """
        try:
            # Calculate total force
            total_force = self.forces["sails"] + self.forces["hulls"]

            # Calculate acceleration components
            ax = Validator.safe_divide(total_force.xcomp(), self.mass, 0.0)
            ay = Validator.safe_divide(total_force.ycomp(), self.mass, 0.0)

            # Create acceleration vector
            magnitude = math.sqrt(ax**2 + ay**2)

            # Avoid division by zero in atan2
            if abs(ax) < EPSILON and abs(ay) < EPSILON:
                angle_deg = 0.0
            else:
                angle_deg = math.atan2(ay, ax) * RAD_TO_DEG

            a = Vector(Angle(1, round(angle_deg * 1000000) / 1000000), magnitude)

            # Update velocity: v_f = v_0 + a*dt
            a *= dt
            self.linearVelocity += a

        except Exception as e:
            logger.error(f"Error updating linear velocity: {e}", exc_info=True)
            raise PhysicsError(f"Linear velocity update failed: {e}")

    def updateRotationalVelocity(self, dt: float) -> None:
        """
        Update rotational velocity based on angular acceleration

        Uses kinematic equation: ω_f = ω_0 + α*dt
        where α = τ/I (torque / rotational inertia)

        Args:
            dt: Timestep in seconds
        """
        try:
            # Calculate total moment
            total_moment = self.moments["sails"] + self.moments["hulls"]

            # Calculate total rotational inertia
            total_inertia = sum([h.I for h in self.hulls]) + sum([s.I for s in self.sails])

            # Calculate angular acceleration
            angular_accel = Validator.safe_divide(total_moment, total_inertia, 0.0)

            # Update angular velocity: ω_f = ω_0 + α*dt
            self.rotationalVelocity += angular_accel * dt

        except Exception as e:
            logger.error(f"Error updating rotational velocity: {e}", exc_info=True)
            raise PhysicsError(f"Rotational velocity update failed: {e}")

    def updateSailForcesandMoments(self, dt: float) -> None:
        """
        Update forces and moments from all sails

        Args:
            dt: Timestep in seconds
        """
        try:
            # Reset sail forces and moments
            self.forces["sails"] = Vector(Angle(1, 0), 0)
            self.moments["sails"] = 0.0

            # Calculate forces from each sail
            for idx in range(len(self.sails)):
                # Calculate lift and drag forces
                lift_force = self.sailLiftForce(idx)
                drag_force = self.sailDragForce(idx)
                total_force = lift_force + drag_force

                # Add to total sail forces
                self.forces["sails"] += total_force

                # Update sail rotation based on apparent wind
                apparent_wind = self.sailAparentWind(idx)
                self.sails[idx].updateSailRotation(dt, apparent_wind)

                # NOTE: Sail moments could be added here if needed
                # self.moments["sails"] += self.sails[idx].moment(total_force)

        except Exception as e:
            logger.error(f"Error updating sail forces: {e}", exc_info=True)
            raise PhysicsError(f"Sail force update failed: {e}")

    def updateHullForcesandMoments(self) -> None:
        """Update forces and moments from all hulls"""
        try:
            # Reset hull forces and moments
            self.forces["hulls"] = Vector(Angle(1, 0), 0)
            self.moments["hulls"] = 0.0

            # Calculate forces and moments from each hull
            for idx in range(len(self.hulls)):
                # Get lift force and moment
                lift_force, lift_moment = self.hullLiftForceandMoment(idx)

                # Get drag force and moment
                drag_force, drag_moment = self.hullDragForceandMoment(idx)

                # Add to totals
                self.forces["hulls"] += lift_force + drag_force
                self.moments["hulls"] += lift_moment + drag_moment

        except Exception as e:
            logger.error(f"Error updating hull forces: {e}", exc_info=True)
            raise PhysicsError(f"Hull force update failed: {e}")


    def sailDragForce(self, idx: int = 0) -> Vector:
        """
        Calculate drag force on a sail

        Args:
            idx: Sail index

        Returns:
            Drag force vector in global coordinates
        """
        # Get apparent force in sail's reference frame
        apparent_wind = self.sailAparentWind(idx)
        apparent_force = self.sails[idx].dragForce(apparent_wind)

        # Transform to global coordinates
        true_force = Vector(
            apparent_force.angle + self.angle + self.sails[idx].angle,
            apparent_force.norm
        )
        true_force.angle = Angle.norm(true_force.angle)

        return true_force

    def sailLiftForce(self, idx: int = 0) -> Vector:
        """
        Calculate lift force on a sail

        Args:
            idx: Sail index

        Returns:
            Lift force vector in global coordinates
        """
        # Get apparent force in sail's reference frame
        apparent_wind = self.sailAparentWind(idx)
        apparent_force = self.sails[idx].liftForce(apparent_wind)

        # Transform to global coordinates
        true_force = Vector(
            apparent_force.angle + self.angle + self.sails[idx].angle,
            apparent_force.norm
        )
        true_force.angle = Angle.norm(true_force.angle)

        return true_force

    def hullDragForceandMoment(self, idx: int = 0) -> Tuple[Vector, float]:
        """
        Calculate drag force and moment on a hull

        Args:
            idx: Hull index

        Returns:
            Tuple of (drag force vector, moment)
        """
        # Get apparent force in hull's reference frame
        apparent_wind = self.hullAparentWind(idx)
        apparent_force = self.hulls[idx].dragForce(apparent_wind)

        # Calculate moment
        moment = self.hulls[idx].moment(apparent_force)

        # Transform force to global coordinates
        true_force = Vector(
            apparent_force.angle + self.angle + self.hulls[idx].angle,
            apparent_force.norm
        )
        true_force.angle = Angle.norm(true_force.angle)

        return true_force, moment

    def hullLiftForceandMoment(self, idx: int = 0) -> Tuple[Vector, float]:
        """
        Calculate lift force and moment on a hull

        Args:
            idx: Hull index

        Returns:
            Tuple of (lift force vector, moment)
        """
        # Get apparent force in hull's reference frame
        apparent_wind = self.hullAparentWind(idx)
        apparent_force = self.hulls[idx].liftForce(apparent_wind)

        # Calculate moment
        moment = self.hulls[idx].moment(apparent_force)

        # Transform force to global coordinates
        true_force = Vector(
            apparent_force.angle + self.angle + self.hulls[idx].angle,
            apparent_force.norm
        )
        true_force.angle = Angle.norm(true_force.angle)

        return true_force, moment

    def globalAparentWind(self) -> Vector:
        """
        Calculate global apparent wind on boat

        Apparent wind = True wind - Boat velocity

        Returns:
            Apparent wind vector
        """
        return self.wind - self.linearVelocity

    def sailAparentWind(self, idx: int = 0) -> Vector:
        """
        Calculate local apparent wind on a sail

        Returns wind angle in perspective of the given sail,
        accounting for boat motion and rotation.

        CONVENTION: Wind points in the direction it's going

        Args:
            idx: Sail index

        Returns:
            Apparent wind vector in sail's reference frame
        """
        # Get global apparent wind
        ap = self.globalAparentWind()

        # Transform to sail's reference frame
        # Rotate by 180° to get wind direction
        ap.angle += Angle(1, 180)

        # Subtract sail and boat angles to get relative angle
        ap.angle = ap.angle - (self.sails[idx].angle + self.angle)

        # Rotate back by 180°
        ap.angle += Angle(1, 180)

        return ap

    def hullAparentWind(self, idx: int = 0) -> Vector:
        """
        Calculate apparent water velocity on a hull

        Accounts for both linear and rotational velocity of the boat.

        CONVENTION: Flow direction is AGAINST the hull

        Args:
            idx: Hull index

        Returns:
            Apparent water velocity vector in hull's reference frame
        """
        # Calculate tangential velocity from rotation
        # V_tangential = ω × r (angular velocity × radius)
        tangential_speed = self.rotationalVelocity * self.hulls[idx].position.norm
        V = Vector(self.angle, tangential_speed)

        # Add linear velocity
        V += self.linearVelocity

        # Transform to hull's reference frame
        V.angle -= (self.angle + self.hulls[idx].angle)

        # Flip to measure flow AGAINST hull
        V.angle += Angle(1, 180)

        return V

    # TODO: Add method for getting true wind angle from apparent wind for actual boat