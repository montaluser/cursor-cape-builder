#!/bin/zsh
set -euo pipefail

project_dir="${0:A:h:h}"
app_path="$project_dir/dist/Cursor Cape Builder.app"
icon_path="$project_dir/build/AppIcon.icns"

rm -rf "$project_dir/build" "$app_path"
mkdir -p "$app_path/Contents/MacOS" "$app_path/Contents/Resources"

python3 "$project_dir/scripts/build-icon.py" "$project_dir/build/AppIcon.png" "$icon_path"

clang -fobjc-arc -framework Cocoa "$project_dir/src/CursorCapeBuilderApp.m" \
  -o "$app_path/Contents/MacOS/CursorCapeBuilder"
cp "$project_dir/src/Info.plist" "$app_path/Contents/Info.plist"
cp "$project_dir/src/CursorCapeBuilder.py" "$app_path/Contents/Resources/CursorCapeBuilder.py"
cp "$project_dir/src/CursorCapeBuilder.template.cape" "$app_path/Contents/Resources/CursorCapeBuilder.template.cape"
cp "$icon_path" "$app_path/Contents/Resources/AppIcon.icns"
codesign --force --deep --sign - "$app_path"
codesign --verify --deep --strict --verbose=2 "$app_path"
plutil -lint "$app_path/Contents/Info.plist"
print "Built: $app_path"
