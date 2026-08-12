#!/bin/zsh
set -euo pipefail

project_dir="${0:A:h:h}"
zsh "$project_dir/scripts/build-app.sh"
mkdir -p "$project_dir/release"
release_path="$project_dir/release/Cursor-Cape-Builder-macOS.zip"
rm -f "$release_path"
(cd "$project_dir/dist" && /usr/bin/zip -r -X -q "$release_path" "Cursor Cape Builder.app")
print "Release archive: $project_dir/release/Cursor-Cape-Builder-macOS.zip"
