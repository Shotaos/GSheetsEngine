import os
import json

def search_ue_projects(root_path=None):
    ue_projects = []
    drives = []

    if root_path is None:
        if os.name == 'nt':
            drives.append('c:/')
        elif os.name =='posix':
            drives.append('/')
    else:
        drives.append(root_path)

    for drive in drives:

        for root, dirs, files in os.walk(drive):

            # Look for .uproject file in current directory
            for _file in files:
                if _file.endswith('.uproject'):
                    # Parse .uproject to get the project name
                    try:
                        with open(os.path.join(root, _file)) as f:
                            uproject = json.load(f)
                            # Make assumption that first module name is the project name
                            name = uproject["Modules"][0]["Name"]
                            ue_projects.append((name, root))

                    except (json.JSONDecodeError, KeyError, IndexError):
                        pass

    return ue_projects
            

