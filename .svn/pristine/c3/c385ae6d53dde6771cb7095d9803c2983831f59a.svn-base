import sys
from proc.package_deploy_local import processor


# main
if __name__ == "__main__":
    if len(sys.argv) == 3:
        job_id = str(sys.argv[1])
        action_step = sys.argv[2]
        processor(job_id, action_step)
    else:
        print('usage:  python3  main_local.py  "job_id"  "gen_job_config"')
