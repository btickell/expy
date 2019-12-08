from expy.tracker import make_experiment, start_run, get_exp_coll

try:
    make_experiment('test_exp', project_dir="*", track_git=False)
except:
    pass

start_run('test_exp', params={'A': 'BAR'})




