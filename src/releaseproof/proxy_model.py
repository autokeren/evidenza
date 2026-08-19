"""Custom Strands model provider that uses NON-STREAMING Anthropic Messages API.

Why this exists: the Anthropic SDK's streaming accumulator chokes on the
tool_use index ordering produced by our local proxy (claude-cf / claude-do).
The proxy's non-streaming `/v1/messages` response is fully correct and
complete, so we sidestep streaming entirely by issuing a single POST and
synthesizing Strands StreamEvents from the returned message.

Fresh implementation for releaseproof. No code copied from any prior project.
"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator

import httpx
from strands.models.model import Model
from strands.types.content import ContentBlock, SystemContentBlock
from strands.types.event_loop import Metrics, StopReason, Usage
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolSpec

logger = logging.getLogger(__name__)


class ProxyModel(Model):
    """Non-streaming Anthropic Messages client pointed at a local proxy.

    Args:
        base_url: Proxy root, e.g. "http://127.0.0.1:8787".
        api_key: API key passed to proxy (often "dummy" for local proxies).
        model_id: Model ID sent in the request (proxy may rewrite it).
        max_tokens: Max output tokens per request.
        params: Extra body params (e.g. {"temperature": 0.3}).
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str = "dummy",
        model_id: str,
        max_tokens: int = 1024,
        params: dict[str, Any] | None = None,
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._config: dict[str, Any] = {
            "model_id": model_id,
            "max_tokens": max_tokens,
            "params": params or {},
        }
        self._timeout = timeout

    # -- required Model interface ----------------------------------------
    def update_config(self, **model_config: Any) -> None:
        self._config.update(model_config)

    def get_config(self) -> Any:
        return dict(self._config)

    @property
    def context_window_limit(self) -> int | None:
        return None

    async def structured_output(self, output_model, prompt, system_prompt=None, **kwargs):
        raise NotImplementedError("structured_output not supported by ProxyModel")

    # -- request building ------------------------------------------------
    def _build_request(
        self,
        messages: list[dict[str, Any]],
        tool_specs: list[ToolSpec] | None,
        system_prompt: str | None,
        system_prompt_content: list[SystemContentBlock] | None,
    ) -> dict[str, Any]:
        req: dict[str, Any] = {
            "model": self._config["model_id"],
            "max_tokens": self._config["max_tokens"],
            "messages": messages,
        }
        # System prompt: prefer structured content, fall back to string.
        if system_prompt_content:
            parts = [b.get("text", "") for b in system_prompt_content if "text" in b]
            if parts:
                req["system"] = "\n\n".join(parts)
        elif system_prompt:
            req["system"] = system_prompt
        if self._config.get("params"):
            req.update(self._config["params"])
        if tool_specs:
            req["tools"] = [self._tool_spec_to_anthropic(t) for t in tool_specs]
        return req

    @staticmethod
    def _tool_spec_to_anthropic(spec: ToolSpec) -> dict[str, Any]:
        # Strands ToolSpec is a TypedDict with name/description/inputSchema.
        out: dict[str, Any] = {"name": spec["name"]}
        if "description" in spec and spec["description"]:
            out["description"] = spec["description"]
        schema_raw = spec.get("inputSchema") or spec.get("input_schema") or {}
        # Strands wraps the JSON schema under a "json" key
        # (e.g. {"json": {"properties": ..., "type": "object"}}). Unwrap it so
        # the backend sees the actual JSON schema in input_schema.
        if isinstance(schema_raw, dict) and "json" in schema_raw and isinstance(schema_raw["json"], dict):
            schema = schema_raw["json"]
        else:
            schema = schema_raw
        out["input_schema"] = schema if schema else {"type": "object", "properties": {}}
        return out

    # -- the one network call --------------------------------------------
    async def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(url, headers=headers, json=body)
        if resp.status_code != 200:
            raise RuntimeError(
                f"ProxyModel POST {url} failed: HTTP {resp.status_code}: {resp.text[:300]}"
            )
        return resp.json()

    # -- the stream() interface Strands calls ----------------------------
    async def stream(
        self,
        messages: list[dict[str, Any]],
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: Any = None,
        system_prompt_content: list[SystemContentBlock] | None = None,
        invocation_state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamEvent, None]:
        body = self._build_request(
            messages, tool_specs, system_prompt, system_prompt_content
        )
        if tool_choice is not None:
            body["tool_choice"] = tool_choice
        elif tool_specs:
            # Some backends (e.g. glm via proxy) won't call tools without an
            # explicit tool_choice. Default to "auto" when tools are present.
            body["tool_choice"] = {"type": "auto"}
        logger.debug("ProxyModel sending request (msg_count=%d, tools=%d)",
                     len(body["messages"]), len(body.get("tools") or []))
        msg = await self._post(body)

        # Synthesize Strands StreamEvents from the non-stream message.
        yield {"messageStart": {"role": "assistant"}}  # type: ignore[typeddict-item]

        content = msg.get("content") or []
        for idx, block in enumerate(content):
            btype = block.get("type")
            # IMPORTANT: process_stream uses an elif chain, so each event
            # type MUST be yielded as its own chunk (one key per dict).
            if btype == "text":
                yield {"contentBlockStart": {"contentBlockIndex": idx, "start": {}}}  # type: ignore[typeddict-item]
                yield {"contentBlockDelta": {"contentBlockIndex": idx, "delta": {"text": block.get("text", "")}}}  # type: ignore[typeddict-item]
                yield {"contentBlockStop": {"contentBlockIndex": idx}}  # type: ignore[typeddict-item]
            elif btype == "tool_use":
                yield {  # type: ignore[typeddict-item]
                    "contentBlockStart": {
                        "contentBlockIndex": idx,
                        "start": {"toolUse": {"toolUseId": block.get("id", ""), "name": block.get("name", "")}},
                    },
                }
                inp = block.get("input")
                yield {  # type: ignore[typeddict-item]
                    "contentBlockDelta": {
                        "contentBlockIndex": idx,
                        "delta": {"toolUse": {"input": json.dumps(inp) if inp is not None else ""}},
                    },
                }
                yield {"contentBlockStop": {"contentBlockIndex": idx}}  # type: ignore[typeddict-item]
            elif btype == "thinking":
                yield {"contentBlockStart": {"contentBlockIndex": idx, "start": {}}}  # type: ignore[typeddict-item]
                yield {  # type: ignore[typeddict-item]
                    "contentBlockDelta": {
                        "contentBlockIndex": idx,
                        "delta": {"reasoningContent": {"text": block.get("thinking", "")}},
                    },
                }
                yield {"contentBlockStop": {"contentBlockIndex": idx}}  # type: ignore[typeddict-item]
            else:
                logger.debug("ProxyModel skipping unknown block type %r", btype)

        # stop reason + usage
        stop_raw = msg.get("stop_reason", "end_turn")
        stop_reason = stop_raw if stop_raw in StopReason.__args__ else "end_turn"
        usage_raw = msg.get("usage") or {}
        in_tok = int(usage_raw.get("input_tokens", 0))
        out_tok = int(usage_raw.get("output_tokens", 0))
        yield {  # type: ignore[typeddict-item]
            "messageStop": {"stopReason": stop_reason},
            "metadata": {
                "usage": Usage(
                    inputTokens=in_tok, outputTokens=out_tok, totalTokens=in_tok + out_tok
                ),
                "metrics": Metrics(latencyMs=0, timeToFirstByteMs=0),
            },
        }

    async def count_tokens(self, messages, tool_specs=None, system_prompt=None,
                           system_prompt_content=None) -> int:
        # Cheap heuristic; not used for billing.
        total = 0
        for m in messages:
            c = m.get("content")
            if isinstance(c, str):
                total += len(c) // 4
            elif isinstance(c, list):
                for b in c:
                    if "text" in b:
                        total += len(b["text"]) // 4
        return total
