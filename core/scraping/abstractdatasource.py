import json


def add_to_gitignore(file_path):
    gitignore_path = ".gitignore"

    try:
        with open(gitignore_path, "r") as gitignore_file:
            lines = gitignore_file.readlines()
    except FileNotFoundError:
        lines = []
    file_to_add = file_path
    if file_to_add + "\n" not in lines:
        lines.append("\n" + file_to_add + "\n")
        print(f"Added '{file_to_add}' to .gitignore")
    else:
        print(f"'{file_to_add}' is already in .gitignore.")
    with open(gitignore_path, "w") as gitignore_file:
        gitignore_file.writelines(lines)


class AbstractDataSource:
    URL = ""

    def scrape_page(self):
        raise NotImplementedError

    def parse_event(self, ev):
        raise NotImplementedError

    def get_events(self):
        events = self.scrape_page()
        return [self.parse_event(ev) for ev in events]

    def save(self, evs):
        print("moments before disaster", evs)
        file_name = f"{self.__class__.__name__}.json"
        add_to_gitignore(file_name)
        with open(file_name, "w") as json_file:
            json.dump(evs, json_file, indent=4)
