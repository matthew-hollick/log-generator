# -*- coding: utf-8 -*-

"""
Copyright 2019-2025 Würth Phoenix S.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Main module for random log generator.
"""

import glob
import logging
import os
import random
import time
from concurrent import futures
from pathlib import Path
from typing import Any, Dict
from tqdm import trange

from . import utils


TEMPLATE = "template"
RAW = "raw"
MAX_CONCUR_REQ = 100


log = logging.getLogger(__name__)


def validate_path(path: str) -> None:
    """Validate that the path is within allowed directories
    
    Arguments:
        path {str} -- Path to validate
        
    Raises:
        ValueError: If path is not in an allowed directory
    """
    abs_path = os.path.abspath(path)
    allowed_dirs = ["/tmp", str(Path.home())]
    if not any(abs_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
        raise ValueError(f"Path {abs_path} is not in an allowed directory")


def log_generator(pattern_conf: Dict[str, Any]) -> int:
    """This function generates a random log file from
    configuration pattern

    Arguments:
        pattern_conf {Dict[str, Any]} -- Python object of configuration pattern

    Raises:
        ValueError: raised when generator_type value is not valid

    Returns:
        int -- number of logs generated
    """
    name = pattern_conf["name"]
    path = pattern_conf["path"]
    
    # Validate path for security
    validate_path(path)
    
    log_path = os.path.dirname(path)
    log.debug(f"[{name}] - Generating logging for {name}")
    log.debug(f"[{name}] - Generating logging in {path}")
    eps = pattern_conf.get("eps", 1)
    log.debug(f"[{name}] - EPS: {eps}")
    time_period = pattern_conf.get("time_period", 60)
    log.debug(f"[{name}] - time period: {time_period}")
    generator_type = pattern_conf.get("generator_type", "raw")
    log.debug(f"[{name}] - generator type: {generator_type}")
    remove_file = pattern_conf.get("remove_file", False)

    # eps correction percentage
    correction = float(pattern_conf.get("correction", 1.12))
    log.debug(f"EPS correction percentage: {correction}")

    # calculate nr logs and sleep
    eps = int(round(eps * (1 + correction / 100), 0))
    log.debug(f"EPS corrected: {eps}")
    nr_logs = eps * time_period
    log.debug(f"[{name}] - Total logs to generate is {nr_logs}")
    sleep_time = 1 / eps

    log.debug(f"[{name}] - Ideal sleep time between logs is {sleep_time}")

    progress_bar = pattern_conf.get("progress_bar", False)

    if remove_file:
        try:
            os.remove(path)
            log.debug(f"[{name}] - File {path} removed")
        except OSError:
            log.debug(f"[{name}] - File {path} doesn't exist")

    # create folder log
    if not os.path.exists(log_path):
        log.debug(f"[{name}] - Created path {log_path}")
        os.makedirs(log_path)

    if progress_bar:  # pragma: no cover
        range_func = trange
        range_kvargs = {"desc": f"{name} logs loop"}
    else:
        range_func = range
        range_kvargs = {}

    if generator_type == TEMPLATE:
        log.debug(f"[{name}] - Generating logs from template")
        fields = pattern_conf["fields"]

        if not isinstance(pattern_conf["template"], list):
            raise ValueError("template must be a list of templates")

        # Initial conditions to fix sleep time
        wait = 0
        elapsed_end = 0

        # Open file once outside the loop
        with open(path, "a") as f:
            for i in range_func(nr_logs, **range_kvargs):
                start = time.time()
                
                template = random.choice(pattern_conf["template"])
                log_str = utils.get_template_log(template, fields)
                f.write(log_str + "\n")
                # Ensure each line is written immediately
                f.flush()
                
                elapsed_first = time.time() - start

                start = time.time()
                wait = sleep_time - elapsed_first - elapsed_end
                try:
                    time.sleep(wait)
                except ValueError:
                    pass
                finally:
                    elapsed_end = time.time() - start - wait

    elif generator_type == RAW:
        log.debug(f"[{name}] - Generating logs from raw examples")
        
        if "examples" not in pattern_conf or not pattern_conf["examples"]:
            raise ValueError(f"[{name}] - Generator type 'raw' requires 'examples' field with sample logs")
            
        examples = pattern_conf["examples"]
        
        # Initial conditions to fix sleep time
        wait = 0
        elapsed_end = 0
        
        # Open file once outside the loop
        with open(path, "a") as f:
            for i in range_func(nr_logs, **range_kvargs):
                start = time.time()
                
                log_str = random.choice(examples)
                f.write(log_str + "\n")
                # Ensure each line is written immediately
                f.flush()
                
                elapsed_first = time.time() - start
                
                start = time.time()
                wait = sleep_time - elapsed_first - elapsed_end
                try:
                    time.sleep(wait)
                except ValueError:
                    pass
                finally:
                    elapsed_end = time.time() - start - wait
    else:
        raise ValueError(f"Generator type {generator_type} doesn't exist")

    return nr_logs


def core(path_patterns: str, max_concur_req: int, progress_bar: bool = False) -> int:
    """This function runs the core of tool.
    All threads are generated here. A thread foreach log file.

    Arguments:
        path_patterns {str} -- path of log patterns
        max_concur_req {int} -- max concurrent log generator
        progress_bar {bool} -- enable/disable progress bar

    Returns:
        int -- Total number of logs generated
    """

    # Load all configuration patterns
    patterns = {
        os.path.basename(i): utils.load_config(i) for i in glob.iglob(
            os.path.join(path_patterns, "*.yml"))}
    # filter patterns not enabled
    patterns = {k: v for k, v in patterns.items() if v.get("enabled", False)}

    if len(patterns) == 0:
        log.error("There aren't logs to generate. Check pattern files")
        return 0

    log.info(f"Loading {len(patterns)} log patterns")

    # add commons extra values foreach log
    commons = {
        'progress_bar': progress_bar}

    for i in patterns:
        for k, v in commons.items():
            patterns[i][k] = v

    # calculate max concurrent threads
    concur_req = int(min(MAX_CONCUR_REQ, len(patterns), max_concur_req))

    log.info(f"Activate {concur_req} parallel threads")

    with futures.ThreadPoolExecutor(max_workers=concur_req) as executor:
        res = executor.map(log_generator, patterns.values())
        return sum(res)
