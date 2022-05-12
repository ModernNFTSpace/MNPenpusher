from typing import Iterator, Optional, Sequence

import yaml
import os
import re

DEFAULT_PATTERN = r".+\.(?!(py.*|yaml)$)([^.]+$)"


def infinity_range(start_from: int = 0) -> Iterator:
    while True:
        yield start_from
        start_from += 1


def get_files_in_dir(dir_for_scan: str, gen_abs_path: bool = True, pattern: str = DEFAULT_PATTERN, id_gen: Iterator = infinity_range()) -> dict:
    """
    Recursively grab assets data, and store it in dict

    :param dir_for_scan: Parent directory for searching files
    :param gen_abs_path: If True, "path" key will be appear in dicts
    :param pattern: Pattern for grabbing files
    :param id_gen: Generator for "id" key
    :return: Dict containing data of assets, which was located in :dir_for_scan:
    """
    with os.scandir(dir_for_scan) as d:
        data_dict = {}

        entry: os.DirEntry
        for entry in d:
            if entry.is_dir():
                data_dict.update(get_files_in_dir(entry.path, gen_abs_path, pattern, id_gen))
            elif re.fullmatch(pattern, entry.name):
                name_without_ext = entry.name.rsplit('.', 1)[0]
                asset_data = \
                    {
                        "id": next(id_gen),
                        "file_name": entry.name
                    }
                if gen_abs_path:
                    asset_data["path"] = os.path.abspath(entry.path)

                data_dict[name_without_ext] = asset_data

        return data_dict


def collect_assets_in_dir(directory: str, pattern: str = DEFAULT_PATTERN, manifest_file_name: str = "0manifest.yaml", override_manifest_dest: Optional[str] = None) -> None:
    """
    Generate manifest file, which contain "meta" data of assets. Manifest will be created in :directory: or in :override_manifest_dest: if specified

    :param directory: Directory for grabbing assets
    :param pattern: Pattern for filtering assets by name and(or) extension. Opensea only support this MIME types: image/*,video/*,audio/*,webgl/*,.glb,.gltf
    :param manifest_file_name: Name of the manifest containing file
    :param override_manifest_dest: Absolute/relative path. If specified, manifest will be created here
    """

    assets_data_dict = get_files_in_dir(directory, gen_abs_path=True, pattern=pattern)
    manifest_data = \
        {
            "assets_data": assets_data_dict,
            "assets_count": len(assets_data_dict)
        }

    with open(os.path.join(override_manifest_dest or directory, manifest_file_name), "w") as f:
        yaml.dump(manifest_data, f)


def main(args: Optional[Sequence[str]] = None):
    """Run as standalone"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to dir for grabbing", required=True)
    parser.add_argument("--manifest-name", help="Name for manifest file", default="0manifest.yaml")
    parser.add_argument("--manifest-dir",
                        help="Override manifest destination dir. By default stored in the directory specified by '--path'", default=None)
    arguments = parser.parse_args(args)
    collect_assets_in_dir(arguments.path, manifest_file_name=arguments.manifest_name, override_manifest_dest=arguments.manifest_dir)


if __name__ == "__main__":
    main()
