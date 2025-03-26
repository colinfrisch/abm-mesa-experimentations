import os
import sys
import argparse
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
    "situation": Slider("Situation (0 = regular, 1=Ambush)", 0, 0, 1, 1),
    "starting_personnel_army": Slider("Initial personnel for army", 100, 1, 150),
    "army_fire_power": Slider("Fire power for the army", 0.5, 0, 1, 0.1),
    "army_sight": Slider("Army sight range", 2, 1, 5),
    "starting_personnel_guerilla": Slider("Initial personnel for guerilla", 50, 1, 150),
    "guerilla_fire_power": Slider("Fire power for the guerilla", 0.5, 0, 1, 0.1),
    "guerilla_sight": Slider("Guerilla sight range", 2, 1, 5),

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
