# This class manages nodes/profiles/programs in the nucore platform


import json
import logging
import argparse
import xml.etree.ElementTree as ET


from ai_iox_workflow.iox.loader import load_nodes
from ai_iox_workflow.iox.profile import Profile, Family, Instance
from ai_iox_workflow.iox.editor import Editor, EditorSubsetRange, EditorMinMaxRange
from ai_iox_workflow.iox.linkdef import LinkDef, LinkParameter
from ai_iox_workflow.iox.nodedef import NodeDef, NodeProperty, NodeCommands, NodeLinks
from ai_iox_workflow.iox.node import TypeInfo, Property, Node
from ai_iox_workflow.iox.cmd import Command, CommandParameter
from ai_iox_workflow.iox.uom import get_uom_by_id
from ai_iox_workflow.iox.nucore_api import nucoreAPI
from ai_iox_workflow.rag.device_rag_formatter import DeviceRagFormatter
from ai_iox_workflow.rag.tools_rag_formatter import ToolsRAGFormatter
from ai_iox_workflow.rag.rag_processor import RAGProcessor
from ai_iox_workflow.config import AIConfig


logger = logging.getLogger(__name__)
config = AIConfig()

class NuCoreError(Exception):
    """Base exception for nucore backend errors."""
    pass


def debug(msg):
    logger.debug(f"[PROFILE FORMAT ERROR] {msg}")


