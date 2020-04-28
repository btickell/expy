import subprocess

def gcp_cp(src, dst):
    cmd = "gsutil -m cp {} {}".format(src, dst)
    subprocess.run(cmd, shell=True)

def gcp_cp_dir(src, dst):
    cmd = "gsutil -m rsync -r {} {}".format(src, dst)
    subprocess.run(cmd, shell=True)

def gcp_rm_dir(d):
    cmd = "gsutil -m rm -r {}".format(d)
    subprocess.run(cmd, shell=True)