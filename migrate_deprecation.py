__author__ = 'alberto'
import os
import sys
from difflib import unified_diff

MIGRATIONS = [
    ("aliases", "indices.aliases"),
    ("status", "indices.status"),
    ("create_index", "indices.create_index"),
    ("create_index_if_missing", "indices.create_index_if_missing"),
    ("delete_index", "indices.delete_index"),
    ("exists_index", "indices.exists_index"),
    ("delete_index_if_exists", "indices.delete_index_if_exists"),
    ("get_indices", "indices.get_indices"),
    ("get_closed_indices", "indices.get_closed_indices"),
    ("get_alias", "indices.get_alias"),
    ("change_aliases", "indices.change_aliases"),
    ("add_alias", "indices.add_alias"),
    ("delete_alias", "indices.delete_alias"),
    ("set_alias", "indices.set_alias"),
    ("close_index", "indices.close_index"),
    ("open_index", "indices.open_index"),
    ("flush", "indices.flush"),
    ("refresh", "indices.refresh"),
    ("optimize", "indices.optimize"),
    ("analyze", "indices.analyze"),
    ("gateway_snapshot", "indices.gateway_snapshot"),
    ("put_mapping", "indices.put_mapping"),
    ("get_mapping", "indices.get_mapping"),
    ("delete_mapping", "indices.delete_mapping"),
    ("get_settings", "indices.get_settings"),
    ("update_settings", "indices.update_settings"),

    # ("index_stats", "indices.index_stats"),
    # ("put_warmer", "indices.put_warmer"),
    # ("get_warmer", "indices.get_warmer"),
    # ("delete_warmer", "indices.delete_warmer"),
    # update_mapping_meta
    ("cluster_health", "cluster.health"),
    ("cluster_state", "cluster.state"),
    ("cluster_nodes", "cluster.nodes"),
    ("cluster_stats", "cluster.stats"),
]

filenames = [filename for filename in os.listdir("tests") if filename.endswith(".py")]
for filename in filenames:
    print "processing", filename
    path = os.path.join("tests", filename)
    ndata = data = open(path).read()
    for old_name, new_name in MIGRATIONS:
        pos = ndata.find(old_name + "(")
        if ndata[pos - 1] != '.':
            pos = ndata.find(old_name, pos + 1)
            continue
        prefix = new_name.split(".")[0]
        while pos != -1:
            #check if already fixed
            ppos = pos - len(prefix) - 1
            if ppos > 0 and ndata[ppos:pos] == "." + prefix:
                pos = ndata.find(old_name, pos + 1)
                continue
            ndata = ndata[:pos] + new_name + ndata[pos + len(old_name):]
            pos = ndata.find(old_name, pos + len(new_name))
    if data != ndata:
        for line in unified_diff(data.splitlines(1), ndata.splitlines(1), fromfile=path, tofile=path):
            sys.stdout.write(line)
        with open(path, "wb") as fo:
            fo.write(ndata)