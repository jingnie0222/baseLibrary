import sys
import os
from proc.package_deploy_dailybuild import processor


# main
if __name__ == "__main__":
    if len(sys.argv) == 2:
        config_file = sys.argv[1]
        if os.path.exists(config_file):
            processor(config_file)
    else:
        print('usage:  python3  main_dailybuild.py  ./conf/conf_template.json')