class NuCore:
    """Class to handle nucore backend operations such as loading profiles and nodes."""
    def __init__(self, profile_path=None, nodes_path=None, url=None, username=None, password=None):
        self.profile_path = profile_path
        self.nodes_path = nodes_path
        self.url = url
        self.username = username
        self.password = password
        if self.url:
            if not self.username or not self.password:
                raise NuCoreError("Username and password must be provided when using URL.")
        elif not self.profile_path and not self.nodes_path: 
            raise NuCoreError("Both profile_path and nodes_path must be provided.")
        self.profile = None
        self.nodes = [] 
        self.lookup = {}

    def __load_profile_from_file__(self):
        """Load profile from the specified file path."""
        if not self.profile_path:
            raise NuCoreError("Profile path is not set.")
        with open(self.profile_path, "rt", encoding="utf8") as f:
            raw = json.load(f)
        return self.__parse_profile__(raw)
    
    def __load_profile_from_url__(self):
        """Load profile from the specified URL."""
        if not self.url:
            raise NuCoreError("URL is not set.")
        if not self.username or not self.password:
            raise NuCoreError("Username and password must be provided for URL access.")

        nucore_api = nucoreAPI(base_url=self.url, username=self.username, password=self.password)
        response = nucore_api.get_profiles()
        if response is None:
            raise NuCoreError("Failed to fetch profile from URL.")
        return self.__parse_profile__(response) 

    def __parse_profile__(self, raw):
        """Build Profile from dict, with type/checking and lookups"""
        families = []
        for fidx, f in enumerate(raw.get("families", [])):
            # Validate keys / format
            if "id" not in f:
                debug(f"Family {fidx} missing 'id'")
            instances = []
            for iidx, i in enumerate(f.get("instances", [])):
                # Build Editors for reference first
                editors_dict = {}
                for edict in i.get("editors", []):
                    if "id" not in edict:
                        debug("Editor missing 'id'")
                        continue
                    editors_dict[edict["id"]] = self.__build_editor__(edict)
                # Build LinkDefs
                linkdefs = []
                for ldict in i.get("linkdefs", []):
                    # parameters resolution below
                    params = []
                    for p in ldict.get("parameters", []):
                        if "editor" not in p:
                            debug(f"LinkDef param missing 'editor': {p}")
                            continue
                        eid = p["editor"]
                        editor = editors_dict.get(eid)
                        if not editor:
                            debug(f"Editor '{eid}' not found for linkdef param")
                        params.append(
                            LinkParameter(
                                id=p["id"],
                                editor=editor,
                                optional=p.get("optional"),
                                name=p.get("name"),
                            )
                        )
                    linkdefs.append(
                        LinkDef(
                            id=ldict["id"],
                            protocol=ldict["protocol"],
                            name=ldict.get("name"),
                            cmd=ldict.get("cmd"),
                            format=ldict.get("format"),
                            parameters=params,
                        )
                    )
                # Build NodeDefs
                nodedefs = []
                for ndict in i.get("nodedefs", []):
                    # NodeProperties
                    props = []
                    for pdict in ndict.get("properties", []):
                        eid = pdict["editor"]
                        editor = editors_dict.get(eid)
                        if not editor:
                            debug(
                                f"Editor '{eid}' not found for property '{pdict.get('id')}' in nodedef '{ndict['id']}'"
                            )
                        props.append(
                            NodeProperty(
                                id=pdict["id"],
                                editor=editor,
                                name=pdict.get("name"),
                                hide=pdict.get("hide"),
                            )
                        )
                    # NodeCommands
                    cmds_data = ndict.get("cmds", {})
                    sends = []
                    accepts = []
                    for ctype, clist in [
                        ("sends", cmds_data.get("sends", [])),
                        ("accepts", cmds_data.get("accepts", [])),
                    ]:
                        for cdict in clist:
                            params = []
                            for p in cdict.get("parameters", []):
                                eid = p["editor"]
                                editor = editors_dict.get(eid)
                                if not editor:
                                    debug(
                                        f"Editor '{eid}' not found for command param"
                                    )
                                params.append(
                                    CommandParameter(
                                        id=p["id"],
                                        editor=editor,
                                        name=p.get("name"),
                                        init=p.get("init"),
                                        optional=p.get("optional"),
                                    )
                                )
                            (sends if ctype == "sends" else accepts).append(
                                Command(
                                    id=cdict["id"],
                                    name=cdict.get("name"),
                                    format=cdict.get("format"),
                                    parameters=params,
                                )
                            )
                    cmds = NodeCommands(sends=sends, accepts=accepts)
                    # NodeLinks
                    links = ndict.get("links", None)
                    node_links = None
                    if links:
                        node_links = NodeLinks(
                            ctl=links.get("ctl") or [], rsp=links.get("rsp") or []
                        )
                    # Build NodeDef
                    nodedefs.append(
                        NodeDef(
                            id=ndict["id"],
                            properties=props,
                            cmds=cmds,
                            nls=ndict.get("nls"),
                            icon=ndict.get("icon"),
                            links=node_links,
                        )
                    )
                # Final Instance
                instances.append(
                    Instance(
                        id=i["id"],
                        name=i["name"],
                        editors=list(editors_dict.values()),
                        linkdefs=linkdefs,
                        nodedefs=nodedefs,
                    )
                )
            families.append(
                Family(id=f["id"], name=f.get("name", ""), instances=instances)
            )
        return Profile(timestamp=raw.get("timestamp", ""), families=families)

    def load_profile(self):
        """Load profile from the specified path or URL."""
        if self.profile_path :
            self.profile = self.__load_profile_from_file__()
        elif self.url:
            self.profile = self.__load_profile_from_url__()
        else:
            raise NuCoreError("No valid profile source provided.")
        return self.profile
        
    def __load_nodes_from_file__(self):
        """Load nodes from the specified XML file path."""
        if not self.nodes_path:
            raise NuCoreError("Nodes path is not set.")
        return ET.parse(self.nodes_path).getroot()

    def __load_nodes_from_url__(self):
        """Load nodes from the specified URL."""
        if not self.url:
            raise NuCoreError("URL is not set.")
        if not self.username or not self.password:
            raise NuCoreError("Username and password must be provided for URL access.")

        nucore_api = nucoreAPI(base_url=self.url, username=self.username, password=self.password)
        response = nucore_api.get_nodes()
        if response is None:
            raise NuCoreError("Failed to fetch nodes from URL.")
        return ET.fromstring(response)

    def __build_nodedef_lookup__(self):
        for family in self.profile.families:
            for instance in family.instances:
                for nodedef in getattr(instance, "nodedefs", []):
                    self.lookup[nodedef.id] = nodedef
        return self.lookup
    
    def __load_nodes__(self):
        """Load nodes from the specified path or URL."""
        nodes = None
        if self.nodes_path:
            nodes = self.__load_nodes_from_file__()
        elif self.url:
            nodes = self.__load_nodes_from_url__()
        else:
            raise NuCoreError("No valid nodes source provided.")
        return nodes

    def __build_editor__(self, edict) -> Editor:
        ranges = []
        for rng in edict.get("ranges", []):
            uom_id = rng["uom"]
            uom = get_uom_by_id(uom_id)
            if not uom:
                debug(f"UOM '{uom_id}' not found")
            # MinMaxRange or Subset
            if "min" in rng and "max" in rng:
                ranges.append(
                    EditorMinMaxRange(
                        uom=uom,
                        min=rng["min"],
                        max=rng["max"],
                        prec=rng.get("prec"),
                        step=rng.get("step"),
                        names=rng.get("names", {}),
                    )
                )
            elif "subset" in rng:
                ranges.append(
                    EditorSubsetRange(
                        uom=uom, subset=rng["subset"], names=rng.get("names", {})
                    )
                )
            else:
                debug(f"Range must have either min/max or subset: {rng}")
        
        return Editor(id=edict["id"], ranges=ranges)

        
    def load(self):
        if not self.load_profile():
            return None
        
        root = self.__load_nodes__()
        if root == None:
            return None

        self.__build_nodedef_lookup__()

        self.nodes = []
        for node_elem in root.findall(".//node"):
            typeinfo_elems = node_elem.findall("./typeInfo/t")
            typeinfo = [
                TypeInfo(t.get("id"), t.get("val")) for t in typeinfo_elems
            ]

            property_elems = node_elem.findall("./property")
            properties = [
                Property(
                    p.get("id"),
                    p.get("value"),
                    p.get("formatted"),
                    p.get("uom"),
                    p.get("prec"),
                    p.get("name"),
                )
                for p in property_elems
            ]
            node_def_id = node_elem.get("nodeDefId")

            node = Node(
                flag=int(node_elem.get("flag")),
                nodeDefId=node_def_id,
                address=node_elem.find("./address").text,
                name=node_elem.find("./name").text,
                family=int(node_elem.find("./family").text),
                hint=node_elem.find("./hint").text,
                type=node_elem.find("./type").text,
                enabled=(node_elem.find("./enabled").text.lower() == "true"),
                deviceClass=int(node_elem.find("./deviceClass").text),
                wattage=int(node_elem.find("./wattage").text),
                dcPeriod=int(node_elem.find("./dcPeriod").text),
                startDelay=int(node_elem.find("./startDelay").text),
                endDelay=int(node_elem.find("./endDelay").text),
                pnode=node_elem.find("./pnode").text,
                rpnode=node_elem.find("./rpnode").text
                if node_elem.find("./rpnode") is not None
                else None,
                sgid=int(node_elem.find("./sgid").text)
                if node_elem.find("./sgid") is not None
                else None,
                typeInfo=typeinfo,
                property=properties,
                parent=node_elem.find("./parent").text
                if node_elem.find("./parent") is not None
                else None,
                custom=node_elem.find("./custom").attrib
                if node_elem.find("./custom") is not None
                else None,
                devtype=node_elem.find("./devtype").attrib
                if node_elem.find("./devtype") is not None
                else None,
            )
            if self.profile and node_def_id:
                node.node_def = self.lookup.get(node_def_id)
                if not node.node_def:
                    debug(f"[WARN] No NodeDef found for: {node_def_id}")

            self.nodes.append(node)

        return self.nodes

    def __str__(self):
        if not self.profile:
            return  "N/A"
        if not self.nodes:
            return  "N/A"
        return "\n".join(str(node) for node in self.nodes)

    def json(self):
        if not self.profile:
            return None 
        if not self.nodes:
            return  None
        return [node.json() for node in self.nodes]
    
    def dump_json(self):
        return json.dumps(self.json())
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Loader for IOX Profile and Nodes XML files."
    )
    parser.add_argument(
        "--profile",
        dest="profile_path",
        type=str,
        required=False,
        help="Path to the profile JSON file (profile-xxx.json)",
    )
    parser.add_argument(
        "--nodes",
        dest="nodes_path",
        type=str,
        required=False,
        help="Path to the nodes XML file (nodes.xml)",
    )
    parser.add_argument(
        "--url",
        dest="url",
        type=str,
        required=False,
        help="The URL to fetch nodes and profiles from the nucore platform",
    )
    parser.add_argument(
        "--username",
        dest="username",
        type=str,
        required=False,
        help="The username to authenticate with the nucore platform",
    )
    parser.add_argument(
        "--password",
        dest="password",
        type=str,
        required=False,
        help="The password to authenticate with the nucore platform",
    )

    args = parser.parse_args()
    nuCore = NuCore(profile_path=args.profile_path, nodes_path=args.nodes_path, url=args.url, username=args.username, password=args.password)
    nuCore.load()
    rag_processor = RAGProcessor(config.getCollectionNameForAssistant())


    device_rag_formatter = DeviceRagFormatter(indent_str=" ", prefix="-")
    device_rag_docs = device_rag_formatter.format(nodes=nuCore.nodes) 
    #if device_rag_docs :
    #    device_rag_formatter.dump(device_rag_docs)
    
    tools_rag_formatter = ToolsRAGFormatter(indent_str=" ", prefix="-")
    tools_rag_docs =tools_rag_formatter.format(tools_path=config.getToolsFile())

    #if tools_rag_docs:
    #    tools_rag_formatter.dump(tools_rag_docs)

    all_docs = device_rag_docs + tools_rag_docs

    processed_docs = rag_processor.process(all_docs)
    rag_processor.dump()
    rerank=True
    while True:
        query = input("Query: ")
        if not query:
            print("Exiting ...")
            break  
        query_results = rag_processor.query(query, 5, rerank=rerank) 
        #device_docs_results = device_rag_processor.query(query, 5)

        if query_results:
            print(f"\n\n*********************Top 5 Query Results:(Rerank = {rerank})********************\n\n")
            for i in range(len(query_results['ids'])):
                print(f"{i+1}. {query_results['ids'][i]} - {query_results['distances'][i]} - {query_results['relevance_scores'][i]}")
            print("\n\n***************************************************************\n\n")

#    if docs:
#        for doc in docs:
#            print(f"{doc}")
#            nuCore.embed_document(doc['content']) 
#            #print(doc['content'])
#            print("\n---\n")
    #print(nuCore.dump_json()



