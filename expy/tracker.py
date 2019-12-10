import os
import random
from string import hexdigits
import shutil
import subprocess
import pymongo
from ml_logger import logger as _logger

from expy import notes

MONGO_CLIENT = pymongo.MongoClient()


LOG_ROOT = os.environ['LOG_ROOT']
PROJECT_ROOT = os.environ['PROJECT_ROOT']

def get_exp_coll():
    return MONGO_CLIENT.get_database('experiments')['experiments']

def make_id(length):
    string = "".join([random.choice(hexdigits.lower()) for _ in range(length)])
    return string

def exp_exists(name):
    coll = get_exp_coll()
    doc = coll.find_one({"expName": name})
    return doc is not None

def remove_experiment(exp_name):
    coll = get_exp_coll()
    exp_doc = coll.find_one({'expName': exp_name})
    logdir = exp_doc['logdir']
    print('Removing experiment data at location: {}'.format(logdir))
    print('Are you sure? y/N')
    s = input() or 'n'
    if s == 'y':
        try:
            shutil.rmtree(logdir)
        except:
            pass

        coll.find_one_and_delete({'expName': exp_name})
    elif s == 'n':
        return 
    else:
        print('Invalid response ... aborting.')

def make_experiment(exp_name, project_dir=None, track_git=True):
    # create experiment :: need to add any information here that is relevant.
    assert not exp_exists(exp_name), """experiment with this name already exists, either remove the existing version or rename the new launch."""
    arg_dict = {}
    expID = make_id(32)
    arg_dict['expID'] = expID
    arg_dict['script'] = sys.argv[0]
    _logger.configure(LOG_ROOT, prefix=exp_name)
    if project_dir:
        dir_zip(PROJECT_ROOT, output_file='source.zip', excludes=["*.ckpt*", "*tmp_dir*", "*.mp4", "*.png", "*data*", "*.pkl", "*.git*"])
        shutil.move('source.zip', os.path.join(LOG_ROOT, exp_name + '/'  + 'source.zip'))
    if track_git:
        git_tag = get_gitinfo()
        arg_dict['gitcommit'] = git_tag
    _logger.log_params(Args={'expID': expID})
    exp_doc = {'expID': expID, 'expName': exp_name, 'logdir': os.path.join(LOG_ROOT, exp_name)}
    coll = get_exp_coll()
    coll.insert(exp_doc)
    return expID

def start_run(exp_name, params):
    coll = get_exp_coll()
    runID = make_id(8)
    run_doc = {
        'runID': runID,
        'params': params,
        'runpath': os.path.join(LOG_ROOT, exp_name + '/' + runID)
    }
    _logger.configure(LOG_ROOT, prefix=exp_name + '/' + runID)  
    coll.update_one({'expName': exp_name}, {'$push': {'runs': run_doc}})
    return _logger 


def dir_zip(root, output_file, excludes=[]):
    cmd = "zip -r {} {}".format(output_file, root)
    for exclude_str in excludes:
        cmd += " -x {} ".format(exclude_str)
        
    subprocess.run(cmd, shell=True)

def get_gitinfo():
    commit_unclean = subprocess.check_output(["git", "rev-list", "--max-parents=0", "HEAD"])
    s = commit_unclean.strip().decode() # get rid of leading white space and decode from bytes
    return s


def main():
    import sys
    args = sys.argv[1:]
    cmd = args[0]
    if cmd == "note":
        mode = args[1] # add or read
        id = args[2]
        col = get_exp_coll()
        exp_doc = col.find_one({'expID': id})
        
        if exp_doc is None:
            print('Experiment not found with id: {}'.format(id))
            exit()
        else:
            path = exp_doc['logdir']
            note_file = os.path.join(path, 'notes.txt')
            if mode == 'read':
                with open(note_file, 'r') as f:
                    note_txt = f.read()
                    print('{}'.format(exp_doc['expName']))
                    print()
                    print(note_txt)

            elif mode == 'add':
                subprocess.call(['vim', note_file])
            else:
                print('Unrecognized command {} for note, try:: add / read'.format(cmd))

if __name__ == "__main__":
    main()
