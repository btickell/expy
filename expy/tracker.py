import os
import sys
import random
from string import hexdigits
import shutil
import subprocess
import pymongo
from ml_logger import logger as _logger
import datetime

MONGO_CLIENT = pymongo.MongoClient()


LOG_ROOT = os.environ['LOG_ROOT']
PROJECT_ROOT = os.environ['PROJECT_ROOT']

def get_exp_coll():
    return MONGO_CLIENT.get_database('experiments')['experiments']

def get_run_doc(exp_name, runID=None):
    db = get_exp_coll()
    exp_doc = db.find_one({'expName': exp_name})
    for run_doc in exp_doc['runs']:
        if run_doc['runID'] == runID:
            return run_doc

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

def make_experiment(exp_name, zip_project=False, track_git=True):
    # create experiment :: need to add any information here that is relevant.
    assert not exp_exists(exp_name), """experiment with this name already exists, either remove the existing version or rename the new launch."""
    arg_dict = {}
    expID = make_id(32)
    arg_dict['expID'] = expID
    arg_dict['script'] = sys.argv[0] # TODO: check that this is the correct approach.
    _logger.configure(LOG_ROOT, prefix=exp_name)
    if zip_project:
        dir_zip(PROJECT_ROOT, output_file='source.zip', excludes=["*.ckpt*", "*tmp_dir*", "*.mp4", "*.png", "*data*", "*.pkl", "*.git*"])
        shutil.move('source.zip', os.path.join(LOG_ROOT, exp_name + '/'  + 'source.zip'))
    if track_git:
        arg_dict['gitcommit'] = get_gitcommit()
        arg_dict['gitbranch'] = get_gitbranch()
        
    _logger.log_params(Args={'expID': expID})
    timestamp = datetime.datetime.now().strftime("%x :: %X")
   
    exp_doc = {
        'expID': expID, 'expName': exp_name, 
        'logdir': os.path.join(LOG_ROOT, exp_name),
        'time': timestamp    
    }

    coll = get_exp_coll()
    coll.insert(exp_doc)
    return expID

def get_exp_doc(exp_name):
    db = get_exp_coll()
    return db.find_one({'expName': exp_name})
def start_run(exp_name, params, runID=None):
    coll = get_exp_coll()
    if runID is None:
        runID = make_id(8)
    
    run_tstamp = datetime.datetime.now().strftime("%x :: %X")

    script_txt = ' '.join(sys.argv)
    run_doc = {
        'runID': runID,
        'params': params,
        'runpath': os.path.join(LOG_ROOT, exp_name + '/' + runID),
        'script': sys.argv[0],
        'command': script_txt,
        'timestamp': run_tstamp
    }
    _logger.configure(LOG_ROOT, prefix=exp_name + '/' + runID)  
    coll.update_one({'expName': exp_name}, {'$push': {'runs': run_doc}})
    _logger.log_params(Args=params)
    
    return _logger 

def continue_run(exp_name, runID):
    _logger.configure(LOG_ROOT, prefix=exp_name + '/' + runID)  
    return _logger 
    
def dir_zip(root, output_file, excludes=[]):
    cmd = "zip -r {} {}".format(output_file, root)
    for exclude_str in excludes:
        cmd += " -x {} ".format(exclude_str)
        
    subprocess.run(cmd, shell=True)

def _clean(s):
    return s.strip().decode()

def get_gitcommit():
    raw_output = subprocess.check_output(["git", "rev-list", "--max-parents=0", "HEAD"])
    return _clean(raw_output) # get rid of leading white space and decode from bytes

def get_gitbranch():
    raw_output = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    return _clean(raw_output)

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        exit()
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
    if cmd == "remove":
        exp_name = args[1]
        remove_experiment(exp_name)

if __name__ == "__main__":
    main()
