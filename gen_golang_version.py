import json
from typing import List

import requests

# Define the API endpoint URL
url = "https://go.dev/dl/?mode=json&include=all"


class File:
    def __init__(self, file: any):
        self._filename = file["filename"]
        self._arch = file["arch"]
        self._sha256 = file["sha256"]

    def __str__(self) -> str:
        return f"\tsha256: {self._sha256}, arch: {self._arch}, filename: {self._filename}\n"

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def arch(self) -> str:
        return self._arch

    @property
    def sha256(self) -> str:
        return self._sha256


class Version:
    def __init__(self, version: any):
        self._version = version["version"][2:]
        self._files = make_files(version["files"])

    def __str__(self) -> str:
        s = f"version: {self._version}\n"
        for f in self._files:
            s += f"{f}"

        return s

    @property
    def version(self) -> str:
        return self._version

    @property
    def files(self) -> List[File]:
        return self._files


def get_versions(url: str) -> str | None:
    try:
        response = requests.get(url)

        if response.status_code == 200:
            json_response = response.json()
            return json_response
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Handle any network-related errors or exceptions
        print(f"Error: {e}")
        return None


def make_files(files: any) -> list[File]:
    f_arr = []

    for file in files:
        if file["os"] == "linux" and file["arch"] in ["amd64", "arm64", "armv6l"]:
            f_arr.append(File(file))

    return f_arr


def make_versions(versions: any) -> list[Version]:
    vers = []

    for version in versions:
        if version["stable"] is True and version["version"] != "go1":
            ver = Version(version)
            vers.append(ver)

    return vers


def write_files(root, versions: list[Version]):
    for version in versions:
        for file in version.files:
            if file.sha256 is not None:
                with open(f"{root}/{version.version}-{file.arch}.yml", "w") as f:
                    f.write("---\n")
                    f.write(
                        f"# SHA256 sum for the redistributable package {file.filename}\n"
                    )
                    f.write(f"golang_redis_sha256sum: '{file.sha256}'\n")


def main():
    response = get_versions(url)

    if response is not None:
        # print(json.dumps(response, indent=4))
        versions = make_versions(response)

        write_files("./vars/versions", versions)


if __name__ == "__main__":
    main()
