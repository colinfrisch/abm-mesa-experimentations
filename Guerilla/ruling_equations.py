import math
import numpy as np
import matplotlib.pyplot as plt


def calculate_Lanchester(initial_army_personnel, step, fire_power, sight):
    """
    Calculate the number of remaining soldiers using Lanchester equations.
    
    Parameters:
    - initial_army_personnel: Starting number of soldiers (0-100)
    - step: Time step for calculation (usually 0-500)
    - fire_power: Probability of hitting a target (0-1)
    - sight: Knowledge of the field (1-10)
    
    Returns:
    Number of remaining soldiers at the given time step
    """
    
    # Calculate firing rate based on fire_power and sight
    # Combine fire_power with sight to create a more nuanced firing effectiveness
    g = fire_power * sight / 280  # Using the approximation from the document
    
    # Use the face-to-face battle model equation
    # x(t) = x0 * cosh(sqrt(ag)t) - (sqrt(g/a) * enemy_x0) * sinh(sqrt(ag)t)
    sqrt_ag = math.sqrt(g)
    
    # Assume symmetrical battle with equal initial conditions
    remaining_soldiers = (
        initial_army_personnel * math.cosh(sqrt_ag * step) - 
        initial_army_personnel * math.sinh(sqrt_ag * step)
    )
    
    # Ensure non-negative result
    return max(0, remaining_soldiers)


def calculate_Deitchman(initial_army_personnel, step, fire_power, sight, side='Army'):
    """
    Calculate the number of remaining soldiers in an ambush scenario using Deitchman's model.
    
    Parameters:
    - initial_army_personnel: Starting number of soldiers (0-100)
    - step: Time step for calculation (usually 0-500)
    - fire_power: Probability of hitting a target (0-1)
    - sight: Knowledge of the field (1-10)
    - side: 'Army' or 'Guerilla' to determine calculation method
    
    Returns:
    Number of remaining soldiers at the given time step
    """

    # A represents the random firing in a large area
    # g represents the targeted firing
    
    # Approximation of firing effectiveness based on document's calculations
    if side == 'Army':
        # Regular army firing randomly (lower accuracy)
        g = fire_power * sight / 280  # base firing rate
        A = 1.06e-5  # random firing coefficient from the document
        
        # Use the ambush model equations
        # Specific calculation for the Army side
        K = initial_army_personnel**2 * A**2 / (2*g)
        
        if K > 0:
            # Calculation for K > 0 case
            C1 = K
            term = math.tanh(math.sqrt(A * C1 / 2) * step)
            remaining = (
                initial_army_personnel / (1 + initial_army_personnel * math.sqrt(A / (2 * C1)) * term)
            )
        elif K == 0:
            # Calculation for K = 0 case
            remaining = initial_army_personnel / (1 + A * initial_army_personnel * step / 2)
        else:
            # Calculation for K < 0 case
            C1 = -K
            term = math.tan(math.sqrt(A * C1 / 2) * step)
            remaining = (
                initial_army_personnel / (1 + initial_army_personnel * math.sqrt(A / (2 * C1)) * term)
            )
    
    else:  # Guerilla side
        # Guerilla fighters with more precise targeting
        g = fire_power * sight / 280  # base firing rate
        A = 1.06e-5  # random firing coefficient
        
        # Simplified calculation for the ambushing side
        remaining = initial_army_personnel * math.exp(-g * step)
    
    return max(0, remaining)



def plot_example():
    """
    Plot an example of an ambush scenario with different parameters
    to demonstrate the Deitchman model's dynamics.
    """
    plt.figure(figsize=(12, 8))
    
    # Scenario 1: Regular army with good fire power
    plt.subplot(2, 2, 1)
    steps = np.linspace(0, 100, 200)
    Army_soldiers1 = [calculate_Deitchman(100, t, 0.8, 8, 'Army') for t in steps]
    Guerilla_soldiers1 = [calculate_Deitchman(100, t, 0.5, 5, 'Guerilla') for t in steps]
    
    plt.plot(steps, Army_soldiers1, label='Regular Army', color='blue')
    plt.plot(steps, Guerilla_soldiers1, label='Guerilla', color='red')
    plt.title('Scenario 1: Strong Regular Army')
    plt.xlabel('Time Step')
    plt.ylabel('Soldiers')
    plt.legend()
    plt.grid(True)
    
    # Scenario 2: Guerilla with surprise advantage
    plt.subplot(2, 2, 2)
    Army_soldiers2 = [calculate_Deitchman(70, t, 0.3, 3, 'Army') for t in steps]
    Guerilla_soldiers2 = [calculate_Deitchman(50, t, 0.9, 9, 'Guerilla') for t in steps]
    
    plt.plot(steps, Army_soldiers2, label='Regular Army', color='blue')
    plt.plot(steps, Guerilla_soldiers2, label='Guerilla', color='red')
    plt.title('Scenario 2: Guerilla Surprise Advantage')
    plt.xlabel('Time Step')
    plt.ylabel('Soldiers')
    plt.legend()
    plt.grid(True)
    
    # Scenario 3: Roughly equal forces
    plt.subplot(2, 2, 3)
    Army_soldiers3 = [calculate_Deitchman(80, t, 0.5, 5, 'Army') for t in steps]
    Guerilla_soldiers3 = [calculate_Deitchman(70, t, 0.5, 5, 'Guerilla') for t in steps]
    
    plt.plot(steps, Army_soldiers3, label='Regular Army', color='blue')
    plt.plot(steps, Guerilla_soldiers3, label='Guerilla', color='red')
    plt.title('Scenario 3: Balanced Forces')
    plt.xlabel('Time Step')
    plt.ylabel('Soldiers')
    plt.legend()
    plt.grid(True)
    
    # Scenario 4: Guerilla with terrain advantage
    plt.subplot(2, 2, 4)
    Army_soldiers4 = [calculate_Deitchman(100, t, 0.4, 2, 'Army') for t in steps]
    Guerilla_soldiers4 = [calculate_Deitchman(50, t, 0.6, 9, 'Guerilla') for t in steps]
    
    plt.plot(steps, Army_soldiers4, label='Regular Army', color='blue')
    plt.plot(steps, Guerilla_soldiers4, label='Guerilla', color='red')
    plt.title('Scenario 4: Terrain Advantage')
    plt.xlabel('Time Step')
    plt.ylabel('Soldiers')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.suptitle('Ambush Scenarios: Soldier Casualties Comparison', fontsize=16)
    plt.show()


if __name__ == "__main__":
    plot_example()