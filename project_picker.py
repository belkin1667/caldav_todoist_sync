from todoist_api_python.api import TodoistAPI

todoist_token =
todoist = TodoistAPI(todoist_token)


class Project:
    id = str
    name = str
    parent_id = str
    children_ids = [str]

    def __init__(self, project):
        self.id = project.id
        self.parent_id = project.parent_id
        self.name = project.name
        self.children_ids = []

    def add_child(self, child):
        self.children_ids.append(child.id)


def ptree(parent, tree, projects_dict, indent=''):
    parent_name = ''
    if parent is not None:
        parent_proj = projects_dict[parent]
        parent_name = parent_proj.name
        print(parent_name, 'id:', parent_proj.id)

    if parent not in tree:
        return

    shift = len(parent_name)
    indent += ' ' * shift

    for child in tree[parent][:-1]:
        print(indent + '|' + '-' * 4, end='')
        ptree(child, tree, projects_dict, indent + '|' + ' ' * 4)

    child = tree[parent][-1]
    print(indent + '`' + '-' * 4, end='')
    ptree(child, tree, projects_dict, indent + ' ' * 4)


def display_projects():
    print('Downloading projects...')
    projects = todoist.get_projects()
    print(len(projects), 'loaded')
    projects_dict = {}

    for proj in projects:
        projects_dict[proj.id] = Project(proj)
    for proj in projects_dict.values():
        if proj.parent_id is not None:
            projects_dict[proj.parent_id].add_child(proj)
    tree_dict = {}
    roots = []
    for proj in projects_dict.values():
        if len(proj.children_ids) > 0:
            tree_dict[proj.id] = proj.children_ids
        if proj.parent_id is None:
            roots.append(proj.id)
    tree_dict[None] = roots

    ptree(None, tree_dict, projects_dict)


display_projects()
