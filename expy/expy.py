import click
from expy.tracker import *
import expy.gcp_utils as gsutils
import subprocess
import tabulate
import datetime
from expy.gather import *

@click.group()
def main():
    pass

from expy.gather import *
from expy.tracker import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@click.group()
def main():
    pass

@main.group()
def note():
    pass


@main.command()
@click.argument('exp-name')
def gather(exp_name):
    get_results_gcp(exp_name, pattern='*results*')

@note.command()
@click.argument('exp-name')
@click.option('--runid', default=None)
def add(exp_name, runid):
    col = get_exp_coll()
    exp_doc = col.find_one({'expName': exp_name})
    path = exp_doc['logdir']
    if runid:
        path = os.path.join(path, str(runid))
    path = os.path.join(path, 'note.txt')
    subprocess.call(['vim', path])

@note.command()
@click.argument('exp-name')
@click.option('--runid', default=None)
def read(exp_name, runid):
    col = get_exp_coll()
    exp_doc = col.find_one({'expName': exp_name})
    path = exp_doc['logdir']
    if runid:
        path = os.path.join(path, str(runid))
    path = os.path.join(path, 'note.txt')
    try:
        with open(path, 'r') as f:
            note_txt = f.read()
            s = ""
            s += 'Experiment Name: '
            s += bcolors.OKGREEN
            s += exp_name
            if runid:
                s += " Run ID: {} ".format(runid)
            s += bcolors.ENDC
            print()
            print(s)
            print()
            print(bcolors.WARNING + note_txt + bcolors.ENDC)
    except:
        print("No note exists -- add with 'expy note add'")

@main.command()
@click.option('-d', type=int, default=10)
@click.option('--max', type=int, default=None)
def ls( d, max):
    col = get_exp_coll()
    res = col.find().sort([("_id",-1)])
    
    tab_list = []
    result_list = list(res)
    
    for doc in result_list[:d]:
        entry = []
        entry.append(doc['expName'])
        if 'time' in doc.keys():
            date, time = doc['time'].split('::')
            entry += [date, time]
        else:
            entry += 2*['N/A']
        tab_list.append(entry)

    if len(result_list) > d:
        tab_list.append(['....'])
    s = tabulate.tabulate(tab_list, headers=['Experiment\nName', 'Date', 'Time', 'Note'], tablefmt='fancy_grid')
    print(s)

@main.command()
@click.argument('exp-name')
def rm(exp_name):
    gcp_fp = "gs://hapticscuriosity-bucket/experiment_storage/{}".format(exp_name)
    try:
        coll = get_exp_coll()
        exp_doc = coll.find_one({'expName': exp_name})  
        logdir = exp_doc['logdir']
    except:
        print("Experiment [" + bcolors.OKBLUE + exp_name + bcolors.ENDC + "] not found")
        exit()
        
    print("Going to remove local files at: {}".format(logdir))
    print("Going to remove experiment files from GCP: {}".format(gcp_fp))  
    print("Are you sure?: y/[n]")
    user_in = input() or 'n'
    if user_in == "n":
        print("Aborting delete operation.")
        exit()
    else:
        try:
            shutil.rmtree(logdir)
            print("Removed local files.")
        except:
            print("No local files.")
        try:
            print("Removing remote files")
            gsutils.gcp_rm_dir(gcp_fp)
        except:
            print("No remote files at {}".format(gcp_fp))

        try:
            print("Removing experiment document.")
            coll.find_one_and_delete({'expName': exp_name})
        except:
            print("Failed to remove experiment document.")

if __name__ == "__main__":
    main()

