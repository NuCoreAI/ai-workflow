import itertools
from dataclasses import dataclass, field

from llm_tap import llm
from llm_tap import models as tap_models
from llm_tap.models import (
    Place,
    Workflow,
    Condition,
    TransitionSet,
    TokenType,
    register_place,
    get_places,
    places_str,
    is_source,
    is_sink,
    clear,
    instructions,
)

from .iox.node import Node
from .iox.profile import Profile
from .iox.loader import load_profile, load_nodes


tap_models.SOURCE = "sensor"
tap_models.SINK = "command"


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

    workflow_llm_model: str = "qwen3-1.7b"
    llm_model: str = "qwen3-1.7b"
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

        places = get_places()
        place_names = places_str()

        with reranker as r:
            scores = r.rank(query, place_names)
            results = zip(places, scores)
            results = sorted(results, key=lambda t: t[1], reverse=True)
            at_least_10_at_most_10_percent = max(10, int(10 / len(places)))
            top_10 = itertools.islice(results, at_least_10_at_most_10_percent)
            return [p for p, _ in top_10]

    def build_conditions(self, query, places):
        generator_model = llm.LLamaCPP(
            model=self.llm_model,
            n_ctx=4_000,
        )

        with self.place_registry(places=places):
            with generator_model as condition_builder:
                for place in filter(is_source, places):
                    prompt = "\n".join(
                        (
                            f"query: {query}",
                            f"place: {place.name}, {place.description}",
                            "Identify condition applicable to query and place",
                        )
                    )
                    condition = condition_builder.parse(
                        data_class=Condition,
                        prompt=prompt,
                    )
                    yield place, condition

    def build_place_set_class(self, query):
        with self.place_registry(nodes=self.nodes):
            places = self.most_relevant_places(query)

            sensors = list(filter(is_source, places))
            sensor_names = set(map(str, sensors))
            commands = list(filter(is_sink, places))
            command_names = set(map(str, commands))

            @dataclass
            class SensorSelector:
                name: str = field(metadata={"choices": lambda: sensor_names})

            @dataclass
            class CommandSelector:
                name: str = field(metadata={"choices": lambda: command_names})

            @dataclass
            class PlaceSet:
                sensors: list[SensorSelector]
                commands: list[CommandSelector]

            return PlaceSet

    def retrieve_relevant_places(self, query):
        PlaceSet = self.build_place_set_class(query)
        prompt = "\n".join(
            (
                f"query: {query}",
                "Identify all inputs and outputs relevant to the query.",
            )
        )
        generator_model = llm.LLamaCPP(
            model=self.llm_model,
            n_ctx=4_000,
        )
        with generator_model as place_set_builder:
            place_set = place_set_builder.parse(
                data_class=PlaceSet,
                prompt=prompt,
                system_prompt=instructions,
            )

        query_node_names = map(
            lambda p: p.name, place_set.sensors + place_set.commands
        )
        places = self.get_places(query_node_names)
        return places

    def generate_workflow(self, query):
        places = self.retrieve_relevant_places(query)
        prompt = "\n".join(
            (
                f"query: {query}",
                "Accurately convert the query into a workflow.",
            )
        )

        generator_model = llm.LLamaCPP(
            model=self.workflow_llm_model,
            n_ctx=4_000,
        )

        with self.place_registry(places=places):
            with generator_model as workflow_builder:
                workflow = workflow_builder.parse(
                    data_class=Workflow,
                    prompt=prompt,
                )

            workflow_places = list(filter(lambda p: p in workflow, places))
            for p, c in self.build_conditions(query, workflow_places):

