#!/usr/bin/env python
import traceback
import logging
from rlog_generator.cli import main

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    main(['-p', 'patterns'])
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
