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

Utils module for rlog_generator.
"""

import datetime
import logging
import random
import socket
import struct
import sys
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

from faker import Faker
import yaml

log = logging.getLogger(__name__)

# Initialize Faker once for performance
_faker = Faker()

# Set locale to ensure consistent output
_faker.seed_instance(42)


def load_config(yaml_file: str) -> Dict[str, Any]:
    """Return a Python object given a YAML file

    Arguments:
        yaml_file {str} -- path of YAML file

    Returns:
        Dict[str, Any] -- Python object of YAML file
    """
    with open(yaml_file, 'r') as f:
        log.debug(f"Loading file {yaml_file}")
        return yaml.safe_load(f)


def randint(min_value: Union[int, str], max_value: Union[int, str]) -> int:
    """Return random integer in range [min_value, max_value],
    including both end points

    Arguments:
        min_value {Union[int, str]} -- min value
        max_value {Union[int, str]} -- max value

    Returns:
        int -- random integer in range [min_value, max_value]
    """
    return random.randint(int(min_value), int(max_value))


def randip() -> str:
    """Return random IP address

    Returns:
        str -- IP address
    """
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))


def fake_ip() -> str:
    """Return random IP address using Faker
    
    Returns:
        str -- IP address
    """
    return _faker.ipv4()


def fake_ipv6() -> str:
    """Return random IPv6 address
    
    Returns:
        str -- IPv6 address
    """
    return _faker.ipv6()


def fake_name() -> str:
    """Return random full name
    
    Returns:
        str -- Person name
    """
    return _faker.name()


def fake_user_agent() -> str:
    """Return random user agent string
    
    Returns:
        str -- User agent
    """
    return _faker.user_agent()


def fake_uuid() -> str:
    """Return random UUID
    
    Returns:
        str -- UUID
    """
    return str(_faker.uuid4())


def fake_email() -> str:
    """Return random email address
    
    Returns:
        str -- Email address
    """
    return _faker.email()


def fake_url() -> str:
    """Return random URL
    
    Returns:
        str -- URL
    """
    return _faker.url()


def fake_hostname() -> str:
    """Return random hostname
    
    Returns:
        str -- Hostname
    """
    return _faker.hostname()


def fake_mac() -> str:
    """Return random MAC address
    
    Returns:
        str -- MAC address
    """
    return _faker.mac_address()


def fake_port() -> int:
    """Return random port number
    
    Returns:
        int -- Port number
    """
    return _faker.port_number()


def fake_unix_time() -> int:
    """Return random Unix timestamp
    
    Returns:
        int -- Unix timestamp
    """
    return int(_faker.unix_time())


def fake_file_path() -> str:
    """Return random file path
    
    Returns:
        str -- File path
    """
    return _faker.file_path()


def fake_process_name() -> str:
    """Return random process name
    
    Returns:
        str -- Process name
    """
    processes = [
        "httpd", "nginx", "postgres", "mysql", "mongod", "redis-server",
        "sshd", "systemd", "bash", "python", "java", "node", "ruby",
        "php-fpm", "uwsgi", "gunicorn", "celery", "cron", "rsyslogd",
        "named", "ntpd", "dhcpd", "smbd", "vsftpd", "dovecot", "postfix"
    ]
    return random.choice(processes)


def fake_log_level() -> str:
    """Return random log level
    
    Returns:
        str -- Log level
    """
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    return random.choice(levels)


def fake_http_method() -> str:
    """Return random HTTP method
    
    Returns:
        str -- HTTP method
    """
    return _faker.http_method()


def fake_http_status_code() -> int:
    """Return random HTTP status code
    
    Returns:
        int -- HTTP status code
    """
    return int(_faker.http_status_code())


def fake_user() -> str:
    """Return random system username
    
    Returns:
        str -- Username
    """
    return _faker.user_name()


def fake_country_code() -> str:
    """Return random country code
    
    Returns:
        str -- Country code
    """
    return _faker.country_code()


def format_date(*args) -> str:
    """Format current date with given format string
    
    Arguments:
        *args -- First argument is used as format string, rest ignored
        
    Returns:
        str -- Formatted date string
    """
    if not args:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.datetime.now().strftime(args[0])


FunctionType = TypeVar('FunctionType', bound=Callable[..., Any])

# Cache for function lookups
_function_cache: Dict[str, FunctionType] = {}

# Direct function aliases to match YAML naming convention
# This is more efficient than complex lookup logic
faker_ip = fake_ip
faker_ipv6 = fake_ipv6
faker_name = fake_name
faker_user_agent = fake_user_agent
faker_uuid = fake_uuid
faker_email = fake_email
faker_url = fake_url
faker_hostname = fake_hostname
faker_mac = fake_mac
faker_port = fake_port
faker_unix_time = fake_unix_time
faker_file_path = fake_file_path
faker_process_name = fake_process_name
faker_log_level = fake_log_level
faker_http_method = fake_http_method
faker_http_status_code = fake_http_status_code
faker_user = fake_user
faker_country_code = fake_country_code

def get_function(function_str: str, module: Any = sys.modules[__name__]) -> FunctionType:
    """Return the function from its string name as func_name
    Example: with the name 'func_randint' you will get the function name 'randint'
    With the name 'func_fake_ip' you will get the function name 'fake_ip'

    Arguments:
        function_str {str} -- name of function preceded by 'func_'

    Keyword Arguments:
        module {module obj} -- module object with the function
                                (default: {sys.modules[__name__]})

    Returns:
        FunctionType -- function of module
    """
    # Check if function is already in cache
    if function_str in _function_cache:
        return _function_cache[function_str]
    
    log.debug(f"Looking up function: {function_str}")
    
    try:
        # Handle different function naming patterns
        if function_str.startswith('func_'):
            # Remove 'func_' prefix
            function_name = function_str[5:]
            log.debug(f"Extracted function name: {function_name}")
            func = cast(FunctionType, getattr(module, function_name))
        else:
            # For non-standard patterns, try direct lookup first
            try:
                func = cast(FunctionType, getattr(module, function_str))
                log.debug(f"Direct lookup succeeded for {function_str}")
            except AttributeError:
                # Fallback to old behavior
                parts = function_str.split("_")
                if len(parts) > 1:
                    function_name = parts[1]
                    log.debug(f"Fallback extraction: {function_name}")
                    func = cast(FunctionType, getattr(module, function_name))
                else:
                    raise ValueError(f"Cannot extract function name from {function_str}")
        
        # Cache the function for future lookups
        _function_cache[function_str] = func
        return func
    except Exception as e:
        log.error(f"Error finding function '{function_str}': {e}")
        # List available functions for debugging
        available_funcs = [name for name in dir(module) 
                         if callable(getattr(module, name)) and not name.startswith('_')]
        log.debug(f"Available functions: {available_funcs}")
        raise


def exec_function_str(function_str: str) -> Any:
    """Return the value of all string function with/without
    parameters.
    Example: a complete string 'func_randint 1 10' runs the function
    randint(1, 10)
    Or 'func_fake_ip' runs the function fake_ip()

    Arguments:
        function_str {str} -- complete string function

    Returns:
        Any -- value of string function
    """
    try:
        tokens = function_str.split()
        func_name = tokens[0]
        
        # Debug logging
        log.debug(f"Looking up function: {func_name}")
        
        func = get_function(func_name)
        
        if len(tokens) == 1:
            return func()
        else:
            return func(*tokens[1:])
    except Exception as e:
        log.error(f"Error executing function '{function_str}': {e}")
        raise


def get_random_value(field_value: Union[str, List[Any]]) -> Any:
    """Return the random value of field value in pattern configuration

    Arguments:
        field_value {Union[str, List[Any]]} -- value of field in pattern configuration

    Raises:
        ValueError: raised when field value is not valid

    Returns:
        Any -- random value
    """
    if isinstance(field_value, str):
        return exec_function_str(field_value)
    elif isinstance(field_value, list):
        # Get a random choice from the list
        choice = random.choice(field_value)
        # If the choice is a string that looks like a function call, evaluate it
        if isinstance(choice, str) and choice.startswith('func_'):
            return exec_function_str(choice)
        return choice
    else:
        raise ValueError('field value can be a string or a list')


def get_template_log(template: str, fields: Dict[str, Union[str, List[Any]]]) -> str:
    """Return a random log from template string in Python formatting string
    (https://docs.python.org/3/library/string.html#custom-string-formatting)

    Arguments:
        template {str} -- template string in Python formatting string
        fields {Dict[str, Union[str, List[Any]]]} -- dict field from pattern configuration file

    Returns:
        str -- random log generated from template
    """
    values = {k: get_random_value(v) for k, v in fields.items()}
    now = datetime.datetime.now()
    return template.format(now, **values)


def custom_log(level: str = "WARNING", name: Optional[str] = None) -> logging.Logger:  # pragma: no cover
    """Configure and return a logger with custom formatting
    
    Arguments:
        level {str} -- Log level (default: "WARNING")
        name {Optional[str]} -- Logger name (default: None)
        
    Returns:
        logging.Logger -- Configured logger
    """
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger()
    logger.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(name)s | "
        "%(module)s | "
        "%(funcName)s | "
        "%(levelname)s | "
        "%(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
