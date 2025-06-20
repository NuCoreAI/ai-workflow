import itertools
from dataclasses import dataclass

from llm_tap import llm
from llm_tap import models as tap_models
from llm_tap.models import (
    Place,
    Workflow,
    TokenType,
    register_place,
    get_places,
    places_str,
    clear,
)

from .iox.node import Node
from .iox.profile import Profile
from .iox.loader import load_profile, load_nodes


tap_models.SOURCE = "sensor"
tap_models.SINK = "command"

system_prompt = """
You are given a set of sensors and commands.

The user needs to map his query to some kind of pseudo code.

Checklist:
- set sensors and commands that are relevant to the query
- set values (discrete, continuous) based on the query
- set conditions based on the query

"""


def make_places(node):
    if not node.node_def:
        return

    for prop in node.node_def.properties:
        if not prop.editor:
            print(f"No editor set for propery {prop}")
            continue

        if not prop.editor.ranges:
            print(f"No ranges set for editor {prop.editor}")
            continue

        description = str(prop.editor.ranges[0])
        property_uom = prop.editor.ranges[0].uom
        value_type = "INT" if property_uom.id == "25" else "FLOAT"
        token_type = TokenType(name=prop.name, type=value_type)

        register_place(
            Place(
                name=node.name,
                description=description,
                type=tap_models.SOURCE,
                token_type=token_type,
            )
        )

    for cmd in node.node_def.cmds.accepts:
        for param in getattr(cmd, "parameters", []):
            if (
                not hasattr(param, "editor")
                or not param.editor
                or not param.editor.ranges
            ):
                continue
            editor_range = param.editor.ranges[0]

            # Choose INT/FLOAT based on uom
            uom = editor_range.uom

            # Improve logic here (if prec = 0, step = 1 => INT)
            if uom.id == "25" or (
                getattr(editor_range, "step", 0) == 1
                and getattr(editor_range, "prec", -1) == 0
            ):
                value_type = "INT"
            else:
                value_type = "FLOAT"

            token_type = TokenType(name=cmd.name, type=value_type)

            register_place(
                Place(
                    name=node.name,
                    description=f"{cmd.name or cmd.id} ({editor_range})",
                    type=tap_models.SINK,
                    token_type=token_type,
                )
            )


@dataclass
class Builder:
    profile: Profile
    nodes: list[Node]

    workflow_llm_model: str = "qwen3-4b"
    reranker_model: str = "bge-reranker-v2-m3"

    @classmethod
    def from_file(cls, profile_path, nodes_path):
        profile = load_profile(profile_path)
        nodes = load_nodes(nodes_path, profile=profile)
        return cls(profile=profile, nodes=nodes)

    def __post_init__(self):
        self._name_to_place = {}

    def get_places(self, names):
        return [self._name_to_place[name] for name in names]

    def place_registry(self, nodes=None, places=None):
        class RegistryContext:
            def __enter__(s):
                if not places:
                    for node in nodes:
                        make_places(node)
                else:
                    [register_place(p) for p in places]

                self._name_to_place.update({str(n): n for n in get_places()})
                return s

            def __exit__(s, exc_type, exc_val, exc_tb):
                clear()

        return RegistryContext()

    def most_relevant_places(self, query):
        reranker = llm.LLamaCPP(
            reranker_model=self.reranker_model,
            n_ctx=4_000,
        )

        with reranker as r:
            places = get_places()
            place_names = places_str()
            scores = r.rank(query, place_names)
            results = zip(places, scores)
            results = sorted(results, key=lambda t: t[1], reverse=True)
            top = sorted(
                itertools.islice(results, 12),
                key=lambda t: t[0].type,
                reverse=True,
            )
            return [p for p, _ in top]

    def retrieve_relevant_places(self, query):
        with self.place_registry(nodes=self.nodes):
            places = self.most_relevant_places(query)
            return places

    def generate_workflow(self, query):
        print("Identifying relevant nodes...")
        places = self.retrieve_relevant_places(query)

        print("Found:")
        for p in places:
            print(f"- {p}")

        with self.place_registry(places=places):
            prompt = "\n".join(
                (
                    "\n\n----\n\n".join([place.details() for place in places]),
                    "----",
                    "====",
                    f"Query: {query}",
                    "Convert the query into a workflow (inputs => conditions => output)",
                )
            )

        generator_model = llm.LLamaCPP(
            model=self.workflow_llm_model,
            n_ctx=8_000,
        )

        print("Building workflow...")
        with self.place_registry(places=places):
            with generator_model as workflow_builder:
                workflow = workflow_builder.parse(
                    data_class=Workflow,
                    prompt=prompt,
                    system_prompt=system_prompt,
                )
                workflow.print()
                return workflow
