# tinylogdir

> A lightweight library for creating output directories of python scripts.

#### Why not just `os.makedirs`?

1. *tinylogdir* handles **existing directories** gracefully by prompting the user to append a timestamp or counter to the directory name, or by deleting the existing directory.
    1. *Use case*: Calling a script with the same output path multiple times, and creating multiple timestamped directories.
3. *tinylogdir* stores information about the **calling environment** in `tinylogdir.yaml`.
    1. *Use case*: Identifying the process, user and hostname for the script of a given logging directory.
    2. *Use case*: Reproducing the context in which the script was called, e.g. the exact command, environment variables, git commit and [diff](https://git-scm.com/docs/git-diff) (if script is part of a git repository).

#### Installation

```bash
pip install tinylogdir
```

## Usage

```python
import argparse, tinylogdir

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=str, required=True)
args = parser.parse_args()

log = tinylogdir.LogDir(args.output)
```

This creates the given logging directory and a file `tinylogdir.yaml` that looks like:

```yaml
cmd: /home/foo/myrepository/myscript.py --output /home/foo/mylogdir
cwd: /home/foo/myrepository
environ:
  CUDA_VISIBLE_DEVICES: '0'
  STY: 4144356.pts-3.pc123-serverroom
git:
  commit: f0efbbada057bf68f8cc7a8e2aa315e65ce93f910
  path: /home/foo/myrepository
hostname: pc123-serverroom
pid: 414276
time: '2021-04-20T12:31:17'
user: myusername
```

If the calling script is part of a git repository, this also creates the file `gitdiff.patch` with the results of a call to [git diff](https://git-scm.com/docs/git-diff) that allows reproducing the state of the repository (tracked files) at the time the script was called.

## Notes

- A default mode for handling existing directories can be passed to the constructor as `tinylogdir.LogDir(args.output, mode="t")` with values in `["d", "delete", "t", "timestamp", "c", "counter"]`.
- The function `log.dir("results-123/test")` can be used to create subdirectories and return the absolute path as string.