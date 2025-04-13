import os
import sys
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle
import matplotlib.colors as mcolors

from model import ForagingAntsModel
from agents import ForagingAnt, Food

sys.path.insert(0, os.path.abspath("../../mesa"))

from mesa.visualization import Slider, SolaraViz, make_space_component

# Pre-compute markers for different angles (e.g., every 10 degrees)
MARKER_CACHE = {}
for angle in range(0, 360, 10):
    ant_marker = MarkerStyle(5)
    ant_marker._transform = ant_marker.get_transform().rotate_deg(angle)
    MARKER_CACHE[angle] = ant_marker

food_marker = MarkerStyle("*")
MARKER_CACHE["food"] = food_marker

def agent_portrayal(agent):
    """Portray an agent for visualization."""
    portrayal = {}
    
    if isinstance(agent, ForagingAnt):
        # Calculate the angle
        deg = agent.angle
        # Round to nearest 10 degrees
        rounded_deg = round(deg / 10) * 10 % 360
        
        portrayal["marker"] = MARKER_CACHE[rounded_deg]
        portrayal["size"] = 30
        
        if agent.mode == "explore":
            # Black if exploring
            portrayal["color"] = "black"
            portrayal["layer"] = 1
            

        elif agent.mode == "go_to_food" :
            # red if found food
            portrayal["color"] = "purple"
            portrayal["layer"] = 2
        
        elif agent.mode == "return_to_colony":
            # brown if returning to colony
            portrayal["color"] = "blue"
            portrayal["layer"] = 3

            
    elif isinstance(agent, Food):
        portrayal["marker"] = MARKER_CACHE["food"]
        portrayal["size"] = 50
        portrayal["color"] = "green"
        portrayal["filled"] = True
        portrayal["layer"] = 0
    
        
    return portrayal


# Add a special circle to represent the colony
def space_drawer(ax):
    """Draw additional elements on the space."""
    # Draw the colony as a circle at the center
    colony = plt.Circle(
        (5, 5), 
        5.0, 
        color="grey", 
        alpha=0.3
    )
    ax.add_patch(colony)


# Setup model parameters for the visualization interface
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": 100,
    "height": 100,
    "initial_ants": Slider(
        label="Number of ants",
        value=30,
        min=5,
        max=60,
        step=10,
    ),
    "speed": Slider(
        label="Speed of Ants",
        value=1,
        min=0.5,
        max=5,
        step=0.5,
    ),
    "range_of_communication": Slider(
        label="Range of Communication",
        value=2,
        min=1,
        max=15,
        step=1,
    ),
    "initial_food": Slider(
        label="Number of food sources",
        value=10,
        min=1,
        max=20,
        step=1,
    ),
    "ants_needed": Slider(
        label="Ants Needed for Food Collection",
        value=3,
        min=1,
        max=10,
        step=1,
    ),
}

# Create model instance for visualization
model = ForagingAntsModel()



# Create the visualization page
page = SolaraViz(
    model,
    components=[
        make_space_component(
            agent_portrayal=agent_portrayal, 
            backend="matplotlib",
            post_process=space_drawer
        )
    ],
    model_params=model_params,
    name="Foraging Ants Model",
)

page  # noqa
