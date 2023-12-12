import os, sys, shutil, datetime, yaml, subprocess, time, socket, threading, getpass

class LogDir:
    """Creates a log directory and stores some information about the environment in the file path/tinylogdir.yaml.

    Parameters:
        path: The path to the log directory.
        mode: String indicating how to handle existing directories. Options: Delete (d, delete), append timestamp (t, timestamp), append counter (c, counter). Defaults to None, which prompts the user.
        environ: List of environment variables to store in the log directory. Defaults to ["CUDA_VISIBLE_DEVICES", "STY"].
        store_git_diff: If True, the git diff is stored in the log directory. Defaults to True.
    """
    def __init__(self, path, mode=None, environ=["CUDA_VISIBLE_DEVICES", "STY"], store_git_diff=True):
        if not mode in ["d", "delete", "t", "timestamp", "c", "counter"] and not mode is None:
            raise ValueError(f"Invalid mode {mode}")
        use_mode = mode
        while True:
            if use_mode == "d" or use_mode == "delete":
                if os.path.isdir(path):
                    print("Deleting directory " + path)
                    shutil.rmtree(path)
            elif use_mode == "t" or use_mode == "timestamp":
                def get_path_t():
                    return path + "-" + datetime.datetime.now().replace(microsecond=0).isoformat().replace(":", "-")
                path_t = get_path_t()
                while os.path.isdir(path_t):
                    time.sleep(0.1)
                    path_t = get_path_t()
                path = path_t
            elif use_mode == "c" or use_mode == "counter":
                c = 1
                def path_c():
                    return path + "-" + str(c)
                while os.path.isdir(path_c()):
                    c += 1
                path = path_c()
            elif not use_mode is None:
                print("Invalid option")
                use_mode = None

            try:
                os.makedirs(path)
                break
            except FileExistsError as e:
                if mode is None:
                    use_mode = input("Directory " + path + " already exists. Options: Delete (d), append timestamp (t), append counter (c)\n> ")
        assert os.path.isdir(path)
        print(f"Created directory {path}")

        self.path = path

        config = {}

        config["cmd"] = " ".join(sys.argv)
        config["cwd"] = os.getcwd()
        config["hostname"] = socket.gethostname()
        config["time"] = datetime.datetime.now().replace(microsecond=0).isoformat()
        config["pid"] = os.getpid()
        config["user"] = getpass.getuser()

        current_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        while current_path != "" and current_path != "/":
            if os.path.isdir(os.path.join(current_path, ".git")):
                out, err = subprocess.Popen("git rev-parse HEAD", stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=current_path, shell=True).communicate()
                if err != 0:
                    config["git"] = {}
                    config["git"]["path"] = current_path
                    config["git"]["commit"] = out.decode().strip()

                    if store_git_diff:
                        patch_file = os.path.join(path, "gitdiff.patch")
                        out, err = subprocess.Popen(f"git diff -p HEAD > {patch_file}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=current_path, shell=True).communicate()
                break
            current_path = os.path.dirname(current_path)

        config["environ"] = {}
        for key in environ:
            if key in os.environ:
                config["environ"][key] = os.environ[key]

        with open(os.path.join(path, "tinylogdir.yaml"), "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        self.lock = threading.Lock()

    """Returns a directory relative to the log directory. If the directory does not exist, it is created.

    Parameters:
        path: The path relative to the log directory.
        create: If true, the directory is created if it does not exist. Defaults to true.

    Returns:
        The absolute path to the directory.
    """
    def dir(self, path=None, create=True):
        if path is None:
            return self.path
        if os.path.isabs(path):
            raise ValueError(f"Path must be relative, got {path}")
        path = os.path.join(self.path, path)
        if not os.path.isdir(path):
            with self.lock:
                if os.path.isfile(path):
                    raise FileExistsError(f"Path {path} already exists and is a file")
                if not os.path.isdir(path) and create:
                    os.makedirs(path)
        return path
