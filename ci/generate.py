"""Generate child pipeline YAML at runtime.

--mode child       one test job per component under services/, a compat matrix, an optional package job,
                   and a job that generates and triggers a grandchild pipeline
--mode grandchild  one job per component
GENERATE_DEPLOY=false drops the package job (conditional generation).
"""
import argparse
import os


def components():
    return sorted(d for d in os.listdir("services") if os.path.isdir(os.path.join("services", d)))


def child():
    out = [
        "default:",
        "  image: python:3.12-alpine",
        "",
        "stages: [test, package, nested-gen, nested-run]",
        "",
    ]
    for comp in components():
        out += [
            "child-test:%s:" % comp,
            "  stage: test",
            "  script:",
            "    - python3 -m unittest discover -s services/%s" % comp,
            "",
        ]
    out += [
        "child-compat:",
        "  stage: test",
        "  parallel:",
        "    matrix:",
        "      - PLATFORM: [linux, windows-sim]",
        "  script:",
        "    - echo \"compat check on $PLATFORM\"",
        "",
    ]
    if os.environ.get("GENERATE_DEPLOY", "true") == "true":
        out += [
            "child-package:",
            "  stage: package",
            "  script:",
            "    - echo \"packaging %s\"" % " ".join(components()),
            "",
        ]
    out += [
        "nested-gen:",
        "  stage: nested-gen",
        "  script:",
        "    - python3 ci/generate.py --mode grandchild > grandchild.yml",
        "    - cat grandchild.yml",
        "  artifacts:",
        "    paths: [grandchild.yml]",
        "",
        "nested-run:",
        "  stage: nested-run",
        "  needs: [nested-gen]",
        "  trigger:",
        "    include:",
        "      - artifact: grandchild.yml",
        "        job: nested-gen",
        "    strategy: depend",
    ]
    return out


def grandchild():
    out = ["default:", "  image: alpine:3.20", ""]
    for comp in components():
        out += [
            "grandchild:%s:" % comp,
            "  script:",
            "    - echo \"grandchild job for %s\"" % comp,
            "",
        ]
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["child", "grandchild"], required=True)
    args = parser.parse_args()
    lines = child() if args.mode == "child" else grandchild()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
