import sys
sys.path.append("/storage/emulated/0/RootBase/lucrative_engines")
from state_manager import StateManager
import os
import sys
# Add lucrative_engines to path
sys.path.append(os.path.abspath("../lucrative_engines"))

sm = StateManager("mrs_higgins_saas/state/pipeline_state.json")
sm.update_key("last_run_status", "success")
print(f"State updated: {sm.load_state()}")
