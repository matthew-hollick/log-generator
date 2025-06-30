# Random Log Generator

Generator of random logs for multiple types of technologies.

This tool can generate all kinds of logs starting from templates or raw examples.
You should create a pattern file in YAML format for each log type you want to generate, like in [conf/patterns](conf/patterns) examples.

If more than one pattern is specified in the patterns folder, all logs are generated in parallel. It's possible to generate up to 100 logs in parallel.

## Install

### Using UV (Recommended)

This project uses [UV](https://github.com/astral-sh/uv) for dependency management. UV is a fast, reliable Python package installer and resolver.

```bash
# Install UV if you don't have it yet
pip install uv

# Clone repository
git clone https://github.com/WuerthPhoenix/log-generator.git
cd log-generator

# Create a virtual environment and install dependencies
uv venv
uv pip install -e .
```

### Using pip

```bash
pip install rlog-generator
```

### From source

```bash
git clone https://github.com/WuerthPhoenix/log-generator.git
cd log-generator
pip install -e .
```

## Pattern file

A pattern file has many parameters.

| Parameters | Descriptions |
| ---------- | ------------ |
| _name_ | Name of log |
| _enabled_ | Enable/disable this pattern |
| _path_ | Path where to store the log (must be in /tmp or home directory for security) |
| _eps_ | Number of logs per second that will be generated |
| _correction_ | EPS correction percentage |
| _time_period_ | How many seconds the generating is active |
| _generator_type_ | Generator type: `template` or `raw` |
| _examples_ | Example logs (required for `raw` generator type) |
| _template_ | Template to use to generate logs (required for `template` generator type) |
| _fields_ | Fields used in template (required for `template` generator type) |


We can have two kinds of fields:

- _list_: the list fields are used to generate random values from a given list
- _func_: the func fields enable functions to generate the random values.

The `func` fields start with `func_` and then have the name of function. It can also have parameters.

The `func` developed are:

### Basic Functions

- `func_randip`: generate a random ip address
- `func_randint`: generate a random integer from _min_ to _max_

### Faker-based Functions

#### Network & Infrastructure

- `func_fake_ip`: generate a realistic IPv4 address
- `func_fake_ipv6`: generate a realistic IPv6 address
- `func_fake_mac`: generate a realistic MAC address
- `func_fake_hostname`: generate a realistic server hostname
- `func_fake_port`: generate a realistic port number

#### User & Identity

- `func_fake_user`: generate a realistic username
- `func_fake_name`: generate a realistic full name
- `func_fake_email`: generate a realistic email address
- `func_fake_uuid`: generate a UUID

#### Web & HTTP

- `func_fake_url`: generate a realistic URL
- `func_fake_user_agent`: generate a realistic browser user agent string
- `func_fake_http_method`: generate an HTTP method (GET, POST, etc.)
- `func_fake_http_status_code`: generate an HTTP status code

#### System & Logs

- `func_fake_process_name`: generate a realistic process name
- `func_fake_log_level`: generate a log level (INFO, ERROR, etc.)
- `func_fake_unix_time`: generate a Unix timestamp
- `func_fake_file_path`: generate a realistic file path
- `func_fake_country_code`: generate a country code

#### Date & Time

- `func_format_date`: format current date with given format string

## Usage Examples

Here are examples of how to use these functions in your pattern files:

```yaml
fields:
  # Network fields
  client_ip: func_fake_ip
  server_hostname: func_fake_hostname
  mac_address: func_fake_mac
  
  # User identity fields
  username: func_fake_user
  email: func_fake_email
  
  # Web request fields
  http_method: func_fake_http_method
  status_code: func_fake_http_status_code
  user_agent: func_fake_user_agent
  
  # System fields
  process: func_fake_process_name
  log_level: func_fake_log_level
  
  # Date formatting
  timestamp: func_format_date "%Y-%m-%d %H:%M:%S"
  
  # Random values
  response_time_ms: func_randint 10 500
```

You can also use these functions within lists for random selection:

```yaml
fields:
  user:
    - "-"  # Anonymous user
    - func_fake_user  # Will be evaluated as a function
  status:
    - "active"
    - "inactive"
    - "pending"
```

For more examples, see the pattern files in the [patterns](patterns) folder.

If you want to contribute with real templates, add them in [patterns](patterns) folder.

## Performance and Realism Considerations

### Advantages of Faker Functions

- **Realistic Data**: Faker functions generate data that closely resembles real-world values, improving testing quality
- **Consistency**: Related data fields maintain logical relationships (e.g., usernames match email patterns)
- **Diversity**: Wide variety of data types covers most common log fields
- **Deterministic**: Seeded for reproducible results while maintaining randomness

### Performance Optimization

The Faker integration is designed for maximum performance:

- Single global Faker instance to minimize overhead
- Function results are cached when possible
- Direct function aliases avoid complex lookup logic
- Minimal string parsing during template rendering

For high-volume log generation (>10,000 EPS), consider:

1. Pre-generating common values in memory
2. Using simpler functions for performance-critical fields
3. Profiling to identify bottlenecks in your specific patterns

## Command line

The installation stores on system the `rlog-generator` command line.

```bash
rlog-generator --help
Usage: rlog-generator [OPTIONS]

  Random Logs Generator Tool.

Options:
  -p, --patterns TEXT             Path all log patterns files (only *.yml)
                                  [default: ~/.config/rlog_generator/patterns]
  -m, --max-concur-req INTEGER    Max concurrent logs generating  [default: 10]
  -l, --log-level [CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
                                  Log level on stdout  [default: WARNING]
  --progress-bar / --no-progress-bar
                                  Enable/Disable progress bar  [default: False]
  --help                          Show this message and exit.

```

## Features

- Random logging from template
- Template can be a list of multiple formats
- Generate logs from raw examples
- Path validation for security
- Modern dependency management with UV
- Type hints throughout the codebase
- Improved error handling

## Development

### Setup Development Environment

```bash
uv venv
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy rlog_generator
```

## Apache 2 Open Source License

This tool can be downloaded, used, and modified free of charge. It is available under the Apache 2 license.