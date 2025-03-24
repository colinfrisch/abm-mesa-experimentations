# Guerilla Warfare Agent-Based Model

This agent-based model (ABM) simulates guerilla warfare scenarios to verify and compare theoretical models: the Square Law (Lanchester) for conventional warfare and the modified asymmetric model (Deitchman adaptation) for guerilla warfare.

## Overview

The model simulates combat between two forces: a conventional Army and a Guerilla force. It supports two engagement scenarios:
- **Classic warfare**: Forces face each other in traditional battle lines
- **Ambush**: Guerilla forces encircle and attack the conventional forces

## Table of Contents
- [Theoretical Background](#theoretical-background)
- [Model Components](#model-components)
- [Scenarios](#scenarios)
- [Agent Behavior](#agent-behavior)
- [Visualization](#visualization)
- [Installation and Usage](#installation-and-usage)
- [Extending the Model](#extending-the-model)
- [References](#references)

## Theoretical Background

The model implements and compares two mathematical warfare models:

| Aspect                 | Classical Engagement                            | Ambush Engagement                                 |
|------------------------|--------------------------------------------------|--------------------------------------------------|
| Visibility             | Mutual visibility                                | Guerrillas are hidden; defenders are exposed      |
| Governing Equations    | dx₁/dt = -a·x₂  <br> dx₂/dt = -b·x₁              | dx₁/dt = -A·x₂·x₁  <br> dx₂/dt = -b·x₁             |
| Required Superiority   | Global numerical and firepower advantage         | Local superiority and tactical advantage          |
| Likely Outcome         | Side with more numbers or firepower wins         | Guerrillas can win despite being outnumbered      |

## Model Components

### GuerillaModel (`model.py`)
The main model class that:
- Initializes the simulation grid
- Places agents according to scenario rules
- Collects data during simulation
- Manages step execution

### SoldierAgent (`agents.py`)
Represents individual soldiers with:
- Side affiliation (Army or Guerilla)
- Firepower (probability of killing when shooting)
- Sight range (distance at which enemies can be detected)
- Movement and combat behavior

### Visualization (`app.py`)
Uses Mesa's visualization tools to create an interactive interface with:
- Grid visualization of agent positions
- Time series plots of force sizes
- Adjustable model parameters



## Scenarios

### Classic Warfare
- Forces are placed on opposite sides of the grid
- Both sides have equal visibility and engagement capabilities
- Outcome typically favors the larger or more powerful force

### Ambush
- Army forces are placed in the center of the grid
- Guerilla forces are placed around the perimeter
- This scenario tests the asymmetric warfare model where smaller forces can prevail through tactical advantage

## Agent Behavior

Each soldier agent follows a simple decision process:
1. Find the closest enemy
2. If enemy is within sight range:
   - Shoot at the enemy with probability defined by fire_power
3. If no enemy is within sight range:
   - Move toward the closest enemy

Movement uses a Manhattan distance calculation to determine the closest enemy, followed by a directional vector to choose the best neighboring cell for movement.

## Visualization

The model includes a visualization interface built with Mesa's SolaraViz:
- Red circles represent Army soldiers
- Blue circles represent Guerilla fighters
- The grid shows current positions and movements
- Plots track the population of each force over time
- Sliders allow adjustment of model parameters

## Installation and Usage

1. Ensure you have Mesa installed:
    ```bash
    pip install mesa
    ```

2. Run the application:
    ```bash
    python app.py
    ```

3. Adjust parameters via the web interface sliders:
   - Set initial force sizes
   - Adjust firepower and sight ranges
   - Switch between Classic and Ambush scenarios

## Extending the Model (to continue)

## References

- Lanchester, F. W. (1916). *Aircraft in Warfare: The Dawn of the Fourth Arm*
- Deitchman, S. J. (1962). *A Lanchester Model of Guerrilla Warfare*. Operations Research, 10(6), 818–827
