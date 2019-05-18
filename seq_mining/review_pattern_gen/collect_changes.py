"""
Get Style missing from diff file
Style misses list
* Rename identifier
* Large to Small (ex:"Style" to "style")
* only make new line
* Space or Tab
* Don't changed AST
"""
import sys
from csv import DictReader
from json import dump, load
from unidiff import PatchSet, errors
from urllib.request import urlopen, Request
from configparser import ConfigParser
from CodeTokenizer.tokenizer import TokeNizer
from lang_extentions import lang_extentions

config = ConfigParser()
config.read('config')
user = config["GitHub"]["id"]
password = config["GitHub"]["password"]
owner = config["Target"]["owner"]
repo = config["Target"]["repo"]
lang = config["Target"]["lang"]
TN = TokeNizer(lang)


def main():
    """
    The main
    """
    #changes_sets = get_project_changes(owner, repo, lang)

    changes_sets = compute_changes()

    out_name = "data/changes/" + owner + "_" + repo + "_" + lang + ".json"

    with open(out_name, "w", encoding='utf-8') as f:
        dump(changes_sets, f, indent=1)


def get_project_changes(owner, repo, lang, diffs_file=None):
    changes_sets = []
    if diffs_file is None:
        diffs_file = "data/pulls/" + owner + "_" + repo + ".csv"
    with open(diffs_file, "r", encoding="utf-8") as diffs:
        reader = DictReader(diffs)
        for diff_path in reader:
            if diff_path["commit_len"] == "1":
                continue
            changes_set = curl_diffs(diff_path)
            if changes_set == []:
                continue
            changes_sets.extend(changes_set)
    return changes_sets

def compute_changes(file_path):
    diffs_file = "data/defects4j/defects4j-bugs.json"
    defects = load(diffs_file)
    for d in defects:
        for key, value in d["changedFiles"]:
            commit_len++
            out_values = {
                    "number": int(d["bugId"]),
                    #"commit_len": int(diff_path["commit_len"]),
                    #"created_at": diff_path["created_at"],
                    #"merged_at": diff_path["merged_at"],
                    #"merged_by": diff_path["merged_by"],
                    #"1-n_url": diff_path["1-n_url"],
                    "file_path": key,
                    "changes_set": TN.make_change_set(source, target)
                }
                if out_metricses["changes_set"] == -1:
                    continue
        out_values["commit_len"] = commit_len

            changes_sets.append(out_metricses)




def curl_diffs(diff_path):
    changes_sets = []

    if "Token" in config["GitHub"]:
        token = config["GitHub"]["Token"]
        diff_url = "https://api.github.com/repos/" + owner + "/" + repo + "/compare/" + diff_path["first_commit_sha"] + "..." + diff_path["merge_commit_sha"]
        request = Request(diff_url)
        request.add_header("Authorization", "token %s" % token)
        request.add_header("Accept", "application/vnd.github.v3.diff")
        try:
            url_diff = urlopen(request)
            diffs = PatchSet(url_diff, encoding="utf-8")
        except (UnicodeDecodeError, errors.UnidiffParseError):
            print("UnicodeDecodeError:" + str(diff_path))
            return []
    else:
        try:
            url_diff = urlopen(diff_path["1-n_url"])
            diffs = PatchSet(url_diff, encoding="utf-8")
        except (UnicodeDecodeError, errors.UnidiffParseError):
            print("UnicodeDecodeError:" + str(diff_path))
            return []

    filtered_diffs = [x for x in diffs
                      if x.is_modified_file
                      and any([x.path.endswith(y) for y in lang_extentions[lang]])]
    files_num = len(filtered_diffs)
    for i, diff in enumerate(filtered_diffs):
        sys.stdout.write("\r%s pulls %d / %d files" %
                         (diff_path["number"], i+1, files_num))
        for hunk in diff:
            source = "".join([x.value for x in hunk if x.is_removed])
            target = "".join([x.value for x in hunk if x.is_added])
            if source == target:
                continue
            out_metricses = {
                "number": int(diff_path["number"]),
                "commit_len": int(diff_path["commit_len"]),
                "created_at": diff_path["created_at"],
                "merged_at": diff_path["merged_at"],
                "merged_by": diff_path["merged_by"],
                "1-n_url": diff_path["1-n_url"],
                "file_path": diff.path,
                "changes_set": TN.make_change_set(source, target)
            }
            if out_metricses["changes_set"] == -1:
                continue

            changes_sets.append(out_metricses)
    return changes_sets


if __name__ == '__main__':
    main()
