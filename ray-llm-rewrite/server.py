from ray import serve
from ray.serve.llm import LLMConfig, build_openai_app

# Define config.
llm_config = LLMConfig(
    model_loading_config={
        "model_id": 'ray',
        "model_source": '/home/data/share/Qwen3-14B-FP8'
    },
    # runtime_env={"env_vars": {"HF_TOKEN": os.environ.get("HF_TOKEN")}},
    deployment_config={
        "autoscaling_config": {
            "min_replicas": 0,
            "max_replicas": 8,
            # complete list: https://docs.ray.io/en/latest/serve/autoscaling-guide.html#serve-autoscaling
        }
    },
    # accelerator_type="L4",
    engine_kwargs={
        "max_model_len": 32768,  # Or increase KV cache size.
        "tensor_parallel_size": 1,
        "enable_lora": False,
        # complete list: https://docs.vllm.ai/en/stable/serving/engine_args.html
    },
)

# Deploy.
app = build_openai_app({"llm_configs": [llm_config]})
serve.run(app, blocking=True)
