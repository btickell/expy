import click
import os
from expy.tracker import get_exp_doc
import subprocess
import multiprocessing as mp

def make_table(dict, keys, fmt="latex"):
    data_frame = {}
    for k in keys:
        data_frame[k] = dict[k]

    print(tabulate.tabulate(table, headers="keys", tablefmt=fmt))

def get_file(tup):
    fp, logdir = tup
    seed = fp.split('/results/')[0].split('/')[-1]
    subprocess.run('gsutil cp ' + fp + ' ' + os.path.join(logdir, seed), shell=True)

def pull_results_gcp(exp_name, pattern='', filter={}):
    doc = get_exp_doc(exp_name)
    logdir = doc['logdir']

    #TODO: Generalize bucket name
    pattern = pattern.replace("*", "**")
    gcp_path = "gs://hapticscuriosity-bucket/experiment_storage/{exp}/{pattern}".format(exp=exp_name, pattern=pattern)
    
    p = subprocess.Popen(['gsutil', 'ls', gcp_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    tgt_files = out.decode().strip().split('\n')
    tgt_files = [(t, logdir) for t in tgt_files]
    pool = mp.Pool(16)
    pool.map(get_file, tgt_files)