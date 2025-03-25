import os
import sys
from agents import SoldierAgent
from model import GuerillaModel

mesa_path = os.path.abspath("/Users/colinfrisch/Desktop/mesa")
if mesa_path not in sys.path:
    sys.path.insert(0, mesa_path)

from mesa.experimental.devs import ABMSimulator
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)


def model_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 25,
    }

    if isinstance(agent, SoldierAgent):
        if agent.side == "Army":
            portrayal["color"] = "tab:red"
            portrayal["marker"] = "o"
            portrayal["zorder"] = 2
        elif agent.side == "Guerilla":
            portrayal["color"] = "tab:blue"
            portrayal["marker"] = "o"
            portrayal["zorder"] = 1

    return portrayal

    
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },

    "starting_personnel_army": Slider("Initial personnel for army", 20, 1, 50),
    "army_fire_power": Slider("Fire power for the army", 0.1, 0, 1, 0.1),
    "army_sight": Slider("How far can the army soliders see", 2, 1, 5),
    "starting_personnel_guerilla": Slider("Initial personnel for guerilla", 10, 1, 50),
    "guerilla_fire_power": Slider("Fire power for the guerilla", 0.1, 0, 1, 0.1),
    "guerilla_sight": Slider("How far can the guerilla soliders see", 2, 1, 5),

}


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))



space_component = make_space_component(
    model_portrayal, draw_grid=False, post_process=post_process_space
)


simulator = ABMSimulator()
model = GuerillaModel(simulator=simulator)

if model.situation == "Classic":
    ruling_equation = "LanchesterEquation"
else:
    ruling_equation = "DeitchmanEquation"

army_lineplot_component = make_plot_component(
    {"ArmySoldiers": "tab:red", f"Army{ruling_equation}":"tab:orange"},
    post_process=post_process_lines,
)
guerilla_lineplot_component = make_plot_component(
    {"GuerillaSoldiers": "tab:blue",f"Guerilla{ruling_equation}":"tab:orange"},
    post_process=post_process_lines,
)




page = SolaraViz(
    model,
    components=[space_component, army_lineplot_component,guerilla_lineplot_component],
    model_params=model_params,
    name="Guerrilla Warfare",
    simulator=simulator,
)
page 
