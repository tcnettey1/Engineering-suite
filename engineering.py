"""
Engineering calculations module for Fluid Flow and Heat Transfer suite.
Handles fluid properties, pipe friction, flow analysis, and thermal dynamics.
"""

import math
import numpy as np


class Fluid:
    """Represents physical properties of a working fluid."""

    def __init__(self, name: str, density: float, viscosity: float, specific_heat: float = 4184):
        """
        :param name: Name of the fluid
        :param density: Fluid density in kg/m^3
        :param viscosity: Dynamic viscosity in Pa·s (kg/(m·s))
        :param specific_heat: Specific heat capacity in J/(kg·K)
        """
        self.name = name
        self.density = density
        self.viscosity = viscosity
        self.specific_heat = specific_heat


class Pipe:
    """Represents pipe geometry and fluid dynamic behavior."""

    def __init__(self, diameter: float, length: float, roughness: float):
        """
        :param diameter: Internal diameter in meters
        :param length: Length in meters
        :param roughness: Absolute pipe roughness in meters
        """
        if diameter <= 0 or length <= 0 or roughness < 0:
            raise ValueError("Pipe dimensions must be positive values.")
        self.diameter = diameter
        self.length = length
        self.roughness = roughness
        self.area = math.pi * (diameter / 2) ** 2

    def calculate_velocity(self, flow_rate_m3h: float) -> float:
        """Calculates flow velocity (m/s) given volumetric flow rate (m^3/h)."""
        flow_rate_m3s = flow_rate_m3h / 3600.0
        return flow_rate_m3s / self.area

    def calculate_reynolds(self, velocity: float, fluid: Fluid) -> float:
        """Calculates Reynolds Number (Re)."""
        return (fluid.density * velocity * self.diameter) / fluid.viscosity

    def calculate_friction_factor(self, reynolds: float) -> float:
        """
        Calculates Darcy-Weisbach friction factor.
        Uses laminar exact formula (64/Re) or Swamee-Jain explicit approximation for turbulent flow.
        """
        if reynolds <= 0:
            return 0.0
        if reynolds < 2300:
            return 64.0 / reynolds
        
        # Swamee-Jain equation for turbulent flow
        rel_roughness = self.roughness / self.diameter
        term = (rel_roughness / 3.7) + (5.74 / (reynolds ** 0.9))
        return 0.25 / ((math.log10(term)) ** 2)

    def calculate_pressure_drop(self, velocity: float, friction_factor: float, fluid: Fluid) -> float:
        """Calculates pressure drop in Pascals (Pa) using Darcy-Weisbach equation."""
        return friction_factor * (self.length / self.diameter) * (fluid.density * (velocity ** 2) / 2.0)


class HeatTransferEngine:
    """Calculates steady-state conduction and transient cooling dynamics."""

    @staticmethod
    def wall_conduction(k: float, area: float, thickness: float, t_inside: float, t_outside: float) -> float:
        """Calculates heat rate Q (Watts) across a flat wall using Fourier's Law."""
        if thickness <= 0:
            raise ValueError("Wall thickness must be greater than zero.")
        return k * area * (t_inside - t_outside) / thickness

    @staticmethod
    def transient_cooling(t_initial: float, t_ambient: float, k_cooling: float, time_max: float, points: int = 200):
        """
        Simulates Newton's Law of Cooling over time: T(t) = T_inf + (T0 - T_inf) * exp(-k*t)
        Returns (times_array, temperatures_array).
        """
        times = np.linspace(0, time_max, points)
        temps = t_ambient + (t_initial - t_ambient) * np.exp(-k_cooling * times)
        return times, temps

    @staticmethod
    def time_to_target_temp(t_initial: float, t_ambient: float, t_target: float, k_cooling: float) -> float:
        """Calculates exact time required to reach a target temperature."""
        if k_cooling <= 0:
            raise ValueError("Cooling constant k must be greater than zero.")
        if (t_target - t_ambient) / (t_initial - t_ambient) <= 0:
            raise ValueError("Target temperature is physically unachievable under these conditions.")
        return -math.log((t_target - t_ambient) / (t_initial - t_ambient)) / k_cooling
