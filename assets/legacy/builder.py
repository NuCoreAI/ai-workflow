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

from iox.node import Node
from iox.profile import Profile
from iox.loader import load_profile, load_nodes
from iox.editor import EditorMinMaxRange, EditorSubsetRange


tap_models.SOURCE = "sensor"
tap_models.SINK = "command"

system_prompt = """You are given a set of sensors and commands.

Map queries to workflows:

- Sensor 1
- Sensor < n >

IF:

< condition 1 on sensor 1 >
< condition n on sensor n >

TRANSITION

< state change >

Checklist:
- Select sensors and commands relevant to the query
- Define values based on the query
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
        editor_range = prop.editor.ranges[0]
        property_uom = prop.editor.ranges[0].uom

        if isinstance(editor_range, EditorSubsetRange):
            value_type = "DISCRETE"
            sub_type = int
            if editor_range.names:
                token_range = tuple(
                    [f"{v}" for k, v in editor_range.names.items()]
                )

        elif isinstance(editor_range, EditorMinMaxRange):
            value_type = "NUMERIC"

            if property_uom.id == "25":
                sub_type = int
            else:
                sub_type = float

            if editor_range.names:
                token_range = tuple(
                    [f"{v}" for k, v in editor_range.names.items()]
                )
                value_type = "DISCRETE"
            else:
                token_range = (editor_range.min, editor_range.max)

        token_type = TokenType(prop.name, value_type, token_range, sub_type)

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

            if isinstance(editor_range, EditorSubsetRange):
                value_type = "DISCRETE"
                sub_type = int
                if editor_range.names:
                    token_range = tuple(
                        [f"{v}" for k, v in editor_range.names.items()]
                    )

            elif isinstance(editor_range, EditorMinMaxRange):
                value_type = "NUMERIC"

                if property_uom.id == "25":
                    sub_type = int
                else:
                    sub_type = float

                if editor_range.names:
                    token_range = tuple(
                        [f"{v}" for k, v in editor_range.names.items()]
                    )
                    value_type = "DISCRETE"
                else:
                    token_range = (editor_range.min, editor_range.max)

            token_type = TokenType(cmd.name, value_type, token_range, sub_type)

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

    workflow_llm_model: str = "qwen3-1.7b"
    reranker_model: str = "bge-reranker-v2-m3"
    max_ranking_results: int = 10

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
                itertools.islice(results, self.max_ranking_results),
                key=lambda t: t[0].type,
                reverse=True,
            )
            return [p for p, _ in top]

    def retrieve_relevant_places(self, query):
        with self.place_registry(nodes=self.nodes):
            places = self.most_relevant_places(query)
            return places

    def generate_workflow(self, query):
        context_size = 8_000
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
                    "",
                    f"Query: {query}",
                    "Convert the Query",
                )
            )

        generator_model = llm.LLamaCPP(
            model=self.workflow_llm_model,
            n_ctx=context_size,
        )

        print("Building workflow...")
        with self.place_registry(places=places):
            with generator_model as workflow_builder:
                workflow = workflow_builder.parse(
                    data_class=Workflow,
                    prompt=prompt,
                    system_prompt=system_prompt,
                )
                return workflow
