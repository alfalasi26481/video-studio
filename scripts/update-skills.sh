#!/usr/bin/env bash
# يحدّث السكلز المنسوخة من المصادر الأصلية
set -e
T=$(mktemp -d)
git clone --depth 1 https://github.com/anthropics/skills $T/a
git clone --depth 1 https://github.com/remotion-dev/skills $T/r
git clone --depth 1 https://github.com/obra/superpowers $T/s
cd "$(dirname "$0")/../.claude/skills"
for k in docx pptx xlsx pdf canvas-design skill-creator mcp-builder frontend-design; do rm -rf $k; cp -r $T/a/skills/$k .; done
for k in best-practices captions create docs markup multimedia render studio; do rm -rf remotion-$k; cp -r $T/r/skills/remotion-$k .; done
for k in brainstorming writing-plans executing-plans systematic-debugging test-driven-development verification-before-completion; do rm -rf $k; cp -r $T/s/skills/$k .; done
rm -rf $T; echo "done"
