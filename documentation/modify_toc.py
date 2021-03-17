from pathlib import Path
import os

source_folder = Path(__file__).parent / "source"
source_list = [
    file_path for file_path in source_folder.iterdir() if file_path.suffix == ".rst"
]

for source in source_list:
    output_path = source.parent / (source.name + ".new")
    with open(source, "r") as input_file:
        with open(output_path, "w") as output_file:
            first_line = True
            delete_next_line = False
            inside_module = False
            for line in input_file.readlines():
                if first_line:
                    new_line = line.split(" ")[0].split(".")[-1] + "\n"
                    first_line = False
                elif delete_next_line:
                    new_line = ""
                    delete_next_line = False
                elif line.startswith(("Submodules", "Module contents", "Subpackages")):
                    new_line = ""
                    delete_next_line = True
                elif "undoc-members" in line:
                    new_line = ""
                # elif line.startswith(".. automodule::"):
                #     inside_module = True
                #     new_line = line
                # elif inside_module:
                #     print(f"{line=}")
                #     if line == "":
                #         new_line = "   :exclude-members: DoesNotExist\n"
                #         inside_module = False
                #     else:
                #         new_line = line
                else:
                    new_line = line
                output_file.write(new_line)
            output_file.write("   :exclude-members: DoesNotExist, staticMetaObject")
    os.remove(str(source.absolute()))
    os.rename(str(output_path.absolute()), str(source.absolute()))
