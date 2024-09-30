import json
import os
from dora import Node, DoraStatus
import pyarrow as pa
from mae.kernel.utils.log import write_agent_log
from mae.kernel.utils.util import load_agent_config, load_dora_inputs_and_task, create_agent_output
from mae.run.run_agent import run_dspy_agent, run_crewai_agent, run_dspy_or_crewai_agent
from mae.utils.files.dir import get_relative_path
from mae.utils.files.read import read_yaml
from mae.utils.files.util import get_all_files
from mae.utils.log.agent import record_agent_result_log


class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            agent_inputs = ['keywords','keyword_extractor_results']
            if dora_event['id'] in agent_inputs:
                keywords = dora_event["value"][0].as_py()
                yaml_file_path = get_relative_path(current_file=__file__, sibling_directory_name='configs', target_file_name='paper_downloader_agent.yml')
                inputs = load_agent_config(yaml_file_path)
                inputs.get('tasks')[0]['description'] = f"keywords: {keywords}"
                agent_result = run_dspy_or_crewai_agent(agent_config=inputs)
                arxiv_result = list(get_all_files('./data/output/arxiv_papers'))
                record_agent_result_log(agent_config=inputs,agent_result={"2, "+ inputs.get('log_step_name', "Step_one"): agent_result})

                print('-------  : ',agent_result)
                send_output("papers_info", pa.array([create_agent_output(step_name='papers_info', output_data=arxiv_result,dataflow_status=os.getenv('IS_DATAFLOW_END',False))]),dora_event['metadata'])

                print('agent_output:',agent_result)
        return DoraStatus.CONTINUE