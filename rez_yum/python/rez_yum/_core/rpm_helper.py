def download_installed_rpms(name, path):
    with _keep_argv(["yumdownloader", "--source", name, "--destdir", directory]):
        yumdownloader.YumDownloader()
