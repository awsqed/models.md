from pathlib import Path

from models_pipeline import llm, output, prompt
from models_pipeline.llm import ChatMessage, ChatRequest, ChatResponse
from models_pipeline.pipeline.types import LoadedConfig, PromptBundle


def step_build_prompt(
    blobs: list[tuple[str, str]],
    schema_text: str,
    output_names: list[str],
) -> PromptBundle:
    system_prompt, user_prompt = prompt.build_catalog_prompt(
        blobs,
        schema_text,
        output_names,
    )
    total = len(system_prompt) + len(user_prompt)
    print(
        f"[prompt] system={len(system_prompt)} chars  user={len(user_prompt)} chars  total={total} chars"
    )
    return PromptBundle(system=system_prompt, user=user_prompt)


def step_call_llm(loaded: LoadedConfig, bundle: PromptBundle) -> ChatResponse:
    print(f"[llm]    calling {loaded.model} ...")
    response = llm.request_chat_completion(
        ChatRequest(
            model=loaded.model,
            api_base_url=loaded.api_base_url,
            messages=[
                ChatMessage(role="system", content=bundle.system),
                ChatMessage(role="user", content=bundle.user),
            ],
            timeout_seconds=loaded.runtime.llm.timeout_seconds,
            max_retries=loaded.runtime.llm.max_retries,
            max_output_tokens=loaded.runtime.llm.max_output_tokens,
            reasoning=not loaded.runtime.llm.disable_thinking,
        )
    )
    print(f"[llm]    response={len(response.content)} chars")
    print(f"[llm]    usage={response.usage}")
    return response


def step_parse_outputs(raw: str, output_names: list[str]) -> dict[str, str]:
    outputs = output.parse(raw, output_names)
    output.validate(outputs, output_names)
    print(f"[parse]  extracted {len(outputs)} output files")
    return outputs


def step_write_outputs(outputs: dict[str, str], *, root: Path, check: bool) -> bool:
    return output.write_or_check(outputs, root=root, check=check)
