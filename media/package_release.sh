#!/bin/bash
# 先把 files 放入 media/ 目录，然后运行此脚本完成 commit + zip
set -e
REPO_DIR="$(pwd)"
MEDIA_DIR="media"
ZIP_NAME="openvpmd_media_bundle.zip"
git add ${MEDIA_DIR}
git commit -m "Add media assets: scenes, scripts, srt, tts scripts, build script" || true
git push origin main
# 打包
zip -r ${ZIP_NAME} ${MEDIA_DIR}
echo "打包完成: ${ZIP_NAME}"
echo "请在 GitHub Releases 页面上传 ${ZIP_NAME} 以便分发。"
