import json
import os
from dora import Node, DoraStatus
import pyarrow as pa
from mofa.kernel.utils.util import load_agent_config, load_dora_inputs_and_task, create_agent_output
from mofa.run.run_agent import run_dspy_agent, run_crewai_agent, run_dspy_or_crewai_agent
from mofa.utils.files.dir import get_relative_path
from mofa.utils.log.agent import record_agent_result_log
from mofa.kernel.utils.util import load_agent_config, load_dora_inputs_and_task, create_agent_output, load_node_result


class Operator:
    def __init__(self):
        self.crawl_result = None
        self.task = None
        self.context_memory = None
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            if dora_event['id'] == "task": self.task = dora_event["value"][0].as_py()
            if dora_event['id'] == "crawl_result": self.crawl_result = load_node_result(dora_event["value"][0].as_py())
            if dora_event['id'] == "context_memory": self.context_memory =  load_node_result(dora_event["value"][0].as_py())
            if self.task is not None and self.crawl_result is not None :

                yaml_file_path = get_relative_path(current_file=__file__, sibling_directory_name='configs', target_file_name='reasoner_agent.yml')
                inputs = load_agent_config(yaml_file_path)
                inputs["task"] = self.task
                if len(self.crawl_result)>0 :
                    inputs['input_fields'] = {"crawl_data":self.crawl_result}
                # if len(self.context_memory)>0:
                #     inputs['input_fields'] = {"memory_data":self.context_memory}
                agent_result = run_dspy_or_crewai_agent(agent_config=inputs)
                record_agent_result_log(agent_config=inputs,
                                        agent_result={
                                            "2, "+ inputs.get('log_step_name', "Step_one"): agent_result})
                send_output("reasoner_response", pa.array([create_agent_output(step_name='reasoner_response', output_data=agent_result,dataflow_status=os.getenv('IS_DATAFLOW_END',False))]),dora_event['metadata'])
                print('reasoner_results:', agent_result)
                self.crawl_result = None
                self.task = None
                self.context_memory = None

        return DoraStatus.CONTINUE